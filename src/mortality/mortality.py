from ..config.config import config
from ..config.schemas import MortalityModel, MortalityTable, Sex
from ..data_io import read_xlsx
import numpy as np




def build_mortality_table() -> MortalityTable: 
    ages = range(config.MIN_INITIAL_AGE_MONTHS, config.TERMINAL_AGE_MONTHS)  #360...1188 (30 to 99 years)
    t_count = config.TERMINAL_AGE_MONTHS - config.MIN_INITIAL_AGE_MONTHS + 1    #(829 months) (99-30) 69 years + 1 month


    if config.MORTALITY_MODEL == MortalityModel.FULL_MORTALITY_SURFACE:
        return from_full_surface(ages, t_count)
    elif config.MORTALITY_MODEL == MortalityModel.CONSTANT:
        return from_constant(ages, t_count)
    # elif config.MORTALITY_MODEL == MortalityModel.REALIZED_AND_TREND:
    #     return from_realized_and_trend(config, ages, t_count)
    else:
        raise ValueError(f"Unknown mortality model: {config.MORTALITY_MODEL}")


def from_full_surface(ages: range, t_count: int) -> MortalityTable:
    table = {}

    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.FULL_MORTALITY_SURFACE]["mortality_prediction"])
    max_year = int(df["year"].max())

    t_arr = np.arange(t_count)
    years = np.minimum(config.BASE_YEAR + (config.BASE_MONTH + t_arr) // 12, max_year)

    for sex_str in df["sex"].unique():
        lookup = df[df["sex"] == sex_str].set_index(["year", "age"])["qx"]
        sex = Sex(sex_str)
        
        year_ages = np.array(ages) // 12  # shape (len(ages),)
        keys = [(y, a) for a in year_ages for y in years]  # all (year, age) pairs
        values = lookup.loc[keys].to_numpy().reshape(len(ages), t_count)
        table[sex] = dict(zip(ages, values))
    return table




def from_constant(ages: range, t_count: int) -> MortalityTable:
    table = {}

    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.FULL_MORTALITY_SURFACE]["mortality_prediction"])
    max_year = int(df["year"].max())

    t_arr = np.arange(t_count)
    years = np.full(t_arr, max_year)

    for sex_str in df["sex"].unique():
        lookup = df[df["sex"] == sex_str].set_index(["year", "age"])["qx"]
        sex = Sex(sex_str)
        
        year_ages = np.array(ages) // 12  # shape (len(ages),)
        keys = [(y, a) for a in year_ages for y in years]  # all (year, age) pairs
        
        values = lookup.loc[keys].to_numpy().reshape(len(ages), t_count)
        table[sex] = dict(zip(ages, values))
    return table

# def from_realized_and_trend(config: Config, ages: range, t_count: int) -> Dict[Sex, Dict[int, np.ndarray]]:
#     realized_df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.REALIZED_AND_TREND]["realized_mortality"])
#     trend_df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.REALIZED_AND_TREND]["mortality_trend"])

#     switch_year = int(realized_df["year"].max())  # last SUSR year (2024)

#     # --- Step 1: fit beta per sex per age ---
#     beta: Dict[str, Dict[int, float]] = {}
#     for sex_str in trend_df["sex"].unique():
#         beta[sex_str] = {}
#         post_df = trend_df[(trend_df["sex"] == sex_str) & (trend_df["year"] > switch_year)]
#         for age in ages:
#             age_df = post_df[post_df["age"] == age].sort_values("year")
#             years = age_df["year"].to_numpy()
#             delta = years - years.min() + 1       # 1-indexed offset from first post-switch year
#             log_qx = np.log(age_df["qx"].to_numpy())
#             slope, _ = np.polyfit(delta, log_qx, 1)
#             beta[sex_str][age] = slope

