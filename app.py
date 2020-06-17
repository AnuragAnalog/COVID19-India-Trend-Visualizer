#!/usr/bin/python3

import requests
import pandas as pd
import streamlit as st
import plotly_express as px

from datetime import date, timedelta
from plotly import graph_objects as go

# Custom modules
from maps_utils import give_data, give_india_map

# Constants
MAPPER1 = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07'}
MAPPER2 = {'an': "Andaman and Nicobar Islands", 'ap': "Andhra Pradesh", 'ar': "Arunachal Pradesh", 'as': "Assam", 'br': "Bihar", 'ch': "Chandigarh", 'ct': "Chhattisgarh", 'dd': "Dadra and Nagar Haveli and Daman and Diu", 'dl': "Delhi", 'dn': "Dadra and Nagar Haveli", 'ga': "Goa", 'gj': "Gujarat",
       'hp': "Himachal Pradesh", 'hr': "Haryana", 'jh': "Jharkhand", 'jk': "Jammu and Kashmir", 'ka': "Karnataka", 'kl': "Kerala", 'la': "Ladakh", 'ld': "Lakshadweep", 'mh': "Maharashtra", 'ml': "Meghalaya", 'mn': "Manipur", 'mp': "Madhya Pradesh",
       'mz': "Mizoram", 'nl': "Nagaland", 'or': "Odisha", 'pb': "Punjab", 'py': "Puducherry", 'rj': "Rajasthan", 'sk': "Sikkim", 'tg': "Telangana", 'tn': "Tamil Nadu", 'tr': "Tripura", 'tt': "tt", 'un': "un",
       'up': "Uttar Pradesh", 'ut': "Uttarakhand", 'wb': "West Bengal", 'date': 'date', "status": "status"}

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
    tests['updatetimestamp'] = pd.to_datetime(tests['updatetimestamp'], format='%d/%m/%Y %H:%M:%S')
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

    return data, tests, states_data, active_states, districts_data

data, tests, states_data, active_states, districts_data = initialize_data()

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
    indias_option = st.selectbox("Select the measure:", data.columns.to_list()+['Total Tested'], index=6)
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
    map_obj = give_india_map(map_data, map_option)
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