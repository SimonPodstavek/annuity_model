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

class Sex(Enum):
    MALE = "M"
    FEMALE = "F"
    TOTAL = "T"

# This dataclass provides paths to the data source files
@dataclass(frozen=True)
class DataSet:
    susr_mortality_path: Path
    europop_mortality_path: Path
    svenson_parameters_path: Optional[Path] = None

# This dataclass provides configuration for the disocunt rates used in calculating PV of annuity
@dataclass(frozen=True)
class Discount:
    discount_model: InterestRateModel
    fixed_rate: Optional[float] = None


@dataclass()
class Mortality: 
    # Types of baseline mortality and mortality trends
    baseline_mortality_type: MortalitySource 
    mortality_trend_type: MortalityTrendSource

    # Paths to baseline mortality and mortality trends as chosen in config
    baseline_mortality_path: Optional[Path] = None
    mortality_trend_path: Optional[Path] = None

    def set_mortality_path(self, dataset) -> None:

        if(self.baseline_mortality_type == MortalitySource.SUSR):
            self.baseline_mortality_path = dataset.susr_mortality_path
        elif (self.baseline_mortality_type == MortalitySource.EUROPOP):
            self.baseline_mortality_path = dataset.susr_mortality_path
        else:
            raise Exception("Incorrect baseline mortality selected")
        
        if(self.mortality_trend_type == MortalityTrendSource.SUSR):
            self.mortality_trend_path = dataset.susr_mortality_path
        elif (self.mortality_trend_type == MortalityTrendSource.EUROPOP):
            self.mortality_trend_path = dataset.europop_mortality_path
        elif(self.mortality_trend_type == MortalityTrendSource.LAST_AVAILABLE_MORTALITY):
            self.mortality_trend_path = self.baseline_mortality_path
        else:
            raise Exception("Incorrect mortality trend selected")
        
    # Constraints
    # min_age is the minimum age that the annuity calculation can start at
    min_initial_age = 30
    max_initial_age = 98
    # terminal_age is the assumed maximum attainable age
    terminal_age = 130

@dataclass()
class Config:
    dataset: DataSet
    discount: Discount
    mortality: Mortality
    sex_separated: bool = True
    present_year: int = 2026

# SUSR initial mortality + EUROPOP trend with fixed risk-free rate at 2% p.a.
dataset = DataSet(
    susr_mortality_path = Path(BASE_DIR / "src/data/susr_mortality.xlsx" ),
    europop_mortality_path = Path(BASE_DIR / "src/data/europop_mortality.xlsx")
)


mortality = Mortality(
    baseline_mortality_type = MortalitySource.SUSR,
    mortality_trend_type = MortalityTrendSource.EUROPOP,
)

mortality.set_mortality_path(dataset)

discount = Discount(
    discount_model = 'fixed', 
    fixed_rate = 0.02
)


config = Config(
    dataset = dataset,
    discount = discount,
    mortality = mortality
)