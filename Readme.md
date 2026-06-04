# IR Result Analysis

A Flask web app for visually analyzing image-recognition results. Browse the score
distribution for each category, scrub a slider to a score value, and inspect the
images that scored around there — filtered to those whose ground-truth label matches
the selected category.

## Visualization

- **SidePanel** — dropdown to select the active category. Updates both panels.
- **Panel-1 (Distribution)** — Plotly histogram of recognition scores for the selected
  category (x = score, y = image count). A horizontal slider selects a score value,
  marked by a dashed line on the histogram.
- **Panel-2 (Images near selected score)** — full-height portrait images sorted by
  descending score, centered on the slider value. Only images whose ground-truth label
  equals the selected category are shown. Each card displays the image, its filename,
  and its score.

## Input Data

A single CSV with these columns:

| Column            | Description                                                        |
| ----------------- | ------------------------------------------------------------------ |
| `image_path`      | Full path to the image file on disk.                               |
| `gt` / `gt_name`  | Ground-truth category label (used to filter Panel-2).              |
| `score_<category>`| One column per category, score in `[0, 1]`. Row scores sum to 1.   |

Categories are auto-discovered from the `score_` prefixed columns. The ground-truth
column may be named either `gt` or `gt_name`. Additional metadata columns (e.g.
`pred`, `correct`) are ignored.

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
# Generate fake placeholder data for local testing (1000 images, 3 categories)
pixi run gen-data

# Run the app against a CSV
pixi run start                       # uses data/sample.csv
python app.py --csv path/to/data.csv # any CSV

# then open http://127.0.0.1:5000
```

`app.py` flags: `--csv` (required), `--host` (default `127.0.0.1`),
`--port` (default `5000`), `--debug`.

## Development

```bash
pixi run test          # run the unit test suite
```

### Structure

```
app.py                    Flask app: CLI, routes, image-serving guard
data_utils.py             CSV loading, category discovery, gt-filtering, score windowing
scripts/gen_fake_data.py  Generates placeholder PNGs + sample.csv
templates/index.html      3-panel layout (Plotly via CDN)
static/css/style.css      Styling
static/js/app.js          Plotly histogram, slider, image strip
tests/test_data_utils.py  Unit tests for the data layer
```

### Security note

Image paths in the CSV may point anywhere on disk, so the `/image` route only serves
files whose resolved path is in the allow-list built from the loaded CSV — arbitrary
file reads are rejected with `403`.
