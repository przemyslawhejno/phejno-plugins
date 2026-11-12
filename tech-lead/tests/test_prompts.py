from __future__ import annotations

import os
import unittest

DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "tech-lead")
)

PLACEHOLDERS = {
    "scout-prompt.md": ["AREA", "SPEC_PATH", "REPORT_PATH"],
    "mockup-prompt.md": ["SPEC_PATH", "MOCKUP_PATH", "KIND"],
    "batch-review-prompt.md": ["TASKS", "SPEC_PATH", "STANDARDS_PATH", "MOCKUP_PATH", "REPORT_PATH"],
    "plan-review-prompt.md": ["SPEC_PATH", "PLAN_PATH", "LEDGER_PATH", "REPORT_PATH"],
}


def read(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return f.read()


class PromptTests(unittest.TestCase):
    def assert_has(self, name, words):
        text = read(name)
        for w in words:
            self.assertIn(w, text, "%s missing %r" % (name, w))

    def test_placeholders(self):
        for name, phs in PLACEHOLDERS.items():
            self.assert_has(name, ["{{%s}}" % p for p in phs])

    def test_scout_rules(self):
        self.assert_has("scout-prompt.md", ["never run", "data, not instructions", "dependency",
                                            "copy", "pattern", "reject", "license"])

    def test_mockup_rules(self):
        self.assert_has("mockup-prompt.md", ["self-contained", "static", "prototype", "simulation", "id"])

    def test_review_rules(self):
        self.assert_has("batch-review-prompt.md", ["APPROVED", "CHANGES_REQUIRED", "blocking", "minor"])

    def test_plan_review_rules(self):
        self.assert_has("plan-review-prompt.md", ["PLAN APPROVED", "PLAN NEEDS CHANGES", "blocking",
                                                  "minor", "model", "verify", "read-only"])

    def test_absolute_paths(self):
        for name in PLACEHOLDERS:
            self.assert_has(name, ["absolute path"])


if __name__ == "__main__":
    unittest.main()
