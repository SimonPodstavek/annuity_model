from pandas import DataFrame
from .config.schemas import verifyDataSetValidity, Sex
from .config.config import config
from .data_io.excel import read_xlsx
from .annuity.annuity import Annuitant, Mortality, Discount, Valuation

# Configure model parameters in config/config.py


def main() -> None:
    # Finish verification method
    verifyDataSetValidity()

    mortality = Mortality()
    discount = Discount()

    # Compute MWR
    CIPS_annuity_df = read_xlsx("src/data/agregaty.xlsx", sheet_name="data2")
    CIPS_annuity_df = CIPS_annuity_df[CIPS_annuity_df["year"] > 2024]

    MWR_offers = []

    for i, offer in enumerate(CIPS_annuity_df.itertuples(index=True), start=1):

        # Annuity configuration
        annuitant = Annuitant(age = offer.age, first_payment_year=2026, present_balance=offer.mean_balance, sex=config.SEX_TYPE)
        # annuitant = Annuitant(age = 65, first_payment_year=2026, present_balance=100000, sex=Sex.WEIGHTED)

        valuation = Valuation(annuitant, mortality, discount)
        annuitant.annuity_factor_adj, mod_duration = valuation.calculateAnnuityFactor()
        fair_offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)

        # Adjustment for §42a profit redistribution   
        # fair_offer /= 1.02

        MWR_offers.append(round(100*(offer.mean_offer/fair_offer),2))   
        # mod_duration = round(mod_duration/(1.01),2)
        
        if(i%5==0):
            # print(f"{offer.age} {offer.year}\t{mod_duration}")
            # print(f"{offer.age} {offer.year} {round(fair_offer,2)}")
            print(f"{offer.age} {round((MWR_offers[0]+MWR_offers[4])/200,3)}")
            MWR_offers=[]


if __name__ == "__main__":
    main()