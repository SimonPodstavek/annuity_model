import numpy as np
from pathlib import Path
from typing import Any

def read_numpy(path: Path, **kwargs: Any) -> np.ndarray:
    return np.load(path, **kwargs)
