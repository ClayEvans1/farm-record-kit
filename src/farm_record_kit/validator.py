from __future__ import annotations

from dataclasses import dataclass
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


SCHEMAS = {
    "harvest_log": {
        "required": ["date", "crop", "variety", "quantity", "unit", "destination"],
        "date": ["date"],
        "decimal": ["quantity"],
    },
    "market_sales": {
        "required": ["date", "market", "item", "quantity", "unit_price", "line_total"],
        "date": ["date"],
        "decimal": ["quantity", "unit_price", "line_total"],
        "computed_total": ("quantity", "unit_price", "line_total"),
    },
    "crops": {
        "required": ["crop", "category", "season", "status"],
        "status": ["active", "inactive"],
    },
}


@dataclass(frozen=True)
class Issue:
    path: str
    row: int
    column: str
    code: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    path: str
    schema: str | None
    issues: tuple[Issue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def validate_file(path: str | Path) -> ValidationResult:
    csv_path = Path(path)
    text_path = str(csv_path)
    schema_name = _infer_schema(csv_path)
    issues: list[Issue] = []

    if schema_name is None:
        return ValidationResult(text_path, None, (Issue(text_path, 1, "", "schema.unknown", "unknown CSV template type"),))

    try:
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            _validate_headers(text_path, schema_name, fieldnames, issues)
            for row_number, row in enumerate(reader, start=2):
                _validate_row(text_path, schema_name, row_number, row, issues)
    except UnicodeDecodeError:
        issues.append(Issue(text_path, 1, "", "file.encoding", "file is not valid UTF-8"))
    except FileNotFoundError:
        issues.append(Issue(text_path, 1, "", "file.missing", "file does not exist"))

    return ValidationResult(text_path, schema_name, tuple(issues))


def _infer_schema(path: Path) -> str | None:
    name = path.stem.lower().replace("-", "_")
    if name in SCHEMAS:
        return name
    if "harvest" in name:
        return "harvest_log"
    if "market" in name or "sales" in name:
        return "market_sales"
    if "crop" in name:
        return "crops"
    return None


def _validate_headers(path: str, schema_name: str, fieldnames: list[str], issues: list[Issue]) -> None:
    normalized = {_normalize_header(name) for name in fieldnames}
    for column in SCHEMAS[schema_name]["required"]:
        if column not in normalized:
            issues.append(Issue(path, 1, column, "header.required", f"missing required column: {column}"))


def _validate_row(path: str, schema_name: str, row_number: int, row: dict[str, str], issues: list[Issue]) -> None:
    normalized = {_normalize_header(key): (value or "").strip() for key, value in row.items() if key is not None}
    schema = SCHEMAS[schema_name]

    for column in schema["required"]:
        if not normalized.get(column):
            issues.append(Issue(path, row_number, column, "value.required", "required value is blank"))

    for column in schema.get("date", []):
        value = normalized.get(column)
        if value and not _is_iso_date(value):
            issues.append(Issue(path, row_number, column, "value.date", "date must use YYYY-MM-DD"))

    for column in schema.get("decimal", []):
        value = normalized.get(column)
        if value and _parse_decimal(value) is None:
            issues.append(Issue(path, row_number, column, "value.decimal", "value must be numeric"))
        elif value and _parse_decimal(value) < Decimal("0"):
            issues.append(Issue(path, row_number, column, "value.negative", "value must be nonnegative"))

    allowed_status = schema.get("status")
    if allowed_status and normalized.get("status") and normalized["status"].lower() not in allowed_status:
        allowed = ", ".join(allowed_status)
        issues.append(Issue(path, row_number, "status", "value.status", f"status must be one of: {allowed}"))

    if "computed_total" in schema:
        quantity_col, price_col, total_col = schema["computed_total"]
        quantity = _parse_decimal(normalized.get(quantity_col, ""))
        price = _parse_decimal(normalized.get(price_col, ""))
        total = _parse_decimal(normalized.get(total_col, ""))
        if quantity is not None and price is not None and total is not None:
            expected = (quantity * price).quantize(Decimal("0.01"))
            actual = total.quantize(Decimal("0.01"))
            if expected != actual:
                issues.append(
                    Issue(path, row_number, total_col, "value.total", f"line_total should be {expected}")
                )


def _normalize_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _parse_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value.replace(",", "").replace("$", "").strip())
    except (InvalidOperation, AttributeError):
        return None
