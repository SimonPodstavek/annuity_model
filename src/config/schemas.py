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
    PURCHASE_YEAR: int
    # 99 years of ife
    TERMINAL_AGE_MONTHS:int = 1188
    SEX_TYPE: Sex
    # 30 years of life
    MIN_INITIAL_AGE_MONTHS:int = 360
    # 90 years of life
    MAX_INITIAL_AGE_MONTHS:int = 1080

@dataclass
class MortalityTable:
    table: Dict[Sex, Dict[int, ndarray]]
    # For t = 0 -> qx (probability of dying) for monthly interval [PURCHASE_YEAR MONTH 0, PURCHASE_YEAR MONTH 1]
    # i.e. qx[t] is the probability of sying DURING month t
    # Count start from the moment of purchase (inclusive). E.g. if annuity is purchased 20/12/2025, then t=0 is December 2025 and t=1 is January 2026
    # Survival from annity purchase until month T = product of (1-qx[s]) for s in 0,...,T-1 
    base_year : int
    base_month: int