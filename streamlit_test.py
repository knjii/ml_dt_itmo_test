import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from catboost import CatBoostClassifier

st.title('Insurance response')

MODEL_PATH = './artifacts/final_cat_model.cbm'
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/get_prediction")

DEFAULT_VALUES_DICT = {
    'Gender': 'Male',
    'Age': int(36),
    'Driving_License': int(1),
    'Region_Code': float(26),
    'Previously_Insured': int(0),
    'Vehicle_Age': '< 1 Year',
    'Vehicle_Damage': 'No',
    'Annual_Premium': float(2630),
    'Policy_Sales_Channel': float(152),
    'Vintage': int(187)
}

# CLM_NAMES = ['Gender', 'Age', 'Driving_License', 'Region_Code', 'Previously_Insured',
#              'Vehicle_Age', 'Vehicle_Damage', 'Annual_Premium', 'Policy_Sales_Channel', 'Vintage', 'Annual_Premium_log']

PSC_BANNED = [72, 77, 84, 85, 141, 144, 149, 161, 162]


def _int_like_to_float(value, label):
    """Cast numeric input to float while warning/rounding non-integer values."""
    numeric = float(value)
    if not numeric.is_integer():
        rounded = float(round(numeric))
        # st.warning(f"{label} должен быть целым. Значение {numeric} будет округлено до {rounded}.")
        return rounded
    return numeric


def _to_int(value, default):
    if value is None:
        return int(default)
    return int(value)


def _to_float(value, default):
    if value is None:
        return float(default)
    return float(value)


def predict(model, gender=None, age=None,
            driving_license=None, region_code=None,
            previously_insured=None, vehicle_age=None,
            vehicle_damage=None, annual_premium=None,
            policy_sales_channel=None, vintage=None):

    gender = str(gender or DEFAULT_VALUES_DICT['Gender'])
    age = _to_int(age, DEFAULT_VALUES_DICT['Age'])
    driving_license = DEFAULT_VALUES_DICT['Driving_License'] if driving_license is None else (1 if driving_license == 'Yes' or driving_license == 1 else 0)
    region_code = _to_float(region_code, DEFAULT_VALUES_DICT['Region_Code'])
    previously_insured = DEFAULT_VALUES_DICT['Previously_Insured'] if previously_insured is None else (1 if previously_insured == 'Yes' or previously_insured == 1 else 0)

    v_a_map = {
        '< 1 Year': '< 1 Year',
        '1-2 Year': '1-2 Year',
        '> 2 Years': '> 2 Years'
    }
    vehicle_age = v_a_map.get(vehicle_age, DEFAULT_VALUES_DICT['Vehicle_Age'])

    vehicle_damage = str(vehicle_damage or DEFAULT_VALUES_DICT['Vehicle_Damage'])

    policy_sales_channel = _to_float(policy_sales_channel, DEFAULT_VALUES_DICT['Policy_Sales_Channel'])
    if policy_sales_channel in PSC_BANNED:
        raise ValueError('Policy sales channel is banned')

    annual_premium = _to_float(annual_premium, DEFAULT_VALUES_DICT['Annual_Premium'])
    vintage = _to_int(vintage, DEFAULT_VALUES_DICT['Vintage'])

    payload = {
        'Gender': gender,
        'Age': age,
        'Driving_License': driving_license,
        'Region_Code': region_code,
        'Previously_Insured': previously_insured,
        'Vehicle_Age': vehicle_age,
        'Vehicle_Damage': vehicle_damage,
        'Annual_Premium': annual_premium,
        'Policy_Sales_Channel': policy_sales_channel,
        'Vintage': vintage
    }

    # Попытка отправить на backend; при ошибке используем локальную модель.
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and 'label' in data:
            print('Успешно использовали бэкенд')
            return data['label']
    except Exception:
        pass

    user_data = {
        'Gender': gender,
        'Age': age,
        'Driving_License': driving_license,
        'Region_Code': region_code,
        'Previously_Insured': previously_insured,
        'Vehicle_Age': vehicle_age,
        'Vehicle_Damage': vehicle_damage,
        'Annual_Premium': annual_premium,
        'Policy_Sales_Channel': policy_sales_channel,
        'Vintage': vintage
    }

    print('Используем локальную функцию')

    user_data['Annual_Premium_log'] = np.log1p(user_data["Annual_Premium"])

    # return user_data

    user_data = pd.DataFrame(data=[user_data])

    pred_p = model.predict_proba(X=user_data)
    surv_prob = float(pred_p[0][1])

    if surv_prob >= 0.7:
        return 'Will respond'
    return 'Will not respond'


if 'gender_options' not in st.session_state:
    st.session_state.gender_options = ['Male', 'Female']

if 'bool_options' not in st.session_state:
    st.session_state.bool_options = ['Yes', 'No']

if 'catboost_model' not in st.session_state:
    catboost_model = CatBoostClassifier()
    catboost_model.load_model(MODEL_PATH)
    st.session_state.catboost_model = catboost_model

st.selectbox(label="Gender", options=st.session_state.gender_options, key='gender')

st.number_input(label="Age", min_value=0, max_value=120, value=36, step=1, key='age')

st.selectbox(label="Driving license", options=st.session_state.bool_options, key='driving_license')

region_code_raw = st.number_input(label="Region code", min_value=0.0, max_value=52.0, value=26.0, step=1.0, format="%.0f", key='region_code')

st.selectbox(label="Previously insured", options=st.session_state.bool_options, key='previously_insured')

st.selectbox(label="Vehicle age", options=['< 1 Year', '1-2 Year', '> 2 Years'], key='vehicle_age')

st.selectbox(label="Vehicle damage", options=st.session_state.bool_options, key='vehicle_damage')

st.number_input(label="Annual premium", min_value=0.0, value=2630.0, step=0.1, key='annual_premium')

policy_sales_channel_raw = st.number_input(label="Policy sales channel", min_value=0.0, max_value=163.0, value=152.0, step=1.0, format="%.0f", key='policy_sales_channel')

st.number_input(label="Vintage", min_value=10, max_value=299, value=187, step=1, key='vintage')

if st.button(label='Get prediction', key='get_pred'):
    with st.spinner("Wait for it..."):
        region_code_value = _int_like_to_float(region_code_raw, "Region code")
        policy_sales_channel_value = _int_like_to_float(policy_sales_channel_raw, "Policy sales channel")
        prediction = predict(model=st.session_state.catboost_model, gender=st.session_state.gender, age=st.session_state.age,
                             driving_license=st.session_state.driving_license, region_code=region_code_value, previously_insured=st.session_state.previously_insured,
                             vehicle_age=st.session_state.vehicle_age, vehicle_damage=st.session_state.vehicle_damage, annual_premium=st.session_state.annual_premium,
                             policy_sales_channel=policy_sales_channel_value, vintage=st.session_state.vintage)
    st.success(prediction)
