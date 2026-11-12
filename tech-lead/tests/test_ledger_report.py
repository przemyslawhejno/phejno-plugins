from __future__ import annotations

import unittest

from helpers import make_task, make_ledger
from ledger_report import render_show


class RenderShowTests(unittest.TestCase):
    def _ledger(self):
        return make_ledger([
            make_task(1),
            make_task(2, depends_on=[1], model="lead", files=[], covers=["R1"]),
        ])

    def test_sections_in_order(self):
        out = render_show(self._ledger())
        idx = [out.index(h) for h in ("## Wave 1", "## Wave 2", "## Requirement coverage",
                                      "## New dependencies and copied code", "## Summary")]
        self.assertEqual(idx, sorted(idx))

    def test_wave_tables(self):
        out = render_show(self._ledger())
        w1, rest = out.split("## Wave 2")
        self.assertIn("| Task | Title | Depends on | Files | Model | Risk | Experts | Reason | Acceptance |", w1)
        self.assertIn("sonnet/low", w1)
        self.assertIn("Task 1", w1)
        w2 = rest.split("## Requirement coverage")[0]
        self.assertIn("Task 2", w2)
        self.assertIn("| lead |", w2)

    def test_risk_and_experts_columns(self):
        out = render_show(make_ledger([
            make_task(1, risk=["security", "data"], experts=["security", "data"])]))
        self.assertIn("| sonnet/low | security<br>data | security<br>data | r |", out)

    def test_kind_suffix(self):
        out = render_show(make_ledger([
            make_task(1), make_task(2, kind="ui"), make_task(3, kind="hygiene")]))
        self.assertIn("| sonnet/low (ui) |", out)
        self.assertIn("| sonnet/low (hygiene) |", out)

    def test_lens_dispatch_counts_distinct_per_wave(self):
        out = render_show(make_ledger([
            make_task(1, experts=["security"]), make_task(2, experts=["security"]),
            make_task(3, depends_on=[1, 2])]))
        self.assertIn("Lens dispatches: wave 1: 1, wave 2: 0 (total 1)", out)

    def test_ledger_without_risk_or_experts_renders_dashes(self):
        out = render_show(self._ledger())
        self.assertIn("| sonnet/low | - | - | r |", out)
        self.assertIn("Lens dispatches: none", out)

    def test_coverage_lists_tasks(self):
        out = render_show(self._ledger())
        self.assertIn("| R1 | r | 1, 2 |", out)

    def test_reuse_list_excludes_pattern(self):
        r = lambda m: {"mode": m, "source": f"src-{m}", "license": "MIT"}
        out = render_show(make_ledger([
            make_task(1, reuse=r("pattern")), make_task(2, reuse=r("dependency")),
            make_task(3, reuse=r("copy"))]))
        self.assertNotIn("src-pattern", out)
        self.assertIn("- Task 2: src-dependency (dependency, MIT)", out)
        self.assertIn("- Task 3: src-copy (copy, MIT)", out)
        self.assertIn("None.", render_show(self._ledger()))
        self.assertNotIn("None.", out)

    def test_summary_counts_and_share(self):
        out = render_show(make_ledger([
            make_task(1), make_task(2), make_task(3, model="opus"),
            make_task(4, model="fable")]))
        self.assertIn("- sonnet: 2", out)
        self.assertIn("- opus: 1", out)
        self.assertNotIn("- haiku", out)
        self.assertIn("Opus and fable share: 50% (2 of 4 tasks)", out)
        self.assertIn("Prior art: done", out)


if __name__ == "__main__":
    unittest.main()
