import numpy as np
import pandas as pd
from decimal import Decimal, getcontext
from typing import List, Dict
from numpy.typing import ArrayLike


def calculate_mortgage_payment(
    effective_interest_rate_per_compounding_period: float,
    number_of_periods_for_loan_term: int,
    loan_amount: float,
) -> Decimal:
    present_value_interest_factor = (
        1
        - (1 + effective_interest_rate_per_compounding_period)
        ** (-1 * number_of_periods_for_loan_term)
    ) / effective_interest_rate_per_compounding_period

    payment = loan_amount / present_value_interest_factor

    return convert_to_2_place_decimal(Decimal(payment))


def convert_to_2_place_decimal(some_decimal: Decimal) -> Decimal:
    return some_decimal.quantize(Decimal("1.00"))


def generate_mortgage_amortization_table(
    annual_rate_percentage: float,
    number_of_periods_per_compounding_term: int,
    loan_amount: float,
    mortgage_payment: float | Decimal,
    property_value: float | Decimal,
) -> pd.DataFrame:
    getcontext().prec = int(Decimal(loan_amount).log10().quantize(Decimal("1"))) + 2

    property_value = Decimal(property_value)
    mortgage_payment = Decimal(mortgage_payment)

    beginning_principal: List[Decimal] = [Decimal(loan_amount)]
    ending_principal: List[Decimal] = []
    interest_to_pay: List[Decimal] = []
    principal_payment: List[Decimal] = []
    equity: List[Decimal] = []

    effective_interest_rate = Decimal(
        annual_rate_percentage / number_of_periods_per_compounding_term
    )

    while True:
        interest_to_pay.append(
            convert_to_2_place_decimal(
                beginning_principal[-1] * effective_interest_rate
            )
        )
        principal_payment.append(mortgage_payment - interest_to_pay[-1])
        ending_principal.append(beginning_principal[-1] - principal_payment[-1])
        equity.append(property_value - ending_principal[-1])
        beginning_principal.append(ending_principal[-1])

        if beginning_principal[-1] <= 0:
            break

    data = {
        "beginning_principal": beginning_principal[:-1],
        "interest_to_pay": interest_to_pay,
        "principal_payment": principal_payment,
        "ending_principal": ending_principal,
        "equity": equity,
    }

    df = pd.DataFrame(data=data).reset_index(names=["period"])
    df["period"] = df["period"] + 1
    df["percent of payment to principal"] = df["principal_payment"].div(
        mortgage_payment
    )
    df["percent of payment to interest"] = df["interest_to_pay"].div(mortgage_payment)
    df["percent of property still debt"] = df["ending_principal"].div(property_value)
    df["percent of property owned"] = df["equity"].div(property_value)

    return df


class Mortgage:
    def __init__(
        self,
        annual_rate_percentage: float,
        number_of_periods_for_loan_term: int,
        loan_amount: float,
        property_value: float,
        number_of_periods_per_compounding_term: int = 12,
    ) -> None:
        self.annual_rate_percentage = annual_rate_percentage / 100
        self.number_of_periods_for_loan_term = number_of_periods_for_loan_term
        self.number_of_periods_per_compounding_term = (
            number_of_periods_per_compounding_term
        )

        self.loan_amount = loan_amount
        self.property_value = property_value

        self.effective_interest_rate_per_compounding_period = (
            self.annual_rate_percentage / self.number_of_periods_per_compounding_term
        )

        self.mortgage_payment = calculate_mortgage_payment(
            effective_interest_rate_per_compounding_period=self.effective_interest_rate_per_compounding_period,
            number_of_periods_for_loan_term=self.number_of_periods_for_loan_term,
            loan_amount=self.loan_amount,
        )

    def get_mortgage_ammortization(self) -> pd.DataFrame:
        if hasattr(Mortgage, "mortgage_ammortization_df"):
            return self.mortgage_ammortization_df

        else:
            self.mortgage_ammortization_df = generate_mortgage_amortization_table(
                annual_rate_percentage=self.annual_rate_percentage,
                number_of_periods_per_compounding_term=self.number_of_periods_per_compounding_term,
                loan_amount=self.loan_amount,
                mortgage_payment=self.mortgage_payment,
                property_value=self.property_value,
            )
        return self.mortgage_ammortization_df


