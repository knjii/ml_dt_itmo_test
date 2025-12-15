# app.py
import os
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import uvicorn
from contextlib import asynccontextmanager

# Путь к модели
script_dir = os.path.dirname(os.path.abspath(__file__))
LGBM_MODEL_PATH = "artifacts/lgbm_model_jl.pkl"

# Глобальные переменные
model = None
feature_cols = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, feature_cols
    try:
        model = joblib.load(LGBM_MODEL_PATH)
        
        if hasattr(model, 'feature_names_'):
            feature_cols = list(model.feature_names_)
        else:
            feature_cols = [
                'Gender', 'Age', 'Driving_License', 'Region_Code',
                'Previously_Insured', 'Vehicle_Age', 'Vehicle_Damage',
                'Annual_Premium', 'Policy_Sales_Channel', 'Vintage',
                'Annual_Premium_log'
            ]
    except Exception as e:
        print(f"Ошибка загрузки модели: {e}")
        raise
    yield
    model = None

app = FastAPI(title="Insurance Prediction API", version="1.0", lifespan=lifespan)

class InsuranceRequest(BaseModel):
    Gender: str = Field(..., description="Пол: Male или Female")
    Age: float = Field(..., description="Возраст")
    Driving_License: int = Field(..., description="Водительские права: 0 или 1")
    Region_Code: float = Field(..., description="Код региона (0-52)")
    Previously_Insured: int = Field(..., description="Ранее застрахован: 0 или 1")
    Vehicle_Age: str = Field(..., description="Возраст авто: < 1 Year, 1-2 Year, > 2 Years")
    Vehicle_Damage: str = Field(..., description="Повреждение авто: Yes или No")
    Annual_Premium: float = Field(..., description="Годовая премия")
    Policy_Sales_Channel: float = Field(..., description="Канал продаж (1-163)")
    Vintage: int = Field(..., description="Стаж в днях (неотрицательное)")

    @field_validator('Gender')
    def validate_gender(cls, v):
        if v not in ['Male', 'Female']:
            raise ValueError('Пол должен быть Male или Female')
        return v

    @field_validator('Age')
    def validate_age(cls, v):
        if v < 18:
            raise ValueError('Возраст должен быть от 18 лет')
        if v > 120:
            raise ValueError('Возраст не может превышать 120 лет')
        return v

    @field_validator('Driving_License')
    def validate_driving_license(cls, v):
        if v not in [0, 1]:
            raise ValueError('В поле "Driving_License" введите 0, если у вас нет водительских прав или 1, если права есть')
        return v

    @field_validator('Region_Code')
    def validate_region_code(cls, v):
        if v < 0 or v > 52:
            raise ValueError('Код региона должен быть от 0 до 52')
        return v

    @field_validator('Previously_Insured')
    def validate_previously_insured(cls, v):
        if v not in [0, 1]:
            raise ValueError('В поле "Previously_Insured" введите 0, если ранее не были застрахованы, или 1, если ранее вы были засрахованы')
        return v

    @field_validator('Vehicle_Age')
    def validate_vehicle_age(cls, v):
        if v not in ['< 1 Year', '1-2 Year', '> 2 Years']:
            raise ValueError('В поле "Vehicle_Age" введите возраст автомобиля в формате < 1 Year, 1-2 Year или > 2 Years')
        return v

    @field_validator('Vehicle_Damage')
    def validate_vehicle_damage(cls, v):
        if v not in ['Yes', 'No']:
            raise ValueError('В поле "Vehicle_Damage" введите "Yes", если автомобиль поврежден или "No", если повреждений нет')
        return v

    @field_validator('Annual_Premium')
    def validate_annual_premium(cls, v):
        if v < 0:
            raise ValueError('Годовая премия в поле "Annual_Premium" не может быть отрицательной')
        return v

    @field_validator('Policy_Sales_Channel')
    def validate_policy_sales_channel(cls, v):
        if v < 1 or v > 163:
            raise ValueError('Канал продаж должен быть от 1 до 163')
        return v

    @field_validator('Vintage')
    def validate_vintage(cls, v):
        if v < 0:
            raise ValueError('Значение в поле "Vintage" не может быть отрицательным')
        return v

# Ответ
class SimplePredictionResponse(BaseModel):
    prediction: str = Field(..., description="ДА - купит, НЕТ - не купит")
    message: str = Field(..., description="Пояснение")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model is not None else "error",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=SimplePredictionResponse)
async def predict(data: InsuranceRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    
    try:
        input_dict = data.model_dump()
        input_df = pd.DataFrame([input_dict])
        input_df["Annual_Premium_log"] = np.log1p(input_df["Annual_Premium"])
        
        if feature_cols:
            common_cols = [col for col in feature_cols if col in input_df.columns]
            input_df = input_df[common_cols]
        
        prediction_p = model.predict_proba(X=input_df)
        positive_prob = float(prediction_p[0][1])
        will_buy = positive_prob >= 0.24528510587877086

        print(positive_prob)
        
        if will_buy:
            return {
                "prediction": "ДА",
                "message": f"Клиент скорее всего КУПИТ страховой продукт (p={positive_prob:.3f})"
            }
        else:
            return {
                "prediction": "НЕТ",
                "message": f"Клиент скорее всего НЕ купит страховой продукт (p={positive_prob:.3f})"
            }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Insurance Prediction API",
        "endpoints": {
            "GET /": "Информация",
            "GET /health": "Проверка состояния",
            "POST /predict": "Предсказание"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
