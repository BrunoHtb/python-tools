# Merge RGB + Infra (GeoTIFF)

Utility to merge paired RGB and infrared GeoTIFFs into a single multi-band output using GDAL (via QGIS OSGeo4W).

## Requirements
- QGIS installed (OSGeo4W.bat available)
- Input files named as: `<name>_RGB.tif` and `<name>_INF.tif`

## Setup
Create `folder.txt` with:
1) Input folder path
2) Path to OSGeo4W.bat

## Usage
```bash
python main.py
