import pandas as pd
from pathlib import Path
from typing import Any

def read_stata(path: Path, **kwargs: Any) -> pd.DataFrame:
    return pd.read_stata(path, **kwargs)
