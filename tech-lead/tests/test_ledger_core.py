from __future__ import annotations

import json
import os
import tempfile
import unittest

from helpers import make_hygiene, make_ledger, make_task  # noqa: F401  (sets sys.path)

import ledger_core
from ledger_core import LedgerError, next_wave, paths_overlap, validate, waves


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def errors_of(*tasks, **overrides):
    return validate(make_ledger(list(tasks), **overrides))


def errors2(*tasks, **overrides):
    return errors_of(*tasks, schema=2, **overrides)


class ValidateTests(unittest.TestCase):
    def assertHas(self, errors, text):
        self.assertTrue(any(text in e for e in errors), f"{text!r} not in {errors}")

    def test_valid_ledger_has_no_errors(self):
        self.assertEqual(validate(make_ledger([make_task(1), make_task(2, depends_on=[1])])), [])

    def test_missing_field(self):
        t = make_task(1)
        del t["reason"]
        self.assertHas(errors_of(t), "task 1: missing field 'reason'")

    def test_empty_acceptance(self):
        self.assertHas(errors_of(make_task(1, acceptance=[])), "task 1: acceptance is empty")

    def test_string_id_rejected(self):
        self.assertHas(errors_of(make_task("1")), "id must be a positive integer")
        self.assertHas(errors_of(make_task(True)), "id must be a positive integer")
        self.assertHas(errors_of(make_task(0)), "id must be a positive integer")

    def test_duplicate_ids(self):
        self.assertHas(errors_of(make_task(1), make_task(1)), "duplicate task id 1")
        self.assertHas(
            validate(make_ledger([make_task(1)], requirements=[
                {"id": "R1", "text": "a"}, {"id": "R1", "text": "b"}])),
            "duplicate requirement id R1",
        )

    def test_unknown_done_id(self):
        self.assertHas(errors_of(make_task(1), done=[9]), "done: unknown task id 9")
        self.assertHas(errors_of(make_task(1), done=["1"]), "done: unknown task id 1")

    def test_invalid_model_effort_reuse_mode(self):
        self.assertHas(errors_of(make_task(1, model="gpt")), "task 1: invalid model 'gpt'")
        self.assertHas(errors_of(make_task(1, effort="huge")), "task 1: invalid effort 'huge'")
        reuse = {"mode": "steal", "source": "s", "license": "MIT"}
        self.assertHas(errors_of(make_task(1, reuse=reuse)), "task 1: invalid reuse.mode 'steal'")

    def test_reuse_needs_source_and_license(self):
        self.assertHas(errors_of(make_task(1, reuse={"mode": "copy"})),
                       "task 1: reuse needs source and license")
        self.assertHas(errors_of(make_task(1, reuse={"mode": "copy", "source": "s"})),
                       "task 1: reuse needs source and license")
        self.assertEqual(errors_of(make_task(1, reuse={"mode": "copy", "source": "s", "license": "MIT"})), [])

    def test_unknown_dependency_and_covers(self):
        errs = errors_of(make_task(1, depends_on=[7], covers=["R1", "R9"]))
        self.assertHas(errs, "task 1: depends on unknown task 7")
        self.assertHas(errs, "task 1: covers unknown requirement R9")

    def test_cycle_reported(self):
        errs = errors_of(make_task(1, depends_on=[2]), make_task(2, depends_on=[1]))
        self.assertHas(errs, "dependency cycle: 1 -> 2 -> 1")

    def test_cycle_starts_at_smallest_id(self):
        errs = errors_of(make_task(1, depends_on=[3]), make_task(2, depends_on=[1]),
                         make_task(3, depends_on=[2]))
        self.assertHas(errs, "dependency cycle: 1 -> 3 -> 2 -> 1")
        errs = errors_of(make_task(1), make_task(2, depends_on=[3]),
                         make_task(3, depends_on=[4]), make_task(4, depends_on=[2]))
        self.assertHas(errs, "dependency cycle: 2 -> 3 -> 4 -> 2")

    def test_bad_requirements_do_not_raise(self):
        for reqs in ([{"id": []}], ["x"], [{"id": ""}], [{"text": "t"}], [{"id": {}}]):
            errs = validate(make_ledger([make_task(1, covers=[[]])], requirements=reqs))
            self.assertTrue(errs, reqs)
        self.assertHas(validate(make_ledger([make_task(1)], requirements=[{"id": []}])),
                       "id must be a non-empty string")

    def test_uncovered_requirement(self):
        errs = validate(make_ledger([make_task(1)], requirements=[
            {"id": "R1", "text": "r"}, {"id": "R2", "text": "r"}]))
        self.assertHas(errs, "requirement R2 is covered by no task")

    def test_lead_task_files_rules(self):
        self.assertHas(errors_of(make_task(1, model="lead", files=["a.py"])), "task 1: lead tasks edit no files")
        self.assertHas(errors_of(make_task(1, files=[])), "task 1: files is empty")
        self.assertEqual(errors_of(make_task(1, model="lead", files=[])), [])

    def test_lead_task_needs_no_effort_or_verify(self):
        t = make_task(1, model="lead", files=[])
        del t["effort"], t["verify"]
        self.assertEqual(errors_of(t), [])
        t = make_task(1)
        del t["effort"]
        self.assertHas(errors_of(t), "task 1: missing field 'effort'")

    def test_empty_verify_needs_reason(self):
        msg = "task 1: verify is empty and no_verify gives no reason"
        self.assertHas(errors_of(make_task(1, verify=[])), msg)
        self.assertEqual(errors_of(make_task(1, verify=[], no_verify="docs only")), [])

    def test_paths_not_normalised(self):
        for p in ["/a", "./a", "a/../b", "a//b", "a\\b", ""]:
            self.assertHas(errors_of(make_task(1, files=[p])), f"task 1: path '{p}' is not normalised")

    def test_same_wave_conflict_with_directory_prefix(self):
        errs = errors_of(make_task(1, files=["src/"]), make_task(2, files=["src/a.py"]))
        self.assertHas(errs, "wave 1: tasks 1 and 2 share")

    def test_conflict_cleared_by_dependency(self):
        errs = errors_of(make_task(1, files=["src/"]), make_task(2, files=["src/a.py"], depends_on=[1]))
        self.assertEqual(errs, [])

    def test_prior_art_missing(self):
        ledger = make_ledger([make_task(1)])
        del ledger["prior_art"]
        self.assertHas(validate(ledger), "missing field 'prior_art'")

    def test_invalid_mode(self):
        self.assertHas(errors_of(make_task(1), mode="wild"), "invalid mode 'wild'")
        self.assertEqual(errors_of(make_task(1), mode="autopilot"), [])
        self.assertEqual(errors_of(make_task(1), mode="gated"), [])

    def test_wrong_types_do_not_raise(self):
        self.assertTrue(validate(dict(make_ledger([make_task(1)]), tasks="x")))
        self.assertTrue(errors_of(make_task(1, files=5)))
        self.assertTrue(errors_of(make_task(1, depends_on=None)))
        self.assertTrue(validate({"tasks": [1, "a", None]}))


