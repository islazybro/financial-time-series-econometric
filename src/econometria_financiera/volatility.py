from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from arch import arch_model

ARCH_ALPHA = 0.05


@dataclass
class GarchSummary:
    omega: float
    alpha_1: float
    beta_1: float
    persistence: float
    aic: float
    bic: float


def arch_effects_present(arch_pvalue: float, alpha: float = ARCH_ALPHA) -> bool:
    """Indica si la prueba ARCH-LM justifica estimar un modelo GARCH."""
    return arch_pvalue < alpha


def fit_garch(returns: pd.Series):
    model = arch_model(returns.dropna() * 100, mean="Constant", vol="GARCH", p=1, q=1, dist="normal")
    fitted = model.fit(disp="off")
    params = fitted.params
    alpha_1 = float(params.get("alpha[1]", float("nan")))
    beta_1 = float(params.get("beta[1]", float("nan")))
    summary = GarchSummary(
        omega=float(params.get("omega", float("nan"))),
        alpha_1=alpha_1,
        beta_1=beta_1,
        persistence=alpha_1 + beta_1,
        aic=float(fitted.aic),
        bic=float(fitted.bic),
    )
    return summary, fitted


def garch_forecast_frame(fitted_model, horizon: int = 5) -> pd.DataFrame:
    forecast = fitted_model.forecast(horizon=horizon)
    variance = forecast.variance.iloc[-1]
    return pd.DataFrame(
        {
            "step": range(1, horizon + 1),
            "variance_forecast": variance.values,
        }
    )
