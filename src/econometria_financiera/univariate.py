from __future__ import annotations

import warnings
from dataclasses import dataclass, asdict
from itertools import product

import numpy as np
import pandas as pd
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.stattools import adfuller


@dataclass
class ADFResult:
    statistic: float
    pvalue: float
    used_lags: int
    nobs: int
    critical_1pct: float
    critical_5pct: float
    critical_10pct: float


@dataclass
class ArimaSelection:
    order: tuple[int, int, int]
    aic: float
    bic: float


@dataclass
class UnivariateSummary:
    series: str
    adf_level_pvalue: float
    adf_return_pvalue: float
    selected_arima: str
    arima_aic: float
    arch_test_pvalue: float
    ljung_box_pvalue: float


def adf_test(series: pd.Series, maxlag: int | None = None) -> ADFResult:
    statistic, pvalue, used_lags, nobs, critical_values, _ = adfuller(series.dropna(), maxlag=maxlag, autolag="AIC")
    return ADFResult(
        statistic=float(statistic),
        pvalue=float(pvalue),
        used_lags=int(used_lags),
        nobs=int(nobs),
        critical_1pct=float(critical_values["1%"]),
        critical_5pct=float(critical_values["5%"]),
        critical_10pct=float(critical_values["10%"]),
    )


def select_arima(series: pd.Series, p_values: range = range(0, 3), d_values: range = range(0, 3), q_values: range = range(0, 3)) -> tuple[ArimaSelection, object]:
    best_model = None
    best_selection = None
    cleaned = series.dropna().astype(float)

    for order in product(p_values, d_values, q_values):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                warnings.simplefilter("ignore", UserWarning)
                fitted = ARIMA(cleaned, order=order, trend="n").fit()
        except Exception:
            continue
        if not np.isfinite(fitted.aic):
            continue
        if best_selection is None or fitted.aic < best_selection.aic:
            best_selection = ArimaSelection(order=order, aic=float(fitted.aic), bic=float(fitted.bic))
            best_model = fitted

    if best_selection is None or best_model is None:
        raise RuntimeError("No fue posible estimar un modelo ARIMA valido.")
    return best_selection, best_model


def arch_lm_test(residuals: pd.Series, nlags: int = 5) -> dict[str, float]:
    lm_stat, lm_pvalue, f_stat, f_pvalue = het_arch(residuals.dropna(), nlags=nlags)
    return {
        "lm_stat": float(lm_stat),
        "lm_pvalue": float(lm_pvalue),
        "f_stat": float(f_stat),
        "f_pvalue": float(f_pvalue),
    }


def ljung_box_test(residuals: pd.Series, lag: int = 10) -> dict[str, float]:
    result = acorr_ljungbox(residuals.dropna(), lags=[lag], return_df=True)
    row = result.iloc[0]
    return {
        "lag": float(lag),
        "lb_stat": float(row["lb_stat"]),
        "lb_pvalue": float(row["lb_pvalue"]),
    }


def residual_acf_frame(residuals: pd.Series, nlags: int = 20) -> pd.DataFrame:
    values = acf(residuals.dropna(), nlags=nlags, fft=False)
    return pd.DataFrame({"lag": range(len(values)), "acf": values})


def arima_forecast_frame(fitted_model, steps: int = 10) -> pd.DataFrame:
    forecast = fitted_model.get_forecast(steps=steps)
    summary = forecast.summary_frame(alpha=0.05).reset_index(drop=True)
    return pd.DataFrame(
        {
            "step": range(1, steps + 1),
            "mean": summary["mean"],
            "mean_ci_lower": summary["mean_ci_lower"],
            "mean_ci_upper": summary["mean_ci_upper"],
        }
    )


def returns_comparison_frame(returns_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in returns_df.columns:
        series = returns_df[column].dropna()
        rows.append(
            {
                "series": column,
                "mean_return": float(series.mean()),
                "volatility": float(series.std()),
                "min_return": float(series.min()),
                "max_return": float(series.max()),
                "observations": int(series.count()),
            }
        )
    return pd.DataFrame(rows)


def summarize_univariate(series_name: str, level_series: pd.Series, return_series: pd.Series) -> tuple[UnivariateSummary, dict[str, object]]:
    adf_level = adf_test(level_series)
    adf_return = adf_test(return_series)
    arima_selection, arima_model = select_arima(level_series)
    residuals = pd.Series(arima_model.resid)
    arch_result = arch_lm_test(residuals)
    ljung_box_result = ljung_box_test(residuals)

    summary = UnivariateSummary(
        series=series_name,
        adf_level_pvalue=adf_level.pvalue,
        adf_return_pvalue=adf_return.pvalue,
        selected_arima=str(arima_selection.order),
        arima_aic=arima_selection.aic,
        arch_test_pvalue=arch_result["lm_pvalue"],
        ljung_box_pvalue=ljung_box_result["lb_pvalue"],
    )

    details = {
        "adf_level": asdict(adf_level),
        "adf_return": asdict(adf_return),
        "arima_selection": asdict(arima_selection),
        "arch_lm": arch_result,
        "ljung_box": ljung_box_result,
        "arima_model": arima_model,
    }
    return summary, details
