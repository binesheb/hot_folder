import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import find_rule_for_path, parse_rule


class RuleParsingTests(unittest.TestCase):
    def test_supported_rules(self):
        self.assertEqual(parse_rule("A4_Simplex").paper, "A4")
        self.assertEqual(parse_rule("A4_Simplex").sides, "simplex")
        self.assertEqual(parse_rule("A4_Duplex").sides, "duplex")
        self.assertEqual(parse_rule("A5-Duplex").paper, "A5")
        self.assertEqual(parse_rule("a5_duplex").sides, "duplex")

    def test_unknown_names_rejected(self):
        for name in ("A3_Simplex", "A4_Color", "A4 Duplex", "Simplex", "A4_Duplex_old"):
            with self.subTest(name=name):
                self.assertIsNone(parse_rule(name))

    def test_nearest_rule_folder_wins(self):
        root = Path("/tmp/printqueue")
        file_path = root / "A4_Duplex" / "nested" / "sample.pdf"
        rule = find_rule_for_path(file_path, root)
        self.assertEqual(rule.paper, "A4")
        self.assertEqual(rule.sides, "duplex")

    def test_file_outside_root_rejected(self):
        self.assertIsNone(find_rule_for_path(Path("/tmp/elsewhere/sample.pdf"), Path("/tmp/printqueue")))


if __name__ == "__main__":
    unittest.main()
