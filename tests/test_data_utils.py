import pandas as pd
import pytest
import data_utils


def make_df(**kwargs):
    return pd.DataFrame(kwargs)


def test_discover_categories_basic():
    df = make_df(image_path=[], score_cat=[], score_dog=[])
    assert set(data_utils.discover_categories(df)) == {"cat", "dog"}


def test_discover_categories_no_image_path_col():
    df = make_df(score_cat=[], score_dog=[])
    assert data_utils.discover_categories(df) == []


def test_discover_categories_empty():
    df = make_df(image_path=["a"], gt=["cat"])
    assert data_utils.discover_categories(df) == []


def test_get_category_records_gt_filter():
    df = make_df(
        image_path=["a", "b", "c"],
        gt=["cat", "dog", "cat"],
        score_cat=[0.9, 0.8, 0.5],
    )
    records = data_utils.get_category_records(df, "cat")
    # only rows where gt == "cat" (a and c)
    assert len(records) == 2
    assert all(r["image"] in ("a", "c") for r in records)


def test_get_category_records_sorted_descending():
    df = make_df(
        image_path=["a", "b", "c"],
        gt=["cat", "cat", "cat"],
        score_cat=[0.1, 0.9, 0.5],
    )
    records = data_utils.get_category_records(df, "cat")
    scores = [r["score"] for r in records]
    assert scores == sorted(scores, reverse=True)


def test_get_category_records_drops_nan():
    df = make_df(image_path=["a", "b"], gt=["cat", "cat"], score_cat=[0.5, None])
    records = data_utils.get_category_records(df, "cat")
    assert len(records) == 1
    assert records[0]["image"] == "a"


def test_get_category_records_gt_name_col():
    df = make_df(
        image_path=["a", "b"],
        gt_name=["dog", "dog"],
        score_dog=[0.9, 0.7],
    )
    records = data_utils.get_category_records(df, "dog")
    assert len(records) == 2


def test_get_distribution_min_max():
    df = make_df(
        image_path=["a", "b", "c"],
        gt=["cat", "cat", "cat"],
        score_cat=[0.2, 0.8, 0.5],
    )
    dist = data_utils.get_distribution(df, "cat")
    assert dist["min"] == pytest.approx(0.2)
    assert dist["max"] == pytest.approx(0.8)
    assert sorted(dist["scores"]) == pytest.approx([0.2, 0.5, 0.8])


def test_get_images_around_center():
    records = [{"score": s, "image": f"img_{i}"} for i, s in enumerate([0.9, 0.7, 0.5, 0.3, 0.1])]
    result = data_utils.get_images_around(records, 0.5, window=1)
    scores = [r["score"] for r in result]
    assert 0.5 in scores


def test_get_images_around_empty():
    assert data_utils.get_images_around([], 0.5) == []


def test_get_images_around_window_clamp():
    records = [{"score": 0.9, "image": "a"}, {"score": 0.1, "image": "b"}]
    result = data_utils.get_images_around(records, 0.9, window=100)
    assert len(result) == 2


# ── Confusion matrix helpers ──────────────────────────────────────────────────


def test_get_predictions_uses_pred_column():
    df = make_df(image_path=["a", "b"], pred=["cat", "dog"],
                 score_cat=[0.9, 0.1], score_dog=[0.1, 0.9])
    preds = data_utils.get_predictions(df)
    assert list(preds) == ["cat", "dog"]


def test_get_predictions_argmax_fallback():
    df = make_df(image_path=["a", "b"], score_cat=[0.9, 0.2], score_dog=[0.1, 0.8])
    preds = data_utils.get_predictions(df)
    assert list(preds) == ["cat", "dog"]


def test_normalize_gt_empty_becomes_bg():
    df = make_df(image_path=["a", "b", "c"], gt=["cat", "", None])
    gts = data_utils.normalize_gt(df)
    assert list(gts) == ["cat", "BG", "BG"]


def test_get_confusion_matrix_counts_and_bg_row():
    df = make_df(
        image_path=["a", "b", "c", "d"],
        gt=["cat", "cat", "dog", ""],          # last row is BG
        score_cat=[0.9, 0.2, 0.1, 0.8],         # argmax: cat, dog, dog, cat
        score_dog=[0.1, 0.8, 0.9, 0.2],
    )
    cm = data_utils.get_confusion_matrix(df, ["cat", "dog"])
    assert cm["gt_labels"] == ["cat", "dog", "BG"]
    assert cm["pred_labels"] == ["cat", "dog"]
    # cat->cat=1, cat->dog=1 ; dog->dog=1 ; BG->cat=1
    assert cm["counts"] == [[1, 1], [0, 1], [1, 0]]


def test_get_cell_records_filter_and_sort_desc():
    df = make_df(
        image_path=["a", "b", "c"],
        gt=["cat", "cat", "cat"],
        score_cat=[0.1, 0.1, 0.9],
        score_dog=[0.9, 0.8, 0.1],              # a,b predicted dog; c predicted cat
    )
    records = data_utils.get_cell_records(df, "cat", "dog")
    # only a and b (gt=cat, pred=dog), sorted by dog score descending
    assert [r["image"] for r in records] == ["a", "b"]
    assert records[0]["score"] == pytest.approx(0.9)
    assert records[1]["score"] == pytest.approx(0.8)
