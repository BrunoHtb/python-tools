# Check Image FTP

Audit tool that validates the existence of image files stored on an FTP server
against records stored in a PostgreSQL database.

## What it does

- Queries multiple tables in PostgreSQL
- Builds dynamic FTP paths based on registration date
- Checks if expected image files physically exist on the FTP server
- Generates CSV reports listing missing images

## Output

- DispSeg_falta_foto.csv
- PRU_falta_foto.csv
- SH_falta_foto.csv
- SV_falta_foto.csv

## Usage

```bash
python main.py
