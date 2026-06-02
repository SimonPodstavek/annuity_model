from ..config.config import config
from ..config.schemas import DiscountModel
from typing import Dict
import numpy as np
from numpy import ndarray
from math import exp, pow

def build_discount_factors() -> Dict[int, ndarray]: 
    period_months = config.AGE_END_MONTHS - config.AGE_START_MONTHS
    
    if config.DISCOUNT_MODEL == DiscountModel.SVENSSON:
        return from_svensson(period_months)
    if config.DISCOUNT_MODEL == DiscountModel.FIXED:
        return fixed_yield(period_months)
    else:
        raise ValueError(f"Unknown discount model: {config.DISCOUNT_MODELs}")


def from_svensson(period_months:int) -> Dict[int, ndarray]:
    discount_factor_series = {}
    period_years = period_months//12

    for i, t_delta in enumerate(np.linspace(0,period_years,period_months)):
        coefficient = pow(calculateSvenssonInterestRate(config.DISCOUNT_CONFIG[DiscountModel.SVENSSON],t_delta),-t_delta) 
        discount_factor_series[i] = coefficient
    return discount_factor_series


def fixed_yield(period_months:int) -> Dict[int, ndarray]:
    discount_factor_series = {}
    period_years = period_months//12

    for i, t_delta in enumerate(np.linspace(0,period_years,period_months)):
        coefficient = pow((1+config.DISCOUNT_CONFIG[DiscountModel.FIXED]['fixed_rate']),-t_delta) 
        discount_factor_series[i] = coefficient
    return discount_factor_series


def calculateSvenssonInterestRate(svensson, t_delta):
    if (t_delta == 0):
        return 1

    if (t_delta > 30):
        t_delta = 30
    
    svensson_parameters = svensson["parameters"]

    b0,b1,b2,b3,t1,t2 = (
        svensson_parameters["b0"],
        svensson_parameters["b1"],
        svensson_parameters["b2"],
        svensson_parameters["b3"],
        svensson_parameters["t1"],
        svensson_parameters["t2"],
    )

    m1 = (1-exp(-t_delta/t1)) / (t_delta/t1)
    m2 = (1-exp(-t_delta/t2)) / (t_delta/t2)

    rate =  b0 + (b1+b2)*m1 - b2 * exp(-t_delta/t1) + b3*(m2-exp(-t_delta/t2))
    
    # Convert to coefficient, e.g. if rate=2.5%, then return 1.025
    return 1 + (rate/100)
        
