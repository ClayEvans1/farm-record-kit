from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .validator import Issue, ValidationResult, validate_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate small-farm CSV record templates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate CSV files")
    validate.add_argument("paths", nargs="+", help="CSV files or directories")
    validate.add_argument("--json", action="store_true", help="emit JSON")

    args = parser.parse_args(argv)

    if args.command == "validate":
        return _validate(args.paths, as_json=args.json)

    parser.error(f"unknown command: {args.command}")
    return 2


def _validate(paths: list[str], as_json: bool) -> int:
    files = _iter_csv_files(paths)
    if not files:
        print("No CSV files found.", file=sys.stderr)
        return 2

    results = [validate_file(path) for path in files]
    if as_json:
        print(json.dumps([_result_to_json(result) for result in results], indent=2))
    else:
        _print_text(results)

    return 1 if any(not result.ok for result in results) else 0


def _iter_csv_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(sorted(candidate for candidate in path.rglob("*.csv") if candidate.is_file()))
        elif path.is_file() and path.suffix.lower() == ".csv":
            files.append(path)
    return files


def _print_text(results: list[ValidationResult]) -> None:
    issue_count = 0
    for result in results:
        if result.ok:
            print(f"OK {result.path} ({result.schema})")
            continue
        for issue in result.issues:
            issue_count += 1
            print(f"{issue.path}:{issue.row}: {issue.column}: {issue.code}: {issue.message}")

    if issue_count:
        print(f"\n{issue_count} issue(s) found.", file=sys.stderr)
    else:
        print(f"\n{len(results)} file(s) passed.")


def _result_to_json(result: ValidationResult) -> dict[str, object]:
    return {
        "path": result.path,
        "schema": result.schema,
        "ok": result.ok,
        "issues": [
            {
                "row": issue.row,
                "column": issue.column,
                "code": issue.code,
                "message": issue.message,
            }
            for issue in result.issues
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
