from pandas import DataFrame
from .config.schemas import Sex, MortalityTable, PricingModel
from .config.config import config
from .data_io.excel import read_xlsx
from .data_io.stata import read_stata 
from typing import Dict
from numpy import ndarray

# from .annuity.annuity import Annuitant, Mortality, Discount, Valuation


from .mortality.mortality import build_mortality_table
from .discount.discount import build_discount_factors

# Configure model parameters in config/config.py


def main() -> None:
    
    mortality_table:MortalityTable = build_mortality_table()
    # survival_factors: Dict[int, ndarray] = build_survival_factors(mortality_table, Sex('T'))
    discount_factors:Dict[int, ndarray] = build_discount_factors()

    if config.PRICING_MODEL == PricingModel.MWR:
        pass
        # df = read_xlsx(r"src/data/agregaty.xlsx", "data2")
        # df = df[df["year"] == 2025]

        # for index, row in df.iterrows():

        #     # Annuity configuration
        #     annuitant = Annuitant(age = int(row["age"]), first_payment_year=2026, present_balance=row["mean_balance"], sex=Sex.TOTAL)
        
        #     valuation = Valuation(annuitant, mortality, discount)
        #     annuitant.annuity_factor_adj, mod_duration = valuation.calculateAnnuityFactor()
        #     fair_offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)

            # Adjustment for §42a profit redistribution   
            # fair_offer /= 1.02

            # print(f"{row["age"]}: MWR: {row["mean_offer"]/fair_offer}")

    if config.PRICING_MODEL == PricingModel.VALUE:
        # Annuity configuration
        annuitant = Annuitant(age = 65, first_payment_year=2026, present_balance=100000, sex=config.SEX_TYPE)

        valuation = Valuation(annuitant, mortality, discount)


    annuitant.annuity_factor_adj, mod_duration = valuation.calculateAnnuityFactor()
    fair_offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)

    # Adjustment for §42a profit redistribution   

    print(fair_offer)

if __name__ == "__main__":
    main()
