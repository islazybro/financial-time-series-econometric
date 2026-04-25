from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


CONFIG_PATH = Path("config/data_sources.json")


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


def load_series_config(config_path: str | Path = CONFIG_PATH) -> list[SeriesConfig]:
    config_path = Path(config_path)
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
    return series
