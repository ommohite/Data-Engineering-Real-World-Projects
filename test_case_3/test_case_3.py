# Author: Om Mohite
# Test Case 3: Python export of the corresponding Jupyter notebook.
# Run from this folder; configure DB_PASSWORD/DB_USER/DB_HOST/DB_PORT as needed.

import os
from pathlib import Path
from getpass import getpass

try:
    from IPython.display import display
except ImportError:
    display = print

from pathlib import Path
import sys
import pandas as pd
from dotenv import load_dotenv

REPO_ROOT = Path.cwd().resolve()
while REPO_ROOT != REPO_ROOT.parent and not (REPO_ROOT / 'Test_Cases' / 'TC01').exists():
    REPO_ROOT = REPO_ROOT.parent
if not (REPO_ROOT / 'Test_Cases' / 'TC01').exists():
    raise FileNotFoundError('Could not locate Test_Cases/TC01 from the current directory.')
PROJECT_DIR = REPO_ROOT / 'Test_Cases' / 'TC01'
sys.path.insert(0, str(PROJECT_DIR / 'src'))
load_dotenv(REPO_ROOT / 'Data-Engineering-Real-World-Projects' / '.env')
load_dotenv(REPO_ROOT / '.env', override=False)

from extract import create_source_engine, data_extraction
from transform import data_transformation, build_sales_reports

print('Project:', PROJECT_DIR)

# %%

# Extract from sales_source. Set DB_PASSWORD in .env or the environment first.
engine = create_source_engine()
try:
    sales_df = data_extraction(engine)
finally:
    engine.dispose()
print('Extracted rows:', len(sales_df))
print('Source columns:', sales_df.columns.tolist())
display(sales_df.head())
print('Missing values before cleaning:')
display(sales_df.isna().sum().to_frame('missing_count'))

# %%

# Clean rows and derive year, month, month name, and quarter.
transformed_df = data_transformation(sales_df)
print('Rows after cleaning:', len(transformed_df))
display(transformed_df.head())
print('Missing values after cleaning:')
display(transformed_df.isna().sum().to_frame('missing_count'))

# %%

# Total sales by year
yearly_report = transformed_df.groupby('year')['total_amount'].sum().sort_index()
display(yearly_report.to_frame('total_sales'))

# %%

# Monthly and quarterly reports for 2024
year_2024 = transformed_df.loc[transformed_df['year'] == 2024]
month_report_2024 = year_2024.groupby('month')['total_amount'].sum().reindex(range(1, 13), fill_value=0)
quarter_report_2024 = year_2024.groupby('quarter')['total_amount'].sum().reindex(range(1, 5), fill_value=0)
print('2024 monthly sales:')
display(month_report_2024.to_frame('total_sales'))
print('2024 quarterly sales:')
display(quarter_report_2024.to_frame('total_sales'))

# %%

# Monthly and quarterly reports for 2025
report_year = 2025
reports_2025 = build_sales_reports(transformed_df, report_year=report_year)
yearly_report = reports_2025['yearly_report']
monthly_report = reports_2025['monthly_report']
quarterly_report = reports_2025['quarterly_report']
print('Yearly totals:')
display(yearly_report.to_frame('total_sales'))
print('2025 monthly totals:')
display(monthly_report.to_frame('total_sales'))
print('2025 quarterly totals:')
display(quarterly_report.to_frame('total_sales'))
