#!/usr/bin/python3

import os
import requests
import pandas as pd
import streamlit as st
import geopandas as gpd
import plotly_express as px

from datetime import date, timedelta
from plotly import graph_objects as go

# Custom modules
from map_utils import give_data, give_map_object

# Constants
GEO_PATH_STATES = './geodata/states/'
GEO_PATH_INDIA = './geodata/'
MAPPER1 = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07'}
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
    URL = 'https://api.covid19india.org/data.json'

    def convert(date): 
        date_splits = date.split() 
        converted = "-".join([date_splits[0], MAPPER1[date_splits[1]], '2020']) 
        return converted

    raw_data = requests.get(URL)
    jsonobj = raw_data.json()
    cases = jsonobj['cases_time_series']
    tests = jsonobj['tested']

    india_data = pd.DataFrame(cases)
    india_data['date'] = india_data['date'].apply(convert)
    tests = pd.DataFrame(tests)

    return india_data, tests

# Get State's data
def get_states_data():
    URL = 'https://api.covid19india.org/states_daily.json'

    raw_data = requests.get(URL)
    jsonobj = raw_data.json()
    cases = jsonobj['states_daily']

    states_data = pd.DataFrame(cases)
    states_data.columns = states_data.columns.map(MAPPER2)

    return states_data

# Preprocessing India data
def preprocess_india_data(data):
    data.set_index(['date'], drop=True, inplace=True)
    data = data[data.columns[data.columns != 'date'].tolist()].astype("int64")
    data.index = pd.to_datetime(data.index, format='%d-%m-%Y')
    data['totalactive'] = (data['totalconfirmed'] - (data['totaldeceased'] + data['totalrecovered']))
    data['dailyactive'] = (data['dailyconfirmed'] - (data['dailydeceased'] + data['dailyrecovered']))

    columns = list(data.columns)
    for i, _ in enumerate(columns):
        for word in ['total', 'daily', 'confirmed', 'recovered', 'deceased', 'active']:
            columns[i] = (columns[i].replace(word, word.capitalize()+" "))
    data.columns = columns

    return data

# Preprocessing India's tests data
def preprocess_india_tests_data(tests):
    tests = tests[['updatetimestamp', 'totalsamplestested']]
    idx = tests[(tests['totalsamplestested'] == "")].index
    tests.drop(idx, axis=0, inplace=True)
    tests['updatetimestamp'] = pd.to_datetime(tests['updatetimestamp'])
    tests.set_index(['updatetimestamp'], drop=True, inplace=True)

    return tests

# Preprocessing States data
def preprocess_states_data(states_data):
    states_data['date'] = pd.to_datetime(states_data['date'])
    states_data.set_index(['date', 'status'], drop=True, inplace=True)
    states_data = states_data.astype("int64")
    states_data.drop(['tt', 'un'], axis=1, inplace=True)

    return states_data

# Get active states data
def get_active_states(states_data):
    confirmed = states_data.loc[(slice(None), "Confirmed"), :].droplevel(level=1)
    recovered = states_data.loc[(slice(None), "Recovered"), :].droplevel(level=1)
    deceased = states_data.loc[(slice(None), "Deceased"), :].droplevel(level=1)

    active = confirmed - (recovered + deceased)

    return active

# Get States Geo-data
def get_states_geo_data():
    states_geo = dict()

    for file_name in os.listdir(GEO_PATH_STATES):
        key = file_name.split('.')[0]
        states_geo[key] = gpd.read_file(GEO_PATH_STATES+file_name)

    return states_geo

# Get States current status
def get_states_current_status(districts_data):
    states_current_status = dict()

    for state in districts_data.keys():
        tmp1 = list()
        for district in districts_data[state]:
            tmp2 = districts_data[state][district][-1].copy()
            tmp2.update({'district': district})
            tmp1.append(tmp2)
        states_current_status[state] = pd.DataFrame(tmp1)

    return states_current_status

# Merging states current status and their Geo data
def merge_geo_and_states_data(districts_data):
    states_geo = get_states_geo_data()
    states_current_status = get_states_current_status(districts_data)

    merged_states = dict()
    for state in MAPPER3.keys():
        left_df = states_geo[MAPPER3[state]]
        right_df = states_current_status[state]

        tmp = pd.merge(left_df, right_df, left_on='district', right_on='district')
        tmp.drop(['notes', 'date', 'dt_code', 'st_code', 'year', 'st_nm'], axis=1, inplace=True)
        merged_states[state] = tmp

    return merged_states

