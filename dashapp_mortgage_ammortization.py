from typing import Dict
import os
from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
from plotly import graph_objects as go
import pandas as pd

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
        dcc.Input(id="term_in_months", type="number", value=360, min=1),
        html.Div(
            children=[dash_table.DataTable(id="estimated_mortgage_payment_grid")],
            id="estimated_mortgage_payment_grid_div",
            title="Mortgage payment Grid",
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
    Output(component_id="estimated_mortgage_payment_grid", component_property="data"),
    Output(
        component_id="estimated_mortgage_payment_grid", component_property="active_cell"
    ),
    Input(component_id="loan_amount", component_property="value"),
    Input(component_id="annual_rate_percentage", component_property="value"),
    Input(component_id="term_in_months", component_property="value"),
)
def update_mortgage_option_range_figure(
    loan_amount: float,
    annual_rate_percentage: float,
    term_in_months: int,
):
    if loan_amount is None or annual_rate_percentage is None or term_in_months is None:
        raise PreventUpdate

    term_in_months_to_display = [15 * 12, 30 * 12]
    if term_in_months != term_in_months_to_display[-1]:
        term_in_months_to_display.append(term_in_months)

    dfs = []

    for term in term_in_months_to_display:
        mortgage_objects: Dict[str, property_math.Mortgage] = {}

        for rate in range(
            int(annual_rate_percentage * 1000) - 1000,
            int(annual_rate_percentage * 1000) + 1250,
            250,
        ):
            rate = rate / 1000
            mortgage_objects[f"{rate}%"] = property_math.Mortgage(
                annual_rate_percentage=rate,
                number_of_periods_for_loan_term=term,
                loan_amount=loan_amount,
                property_value=0,
            )

        df = pd.DataFrame(
            {
                rate: [mortgage.mortgage_payment]
                for rate, mortgage in mortgage_objects.items()
            }
        )
        df["term"] = term
        dfs.append(df)

    df_all = pd.concat(dfs, axis=0)
    columns_of_df_all = df_all.columns
    df_all = df_all[[columns_of_df_all[-1]] + columns_of_df_all[:-1].to_list()]

    active_cell = {
        "row": len(df_all) - 1,
        "column": 5,
        "column_id": f"{annual_rate_percentage}%",
    }

    return df_all.to_dict("records"), active_cell


@callback(
    Output(component_id="graph_div", component_property="children"),
    Input(component_id="loan_amount", component_property="value"),
    Input(component_id="term_in_months", component_property="value"),
    Input(component_id="property_value", component_property="value"),
    Input(
        component_id="estimated_mortgage_payment_grid", component_property="active_cell"
    ),
    Input(component_id="graph_selector", component_property="value"),
)
def update_ammortization_figure(
    loan_amount: float,
    term_in_months: int,
    property_value: float,
    active_cell_selected: Dict[str, str],
    graph_selector: str,
):
    if active_cell_selected is None or property_value is None:
        raise PreventUpdate

    annual_rate_percentage = float(active_cell_selected["column_id"][:-1])
    row_selected = active_cell_selected["row"]

    if row_selected == 0:
        term_in_months_to_use = 12 * 15
    elif row_selected == 1:
        term_in_months_to_use = 12 * 30
    else:
        term_in_months_to_use = term_in_months

    mortgage = property_math.Mortgage(
        annual_rate_percentage=annual_rate_percentage,
        number_of_periods_for_loan_term=term_in_months_to_use,
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
        title_text="Mortgage Ammortization and Equity assuming contsant property value over time.",
        hovermode="x",
        xaxis_title="Periods",
        yaxis_title="Dollars",
    )

    return dcc.Graph(id="ammortization_graph", figure=fig)


@callback(
    Output(component_id="ammortization_table", component_property="data"),
    Output(component_id="ammortization_table", component_property="page_size"),
    Input(component_id="loan_amount", component_property="value"),
    Input(component_id="term_in_months", component_property="value"),
    Input(component_id="property_value", component_property="value"),
    Input(
        component_id="estimated_mortgage_payment_grid", component_property="active_cell"
    ),
)
def update_ammortization_table(
    loan_amount: float,
    term_in_months: int,
    property_value: float,
    active_cell_selected: Dict[str, str],
):
    if active_cell_selected is None or property_value is None:
        raise PreventUpdate

    annual_rate_percentage = float(active_cell_selected["column_id"][:-1])
    row_selected = active_cell_selected["row"]

    if row_selected == 0:
        term_in_months_to_use = 12 * 15
    elif row_selected == 1:
        term_in_months_to_use = 12 * 30
    else:
        term_in_months_to_use = term_in_months

    mortgage = property_math.Mortgage(
        annual_rate_percentage=annual_rate_percentage,
        number_of_periods_for_loan_term=term_in_months_to_use,
        loan_amount=loan_amount,
        property_value=property_value,
    )

    df = mortgage.get_mortgage_ammortization()

    return df.to_dict("records"), len(df)


if __name__ == "__main__":
    app.run(debug=False)
