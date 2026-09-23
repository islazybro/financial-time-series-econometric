from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "data_sources.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"
DEFAULT_FIGURE_DIR = PROJECT_ROOT / "docs" / "figures"


def resolve_path(path: str | Path) -> Path:
    """Resuelve una ruta relativa contra la raiz del proyecto."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


@dataclass(frozen=True)
class SeriesConfig:
    name: str
    ticker: str
    output: Path

    @property
    def slug(self) -> str:
        value = self.ticker or self.name
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
        return slug or "series"

    @property
    def label(self) -> str:
        return self.ticker or self.name

    @property
    def resolved_output(self) -> Path:
        return resolve_path(self.output)


@dataclass(frozen=True)
class DataSourceConfig:
    start: str
    end: str
    interval: str
    source: str
    price_field: str
    series: list[SeriesConfig]


def load_data_config(config_path: str | Path = CONFIG_PATH) -> DataSourceConfig:
    config_path = resolve_path(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    series = [
        SeriesConfig(
            name=item["name"],
            ticker=item.get("ticker", item["name"]),
            output=Path(item["output"]),
        )
        for item in config["series"]
    ]
    if len(series) != 2:
        raise ValueError("Este pipeline esta disenado para comparar exactamente dos series.")
    return DataSourceConfig(
        start=config.get("start", ""),
        end=config.get("end", ""),
        interval=config.get("interval", "1mo"),
        source=config.get("source", "Yahoo Finance (yfinance)"),
        price_field=config.get("price_field", "Adj Close"),
        series=series,
    )


def load_series_config(config_path: str | Path = CONFIG_PATH) -> list[SeriesConfig]:
    return load_data_config(config_path).series
