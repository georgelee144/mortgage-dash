import pandas as pd
from decimal import Decimal, getcontext
from typing import List


def calculate_mortgage_payment(
    effective_interest_rate_per_compounding_period: float,
    number_of_periods_for_loan_term: int,
    loan_amount: float,
):
    present_value_interest_factor = (
        1
        - (1 + effective_interest_rate_per_compounding_period)
        ** (-1 * number_of_periods_for_loan_term)
    ) / effective_interest_rate_per_compounding_period

    payment = loan_amount / present_value_interest_factor

    return round(payment, 2)


def convert_to_2_place_decimal(some_decimal: Decimal):
    return some_decimal.quantize(Decimal("1.00"))


def generate_mortgage_amortization_table(
    annual_rate_percentage: float,
    number_of_periods_per_compounding_term: int,
    loan_amount: float,
    mortgage_payment: float,
    property_value: float,
):
    getcontext().prec = int(Decimal(loan_amount).log10().quantize(Decimal("1"))) + 2

    property_value = Decimal(str(property_value))
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
        interest_to_pay.append(beginning_principal[-1] * effective_interest_rate)
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

    return df


class Mortgage:
    def __init__(
        self,
        annual_rate_percentage: float,
        number_of_periods_for_loan_term: int,
        number_of_periods_per_compounding_term: int,
        loan_amount: float,
        property_value: float,
    ) -> None:
        self.annual_rate_percentage = annual_rate_percentage
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
            effective_interest_rate_per_compounding_period=self.annual_rate_percentage,
            number_of_periods_for_loan_term=self.number_of_periods_for_loan_term,
            number_of_periods_per_compounding_term=self.number_of_periods_per_compounding_term,
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
