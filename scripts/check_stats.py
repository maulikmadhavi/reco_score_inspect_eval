import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import data_utils

df = pd.read_csv("data/sample.csv")
print("Rows:", len(df))
print("Empty gt (BG) rows:", (df["gt"].fillna("").astype(str).str.strip() == "").sum())

cats = data_utils.discover_categories(df)
cm = data_utils.get_confusion_matrix(df, cats)
print("gt_labels:", cm["gt_labels"])
print("pred_labels:", cm["pred_labels"])
print("counts:")
for label, row in zip(cm["gt_labels"], cm["counts"]):
    print(f"  {label:5s} {row}")
