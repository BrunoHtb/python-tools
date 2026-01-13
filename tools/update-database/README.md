# Update Database

Utility to execute and schedule PostgreSQL SQL scripts with transaction control.

## What it does
- Reads an external `.sql` file path
- Executes SQL commands sequentially
- Commits or rolls back on failure
- Schedules periodic execution (every 3 hours)

## Configuration
Set environment variables:
- DB_HOST
- DB_NAME
- DB_USER
- DB_PASSWORD

Create `caminho_script_sql.txt` pointing to the SQL file.

## Usage
```bash
python main.py
