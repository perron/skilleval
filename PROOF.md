# skilleval proof

Captured 2026-11-09 13:27 PST.

Fresh-venv install: `pip install .` succeeded and `skilleval --version` printed `skilleval 0.1.1`.

Tests: 14 passed in 1.32s

```
variant	checks passed	cases
baseline	2/5	1
with_skill	5/5	1

[changelog]
  baseline: 2/5
    FAIL  contains "Release notes"
    ok  contains "timeout"
    FAIL  not_contains "lorem ipsum"
    FAIL  regex ^# 
    ok  exit_code 0
  with_skill: 5/5
    ok  contains "Release notes"
    ok  contains "timeout"
    ok  not_contains "lorem ipsum"
    ok  regex ^# 
    ok  exit_code 0
exit: 0
```
