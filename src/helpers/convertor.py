import pandas as pd
import numpy as np
from pathlib import Path

from ..config.config import BASE_DIR

BASE_YEAR = 2025
END_YEAR = 2101  # exclusive

REGION_CODES = ["ZA", "TN", "TT", "PO", "NR", "KE", "BB", "BA", "total"]


def _fit_decay_factors(ep_mort_df):
    """Per-(sex, age) annual multiplicative decay factor from EUROPOP.

    EUROPOP mortality declines roughly exponentially, so we fit
    log(qx) = a + b * (year - BASE_YEAR) for each (sex, age) and take
    the annual factor as exp(b). Only positive observations are used.
    """
    ep = ep_mort_df.copy()
    ep["age"] = ep["age"].str.split(" ").str[0].astype(int)
    ep["sex"] = ep["sex"].map({"Females": "F", "Males": "M"})
    ep = ep[(ep["TIME_PERIOD"] >= BASE_YEAR) & (ep["TIME_PERIOD"] < END_YEAR)]

    def fit(group):
        years = group["TIME_PERIOD"].to_numpy() - BASE_YEAR
        vals = group["OBS_VALUE"].to_numpy()
        mask = vals > 0
        if mask.sum() < 2:
            return 1.0
        slope = np.polyfit(years[mask], np.log(vals[mask]), 1)[0]
        return float(np.exp(slope))

    factors = ep.groupby(["sex", "age"]).apply(fit, include_groups=False)
    return factors.to_dict()  # {(sex, age): factor}


def _factor_lookup(factors, sex, age):
    """Gender- and age-specific decay factor.

    EUROPOP only provides Males/Females, so the 'T' (total) rows use the
    average of the male and female factors at that age.
    """
    if sex in ("F", "M"):
        return factors.get((sex, age), 1.0)
    f_female = factors.get(("F", age), 1.0)
    f_male = factors.get(("M", age), 1.0)
    return (f_female + f_male) / 2.0


def _interpolate_zero_qx(base_df, group_cols):
    """Replace qx == 0 by log-linear interpolation over neighbouring ages.

    Mortality is roughly log-linear in age, so interior gaps are
    interpolated in log space. Zeros at the age boundaries (no neighbour
    on one side) hold the nearest valid value.
    """
    parts = []
    for _, group in base_df.groupby(group_cols, sort=False):
        group = group.sort_values("age").copy()
        qx = group["qx"].astype(float).where(lambda x: x > 0)  # zeros -> NaN
        group["qx"] = np.exp(
            np.log(qx).interpolate(method="linear", limit_direction="both")
        )
        parts.append(group)
    return pd.concat(parts, ignore_index=True)


def _extrapolate(base_df, factors, extra_cols=()):
    """Project a BASE_YEAR table forward to END_YEAR via exponential decay.

    qx(year) = qx(BASE_YEAR) * factor ** (year - BASE_YEAR)

    `extra_cols` are leading identifier columns to carry through (e.g."region" for the combined sheet).
    """
    years = range(BASE_YEAR, END_YEAR)
    rows = []
    for row in base_df.itertuples(index=False):
        record = row._asdict()
        sex, age, qx = record["sex"], record["age"], record["qx"]
        factor = _factor_lookup(factors, sex, age)
        prefix = tuple(record[c] for c in extra_cols)
        for year in years:
            rows.append(prefix + (sex, age, year, qx * factor ** (year - BASE_YEAR)))

    cols = list(extra_cols) + ["sex", "age", "year", "qx"]
    return (
        pd.DataFrame(rows, columns=cols)
        .sort_values(list(extra_cols) + ["sex", "age", "year"])
        .reset_index(drop=True)
    )


def generateRegionalGenderSpecificMortalityTables():
    mortality_path = Path(BASE_DIR, "data/mortality/regions/regional_mortality.xlsx")
    output_path = Path(BASE_DIR, "data/mortality/regions/regional_mortality_extrapolated.xlsx")
    ep_mort_df = pd.read_csv(Path(BASE_DIR, "data/raw/europop mortality.csv"))

    factors = _fit_decay_factors(ep_mort_df)

    xl = pd.ExcelFile(mortality_path)
    sheets = {name: pd.read_excel(mortality_path, sheet_name=name) for name in xl.sheet_names}

    # Per-region sheets: columns [sex, age, year, qx]
    for code in REGION_CODES:
        name = f"{code}_mortality"
        base = sheets[name]
        base = base[base["year"] == BASE_YEAR].sort_values(["sex", "age"])
        base = _interpolate_zero_qx(base, group_cols=["sex"])
        sheets[name] = _extrapolate(base, factors)

    # Combined 'mortality' sheet: columns [region, sex, age, year, qx]
    combined = sheets["mortality"]
    combined = combined[combined["year"] == BASE_YEAR].sort_values(["region", "sex", "age"])
    combined = _interpolate_zero_qx(combined, group_cols=["region", "sex"])
    sheets["mortality"] = _extrapolate(combined, factors, extra_cols=["region"])

    # Write to a separate file, preserving original sheet order (deaths/population untouched)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for name in xl.sheet_names:
            sheets[name].to_excel(writer, sheet_name=name, index=False)


if __name__ == "__main__":
    generateRegionalGenderSpecificMortalityTables()