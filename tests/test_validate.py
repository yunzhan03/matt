import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from alloydata.validate import validate_record


def valid_record(**overrides):
    record = {
        "sample_id": "S001",
        "heat_id": "H-2026-01",
        "composition": {"Al": 90.0, "Si": 9.0, "Mg": 0.5, "Zr": 0.2, "Mn": 0.3},
        "casting_process": "vacuum_high_pressure_die_cast",
        "heat_treatment": "as_cast",
        "test_standard": "ASTM B117",
        "source": "doi:10.1016/j.msea.2014.01.001",
    }
    record.update(overrides)
    return record


class MissingFieldTest(unittest.TestCase):
    def test_missing_required_field_is_reported_with_its_name(self):
        record = valid_record()
        del record["heat_id"]

        issues = validate_record(record)

        self.assertIn(("MISSING_FIELD", "heat_id"), [(i.code, i.field) for i in issues])

    def test_empty_required_field_is_reported(self):
        issues = validate_record(valid_record(sample_id="  "))

        self.assertIn(("MISSING_FIELD", "sample_id"), [(i.code, i.field) for i in issues])


class EnumTest(unittest.TestCase):
    def test_unknown_casting_process_is_rejected(self):
        issues = validate_record(valid_record(casting_process="sand cast"))

        self.assertIn(("UNKNOWN_ENUM", "casting_process"), [(i.code, i.field) for i in issues])

    def test_unknown_heat_treatment_is_rejected(self):
        issues = validate_record(valid_record(heat_treatment="T7"))

        self.assertIn(("UNKNOWN_ENUM", "heat_treatment"), [(i.code, i.field) for i in issues])


class SourceTest(unittest.TestCase):
    def test_placeholder_sources_are_rejected(self):
        for placeholder in ["", "  ", "n/a", "N/A", "unknown", "待补", "-"]:
            with self.subTest(source=placeholder):
                issues = validate_record(valid_record(source=placeholder))

                self.assertIn(("MISSING_SOURCE", "source"), [(i.code, i.field) for i in issues])

    def test_real_source_is_accepted(self):
        issues = validate_record(valid_record(source="doi:10.1000/xyz"))

        self.assertEqual(issues, [])


class HappyPathTest(unittest.TestCase):
    def test_valid_record_returns_no_issues(self):
        self.assertEqual(validate_record(valid_record()), [])

    def test_never_raises_on_garbage_shape(self):
        issues = validate_record({"composition": "not a dict"})

        self.assertTrue(issues)
        self.assertTrue(all(hasattr(issue, "code") for issue in issues))
