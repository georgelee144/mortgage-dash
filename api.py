import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import FRED_data_service
import property_math

app = Flask(__name__)
CORS(app,resources = {r"/api/*":{"origins":"http://localhost:3000"}})

try:
    fred_data_service = FRED_data_service.FRED_data(API_key=os.getenv("FRED_API", ""))
except Exception as e:
    print(f"Could not initialize FRED service:{e}")
    fred_data_service = None
    

