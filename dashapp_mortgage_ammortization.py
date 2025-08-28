import os
from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
from plotly import graph_objects as go

import FRED_data_service
import property_math

app = Dash()
fred_data_service = FRED_data_service.FRED_data(API_key=os.getenv("FRED_API", ""))

app.layout = html.Div(
    children=[
        dcc.Input(id="loan_amount", type="number", placeholder="loan_amount", min=1),
        dcc.Input(
            id="property_value", type="number", placeholder="property_value", min=1
        ),
        dcc.Input(
            id="annual_rate_percentage",
            type="number",
            placeholder="interest_rate",
            value=float(fred_data_service.get_most_recent_interest_rate()),
        ),
        dcc.Input(
            id="term_in_months",
            type="number",
            value=360,
            min=1
        ),
        html.Div(
            children=[
                dcc.Dropdown(
                    ["Bar Graph", "Line Graph"], "Bar Graph", id="graph_selector"
                )
            ],
            id="graph_selector_div",
        ),
        html.Div(
            children=[],
            id="graph_div",
            title="Mortgage ammortization graph",
        ),
        html.Div(
            [
                html.Button("Download Ammortization Table", id="btn_txt"),
                dcc.Download(id="download-text-index"),
            ]
        ),
        html.Div(
            children=[dash_table.DataTable(id="ammortization_table")],
            id="table_div",
            title="Mortgage ammortization_table",
        ),
    ]
)


@callback(
    Output(component_id="graph_div", component_property="children"),
    Input(component_id="loan_amount", component_property="value"),
    Input(component_id="annual_rate_percentage", component_property="value"),
    Input(component_id="term_in_months", component_property="value"),
    Input(component_id="property_value", component_property="value"),
    Input(component_id="graph_selector", component_property="value"),
)
def update_ammortization_figure(
    loan_amount: float,
    annual_rate_percentage: float,
    term_in_months: int,
    property_value: float,
    graph_selector: str,
):
    if (
        loan_amount is None
        or annual_rate_percentage is None
        or term_in_months is None
        or property_value is None
    ):
        raise PreventUpdate

    mortgage = property_math.Mortgage(
        annual_rate_percentage=annual_rate_percentage,
        number_of_periods_for_loan_term=term_in_months,
        loan_amount=loan_amount,
        property_value=property_value,
    )
    df = mortgage.get_mortgage_ammortization()

    if graph_selector == "Bar Graph":
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Debt",
                    x=df["period"],
                    y=df["ending_principal"] * -1,
                ),
                go.Bar(name="Equity", x=df["period"], y=df["equity"], base=0),
            ]
        )
        fig.update_layout(barmode="stack")

    elif graph_selector == "Line Graph":
        fig = go.Figure(
            data=[
                go.Scatter(name="Debt", x=df["period"], y=df["ending_principal"]),
                go.Scatter(name="Equity", x=df["period"], y=df["equity"]),
            ]
        )

    fig.update_layout(
        title_text="Mortgage Ammortization and Equity assuming contsant property value over time."
    )
    fig.update_layout(hovermode="x")

    return dcc.Graph(id="ammortization_graph", figure=fig)


@callback(
    Output(component_id="ammortization_table", component_property="data"),
    Output(component_id="ammortization_table", component_property="page_size"),
    Input(component_id="loan_amount", component_property="value"),
    Input(component_id="annual_rate_percentage", component_property="value"),
    Input(component_id="term_in_months", component_property="value"),
    Input(component_id="property_value", component_property="value"),
)
def update_ammortization_table(
    loan_amount: float,
    annual_rate_percentage: float,
    term_in_months: int,
    property_value: float,
):
    if (
        loan_amount is None
        or annual_rate_percentage is None
        or term_in_months is None
        or property_value is None
    ):
        raise PreventUpdate

    mortgage = property_math.Mortgage(
        annual_rate_percentage=annual_rate_percentage,
        number_of_periods_for_loan_term=term_in_months,
        loan_amount=loan_amount,
        property_value=property_value,
    )
    df = mortgage.get_mortgage_ammortization()

    return df.to_dict("records"), len(df)


if __name__ == "__main__":
    app.run(debug=False)
