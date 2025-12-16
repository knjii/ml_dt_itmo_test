import os
import pandas as pd
import requests
from sklearn.metrics import f1_score
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

if config['using_server']:
    BACKEND_PREDICT_URL = config['backend_predict_url_server']
else:
    BACKEND_PREDICT_URL = config['backend_predict_url_local']
    
dataset_path = config['train_dataset_path']
y_true, preds = [], []

for i, chunk in enumerate(pd.read_csv(dataset_path, chunksize=5000)):
    y_true.extend(chunk["Response"].astype(int).tolist())
    features = chunk.drop(columns=[c for c in ["id", "Response"] if c in chunk.columns])
    for _, row in features.iterrows():
        r = requests.post(BACKEND_PREDICT_URL, json=row.to_dict())
        r = r.json()
        preds.append(1 if r["prediction"].strip() == "ДА" else 0)
    print('Прошла итерация №', i)

print(f"F1 score: {(score:=f1_score(y_true, preds)):.4f}")
with open("test_backend_results.txt", mode='w', encoding='utf-8') as file:
    file.write(str(score))