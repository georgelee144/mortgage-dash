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

    FRED_mortgages = {
        "average_30_year": "MORTGAGE30US",
        "average_15_year": "MORTGAGE15US",
    }

    FRED_home_indicies = {
        "S&P CoreLogic Case-Shiller U.S. National Home Price Index (Seasonal Adjusted)": "CSUSHPISA",
        "S&P CoreLogic Case-Shiller U.S. National Home Price Index": "CSUSHPINSA",
        "S&P CoreLogic Case-Shiller 20-City Composite Home Price Index": "SPCS20RSA",
        "Purchase Only House Price Index for the United States": "HPIPONM226S",
        "S&P CoreLogic Case-Shiller CA-San Francisco Home Price Index": "SFXRSA",
        "S&P CoreLogic Case-Shiller CA-Los Angeles Home Price Index": "LXXRSA",
        "S&P CoreLogic Case-Shiller NY-New York Home Price Index": "NYXRSA",
        "S&P CoreLogic Case-Shiller IL-Chicago Home Price Index": "CHXRSA",
        "S&P CoreLogic Case-Shiller WA-Seattle Home Price Index": "SEXRSA",
        "S&P CoreLogic Case-Shiller FL-Miami Home Price Index": "MIXRSA",
        "Condo Price Index for New York, New York": "NYXRCSA",
        "S&P CoreLogic Case-Shiller CA-San Diego Home Price Index": "SDXRSA",
        "Research Consumer Price Index: Housing": "CPIEHOUSE",
        "S&P CoreLogic Case-Shiller CO-Denver Home Price Index": "DNXRSA",
        "S&P CoreLogic Case-Shiller TX-Dallas Home Price Index": "DAXRSA",
        "S&P CoreLogic Case-Shiller MA-Boston Home Price Index": "BOXRSA",
        "S&P CoreLogic Case-Shiller AZ-Phoenix Home Price Index": "PHXRSA",
        "S&P CoreLogic Case-Shiller NV-Las Vegas Home Price Index": "LVXRSA",
        "S&P CoreLogic Case-Shiller 10-City Composite Home Price Index": "SPCS10RSA",
        "S&P CoreLogic Case-Shiller FL-Tampa Home Price Index": "TPXRSA",
        "S&P CoreLogic Case-Shiller GA-Atlanta Home Price Index": "ATXRSA",
        "S&P CoreLogic Case-Shiller OR-Portland Home Price Index": "POXRSA",
        "S&P CoreLogic Case-Shiller DC-Washington Home Price Index": "WDXRSA",
        "Condo Price Index for Chicago, Illinois": "CHXRCSA",
        "Condo Price Index for San Francisco, California": "SFXRCSA",
        "S&P CoreLogic Case-Shiller MN-Minneapolis Home Price Index": "MNXRSA",
        "S&P CoreLogic Case-Shiller NC-Charlotte Home Price Index": "CRXRSA",
        "S&P CoreLogic Case-Shiller MI-Detroit Home Price Index": "DEXRSA",
        "S&P CoreLogic Case-Shiller OH-Cleveland Home Price Index": "CEXRSA",
        "Home Price Index (High Tier) for Chicago, Illinois": "CHXRHTSA",
        "Condo Price Index for Los Angeles, California": "LXXRCSA",
        "Condo Price Index for Boston, Massachusetts": "BOXRCSA",
        "Home Price Index (Middle Tier) for Phoenix, Arizona": "PHXRMTSA",
        "Home Price Index (High Tier) for Seattle, Washington": "SEXRHTSA",
        "Home Price Index (High Tier) for San Francisco, California": "SFXRHTSA",
        "Home Price Index (High Tier) for Washington D.C.": "WDXRHTSA",
        "Home Price Index (High Tier) for New York, New York": "NYXRHTSA",
        "Home Price Index (High Tier) for Denver, Colorado": "DNXRHTSA",
        "Home Price Index (High Tier) for Boston, Massachusetts": "BOXRHTSA",
        "Home Price Index (High Tier) for San Diego, California": "SDXRHTSA",
        "Home Price Index (High Tier) for Miami, Florida": "MIXRHTSA",
        "Home Price Index (High Tier) for Los Angeles, California": "LXXRHTSA",
        "Purchase Only House Price Index for the New England Census Division": "PONHPI00101M226S",
        "Home Price Index (High Tier) for Las Vegas, Nevada": "LVXRHTSA",
        "Home Price Index (High Tier) for Tampa, Florida": "TPXRHTSA",
        "Home Price Index (Low Tier) for San Francisco, California": "SFXRLTSA",
        "Home Price Index (Middle Tier) for San Diego, California": "SDXRMTSA",
        "Home Price Index (High Tier) for Minneapolis, Minnesota": "MNXRHTSA",
        "Home Price Index (High Tier) for Atlanta, Georgia": "ATXRHTSA",
        "Home Price Index (High Tier) for Portland, Oregon": "POXRHTSA",
        "Purchase Only House Price Index for the Pacific Census Division": "PONHPI00109M226S",
        "Purchase Only House Price Index for the Middle Atlantic Census Division": "PONHPI00102M226S",
        "Home Price Index (Middle Tier) for Atlanta, Georgia": "ATXRMTSA",
        "Home Price Index (Middle Tier) for Chicago, Illinois": "CHXRMTSA",
        "Home Price Index (Low Tier) for New York, New York": "NYXRLTSA",
        "Home Price Index (Low Tier) for Seattle, Washington": "SEXRLTSA",
        "Home Price Index (High Tier) for Phoenix, Arizona": "PHXRHTSA",
        "Purchase Only House Price Index for the West North Central Census Division": "PONHPI00107M226S",
        "Home Price Index (Middle Tier) for Los Angeles, California": "LXXRMTSA",
        "Home Price Index (Low Tier) for Tampa, Florida": "TPXRLTSA",
        "Home Price Index (Middle Tier) for San Francisco, California": "SFXRMTSA",
        "Home Price Index (Low Tier) for Chicago, Illinois": "CHXRLTSA",
        "Home Price Index (Middle Tier) for Miami, Florida": "MIXRMTSA",
        "Home Price Index (Middle Tier) for Seattle, Washington": "SEXRMTSA",
        "Home Price Index (Middle Tier) for Minneapolis, Minnesota": "MNXRMTSA",
        "Home Price Index (Middle Tier) for Tampa, Florida": "TPXRMTSA",
        "Home Price Index (Low Tier) for Los Angeles, California": "LXXRLTSA",
        "Home Price Index (Low Tier) for Miami, Florida": "MIXRLTSA",
        "Home Price Index (Middle Tier) for Denver, Colorado": "DNXRMTSA",
        "Purchase Only House Price Index for the East South Central Census Division": "PONHPI00104M226S",
        "Home Price Index (Middle Tier) for New York, New York": "NYXRMTSA",
        "Purchase Only House Price Index for the West South Central Census Division": "PONHPI00105M226S",
        "Home Price Index (Middle Tier) for Las Vegas, Nevada": "LVXRMTSA",
        "Home Price Index (Low Tier) for Minneapolis, Minnesota": "MNXRLTSA",
        "Home Price Index (Middle Tier) for Portland, Oregon": "POXRMTSA",
        "Home Price Index (Low Tier) for Boston, Massachusetts": "BOXRLTSA",
        "Home Price Index (Low Tier) for San Diego, California": "SDXRLTSA",
        "Purchase Only House Price Index for the Mountain Census Division": "PONHPI00108M226S",
        "Purchase Only House Price Index for the East North Central Census Division": "PONHPI00106M226S",
        "Purchase Only House Price Index for the South Atlantic Census Division": "PONHPI00103M226S",
        "Home Price Index (Middle Tier) for Boston, Massachusetts": "BOXRMTSA",
        "Home Price Index (Low Tier) for Portland, Oregon": "POXRLTSA",
        "Home Price Index (Low Tier) for Atlanta, Georgia": "ATXRLTSA",
        "Home Price Index (Low Tier) for Denver, Colorado": "DNXRLTSA",
        "Home Price Index (Low Tier) for Phoenix, Arizona": "PHXRLTSA",
        "Home Price Index (Low Tier) for Washington D.C.": "WDXRLTSA",
        "Home Price Index (Middle Tier) for Washington D.C.": "WDXRMTSA",
        "Home Price Index (Low Tier) for Las Vegas, Nevada": "LVXRLTSA",
    }

    FRED_data_constants = FRED_mortgages | FRED_home_indicies

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
            # "frequency": "m",
            # "aggregation_method": "eop",
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

        aggregated_df = df_raw.groupby("Date").agg(
            last_value_per_month=pd.NamedAgg(column="Value", aggfunc="last")
        )
        aggregated_df["returns"] = aggregated_df["last_value_per_month"].pct_change()

        self.last_cleaned_df = {series_id: aggregated_df}

        return aggregated_df

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

        return df_interest_rates["last_value_per_month"].values[-1]


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
