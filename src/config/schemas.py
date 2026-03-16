from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


# This Enum provides data source for the model 
class InterestRateModel(str, Enum):
    FIXED = "FIXED"
    ZERO = "ZERO"
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


# Finish this verification function
def verifyDataSetValidity():    
    # min_age is the minimum age that the annuity calculation can start at
    min_initial_age = 30
    max_initial_age = 98
    # terminal_age is the assumed maximum attainable age
    terminal_age = 105

@dataclass()
class Config:
    DATASET_PATH: dict
    MORTALITY_MODEL: MortalityModel
    MORTALITY_CONFIG: dict
    DISCOUNT_MODEL: InterestRateModel
    DISCOUNT_CONFIG: dict
    PURCHASE_YEAR: int
    TERMINAL_AGE: int
    SEX_TYPE: Sex
    MIN_INITIAL_AGE = 30
    MAX_INITIAL_AGE = 100