from ..config.schemas import InterestRateModel, Sex, verifyDataSetValidity, Config
from ..config.config import config
from ..mortality.preprocess import build_mortality_table
import numpy as np
from math import exp


class Annuitant():
    def __init__(self, age: int, first_payment_year: int, present_balance: float, sex: Sex = Sex.TOTAL) -> None:
        self.age = age
        self.sex = sex
        self.first_payment_year = first_payment_year
        self.present_balance = present_balance
        self.mortality_trend: Annuitant.MortalityTrend = None
        self.annuity_factor_adj: int = 0


class Mortality:
    def __init__(self) -> None:
        self.qx_dict = build_mortality_table(config)


class Discount:
    def __init__(self) -> None:
        self.discount_factor_series: dict[int, float] = {}

        def calculateSvenssonInterestRate(svensson: dict, t_delta: int) -> float:
            t_delta = t_delta+1

            if (t_delta > 30):
                t_delta = 30

            svensson_parameters = svensson["parameters"]

            b0,b1,b2,b3,t1,t2 = (
                svensson_parameters["b0"],
                svensson_parameters["b1"],
                svensson_parameters["b2"],
                svensson_parameters["b3"],
                svensson_parameters["t1"],
                svensson_parameters["t2"],
            )

            m1 = (1-exp(-t_delta/t1)) / (t_delta/t1)
            m2 = (1-exp(-t_delta/t2)) / (t_delta/t2)

            rate =  b0 + (b1+b2)*m1 - b2 * exp(-t_delta/t1) + b3*(m2-exp(-t_delta/t2))

            # Convert to coefficient, e.g. if rate=2.5%, then return 1.025
            return 1 + (rate/100)

        # For fixed interest rate
        if config.DISCOUNT_MODEL in (InterestRateModel.FIXED, InterestRateModel.ZERO):
            if config.DISCOUNT_MODEL == InterestRateModel.FIXED:
                if (config.DISCOUNT_CONFIG[InterestRateModel.FIXED]["fixed_rate"] == None):
                    raise Exception("Fixed interest rate must be set in order to determine the discount factor")
                fixed_rate = config.DISCOUNT_CONFIG[InterestRateModel.FIXED]["fixed_rate"]
            if config.DISCOUNT_MODEL == InterestRateModel.ZERO:
                fixed_rate = 0

            discount_factor = 1
            for t_delta in range(0, config.TERMINAL_AGE-30+1):
                self.discount_factor_series[t_delta] = 1/discount_factor
                discount_factor = discount_factor * (1 + fixed_rate)

        # For svensson interest rate
        if config.DISCOUNT_MODEL == InterestRateModel.SVENSSON:
            discount_factor = 1
            for t_delta in range(0, config.TERMINAL_AGE-30+1):
                self.discount_factor_series[t_delta] = 1/discount_factor
                discount_factor = discount_factor * calculateSvenssonInterestRate(config.DISCOUNT_CONFIG[InterestRateModel.SVENSSON], t_delta)


class Valuation():
    def __init__(self, annuitant: Annuitant, mortality: Mortality, discount: Discount) -> None:
        self.annuitant = annuitant
        self.mortality = mortality
        self.discount = discount

    def calculateAnnuityFactor(self) -> tuple[float, float]:
        # Survival function modeling
        initial_delta = self.annuitant.first_payment_year - config.PURCHASE_YEAR
        last_delta = config.TERMINAL_AGE - self.annuitant.age
        max_lookup_age = config.MAX_INITIAL_AGE - 1  # 99
        survival_function = {0: np.float64(1)}

        for t_delta in range(0, last_delta + 1):
            current_age = min(self.annuitant.age + t_delta, max_lookup_age)
            qx = self.mortality.qx_dict[self.annuitant.sex][current_age][t_delta]
            survival_function[t_delta + 1] = survival_function[t_delta] * (1 - qx)

        macaulay_duration_numerator = 0
        annuity_factor_PV = 0

        # First leg of the annuity (annuity year 1-7)
        for t_delta in range(1, 8):
            annuity_factor_PV += self.discount.discount_factor_series[t_delta]
            macaulay_duration_numerator += self.discount.discount_factor_series[t_delta] * t_delta

        # Second leg of the annuity (annuity year 7+)
        for t_delta in range(8, last_delta + 1):
            annuity_factor_PV += survival_function[t_delta] * self.discount.discount_factor_series[t_delta]
            macaulay_duration_numerator += survival_function[t_delta] * self.discount.discount_factor_series[t_delta] * t_delta

        # Calculate modified duration for the annuity
        mod_duration = macaulay_duration_numerator / annuity_factor_PV

        annuity_factor_adj = survival_function[initial_delta] * annuity_factor_PV
        return annuity_factor_adj, mod_duration
