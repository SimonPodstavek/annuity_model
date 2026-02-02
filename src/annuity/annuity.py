from ..config.schemas import config, Sex,MortalityTrendSource, InterestRateModel
from math import ceil
# from scipy.optimize import curve_fit
import numpy as np
from math import exp


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
    def __init__(self, mortality_df):
        self.mortality_df = mortality_df
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


class DiscountRate:
    def __init__(self):
        self.discount_factor_series = {}
        
        def calculateSvenssonInterestRate(svensson_parameters, t_delta):
            t_delta = t_delta+1 
            b0,b1,b2,b3,t1,t2 = (
                svensson_parameters["b0"],
                svensson_parameters["b1"],
                svensson_parameters["b2"],
                svensson_parameters["b3"],
                svensson_parameters["t1"],
                svensson_parameters["t2"],
            )

            m1 = (1-exp(-t_delta/t1)) / (t_delta/t1)
            m2 = (1-exp(-t_delta/t2)) / (t_delta/t2)

            rate =  b0 + (b1+b2)*m1 - b2 * exp(-t_delta/t1) + b3*(m2-exp(-t_delta/t2))
            # Convert to coefficient, e.g. if rate=2.5%, then return 1.025
            return 1 + (rate/100)
            

        
        # Fixed interest rate
        if config.discount.discount_model == InterestRateModel.FIXED or config.discount.discount_model == InterestRateModel.ZERO:
            
            # Check that the interest rate is set for fixed rate
            if (config.discount.discount_model == InterestRateModel.FIXED and config.discount.fixed_rate == None):
                raise Exception("Fixed interest rate must be set in order to determine the discount factor")

            # Set fixed rate to zero if such discounting is selected
            if config.discount.discount_model == InterestRateModel.ZERO:
                config.discount.fixed_rate = 0

            discount_factor = 1
            for t_delta in range(0, 110):
                self.discount_factor_series[t_delta] = 1/discount_factor
                discount_factor = discount_factor * (1+ config.discount.fixed_rate)        



        if config.discount.discount_model == InterestRateModel.SVENSSON:
            discount_factor = 1
            for t_delta in range(0, 110):
                self.discount_factor_series[t_delta] = 1/discount_factor
                discount_factor = discount_factor * calculateSvenssonInterestRate(config.discount.svenson_parameters, t_delta)        




class Valuation():
    def __init__(self, annuitant: Annuitant, baseline_mortality_df, mortality_trend: MortalityTrend, discount_rate: DiscountRate):
        self.annuitant = annuitant
        self.baseline_mortality_df = baseline_mortality_df
        self.mortality_trend = mortality_trend
        self.discount_rate = discount_rate

    def calculateAnnuityFactor(self) -> int:
        # Survival function modeling
        # initial_delta = self.annuitant.first_payment_year - config.present_year
        initial_delta = 0
        last_delta = 98 - self.annuitant.age +1
        survival_function = {0:np.float64(1)}

        # Make sure to make the lastest year dynamic
        # Up to 98 YOA
        latest_year = self.baseline_mortality_df.index.get_level_values("year").max()         
        for t_delta in range(0, last_delta):
            age = self.annuitant.age+t_delta
            qx = self.baseline_mortality_df.loc[(latest_year, age, self.annuitant.sex.value), "qx"]
            beta = self.mortality_trend.b_age_parameters[self.annuitant.sex][age] 
            # beta = 0
            survival_function[t_delta+1] = survival_function[t_delta] * (1- qx * np.exp(beta*t_delta))
            
        # 98 up to 105 YOA
        for age in range(99, 105):
            
            t_delta = age - self.annuitant.age
            qx = self.baseline_mortality_df.loc[(latest_year, age, self.annuitant.sex.value), "qx"]
            beta = self.mortality_trend.b_age_parameters[self.annuitant.sex][98] 
            survival_function[t_delta+1] = survival_function[t_delta] * (1- qx * np.exp(beta*t_delta))
        

        annuity_factor_future = 0

        for t_delta in range(initial_delta, last_delta): 
            annuity_factor_future += survival_function[t_delta] * self.discount_rate.discount_factor_series[t_delta] 
        
        annuity_factor_adj = survival_function[initial_delta] * annuity_factor_future
        return annuity_factor_adj
