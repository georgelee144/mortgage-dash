import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
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
    """Endpoint to calculate the mortgage amortization schedule."""
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
