# Photoshop Actions Automator

Batch automation tool that processes TIFF images in Adobe Photoshop by loading ATN action sets and executing filter + export actions.

## What it does
- Connects to Photoshop via COM (win32com)
- Ensures ActionSets are uniquely loaded (removes duplicates)
- Filters files by keyword and extension
- Applies configurable ATN actions (filter + export)
- Closes documents without saving

## Setup
Copy `config.example.ini` to `config.ini` and set:
- input/output folders
- keyword filter
- ATN paths
- action set and action names

## Usage
```bash
python main.py
