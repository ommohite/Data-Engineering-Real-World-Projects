# Test Case 8

## Objective

Transform sales data into a monthly product revenue pivot.

## Files

- `test_case_8.py` — Python implementation exported or consolidated from the notebook.
- `test_case_8.sql` — MySQL schema, sample data, or SQL analysis used by this case.
- Jupyter notebook — step-by-step working version, when present in this folder.

## Run

1. Review the SQL file and run its schema/data setup in MySQL when applicable.
2. Configure `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in a local `.env` file if the Python script needs MySQL.
3. Run `python test_case_8.py` from this folder, or open the notebook and run its cells in order.

Python dependencies commonly used: `pandas`, `sqlalchemy`, `pymysql`, and `python-dotenv`. Some cases may require additional packages noted in the notebook.

## Notes

The SQL and Python files use the case-specific database and tables described in their source notebook. Case 19 and Case 20 read the `aggregation_test.sales` fixture from Test Case 18.
