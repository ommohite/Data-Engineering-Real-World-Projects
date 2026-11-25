# Author: Om Mohite
# Test Case 1: Python export of the corresponding Jupyter notebook.
# Run from this folder; configure DB_PASSWORD/DB_USER/DB_HOST/DB_PORT as needed.

import os
from pathlib import Path
from getpass import getpass

try:
    from IPython.display import display
except ImportError:
    display = print

import pandas as pd
from pathlib import Path
import logging
from sqlalchemy import create_engine, URL,text

# %%


connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=getpass("MySQL password: "),
    host="localhost",
    port=3306,
    database="test_cases"
)
engine = create_engine(connection_url)

# %%

p = Path(__file__).resolve().parent / "datasets" / "nba.csv"

# %%

df_sql = pd.read_sql("select * from nba_players",engine)

# %%

df_sql

# %%

logging.basicConfig(level=logging.INFO,force=True)

# %%

logging.debug("program is debuged")
logging.info("program is STARTED")
logging.warning("program is failing")
logging.error("program is failed")
logging.critical("program is in  critical stage")

# %%

def read_data(p):
    try:
        logging.info("Loading Data")
        df = pd.read_csv(p)
        logging.info("Data Loaded Successfully")
        return df
    except Exception as e:
        logging.error(f"Error : {e} ")
        raise

# %%

df=read_data(p)

# %%

print(df.info())

df.duplicated().sum()
df.isnull().sum()

# %%

def tranformation(df):
    transforemed_df=df.drop_duplicates()
    transforemed_df.columns = transforemed_df.columns.str.upper()
    transforemed_df['COLLEGE']=transforemed_df['COLLEGE'].fillna('Unknown')
    transforemed_df['SALARY']=transforemed_df['SALARY'].fillna(transforemed_df['SALARY'].mean())
    transforemed_df = transforemed_df.drop('HEIGHT',axis=1)
    return transforemed_df

# %%

print(tranformation(df))

# %%

def laod_data(df,table_name,engine):
    try:
        logging.info("Starting the Laoding")
        df.to_sql(name=table_name,
              con=engine,
              if_exists='append',
              index=False
              )
        logging.info("Laoding completed successfully")
    except Exception as e:
        logging.error(e)

# %%


def main_function():
    df = read_data(p)
    new_df = tranformation(df)
    laod_data(new_df,'nba_players',engine)

# %%

# import schedule
# import time

# def daily_task():
#     print("Executing daily ETL pipeline...")

# schedule.every(1).minute.do(daily_task)

# while True:
#     schedule.run_pending()
#     time.sleep(60)

# %%

df

# %%

df.loc[0,"Name"] ="Anderson silve"

# %%

print("df columns:")
print(df.columns.tolist())

print("\ndf_clean columns:")
print(df_clean.columns.tolist())

print("\ndf_clean shape:")
print(df_clean.shape)

print("\nDuplicate player names:")
print(df_clean["Name"].duplicated().sum())

# %%

new_df = df_clean.rename(columns=str.upper)

print("DATA READY FOR MYSQL LOAD")
print("Shape:", new_df.shape)
print("Columns:", new_df.columns.tolist())

print("\nMissing Values:")
print(new_df.isnull().sum())

# %%


# =====================================================
# STEP 1: IMPORT LIBRARIES
# =====================================================

import pandas as pd

from getpass import getpass

from sqlalchemy import create_engine, URL, text


# =====================================================
# STEP 2: MYSQL DATABASE CONNECTION
# =====================================================

mysql_password = getpass("MySQL password: ")

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=mysql_password,
    host="127.0.0.1",
    port=3306,
    database="test_cases"
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)


# Test database connection

with engine.connect() as conn:

    result = conn.execute(
        text("""
            SELECT VERSION(), DATABASE(), CURRENT_USER()
        """)
    )

    row = result.fetchone()

    print("MYSQL CONNECTION SUCCESSFUL!")
    print("MySQL Version:", row[0])
    print("Database:", row[1])
    print("User:", row[2])