@st.cache(allow_output_mutation=True)
def initialize_data():
    data, tests = get_india_data()
    states_data = get_states_data()
    districts_data = requests.get("https://api.covid19india.org/districts_daily.json")
    districts_data = districts_data.json()['districtsDaily']

    # Applying preprocessing steps
    data = preprocess_india_data(data)
    tests = preprocess_india_tests_data(tests)
    states_data = preprocess_states_data(states_data)
    active_states = get_active_states(states_data)
    merged_states = merge_geo_and_states_data(districts_data)

    return data, tests, states_data, active_states, districts_data, merged_states

data, tests, states_data, active_states, districts_data, merged_states = initialize_data()

######### Web Design #########
st.header("Covid-19 Trend Visualizer in India")

if st.sidebar.checkbox("Wanna see states data?", False):
    states_option1 = st.sidebar.selectbox("State", states_data.columns)
    states_option2 = st.sidebar.selectbox("State Type", ['Confirmed', 'Deceased', 'Recovered', 'Active'])

    st.subheader(states_option2+" Cases in "+states_option1)
    if states_option2 == "Active":
        show_data = active_states.loc[:, states_option1].cumsum()
        st.write(go.Figure(data=go.Scatter(x=show_data.index, y=show_data.values, mode='lines+markers')))
    else:
        show_data = states_data.loc[(slice(None), states_option2), states_option1].droplevel(level=1).cumsum()
        st.write(go.Figure(data=go.Scatter(x=show_data.index, y=show_data.values, mode='lines+markers')))

    st.subheader("Cases at a glance")
    yesterday = date.today() - timedelta(days=1)
    map_option = st.selectbox("Select an Option:", ["Confirmed", "Recovered", "Deceased", "Active"])
    customization = {'title': ' cases in India', 'tools': [('District', '@district')], 'status': "L"}
    map_obj = give_map_object(merged_states[states_option1], map_option.lower(), customization)
    st.bokeh_chart(map_obj, use_container_width=True)

    if st.sidebar.checkbox("See at district level?", False):
        select_district1 = st.sidebar.selectbox("District", list(districts_data[states_option1].keys()))
        select_district2 = st.sidebar.selectbox("District Type", ['Confirmed', 'Deceased', 'Recovered', 'Active'])
        district_level = pd.DataFrame(districts_data[states_option1][select_district1]).set_index(['date'])
        district_level.drop(['notes'], axis=1, inplace=True)

        st.subheader(select_district2+" Cases in "+select_district1)
        show_data = district_level[select_district2.lower()]
        st.write(go.Figure(data=go.Scatter(x=show_data.index, y=show_data.values, mode='lines+markers')))
else:
    header = "Data since 30-01-2020 to till date:"
    indias_option = st.selectbox("Select the measure:", data.columns, index=6)
    st.subheader(indias_option+" Cases in India.")
    if indias_option == "Total Tested":
        show_data = tests
    else:    
        show_data = data[indias_option]
    st.write(go.Figure(data=go.Scatter(x=show_data.index, y=show_data.values, mode='lines+markers')))

    if st.checkbox("Show Raw Data", False):
        st.subheader(header)
        st.write(show_data)

    st.subheader("Cases at a glance")
    yesterday = date.today() - timedelta(days=1)
    map_option = st.selectbox("Select an Option:", ['Confirmed', "Recovered", "Deceased"])
    map_data = give_data(states_data, yesterday, map_option)
    customization = {'title': ' cases in India', 'tools': [('State', '@st_nm')], 'status': "C"}
    map_obj = give_map_object(map_data, map_option, customization)
    st.bokeh_chart(map_obj, use_container_width=True)

    date_month_year = [(d.day, d.month, d.year) for d in states_data.index.levels[0]]
    d, m, y = date_month_year[0]

    slide_value = st.slider("Select date:", min_value = 0, max_value = len(date_month_year), value = date_month_year.index((d, m, y)), format = "")
    d, m, y = date_month_year[slide_value]
    d = date(y, m, d)

    st.subheader(f"Active Cases across India as on: {d:%d} {d:%B} {d:%Y}")
    st.write(px.bar(x=active_states.columns, y=active_states.cumsum().loc[d, :].values))

    st.subheader(f"Top 10 Infected states on: {d:%d} {d:%B} {d:%Y}")
    top10 = states_data.loc[(d, slice(None)), :].droplevel(level=0).T.sort_values(by="Confirmed", ascending=False).iloc[:10, :]

    st.write(px.bar(top10, barmode='group'))

    # st.subheader("Compare different state's Active data:")
    # multi_state = st.multiselect("Select States", active_states.columns.to_list(), default=['Maharashtra', 'Telangana', 'Andhra Pradesh', 'Kerala'])
    # show_data = active_states.loc[:, multi_state].cumsum()
    # st.write(go.Figure(data=go.Scatter(x=show_data.index, y=show_data.values, mode='lines+markers')))