class Schema2Tests(unittest.TestCase):
    def assertHas(self, errors, text):
        self.assertTrue(any(text in e for e in errors), f"{text!r} not in {errors}")

    def test_valid_schema2_ledger(self):
        tasks = [
            make_task(1, risk=["security"], experts=["security"]),
            make_task(2, risk=["data"], experts=["data"]),
            make_task(3, model="opus", risk=["irreversible"], experts=["api"]),
            make_hygiene(4, [1, 2, 3]),
        ]
        self.assertEqual(errors2(*tasks), [])

    def test_no_schema_field_skips_schema2_rules(self):
        tasks = [make_task(i, experts=["bogus"], kind="nope") for i in (1, 2, 3, 4)]
        self.assertEqual(errors_of(*tasks), [])

    def test_schema_must_be_int_two(self):
        for bad in (3, "2", 2.0, True):
            self.assertHas(errors_of(make_task(1), schema=bad), f"invalid schema '{bad}'")
        self.assertEqual(errors_of(make_task(1), schema=2), [])

    def test_schema2_ui_must_be_boolean(self):
        self.assertHas(errors2(make_task(1), ui="yes"), "ui must be a boolean")

    def test_schema2_hygiene_depends_on_every_other_task(self):
        self.assertHas(errors2(make_task(1, kind="docs")), "task 1: invalid kind 'docs'")
        self.assertEqual(errors2(make_task(1, model="lead", files=[], kind="docs")), [])

    def test_schema2_list_fields_must_be_string_lists(self):
        for f in ("risk", "experts", "replaces"):
            for bad in ("security", [1], None):
                self.assertHas(errors2(make_task(1, **{f: bad})), f"task 1: {f} must be a list of strings")

    def test_schema2_invalid_risk(self):
        self.assertHas(errors2(make_task(1, risk=["scary"])), "task 1: invalid risk 'scary'")

    def test_schema2_unknown_lens(self):
        self.assertHas(errors2(make_task(1, risk=["data"], experts=["data", "magic"])),
                       "task 1: unknown lens 'magic'")

    def test_case_sensitive_lens_and_risk(self):
        self.assertHas(errors2(make_task(1, risk=["Security"])), "task 1: invalid risk 'Security'")
        self.assertHas(errors2(make_task(1, risk=["security"], experts=["Security"])),
                       "task 1: unknown lens 'Security'")

    def test_schema2_more_than_four_experts(self):
        t = make_task(1, risk=["irreversible"],
                      experts=["data", "api", "architecture", "security", "tests"])
        self.assertHas(errors2(t), "task 1: more than 4 experts")

    def test_schema2_lead_takes_no_experts(self):
        t = make_task(1, model="lead", files=[], experts=["security"])
        self.assertHas(errors2(t), "task 1: lead tasks take no experts")

    def test_schema2_risk_needs_matching_lens(self):
        self.assertHas(errors2(make_task(1, risk=["security"], experts=["tests"])),
                       "task 1: risk 'security' needs one of the lenses security")
        self.assertHas(errors2(make_task(1, risk=["irreversible"], experts=["tests"])),
                       "task 1: risk 'irreversible' needs one of the lenses data, api, architecture")
        self.assertHas(errors2(make_task(1, risk=["data"])),
                       "task 1: risk 'data' needs one of the lenses data")

    def test_system_wide_matches_ui_ux_on_ui_task(self):
        ui = make_task(1, kind="ui", risk=["ux", "system-wide"], experts=["ui-ux"])
        self.assertEqual(errors2(ui, ui=True), [])
        code = make_task(1, risk=["system-wide"], experts=["ui-ux"])
        self.assertHas(errors2(code), "task 1: risk 'system-wide' needs one of the lenses architecture")

    def test_schema2_routine_task_takes_no_experts(self):
        self.assertHas(errors2(make_task(1, model="haiku", experts=["tests"])),
                       "task 1: routine task takes no experts")
        self.assertHas(errors2(make_task(1, experts=["tests"])),
                       "task 1: routine task takes no experts")
        self.assertEqual(errors2(make_task(1, effort="medium", experts=["tests"])), [])

    def test_schema2_ui_kind_needs_top_level_ui(self):
        t = make_task(1, kind="ui", risk=["ux"], experts=["ui-ux"])
        self.assertHas(errors2(t), "task 1: kind 'ui' needs top-level ui: true")
        self.assertHas(errors2(t, ui=False), "task 1: kind 'ui' needs top-level ui: true")
        self.assertEqual(errors2(t, ui=True), [])

    def test_schema2_ui_task_not_on_haiku_needs_ux(self):
        self.assertHas(errors2(make_task(1, kind="ui"), ui=True),
                       "task 1: ui task not on haiku needs risk 'ux'")
        self.assertEqual(errors2(make_task(1, kind="ui", model="haiku"), ui=True), [])

    def test_schema2_haiku_cannot_carry_risk(self):
        errs = errors2(make_task(1, model="haiku", risk=["data"]))
        self.assertHas(errs, "task 1: haiku task cannot carry risk 'data'")
        self.assertFalse(any("needs one of the lenses" in e for e in errs), errs)

    def test_schema2_missing_hygiene_task(self):
        three = [make_task(i) for i in (1, 2, 3)]
        self.assertHas(errors2(*three), "missing hygiene task")
        self.assertEqual(errors2(make_task(1), make_task(2)), [])
        self.assertHas(errors2(make_task(1), make_task(2, replaces=["old.py"])), "missing hygiene task")
        self.assertEqual(errors2(make_task(1, model="lead", files=[]), make_task(2), make_task(3)), [])

    def test_ui_tasks_count_toward_hygiene_threshold(self):
        ui = [make_task(i, kind="ui", model="haiku") for i in (1, 2, 3)]
        self.assertHas(errors2(*ui, ui=True), "missing hygiene task")

    def test_schema2_hygiene_must_depend_on_code_tasks(self):
        tasks = [make_task(1), make_task(2), make_task(3), make_hygiene(4, [1])]
        errs = errors2(*tasks)
        self.assertHas(errs, "task 4: hygiene task must depend on task 2")
        self.assertHas(errs, "task 4: hygiene task must depend on task 3")
        self.assertFalse(any("depend on task 1" in e for e in errs), errs)

    def test_0_1_0_initiative_ledger_without_schema_validates(self):
        path = os.path.join(REPO_ROOT, "docs", "initiatives", "2026-11-11-tech-lead", "ledger.json")
        self.assertEqual(validate(ledger_core.load(path)), [])


