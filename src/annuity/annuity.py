from ..config.schemas import Sex
from ..config.config import config
import numpy as np
from numpy import ndarray
from math import pow


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

    def calculateAnnuityFactor(self) -> tuple[float, float, float]:

        # Survival function modeling 
        modified_duration_numerator = 0
        present_yield_numerator = 0
        annuity_factor_PV = 0   


        age_span_months = config.AGE_END_MONTHS - self.annuitant.initial_month_age 


        for delta_months in range(age_span_months):
            t_idx = -1 / ((delta_months + 0.00000001) / 12)

            # Calculate the premium for survivor coverage
            unconditional_qx = self.survival_factors[delta_months] - self.survival_factors[min(delta_months+1,age_span_months-1)]
            AF_contribution = config.SURVIVOR_COVERAGE*unconditional_qx* self.discount_factors[delta_months]

            
            if config.GUARANTEE_84_MONTHS and delta_months < 84:
                AF_contribution += self.discount_factors[delta_months] 
            else:
                AF_contribution += self.survival_factors[delta_months] * self.discount_factors[delta_months]

            # Adjust for increasing annuities
            AF_contribution *= pow(config.YEARLY_INCREASE_COEFFICIENT, delta_months / 12)

            modified_duration_numerator += AF_contribution * (delta_months / 12)
            present_yield_numerator += AF_contribution * (pow(self.discount_factors[delta_months], t_idx) - 1)
            annuity_factor_PV += AF_contribution



        # Calculate the annualized effective yield that a portfolio is making at this instant 
        portfolio_effective_yield = present_yield_numerator / annuity_factor_PV

        # Calculate modified duration for the annuity 
        modified_duration = modified_duration_numerator / annuity_factor_PV
        
        # Adjust for insurer variable fee
        annuity_factor_PV = annuity_factor_PV / (1-config.VARIABLE_FEE)

        return annuity_factor_PV, modified_duration, portfolio_effective_yield
