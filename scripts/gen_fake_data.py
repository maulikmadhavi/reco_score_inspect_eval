"""Generate placeholder PNGs and a fake sample.csv for local testing."""
import csv
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
IMAGES_DIR = PROJECT_DIR / "data" / "images"
CSV_PATH = PROJECT_DIR / "data" / "sample.csv"

CATEGORIES = ["cat", "dog", "bird"]
BG_COLOR = (220, 220, 220)

# (dominant_category, n_images, dominant_mean)
# First 300 images peak at cat, next 300 at dog, last 400 at bird
GROUPS = [
    ("cat",  300, 0.85),
    ("dog",  300, 0.85),
    ("bird", 400, 0.85),
]
DOMINANT_STD = 0.05  # tight Gaussian around the mean

# Fraction of labeled images that are mispredicted (scores peak at a wrong
# category) so the confusion matrix has off-diagonal cells to inspect.
NOISE_FRAC = 0.15

# Number of unlabeled (empty gt) "background" images, for the BG matrix row.
N_BG = 40

rng = np.random.default_rng(42)


def make_placeholder(path: Path, label: str) -> None:
    img = Image.new("RGB", (128, 128), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, 124, 124], outline=(80, 80, 80), width=2)
    bbox = draw.textbbox((0, 0), label)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((128 - tw) // 2, (128 - th) // 2), label, fill=(40, 40, 40))
    img.save(path)


def make_scores(dominant: str, mean: float, std: float) -> dict[str, float]:
    """Draw dominant score ~ N(mean, std), split remainder uniformly between the other two."""
    dom_score = float(np.clip(rng.normal(mean, std), 0.01, 0.99))
    remainder = 1.0 - dom_score
    others = [c for c in CATEGORIES if c != dominant]
    split = float(rng.uniform(0, 1))
    other_scores = [remainder * split, remainder * (1 - split)]
    scores = {cat: round(s, 4) for cat, s in zip(others, other_scores)}
    scores[dominant] = round(dom_score, 4)
    # absorb rounding error into dominant score
    diff = round(1.0 - sum(scores.values()), 4)
    scores[dominant] = round(scores[dominant] + diff, 4)
    return scores


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    idx = 0

    # Labeled images: ground truth is the group's category. For NOISE_FRAC of
    # them, the scores peak at a different (wrong) category -> a misprediction.
    for dominant, n, mean in GROUPS:
        for _ in range(n):
            img_path = IMAGES_DIR / f"image_{idx:04d}.png"
            make_placeholder(img_path, f"img {idx}")

            if rng.random() < NOISE_FRAC:
                wrong = [c for c in CATEGORIES if c != dominant]
                peak = str(rng.choice(wrong))
            else:
                peak = dominant
            scores = make_scores(peak, mean, DOMINANT_STD)

            row = {"image_path": str(img_path.resolve()), "gt": dominant}
            for cat in CATEGORIES:
                row[f"score_{cat}"] = scores[cat]
            rows.append(row)
            idx += 1

    # Background images: no ground-truth label (empty gt), scores peak at a
    # random category -> these populate the BG row of the confusion matrix.
    for _ in range(N_BG):
        img_path = IMAGES_DIR / f"image_{idx:04d}.png"
        make_placeholder(img_path, f"bg {idx}")
        peak = str(rng.choice(CATEGORIES))
        scores = make_scores(peak, 0.85, DOMINANT_STD)

        row = {"image_path": str(img_path.resolve()), "gt": ""}
        for cat in CATEGORIES:
            row[f"score_{cat}"] = scores[cat]
        rows.append(row)
        idx += 1

    total = sum(n for _, n, _ in GROUPS) + N_BG
    fieldnames = ["image_path", "gt"] + [f"score_{cat}" for cat in CATEGORIES]

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {total} placeholder images in {IMAGES_DIR}")
    print(f"Wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
