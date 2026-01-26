from ..config.schemas import config, Sex,MortalityTrendSource
from math import ceil
# from scipy.optimize import curve_fit
import numpy as np
from math import pow


class Annuitant():
    def __init__(self, age, first_payment_year, present_balance, sex: Sex = Sex.TOTAL):
        self.age = age
        if config.sex_separated:
            self.sex = sex
        else:
            self.sex = Sex.TOTAL

        self.first_payment_year = first_payment_year
        self.present_balance = present_balance 
        self.mortality_trend: Annuitant.MortalityTrend = None
        self.annuity_factor_adj: int = 0 

class MortalityTrend:
    def __init__(self, mortality_df, annuitant: "Annuitant"):
        self.mortality_df = mortality_df
        self.annuitant = annuitant
        self.b_age_parameters = {Sex.FEMALE: {},
                               Sex.MALE: {},
                               Sex.TOTAL: {}}
        
    def estimateMortalityTrend(self) -> None:
        # If mortality is assumed to be constant
        for sex in Sex:
            for age in range(30, 99):
                self.b_age_parameters[sex][age] = 0

        for sex in Sex:
            mortality_df_slice_gender = self.mortality_df[self.mortality_df["sex"] == sex.value]
            for age in range(30, 99):
                mortality_df_slice = mortality_df_slice_gender[mortality_df_slice_gender["age"] == age]
    
                year = mortality_df_slice["year"].to_numpy()
                year = year - mortality_df_slice["year"].min() +1
                mortality = mortality_df_slice["qx"].to_numpy()
                b, ln_a = np.polyfit(year, np.log(mortality),1)
                self.b_age_parameters[sex][age] = b

class InterestRate:
    def __init__(self):
        self.interest_rate_series = {}
        
        if config.discount.fixed_rate:
            for year in range(0, 70):
                self.interest_rate_series[year] = config.discount.fixed_rate

class Valuation():
    def __init__(self, annuitant: Annuitant, baseline_mortality_df, mortality_trend: MortalityTrend, interest_rate: InterestRate):
        self.annuitant = annuitant
        self.baseline_mortality_df = baseline_mortality_df
        self.mortality_trend = mortality_trend
        self.interest_rate = interest_rate

    def calculateAnnuityFactor(self) -> int:
        # Survival function modeling
        initial_delta = self.annuitant.first_payment_year - config.present_year
        last_delta = 98 - self.annuitant.age +1
        survival_function = {0:np.float64(1)}

        # Make sure to make the lastest year dynamic
        latest_year = self.baseline_mortality_df.index.get_level_values("year").max()         
        for t_delta in range(0, last_delta):
            age = self.annuitant.age+t_delta
            qx = self.baseline_mortality_df.loc[(latest_year, age, self.annuitant.sex.value), "qx"]
            beta = self.mortality_trend.b_age_parameters[self.annuitant.sex][age] 
            # beta = 0
            survival_function[t_delta+1] = survival_function[t_delta] * (1- qx * np.exp(beta*t_delta))


        annuity_factor_future = 0

        for t_delta in range(initial_delta, last_delta): 
            discount_factor = 1/ pow(1+self.interest_rate.interest_rate_series[t_delta], t_delta) 
            annuity_factor_future += survival_function[t_delta] * discount_factor 
        
        annuity_factor_adj = survival_function[initial_delta] * annuity_factor_future
        return annuity_factor_adj
