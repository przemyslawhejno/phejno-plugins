from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import ledger_core  # noqa: E402

PLUGIN = Path(__file__).resolve().parent.parent
ROOT = PLUGIN.parent
DESC = (
    "Lead orchestrator: plans a spec into waves of tasks, assigns the cheapest "
    "capable model to each, delegates, reviews and verifies; adds hygiene passes, "
    "expert panels and UI/UX review; keeps project docs, status and backlog in "
    "one hierarchy; optional superdesign mockup provider"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "no frontmatter"
    return m.group(1)


class PackagingTests(unittest.TestCase):
    def test_plugin_json(self):
        d = load(PLUGIN / ".claude-plugin" / "plugin.json")
        self.assertEqual(d["name"], "tech-lead")
        self.assertEqual(d["description"], DESC)
        self.assertEqual(d["version"], "0.3.1")
        self.assertEqual(d["author"]["name"], "Przemyslaw Hejno")

    def test_marketplace_entry_matches_plugin(self):
        p = load(PLUGIN / ".claude-plugin" / "plugin.json")
        m = load(ROOT / ".claude-plugin" / "marketplace.json")
        entry = [e for e in m["plugins"] if e["name"] == "tech-lead"]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["source"], "./tech-lead")
        self.assertEqual(entry[0]["version"], p["version"])
        self.assertEqual(entry[0]["description"], p["description"])

    def test_hook_points_to_existing_script(self):
        d = load(PLUGIN / "hooks" / "hooks.json")
        group = d["hooks"]["SessionStart"][0]
        self.assertEqual(group["matcher"], "startup|clear|compact")
        cmd = group["hooks"][0]["command"]
        self.assertIn("scripts/status.py", cmd)
        self.assertIn("--brief", cmd)
        self.assertTrue((PLUGIN / "scripts" / "status.py").is_file())

    def test_command_frontmatter(self):
        path = PLUGIN / "commands" / "run.md"
        fm = frontmatter(path)
        self.assertRegex(fm, r"(?m)^description:")
        self.assertRegex(fm, r"(?m)^argument-hint:")
        self.assertNotRegex(fm, r"(?m)^(model|effort):")
        body = path.read_text(encoding="utf-8")
        for s in ("tech-lead:tech-lead", "$ARGUMENTS", "--auto"):
            self.assertIn(s, body)

    def test_skill_references_exist(self):
        d = PLUGIN / "skills" / "tech-lead"
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        names = set(re.findall(r"[\w-]+-prompt\.md", text)) | {"layout.md", "lenses.md"}
        for n in names:
            self.assertTrue((d / n).is_file(), n)
        for n in set(re.findall(r"\.\./\.\./scripts/([\w-]+\.py)", text)):
            self.assertTrue((PLUGIN / "scripts" / n).is_file(), n)

    def test_lenses_match_ledger_core(self):
        d = PLUGIN / "skills" / "tech-lead"
        text = (d / "lenses.md").read_text(encoding="utf-8")
        heads = re.findall(r"(?m)^## (.+)$", text)
        lenses = [h for h in heads if h not in ("Dispatch", "Yield")]
        self.assertEqual(lenses, list(ledger_core.LENSES))

    def test_readmes(self):
        r = (PLUGIN / "README.md").read_text(encoding="utf-8")
        for s in ("/tech-lead:run", "model-manager", "superpowers", "TECH_LEAD_STATUS", "The lenses are `security`", "`kind: hygiene`", "WCAG 2.2", '"schema": 2', "`## Codemap` section"):
            self.assertIn(s, r)
        for s in ("superdesign", "/plugin marketplace add superdesigndev/superdesign-skill", "npx --yes @superdesign/cli@latest login", "credits"):
            self.assertIn(s, r)
        for s in ("not asked again", "deleting the file", "verbatim", ".superdesign/*", "the built-in builder always runs"):
            self.assertIn(s, r)
        for s in ("fonts and logos", "component templates", "not answering"):
            self.assertIn(s, r)
        self.assertNotIn("recorded before the start", r)
        root = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("### tech-lead", root)


if __name__ == "__main__":
    unittest.main()
