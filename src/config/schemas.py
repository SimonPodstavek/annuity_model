from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal

@dataclass(frozen=True)
class DataSet:
    baseline_mortality_path: Path
    europop_mortality_path: Path
    svenson_parameters_path: Path

@dataclass(frozen=True)
class Discount:
    discount_model: Literal['fixed', 'ECBSVENSON']
    fixed_rate: Optional[float]

@dataclass(frozen=True)
class Mortality: 
    mortality_model: Literal['SUSR+EUROPOP', 'EUROPOP', 'fixed'] 
    terminal_age: int
    sex_separated: bool


@dataclass(frozen=True)
class Config:
    present_year = 2026
    dataset_config = DataSet
    discount_config = Discount
    mortality_config = Mortality



# SUSR initial mortality + EUROPOP trend with fixed risk-free rate at 2% p.a.

dataset_config = DataSet()
discount_config = Discount('fixed', 0.02)



Config = 