#     # --- Step 2: build table ---
#     table = {}
#     for sex_str in realized_df["sex"].unique():
#         base_lookup = realized_df[realized_df["sex"] == sex_str].set_index(["year", "age"])["qx"]
#         sex = Sex(sex_str)
#         table[sex] = {}
#         for age in ages:
#             base_qx = base_lookup.loc[(switch_year, age)]
#             b = beta[sex_str][age]
#             table[sex][age] = np.array([base_qx * exp(b * t) for t in range(t_count)])
#     return table


# def __init__(self):
#     self.qx_dict = {}
    
#     qx_dict = {}

#     age_range = config.MAX_INITIAL_AGE - config.MIN_INITIAL_AGE

#     if config.MORTALITY_MODEL == MortalityModel.FULL_MORTALITY_SURFACE:
#         prediction_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["mortality_prediction"])
#         for sex in prediction_df["sex"].unique():
#             qx_dict[sex] = {}
#             for age in range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE):
#                 mortality_df_slice = prediction_df[prediction_df["sex"] == sex]
#                 values = []
#                 qx_lookup = mortality_df_slice.set_index(["year", "age"])["qx"]
#                 for i in range(age_range + 1):
#                     used_year = config.PURCHASE_YEAR + i if i < age_range +1 else config.PURCHASE_YEAR + age_range
#                     used_age = age + i  if age < config.MAX_INITIAL_AGE else config.MAX_INITIAL_AGE -1
#                     values.append(qx_lookup.loc[(used_year, age)])

#                 qx_dict[sex][age] = values

#     if config.MORTALITY_MODEL == MortalityModel.CONSTANT:
#         realized_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["realized_mortality"])
#         for sex in realized_df["sex"].unique():
#             latest_year = realized_df["year"].max()
#             qx_dict[sex] = {}
#             for age in range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE):
#                 mortality_df_slice = realized_df[realized_df["sex"] == sex]
#                 values = []
#                 qx_lookup = mortality_df_slice.set_index(["year", "age"])["qx"]

#                 for i in range(age_range + 1):
#                     used_year = config.PURCHASE_YEAR
#                     used_age = age + i if age < config.MAX_INITIAL_AGE else config.MAX_INITIAL_AGE -1
#                     values.append(qx_lookup.loc[(used_year, age)])

#                 qx_dict[sex][age] = values

#     if config.MORTALITY_MODEL == MortalityModel.REALIZED_AND_TREND:
#         realized_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["realized_mortality"])
#         mortality_trend_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["mortality_trend"])
#         beta_age_parameters = {}
        
#         # Get beta parameter from europop trend
#         for sex in mortality_trend_df["sex"].unique():
#             beta_age_parameters[sex] = {}
#             switch_year = realized_df["year"].max()
#             mortality_df_slice = mortality_trend_df[(mortality_trend_df["sex"] == sex) & (mortality_trend_df["year"] > switch_year)]
#             for age in range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE):
#                 mortality_df_superslice = mortality_df_slice[mortality_df_slice["age"] == age]
#                 year = mortality_df_superslice["year"].to_numpy()
#                 delta_year = year - mortality_df_superslice["year"].min() +1
#                 mortality = mortality_df_superslice["qx"].to_numpy()
#                 beta, ln_a = np.polyfit(delta_year, np.log(mortality),1)
#                 beta_age_parameters[sex][age] = beta
        
#         # Calculate mortality prediction
#         for sex in realized_df["sex"].unique():
#             switch_year = realized_df["year"].max()
#             mortality_df_slice = realized_df[(realized_df["sex"] == sex)]
#             qx_dict[sex] = {}
#             qx_lookup = mortality_df_slice.set_index(["year", "age"])["qx"]
#             for age in range(30, 100):
#                 values = []

#                 # Check for range max
#                 for i in range(0, config.TERMINAL_AGE - config.MIN_INITIAL_AGE +1):
#                     used_year = switch_year
#                     used_age = age
#                     base_qx = qx_lookup.loc[(used_year, used_age)]
#                     coeff = exp(beta_age_parameters[sex][used_age]*i)

#                     values.append(base_qx*coeff)
#                 qx_dict[sex][age] = values

#     for key in qx_dict.keys():
#       self.qx_dict[Sex(key)] = qx_dict[key]