# Farm Record Kit

Small-farm CSV templates and validation tools for harvest, market, and crop records.

`farm-record-kit` is intentionally plain: it uses CSV files that work in Excel,
Numbers, Google Sheets, LibreOffice, or a text editor. The CLI helps catch common
recordkeeping mistakes before a farm season's notes become hard to reconcile.

## What it checks

- Harvest logs with dates, crop names, units, quantities, and destinations.
- Market sales logs with items, quantities, unit prices, and line totals.
- Crop lists with crop names, categories, seasons, and active/inactive status.
- Required columns, valid dates, numeric quantities, nonnegative prices, and
  sales line totals.

The tool runs locally and does not upload farm records anywhere.

## Install

```bash
python -m pip install .
```

For local development:

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Usage

Validate all CSV files in a directory:

```bash
farm-record-kit validate templates
```

Validate one file:

```bash
farm-record-kit validate templates/harvest_log.csv
```

Print JSON:

```bash
farm-record-kit validate --json templates
```

## Templates

- `templates/harvest_log.csv`
- `templates/market_sales.csv`
- `templates/crops.csv`

Copy the templates into your own farm folder and edit the rows. Keep the column
headers unchanged if you want the validator to understand the file.

## License

MIT
