from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def simulated_prices(seed: int, name: str) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2019-01-31", periods=84, freq="ME")
    shocks = rng.normal(loc=0.01, scale=0.06, size=len(dates))
    level = 100 * np.exp(np.cumsum(shocks))
    return pd.DataFrame({"Fecha": dates, "Cierre": np.round(level, 2), "Activo": name})


def main() -> None:
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    bbva = simulated_prices(seed=42, name="BBVA").drop(columns="Activo")
    san = simulated_prices(seed=7, name="SAN").drop(columns="Activo")

    bbva.to_csv(output_dir / "BBVA.csv", index=False)
    san.to_csv(output_dir / "SAN.csv", index=False)

    print("Datos de ejemplo creados en data/raw/BBVA.csv y data/raw/SAN.csv")


if __name__ == "__main__":
    main()