# =====================================================
# STEP 3: VALIDATE SOURCE DATA
# =====================================================

if "new_df" not in globals():
    raise NameError(
        "new_df not found. Run your previous data cleaning cells first."
    )

df = new_df.copy()

df.columns = df.columns.str.upper()

required_columns = [
    "NAME",
    "TEAM",
    "NUMBER",
    "POSITION",
    "AGE",
    "HEIGHT",
    "WEIGHT",
    "COLLEGE",
    "SALARY"
]

missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

if df["NAME"].isna().any():
    raise ValueError("Player NAME contains NULL values.")

if df["NAME"].duplicated().any():
    raise ValueError(
        "Duplicate player names found. Resolve duplicates before loading."
    )

df = df[required_columns]

print("\nSOURCE DATA VALIDATION SUCCESSFUL!")
print("Source Records:", len(df))
print("Columns:", df.columns.tolist())


# =====================================================
# STEP 4: CREATE TARGET TABLE
# =====================================================

create_table_query = """
CREATE TABLE IF NOT EXISTS nba_players (

    player_id INT AUTO_INCREMENT PRIMARY KEY,

    NAME VARCHAR(100) NOT NULL,

    TEAM VARCHAR(100),

    NUMBER INT,

    POSITION VARCHAR(10),

    AGE INT,

    HEIGHT VARCHAR(10),

    WEIGHT INT,

    COLLEGE VARCHAR(150),

    SALARY DECIMAL(12,2),

    UNIQUE KEY uq_player_name (NAME)

)
"""

with engine.begin() as conn:
    conn.execute(text(create_table_query))

print("\nTARGET TABLE READY!")


# =====================================================
# STEP 5: UPSERT FUNCTION
# =====================================================

