import requests
from typing import Dict


class FRED_data:
    def __init__(self, API_key: str = "cecc63627eeb58ce8bacf525aba01e99"):
        self.API_key = API_key

        self.base_url = "https://api.stlouisfed.org/fred/series"

    FRED_data_constants = {"average_30_year": "MORTGAGE30US"}

    def make_FRED_parameters(
        self, series_id: str, realtime_start: str, realtime_end: str
    ):
        return {
            "series_id": series_id,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
        }

    def request_FRED_data(self, parameters: Dict[str, str]):
        response = requests.get(self.base_url, params=parameters)

        return response

    def get_FRED_date(self, series_id: str, realtime_start: str, realtime_end: str):
        parameters = self.make_FRED_parameters(
            series_id=series_id,
            realtime_start=realtime_start,
            realtime_end=realtime_end,
        )

        self.request_FRED_data(parameters)

        return
