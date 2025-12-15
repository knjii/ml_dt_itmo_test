import streamlit as st
import requests
import os
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

if config['using_docker']:
    BACKEND_PREDICT_URL = config['backend_predict_url_docker']
else:
    if config['using_server']:
        BACKEND_PREDICT_URL = config['backend_predict_url_server']
    else:
        BACKEND_PREDICT_URL = config['backend_predict_url_local']

def load_css():
    css_file = "style.css"  
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"Файл {css_file} не найден")

load_css()

st.title('Insurance response', anchor = False) # anchor - гиперссылка справа от текста, из-за неё не центрировалось нормально

left, center, right = st.columns([1, 2, 1])
with center:
    st.text('Our model predicts whether the client will or will not respond positively to a car insurance offer')



def predict(gender=None, age=None,
            driving_license=None, region_code=None,
            previously_insured=None, vehicle_age=None,
            vehicle_damage=None, annual_premium=None,
            policy_sales_channel=None, vintage=None):

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

    resp = requests.post(BACKEND_PREDICT_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and 'prediction' in data:
        return data['prediction']
    

if 'gender_options' not in st.session_state:
    st.session_state.gender_options = ['Male', 'Female']

if 'bool_options' not in st.session_state:
    st.session_state.bool_options = ['Yes', 'No']


st.markdown("### 📊 Personal Information")

basic_info_cols = st.columns(3)

with basic_info_cols[0]:
    st.selectbox(label="Gender", options=st.session_state.gender_options, key='gender')
    
with basic_info_cols[1]:
    st.number_input(label="Age", min_value=0, max_value=120, value=36, step=1, placeholder='Male', key='age')

with basic_info_cols[2]:
    st.number_input(label="Driving license", min_value=0, max_value=1, step=1, key='driving_license')

st.text("")
st.markdown("### 🚗 Vehicle Details")

vehicle_info_cols = st.columns(3)

with vehicle_info_cols[0]:
    st.number_input(label="Region code", min_value=0.0, max_value=52.0, value=26.0, step=1.0, format="%.0f", key='region_code')
    
with vehicle_info_cols[1]:
    st.selectbox(label="Vehicle age", options=['< 1 Year', '1-2 Year', '> 2 Years'], key='vehicle_age')

with vehicle_info_cols[2]:
    st.selectbox(label="Vehicle damage", options=st.session_state.bool_options, key='vehicle_damage')

st.text("")
st.markdown("### 🏢 Insurance Information")

vehicle_info_cols = st.columns(3)

with vehicle_info_cols[0]:
    st.number_input(label="Previously insured", min_value=0, max_value=1, step=1, key='previously_insured')
    
with vehicle_info_cols[1]:
    st.number_input(label="Vintage", min_value=10, max_value=299, value=187, step=1, key='vintage')

with vehicle_info_cols[2]:
    st.number_input(label="Annual premium", min_value=0.0, value=2630.0, step=0.1, key='annual_premium')
 
    st.number_input(label="Policy sales channel", min_value=0.0, max_value=163.0, value=152.0, step=1.0, format="%.0f", key='policy_sales_channel')

st.text("")

left, center, right = st.columns(3)
with center:
    if st.button(label='Get prediction', key='get_pred', width="stretch"):
        with st.spinner("Wait for it..."):
            prediction = predict(gender=st.session_state.gender, age=st.session_state.age,
                                driving_license=st.session_state.driving_license, region_code=st.session_state.region_code, previously_insured=st.session_state.previously_insured,
                                vehicle_age=st.session_state.vehicle_age, vehicle_damage=st.session_state.vehicle_damage, annual_premium=st.session_state.annual_premium,
                                policy_sales_channel=st.session_state.policy_sales_channel, vintage=st.session_state.vintage)
        st.success(prediction)
