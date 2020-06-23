#!/usr/bin/python3

import json
import numpy as np
import pandas as pd
import streamlit as st
import geopandas as gpd

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.palettes import brewer
from bokeh.models import GeoJSONDataSource, LinearColorMapper, HoverTool, ColorBar

# Constants
HUE_MAPPER = {'Confirmed': 'Reds', 'Recovered': 'Greens', 'Deceased': 'Greys'}

# Loading states data
def give_data(states_data, date, status):
    map_data = states_data.loc[(slice(None), status), :].droplevel(level=1).cumsum().loc[date]
    map_data = pd.DataFrame({"st_nm": map_data.index, status: map_data.values})

    sf_india = gpd.read_file(r'./geodata/india-polygon.shp')
    sf_india.st_nm.iloc[7] = "Dadra and Nagar Haveli Daman and Diu"
    merged = pd.merge(sf_india, map_data, on = 'st_nm', how = 'inner')

    return merged

def give_india_map(merged_data, status):
    # Conversion the entire data into string
    merged_json = json.loads(merged_data.to_json())
    json_data = json.dumps(merged_json)
    geosource = GeoJSONDataSource(geojson = json_data)

    # Define a multi-hue color scheme.
    scheme = HUE_MAPPER[status]
    palette = brewer[scheme][9]
    palette = palette[::-1]

    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette = palette, low = merged_data[status].min(), high = merged_data[status].max(), nan_color = '#d9d9d9')
    hover = HoverTool(tooltips = [('States','@st_nm'),(status,'@'+status)])
    
    # Create color bar. 
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20, border_line_color=None,location = (0,0), orientation = 'horizontal')
    
    # Create figure object.
    map_obj = figure(title = status+' cases in India', plot_height = 800 , plot_width = 750, tools = [hover])

    map_obj.title.text_font_size = '20pt'
    map_obj.xaxis.visible = False
    map_obj.yaxis.visible = False
    map_obj.xgrid.grid_line_color = None
    map_obj.ygrid.grid_line_color = None

    map_obj.patches('xs','ys', source = geosource, fill_color = {'field' :status, 'transform' : color_mapper}, line_color = 'black', line_width = 0.25, fill_alpha = 1)
    map_obj.add_layout(color_bar, 'below')

    return map_obj

if __name__ == "__main__":
    states = pd.read_csv("states_data.csv", parse_dates=['date'], index_col=['date', 'status'])
    merged = give_data(states, "2020-06-14", "Confirmed")
    map_obj = give_india_map(merged, "Confirmed")
    st.bokeh_chart(map_obj, use_container_width=True)