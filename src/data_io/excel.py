import pandas as pd
from pathlib import Path
from typing import Any

def read_xlsx(path: Path, sheet_name: str = "mortality", **kwargs: Any) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name, **kwargs)
