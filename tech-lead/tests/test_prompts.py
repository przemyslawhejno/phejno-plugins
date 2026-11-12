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
    "plan-review-prompt.md": ["SPEC_PATH", "PLAN_PATH", "LEDGER_PATH", "STANDARDS_PATH", "REPORT_PATH"],
}


NEVER_SUPERDESIGN = "Never invoke the superdesign skill or the superdesign CLI."


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
        self.assert_has("mockup-prompt.md", ["self-contained", "static", "prototype", "simulation", 'id="'])

    def test_review_rules(self):
        self.assert_has("batch-review-prompt.md", ["APPROVED", "CHANGES_REQUIRED", "none"])

    def test_lens_checklists_at_most_8_bullets(self):
        lens = None
        counts = {}
        for line in read("lenses.md").splitlines():
            if line.startswith("## "):
                lens = line[3:].strip()
                counts[lens] = 0
            elif line.startswith("- Uses when installed"):
                lens = None
            elif lens and line.startswith("- "):
                counts[lens] += 1
        for name in LENS_NAMES:
            self.assertTrue(0 < counts[name] <= 8, "%s has %d bullets" % (name, counts[name]))

    def test_plan_review_rules(self):
        self.assert_has("plan-review-prompt.md", ["PLAN APPROVED", "PLAN NEEDS CHANGES", "model", "verify",
                                                  "read-only"])

    def test_severity_scale(self):
        for name in ("batch-review-prompt.md", "plan-review-prompt.md", "lens-review-prompt.md"):
            self.assert_has(name, ["Critical", "Important", "Minor"])

    def test_lenses_cover_all(self):
        headings = [line[3:].strip() for line in read("lenses.md").splitlines() if line.startswith("## ")]
        for lens in LENS_NAMES:
            self.assertIn(lens, headings)
        self.assert_has("lenses.md", ["Lens yield: ", "Uses when installed"])

    def test_lens_review_rules(self):
        self.assert_has("lens-review-prompt.md", ["not rendered", ".tech-lead/scratch/", "read-only"])

    def test_inventory_read_only(self):
        self.assert_has("inventory-prompt.md", ["change nothing", "vulture", "knip"])

    def test_batch_review_hygiene(self):
        self.assert_has("batch-review-prompt.md", ["obsolete", "duplicat", "ui-ux"])

    def test_plan_review_risk_and_hygiene(self):
        self.assert_has("plan-review-prompt.md", ["replaces", "risk", "hygiene", "Lens yield"])

    def test_mockup_standards(self):
        self.assert_has("mockup-prompt.md", ["WCAG 2.2", "2.4.11", "2.5.7", "2.5.8", "3.2.6", "3.3.7",
                                             "3.3.8", "modern-web-guidance", "resumed"])

    def test_codemap_navigation(self):
        for name in ["lens-review-prompt.md", "inventory-prompt.md", "batch-review-prompt.md",
                     "plan-review-prompt.md"]:
            self.assert_has(name, [".claude/codemap/"])

    def test_never_invoke_superdesign(self):
        names = sorted(n for n in os.listdir(DIR) if n.endswith("-prompt.md"))
        self.assertEqual(names, sorted(PLACEHOLDERS))
        for name in names:
            self.assert_has(name, [NEVER_SUPERDESIGN])

    def test_mockup_superdesign_export_mode(self):
        self.assert_has("mockup-prompt.md", ["superdesign-export", "sd-component", "Tailwind", "Lucide",
                                             "list-components", "screen id", "mapping"])
        self.assert_has("mockup-prompt.md", ["fetch", "XMLHttpRequest", "WebSocket", "<iframe>", "x.y.z",
                                             "rebuild", "locally", "Content-Security-Policy", "connect-src 'none'",
                                             "https://cdn.tailwindcss.com/<x.y.z>", "https://cdn.jsdelivr.net/npm/tailwindcss@<x.y.z>/",
                                             "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@<x.y.z>", "https://cdn.jsdelivr.net/npm/lucide@<x.y.z>/",
                                             "Always remove every existing", "as the first element in `<head>`", "https://unpkg.com/lucide@<x.y.z>/",
                                             "<object>", "<embed>", "http-equiv=\"refresh\""])

    def test_absolute_paths(self):
        for name in PLACEHOLDERS:
            self.assert_has(name, ["absolute path"])


if __name__ == "__main__":
    unittest.main()
