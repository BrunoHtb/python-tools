# ParanamaP Backup Catalog

Utility that catalogs a structured filesystem (deliveries) into PostgreSQL, including disk label/serial metadata, file paths and last-modified timestamps.

## What it does
- Detects disk label and serial (Windows/WMI)
- Walks a structured deliveries folder tree
- Inserts file metadata into PostgreSQL in batches
- Upserts updates when files change

## Setup
Copy `config.example.ini` to `config.ini` and fill your values.

## Usage
```bash
python main.py
