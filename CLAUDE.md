# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`reco_score_inspect_eval` is a Flask web app for **debugging recognition-model results**
(image classification only). Two views, switchable from the sidebar:

- **Score distribution** (`/`) — Plotly histogram of per-category scores with a slider;
  Panel-2 shows images near the selected score, filtered to those whose ground truth
  matches the category.
- **Confusion matrix** (`/confusion`) — Plotly heatmap of ground-truth × predicted with a
  trailing **`BG`** row for unlabeled images. Clicking a cell loads its images sorted by
  prediction confidence (descending) — the core error-inspection workflow.

Charts are **client-side Plotly** (CDN), not server-rendered. See `Readme.md` for the
architecture diagram and full feature docs.

## Running commands (IMPORTANT: pixi is linux-64 only)

The pixi environment targets `linux-64`, so on this Windows host **everything runs through
WSL**. `pixi` on the Windows PATH will fail with `unsupported-platform`. Use one of:

```bash
# via WSL (pixi binary is not on PATH for non-login shells — use the full path)
wsl -u maulik -e bash -c "/home/maulik/.pixi/bin/pixi run <task>" -- --workdir /mnt/d/dev_repos/dev_ir_result_analysis

# or call the env interpreter directly (faster startup, no pixi overhead)
.pixi/envs/default/bin/python3.14 <script>.py
```

Pixi tasks (`pixi.toml`):

| Task | Command |
|---|---|
| `gen-data` | regenerate `data/sample.csv` + placeholder PNGs (deterministic, seed 42) |
| `start` | `python app.py --csv data/sample.csv` |
| `test` | `pytest tests/ -v` |

Run the app directly with flags: `python app.py --csv <path> [--host --port --debug]`.
Run a single test: `pixi run pytest tests/test_data_utils.py::test_name -v`.

## Architecture

- **`app.py`** — HTTP layer only: CLI, Flask routes, and the `/image` allow-list guard.
  Loads the CSV once at startup into module globals (`_df`, `_categories`,
  `_known_image_paths`). Routes delegate all logic to `data_utils`.
- **`data_utils.py`** — pure functions, **no Flask imports**, fully unit-tested. Core
  helpers shared by the confusion view: `normalize_gt` (empty/NaN gt → `BG`),
  `get_predictions` (`pred` column or argmax of `score_*`), `_gt_column`.
- **`tests/test_data_utils.py`** — 16 tests on the data layer. `conftest.py` adds the
  project root to `sys.path` so `import data_utils` works.
- Frontend: `templates/{index,confusion}.html`, `static/js/{app,confusion}.js`,
  `static/css/style.css` (shared).

## Data schema

Single CSV. Columns: `image_path` (full path on disk), `gt` or `gt_name` (ground truth;
empty → `BG`), `score_<category>` (one per category, row sums to 1), and optional `pred`.
Categories are auto-discovered from `score_`-prefixed columns. `pred`/`correct`/other
columns are otherwise ignored. The `/image` route only serves paths present in the loaded
CSV (arbitrary file reads → 403).

## Conventions

- **Readability over compaction.** Prefer clear, explicit code over dense one-liners —
  e.g. keep step-by-step `sub = ...` pandas reassignments rather than long method chains;
  avoid `**{...}` dict-unpacking and inline slice expressions that hide named variables.
- `data/images/*.png` are tracked via **Git LFS**; `data/sample.csv` is a normal file.
  Both are regenerable via `pixi run gen-data`, so don't hand-edit them.
- Commit style: Conventional Commits (`feat(confusion):`, `fix:`, `docs:`, `test:`).

## Dependencies (pixi.toml)

Python 3.14+, Flask, pandas, numpy, pillow (generator only), pytest. Plotly loads from CDN
in the browser — no server-side plotting dependency.
