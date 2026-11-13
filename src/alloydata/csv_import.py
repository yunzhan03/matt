"""Batch validation for CSV exports, one bad row never stops the batch."""

import csv
import io
from dataclasses import dataclass, field

from .record import DEFAULT_SUM_TOLERANCE, Issue
from .validate import validate_record


@dataclass
class RowReport:
    line_number: int
    status: str
    issues: list[Issue] = field(default_factory=list)


@dataclass
class CsvReport:
    rows: list[RowReport] = field(default_factory=list)

    @property
    def ok_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "ok")

    @property
    def error_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "error")


def parse_composition(cell: str) -> tuple[dict | None, Issue | None]:
    """Parse `Al:90;Si:9;Mg:0.5` into a mapping."""
    composition: dict[str, float] = {}
    for chunk in filter(None, (part.strip() for part in str(cell).split(";"))):
        if ":" not in chunk:
            return None, Issue("BAD_COMPOSITION_FORMAT", "composition", f"{chunk!r} is not element:amount")
        element, _, raw = chunk.partition(":")
        try:
            composition[element.strip()] = float(raw)
        except ValueError:
            return None, Issue("BAD_COMPOSITION_FORMAT", "composition", f"{chunk!r} has a non-numeric amount")
    if not composition:
        return None, Issue("BAD_COMPOSITION_FORMAT", "composition", "composition cell is empty")
    return composition, None


def validate_csv(text: str, *, sum_tolerance: float = DEFAULT_SUM_TOLERANCE) -> CsvReport:
    reader = csv.DictReader(io.StringIO(text.strip()))
    report = CsvReport()

    for offset, raw_row in enumerate(reader):
        line_number = offset + 2
        record = {key: (value.strip() if isinstance(value, str) else value) for key, value in raw_row.items()}

        issues: list[Issue] = []
        composition, composition_issue = parse_composition(record.get("composition") or "")
        if composition_issue is not None:
            issues.append(composition_issue)
            record["composition"] = {}
        else:
            record["composition"] = composition

        issues.extend(validate_record(record, sum_tolerance=sum_tolerance))
        report.rows.append(
            RowReport(line_number=line_number, status="error" if issues else "ok", issues=issues)
        )

    return report
