from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = "./artifacts/final_cat_model.cbm"
catboost_model: Optional[CatBoostClassifier] = None


class CatboostRequest(BaseModel):
    Gender: str
    Age: int
    Driving_License: int
    Region_Code: float
    Previously_Insured: int
    Vehicle_Age: str
    Vehicle_Damage: str
    Annual_Premium: float
    Policy_Sales_Channel: float
    Vintage: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    global catboost_model
    model = CatBoostClassifier()
    model.load_model(MODEL_PATH)
    catboost_model = model
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/get_prediction")
def get_prediction(prediction_features: CatboostRequest):
    if catboost_model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    features = prediction_features.model_dump()
    features["Annual_Premium_log"] = np.log1p(features["Annual_Premium"])

    df = pd.DataFrame(data=[features])
    pred_p = catboost_model.predict_proba(X=df)
    surv_prob = float(pred_p[0][1])

    return {
        "probability": surv_prob,
        "label": "Will respond" if surv_prob >= 0.7 else "Will not respond",
    }
