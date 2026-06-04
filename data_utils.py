import pandas as pd


def load_dataframe(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def discover_categories(df: pd.DataFrame) -> list[str]:
    if "image_path" not in df.columns:
        return []
    return [col[len("score_"):] for col in df.columns if col.startswith("score_")]


def get_category_records(df: pd.DataFrame, category: str) -> list[dict]:
    score_col = f"score_{category}"
    label_col = "gt_name" if "gt_name" in df.columns else "gt"
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
