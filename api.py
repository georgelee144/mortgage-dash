import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
print(f"--- API KEY LOADED: '{os.getenv('FRED_API')}' ---")

import FRED_data_service
import property_math

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

try:
    fred_data_service = FRED_data_service.FRED_data(API_key=os.getenv("FRED_API", ""))
except Exception as e:
    print(f"Could not initialize FRED service:{e}")
    fred_data_service = None


@app.route("/api/current-rate", methods=["GET"])
def get_current_rate():
    if not fred_data_service:
        return jsonify({"error": "FRED service not available"}), 500
    try:
        rate = fred_data_service.get_most_recent_interest_rate()
        return jsonify({"rate": float(rate)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/amortization", methods=["POST"])
def get_amortization_schedule():
    data = request.get_json()

    # Basic validation
    required_keys = ["loanAmount", "propertyValue", "annualRate", "termInMonths"]
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        mortgage = property_math.Mortgage(
            annual_rate_percentage=float(data["annualRate"]),
            number_of_periods_for_loan_term=int(data["termInMonths"]),
            loan_amount=float(data["loanAmount"]),
            property_value=float(data["propertyValue"]),
        )
        df = mortgage.get_mortgage_ammortization()
        # Convert DataFrame to a list of dictionaries for JSON compatibility
        return jsonify(df.to_dict("records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/monte-carlo", methods=["POST"])
def get_monte_carlo_simulation():
    data = request.get_json()

    # Define and check for the keys this endpoint actually needs
    required_keys = ["propertyValue", "termInMonths", "priceIndexKey"]
    if not all(key in data for key in required_keys):
        return jsonify(
            {"error": "Missing required fields for Monte Carlo simulation"}
        ), 400

    try:
        # Get historical price data from FRED
        df_sample_data = fred_data_service.get_FRED_data_observations(
            series_key_or_series_id=data["priceIndexKey"]
        )
        df_sample_data["returns"] = df_sample_data["last_value_per_month"].pct_change()
        sample_data = df_sample_data["returns"].dropna()  # Drop NaN values

        # Run the simulation using data from the request
        monte_carlo_simulator = property_math.MonteCarloPropertyValue(
            starting_property_value=float(data["propertyValue"]),
            sample_data=sample_data,
            length_of_each_run=int(data["termInMonths"]),
            number_of_runs=100,  # Keep runs low for faster API response
        )

        df_sim = monte_carlo_simulator.generate_sample_data()

        # Process the results for a clean JSON response
        df_sim_T = df_sim.drop(columns="period").transpose()
        results = {
            "periods": df_sim["period"].tolist(),
            "median": df_sim_T.median().tolist(),
            "quantile_25": df_sim_T.quantile(0.25).tolist(),
            "quantile_75": df_sim_T.quantile(0.75).tolist(),
            # Optionally, include a few raw runs for visualization
            "runs": df_sim.iloc[:, 1:6].to_dict("list"),  # First 5 runs
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/mortgage-options", methods=["POST"])
def get_mortgage_options():
    data = request.get_json()
    required_keys = ["loanAmount", "annualRate", "termInMonths"]
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        loan_amount = float(data["loanAmount"])
        annual_rate_percentage = float(data["annualRate"])
        term_in_months = int(data["termInMonths"])

        term_in_months_to_display = [15 * 12, 30 * 12]
        if term_in_months not in term_in_months_to_display:
            term_in_months_to_display.append(term_in_months)
            term_in_months_to_display.sort()

        rates = []
        start_rate = annual_rate_percentage - 1.0
        for i in range(9):
            rates.append((start_rate + (i * 25)))

        table_data = []
        for term in term_in_months_to_display:
            row = {"term": term}
            for rate in rates:
                mortgage = property_math.Mortgage(
                    annual_rate_percentage=rate,
                    number_of_periods_for_loan_term=term,
                    loan_amount=loan_amount,
                    property_value=0,
                )
                row[f"{rate:.3f}"] = float(mortgage.mortgage_payment)
            table_data.append(row)

        response_data = {
            "columns": [f"{rate:.3f}" for rate in rates],
            "data": table_data,
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
