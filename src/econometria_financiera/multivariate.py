from __future__ import annotations

from dataclasses import dataclass, asdict

import pandas as pd
from statsmodels.tsa.api import VAR


@dataclass
class VarSummary:
    selected_lag: int
    aic: float
    bic: float


def fit_var(returns_df: pd.DataFrame, maxlags: int = 6):
    model = VAR(returns_df.dropna())
    order_results = model.select_order(maxlags=maxlags)
    selected_lag = order_results.selected_orders.get("aic") or 1
    selected_lag = max(1, int(selected_lag))
    fitted = model.fit(maxlags=selected_lag)
    summary = VarSummary(selected_lag=int(selected_lag), aic=float(fitted.aic), bic=float(fitted.bic))
    return summary, fitted


def granger_causality(fitted_var, caused: str, causing: list[str]) -> dict[str, float]:
    result = fitted_var.test_causality(caused=caused, causing=causing, kind="f")
    return {
        "test_statistic": float(result.test_statistic),
        "pvalue": float(result.pvalue),
    }


def forecast_var(fitted_var, steps: int = 5) -> pd.DataFrame:
    lagged_values = fitted_var.endog[-fitted_var.k_ar :]
    forecast = fitted_var.forecast(y=lagged_values, steps=steps)
    columns = [f"{name}_forecast" for name in fitted_var.names]
    forecast_df = pd.DataFrame(forecast, columns=columns)
    forecast_df.insert(0, "step", range(1, steps + 1))
    return forecast_df


def impulse_response_table(fitted_var, steps: int = 5) -> pd.DataFrame:
    irf = fitted_var.irf(steps)
    rows = []
    for impulse_idx, impulse_name in enumerate(fitted_var.names):
        for response_idx, response_name in enumerate(fitted_var.names):
            for step in range(steps + 1):
                rows.append(
                    {
                        "impulse": impulse_name,
                        "response": response_name,
                        "step": step,
                        "effect": float(irf.irfs[step, response_idx, impulse_idx]),
                    }
                )
    return pd.DataFrame(rows)


def serialize_var_summary(summary: VarSummary) -> dict[str, float]:
    return asdict(summary)
