# MultiDrive Indexer

A high-performance Python utility designed to catalog and track files across multiple storage devices (HDDs/SSDs) into a centralized PostgreSQL database.

## Key Features
* **Hardware Identification:** Automatically detects Disk Label and Serial Number (Windows/WMI) to track exactly which physical device holds each file.
* **Multi-Root Support:** Scans multiple drives or directories in a single execution.
* **High Performance:** Uses `execute_batch` and `Upsert` (ON CONFLICT) logic to handle thousands of records efficiently.
* **Metadata Tracking:** Catalogs structured folder trees, file paths, and last-modified timestamps.

## Setup
1.  **Install dependencies:**
    ```bash
    pip install wmi psycopg2
    ```
2.  **Configure Environment:**
    Copy `config.example.ini` to `config.ini` and fill in your database credentials and the root paths to scan.

## Usage
```bash
python main.py

---

```ini
[FILESYSTEM]
root =
    K:\YOUR_BACKUP_PATH
    L:\ANOTHER_DRIVE
entregas_dir = diretorio_padrao_todos_hds

[POSTGRES]
host = localhost
database = your_db_name
user = postgres
password = your_password
port = 5432

[EXECUTION]
batch_size = 10000