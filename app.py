#!/usr/bin/python3

import pandas as pd
import streamlit as st
import geopandas as gpd
import plotly_express as px

from datetime import date, timedelta
from plotly import graph_objects as go

# Custom modules
from map_utils import give_data, give_map_object

# Setting page configuration
st.set_page_config(page_title="Covid19 India Dashboard")

# Constants
GEO_PATH_STATES = './geodata/states/'
GEO_PATH_INDIA = './geodata/'
MAPPER1 = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11'}
MAPPER2 = {'an': "Andaman and Nicobar Islands", 'ap': "Andhra Pradesh", 'ar': "Arunachal Pradesh", 'as': "Assam", 'br': "Bihar", 'ch': "Chandigarh", 'ct': "Chhattisgarh", 'dd': "Dadra and Nagar Haveli and Daman and Diu", 'dl': "Delhi", 'dn': "Dadra and Nagar Haveli", 'ga': "Goa", 'gj': "Gujarat",
       'hp': "Himachal Pradesh", 'hr': "Haryana", 'jh': "Jharkhand", 'jk': "Jammu and Kashmir", 'ka': "Karnataka", 'kl': "Kerala", 'la': "Ladakh", 'ld': "Lakshadweep", 'mh': "Maharashtra", 'ml': "Meghalaya", 'mn': "Manipur", 'mp': "Madhya Pradesh",
       'mz': "Mizoram", 'nl': "Nagaland", 'or': "Odisha", 'pb': "Punjab", 'py': "Puducherry", 'rj': "Rajasthan", 'sk': "Sikkim", 'tg': "Telangana", 'tn': "Tamil Nadu", 'tr': "Tripura", 'tt': "tt", 'un': "un",
       'up': "Uttar Pradesh", 'ut': "Uttarakhand", 'wb': "West Bengal", 'date': 'date', "status": "status"}
MAPPER3 = {'Andaman and Nicobar Islands': 'andamannicobarislands', 'Andhra Pradesh': 'andhrapradesh', 'Arunachal Pradesh': 'arunachalpradesh', 'Assam': 'assam', 'Bihar': 'bihar', 'Chandigarh': 'chandigarh', 'Chhattisgarh': 'chhattisgarh', 'Dadra and Nagar Haveli and Daman and Diu': 'dnh-and-dd', 
        'Delhi': 'delhi', 'Goa': 'goa', 'Gujarat': 'gujarat', 'Himachal Pradesh': 'himachalpradesh', 'Haryana': 'haryana', 'Jharkhand': 'jharkhand', 'Jammu and Kashmir': 'jammukashmir', 'Karnataka': 'karnataka', 'Kerala': 'kerala', 'Ladakh': 'ladakh', 'Lakshadweep': 'lakshadweep', 'Maharashtra': 'maharashtra', 
        'Meghalaya': 'meghalaya', 'Manipur': 'manipur', 'Madhya Pradesh': 'madhyapradesh', 'Mizoram': 'mizoram', 'Nagaland': 'nagaland', 'Odisha': 'odisha', 'Punjab': 'punjab', 'Puducherry': 'puducherry', 'Rajasthan': 'rajasthan', 'Sikkim': 'sikkim', 'Telangana': 'telangana', 'Tamil Nadu': 'tamilnadu', 
        'Tripura': 'tripura', 'Uttar Pradesh': 'uttarpradesh', 'Uttarakhand': 'uttarakhand', 'West Bengal': 'westbengal'}

# Get India's data
def get_india_data():
    india_ts = pd.read_csv('https://api.covid19india.org/csv/latest/case_time_series.csv', parse_dates=['Date_YMD'])

    return india_ts

def preprocess_india_data():
    india_ts['Total Active'] = india_ts['Total Confirmed'] - india_ts['Total Recovered']
    return india_ts

@st.cache(allow_output_mutation=True)
def initialize_data():
    india_ts = get_india_data()

    # Applying preprocessing steps

    return india_ts

overall_ts = initialize_data()

######### Web Design #########
st.title("Covid-19 Trend Visualizer in India")

type_cases = ['Daily Confirmed', 'Total Confirmed', 'Daily Recovered', 'Total Recovered', 'Daily Deceased', 'Total Deceased']
tc = st.selectbox(label="Type of Cases", options=type_cases)
st.plotly_chart(px.line(data_frame=overall_ts, x='Date_YMD', y=tc))