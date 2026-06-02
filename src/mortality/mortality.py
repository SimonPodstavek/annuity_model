from ..config.config import config
from ..config.schemas import MortalityModel, MortalityTable, Sex
from ..data_io import read_xlsx
import numpy as np

# def build_survival_factors(mortality_table: MortalityModel, sex:Sex):
    


def build_mortality_table() -> MortalityTable: 
    ages = range(config.AGE_START_MONTHS, config.AGE_END_MONTHS)  #360...1199 (30years 0 months to 99 years 11 months)


    if config.MORTALITY_MODEL == MortalityModel.FULL_MORTALITY_SURFACE:
        return from_full_surface(ages)
    elif config.MORTALITY_MODEL == MortalityModel.CONSTANT:
        return from_constant(ages)
    else:
        raise ValueError(f"Unknown mortality model: {config.MORTALITY_MODEL}")


def from_full_surface(ages: range) -> MortalityTable:
    table = {}
    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.FULL_MORTALITY_SURFACE]["mortality_prediction"])

    for sex_str in df["sex"].unique():
        sex = Sex(sex_str)
        table[sex] = {}
        for age in ages:
            if age % 12 == 0:
                age_year = age // 12
                age_specific_mortalities =  df[(df["sex"] == sex_str) & (df["age"] == age_year)].sort_values("year")["qx"].to_numpy()
            table[sex][age] = age_specific_mortalities
    return table


def from_constant(ages: range) -> MortalityTable:
    table = {}
    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.CONSTANT]["realized_mortality"])
    latest_year = df["year"].max()

    for sex_str in df["sex"].unique():
        sex = Sex(sex_str)
        table[sex] = {}
        year_span = len(ages)
        for age in ages:
            if age % 12 == 0:
                age_year = age // 12
                q =  df[(df["sex"] == sex_str) & (df["age"] == age_year) & (df["year"] == latest_year)]["qx"].values[0]
                constant_age_specific_mortality = np.full(year_span, q)
            table[sex][age] = constant_age_specific_mortality
    return table