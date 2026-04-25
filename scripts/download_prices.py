from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yfinance as yf


CONFIG_PATH = Path("config/data_sources.json")


def normalize_prices(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        raise ValueError("la descarga no devolvio observaciones")

    if isinstance(frame.columns, pd.MultiIndex):
        frame = frame.copy()
        frame.columns = frame.columns.get_level_values(0)

    price_column = "Adj Close" if "Adj Close" in frame.columns else "Close"
    prices = (
        frame.reset_index()[["Date", price_column]]
        .rename(columns={"Date": "Fecha", price_column: "Cierre"})
        .assign(Fecha=lambda data: pd.to_datetime(data["Fecha"]).dt.date)
        .dropna()
    )

    if prices.empty:
        raise ValueError("no hay precios validos despues de limpiar la descarga")

    return prices


def download_one(name: str, ticker: str, output: str, start: str, end: str, interval: str) -> None:
    print(f"Descargando {name} ({ticker})...")
    raw = yf.download(
        tickers=ticker,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )
    prices = normalize_prices(raw)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(output_path, index=False)
    print(f"Guardado: {output_path} ({len(prices)} observaciones)")


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    start = config["start"]
    end = config["end"]
    interval = config.get("interval", "1mo")

    for item in config["series"]:
        download_one(
            name=item["name"],
            ticker=item["ticker"],
            output=item["output"],
            start=start,
            end=end,
            interval=interval,
        )


if __name__ == "__main__":
    main()
