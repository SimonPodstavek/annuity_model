from pandas import DataFrame
from typing import Dict
from pathlib import Path
from numpy import ndarray
from math import factorial
from itertools import combinations

from .config.schemas import Sex, MortalityTable, PricingModel
from .config.config import config
from .data_io.excel import read_xlsx
from .mortality.mortality import build_mortality_table, build_survival_factors
from .discount.discount import build_discount_factors
from .annuity.annuity import Annuitant, Valuation
from .shapley.shapley import config, FEATURES, set_config
# from .helpers.convertor import generateRegionalGenderSpecificMortalityTables

# Configure model parameters in config/config.py

def shapley_values() -> dict:
    N = len(FEATURES)
    phi = {}

    set_config(frozenset())

    BENCHMARK_OFFER = calculateOffer()

    for feature in FEATURES:
        others = [f for f in FEATURES if f != feature]
        phi[feature] = 0
        for r in range(len(others) + 1):
            for s in combinations(others, r):
                S_set = frozenset(s)
                weight = factorial(len(s)) * factorial(N - len(s) -1) / factorial(N)
                set_config(S_set)
                subset_featureless_Offer = calculateOffer()
                set_config(S_set | {feature})
                subset_Offer = calculateOffer()
                phi[feature] += weight*(subset_Offer - subset_featureless_Offer) 
        phi[feature] /= BENCHMARK_OFFER

    return phi


def main():
    calculateOffer()

def calculateOffer() -> float:
    
    mortality_table: MortalityTable = build_mortality_table()
    discount_factors: ndarray = build_discount_factors()

    if config.PRICING_MODEL == PricingModel.MWR:
    
        aggregates_path = Path("data/agregaty.xlsx")
        df = read_xlsx(aggregates_path, "data2")
        df = df[df["year"] == 2025]

        for index, row in df.iterrows():
            # Annuity configuration
            annuitant = Annuitant(age_years = int(row["age"]), age_months=6, first_payment_year=2025, present_balance=row["mean_balance"], sex=config.SEX)
        
            survival_factors: ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)
            valuation = Valuation(annuitant, survival_factors , discount_factors)
            annuity_factor_PV, modified_duration,portfolio_effective_yield = valuation.calculateAnnuityFactor()
            fair_offer = annuitant.present_balance / annuity_factor_PV

            print(f"Age: {row["age"]} Balance: {row["mean_balance"]}  MWR: {row["mean_offer"]/fair_offer}")
            return fair_offer

    if config.PRICING_MODEL == PricingModel.VALUE:
        # Annuity configuration
            annuitant = Annuitant(age_years = 65, age_months = 6, first_payment_year=2025, present_balance=50000, sex=config.SEX)
        
            survival_factors: ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)
            valuation = Valuation(annuitant, survival_factors , discount_factors)
            annuity_factor_PV, modified_duration, portfolio_effective_yield = valuation.calculateAnnuityFactor()

            fair_offer = annuitant.present_balance / annuity_factor_PV
            print(f"{fair_offer}")
            return fair_offer
    else:
         return -1

if __name__ == "__main__":
    shapley_values()
    # main()
