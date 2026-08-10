from ..config.config import config
from ..config.schemas import DiscountModel
from ..data_io.numpy import read_numpy
from typing import Dict
import numpy as np
from numpy import ndarray
from math import exp, pow
from functools import lru_cache

def build_discount_factors() -> ndarray: 
    period_months = config.AGE_END_MONTHS - config.AGE_START_MONTHS
    

    if config.DISCOUNT_MODEL == DiscountModel.FULL_DISCOUNT_SERIES:
        return discount_series(period_months)
    if config.DISCOUNT_MODEL == DiscountModel.FIXED:
        return fixed_yield(period_months)
    if config.DISCOUNT_MODEL == DiscountModel.SVENSSON:
        return from_svensson(period_months)
    else:
        raise ValueError(f"Unknown discount model: {config.DISCOUNT_MODEL}")



def discount_series(period_months:int) -> ndarray:
    cluster_yields = read_numpy(config.DISCOUNT_CONFIG[DiscountModel.FULL_DISCOUNT_SERIES]["discount_series_path"])
    return cluster_yields

@lru_cache(maxsize = 10)
def _fixed_yield_cached(period_months:int, fixed_rate: float) -> ndarray:
    discount_factor_series = np.zeros(period_months)
    period_years = period_months//12

    for i, t_delta in enumerate(np.linspace(0,period_years,period_months)):
        coefficient = pow((1+fixed_rate),-t_delta) 
        discount_factor_series[i] = coefficient
    return discount_factor_series


def fixed_yield(period_months:int) -> ndarray:
   fixed_rate = config.DISCOUNT_CONFIG[DiscountModel.FIXED]['fixed_rate']
   return _fixed_yield_cached(period_months, fixed_rate).copy()

@lru_cache(maxsize = 10)
def _from_svensson_cached(period_months:int, svensson_parameters: tuple) -> ndarray:
    discount_factor_series = np.zeros(period_months)
    period_years = period_months//12

    for i, t_delta in enumerate(np.linspace(0,period_years,period_months)):
        coefficient = pow(calculateSvenssonInterestRate(svensson_parameters,t_delta),-t_delta) 
        discount_factor_series[i] = coefficient
    return discount_factor_series

def from_svensson(period_months:int) -> ndarray:
    params = config.DISCOUNT_CONFIG[DiscountModel.SVENSSON]
    svensson_parameters = tuple(params["parameters"].values())
    return _from_svensson_cached(period_months, svensson_parameters).copy()

def calculateSvenssonInterestRate(svensson_parameters, t_delta):
    if (t_delta == 0):
        return 1

    if (t_delta > 30):
        t_delta = 30
    
    b0,b1,b2,b3,t1,t2 = svensson_parameters

    m1 = (1-exp(-t_delta/t1)) / (t_delta/t1)
    m2 = (1-exp(-t_delta/t2)) / (t_delta/t2)

    rate =  b0 + (b1+b2)*m1 - b2 * exp(-t_delta/t1) + b3*(m2-exp(-t_delta/t2))
    
    # Convert to coefficient, e.g. if rate=2.5%, then return 1.025
    return 1 + (rate/100)
        
