from .schemas import Config, InterestRateModel, MortalityModel, Sex
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Step 1: Choose any of the 3 available interest rate models (ZERO, SVENSSON, FIXED) and change parameters of the respective model in DISCOUNT_CONFIG.
DISCOUNT_MODEL = InterestRateModel.FIXED

DISCOUNT_CONFIG = {
    InterestRateModel.FIXED: {
        "fixed_rate": 0.01
    },
    InterestRateModel.SVENSSON: {
            "parameters": {
                "b0": 1.164096,
                "b1": 0.689967,
                "b2": 2.443759,
                "b3": 7.329445,
                "t1": 0.864350,
                "t2": 13.853053
        }
    }
}

# Step 2.1: This model uses one of two modes of operation for mortality prediction:
MORTALITY_MODEL = MortalityModel.REALIZED_AND_TREND


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
SUSR_MORTALITY_PATH = BASE_DIR / "src/data/susr_mortality.xlsx"
EUROPOP_MORTALITY_PATH = BASE_DIR / "src/data/europop_mortality.xlsx"
RRZ_MORTALITY_PATH = BASE_DIR / "src/data/RRZ_mortality_projection.xlsx"
IRELAND_EUROPOP_MORTALITY_PATH = BASE_DIR / "src/data/ireland_full_mortality_surface.xlsx"



# Step 2.3 Update mortality config according to 2.1
MORTALITY_CONFIG = {
    MortalityModel.FULL_MORTALITY_SURFACE: {
        "mortality_prediction": RRZ_MORTALITY_PATH
    },
    MortalityModel.CONSTANT: {
        "realized_mortality": SUSR_MORTALITY_PATH
    },
    MortalityModel.REALIZED_AND_TREND: {
        "realized_mortality": SUSR_MORTALITY_PATH,
        "mortality_trend": EUROPOP_MORTALITY_PATH
    }
}

# Step 2.4: Chooose sex type. Make sure that the sex type is available in both datasets provided (THIS IS NOT CHECKED, and if chosen sex is not available, the model WILL FAIL)
# Check in schams.py that the encoded representation matches that of dataset (E.g. Sex.FEMALE corresponds to F, and therefore F must be in the Sex field)
SEX_TYPE = Sex.TOTAL

# Step 3: Set annuity pruchase year. (default 2026) This may differ from the year when the annuity starts paying out.
PURCHASE_YEAR = 2026

# Step 4: The maximum attainable age in the model
TERMINAL_AGE = 105


config = Config(
    MORTALITY_MODEL=MORTALITY_MODEL,
    MORTALITY_CONFIG=MORTALITY_CONFIG,
    DISCOUNT_MODEL=DISCOUNT_MODEL,
    DISCOUNT_CONFIG=DISCOUNT_CONFIG,
    PURCHASE_YEAR=PURCHASE_YEAR,
    TERMINAL_AGE=TERMINAL_AGE,
    SEX_TYPE=SEX_TYPE,
)



