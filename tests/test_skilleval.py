import json
from pathlib import Path
import skilleval.cli as se


SOLVER = r"""
import os
import pathlib
prompt = os.environ["SKILLEVAL_PROMPT"]
skill = os.environ.get("SKILLEVAL_SKILL") or ""
out = pathlib.Path(os.environ["SKILLEVAL_OUT"])
text = "prompt:" + prompt + "\n"
if skill:
    skill_md = pathlib.Path(skill) / "SKILL.md"
    if skill_md.is_file():
        body = skill_md.read_text()
        if "release notes" in body.lower():
            text += "# Release notes\n\n- fix timeout\n"
        else:
            text += body
    else:
        text += "skill-missing\n"
else:
    text += "lorem ipsum draft\n"
out.write_text(text)
"""


def write_setup(tmp_path: Path):
    skill = tmp_path / "release-notes"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: release-notes\n"
        "description: Writes release notes. Use when asked for a changelog.\n"
        "---\n\nWrite release notes as a markdown heading plus bullets.\n",
        encoding="utf-8",
    )
    solver = tmp_path / "solver.py"
    solver.write_text(SOLVER)
    ev = tmp_path / "eval.json"
    ev.write_text(json.dumps({
        "solver": "python3 " + str(solver),
        "cases": [{
            "id": "changelog",
            "prompt": "Write release notes for: fix timeout",
            "skill": str(skill),
            "baseline_skill": None,
            "checks": [
                {"type": "contains", "text": "Release notes"},
                {"type": "contains", "text": "timeout"},
                {"type": "not_contains", "text": "lorem ipsum"},
                {"type": "regex", "pattern": r"^# "},
                {"type": "exit_code", "value": 0},
            ],
        }],
    }))
    return ev


def test_skill_beats_baseline(tmp_path, capsys):
    ev = write_setup(tmp_path)
    assert se.main([str(ev), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["variants"]["baseline"]["passed"] < data["variants"]["with_skill"]["passed"]
    assert data["variants"]["with_skill"]["passed"] == data["variants"]["with_skill"]["total"]


def test_failing_skill_exits_2(tmp_path, capsys):
    ev = write_setup(tmp_path)
    payload = json.loads(ev.read_text())
    payload["cases"][0]["checks"].append({"type": "contains", "text": "this-string-is-never-emitted"})
    ev.write_text(json.dumps(payload))
    assert se.main([str(ev)]) == 2
    out = capsys.readouterr().out
    assert "FAIL" in out


def test_missing_solver(tmp_path, capsys):
    ev = tmp_path / "eval.json"
    ev.write_text(json.dumps({"cases": [{"id": "x", "prompt": "hi", "checks": []}]}))
    assert se.main([str(ev)]) == 1
    assert "solver" in capsys.readouterr().out


def test_relative_solver_path(tmp_path, capsys):
    ev = write_setup(tmp_path)
    payload = json.loads(ev.read_text())
    payload["solver"] = "python3 solver.py"
    ev.write_text(json.dumps(payload))
    assert se.main([str(ev), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["variants"]["with_skill"]["passed"] == data["variants"]["with_skill"]["total"]


def test_relative_skill_and_solver_from_eval_dir(tmp_path, capsys):
    ev = write_setup(tmp_path)
    payload = json.loads(ev.read_text())
    payload["solver"] = "python3 solver.py"
    payload["cases"][0]["skill"] = "./release-notes"
    ev.write_text(json.dumps(payload))
    assert se.main([str(ev), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["variants"]["with_skill"]["passed"] == data["variants"]["with_skill"]["total"]
    assert "lorem ipsum" in data["cases"][0]["variants"]["baseline"]["output"]
    assert "Release notes" in data["cases"][0]["variants"]["with_skill"]["output"]
