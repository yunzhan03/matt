import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from alloydata.csv_import import validate_csv


HEADER = "sample_id,heat_id,composition,casting_process,heat_treatment,test_standard,source"


def csv_with(*rows):
    return "\n".join((HEADER,) + rows)


class CsvImportTest(unittest.TestCase):
    def test_valid_rows_all_pass(self):
        text = csv_with(
            "S001,H1,Al:90;Si:9;Mg:0.5;Zr:0.2,high_pressure_die_cast,as_cast,ASTM B117,doi:10.1000/a",
            "S002,H1,Al:89.2;Si:9.5;Mg:0.5;Mn:0.4,high_pressure_die_cast,T5,ASTM B117,doi:10.1000/b",
        )

        report = validate_csv(text)

        self.assertEqual([row.status for row in report.rows], ["ok", "ok"])

    def test_one_bad_row_does_not_stop_the_batch(self):
        text = csv_with(
            "S001,H1,Al:90;Si:9;Mg:0.5,high_pressure_die_cast,as_cast,ASTM B117,doi:10.1000/a",
            "S002,H1,Al:90;Si:9;Mg:0.5,not_a_process,as_cast,ASTM B117,doi:10.1000/b",
            "S003,H1,Al:90;Si:9;Mg:0.5,high_pressure_die_cast,T6,ASTM B117,doi:10.1000/c",
        )

        report = validate_csv(text)

        self.assertEqual([row.status for row in report.rows], ["ok", "error", "ok"])

    def test_report_carries_line_number_and_error_code(self):
        text = csv_with(
            "S001,H1,Al:90;Si:9;Mg:0.5,high_pressure_die_cast,as_cast,ASTM B117,",
        )

        report = validate_csv(text)
        row = report.rows[0]

        self.assertEqual(row.line_number, 2)
        self.assertIn("MISSING_SOURCE", [issue.code for issue in row.issues])

    def test_unparsable_composition_cell_is_reported(self):
        text = csv_with(
            "S001,H1,Al90;Si:9,high_pressure_die_cast,as_cast,ASTM B117,doi:10.1000/a",
        )

        report = validate_csv(text)

        self.assertIn("BAD_COMPOSITION_FORMAT", [i.code for i in report.rows[0].issues])
