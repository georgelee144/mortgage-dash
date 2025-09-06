import os
from typing import Any, Dict, Tuple
from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import FRED_data_service
import property_math

app = Dash()
fred_data_service = FRED_data_service.FRED_data(API_key=os.getenv("FRED_API", ""))

app.layout = html.Div(
    children=[
        dcc.Input(
            id="property_value", type="number", placeholder="property_value", min=1
        ),
        dcc.Input(
            id="term_in_months",
            type="number",
            value=360,
            min=1,
        ),
        html.Div(
            children=[
                dcc.Dropdown(
                    options=list(fred_data_service.FRED_home_indicies.keys()),
                    value=None,
                    id="property_price_index",
                )
            ],
            id="data_selector",
        ),
        html.Div(
            children=[],
            id="graph_div",
            title="Property values graph",
        ),
        html.Div(
            [
                html.Button("Download Ammortization Table", id="btn_txt"),
                dcc.Download(id="download-text-index"),
            ]
        ),
        html.Div(
            children=[dash_table.DataTable(id="simulated_property_value_table")],
            id="table_div",
            title="Property value table",
        ),
    ]
)


@callback(
    Output(component_id="graph_div", component_property="children"),
    Input(component_id="term_in_months", component_property="value"),
    Input(component_id="property_value", component_property="value"),
    Input(component_id="property_price_index", component_property="value"),
)
def update_property_value(
    term_in_months: int,
    property_value: float,
    property_price_index: str,
) -> dcc.Graph:
    if term_in_months is None or property_value is None or property_price_index is None:
        raise PreventUpdate

    df_sample_data = fred_data_service.get_FRED_data_observations(
        series_key_or_series_id=property_price_index
    )

    sample_data = df_sample_data["returns"]
    monte_carlo_property_value_simulator = property_math.MonteCarloPropertyValue(
        starting_property_value=property_value, sample_data=sample_data
    )

    df = monte_carlo_property_value_simulator.generate_sample_data()

    fig = go.Figure(
        data=[
            go.Scatter(name=f"Run_{column}", x=df["period"], y=df[column])
            for column in df.columns[1:]
        ]
    )

    fig.update_layout(
        title_text=f"Simulated Property Value based on the past performance of {property_price_index}"
    )
    fig.update_layout(hovermode="x")

    return dcc.Graph(id="ammortization_graph", figure=fig)


@callback(
    Output(component_id="simulated_property_value_table", component_property="data"),
    Output(
        component_id="simulated_property_value_table", component_property="page_size"
    ),
    Input(component_id="term_in_months", component_property="value"),
    Input(component_id="property_value", component_property="value"),
    Input(component_id="property_price_index", component_property="value"),
)
def update_summary_table(
    term_in_months: int,
    property_value: float,
    property_price_index: str,
) -> Tuple[Dict[Any, Any], int]:
    if term_in_months is None or property_value is None or property_price_index is None:
        raise PreventUpdate

    df_sample_data = fred_data_service.get_FRED_data_observations(
        series_key_or_series_id=property_price_index
    )

    sample_data = df_sample_data["returns"]
    monte_carlo_property_value_simulator = property_math.MonteCarloPropertyValue(
        starting_property_value=property_value, sample_data=sample_data
    )

    df = monte_carlo_property_value_simulator.summary_results()

    return df.to_dict("records"), len(df)


if __name__ == "__main__":
    app.run(debug=False)
