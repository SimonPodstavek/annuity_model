import pandas as pd
from pathlib import Path


def read_xlsx(path: Path, **kwargs: Any):
    return pd.read_excel(Path(path), **kwargs)