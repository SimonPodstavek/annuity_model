from ..config.config import config
from ..config.schemas import MortalityModel, MortalityTable, Sex
from ..data_io import read_xlsx
import numpy as np
from ..annuity.annuity import Annuitant
from math import ceil

def build_survival_factors(annuitant: Annuitant, mortality_table: MortalityTable):
    time_span = config.AGE_END_MONTHS - annuitant.initial_month_age 

    initial_year = annuitant.first_payment_year
    
    age_specific_mortality_table = mortality_table[annuitant.sex]

    survival_factors = np.zeros(time_span)
    sx = 1

    for i in range(time_span):
        t = annuitant.initial_month_age + i
        year_delta = i//12
          

        qx = age_specific_mortality_table[t][year_delta] * config.RELATIVE_MORTALITY
        sx = sx * (1-qx)

        survival_factors[i] = sx
    return survival_factors 


def build_mortality_table() -> MortalityTable: 
    ages = range(config.AGE_START_MONTHS, config.AGE_END_MONTHS)  #360...1199 (30years 0 months to 99 years 11 months)
    year_range = range(config.BASE_YEAR,(config.BASE_YEAR) + ceil(len(ages)/12)+1)

    if config.MORTALITY_MODEL == MortalityModel.FULL_MORTALITY_SURFACE:
        return from_full_surface(ages,year_range)
    elif config.MORTALITY_MODEL == MortalityModel.CONSTANT:
        return from_constant(ages,year_range)
    else:
        raise ValueError(f"Unknown mortality model: {config.MORTALITY_MODEL}")


def from_full_surface(ages: range, year_range:range) -> MortalityTable:
    table = {}
    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.FULL_MORTALITY_SURFACE]["mortality_prediction"])

    age_specific_mortalities = None

    for sex_str in df["sex"].unique():
        sex = Sex(sex_str)
        table[sex] = {}
        for age in ages:
            if age % 12 == 0:
                age_year = age // 12
                age_specific_mortalities =  df[(df["sex"] == sex_str) & (df["age"] == age_year) & (df["year"].isin(year_range)) ].sort_values("year")["qx"].to_numpy()

                # Assume uniform distribution of Deaths within a year and adjust to monthly mortality 
                age_specific_mortalities = age_specific_mortalities / 12
            table[sex][age] = age_specific_mortalities
    return table


def from_constant(ages: range, year_range:range) -> MortalityTable:
    table = {}
    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.CONSTANT]["realized_mortality"])
    latest_year = df["year"].max()
    constant_age_specific_mortality = None

    for sex_str in df["sex"].unique():
        sex = Sex(sex_str)
        table[sex] = {}
        year_span = len(ages)
        for age in ages:
            if age % 12 == 0:
                age_year = age // 12
                q =  df[(df["sex"] == sex_str) & (df["age"] == age_year) & (df["year"] == latest_year)]["qx"].values[0]
                # Assume uniform distribution of Deaths within a year and adjust to monthly mortality 
                q /= 12
                constant_age_specific_mortality = np.full(len(year_range), q)
            table[sex][age] = constant_age_specific_mortality
    return table