class WavesTests(unittest.TestCase):
    def test_waves(self):
        tasks = [make_task(1), make_task(2), make_task(3, depends_on=[1, 2]), make_task(4, depends_on=[3])]
        self.assertEqual(waves(tasks), {1: 1, 2: 1, 3: 2, 4: 3})

    def test_paths_overlap(self):
        self.assertTrue(paths_overlap("src/", "src/a.py"))
        self.assertTrue(paths_overlap("src/a.py", "src/a.py"))
        self.assertFalse(paths_overlap("src", "src2"))
        self.assertFalse(paths_overlap("src/a", "src/ab"))

    def test_next_wave(self):
        tasks = [make_task(1), make_task(2), make_task(3, depends_on=[1, 2])]
        w, ts = next_wave(make_ledger(tasks))
        self.assertEqual((w, [t["id"] for t in ts]), (1, [1, 2]))
        w, ts = next_wave(make_ledger(tasks, done=[1]))
        self.assertEqual((w, [t["id"] for t in ts]), (1, [2]))
        w, ts = next_wave(make_ledger(tasks, done=[1, 2]))
        self.assertEqual((w, [t["id"] for t in ts]), (2, [3]))
        self.assertIsNone(next_wave(make_ledger(tasks, done=[1, 2, 3])))


class LoadTests(unittest.TestCase):
    def test_load_errors(self):
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "none.json")
            bad = os.path.join(d, "bad.json")
            lst = os.path.join(d, "list.json")
            with open(bad, "w", encoding="utf-8") as f:
                f.write("{nope")
            with open(lst, "w", encoding="utf-8") as f:
                f.write("[]")
            for p in (missing, bad, lst):
                with self.assertRaises(LedgerError) as cm:
                    ledger_core.load(p)
                self.assertTrue(str(cm.exception).startswith(p + ": "), str(cm.exception))

    def test_load_ok(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "l.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"tasks": []}, f)
            self.assertEqual(ledger_core.load(p), {"tasks": []})


if __name__ == "__main__":
    unittest.main()
