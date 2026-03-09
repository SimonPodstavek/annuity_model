import pandas as pd
from pathlib import Path
from typing import Any

def read_xlsx(path: Path, sheet_name="mortality", **kwargs: Any):
    return pd.read_excel(path, sheet_name, **kwargs)
