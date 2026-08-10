from pathlib import Path
from ..config.schemas import Sex, MortalityModel, DiscountModel, PricingModel
from ..config.config import config, BASE_DIR


FEATURES = ["sex", "relative_mortality", "variable_fee", "duration_mismatch", "excess_return_payout", "guarantee_84_months", "yearly_increase_coefficient", "survivor_coverage"]

# Values in real scenario
ACTUAL = {
    "sex": Sex.TOTAL,
    "relative_mortality": 0.6,
    "variable_fee": 0.1,
    "duration_mismatch": True,
    "excess_return_payout": True,
    "guarantee_84_months": True,
    "yearly_increase_coefficient": 1.02,
    "survivor_coverage": 12

}

# Values in ideal scenario
BENCHMARK = {
    "sex": Sex.MALE,
    "relative_mortality": 1,
    "variable_fee": 0,
    "duration_mismatch": False,
    "excess_return_payout": False,
    "guarantee_84_months": False,
    "yearly_increase_coefficient": 1,
    "survivor_coverage": 0
}


def set_config(subset: frozenset) -> None:
    duration_mismatch = (ACTUAL if 'duration_mismatch' in subset else BENCHMARK)['duration_mismatch']
    excess_return_payout = (ACTUAL if 'excess_return_payout' in subset else BENCHMARK)['excess_return_payout']
    RELATIVE_MORTALITY = (ACTUAL if 'relative_mortality' in subset else BENCHMARK)['relative_mortality']
    SEX = (ACTUAL if 'sex' in subset else BENCHMARK)['sex']
    GUARANTEE_84_MONTHS = (ACTUAL if 'guarantee_84_months' in subset else BENCHMARK)['guarantee_84_months']

    VARIABLE_FEE = (ACTUAL if 'variable_fee' in subset else BENCHMARK)['variable_fee']  
    MORTALITY_CONFIG = { MortalityModel.FULL_MORTALITY_SURFACE:{
        "mortality_prediction": Path(BASE_DIR / "data/mortality/europop_mortality.xlsx")
    }}

    YEARLY_INCREASE_COEFFICIENT = (ACTUAL if 'yearly_increase_coefficient' in subset else BENCHMARK)['yearly_increase_coefficient']
    SURVIVOR_COVERAGE = (ACTUAL if 'survivor_coverage' in subset else BENCHMARK)['survivor_coverage']
    

    # if duration_mismatch, then the insurer received only fixed length on short term maturities
    # if excess_return_payout, then the insurer may pay out excess return. In calculation, act as if though they did not to estimate the effect. If excess_return_payout, then the annuity amount should be lower

    if duration_mismatch and excess_return_payout:
        DISCOUNT_MODEL = DiscountModel.FIXED
        DISCOUNT_CONFIG ={DiscountModel.FIXED: {"fixed_rate": 0.01}}
    elif duration_mismatch and not excess_return_payout:
        DISCOUNT_MODEL = DiscountModel.FIXED
        DISCOUNT_CONFIG ={DiscountModel.FIXED: {"fixed_rate": 0.02520}}
    elif not duration_mismatch and excess_return_payout:
        DISCOUNT_MODEL = DiscountModel.SVENSSON
        DISCOUNT_CONFIG ={DiscountModel.SVENSSON:{
            "parameters": {
                "b0": 0,
                "b1": 0.896780,
                "b2": -0.953647,
                "b3": 6.818138,
                "t1": 2.028327,
                "t2": 12.022171	
        }}}
    else:
        DISCOUNT_MODEL = DiscountModel.SVENSSON
        DISCOUNT_CONFIG ={DiscountModel.SVENSSON:{
            "parameters": {
                "b0": 0.996390,
                "b1": 0.896780,
                "b2": -0.953647,
                "b3": 6.818138,
                "t1": 2.028327,
                "t2": 12.022171	
        }}}


    config.__dict__.update(
        MORTALITY_MODEL = MortalityModel.FULL_MORTALITY_SURFACE,
        MORTALITY_CONFIG = MORTALITY_CONFIG,
        DISCOUNT_MODEL = DISCOUNT_MODEL,
        DISCOUNT_CONFIG = DISCOUNT_CONFIG,
        PRICING_MODEL = PricingModel.SHAPLEY,
        BASE_YEAR = 2026,
        AGE_START_MONTHS = 360,
        AGE_END_MONTHS = 1200,
        SEX = SEX,
        GUARANTEE_84_MONTHS = GUARANTEE_84_MONTHS,
        RELATIVE_MORTALITY = RELATIVE_MORTALITY,
        VARIABLE_FEE = VARIABLE_FEE,
        YEARLY_INCREASE_COEFFICIENT = YEARLY_INCREASE_COEFFICIENT,
        SURVIVOR_COVERAGE = SURVIVOR_COVERAGE
        )
    

