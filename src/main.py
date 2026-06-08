from pandas import DataFrame
from .config.schemas import Sex, MortalityTable, PricingModel
from .config.config import config
from .data_io.excel import read_xlsx
from typing import Dict
from pathlib import Path
from numpy import ndarray
from .mortality.mortality import build_mortality_table, build_survival_factors
from .discount.discount import build_discount_factors
from .annuity.annuity import Annuitant, Valuation

# Configure model parameters in config/config.py


def main() -> None:
    
    mortality_table: MortalityTable = build_mortality_table()
    discount_factors: ndarray = build_discount_factors()

    if config.PRICING_MODEL == PricingModel.MWR:
        pass
        aggregates_path = Path("data/agregaty.xlsx")
        df = read_xlsx(aggregates_path, "data2")
        df = df[df["year"] == 2025]

        for index, row in df.iterrows():
            # Annuity configuration
            annuitant = Annuitant(age_years = int(row["age"]), age_months=6, first_payment_year=2025, present_balance=row["mean_balance"], sex=Sex.TOTAL)
        
            survival_factors: ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)
            valuation = Valuation(annuitant, survival_factors , discount_factors)
            annuity_factor_PV, modified_duration = valuation.calculateAnnuityFactor()
            fair_offer = annuitant.present_balance / annuity_factor_PV

            print(f"{row["age"]}: MWR: {row["mean_offer"]/fair_offer}")

    if config.PRICING_MODEL == PricingModel.VALUE:
        # Annuity configuration
        annuitant = Annuitant(age_years = 75, age_months = 6, first_payment_year=2025, present_balance=17967, sex=Sex.TOTAL)
    
        survival_factors: ndarray = build_survival_factors(annuitant = annuitant, mortality_table = mortality_table)
        valuation = Valuation(annuitant, survival_factors , discount_factors)
        annuity_factor_PV, modified_duration = valuation.calculateAnnuityFactor()

        fair_offer = annuitant.present_balance / annuity_factor_PV
        print(fair_offer)

if __name__ == "__main__":
    main()
