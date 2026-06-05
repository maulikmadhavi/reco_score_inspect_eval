# IR Result Analysis

A Flask web app for visually **debugging recognition-model results**. It has two views,
switchable from the sidebar:

1. **Score distribution** (`/`) — browse the score distribution for each category and
   inspect the images around any score value.
2. **Confusion matrix** (`/confusion`) — see ground-truth vs predicted counts and click
   any cell to inspect the images in it (correct hits or errors), sorted by confidence.

## Views

### Score distribution (`/`)

- **SidePanel** — dropdown to select the active category. Updates both panels.
- **Panel-1 (Distribution)** — Plotly histogram of recognition scores for the selected
  category (x = score, y = image count). A horizontal slider selects a score value,
  marked by a dashed line on the histogram.
- **Panel-2 (Images near selected score)** — full-height portrait images sorted by
  descending score, centered on the slider value. Only images whose ground-truth label
  equals the selected category are shown. Each card shows the image, filename, and score.

### Confusion matrix (`/confusion`)

- **Matrix** — a Plotly heatmap of ground-truth (rows) vs predicted (columns), with the
  count drawn in each cell. A trailing **`BG`** row holds background images that have no
  ground-truth label (empty `gt`) — future-proofing for unlabeled data.
- **Click a cell** — loads the images in that cell into the panel below, sorted by the
  predicted class's score (confidence) in descending order. This makes it easy to inspect
  high-confidence mistakes (off-diagonal cells) and feed findings back into training.

## Input Data

A single CSV with these columns:

| Column             | Description                                                         |
| ------------------ | ------------------------------------------------------------------- |
| `image_path`       | Full path to the image file on disk.                                |
| `gt` / `gt_name`   | Ground-truth category label. Empty/missing → treated as `BG`.       |
| `score_<category>` | One column per category, score in `[0, 1]`. Row scores sum to 1.    |
| `pred` *(optional)*| Predicted category. If absent, prediction = argmax of `score_*`.    |

Categories are auto-discovered from the `score_`-prefixed columns. The ground-truth
column may be named either `gt` or `gt_name`. For the confusion matrix, the predicted
label comes from the `pred` column if present, otherwise from the highest score.

Example:

```csv
image_path,gt,score_kid_female,score_kid_male,score_adult_female,score_adult_male
/data/imgs/01065.png,adult_female,0.0001,0.0000,0.9998,0.0001
```

## Setup

This project uses [Pixi](https://pixi.sh) for dependency management. The environment
targets `linux-64` (run under WSL on Windows).

```bash
pixi install
```

## Usage

```bash
# Generate fake placeholder data for local testing
# (1000 labeled images across 3 categories + 40 background images, with
#  ~15% mispredictions so the confusion matrix has errors to inspect)
pixi run gen-data

# Run the app against a CSV
pixi run start                       # uses data/sample.csv
python app.py --csv path/to/data.csv # any CSV

# then open http://127.0.0.1:5000  (and /confusion for the matrix view)
```

`app.py` flags: `--csv` (required), `--host` (default `127.0.0.1`),
`--port` (default `5000`), `--debug`.

## Development

```bash
pixi run test                       # run the unit test suite

# smoke-test the /confusion endpoints against sample data
bash scripts/verify_confusion.sh
```

### Structure

```
app.py                      Flask app: CLI, routes (/, /confusion, /image, /api/*)
data_utils.py               CSV loading, category/prediction discovery, matrix + cell helpers
scripts/gen_fake_data.py    Generates placeholder PNGs + sample.csv (with noise & BG rows)
scripts/check_stats.py      Prints data stats + the confusion matrix for the sample data
scripts/verify_confusion.sh Smoke-tests the /confusion HTTP endpoints
templates/index.html        Score-distribution view
templates/confusion.html    Confusion-matrix view
static/css/style.css        Styling (shared across views)
static/js/app.js            Histogram, slider, image strip
static/js/confusion.js      Heatmap + click-to-inspect cell images
tests/test_data_utils.py    Unit tests for the data layer
```

### Security note

Image paths in the CSV may point anywhere on disk, so the `/image` route only serves
files whose resolved path is in the allow-list built from every `image_path` in the
loaded CSV — arbitrary file reads are rejected with `403`.
