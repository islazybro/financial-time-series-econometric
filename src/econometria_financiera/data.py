from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


DATE_COLUMNS = ("Fecha", "Date")
PRICE_COLUMNS = ("Cierre", "Close", "Adj Close", "Precio")


@dataclass
class SeriesBundle:
    name: str
    prices: pd.Series
    returns: pd.Series


def _find_column(columns: list[str], candidates: tuple[str, ...]) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"No se encontro ninguna columna valida entre: {candidates}")


def load_price_series(csv_path: str | Path, series_name: str) -> SeriesBundle:
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    date_col = _find_column(df.columns.tolist(), DATE_COLUMNS)
    price_col = _find_column(df.columns.tolist(), PRICE_COLUMNS)

    cleaned = (
        df[[date_col, price_col]]
        .rename(columns={date_col: "date", price_col: "close"})
        .assign(
            date=lambda frame: pd.to_datetime(frame["date"]),
            close=lambda frame: pd.to_numeric(frame["close"], errors="coerce"),
        )
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")
        .reset_index(drop=True)
    )

    prices = cleaned.set_index("date")["close"].astype(float)
    inferred_frequency = pd.infer_freq(prices.index)
    if inferred_frequency is not None:
        prices = prices.asfreq(inferred_frequency)

    returns = np.log(prices / prices.shift(1)).dropna()
    returns.name = f"{series_name}_returns"
    prices.name = series_name
    return SeriesBundle(name=series_name, prices=prices, returns=returns)


def combine_returns(*bundles: SeriesBundle) -> pd.DataFrame:
    data = pd.concat([bundle.returns.rename(bundle.name) for bundle in bundles], axis=1).dropna()
    return data


def preview_dataframe(*bundles: SeriesBundle) -> pd.DataFrame:
    frames = []
    for bundle in bundles:
        frame = pd.DataFrame(
            {
                "date": bundle.prices.index,
                "series": bundle.name,
                "price": bundle.prices.values,
            }
        )
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)
