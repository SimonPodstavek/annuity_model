from dataclasses import dataclass
from enum import Enum
from numpy import ndarray
from typing import Dict


# This Enum provides data source for the model 
class InterestRateModel(str, Enum):
    FIXED = "FIXED"
    SVENSSON = "SVENSSON"

class MortalityModel(str, Enum):
    FULL_MORTALITY_SURFACE = "MORTALITY_SURFACE"
    REALIZED_AND_TREND = "REALIZED_&_TREND"
    CONSTANT = "CONSTANT"

class Sex(Enum):
    MALE = "M"
    FEMALE = "F"
    TOTAL = "T"
    WEIGHTED = "W"



@dataclass
class Config:
    MORTALITY_MODEL: MortalityModel
    MORTALITY_CONFIG: dict
    DISCOUNT_MODEL: InterestRateModel
    DISCOUNT_CONFIG: dict
    BASE_YEAR: int
    AGE_START_MONTHS: int
    AGE_END_MONTHS: int 


# Mortality table measure the probability of dying in a monthly interval
# For t = 0 -> qx (probability of dying) in a month [PURCHASE_YEAR MONTH  0, PURCHASE_YEAR MONTH 1]
# i.e. qx[t] is the probability of dying DURING month t
# The first KVP (Sex - Dict) defines sex specific mortality within the dataset, as mortality for multiple sexes may be available
# The second KVP is (int, ndarray) identifies mortality in a given year (ndarray) for age in months (int)
MortalityTable = Dict[Sex, Dict[int, ndarray]]
