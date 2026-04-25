from __future__ import annotations

from pathlib import Path

import pandas as pd

from econometria_financiera.data import load_price_series


RAW_DIR = Path("data/raw")
EXPECTED_FILES = {
    "BBVA": RAW_DIR / "BBVA.csv",
    "Santander": RAW_DIR / "SAN.csv",
}


def validate_series(name: str, path: Path) -> list[str]:
    issues: list[str] = []

    if not path.exists():
        return [f"{name}: no existe el archivo {path}"]

    raw_rows = len(pd.read_csv(path))

    try:
        bundle = load_price_series(path, name)
    except Exception as exc:
        return [f"{name}: no se pudo leer el archivo. Detalle: {exc}"]

    prices = bundle.prices.dropna()
    returns = bundle.returns.dropna()
    dropped_rows = raw_rows - len(prices)

    if dropped_rows > 0:
        issues.append(
            f"{name}: se descartaron {dropped_rows} filas al limpiar. "
            "Revisa encabezados, fechas vacias o precios no numericos."
        )

    if len(prices) < 36:
        issues.append(f"{name}: tiene {len(prices)} observaciones; se recomiendan al menos 36.")

    if prices.index.has_duplicates:
        issues.append(f"{name}: hay fechas duplicadas.")

    if (prices <= 0).any():
        issues.append(f"{name}: hay precios menores o iguales a cero.")

    if returns.empty:
        issues.append(f"{name}: no se pudieron calcular rendimientos.")

    if issues:
        return issues

    start = prices.index.min().date()
    end = prices.index.max().date()
    return [
        f"{name}: OK. Observaciones={len(prices)}, inicio={start}, fin={end}, "
        f"precio_min={prices.min():.2f}, precio_max={prices.max():.2f}"
    ]


def main() -> None:
    print("Validando archivos en data/raw...\n")
    for name, path in EXPECTED_FILES.items():
        for message in validate_series(name, path):
            print(message)


if __name__ == "__main__":
    main()
