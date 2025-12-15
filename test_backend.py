import pandas as pd
import requests
from sklearn.metrics import f1_score

test_path = "train.csv"

df = pd.read_csv(test_path)
y_true = df["Response"]

preds = []

for i, row in df.drop(columns=["id", "Response"]).iterrows():
    r = requests.post("http://127.0.0.1:8000/predict", json=row.to_dict())
    r = r.json()
    preds.append(1 if r["prediction"].strip() == "ДА" else 0)

print(f"F1 score: {(score:=f1_score(y_true, preds)):.4f}")
with open("test_backend_results.txt", mode='w', encoding='utf-8') as file:
    file.write(str(score))
