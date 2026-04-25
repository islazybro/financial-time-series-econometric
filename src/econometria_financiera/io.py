from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_csv(frame: pd.DataFrame, path: str | Path, index: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame.to_csv(path, index=index)
    except PermissionError as exc:
        raise PermissionError(f"No se pudo escribir {path}. Cierra el archivo si esta abierto y vuelve a intentar.") from exc
