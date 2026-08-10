from .schemas import Config, DiscountModel, MortalityModel, PricingModel,  Sex
from pathlib import Path
from itertools import combinations
from math import factorial

BASE_DIR = Path(__file__).resolve().parents[2]

# Step 1: Choose any of the 3 available interest rate models (ZERO, SVENSSON, FIXED) and change parameters of the respective model in DISCOUNT_CONFIG.
DISCOUNT_MODEL = DiscountModel.FIXED

DISCOUNT_CONFIG = {
    DiscountModel.FIXED: {
        "fixed_rate": 0.0
    },

    #  1 July 2025
    DiscountModel.SVENSSON: {
            "parameters": {
                "b0": 0.996390,
                "b1": 0.896780,
                "b2": -0.953647,
                "b3": 6.818138,
                "t1": 2.028327,
                "t2": 12.022171	
        }
    },
    DiscountModel.FULL_DISCOUNT_SERIES: {
        "discount_series_path": Path(BASE_DIR / "data/cluster_yields.npy" )
    }
}
	
# Step 2.1: This model uses one of two modes of operation for mortality prediction:
MORTALITY_MODEL = MortalityModel.FULL_MORTALITY_SURFACE


# a) Full mortality surface - you provide full mortality prediction. 
# b) Realized + trend - you provide realized mortality and mortality trend.
# c) Constant mortality. This assumes mortality to be only age dependent (ignores year).
# For mode a), b) and c) the ages must be between 30 and 99 (inclusive for both ends).
# for mode a) the years must range from  purchase year to purchase year + 75 (So if it is now 2026, the years must range from 2026 to 2101)
# for mode b) There MUST be an intercept in year range between realized mortality and mortality prediction. (If realized mortality ends in 2024 and first mortality trend is in 2025, the model WILL FAIL).
# The model will take the most recent mortality available in the baseline model (e.g. 2024) and extract mortality prediction from the second dataset from 2024 onwards and applies it to the baseline prediction.
# For mode b) make sure that every sex present in realized motality is present in mortality trend and vice versa.
# for mode c) the latest available year will be used

# Step 2.2 Update dataset paths
DATASET_PATH = {
    "susr_mortality_path": Path(BASE_DIR / "data/mortality/susr_mortality.xlsx" ),
    "europop_mortality_path": Path(BASE_DIR / "data/mortality/europop_mortality.xlsx"),
    "RRZ_mortality_path": Path(BASE_DIR / "data/mortality/RRZ_mortality_projection.xlsx"),
    "presov_mortality_path": Path(BASE_DIR / "data/mortality/regions/regional_mortality_PO_extrapolated.xlsx"),
    "lithuania_mortality_path": Path(BASE_DIR / "data/mortality/foreign/lithuania_full_mortality_surface.xlsx"),
    "germany_mortality_path": Path(BASE_DIR / "data/mortality/foreign/germany_full_mortality_surface.xlsx"),
    "latvia_mortality_path": Path(BASE_DIR / "data/mortality/foreign/latvia_full_mortality_surface.xlsx"),
    "ireland_mortality_path": Path(BASE_DIR / "data/mortality/foreign/ireland_full_mortality_surface.xlsx"),
}


# Step 2.3 Update mortality config according to 2.1
MORTALITY_CONFIG = {
    MortalityModel.FULL_MORTALITY_SURFACE:{
        "mortality_prediction": DATASET_PATH["europop_mortality_path"]
    },
    MortalityModel.CONSTANT: {
        "realized_mortality": DATASET_PATH["susr_mortality_path"]
    }
}

# Step 2.4: Chooose sex type. Make sure that the sex type is available in both datasets provided (THIS IS NOT CHECKED, and if chosen sex is not available, the model WILL FAIL)
# Check in schams.py that the encoded representation matches that of dataset (E.g. Sex.FEMALE corresponds to F, and therefore F must be in the Sex field)
SEX = Sex.TOTAL

# Step 3: Set annuity pruchase year. (default 2026) This is also the time when the annuity the annuity starts paying out (no deferred annuities).
BASE_YEAR = 2026

# Age range for time tables. Do not change these unless time rnage has changes in the life tables themselves
# 30 years of life - Used as range for computing life table
AGE_START_MONTHS = 360 #360 = 30 years 0 months (inclusive)
# 99 years of life - Used as range for computing life table
AGE_END_MONTHS = 1200 #1200 = 100 years 0 months (exclusive)

# Step 4: Choose the mode of the tool - calculate annuity (PricingModel.VALUE) / calculate fees (PricingModel.FEES)
PRICING_MODEL = PricingModel.VALUE

# Step 5: Choose whether to take into account 7 year guarantee as defined in § 32 of 43/2004
GUARANTEE_84_MONTHS = True

# Step 6: Set the relativae mortality of annuitant in relation to the general population - this shoud be between 0  (immortality) and 2 (double the mortality of population)
RELATIVE_MORTALITY = 1

# Step 7: Set the variable fee that the insurer demands for their services - this shoud be between 0  (no fee) and 1 (100% fee)
VARIABLE_FEE = 0

# Step 8: Set the fraction by which the annuity changes each year. Meaning: 0  (no annuity :( ), 0.5 (annuity halves every year) 1 (annuity remains the same), 2 (annuity doubles every year)
YEARLY_INCREASE_COEFFICIENT = 1

# Step 9 Set survivor coverage in months. Meaning: 0 (no survivor coverage), 12 (12 months survivor coverage), 24 (24 months survivor coverage)  
SURVIVOR_COVERAGE = 0



config = Config(
    MORTALITY_MODEL = MORTALITY_MODEL,
    MORTALITY_CONFIG = MORTALITY_CONFIG,
    DISCOUNT_MODEL = DISCOUNT_MODEL,
    DISCOUNT_CONFIG = DISCOUNT_CONFIG,
    PRICING_MODEL = PRICING_MODEL,
    BASE_YEAR = BASE_YEAR,
    AGE_START_MONTHS = AGE_START_MONTHS,
    AGE_END_MONTHS = AGE_END_MONTHS,
    SEX = SEX,
    GUARANTEE_84_MONTHS = GUARANTEE_84_MONTHS,
    RELATIVE_MORTALITY = RELATIVE_MORTALITY,
    VARIABLE_FEE = VARIABLE_FEE,
    YEARLY_INCREASE_COEFFICIENT = YEARLY_INCREASE_COEFFICIENT,
    SURVIVOR_COVERAGE = SURVIVOR_COVERAGE
)
