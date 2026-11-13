"""Pure validation functions: dict in, list of issues out."""

from collections.abc import Mapping

from .record import (
    CASTING_PROCESSES,
    DEFAULT_SUM_TOLERANCE,
    DESIGN_SPACE,
    HEAT_TREATMENTS,
    KNOWN_ELEMENTS,
    REQUIRED_FIELDS,
    SOURCE_PLACEHOLDERS,
    Issue,
)


def _is_blank(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_record(record, *, sum_tolerance: float = DEFAULT_SUM_TOLERANCE) -> list[Issue]:
    """Check one record against the field contract."""
    if not isinstance(record, Mapping):
        return [Issue("BAD_RECORD", "", "record must be a mapping")]

    issues: list[Issue] = []

    for field in REQUIRED_FIELDS:
        if field in record and not _is_blank(record[field]):
            continue
        if field == "source":
            issues.append(Issue("MISSING_SOURCE", field, "source must identify where the record came from"))
        else:
            issues.append(Issue("MISSING_FIELD", field, f"{field} is required"))

    process = record.get("casting_process")
    if not _is_blank(process) and process not in CASTING_PROCESSES:
        issues.append(
            Issue("UNKNOWN_ENUM", "casting_process", f"{process!r} is not a known casting process")
        )

    treatment = record.get("heat_treatment")
    if not _is_blank(treatment) and treatment not in HEAT_TREATMENTS:
        issues.append(
            Issue("UNKNOWN_ENUM", "heat_treatment", f"{treatment!r} is not a known heat treatment")
        )

    source = record.get("source")
    if not _is_blank(source) and str(source).strip().lower() in SOURCE_PLACEHOLDERS:
        issues.append(
            Issue("MISSING_SOURCE", "source", "source must identify where the record came from")
        )

    composition = record.get("composition")
    composition_issues = _validate_composition(composition, sum_tolerance)
    issues.extend(composition_issues)

    return issues


def _validate_composition(composition, sum_tolerance: float) -> list[Issue]:
    if composition is None:
        return []
    if not isinstance(composition, Mapping):
        return [Issue("BAD_COMPOSITION", "composition", "composition must be a mapping of element to wt.%")]
    if not composition:
        return []

    issues: list[Issue] = []
    total = 0.0
    has_bad_amount = False

    for element, amount in composition.items():
        field = f"composition.{element}"
        if element not in KNOWN_ELEMENTS:
            issues.append(Issue("UNKNOWN_ELEMENT", field, f"{element!r} is not a known element symbol"))
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            issues.append(Issue("BAD_AMOUNT", field, f"{amount!r} is not a number"))
            has_bad_amount = True
            continue
        if amount < 0:
            issues.append(Issue("NEGATIVE_AMOUNT", field, f"{amount} is negative"))
            has_bad_amount = True
        total += float(amount)

    if not has_bad_amount and abs(total - 100.0) > sum_tolerance:
        issues.append(
            Issue(
                "COMPOSITION_SUM",
                "composition",
                f"composition sums to {total:.2f}, expected 100 +/- {sum_tolerance}",
            )
        )

    return issues


def check_design_space(record, design_space=None) -> list[Issue]:
    """Check a record against the design-space box. Warnings, not validity errors."""
    space = DESIGN_SPACE if design_space is None else design_space
    composition = record.get("composition") if isinstance(record, Mapping) else None
    if not isinstance(composition, Mapping):
        return []

    issues: list[Issue] = []
    for element, amount in composition.items():
        field = f"composition.{element}"
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            continue
        if element not in space:
            issues.append(
                Issue("OUTSIDE_DESIGN_SPACE", field, f"{element} is not part of the design-space element pool")
            )
            continue
        low, high = space[element]
        if not low <= amount <= high:
            issues.append(
                Issue(
                    "OUTSIDE_DESIGN_SPACE",
                    field,
                    f"{element}={amount} is outside [{low}, {high}]",
                )
            )

    return issues
