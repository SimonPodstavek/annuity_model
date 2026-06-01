from pandas import DataFrame
from .config.schemas import Sex
from .config.config import config
from .data_io.excel import read_xlsx
from .data_io.stata import read_stata 

from .annuity.annuity import Annuitant, Mortality, Discount, Valuation

# Configure model parameters in config/config.py


def main() -> None:

    mortality = Mortality()
    discount = Discount()

    # df = read_xlsx(r"src/data/agregaty.xlsx", "data2")
    # df = df[df["year"] == 2025]

    # for index, row in df.iterrows():

    #     # Annuity configuration
    #     annuitant = Annuitant(age = int(row["age"]), first_payment_year=2026, present_balance=row["mean_balance"], sex=Sex.TOTAL)

    #     valuation = Valuation(annuitant, mortality, discount)
    #     annuitant.annuity_factor_adj, mod_duration = valuation.calculateAnnuityFactor()
    #     fair_offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)

    #     # Adjustment for §42a profit redistribution   
    #     # fair_offer /= 1.02

    #     print(f"{row["age"]}: MWR: {row["mean_offer"]/fair_offer}")

    # Annuity configuration
    annuitant = Annuitant(age = 65, first_payment_year=2026, present_balance=100000, sex=Sex.TOTAL)

    valuation = Valuation(annuitant, mortality, discount)


    annuitant.annuity_factor_adj, mod_duration = valuation.calculateAnnuityFactor()
    fair_offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)

    # Adjustment for §42a profit redistribution   

    print(fair_offer)

if __name__ == "__main__":
    df = read_stata(r"H:\My Drive\RRZ\annuity_model\src\data\priebehy_synteticke.dta")
    main()
