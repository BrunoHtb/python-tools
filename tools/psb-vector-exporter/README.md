# PSB Vector Exporter

Exports vector paths embedded in Photoshop PSB files into georeferenced GIS layers (GeoPackage),
using the corresponding TFW file for pixel-to-world transformation.

## What it does
- Reads `.psb` + matching `.tfw`
- Extracts named vector paths (filters by "fx")
- Samples Bézier curves into points
- Converts pixels to projected coordinates
- Exports polygons/lines to `.gpkg`

## Setup
Copy `config.example.ini` → `config.ini` and set:
- input_dir
- output_dir
- utm_zone

## Usage
```bash
poetry install
poetry run python main.py
