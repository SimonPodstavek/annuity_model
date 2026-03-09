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

# This dataclass provides configuration for the disocunt rates used in calculating PV of annuity
@dataclass(frozen=True)
class Discount:
    discount_model: InterestRateModel
    fixed_rate: Optional[float] = None
    svenson_parameters: Optional[dict] = None

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
    MORTALITY_CONFIG: dict
    DISCOUNT_CONFIG: dict
    PURCHASE_YEAR: int