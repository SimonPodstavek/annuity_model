from pandas import DataFrame
from .config.schemas import config, Sex
from .data_io.excel import read_xlsx
from .annuity.annuity import Annuitant, MortalityTrend, InterestRate, Valuation


# Basic config
config.present_year = 2026
config.sex_separated = True

# Annuity configuration
anuitant = Annuitant(age = 69, first_payment_year=2026, present_balance=17973, sex=Sex.FEMALE)


def main(annuitant) -> None:

    # Model preparation
    baseline_mortality_df = read_xlsx(config.mortality.baseline_mortality_path)
    baseline_mortality_df = baseline_mortality_df.set_index(["year", "age","sex"]).sort_index()
    mortality_trend_df = read_xlsx(config.mortality.mortality_trend_path)
    mortality_trend = MortalityTrend(mortality_trend_df,anuitant)
    mortality_trend.estimateMortalityTrend()
    interest_rate = InterestRate()
    

    valuation = Valuation(annuitant, baseline_mortality_df, mortality_trend, interest_rate)
    annuitant.annuity_factor_adj = valuation.calculateAnnuityFactor()

    offer = annuitant.present_balance / (12*annuitant.annuity_factor_adj)

    print(f"Offer: {offer}")


if __name__ == "__main__":
    main(anuitant)