# Web Scraping — Dynamic Real Estate Crawler

Crawler that collects property listing URLs and extracts structured data from JavaScript-rendered pages using Playwright.

## What it does
- Navigates paginated listing pages
- Scrolls and captures dynamically loaded cards
- Extracts property details from individual pages
- Outputs structured CSV datasets

## Output
- data/imoveis_links.csv
- data/imoveis_detalhes.csv

## Usage
```bash
python main.py
