import pandas as pd
df = pd.read_csv("data/sample.csv")
print("Rows:", len(df))
sums = df[["score_cat","score_dog","score_bird"]].sum(axis=1)
print("Row sums min/max:", round(sums.min(), 4), round(sums.max(), 4))
print(df[["score_cat","score_dog","score_bird"]].describe().round(3))
