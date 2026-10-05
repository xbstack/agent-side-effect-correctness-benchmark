import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark import state_matches
from suite import evaluate_suite


class BenchmarkTests(unittest.TestCase):
    def test_subset_state_matching(self):
        self.assertTrue(state_matches({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(state_matches({"a": 1}, {"a": 2}))

    def test_synthetic_suite(self):
        payload = json.loads((ROOT / "examples" / "synthetic-suite.json").read_text())
        report = evaluate_suite(payload)
        s = report["summary"]
        self.assertEqual(s["tasks"], 4)
        self.assertEqual(s["trials"], 12)
        self.assertEqual(s["passed"], 5)
        self.assertEqual(s["false_success_trials"], 6)
        self.assertEqual(s["state_mismatch_trials"], 4)
        self.assertEqual(s["duplicate_effect_trials"], 2)
        self.assertEqual(s["missing_effect_trials"], 3)
        self.assertEqual(s["forbidden_effect_trials"], 1)
        self.assertEqual(s["observed_all_pass_tasks"], 0)


if __name__ == "__main__":
    unittest.main()
