from ..config.schemas import config, Sex,MortalityTrendSource
from math import ceil
# from scipy.optimize import curve_fit
import numpy as np

class Annuitant():
    def __init__(self, age, first_payment_year, present_balance, sex: Sex = Sex.TOTAL):
        self.age = age
        if config.sex_separated:
            self.sex = Sex.TOTAL
        else:
            self.sex = sex

        self.first_payment_year = first_payment_year
        self.present_balance = present_balance 
        self.mortality_trend: Annuitant.MortalityTrend = None

class MortalityTrend:
    def __init__(self, mortality_df, annuitant: "Annuitant"):
        self.mortality_df = mortality_df
        self.annuitant = annuitant
        self.age_parameters = {Sex.FEMALE: {},
                               Sex.MALE: {},
                               Sex.TOTAL: {}}


    def estimateMortalityTrend(self):
        # If mortality is assumed to be constant
        for sex in Sex:
            for age in range(30, 98):
                self.age_parameters[sex][age] = 0

        for sex in Sex:
            mortality_df_slice_gender = self.mortality_df[self.mortality_df["sex"] == sex.value]
            for age in range(30, 98):
                mortality_df_slice = mortality_df_slice_gender[mortality_df_slice_gender["age"] == age]
                
                year = mortality_df_slice["year"].to_numpy()
                year = year - mortality_df_slice["year"].min()
                mortality = mortality_df_slice["qx"].to_numpy()

                b, ln_a = np.polyfit(year, np.log(mortality),1)

                self.age_parameters[sex][age] = b