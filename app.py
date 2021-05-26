#!/usr/bin/python3

import numpy as np
import pandas as pd
import streamlit as st

from datetime import date, timedelta
from plotly import graph_objects as go

# Setting page configuration
st.set_page_config(page_title="Covid19 India Dashboard")

# Constants
GEO_PATH_STATES = './geodata/states/'
GEO_PATH_INDIA = './geodata/'

# Get India's data
def get_india_data():
    india_ts = pd.read_csv('https://api.covid19india.org/csv/latest/case_time_series.csv', parse_dates=['Date_YMD'])

    return india_ts

def get_states_data():
    states_ts = pd.read_csv('https://api.covid19india.org/csv/latest/states.csv', parse_dates=['Date'])

    return states_ts

def preprocess_india_data(india_ts):
    india_ts['Total Active'] = india_ts['Total Confirmed'] - india_ts['Total Recovered'] - india_ts['Total Deceased']
    india_ts['Daily Active'] = india_ts['Daily Confirmed'] - india_ts['Daily Recovered'] - india_ts['Daily Deceased']

    return india_ts

def preprocess_states_data(states_ts):
    states_ts.replace(np.nan, 0)
    states_ts['Active'] = states_ts['Confirmed'] - states_ts['Recovered'] - states_ts['Deceased']

    return states_ts

@st.cache(allow_output_mutation=True)
def initialize_data():
    india_ts = get_india_data()
    states_ts = get_states_data()

    # Applying preprocessing steps
    india_ts = preprocess_india_data(india_ts)
    states_ts = preprocess_states_data(states_ts)

    return india_ts, states_ts

overall_ts, states = initialize_data()

######### Web Design #########
st.title("Covid-19 Trend Visualizer in India")

see_states = st.checkbox("Wanna see states data?")

if see_states:
    state_opt = st.selectbox('Pick a state', options=states['State'].unique()[states['State'].unique() != 'India'].tolist())
    type_opts = ['Confirmed', 'Active', 'Recovered', 'Deceased', 'Tested']
    tc = st.selectbox(label="Type of cases", options=type_opts)

    state_info = (states['State'] == state_opt)
    st.header(state_opt)
    st.subheader(tc+' Count')
    st.plotly_chart(go.Figure(go.Scatter(x=states[state_info]['Date'], y=states[state_info][tc])))
else:
    type_opts = ['Daily Confirmed', 'Total Confirmed', 'Daily Recovered', 'Total Recovered', 'Daily Deceased', 'Total Deceased', 'Daily Active', 'Total Active']
    tc = st.selectbox(label="Type of Cases", options=type_opts)
    st.plotly_chart(go.Figure(go.Scatter(x=overall_ts['Date_YMD'], y=overall_ts[tc])))