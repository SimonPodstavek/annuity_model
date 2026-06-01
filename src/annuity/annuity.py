from ..config.schemas import InterestRateModel, Sex
from ..config.config import config
import numpy as np
from math import exp, pow


class Annuitant():
    def __init__(self, age, first_payment_year, present_balance, sex: Sex = Sex.TOTAL):
        self.age_months: int = age_months
        self.sex = sex
        self.first_payment_year = first_payment_year
        self.present_balance = present_balance 
        self.mortality_trend: Annuitant.MortalityTrend = None
        self.annuity_factor_adj: int = 0 
        

class Valuation():
    def __init__(self, annuitant: Annuitant, mortality:Mortality, discount: Discount):
        self.annuitant = annuitant
        self.mortality = mortality
        self.discount = discount

    def calculateAnnuityFactor(self) -> int:
        # Survival function modeling
        initial_delta = self.annuitant.first_payment_year - config.PURCHASE_YEAR
        last_delta = config.TERMINAL_AGE - self.annuitant.age
        survival_function = {0:np.float64(1)}

        for t_delta in range(0, last_delta+1):
            age = self.annuitant.age
            used_delta = t_delta if t_delta < config.TERMINAL_AGE - self.annuitant.age else config.TERMINAL_AGE - self.annuitant.age - 1
            qx = self.mortality.qx_dict[self.annuitant.sex][age+used_delta][t_delta]
            survival_function[t_delta+1] = survival_function[t_delta] * (1-qx)

        macaulay_duration_numerator = 0
        annuity_factor_PV = 0   

        # First leg of the annuity (annuity year 1-7), with guaranteed payout for Slovak annuities
        for t_delta in range(initial_delta, initial_delta+7): 
            annuity_factor_PV += self.discount.discount_factor_series[t_delta] 
            macaulay_duration_numerator += self.discount.discount_factor_series[t_delta] * t_delta

        # Second leg of the annuity (annuity year 7+)
        for t_delta in range(initial_delta+7, last_delta+1): 
            annuity_factor_PV += survival_function[t_delta] * self.discount.discount_factor_series[t_delta] 
            macaulay_duration_numerator += survival_function[t_delta] * self.discount.discount_factor_series[t_delta] * t_delta

        # Calculate modified duration for the annuity 
        mod_duration = macaulay_duration_numerator/annuity_factor_PV

        annuity_factor_adj = survival_function[initial_delta] * annuity_factor_PV
        return annuity_factor_adj, mod_duration
