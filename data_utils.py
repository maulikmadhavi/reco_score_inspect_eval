import pandas as pd

# Ground-truth label used for images that have no annotation (empty/None gt).
BG_LABEL = "BG"


def load_dataframe(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def _gt_column(df: pd.DataFrame) -> str:
    """Name of the ground-truth column ('gt_name' preferred, else 'gt')."""
    return "gt_name" if "gt_name" in df.columns else "gt"


def discover_categories(df: pd.DataFrame) -> list[str]:
    if "image_path" not in df.columns:
        return []
    return [col[len("score_"):] for col in df.columns if col.startswith("score_")]


def get_category_records(df: pd.DataFrame, category: str) -> list[dict]:
    score_col = f"score_{category}"
    label_col = _gt_column(df)
    sub = df[["image_path", score_col, label_col]].dropna()
    sub = sub[sub[label_col] == category]
    sub = sub[["image_path", score_col]].rename(columns={score_col: "score", "image_path": "image"})
    sub = sub.sort_values("score", ascending=False)
    return sub.to_dict(orient="records")


def get_distribution(df: pd.DataFrame, category: str) -> dict:
    scores = [r["score"] for r in get_category_records(df, category)]
    return {
        "scores": scores,
        "min": min(scores) if scores else 0.0,
        "max": max(scores) if scores else 1.0,
    }


def get_images_around(records: list[dict], score: float, window: int = 10) -> list[dict]:
    if not records:
        return []
    # find index of the record whose score is closest to the selected value
    closest_idx = min(range(len(records)), key=lambda i: abs(records[i]["score"] - score))
    start = max(0, closest_idx - window)
    end = min(len(records), closest_idx + window + 1)
    return records[start:end]


def get_predictions(df: pd.DataFrame) -> pd.Series:
    """Predicted category per row.

    Uses the CSV's 'pred' column if present; otherwise falls back to the
    category with the highest score_<category> value (argmax).
    """
    if "pred" in df.columns:
        return df["pred"]

    categories = discover_categories(df)
    score_cols = [f"score_{cat}" for cat in categories]
    # idxmax returns the winning column name per row, e.g. "score_dog"
    winning_col = df[score_cols].idxmax(axis=1)
    return winning_col.str[len("score_"):]


def normalize_gt(df: pd.DataFrame) -> pd.Series:
    """Ground-truth label per row, with empty/missing labels mapped to BG."""
    gt_col = _gt_column(df)
    if gt_col not in df.columns:
        return pd.Series([BG_LABEL] * len(df), index=df.index)
    gt = df[gt_col].fillna("").astype(str).str.strip()
    return gt.replace("", BG_LABEL)


def get_confusion_matrix(df: pd.DataFrame, categories: list[str]) -> dict:
    """Count matrix of ground-truth (rows) vs predicted (cols).

    Rows are the categories plus a trailing BG row (always present).
    Columns are the categories (predictions are always a real category).
    """
    gt = normalize_gt(df)
    pred = get_predictions(df)

    gt_labels = list(categories) + [BG_LABEL]
    pred_labels = list(categories)

    counts = []
    for gt_label in gt_labels:
        row = []
        for pred_label in pred_labels:
            n = int(((gt == gt_label) & (pred == pred_label)).sum())
            row.append(n)
        counts.append(row)

    return {"gt_labels": gt_labels, "pred_labels": pred_labels, "counts": counts}


def get_cell_records(df: pd.DataFrame, gt_label: str, pred_label: str) -> list[dict]:
    """Images in one confusion-matrix cell, sorted by prediction confidence.

    The confidence is the predicted category's score (score_<pred_label>),
    sorted descending so the most confident predictions appear first.
    """
    gt = normalize_gt(df)
    pred = get_predictions(df)
    cell = df[(gt == gt_label) & (pred == pred_label)]

    score_col = f"score_{pred_label}"
    records = []
    for _, row in cell.iterrows():
        records.append({
            "image": row["image_path"],
            "score": float(row[score_col]),
            "gt": gt_label,
            "pred": pred_label,
        })
    records.sort(key=lambda r: r["score"], reverse=True)
    return records
