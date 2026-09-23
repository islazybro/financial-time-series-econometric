from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass
from itertools import product

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tools.sm_exceptions import ConvergenceWarning, InterpolationWarning
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from statsmodels.tsa.stattools import acf, adfuller, kpss

ADF_NULL_HYPOTHESIS = "la serie tiene raiz unitaria (no es estacionaria)"
KPSS_NULL_HYPOTHESIS = "la serie es estacionaria"


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
class KPSSResult:
    statistic: float
    pvalue: float
    used_lags: int
    null_hypothesis: str
    interpretation: str
    pvalue_censured: bool


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
    selected_d: int
    selected_arima: str
    arima_aic: float
    arima_bic: float
    kpss_level_statistic: float
    kpss_level_lags: int
    kpss_level_pvalue: float
    kpss_level_censured: bool
    kpss_return_statistic: float
    kpss_return_lags: int
    kpss_return_pvalue: float
    kpss_return_censured: bool
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


def kpss_test(series: pd.Series, regression: str = "c", nlags: str | int = "auto", alpha: float = 0.05) -> KPSSResult:
    """Prueba KPSS de estacionariedad (H0: la serie es estacionaria).

    Complementa al ADF: el ADF contrasta H0 = raiz unitaria mientras que el
    KPSS contrasta H0 = estacionariedad. Si el p-valor queda en el borde de la
    tabla de statsmodels, se marca `pvalue_censured` y se interpreta con cautela.
    """
    cleaned = series.dropna().astype(float)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InterpolationWarning)
        warnings.simplefilter("always", UserWarning)
        statistic, pvalue, used_lags, _ = kpss(cleaned, regression=regression, nlags=nlags)

    pvalue = float(pvalue)
    censured = any(issubclass(item.category, InterpolationWarning) for item in caught)

    if censured:
        if pvalue < alpha:
            interpretation = (
                "p-valor en el limite inferior tabulado: evidencia extrema contra H0 "
                "(se rechaza estacionariedad)."
            )
        else:
            interpretation = (
                "p-valor en el limite superior tabulado: evidencia extrema a favor de H0 "
                "(no se rechaza estacionariedad)."
            )
    elif pvalue < alpha:
        interpretation = "Se rechaza H0 al 5%: evidencia contra la estacionariedad."
    else:
        interpretation = "No se rechaza H0 al 5%: sin evidencia suficiente contra la estacionariedad."

    return KPSSResult(
        statistic=float(statistic),
        pvalue=pvalue,
        used_lags=int(used_lags),
        null_hypothesis=KPSS_NULL_HYPOTHESIS,
        interpretation=interpretation,
        pvalue_censured=censured,
    )


def select_differentiation_order(series: pd.Series, max_d: int = 2, alpha: float = 0.05) -> int:
    """Determina el orden de integracion d aplicando ADF de forma secuencial.

    A diferencia de comparar AIC entre grados de diferenciacion (no comparables
    porque cambia el dato modelado), aqui se usa la regla estandar de raiz
    unitaria: se diferencia hasta que el ADF rechaza la hipotesis nula.
    """
    current = series.dropna().astype(float)
    if current.empty or adf_test(current).pvalue < alpha:
        return 0
    for order in range(1, max_d + 1):
        current = current.diff().dropna()
        if current.empty or adf_test(current).pvalue < alpha:
            return order
    return max_d


def select_arima(
    series: pd.Series,
    d: int,
    p_values: range = range(0, 3),
    q_values: range = range(0, 3),
) -> tuple[ArimaSelection, ARIMAResults]:
    best_model = None
    best_selection = None
    cleaned = series.dropna().astype(float)

    for p, q in product(p_values, q_values):
        order = (p, d, q)
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


def arima_forecast_frame(fitted_model: ARIMAResults, steps: int = 10) -> pd.DataFrame:
    forecast = fitted_model.get_forecast(steps=steps)
    summary = forecast.summary_frame(alpha=0.05).reset_index(drop=True)
    frame = pd.DataFrame(
        {
            "step": range(1, steps + 1),
            "mean_log": summary["mean"],
            "mean_log_ci_lower": summary["mean_ci_lower"],
            "mean_log_ci_upper": summary["mean_ci_upper"],
        }
    )
    frame["mean_price"] = np.exp(frame["mean_log"])
    frame["price_ci_lower"] = np.exp(frame["mean_log_ci_lower"])
    frame["price_ci_upper"] = np.exp(frame["mean_log_ci_upper"])
    return frame


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


def summarize_univariate(
    series_name: str, log_price_series: pd.Series, return_series: pd.Series
) -> tuple[UnivariateSummary, dict[str, object]]:
    adf_log_price = adf_test(log_price_series)
    adf_return = adf_test(return_series)
    kpss_log_price = kpss_test(log_price_series)
    kpss_return = kpss_test(return_series)
    selected_d = select_differentiation_order(log_price_series)
    arima_selection, arima_model = select_arima(log_price_series, d=selected_d)
    residuals = pd.Series(arima_model.resid)
    ljung_box_result = ljung_box_test(residuals)
    demeaned_returns = return_series.dropna() - float(return_series.dropna().mean())
    arch_result = arch_lm_test(demeaned_returns)

    summary = UnivariateSummary(
        series=series_name,
        adf_level_pvalue=adf_log_price.pvalue,
        adf_return_pvalue=adf_return.pvalue,
        selected_d=selected_d,
        selected_arima=str(arima_selection.order),
        arima_aic=arima_selection.aic,
        arima_bic=arima_selection.bic,
        kpss_level_statistic=kpss_log_price.statistic,
        kpss_level_lags=kpss_log_price.used_lags,
        kpss_level_pvalue=kpss_log_price.pvalue,
        kpss_level_censured=kpss_log_price.pvalue_censured,
        kpss_return_statistic=kpss_return.statistic,
        kpss_return_lags=kpss_return.used_lags,
        kpss_return_pvalue=kpss_return.pvalue,
        kpss_return_censured=kpss_return.pvalue_censured,
        arch_test_pvalue=arch_result["lm_pvalue"],
        ljung_box_pvalue=ljung_box_result["lb_pvalue"],
    )

    details = {
        "adf_log_price": asdict(adf_log_price),
        "adf_return": asdict(adf_return),
        "kpss_log_price": asdict(kpss_log_price),
        "kpss_return": asdict(kpss_return),
        "arima_selection": asdict(arima_selection),
        "arch_lm": arch_result,
        "ljung_box": ljung_box_result,
        "arima_model": arima_model,
    }
    return summary, details
