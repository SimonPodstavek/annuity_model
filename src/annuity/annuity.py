from ..config.schemas import Sex
from ..config.config import config
import numpy as np
from numpy import ndarray
from math import ceil


class Annuitant:
    def __init__(self, age_months, age_years, first_payment_year, present_balance, sex: Sex = Sex.TOTAL):
        self.age_months: int = age_months
        self.age_years: int = age_years
        self.initial_month_age = age_years*12 + age_months
        self.first_payment_year: int = first_payment_year
        self.present_balance = present_balance 
        self.sex: Sex = sex
        self.annuity_factor_adj: int = 0 
        

class Valuation:
    def __init__(self, annuitant: Annuitant, survival_factors: ndarray, discount_factors: ndarray):
        self.annuitant = annuitant
        self.survival_factors = survival_factors
        self.discount_factors = discount_factors

    def calculateAnnuityFactor(self) -> int:
        # Survival function modeling 
        macaulay_duration_numerator = 0
        annuity_factor_PV = 0   

        age_span_months = config.AGE_END_MONTHS - self.annuitant.initial_month_age 
        # year_range = range(config.BASE_YEAR,(config.BASE_YEAR) + ceil((age_span_months)/12)+1)



        if config.GUARANTEE_84_MONTHS:
            for delta_months in range(84):
                AF = self.discount_factors[delta_months]
                macaulay_duration_numerator += AF * (delta_months/12)
                annuity_factor_PV += AF
            for delta_months in range(84,age_span_months):
                AF = self.survival_factors[delta_months] * self.discount_factors[delta_months]
                macaulay_duration_numerator += AF * (delta_months/12)
                annuity_factor_PV += AF
        else:
            for delta_months in range(age_span_months):
                AF = self.survival_factors[delta_months] * self.discount_factors[delta_months]
                macaulay_duration_numerator += AF * (delta_months/12)
                annuity_factor_PV += AF

        # Calculate modified duration for the annuity 
        maccaulay_duration = macaulay_duration_numerator/annuity_factor_PV
        modified_duration = maccaulay_duration / (1+ self.discount_factors[ceil(maccaulay_duration)*12]/12)

        return annuity_factor_PV, modified_duration
