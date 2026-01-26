from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


BASE_DIR = Path(__file__).resolve().parents[2]

# This Enum provides data source for the baseline mortality in the initial year
class MortalitySource(str, Enum):
    EUROPOP = "EUROPOP"
    SUSR = "SUSR"

# This Enum provides data source for the mortality trend
class MortalityTrendSource(str, Enum):
    LAST_AVAILABLE_MORTALITY = "LAST_AVAILABLE_MORTALITY"
    EUROPOP = "EUROPOP"
    SUSR = "SUSR"

# This Enum provides data source for the model 
class InterestRateModel(str, Enum):
    ZERO = "ZERO"
    FIXED = "FIXED"
    SVENSSON = "SVENSSON"

# This dataclass provides paths to the data source files
@dataclass(frozen=True)
class DataSet:
    baseline_mortality_path: Path
    europop_mortality_path: Path
    svenson_parameters_path: Optional[Path] = None

# This dataclass provides configuration for the disocunt rates used in calculating PV of annuity
@dataclass(frozen=True)
class Discount:
    discount_model: InterestRateModel
    fixed_rate: Optional[float] = None


@dataclass(frozen=True)
class Mortality: 
    base_mortality: MortalitySource 
    mortality_trend: MortalityTrendSource
    # min_age is the minimum age that the annuity calculation can start at
    min_age = 30
    # terminal_age is the assumed maximum attainable age
    terminal_age = 130
    # Are Males and Females priced differently?
    sex_separated: bool

@dataclass(frozen=True)
class Config:
    present_year = 2026
    dataset: DataSet
    discount: Discount
    mortality: Mortality

# SUSR initial mortality + EUROPOP trend with fixed risk-free rate at 2% p.a.
dataset = DataSet(
    baseline_mortality_path = Path(BASE_DIR / "data" / "susr_mortality.xlsx"),
    europop_mortality_path = Path(BASE_DIR / "data" / "europop_mortality.xlsx")
)

discount = Discount(
    discount_model = 'fixed', 
    fixed_rate = 0.02
)

mortality = Mortality(
    base_mortality = MortalitySource.SUSR,
    mortality_trend = MortalityTrendSource.EUROPOP,
    sex_separated = True
)

config = Config(
    dataset = dataset,
    discount = discount,
    mortality = mortality
)