class MonteCarloPropertyValue:
    def __init__(
        self,
        starting_property_value: float,
        sample_data: ArrayLike,
        assumed_constant_annual_growth_rate: float = 0.02,
        seed: int | None = None,
        length_of_each_run: int = 360,
        number_of_runs: int = 1000,
    ) -> None:
        self.starting_property_value = starting_property_value
        self.sample_data = self.__clean_sample_data(sample_data)
        self.assumed_constant_annual_growth_rate = assumed_constant_annual_growth_rate
        self.length_of_each_run = length_of_each_run
        self.number_of_runs = number_of_runs

        self.random_number_generator = np.random.default_rng(seed=seed)

    def __clean_sample_data(self, sample_data: ArrayLike) -> np.ndarray:
        np_sample_data = np.array(sample_data)

        return np_sample_data[~np.isnan(np_sample_data)]

    def generate_sample_data(self):
        sampled_runs = self.random_number_generator.choice(
            a=self.sample_data,
            size=(self.number_of_runs, self.length_of_each_run),
            replace=True,
        )
        sampled_runs = np.add(sampled_runs, 1)
        self.sampled_runs = np.insert(
            arr=sampled_runs, obj=0, values=self.starting_property_value, axis=1
        )
        self.compounded_sample_runs = np.cumprod(a=self.sampled_runs, axis=1)

        self.df = pd.DataFrame(self.compounded_sample_runs.T).reset_index(
            names=["period"]
        )
        return self.df

    def summary_results(self):
        if not hasattr(self, "df"):
            self.generate_sample_data()

        if hasattr(self, "df_stats"):
            return self.df_stats

        df_last_row = self.df.iloc[-1, 1:]

        stats: Dict[str, float | np.floating] = {}

        price_with_assumed_constant_growth_rate = (
            self.starting_property_value
            * (1 + self.assumed_constant_annual_growth_rate / 12)
            ** self.length_of_each_run
        )
        average_ending_price = np.average(df_last_row)

        stats["Starting Price"] = self.starting_property_value
        stats["Median End Price"] = np.median(df_last_row)
        stats["Average End Price"] = average_ending_price

        stats["Precent greater than starting price"] = (
            len(df_last_row[df_last_row > self.starting_property_value].index)
            / self.number_of_runs
        )

        stats["Starting Price adjusted for constant growth rate"] = (
            price_with_assumed_constant_growth_rate
        )
        stats[
            "Precent greater than starting Price adjusted for constant growth rate"
        ] = (
            len(
                df_last_row[df_last_row > price_with_assumed_constant_growth_rate].index
            )
            / self.number_of_runs
        )
        stats["Precent greater than average ending price"] = (
            len(df_last_row[df_last_row > average_ending_price].index)
            / self.number_of_runs
        )

        stats["Lowest Value"] = np.min(df_last_row)
        stats["25th percentile"] = np.percentile(
            a=df_last_row, q=25, method="inverted_cdf"
        )
        stats["75th percentile"] = np.percentile(
            a=df_last_row, q=75, method="inverted_cdf"
        )
        stats["25th percentile"] = np.percentile(
            a=df_last_row, q=25, method="inverted_cdf"
        )
        stats["Greatest Value"] = np.max(df_last_row)

        keys = stats.keys()
        values = [value for _, value in stats.items()]

        self.df_stats = pd.DataFrame({"desc": keys, "value": values})

        self.df_stats["total return based on starting value"] = (
            self.df_stats["value"] / self.starting_property_value - 1
        )
        columns_to_nan_out = [
            "Precent greater than starting price",
            "Precent greater than inflation adjusted price",
            "Precent greater than average ending price",
        ]
        self.df_stats["total return based on starting value"] = self.df_stats[
            "total return based on starting value"
        ].where(
            cond=~self.df_stats["desc"].isin(values=columns_to_nan_out), other=pd.NA
        )
        self.df_stats["annual return based on starting value"] = (
            1 + self.df_stats["total return based on starting value"]
        ) ** (12 / self.length_of_each_run) - 1

        return self.df_stats

    def __make_cdf_x_y(self, data: ArrayLike):
        data = np.array(data).flatten()
        data = data[~np.isnan(data)]

        if len(data) == 0:
            return np.array([]), np.array([])

        sorted_data = np.sort(data)
        n = len(sorted_data)

        x = sorted_data
        y = np.arange(1, n + 1) / n

        return x, y

    def get_returns_cdf(self):
        return self.__make_cdf_x_y(data=self.sample_data)

    def get_ending_prices_cdf(self):
        if not hasattr(self, "df"):
            self.generate_sample_data()

        df_last_row = self.df.iloc[-1, 1:]

        return self.__make_cdf_x_y(data=df_last_row)

    def selective_runs_to_plot(self, max_number_runs=100):
        # max_number_runs - 5
        return


if __name__ == "__main__":
    sample_data = [
        -0.0145947623533657,
        -0.0113103227090207,
        0.0318107984029976,
        -0.0343037397382817,
        0.0271133103740771,
        0.00208139532832055,
        0.0225405523322911,
        -0.0219424563781536,
        0.0278678323827663,
        0.00766370045322564,
        0.0389115233128896,
        -0.0235901283775854,
        -0.0119905869413267,
        -0.0113248684831721,
        0.0378917429095959,
        0.025694358639641,
        0.0203434572727179,
        -0.0168559529551218,
        0.00659463907900184,
        -0.000792515737371247,
        0.00431814923681187,
        -0.0295247717825818,
        0.0418719380224818,
        0.0095977488602952,
        -0.00340356991513227,
        0.017913684547113,
        0.0353109944386975,
        -0.0131289773212877,
        0.00755111580389394,
        -0.0121039761797737,
        -0.0409160289578425,
        -0.0058876873667133,
        -0.0432866014539221,
        0.000925579065476312,
        -0.00857158318451708,
        -0.0266961156853273,
        -0.0492090609353048,
        -0.0359233288289329,
        0.00856409833048991,
        -0.027704762902834,
        -0.0223014193458127,
        0.0146576339772107,
        -0.0172506622424537,
        0.0363798092826716,
        -0.0189895632476021,
        0.0259647379752098,
        -0.0296252894292684,
        0.0338526371972552,
        -0.0148630377977418,
        -0.0273730670891388,
        -0.033766151005787,
    ]
    monte_carlo = MonteCarloPropertyValue(
        starting_property_value=500000, sample_data=sample_data, seed=81007
    )
    monte_carlo.generate_sample_data()
    print(monte_carlo.sampled_runs)

    print(monte_carlo.compounded_sample_runs)
