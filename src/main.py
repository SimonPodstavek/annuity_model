from pandas import DataFrame
from .config.schemas import config, Sex
from .data_io.excel import read_xlsx
from .annuity.annuity import Annuitant, MortalityTrend

# Annuity configuration
anuitant = Annuitant(age = 65, first_payment_year=2026, present_balance=10000, sex=Sex.FEMALE),
config.present_year = 2026




def main(annuitant) -> None:

    

    mortality_trend_df = read_xlsx(config.mortality.mortality_trend_path)
    mortality_trend = MortalityTrend(mortality_trend_df,anuitant)
    mortality_trend.estimateMortalityTrend()



if __name__ == "__main__":
    main(anuitant)