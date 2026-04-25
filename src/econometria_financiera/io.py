from __future__ import annotations

from pathlib import Path

import pandas as pd


def clean_analysis_outputs(output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.csv", "analysis_report.md"):
        for path in output_dir.glob(pattern):
            try:
                path.unlink()
            except PermissionError as exc:
                raise PermissionError(f"No se pudo limpiar {path}. Cierra el archivo si esta abierto y vuelve a intentar.") from exc


def write_csv(frame: pd.DataFrame, path: str | Path, index: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame.to_csv(path, index=index)
    except PermissionError as exc:
        raise PermissionError(f"No se pudo escribir {path}. Cierra el archivo si esta abierto y vuelve a intentar.") from exc
