import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from alloydata.validate import check_design_space, validate_record


def record_with(**composition):
    return {
        "sample_id": "S001",
        "heat_id": "H-2026-01",
        "composition": composition,
        "casting_process": "high_pressure_die_cast",
        "heat_treatment": "as_cast",
        "test_standard": "ASTM B117",
        "source": "doi:10.1000/xyz",
    }


class CompositionRuleTest(unittest.TestCase):
    def test_unknown_element_is_rejected(self):
        issues = validate_record(record_with(Al=90.0, Si=9.0, Mg=0.5, Xx=0.5))

        self.assertIn(("UNKNOWN_ELEMENT", "composition.Xx"), [(i.code, i.field) for i in issues])

    def test_negative_amount_is_rejected(self):
        issues = validate_record(record_with(Al=90.0, Si=9.0, Mg=0.5, Zr=-0.1))

        self.assertIn(("NEGATIVE_AMOUNT", "composition.Zr"), [(i.code, i.field) for i in issues])

    def test_sum_outside_default_tolerance_is_rejected(self):
        issues = validate_record(record_with(Al=85.0, Si=9.0, Mg=0.5))

        self.assertIn("COMPOSITION_SUM", [i.code for i in issues])

    def test_sum_tolerance_is_configurable(self):
        issues = validate_record(record_with(Al=85.0, Si=9.0, Mg=0.5), sum_tolerance=6.0)

        self.assertNotIn("COMPOSITION_SUM", [i.code for i in issues])

    def test_non_numeric_amount_is_rejected(self):
        issues = validate_record(record_with(Al="90", Si=9.5, Mg=0.5))

        self.assertIn(("BAD_AMOUNT", "composition.Al"), [(i.code, i.field) for i in issues])


class DesignSpaceTest(unittest.TestCase):
    def test_element_outside_design_space_is_flagged(self):
        issues = check_design_space(record_with(Al=90.0, Si=9.0, Mg=0.5, Zr=0.9))

        self.assertIn(("OUTSIDE_DESIGN_SPACE", "composition.Zr"), [(i.code, i.field) for i in issues])

    def test_element_not_in_design_space_pool_is_flagged(self):
        issues = check_design_space(record_with(Al=90.0, Si=9.0, Mg=0.5, Ni=0.4))

        self.assertIn(("OUTSIDE_DESIGN_SPACE", "composition.Ni"), [(i.code, i.field) for i in issues])

    def test_design_space_violation_is_not_a_validity_error(self):
        record = record_with(Al=90.0, Si=9.0, Mg=0.5, Zr=0.9)

        self.assertEqual(validate_record(record), [])
        self.assertTrue(check_design_space(record))

    def test_record_inside_design_space_passes(self):
        record = record_with(Al=90.0, Si=9.0, Mg=0.5, Zr=0.2, Mn=0.4, Ti=0.1, Sr=0.02)

        self.assertEqual(check_design_space(record), [])
