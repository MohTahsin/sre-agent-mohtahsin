# Grok SRE Agent

Autonomous Site Reliability Engineering agent built on FastAPI + Strands Agents
(xAI Grok) that investigates production alerts and recommends/executes safe
remediations.

## Build & Test
- Install runtime deps: `pip install -r backend/requirements.txt`
- Install dev deps: `pip install -r requirements-dev.txt`
- Run the test suite: `pytest -q`
- Tests live in `tests/`; `pythonpath` is the repo root (see `pytest.ini`).

## Project Layout
- `backend/` — agent entrypoints: `agent.py`, `main.py` (FastAPI app), `tools.py`
- `backend/remediation/` — remediation logic; `lambda_scaling.py` holds the
  Lambda throttling playbook
- `tests/` — pytest suite (e.g. `test_lambda_scaling.py`)
- `docs/`, `README.md` — operator-facing documentation
- `frontend/` — demo UI

## Remediation Contract
`calculate_reserved_concurrency(current_throttles, avg_rps)` in
`backend/remediation/lambda_scaling.py` must:
- Return an `int` (AWS reserved-concurrency API requires an integer).
- Never recommend below the documented minimum floor (`MIN_RESERVED_CONCURRENCY`).
- Apply the documented safety buffer (`SAFETY_BUFFER_MULTIPLIER`) over the
  observed average RPS.
- Never recommend a value below current observed load (that would guarantee
  continued throttling).
- Reject negative `avg_rps` or `current_throttles` with `ValueError`.

The authoritative floor and buffer values are the module-level constants in
`lambda_scaling.py` and the assertions in `tests/test_lambda_scaling.py`. When
they disagree with this file, the code and tests win.

## Conventions & Patterns
- Python 3.11, standard library `math` for rounding (`math.ceil`).
- Keep remediation functions pure and deterministic so they stay unit-testable.
- When fixing a logic bug, add or update a test in `tests/` that proves the fix.
- Do not change unrelated files; keep diffs scoped to the task.

## Git Workflow
- In CI/`droid exec` runs, do NOT commit or push — the workflow handles all git
  operations.
- Automated commits use the `factory-droid[bot]` identity and a
  `Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>`
  trailer.
