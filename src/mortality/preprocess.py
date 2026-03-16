import numpy as np
from math import exp
from typing import Dict
from ..config.schemas import Sex, MortalityModel, Config
from ..data_io.excel import read_xlsx


def build_mortality_table(config: Config) -> Dict[Sex, Dict[int, np.ndarray]]:
    """
    Build a period mortality table indexed by [sex][age][t].

    Semantics: table[sex][age][t] = qx for someone aged `age`
    in calendar year (PURCHASE_YEAR + t).

    age : MIN_INITIAL_AGE to MAX_INITIAL_AGE - 1 (30..99 inclusive)
    t   : 0 to TERMINAL_AGE - MIN_INITIAL_AGE   (0..75 inclusive)

    All data-source-specific age/year capping is handled here.
    The annuity model only does: current_age = min(age + t, MAX_INITIAL_AGE - 1)
    """
    ages = range(config.MIN_INITIAL_AGE, config.MAX_INITIAL_AGE)  # 30..99
    t_count = config.TERMINAL_AGE - config.MIN_INITIAL_AGE + 1    # 76

    if config.MORTALITY_MODEL == MortalityModel.FULL_MORTALITY_SURFACE:
        return _from_full_surface(config, ages, t_count)
    elif config.MORTALITY_MODEL == MortalityModel.CONSTANT:
        return _from_constant(config, ages, t_count)
    elif config.MORTALITY_MODEL == MortalityModel.REALIZED_AND_TREND:
        return _from_realized_and_trend(config, ages, t_count)
    else:
        raise ValueError(f"Unknown mortality model: {config.MORTALITY_MODEL}")


def _from_full_surface(config: Config, ages: range, t_count: int) -> Dict[Sex, Dict[int, np.ndarray]]:
    """
    RRZ full projected surface.
    For each (age, t): look up qx(year = PURCHASE_YEAR + t, age) directly.
    Year is capped at the maximum year available in the dataset.
    """
    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.FULL_MORTALITY_SURFACE]["mortality_prediction"])
    max_year = int(df["year"].max())

    table = {}
    for sex_str in df["sex"].unique():
        lookup = df[df["sex"] == sex_str].set_index(["year", "age"])["qx"]
        sex = Sex(sex_str)
        table[sex] = {}
        for age in ages:
            values = np.empty(t_count)
            for t in range(t_count):
                year = min(config.PURCHASE_YEAR + t, max_year)
                values[t] = lookup.loc[(year, age)]
            table[sex][age] = values
    return table


def _from_constant(config: Config, ages: range, t_count: int) -> Dict[Sex, Dict[int, np.ndarray]]:
    """
    SUSR realized mortality, frozen at the latest available year.
    qx is constant across t for each age — no calendar-year improvement.
    """
    df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.CONSTANT]["realized_mortality"])
    latest_year = int(df["year"].max())

    table = {}
    for sex_str in df["sex"].unique():
        lookup = df[df["sex"] == sex_str].set_index(["year", "age"])["qx"]
        sex = Sex(sex_str)
        table[sex] = {}
        for age in ages:
            qx_val = lookup.loc[(latest_year, age)]
            table[sex][age] = np.full(t_count, qx_val)
    return table


def _from_realized_and_trend(config: Config, ages: range, t_count: int) -> Dict[Sex, Dict[int, np.ndarray]]:
    """
    SUSR base mortality + EUROPOP exponential improvement trend.

    Step 1 — Fit improvement rate beta(age) from EUROPOP:
        For each age, fit log(qx) ~ beta * delta_year on EUROPOP data
        that lies strictly after the SUSR switch year (the last SUSR year).
        beta < 0 means mortality is improving (declining) over time.

    Step 2 — Build period table:
        base_qx(age) = SUSR qx at switch year
        table[sex][age][t] = base_qx(age) * exp(beta(age) * t)

    This gives period mortality for someone of fixed age `age`
    with t years of trend improvement applied.
    """
    realized_df = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.REALIZED_AND_TREND]["realized_mortality"])
    trend_df    = read_xlsx(config.MORTALITY_CONFIG[MortalityModel.REALIZED_AND_TREND]["mortality_trend"])

    switch_year = int(realized_df["year"].max())  # last SUSR year (2024)

    # --- Step 1: fit beta per sex per age ---
    beta: Dict[str, Dict[int, float]] = {}
    for sex_str in trend_df["sex"].unique():
        beta[sex_str] = {}
        post_df = trend_df[(trend_df["sex"] == sex_str) & (trend_df["year"] > switch_year)]
        for age in ages:
            age_df   = post_df[post_df["age"] == age].sort_values("year")
            years    = age_df["year"].to_numpy()
            delta    = years - years.min() + 1       # 1-indexed offset from first post-switch year
            log_qx   = np.log(age_df["qx"].to_numpy())
            slope, _ = np.polyfit(delta, log_qx, 1)
            beta[sex_str][age] = slope

    # --- Step 2: build table ---
    table = {}
    for sex_str in realized_df["sex"].unique():
        base_lookup = realized_df[realized_df["sex"] == sex_str].set_index(["year", "age"])["qx"]
        sex = Sex(sex_str)
        table[sex] = {}
        for age in ages:
            base_qx  = base_lookup.loc[(switch_year, age)]
            b        = beta[sex_str][age]
            table[sex][age] = np.array([base_qx * exp(b * t) for t in range(t_count)])
    return table
