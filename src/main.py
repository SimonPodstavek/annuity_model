import pandas as pd
from typing import Dict
from pathlib import Path
import numpy as np
from math import factorial, log
from itertools import combinations
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


from .config.schemas import Sex, MortalityTable, PricingModel
from .config.config import config
from .data_io.excel import read_xlsx
from .mortality.mortality import build_mortality_table, build_survival_factors
from .discount.discount import build_discount_factors
from .annuity.annuity import Annuitant, Valuation
from .shapley.shapley import FEATURES, set_config
from .helpers.convertor import generateRegionalGenderSpecificMortalityTables

# TODO
# Add increasing annuity amount to shapley 


# Configure model parameters in config/config.py
def shapley_values() -> dict:
    N = len(FEATURES)
    phi = {}

    set_config(frozenset())

    BENCHMARK_OFFER = calculateOffer()
    count = 0
    for feature in FEATURES:
        others = [f for f in FEATURES if f != feature]
        phi[feature] = 0
        for r in range(len(others) + 1):
            for s in combinations(others, r):
                S_set = frozenset(s)
                weight = factorial(len(s)) * factorial(N - len(s) -1) / factorial(N)
                set_config(S_set)
                subset_featureless_Offer: float = calculateOffer()
                set_config(S_set | {feature})
                subset_Offer:float = calculateOffer()
                phi[feature] += weight*(subset_Offer - subset_featureless_Offer)
                count += 1
        phi[feature] /= BENCHMARK_OFFER

    for factor in phi.values():
        print(factor)


def main():
    calculateOffer()

def fee_function(x,b,c):
    return x*b+c

def calculateOffer() -> float | None:
    
    mortality_table: MortalityTable = build_mortality_table()
    discount_factors: np.ndarray = build_discount_factors()


    if config.PRICING_MODEL == PricingModel.FEES:
        annuity_df = pd.read_csv('data/offers/105_AF_by_age_and_NS_quintiles.csv')
        for index, row in annuity_df.iterrows():
            # Annuity configurations
            annuitant = Annuitant(age_years = int(row["age"]), age_months=6, first_payment_year=2025, present_balance=10000, sex=config.SEX)
        
            survival_factors: np.ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)
            valuation = Valuation(annuitant, survival_factors , discount_factors)
            annuity_factor_PV, modified_duration,portfolio_effective_yield = valuation.calculateAnnuityFactor()
            fair_offer = annuitant.present_balance / annuity_factor_PV

            annuity_df.loc[index, 'MWR'] = annuity_factor_PV /  row['AF']

        # Captures 96.7% of offers in 2025
        subset = annuity_df[annuity_df['age'].between(59,66)] 
        subset['fee'] = subset['NS']*(1-subset['MWR'])

        coefficients, covariance = curve_fit(fee_function, subset['NS'], subset['fee'])

        fee_actual = subset['fee']
        fee_pred = fee_function(subset['NS'], *coefficients)

        # R² by hanq
        ss_res = np.sum((fee_actual - fee_pred) ** 2)          # residual sum of squares
        ss_tot = np.sum((fee_actual - fee_actual.mean()) ** 2) # total sum of squares
        r_squared = 1 - (ss_res / ss_tot)

        plt.scatter(subset['NS'], subset['fee'])
        plt.show()

    if config.PRICING_MODEL == PricingModel.SHAPLEY:
        annuitant = Annuitant(age_years = 63, age_months = 6, first_payment_year=2025, present_balance=10000, sex=config.SEX)
        survival_factors: np.ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)

        valuation = Valuation(annuitant, survival_factors , discount_factors)
        annuity_factor_PV, modified_duration, portfolio_effective_yield = valuation.calculateAnnuityFactor()

        fair_offer = annuitant.present_balance / annuity_factor_PV
        return fair_offer


    if config.PRICING_MODEL == PricingModel.VALUE:
        # Annuity configuration
        for age in range(63,90):   
            annuitant = Annuitant(age_years = 63, age_months = 6, first_payment_year=2025, present_balance=147369.52, sex=config.SEX)
            survival_factors: np.ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)

            valuation = Valuation(annuitant, survival_factors , discount_factors)
            annuity_factor_PV, modified_duration, portfolio_effective_yield = valuation.calculateAnnuityFactor()

            fair_offer = annuitant.present_balance / annuity_factor_PV
            print(f"{portfolio_effective_yield}")




if __name__ == "__main__":
    # generateRegionalGenderSpecificMortalityTables()
    # main()  
    shapley_values()