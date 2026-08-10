import pandas as pd
from pathlib import Path
from typing import Any
from functools import lru_cache


def read_xlsx(path: Path, sheet_name: str = "mortality", **kwargs: Any) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name, **kwargs)
