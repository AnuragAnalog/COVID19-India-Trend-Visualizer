#!/usr/bin/python3

import requests
import pandas as pd

MAPPER = {'an': "Andaman and Nicobar Islands", 'ap': "Andhra Pradesh", 'ar': "Arunachal Pradesh", 'as': "Assam", 'br': "Bihar", 'ch': "Chandigarh", 'ct': "Chhattisgarh", 'dd': "Dadra and Nagar Haveli and Daman and Diu", 'dl': "Delhi", 'dn': "Dadra and Nagar Haveli", 'ga': "Goa", 'gj': "Gujarat",
       'hp': "Himachal Pradesh", 'hr': "Haryana", 'jh': "Jharkhand", 'jk': "Jammu and Kashmir", 'ka': "Karnataka", 'kl': "Kerala", 'la': "Ladakh", 'ld': "Lakshadweep", 'mh': "Maharashtra", 'ml': "Meghalaya", 'mn': "Manipur", 'mp': "Madhya Pradesh",
       'mz': "Mizoram", 'nl': "Nagaland", 'or': "Odisha", 'pb': "Punjab", 'py': "Puducherry", 'rj': "Rajasthan", 'sk': "Sikkim", 'tg': "Telangana", 'tn': "Tamil Nadu", 'tr': "Tripura", 'tt': "tt", 'un': "un",
       'up': "Uttar Pradesh", 'ut': "Uttarakhand", 'wb': "West Bengal", 'date': 'date', "status": "status"}

def get_data():
    URL = 'https://api.covid19india.org/states_daily.json'

    raw_data = requests.get(URL)
    jsonobj = raw_data.json()
    cases = jsonobj['states_daily']

    states_data = pd.DataFrame(cases)
    states_data.columns = states_data.columns.map(MAPPER)

    return states_data

if __name__ == '__main__':
    data = get_data()
    data.to_csv('states_data.csv', index=False)