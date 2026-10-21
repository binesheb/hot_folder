import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import completed_destination, find_rule_for_path, move_to_completed, parse_rule


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


class CompletedArchiveTests(unittest.TestCase):
    def test_archive_preserves_rule_and_nested_folder_structure(self):
        root = Path("/tmp/printqueue")
        source = root / "A4_Simplex" / "branch" / "invoice.pdf"
        self.assertEqual(
            completed_destination(source, root),
            root.resolve() / "Completed" / "A4_Simplex" / "branch" / "invoice.pdf",
        )

    def test_archive_does_not_requeue_completed_files(self):
        root = Path("/tmp/printqueue")
        source = root / "Completed" / "A4_Simplex" / "invoice.pdf"
        self.assertIsNone(completed_destination(source, root))

    def test_archive_rejects_files_outside_root(self):
        self.assertIsNone(
            completed_destination(Path("/tmp/outside/invoice.pdf"), Path("/tmp/printqueue"))
        )

    def test_move_to_completed_moves_file_and_preserves_content(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "queue"
            source = root / "A4_Duplex" / "invoice.pdf"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"test pdf bytes")
            ok, message = move_to_completed(source, root)
            archived = root / "Completed" / "A4_Duplex" / "invoice.pdf"
            self.assertTrue(ok, message)
            self.assertFalse(source.exists())
            self.assertEqual(archived.read_bytes(), b"test pdf bytes")

    def test_move_to_completed_never_overwrites_archive_collision(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "queue"
            source = root / "A4_Simplex" / "invoice.pdf"
            archived = root / "Completed" / "A4_Simplex" / "invoice.pdf"
            source.parent.mkdir(parents=True)
            archived.parent.mkdir(parents=True)
            source.write_bytes(b"new")
            archived.write_bytes(b"old")
            ok, _ = move_to_completed(source, root)
            self.assertTrue(ok)
            self.assertEqual(archived.read_bytes(), b"old")
            self.assertEqual((archived.parent / "invoice (1).pdf").read_bytes(), b"new")


if __name__ == "__main__":
    unittest.main()
