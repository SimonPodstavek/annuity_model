from .schemas import Config, InterestRateModel, MortalityModel
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Step 1: Choose any of the 3 available interest rate models (ZERO, SVENSSON, FIXED) and change parameters of the respective model in DISCOUNT_CONFIG.
DISCOUNT_MODEL = InterestRateModel.SVENSSON

DISCOUNT_CONFIG = {
    InterestRateModel.FIXED: {
        "fixed_rate": 0.01
    },
    InterestRateModel.SVENSSON: {
            "svenson_parameters": {
                "b0": 1.189950,
                "b1": 0.776282,
                "b2": -0.653820,
                "b3": 7.321428,
                "t1": 2.708616,
                "t2": 16.292510
        }
    }
}

# Step 2: This model uses one of two modes of operation for mortality prediction:
MORTALITY_MODEL = MortalityModel.CONSTANT
# a)  Full mortality surface - you provide full mortality prediction. 
# b) Realized + trend - you provide realized mortality and mortality trend.
# c) Constant mortality. This assumes mortality to be only age dependent (ignores year).
# For mode a), b) and c) the ages must be between 30 and 105.
# for mode a) the years must range from  purchase year to purchase year + 75 (So if it is now 2026, the years must range from 2026 to 2101)
# for mode b) There MUST be an intercept in year range between baseline model and mortality prediction. (If realized mortality ends in 2024 and first mortality trend is in 2025, the model WILL FAIL)
# The model will take the most recent mortality available in the baseline model (e.g. 2024) and extract mortality prediction from the second dataset from 2024 onwards and applies it to the baseline prediction.
# for mode c) the latest available year will be used

# Step 2.5 Update dataset paths
DATASET_PATH = {
    "susr_mortality_path": Path(BASE_DIR / "src/data/susr_mortality.xlsx" ),
    "europop_mortality_path": Path(BASE_DIR / "src/data/europop_mortality.xlsx"),
    "RRZ_mortality_path": Path(BASE_DIR / "src/data/RRZ_mortality_projection.xlsx")
}
   


# Update mortality config according to the rules above
MORTALITY_CONFIG = {
    MortalityModel.CONSTANT:{
        "realized_mortality": DATASET_PATH.susr_mortality_path
    },
    
    MortalityModel.FULL_MORTALITY_SURFACE:{
        "mortality_prediction": DATASET_PATH.RRZ_mortality_path
    },
  
    MortalityModel.REALIZED_AND_TREND:{
        "realized_mortality": DATASET_PATH.susr_mortality_path,
        "mortality_trend": DATASET_PATH.europop_mortality_path
    }
}

# Step 3: Set annuity pruchase year. (default 2026) This may differ from the year when the annuity starts paying out.
PURCHASE_YEAR = 2026


config = Config(
    DATASET_PATH = DATASET_PATH,
    MORTALITY_CONFIG = MORTALITY_CONFIG,
    DISCOUNT_CONFIG = DISCOUNT_CONFIG,
    PURCHASE_YEAR = PURCHASE_YEAR
)



