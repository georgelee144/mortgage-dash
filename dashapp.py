from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
import mortgage_math
import plotly.graph_objects as go

app = Dash()
app.layout = html.Div(
    children=[
        dcc.Input(id="loan_amount", type="number", placeholder="loan_amount", min=1),
        dcc.Input(
            id="interest_rate",
            type="number",
            placeholder="interest_rate",
        ),
        dcc.Input(
            id="term_in_years", type="number", placeholder="term_in_years", min=0
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
                html.Button("Download Text", id="btn_txt"),
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
    Input(component_id="interest_rate", component_property="value"),
    Input(component_id="term_in_years", component_property="value"),
    Input(component_id="graph_selector", component_property="value"),
)
def update_ammortization_figure(
    loan_amount: float, interest_rate: float, term_in_years: int, graph_selector: str
):
    if (
        loan_amount is None
        or loan_amount <= 0
        or interest_rate is None
        or interest_rate <= 0
        or term_in_years is None
        or term_in_years <= 0
    ):
        raise PreventUpdate

    annual_rate_percentage = interest_rate / 100

    mortgage_payment = mortgage_math.calculate_mortgage_payment(
        effective_interest_rate_per_compounding_period=annual_rate_percentage,
        number_of_periods_for_loan_term=term_in_years,
        number_of_periods_per_compounding_term=12,
        loan_amount=loan_amount,
    )
    df = mortgage_math.generate_mortgage_amortization_table(
        annual_rate_percentage=annual_rate_percentage,
        number_of_periods_per_compounding_term=12,
        loan_amount=loan_amount,
        mortgage_payment=mortgage_payment,
        property_value=loan_amount,
    )

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

    fig.update_layout(hovermode="x")
    return dcc.Graph(id="ammortization_graph", figure=fig)


@callback(
    Output(component_id="ammortization_table", component_property="data"),
    Output(component_id="ammortization_table", component_property="page_size"),
    Input(component_id="loan_amount", component_property="value"),
    Input(component_id="interest_rate", component_property="value"),
    Input(component_id="term_in_years", component_property="value"),
)
def update_ammortization_table(
    loan_amount: float, interest_rate: float, term_in_years: int
):
    if (
        loan_amount is None
        or loan_amount <= 0
        or interest_rate is None
        or interest_rate <= 0
        or term_in_years is None
        or term_in_years <= 0
    ):
        raise PreventUpdate

    annual_rate_percentage = interest_rate / 100

    mortgage_payment = mortgage_math.calculate_mortgage_payment(
        effective_interest_rate_per_compounding_period=annual_rate_percentage,
        number_of_periods_for_loan_term=term_in_years,
        number_of_periods_per_compounding_term=12,
        loan_amount=loan_amount,
    )
    df = mortgage_math.generate_mortgage_amortization_table(
        annual_rate_percentage=annual_rate_percentage,
        number_of_periods_per_compounding_term=12,
        loan_amount=loan_amount,
        mortgage_payment=mortgage_payment,
        property_value=loan_amount,
    )

    return df.to_dict("records"), len(df)


if __name__ == "__main__":
    app.run(debug=False)
