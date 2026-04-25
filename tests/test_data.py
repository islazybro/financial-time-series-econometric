from __future__ import annotations

import numpy as np
import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series
from econometria_financiera.univariate import returns_comparison_frame


def test_load_price_series_standardizes_columns_and_returns(tmp_path):
    csv_path = tmp_path / "prices.csv"
    pd.DataFrame(
        {
            "Fecha": pd.date_range("2024-01-01", periods=4, freq="MS"),
            "Cierre": [100.0, 110.0, 121.0, 133.1],
        }
    ).to_csv(csv_path, index=False)

    bundle = load_price_series(csv_path, "Demo")

    assert bundle.name == "Demo"
    assert list(bundle.prices.round(2)) == [100.0, 110.0, 121.0, 133.1]
    assert len(bundle.returns) == 3
    assert np.isclose(bundle.returns.iloc[0], np.log(110.0 / 100.0))


def test_load_price_series_accepts_english_column_names(tmp_path):
    csv_path = tmp_path / "prices.csv"
    pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="MS"),
            "Close": [10.0, 11.0, 12.0],
        }
    ).to_csv(csv_path, index=False)

    bundle = load_price_series(csv_path, "Asset")

    assert bundle.prices.name == "Asset"
    assert bundle.returns.name == "Asset_returns"


def test_combine_returns_aligns_dates(tmp_path):
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"

    pd.DataFrame(
        {
            "Fecha": pd.date_range("2024-01-01", periods=4, freq="MS"),
            "Cierre": [100.0, 101.0, 102.0, 103.0],
        }
    ).to_csv(first_path, index=False)
    pd.DataFrame(
        {
            "Fecha": pd.date_range("2024-02-01", periods=4, freq="MS"),
            "Cierre": [50.0, 51.0, 52.0, 53.0],
        }
    ).to_csv(second_path, index=False)

    first = load_price_series(first_path, "First")
    second = load_price_series(second_path, "Second")
    combined = combine_returns(first, second)

    assert list(combined.columns) == ["First", "Second"]
    assert len(combined) == 2


def test_returns_comparison_frame_summarizes_each_series():
    returns = pd.DataFrame(
        {
            "First": [0.01, 0.02, -0.01],
            "Second": [0.03, -0.02, 0.01],
        }
    )

    summary = returns_comparison_frame(returns)

    assert list(summary["series"]) == ["First", "Second"]
    assert list(summary["observations"]) == [3, 3]
    assert "volatility" in summary.columns
