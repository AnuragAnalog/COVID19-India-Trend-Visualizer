#!/usr/bin/python3

import requests
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import plotly_express as px

from datetime import date

st.header("Covid-19 Trend Visualizer in India")

# Preprocessing India data
def preprocess_india_data(data):
    data.index = pd.to_datetime(data.index, format='%d-%m-%Y')
    data['totalactive'] = (data['totalconfirmed'] - (data['totaldeceased'] + data['totalrecovered']))
    data['dailyactive'] = (data['dailyconfirmed'] - (data['dailydeceased'] + data['dailyrecovered']))

    columns = list(data.columns)
    for i, _ in enumerate(columns):
        for word in ['total', 'daily', 'confirmed', 'recovered', 'deceased', 'active']:
            columns[i] = (columns[i].replace(word, word.capitalize()+" "))
    data.columns = columns

    return data

# Preprocessing States data
def preprocess_states_data(states_data):
    states_data.drop(['tt', 'un'], axis=1, inplace=True)

    return states_data

# Get active states record
def get_active_states(states_data):
    confirmed = states_data.loc[(slice(None), "Confirmed"), :].droplevel(level=1)
    recovered = states_data.loc[(slice(None), "Recovered"), :].droplevel(level=1)
    deceased = states_data.loc[(slice(None), "Deceased"), :].droplevel(level=1)

    active = confirmed - (recovered + deceased)

    return active

@st.cache(allow_output_mutation=True)
def initialize_data():
    data = pd.read_csv('india_data.csv', index_col=['date'])
    states_data = pd.read_csv('states_data.csv', parse_dates=['date'], index_col=['date', 'status'])
    # districts_data = requests.get("https://api.covid19india.org/districts_daily.json")
    # districts_data = districts_data.json()['districtsDaily']
    districts_data = 0
    latlong = pd.read_csv('latlong.csv', index_col=['state'])

    # Applying preprocessing steps
    data = preprocess_india_data(data)
    states_data = preprocess_states_data(states_data)
    active_states = get_active_states(states_data)

    return data, states_data, active_states, districts_data, latlong

data, states_data, active_states, districts_data, latlong = initialize_data()

if st.sidebar.checkbox("Wanna see states data?", False):
    header = "Since 14th March"
    states_option1 = st.sidebar.selectbox("State", states_data.columns)
    states_option2 = st.sidebar.selectbox("State Type", ['Confirmed', 'Deceased', 'Recovered', 'Active'])

    st.subheader(states_option2+" Cases in "+states_option1)
    if states_option2 == "Active":
        st.line_chart(active_states.loc[:, states_option1].cumsum())
    else:
        st.line_chart(states_data.loc[(slice(None), states_option2), states_option1].droplevel(level=1).cumsum())

    # if st.sidebar.checkbox("See at district level?", False):
        # select_district1 = st.sidebar.selectbox("District", list(districts_data[states_option1].keys()))
        # select_district2 = st.sidebar.selectbox("District Type", ['Confirmed', 'Deceased', 'Recovered', 'Active'])
        # district_level = pd.DataFrame(districts_data[states_option1][select_district1]).set_index(['date'])
        # district_level.drop(['notes'], axis=1, inplace=True)
# 
        # st.subheader(select_district2+" Cases in "+select_district1)
        # st.line_chart(district_level[select_district2.lower()])
else:
    header = "Since 30th January"
    indias_option = st.selectbox("Select the measure:", data.columns, index=6)
    st.subheader(indias_option+" Cases in India.")
    st.write(px.scatter(data[indias_option]))

    if st.checkbox("Show Raw Data", False):
        st.subheader(header)
        st.write(data)

    date_month_year = [(d.day, d.month, d.year) for d in states_data.index.levels[0]]
    d, m, y = date_month_year[0]

    st.subheader("Select date:")
    slide_value = st.slider("", min_value = 0, max_value = len(date_month_year), value = date_month_year.index((d, m, y)), format = "")
    d, m, y = date_month_year[slide_value]
    d = date(y, m, d)

    st.subheader(f"Active Cases across India as on: {d:%d}-{d:%m}-{d:%Y}")
    st.write(px.bar(x=active_states.columns, y=active_states.cumsum().loc[d, :].values))

    st.subheader(f"Top 10 Infected states on: {d:%d}-{d:%m}-{d:%Y}")
    top10 = states_data.loc[(d, slice(None)), :].droplevel(level=0).T.sort_values(by="Confirmed", ascending=False).iloc[:10, :]

    st.write(px.bar(top10, barmode='group'))