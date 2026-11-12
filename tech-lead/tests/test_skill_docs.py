from __future__ import annotations

import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "tech-lead"
SKILL = SKILL_DIR / "SKILL.md"
LAYOUT = SKILL_DIR / "layout.md"

REQUIRED_IN_SKILL = [
    "model-manager:model-manager",
    "superpowers:brainstorming",
    "superpowers:writing-plans",
    "superpowers:subagent-driven-development",
    "superpowers:verification-before-completion",
    "superpowers:finishing-a-development-branch",
    "ledger.py check",
    "ledger.py show",
    "ledger.py next",
    "ledger.py checkpoint",
    "--mark",
    "status.py",
    "layout.md",
    "scout-prompt.md",
    "mockup-prompt.md",
    "batch-review-prompt.md",
    "plan-review-prompt.md",
    "autopilot",
    "--auto",
    "--progress",
    "--wave",
    "--base",
    "sdd-workspace",
    "../../scripts/",
    "superpowers:test-driven-development",
    "superpowers:requesting-code-review",
    "security-review",
    "engineering:architecture",
    "modern-web-guidance",
    "fable",
    ".worktrees/",
    "absolute",
    "backlog.md",
    "research/plan-review.md",
    "docs/superpowers/",
    "lenses.md",
    "lens-review-prompt.md",
    "inventory-prompt.md",
    '"schema": 2',
    "replaces",
    "`risk`: any of",
    "`experts`: lens names",
    "`kind: hygiene`",
    "`ui-ux` checklist",
    "Suite time",
    "WCAG 2.2",
    "superpowers:systematic-debugging",
    ".claude/codemap/",
    "/codemap update",
    "pending.md",
    "engineering:tech-debt",
    "simplify",
    "Lens yield",
    "{{CANDIDATES_PATH}}",
]

SECTIONS = [
    "Role",
    "Start of work",
    "Process",
    "Tiers",
    "Escalation",
    "Lanes",
    "Turn economy",
    "Paths",
    "Commands",
]

REQUIRED_IN_LAYOUT = [
    "docs/STATUS.md",
    "docs/backlog.md",
    "docs/standards.md",
    "docs/adr/",
    "docs/initiatives/",
    "journal.md",
    "ledger.json",
    "mockup.html",
    "research/",
    ".tech-lead/scratch/",
    "Closed:",
    "- [ ] B",
    ".gitignore",
    "docs/superpowers/",
    "git mv",
    "[hygiene]",
    "Suite time:",
    "Lens yield",
    "Timing:",
]


NEVER_SUPERDESIGN = "Never invoke the superdesign skill or the superdesign CLI."

REQUIRED_SUPERDESIGN_IN_SKILL = [
    "superdesign:superdesign",
    ".tech-lead/superdesign-consent",
    "credits",
    "main session",
    "get-design --draft-id",
    "import-design-draft --into",
    "built-in",
    "built-in builder",
    "mockup-prompt.md",
    "Mockup via superdesign",
    "Superdesign repository analysis",
]

REQUIRED_SUPERDESIGN_IN_LAYOUT = [
    ".superdesign/*",
    "!.superdesign/design-system.md",
    "Design system: .superdesign/design-system.md",
    ".tech-lead/superdesign-consent",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError("no frontmatter")
    keys = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return keys
        if line and not line.startswith((" ", "\t")) and ":" in line:
            key, value = line.split(":", 1)
            keys[key.strip()] = value.strip()
    raise AssertionError("unterminated frontmatter")


def headings(text: str) -> list:
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


class SkillDocsTest(unittest.TestCase):
    def test_frontmatter(self):
        fm = frontmatter(read(SKILL))
        self.assertEqual(set(fm), {"name", "description"})
        self.assertEqual(fm["name"], "tech-lead")
        self.assertTrue(fm["description"].startswith("Use when"))

    def test_mentions_required_items(self):
        text = read(SKILL)
        missing = [item for item in REQUIRED_IN_SKILL if item not in text]
        self.assertEqual(missing, [])

    def test_failure_causes_in_escalation(self):
        text = read(SKILL)
        start = text.index("\n## Escalation")
        end = text.index("\n## ", start + 1)
        section = text[start:end]
        for cause in ("`brief`", "`context`", "`plan`", "`capability`", "`unknown`"):
            self.assertIn(cause, section)

    def test_section_order(self):
        found = headings(read(SKILL))
        positions = []
        for name in SECTIONS:
            matches = [i for i, h in enumerate(found) if h.startswith(name)]
            self.assertTrue(matches, "missing section " + name)
            positions.append(matches[0])
        self.assertEqual(positions, sorted(positions))

    def test_length(self):
        self.assertLess(len(read(SKILL).splitlines()), 300)

    def test_layout_paths(self):
        text = read(LAYOUT)
        missing = [item for item in REQUIRED_IN_LAYOUT if item not in text]
        self.assertEqual(missing, [])

    def test_superdesign_in_skill(self):
        text = read(SKILL)
        missing = [item for item in REQUIRED_SUPERDESIGN_IN_SKILL if item not in text]
        self.assertEqual(missing, [])

    def test_superdesign_conditions_in_order(self):
        text = read(SKILL)
        pos = text.index("## Process")
        for item in ("superdesign:superdesign", ".tech-lead/superdesign-consent", "login", "built-in"):
            found = text.find(item, pos)
            self.assertNotEqual(found, -1, "%r missing after previous condition" % item)
            pos = found

    def test_superdesign_init_exception(self):
        text = read(SKILL)
        sentences = [s for s in text.replace("\n", " ").split(". ") if ".superdesign/init/" in s]
        self.assertTrue(sentences)
        self.assertTrue(any("only" in s and "never runs the CLI" in s for s in sentences), sentences)

    def test_superdesign_consent_text(self):
        text = read(SKILL) + read(LAYOUT)
        for item in ("public URLs", "unpinned", "credits", "tokens"):
            self.assertIn(item, text)

    def test_every_brief_carries_never_invoke(self):
        lines = read(SKILL).splitlines()
        for marker in ("Every brief says:", "Every subagent brief"):
            hits = [line for line in lines if marker in line]
            self.assertTrue(hits, marker)
            for line in hits:
                self.assertIn(NEVER_SUPERDESIGN, line)

    def test_layout_superdesign(self):
        text = read(LAYOUT)
        missing = [item for item in REQUIRED_SUPERDESIGN_IN_LAYOUT if item not in text]
        self.assertEqual(missing, [])

    def test_no_model_switch(self):
        for path in (SKILL, LAYOUT):
            self.assertNotIn("/model ", read(path), str(path))


if __name__ == "__main__":
    unittest.main()
