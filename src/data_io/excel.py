import pandas as pd
from pathlib import Path
from typing import Any

def read_xlsx(path: Path, **kwargs: Any):
    return pd.read_excel(Path(path), **kwargs)
