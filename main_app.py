import os

print(f"--- Is the FRED API Key loaded? -> '{os.getenv('FRED_API')}' ---")

from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd
import FRED_data_service
import property_math


external_css = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_css)
server = app.server  # for deployment use

fred_data_service = FRED_data_service.FRED_data(API_key=os.getenv("FRED_API", ""))

app.layout = html.Div(
    [
        html.H1("Home Buyer's Financial Dashboard", style={"textAlign": "center"}),
        html.Div(
            [
                html.H4("Common Inputs"),
                dcc.Input(
                    id="property_value",
                    type="number",
                    placeholder="Property Value",
                    min=1,
                    style={"marginRight": "10px"},
                ),
                dcc.Input(
                    id="loan_amount",
                    type="number",
                    placeholder="Loan Amount",
                    min=1,
                    style={"marginRight": "10px"},
                ),
                dcc.Input(
                    id="annual_rate_percentage",
                    type="number",
                    placeholder="Interest Rate (%)",
                    value=float(fred_data_service.get_most_recent_interest_rate()),
                    style={"marginRight": "10px"},
                ),
                dcc.Input(
                    id="term_in_months",
                    type="number",
                    value=360,
                    min=1,
                    style={"marginRight": "10px"},
                ),
            ],
            style={
                "marginBottom": "20px",
                "padding": "10px",
                "border": "1px solid #ddd",
                "borderRadius": "5px",
            },
        ),
        dcc.Tabs(
            id="tabs-main",
            value="tab-mortage",
            children=[
                dcc.Tab(
                    label="Mortgage Amoritization Calculator",
                    value="tab-mortgage",
                    children=[
                            
                    ],
                )
            ],
        ),
    ]
)
