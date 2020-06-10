#!/usr/bin/python3

import requests
import pandas as pd

MAPPER = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07'}

def get_data():
    URL = 'https://api.covid19india.org/data.json'

    def convert(date): 
        date_splits = date.split() 
        converted = "-".join([date_splits[0], MAPPER[date_splits[1]], '2020']) 
        return converted

    raw_data = requests.get(URL)
    jsonobj = raw_data.json()
    cases = jsonobj['cases_time_series']

    india_data = pd.DataFrame(cases)
    india_data['date'] = india_data['date'].apply(convert)

    return india_data

if __name__ == '__main__':
    data = get_data()
    data.to_csv('india_data.csv', index=False)