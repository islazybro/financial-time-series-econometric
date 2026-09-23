from __future__ import annotations

import numpy as np
import pandas as pd

from econometria_financiera.data import load_price_series
from econometria_financiera.univariate import (
    arima_forecast_frame,
    kpss_test,
    select_arima,
    select_differentiation_order,
    summarize_univariate,
)


def _write_prices(tmp_path, values: list[float]) -> object:
    path = tmp_path / "prices.csv"
    pd.DataFrame(
        {
            "Fecha": pd.date_range("2020-01-01", periods=len(values), freq="MS"),
            "Cierre": values,
        }
    ).to_csv(path, index=False)
    return path


def test_log_prices_are_natural_log_and_finite(tmp_path):
    values = [100.0, 110.0, 99.0, 121.0, 115.5]
    bundle = load_price_series(_write_prices(tmp_path, values), "Demo")

    log_prices = bundle.log_prices

    assert np.allclose(log_prices.to_numpy(), np.log(values))
    assert np.isfinite(log_prices.to_numpy()).all()
    assert (bundle.prices.to_numpy() > 0).all()


def test_select_differentiation_order_for_random_walk():
    rng = np.random.default_rng(0)
    walk = pd.Series(100 + np.cumsum(rng.normal(size=200)))

    assert select_differentiation_order(walk) == 1


def test_summarize_univariate_models_the_log_price_series(tmp_path):
    rng = np.random.default_rng(1)
    prices = 10 * np.exp(np.cumsum(rng.normal(scale=0.05, size=120)))
    bundle = load_price_series(_write_prices(tmp_path, list(prices)), "Demo")

    log_prices = bundle.log_prices
    expected_d = select_differentiation_order(log_prices)
    expected_selection, _ = select_arima(log_prices, d=expected_d)

    summary, _ = summarize_univariate("Demo", log_prices, bundle.returns)

    assert summary.selected_d == expected_d
    assert summary.selected_arima == str(expected_selection.order)
    assert np.isclose(summary.arima_aic, expected_selection.aic)


def test_arima_forecast_price_reconstruction_is_positive(tmp_path):
    values = [10.0, 10.5, 10.2, 11.0, 10.8, 11.5, 11.2, 12.0, 11.7, 12.3,
              12.0, 12.8, 12.5, 13.1, 12.9, 13.5, 13.2, 13.9, 13.6, 14.2]
    bundle = load_price_series(_write_prices(tmp_path, values), "Demo")

    log_prices = bundle.log_prices
    d = select_differentiation_order(log_prices)
    _, model = select_arima(log_prices, d=d)

    frame = arima_forecast_frame(model, steps=5)

    assert (frame["mean_price"] > 0).all()
    assert (frame["price_ci_lower"] > 0).all()
    assert (frame["price_ci_upper"] >= frame["price_ci_lower"]).all()
    assert np.allclose(frame["mean_price"], np.exp(frame["mean_log"]))


def test_kpss_stationary_series_does_not_reject():
    rng = np.random.default_rng(0)
    stationary = pd.Series(rng.normal(size=200))

    result = kpss_test(stationary)

    assert result.pvalue >= 0.05
    assert result.null_hypothesis == "la serie es estacionaria"
    assert result.used_lags >= 0
    assert isinstance(result.pvalue_censured, bool)


def test_kpss_random_walk_rejects_stationarity():
    rng = np.random.default_rng(0)
    walk = pd.Series(np.cumsum(rng.normal(size=200)))

    result = kpss_test(walk)

    assert result.pvalue < 0.05
    assert "estacionariedad" in result.interpretation
