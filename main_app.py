import os
from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd
import FRED_data_service
import property_math


external_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_css)
server = app.server #for deployment use

fred_data_service = FRED_data_service.FRED_data(API_key=os.getenv("FRED_API",""))