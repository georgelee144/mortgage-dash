import json
import os
import warnings
import requests
import pandas as pd
from typing import Any, Dict


class FRED_data:
    def __init__(self, API_key: str):
        self.API_key = API_key

        self.info_url = "https://api.stlouisfed.org/fred/series"
        self.data_url = "https://api.stlouisfed.org/fred/series/observations"

    FRED_data_constants = {
        "average_30_year": "MORTGAGE30US",
        "S&P CoreLogic Case-Shiller U.S. National Home Price Index": "CSUSHPISA",
    }

    def make_FRED_parameters(
        self,
        series_id: str,
        realtime_start: str = "1776-07-04",
        realtime_end: str = "9999-12-31",
    ):
        return {
            "order_by": "observation_date",
            "sort_order": "asc",
            "file_type": "json",
            "series_id": series_id,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "api_key": self.API_key,
        }

    def __raise_on_bad_response(self, response: requests.Response) -> None:
        if response.status_code != 200:
            warnings.warn(f"Response was not 200 for {response.url}")
            response.raise_for_status()
        else:
            return

    def request_get_data(self, url: str, parameters: Dict[str, str]):
        response = requests.get(url, params=parameters)
        self.__raise_on_bad_response(response)

        return response

    def get_FRED_data_info(self, series_key_or_series_id: str):
        series_id = self.FRED_data_constants.get(
            series_key_or_series_id, series_key_or_series_id
        )

        parameters = self.make_FRED_parameters(
            series_id=series_id,
        )

        response = self.request_get_data(url=self.info_url, parameters=parameters)

        return response.text

    def __load_and_clean_df(self, json_response: Any, series_id: str):
        df_raw = pd.DataFrame(json_response["observations"])
        self.last_raw_df = {series_id: df_raw}

        df_raw["Value"] = pd.to_numeric(df_raw["value"], errors="coerce")
        df_raw.dropna(subset=["Value"], inplace=True)

        df_raw["Date"] = pd.to_datetime(
            df_raw["date"], format="%Y-%m-%d", errors="coerce"
        )
        df_raw.dropna(subset=["Date"], inplace=True)

        return df_raw[["Date", "Value"]]

    def get_FRED_data_observations(
        self,
        series_key_or_series_id: str,
        realtime_start: str = "1776-07-04",
        realtime_end: str = "9999-12-31",
    ):
        series_id = self.FRED_data_constants.get(
            series_key_or_series_id, series_key_or_series_id
        )

        parameters = self.make_FRED_parameters(
            series_id=series_id,
            realtime_start=realtime_start,
            realtime_end=realtime_end,
        )

        response = self.request_get_data(url=self.data_url, parameters=parameters)
        json_response = json.loads(response.text)

        return self.__load_and_clean_df(
            json_response=json_response, series_id=series_id
        )

    def get_most_recent_interest_rate(self) -> str:
        df_interest_rates = self.get_FRED_data_observations(
            series_key_or_series_id="average_30_year"
        )

        return df_interest_rates["Value"].values[-1]


if __name__ == "__main__":
    api_key = os.getenv("FRED_API", "")
    data_service = FRED_data(API_key=api_key)

    print(
        data_service.get_FRED_data_info(
            series_key_or_series_id="average_30_year",
        )
    )

    print(
        data_service.get_FRED_data_observations(
            series_key_or_series_id="average_30_year", realtime_start="1971-04-02"
        )
    )

    print(data_service.get_most_recent_interest_rate())
