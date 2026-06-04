import argparse
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file, abort

import data_utils

app = Flask(__name__)

# loaded at startup
_df = None
_categories: list[str] = []
_known_image_paths: set[str] = set()


def _load_data(csv_path: str) -> None:
    global _df, _categories, _known_image_paths
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    _df = data_utils.load_dataframe(csv_path)
    _categories = data_utils.discover_categories(_df)

    if not _categories:
        print("Error: no valid score_/image_ column pairs found in CSV.", file=sys.stderr)
        sys.exit(1)

    # build allow-list of image paths so /image can't serve arbitrary files
    for cat in _categories:
        records = data_utils.get_category_records(_df, cat)
        for r in records:
            _known_image_paths.add(str(Path(r["image"]).resolve()))

    print(f"Loaded {len(_df)} rows, categories: {_categories}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/categories")
def api_categories():
    return jsonify({"categories": _categories})


@app.route("/api/distribution")
def api_distribution():
    category = request.args.get("category", "")
    if category not in _categories:
        return jsonify({"error": "unknown category"}), 400
    dist = data_utils.get_distribution(_df, category)
    return jsonify(dist)


@app.route("/api/images")
def api_images():
    category = request.args.get("category", "")
    if category not in _categories:
        return jsonify({"error": "unknown category"}), 400
    try:
        score = float(request.args.get("score", 0.5))
        window = int(request.args.get("window", 10))
    except ValueError:
        return jsonify({"error": "invalid parameters"}), 400

    records = data_utils.get_category_records(_df, category)
    images = data_utils.get_images_around(records, score, window)
    # replace full path with a URL-safe reference
    result = [{"name": Path(r["image"]).name, "score": r["score"], "path": r["image"]} for r in images]
    return jsonify({"images": result})


@app.route("/image")
def serve_image():
    raw_path = request.args.get("path", "")
    resolved = str(Path(raw_path).resolve())
    if resolved not in _known_image_paths:
        abort(403)
    p = Path(resolved)
    if not p.is_file():
        abort(404)
    return send_file(resolved)


def main():
    parser = argparse.ArgumentParser(description="IR Result Analysis")
    parser.add_argument("--csv", required=True, help="Path to input CSV")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    _load_data(args.csv)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
