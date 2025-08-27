import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import FRED_data_service
import property_math
