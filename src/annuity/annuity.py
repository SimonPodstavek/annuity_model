from ..config.schemas import InterestRateModel, MortalityModel, Sex
from ..config.config import config
from ..data_io.excel import read_xlsx
import numpy as np
from math import exp, pow


class Annuitant():
    def __init__(self, age, first_payment_year, present_balance, sex: Sex = Sex.TOTAL):
        self.age = age
        self.sex = sex
        self.first_payment_year = first_payment_year
        self.present_balance = present_balance 
        self.mortality_trend: Annuitant.MortalityTrend = None
        self.annuity_factor_adj: int = 0 


class Mortality:
    def __init__(self):
        self.qx_dict = {}
        
        qx_dict = {}

        age_range = config.MAX_INITIAL_AGE - config.MIN_INITIAL_AGE

        if config.MORTALITY_MODEL == MortalityModel.FULL_MORTALITY_SURFACE:
            prediction_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["mortality_prediction"])
            for sex in prediction_df["sex"].unique():
                qx_dict[sex] = {}
                for age in range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE):
                    mortality_df_slice = prediction_df[prediction_df["sex"] == sex]
                    values = []
                    qx_lookup = mortality_df_slice.set_index(["year", "age"])["qx"]
                    for i in range(age_range + 1):
                        used_year = config.PURCHASE_YEAR + i if i < age_range +1 else config.PURCHASE_YEAR + age_range
                        used_age = age + i  if age < config.MAX_INITIAL_AGE else config.MAX_INITIAL_AGE -1
                        values.append(qx_lookup.loc[(used_year, age)])

                    qx_dict[sex][age] = values

        if config.MORTALITY_MODEL == MortalityModel.CONSTANT:
            realized_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["realized_mortality"])
            for sex in realized_df["sex"].unique():
                latest_year = realized_df["year"].max()
                qx_dict[sex] = {}
                for age in range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE):
                    mortality_df_slice = realized_df[realized_df["sex"] == sex]
                    values = []
                    qx_lookup = mortality_df_slice.set_index(["year", "age"])["qx"]

                    for i in range(age_range + 1):
                        used_year = config.PURCHASE_YEAR
                        used_age = age + i if age < config.MAX_INITIAL_AGE else config.MAX_INITIAL_AGE -1
                        values.append(qx_lookup.loc[(used_year, age)])

                    qx_dict[sex][age] = values

        if config.MORTALITY_MODEL == MortalityModel.REALIZED_AND_TREND:
            realized_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["realized_mortality"])
            mortality_trend_df = read_xlsx(config.MORTALITY_CONFIG[config.MORTALITY_MODEL]["mortality_trend"])
            beta_age_parameters = {}
            
            # Get beta parameter from europop trend
            for sex in mortality_trend_df["sex"].unique():
                beta_age_parameters[sex] = {}
                switch_year = realized_df["year"].max()
                mortality_df_slice = mortality_trend_df[(mortality_trend_df["sex"] == sex) & (mortality_trend_df["year"] > switch_year)]
                for age in range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE):
                    mortality_df_superslice = mortality_df_slice[mortality_df_slice["age"] == age]
                    year = mortality_df_superslice["year"].to_numpy()
                    delta_year = year - mortality_df_superslice["year"].min() +1
                    mortality = mortality_df_superslice["qx"].to_numpy()
                    beta, ln_a = np.polyfit(delta_year, np.log(mortality),1)
                    beta_age_parameters[sex][age] = beta
            
            # Calculate mortality prediction
            for sex in realized_df["sex"].unique():
                switch_year = realized_df["year"].max()
                mortality_df_slice = realized_df[(realized_df["sex"] == sex)]
                qx_dict[sex] = {}
                qx_lookup = mortality_df_slice.set_index(["year", "age"])["qx"]
                for age in range(30, 100):
                    values = []

                    # Check for range max
                    for i in range(0, config.TERMINAL_AGE - config.MIN_INITIAL_AGE +1):
                        used_year = switch_year
                        used_age = age
                        base_qx = qx_lookup.loc[(used_year, used_age)]
                        coeff = exp(beta_age_parameters[sex][used_age]*i)

                        values.append(base_qx*coeff)
                    qx_dict[sex][age] = values

        for key in qx_dict.keys():
          self.qx_dict[Sex(key)] = qx_dict[key]

