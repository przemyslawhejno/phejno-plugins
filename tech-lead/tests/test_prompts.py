from __future__ import annotations

import os
import unittest

DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "tech-lead")
)

LENS_NAMES = ["security", "data", "api", "architecture", "performance", "errors", "tests", "ui-ux"]

PLACEHOLDERS = {
    "scout-prompt.md": ["AREA", "SPEC_PATH", "REPORT_PATH"],
    "mockup-prompt.md": ["SPEC_PATH", "MOCKUP_PATH", "KIND"],
    "batch-review-prompt.md": ["TASKS", "SPEC_PATH", "STANDARDS_PATH", "MOCKUP_PATH", "CANDIDATES_PATH",
                               "REPORT_PATH"],
    "lens-review-prompt.md": ["LENS", "TASKS", "SPEC_PATH", "STANDARDS_PATH", "LENSES_PATH",
                              "CANDIDATES_PATH", "REPORT_PATH"],
    "inventory-prompt.md": ["CHANGES", "TEST_ROOTS", "CODE_ROOTS", "REPORT_PATH"],
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

    def test_lenses_cover_all(self):
        headings = [l[3:].strip() for l in read("lenses.md").splitlines() if l.startswith("## ")]
        for lens in LENS_NAMES:
            self.assertIn(lens, headings)
        self.assert_has("lenses.md", ["Lens yield: ", "Uses when installed"])

    def test_lens_review_rules(self):
        self.assert_has("lens-review-prompt.md", ["Important", "Minor", "not rendered", ".tech-lead/scratch/",
                                                  "read-only"])

    def test_inventory_read_only(self):
        self.assert_has("inventory-prompt.md", ["change nothing", "vulture", "knip"])

    def test_batch_review_hygiene(self):
        self.assert_has("batch-review-prompt.md", ["{{CANDIDATES_PATH}}", "obsolete", "duplicat", "ui-ux"])

    def test_plan_review_risk_and_hygiene(self):
        self.assert_has("plan-review-prompt.md", ["replaces", "risk", "hygiene", "Lens yield"])

    def test_mockup_standards(self):
        self.assert_has("mockup-prompt.md", ["WCAG 2.2", "2.4.11", "2.5.7", "2.5.8", "3.2.6", "3.3.7",
                                             "3.3.8", "modern-web-guidance", "resumed"])

    def test_codemap_navigation(self):
        for name in ["lens-review-prompt.md", "inventory-prompt.md", "batch-review-prompt.md",
                     "plan-review-prompt.md"]:
            self.assert_has(name, [".claude/codemap/"])

    def test_absolute_paths(self):
        for name in PLACEHOLDERS:
            self.assert_has(name, ["absolute path"])


if __name__ == "__main__":
    unittest.main()
