from pandas import DataFrame
from .config.schemas import config, Sex
from .data_io.excel import read_xlsx
from .annuity.annuity import Annuitant, MortalityTrend, DiscountRate, Valuation

# Basic config
config.present_year = 2026
config.sex_separated = True


def main() -> None:
    # Model preparation
    baseline_mortality_df = read_xlsx(config.mortality.baseline_mortality_path, sheet_name="mortality")
    baseline_mortality_df = baseline_mortality_df.set_index(["year", "age","sex"]).sort_index()
    mortality_trend_df = read_xlsx(config.mortality.mortality_trend_path, sheet_name="mortality")
    mortality_trend = MortalityTrend(mortality_trend_df)
    mortality_trend.estimateMortalityTrend()
    discount_rate = DiscountRate()




    CIPS_annuity_df = read_xlsx("src/data/agregaty.xlsx", sheet_name="data2")
    CIPS_annuity_df = CIPS_annuity_df[CIPS_annuity_df["year"] > 2024]
    offers = []
    for i, offer in enumerate(CIPS_annuity_df.itertuples(index=True), start=1):
        # Annuity configuration
        annuitant = Annuitant(age = offer.age, first_payment_year=offer.year, present_balance=offer.mean_balance, sex=Sex.TOTAL)
        valuation = Valuation(annuitant, baseline_mortality_df, mortality_trend, discount_rate)
        annuitant.annuity_factor_adj = valuation.calculateAnnuityFactor()
        fair_offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)
        # print(f"Age: {offer.age}, Year: {offer.year}, Quintile: {offer.quintile}  MWR: {round(100*(offer.mean_offer/fair_offer),2) } %")
        offers.append(round(100*(offer.mean_offer/fair_offer),2))   
        
        if(i%5==0):
            print(f"Age: {offer.age}, Year: {offer.year}, Q1 MWR: {offers[0]}% Q5 MWR: {offers[4]} %")
            # print(f"{offer.age} - {offer.year} - {offers[2]}")
            offers=[]


if __name__ == "__main__":
    main()