def upsert_load(df, engine):

    inserted_count = 0
    updated_count = 0

    with engine.begin() as conn:

        for _, row in df.iterrows():

            params = {}

            for column in required_columns:

                value = row[column]

                if pd.isna(value):
                    value = None

                elif hasattr(value, "item"):
                    value = value.item()

                params[column.lower()] = value

            # Check existing player

            existing_player = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM nba_players
                    WHERE NAME = :name
                """),
                {"name": params["name"]}
            ).scalar_one()

            if existing_player > 0:

                # UPDATE existing player

                conn.execute(
                    text("""
                        UPDATE nba_players
                        SET
                            TEAM = :team,
                            NUMBER = :number,
                            POSITION = :position,
                            AGE = :age,
                            HEIGHT = :height,
                            WEIGHT = :weight,
                            COLLEGE = :college,
                            SALARY = :salary

                        WHERE NAME = :name
                    """),
                    params
                )

                updated_count += 1

            else:

                # INSERT new player

                conn.execute(
                    text("""
                        INSERT INTO nba_players (
                            NAME,
                            TEAM,
                            NUMBER,
                            POSITION,
                            AGE,
                            HEIGHT,
                            WEIGHT,
                            COLLEGE,
                            SALARY
                        )
                        VALUES (
                            :name,
                            :team,
                            :number,
                            :position,
                            :age,
                            :height,
                            :weight,
                            :college,
                            :salary
                        )
                    """),
                    params
                )

                inserted_count += 1

    print("\nUPSERT COMPLETED SUCCESSFULLY!")
    print("--------------------------------")
    print("Inserted Records:", inserted_count)
    print("Updated Records:", updated_count)
    print("Total Processed:", inserted_count + updated_count)


# =====================================================
# STEP 6: EXECUTE DATA LOAD
# =====================================================

upsert_load(df, engine)


# =====================================================
# STEP 7: VERIFY TARGET DATA
# =====================================================

with engine.connect() as conn:

    total_records = conn.execute(
        text("SELECT COUNT(*) FROM nba_players")
    ).scalar_one()

    null_records = conn.execute(
        text("""
            SELECT COUNT(*)
            FROM nba_players
            WHERE NAME IS NULL
        """)
    ).scalar_one()

    duplicate_records = conn.execute(
        text("""
            SELECT COUNT(*)
            FROM (
                SELECT NAME
                FROM nba_players
                GROUP BY NAME
                HAVING COUNT(*) > 1
            ) AS duplicates
        """)
    ).scalar_one()

    print("\nFINAL DATA VALIDATION")
    print("--------------------------------")
    print("Total Target Records:", total_records)
    print("NULL Player Names:", null_records)
    print("Duplicate Player Names:", duplicate_records)

    result = conn.execute(
        text("""
            SELECT *
            FROM nba_players
            ORDER BY player_id
            LIMIT 10
        """)
    )

    output_df = pd.DataFrame(
        result.fetchall(),
        columns=result.keys()
    )

    print("\nSAMPLE TARGET DATA:")
    display(output_df)


# =====================================================
# STEP 8: CLOSE CONNECTION
# =====================================================

engine.dispose()

print("\nNBA PLAYERS ETL PIPELINE COMPLETED!")

# %%

new_record = pd.DataFrame([{
    '': 456,
    'Name': 'Jeff Withey',
    'Team': 'Utah Jazz',
    'Number': 24,
    'Position': 'C',
    'Age': 26,
    'Height': '7-0',
    'Weight': 231,
    'College': 'Kansas',
    'Salary': 947276.0
}])

# %%

df = pd.concat([df, new_record], ignore_index=True)

# %%

df

# %%

new_df = tranformation(df)

# %%

new_df

# %%

connection_url_2 = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=mysql_password,
    host="localhost",
    port=3306,
    database="test_cases"
)

engine2 = create_engine(connection_url_2)

# %%

upsert_load(new_df,engine)

# %%

import sys
import pandas as pd
import sqlalchemy
import pymysql

print("Python Path:", sys.executable)
print("Pandas:", pd.__version__)
print("SQLAlchemy:", sqlalchemy.__version__)
print("All imports successful!")

# %%

from getpass import getpass

mysql_password = getpass("MySQL password: ")

if mysql_password:
    print("Password received successfully.")
    print("Password length:", len(mysql_password))
else:
    print("Password is EMPTY. Try again.")

# %%

from sqlalchemy import create_engine, URL, text

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=mysql_password,
    host="127.0.0.1",
    port=3306,
    database="data_engineering"
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

try:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT VERSION(), DATABASE(), CURRENT_USER()")
        )
        print("MySQL Connection Successful!")
        print(result.fetchone())

except Exception as e:
    print("Connection Failed!")
    print(type(e).__name__, e)

# %%

from pathlib import Path
import pandas as pd
from sqlalchemy import text

# CSV file path
csv_path = Path("Test_Cases_Original/datasets-df-series/nba.csv")

# Verify file
if not csv_path.exists():
    raise FileNotFoundError(f"CSV not found: {csv_path.resolve()}")

# Extract data
df = pd.read_csv(
    csv_path,
    dtype=str,
    skipinitialspace=True
)

df.columns = df.columns.str.strip()

print("CSV Extraction Successful")
print("File:", csv_path.resolve())
print("Rows:", len(df))
print("Columns:", df.columns.tolist())

# Verify database
with engine.connect() as conn:
    result = conn.execute(text("SELECT DATABASE()"))
    print("Connected Database:", result.scalar())

display(df.head())

# %%

from pathlib import Path
import pandas as pd

csv_path = Path("../datasets-df-series/nba.csv")

print("Resolved Path:", csv_path.resolve())
print("File Exists:", csv_path.exists())

if not csv_path.exists():
    raise FileNotFoundError("NBA CSV file not found!")

df = pd.read_csv(
    csv_path,
    dtype=str,
    skipinitialspace=True
)

df.columns = df.columns.str.strip()

print("\nCSV Extraction Successful")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Column Names:", df.columns.tolist())

display(df.head())

# %%

# 1. Dataset Information
print("DATASET INFORMATION")
df.info()

# 2. Missing Values
print("\nMISSING VALUES")
print(df.isnull().sum())

# 3. Missing Value Percentage
print("\nMISSING VALUE PERCENTAGE")
print((df.isnull().mean() * 100).round(2))

# 4. Duplicate Records
print("\nEXACT DUPLICATE ROWS")
print(df.duplicated().sum())

# 5. Duplicate Player Names
print("\nDUPLICATE PLAYER NAMES")
print(df[df.duplicated(subset=["Name"], keep=False)])

# 6. Unique Height Values
print("\nHEIGHT VALUES")
print(sorted(df["Height"].dropna().unique()))

# 7. Salary Missing Records
print("\nSALARY MISSING RECORDS")
display(df[df["Salary"].isna()][["Name", "Team", "Salary"]])

# 8. Dataset Summary
print("\nDATASET SUMMARY")
print("Total Rows:", len(df))
print("Total Columns:", len(df.columns))

# %%

# 1. Missing values report
print("MISSING VALUE REPORT")
print(df.isnull().sum())

# 2. Height values with frequency
print("\nHEIGHT VALUE FREQUENCY")
print(df["Height"].value_counts(dropna=False).sort_index())

# 3. Salary values that cannot be converted to numbers
salary_numeric = pd.to_numeric(df["Salary"], errors="coerce")

print("\nSALARY INVALID / MISSING VALUES")
display(
    df.loc[
        salary_numeric.isna(),
        ["Name", "Team", "Salary"]
    ]
)

# 4. Exact duplicate rows
print("\nEXACT DUPLICATE ROWS")
print(df.duplicated().sum())

# 5. Duplicate player names
print("\nDUPLICATE PLAYER NAMES")
display(
    df[df.duplicated(subset=["Name"], keep=False)]
    .sort_values("Name")
)

# 6. Whitespace check
print("\nWHITESPACE CHECK")
for col in df.select_dtypes(include="object").columns:
    print(col, ":", df[col].ne(df[col].str.strip()).sum())

# %%

import re

month_map = {
    "Jan": "1", "Feb": "2", "Mar": "3",
    "Apr": "4", "May": "5", "Jun": "6",
    "Jul": "7", "Aug": "8", "Sep": "9",
    "Oct": "10", "Nov": "11", "Dec": "12"
}

def clean_height(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    # Example: 06-Feb -> 6-2
    match = re.fullmatch(r"(\d{2})-([A-Za-z]{3})", value)

    if match:
        feet = str(int(match.group(1)))
        inches = month_map[match.group(2).title()]
        return f"{feet}-{inches}"

    # Already in correct format: 7-0
    if re.fullmatch(r"\d+-\d+", value):
        return value

    return value


df["Height_Clean"] = df["Height"].apply(clean_height)

print("Original vs Cleaned Height")

display(
    df[["Height", "Height_Clean"]].drop_duplicates()
    .sort_values("Height")
)

# %%

# Create a separate copy
df_clean = df.copy()

# 1. Clean Height column
df_clean["Height"] = df_clean["Height_Clean"]

# Remove temporary column
df_clean.drop(columns=["Height_Clean"], inplace=True)

# 2. Clean text columns
text_columns = ["Name", "Team", "Position", "College"]

for col in text_columns:
    df_clean[col] = df_clean[col].astype("string").str.strip()

# 3. Handle missing College values
df_clean["College"] = df_clean["College"].fillna("Unknown")

# 4. Convert numeric columns
numeric_columns = ["Number", "Age", "Weight"]

for col in numeric_columns:
    df_clean[col] = pd.to_numeric(
        df_clean[col], errors="coerce"
    ).astype("Int64")

# 5. Convert Salary into numeric
df_clean["Salary"] = pd.to_numeric(
    df_clean["Salary"], errors="coerce"
).astype("Float64")

# 6. Final validation
print("FINAL DATASET INFORMATION")
df_clean.info()

print("\nMISSING VALUES")
print(df_clean.isnull().sum())

print("\nDATASET SHAPE")
print(df_clean.shape)

print("\nCLEANED DATA PREVIEW")
display(df_clean.head(10))

# %%

# 1. Create validation report

validation_report = {}

# Check duplicate business keys
validation_report["Duplicate_Player_Keys"] = (
    df_clean.duplicated(
        subset=["Name", "Team", "Number"]
    ).sum()
)

# Check invalid ages
validation_report["Invalid_Age"] = (
    (~df_clean["Age"].between(18, 60)).sum()
)

# Check invalid weights
validation_report["Invalid_Weight"] = (
    (~df_clean["Weight"].between(100, 400)).sum()
)

# Check invalid salaries
validation_report["Negative_Salary"] = (
    (df_clean["Salary"] < 0).sum()
)

# Check invalid height format
height_pattern = r"^\d+-\d+$"

validation_report["Invalid_Height_Format"] = (
    ~df_clean["Height"].str.fullmatch(
        height_pattern, na=False
    )
).sum()

# Check invalid height inches
height_parts = df_clean["Height"].str.split("-", expand=True)

height_inches = pd.to_numeric(
    height_parts[1], errors="coerce"
)

validation_report["Invalid_Height_Inches"] = (
    (~height_inches.between(0, 11)).sum()
)

# Display report
print("BUSINESS RULE VALIDATION REPORT")

for rule, count in validation_report.items():
    print(f"{rule}: {count}")

# %%

from sqlalchemy import text

with engine.connect() as conn:

    # Current database
    database = conn.execute(
        text("SELECT DATABASE()")
    ).scalar()

    print("Connected Database:", database)

    # Available tables
    tables = conn.execute(
        text("SHOW TABLES")
    ).fetchall()

    print("\nAvailable Tables:")

    for table in tables:
        print(table[0])

# %%

from sqlalchemy import text

create_table_query = """
CREATE TABLE IF NOT EXISTS nba_players (

    player_id INT AUTO_INCREMENT PRIMARY KEY,

    Name VARCHAR(100) NOT NULL,
    Team VARCHAR(100) NOT NULL,
    Number INT,
    Position VARCHAR(10),
    Age INT,
    Height VARCHAR(10),
    Weight INT,
    College VARCHAR(150),
    Salary DECIMAL(12,2),

    CONSTRAINT uq_nba_player
    UNIQUE (Name, Team, Number)

);
"""

with engine.begin() as conn:
    conn.execute(text(create_table_query))

print("Target table created successfully!")

# %%

from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("DESCRIBE nba_players")
    )

    for row in result:
        print(row)

# %%

with engine.connect() as conn:

    indexes = conn.execute(
        text("SHOW INDEX FROM nba_players")
    )

    for row in indexes:
        print(row)

    count = conn.execute(
        text("SELECT COUNT(*) FROM nba_players")
    ).scalar()

    print("\nCurrent Records:", count)

# %%

df_clean.to_sql(
    name="nba_players",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=100
)

print("Initial Data Load Completed!")

# %%

with engine.connect() as conn:

    count = conn.execute(
        text("SELECT COUNT(*) FROM nba_players")
    ).scalar()

    print("Records Loaded:", count)

# %%

from sqlalchemy import text

with engine.connect() as conn:

    # 1. Total Records
    total = conn.execute(
        text("SELECT COUNT(*) FROM nba_players")
    ).scalar_one()

    # 2. Duplicate Records
    duplicates = conn.execute(text("""
        SELECT COUNT(*)
        FROM (
            SELECT Name, Team, Number
            FROM nba_players
            GROUP BY Name, Team, Number
            HAVING COUNT(*) > 1
        ) AS duplicate_records
    """)).scalar_one()

    # 3. Missing Values
    missing = conn.execute(text("""
        SELECT
            SUM(Name IS NULL) AS missing_name,
            SUM(Team IS NULL) AS missing_team,
            SUM(Salary IS NULL) AS missing_salary
        FROM nba_players
    """)).fetchone()

    # 4. Sample Records
    sample = conn.execute(text("""
        SELECT *
        FROM nba_players
        LIMIT 5
    """)).fetchall()

    print("===== DATA QUALITY REPORT =====")
    print("Total Records:", total)
    print("Duplicate Groups:", duplicates)
    print("Missing Name:", missing[0])
    print("Missing Team:", missing[1])
    print("Missing Salary:", missing[2])

    print("\nSample Records:")
    for row in sample:
        print(row)

# %%

with engine.connect() as conn:

    result = conn.execute(text("""
        SELECT
            player_id,
            Name,
            Team,
            Salary
        FROM nba_players
        WHERE Salary IS NULL
        ORDER BY player_id
    """))

    missing_salary_df = pd.DataFrame(
        result.fetchall(),
        columns=result.keys()
    )

display(missing_salary_df)

print("Missing Salary Records:", len(missing_salary_df))

# %%

# SOURCE VALIDATION
source_missing = df_clean["Salary"].isna().sum()

# TARGET VALIDATION
with engine.connect() as conn:

    target_missing = conn.execute(text("""
        SELECT COUNT(*)
        FROM nba_players
        WHERE Salary IS NULL
    """)).scalar_one()

    total_records = conn.execute(text("""
        SELECT COUNT(*)
        FROM nba_players
    """)).scalar_one()

print("===== SOURCE vs TARGET VALIDATION =====")

print("Source Missing Salary:", source_missing)
print("Target Missing Salary:", target_missing)
print("Target Total Records:", total_records)

if source_missing == target_missing and total_records == len(df_clean):
    print("VALIDATION PASSED")
else:
    print("VALIDATION FAILED")

# %%

import json
import re
from pathlib import Path

p = Path("use_case_1.ipynb")
nb = json.loads(p.read_text())

for i, cell in enumerate(nb["cells"]):
    source = "".join(cell.get("source", []))

    for line_no, line in enumerate(source.splitlines(), 1):
        if re.search(r"(?i)\b(password|passwd|pwd)\s*=", line):
            safe_line = re.sub(
                r"(?i)(password|passwd|pwd)(\s*=\s*).*",
                r"\1\2[HIDDEN]",
                line
            )
            print(f"Cell {i}, Line {line_no}: {safe_line}")

# %%

from sqlalchemy import text

try:
    with engine2.connect() as conn:
        result = conn.execute(
            text("SELECT VERSION(), DATABASE(), CURRENT_USER()")
        )

        print("DATABASE CONNECTION SUCCESSFUL!")

        for row in result:
            print("MySQL Version:", row[0])
            print("Database:", row[1])
            print("User:", row[2])

except Exception as e:
    print("DATABASE CONNECTION FAILED!")
    print("Error:", e)

# %%

from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(
        text("CREATE DATABASE IF NOT EXISTS test_cases")
    )

print("Database test_cases created successfully!")

# %%

with engine2.connect() as conn:
    result = conn.execute(
        text("SELECT VERSION(), DATABASE(), CURRENT_USER()")
    )

    for row in result:
        print("MySQL Version:", row[0])
        print("Database:", row[1])
        print("User:", row[2])

# %%

with engine2.connect() as conn:

    result = conn.execute(text("SHOW TABLES"))

    tables = result.fetchall()

    print("TABLES IN test_cases DATABASE:")

    for table in tables:
        print(table[0])

# %%

# Run the same ETL pipeline again
upsert_load(df, engine)

# %%

with engine.connect() as conn:

    result = conn.execute(text("""
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT NAME) AS unique_players
        FROM nba_players
    """))

    row = result.fetchone()

    print("Total Records:", row[0])
    print("Unique Players:", row[1])

    if row[0] == row[1]:
        print("DATA VALIDATION PASSED!")
    else:
        print("DUPLICATE RECORDS FOUND!")

# %%

from getpass import getpass

mysql_password = getpass("MySQL password: ")

# %%

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=mysql_password,
    host="localhost",
    port=3306,
    database="test_cases"
)

engine = create_engine(connection_url)

# %%

connection_url_2 = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=mysql_password,
    host="localhost",
    port=3306,
    database="test_cases"
)

engine2 = create_engine(connection_url_2)

# %%

from getpass import getpass

mysql_password = getpass("MySQL password: ")
