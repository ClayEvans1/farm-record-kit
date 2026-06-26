# Contributing

Thanks for helping improve `farm-record-kit`.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

Keep the project plain and offline. Templates should remain normal CSV files
that work in spreadsheet apps, and validation rules should explain the record
problem in terms a farm operator can fix.

## Good First Issues

- Add a template for CSA shares, farm stand inventory, or donations.
- Improve validation messages for spreadsheet users.
- Add summaries by crop, market, or month.
- Add examples for common market-garden workflows.
