from dataclasses import dataclass
from enum import Enum
from numpy import ndarray
from typing import Dict


# This Enum provides data source for the model 
class DiscountModel(str, Enum):
    FIXED = "FIXED"
    SVENSSON = "SVENSSON"

class MortalityModel(str, Enum):
    FULL_MORTALITY_SURFACE = "MORTALITY_SURFACE"
    CONSTANT = "CONSTANT"

class Sex(Enum):
    MALE = "M"
    FEMALE = "F"
    TOTAL = "T"
    WEIGHTED = "W"


class PricingModel(Enum):
    MWR = "MWR"
    VALUE = "VALUE"



@dataclass
class Config:
    MORTALITY_MODEL: MortalityModel
    MORTALITY_CONFIG: dict
    DISCOUNT_MODEL: DiscountModel
    DISCOUNT_CONFIG: dict
    PRICING_MODEL: PricingModel
    BASE_YEAR: int
    AGE_START_MONTHS: int
    AGE_END_MONTHS: int
    GUARANTEE_84_MONTHS: bool


# MortalityTable[sex][age_months] -> ndarray of length n_years
# ndarray[t] = annual qx for calendar year (BASE_YEAR + t)
# age_months: AGE_START_MONTHS to AGE_END_MONTHS - 1 (360..1199 = 30y0m to 99y11m)
# Months within the same integer age share the same qx — mortality data is annual.
MortalityTable = Dict[Sex, Dict[int, ndarray]]