class Discount:
    def __init__(self):
        self.discount_factor_series = {}
        
        def calculateSvenssonInterestRate(svensson, t_delta):
            
            if (t_delta == 0):
                return 1

            if (t_delta > 30):
                t_delta = 30
            
            svensson_parameters = svensson["parameters"]

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
        
        # For fixed interest rate
        if config.DISCOUNT_MODEL in (InterestRateModel.FIXED, InterestRateModel.ZERO):
            if config.DISCOUNT_MODEL == InterestRateModel.FIXED:
                # Check that the interest rate is set for fixed rate
                if (config.DISCOUNT_CONFIG[InterestRateModel.FIXED]["fixed_rate"] == None):
                    raise Exception("Fixed interest rate must be set in order to determine the discount factor")
                fixed_rate = config.DISCOUNT_CONFIG[InterestRateModel.FIXED]["fixed_rate"]
            if config.DISCOUNT_MODEL == InterestRateModel.ZERO:
                fixed_rate = 0
            for t_delta in range(0, config.TERMINAL_AGE-30+1):
                self.discount_factor_series[t_delta] = pow(1 + fixed_rate,-t_delta)         


        # For svensson interest rate
        if config.DISCOUNT_MODEL == InterestRateModel.SVENSSON:
            for t_delta in range(0, config.TERMINAL_AGE-30+1):
                self.discount_factor_series[t_delta] = pow(calculateSvenssonInterestRate(config.DISCOUNT_CONFIG[InterestRateModel.SVENSSON], t_delta) ,-t_delta)    

        

class Valuation():
    def __init__(self, annuitant: Annuitant, mortality:Mortality, discount: Discount):
        self.annuitant = annuitant
        self.mortality = mortality
        self.discount = discount

    def calculateAnnuityFactor(self) -> int:
        # Survival function modeling
        initial_delta = self.annuitant.first_payment_year - config.PURCHASE_YEAR
        last_delta = config.TERMINAL_AGE - self.annuitant.age
        survival_function = {0:np.float64(1)}

        for t_delta in range(0, last_delta+1):
            age = self.annuitant.age
            used_delta = t_delta if t_delta < config.TERMINAL_AGE - self.annuitant.age else config.TERMINAL_AGE - self.annuitant.age - 1
            qx = self.mortality.qx_dict[self.annuitant.sex][age+used_delta][t_delta]
            survival_function[t_delta+1] = survival_function[t_delta] * (1-qx)

        macaulay_duration_numerator = 0
        annuity_factor_PV = 0   

        # First leg of the annuity (annuity year 1-7), with guaranteed payout for Slovak annuities
        for t_delta in range(initial_delta, initial_delta+7): 
            annuity_factor_PV += self.discount.discount_factor_series[t_delta] 
            macaulay_duration_numerator += self.discount.discount_factor_series[t_delta] * t_delta

        # Second leg of the annuity (annuity year 7+)
        for t_delta in range(initial_delta, last_delta+1): 
            annuity_factor_PV += survival_function[t_delta] * self.discount.discount_factor_series[t_delta] 
            macaulay_duration_numerator += survival_function[t_delta] * self.discount.discount_factor_series[t_delta] * t_delta

        # Calculate modified duration for the annuity 
        mod_duration = macaulay_duration_numerator/annuity_factor_PV

        annuity_factor_adj = survival_function[initial_delta] * annuity_factor_PV
        return annuity_factor_adj, mod_duration
