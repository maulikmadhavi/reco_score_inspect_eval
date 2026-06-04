# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application for visualizing image recognition results. It displays:
- **Panel-1 (Distribution)**: Histogram of recognition scores across images with a slider to select a score range
- **Panel-2 (Image Gallery)**: Images sorted by recognition score value, corresponding to the selected score range
- **SidePanel (Category Selector)**: Dropdown to filter results by category

The application processes CSV input files containing variable score and image name columns per category (named as `score_<category>` and `image_<category>`). Score values range from 0 to 1.

## Development Setup

This project uses **Pixi** for dependency management. The Python 3.14+ environment is configured in `pixi.toml`.

```bash
# Install pixi (if not already installed)
# https://pixi.sh

# Activate the pixi environment
pixi shell

# Or run commands directly with pixi
pixi run python app.py

# Add a new dependency
pixi add <package-name>

# Add a new PyPI dependency
pixi add --pypi <package-name>

# Update dependencies
pixi update

# Run the application
pixi run python app.py

# Run tests (after adding pytest to pixi.toml)
pixi run pytest

# Run a single test
pixi run pytest tests/test_name.py::test_function -v
```

**Python Location**: `.pixi/envs/default/bin/python3.14`

## Project Structure

```
dev_ir_result_analysis/
├── app.py                 # Main Flask application
├── static/               # Static assets (CSS, JS, images)
│   └── ...
├── templates/            # Jinja2 templates
│   └── index.html
├── data/                 # Sample CSV input files
│   └── sample.csv
└── tests/                # Unit tests
    └── ...
```

## Dependencies

**Current (from pixi.toml)**:
- Python 3.14.5+
- Flask 3.1.3+

**Recommended additions**:
```bash
pixi add --pypi pandas numpy pillow matplotlib pytest
```

## Key Components

- **Data Processing**: CSV parsing with pandas, category filtering, score-to-image mapping
- **Backend**: Flask routes for category selection, slider value updates, image data retrieval
- **Frontend**: HTML/CSS/JavaScript for interactive panels, slider control, dropdown menu
- **Visualization**: Matplotlib for histogram generation, image gallery rendering

## Common Tasks

### Add a new category
1. Input CSV should contain `score_<category>` and `image_<category>` columns
2. Application auto-discovers categories from CSV headers
3. Update category dropdown in template if needed

### Adjust score binning
- Modify histogram binning logic in the data processing module (typically in `app.py` or a `data_utils.py` module)

### Change visualization styling
- Update CSS in `static/` for panel layouts and colors
- Modify matplotlib figure settings in image rendering code

## Testing Strategy

- Use pytest for unit tests
- Test data processing (CSV parsing, category filtering)
- Test Flask route endpoints
- Mock image data for visualization tests
- Include integration tests for full workflow (upload CSV → view results)

## Git Workflow

- Commit frequently with descriptive messages
- Use feature branches for new features
- Ensure tests pass before merging to main
