from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import het_arch
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.var_model import VARResults

IRF_LAG_CRITERION = "aic"
WHITENESS_LAGS = 10
ARCH_LAGS = 5
IRF_SIGNIF = 0.05
Z_95 = 1.959963984540054


@dataclass
class VarSummary:
    selected_lag: int
    lag_criterion: str
    selected_orders: dict[str, int]
    aic: float
    bic: float
    hqic: float
    fpe: float
    is_stable: bool
    min_root_modulus: float
    roots: list[complex]


def fit_var(returns_df: pd.DataFrame, maxlags: int = 6) -> tuple[VarSummary, VARResults]:
    """Estima el VAR seleccionando el rezago por AIC (sin imponer minimo de 1).

    Se conserva el valor seleccionado aunque sea 0: un VAR(0) solo tiene
    terminos constantes y sigue siendo una especificacion valida.
    """
    model = VAR(returns_df.dropna())
    order_results = model.select_order(maxlags=maxlags)
    selected_orders = {name: int(value) for name, value in order_results.selected_orders.items()}
    selected_lag = selected_orders[IRF_LAG_CRITERION]
    fitted = model.fit(maxlags=selected_lag)

    root_moduli = np.abs(fitted.roots)
    summary = VarSummary(
        selected_lag=selected_lag,
        lag_criterion=IRF_LAG_CRITERION.upper(),
        selected_orders=selected_orders,
        aic=float(fitted.aic),
        bic=float(fitted.bic),
        hqic=float(fitted.hqic),
        fpe=float(fitted.fpe),
        is_stable=bool(root_moduli.size > 0 and np.all(root_moduli > 1)),
        min_root_modulus=float(np.min(root_moduli)) if root_moduli.size else float("nan"),
        roots=[complex(root) for root in fitted.roots],
    )
    return summary, fitted


def var_residual_diagnostics(
    fitted, whiteness_lags: int = WHITENESS_LAGS, arch_lags: int = ARCH_LAGS
) -> dict[str, object]:
    """Diagnostico de residuos del VAR: autocorrelacion, normalidad y ARCH."""
    whiteness = fitted.test_whiteness(nlags=whiteness_lags)
    normality = fitted.test_normality()

    residuals = np.asarray(fitted.resid)
    arch_pvalues = {}
    for index, name in enumerate(fitted.names):
        _, pvalue, _, _ = het_arch(residuals[:, index], nlags=arch_lags)
        arch_pvalues[name] = float(pvalue)

    return {
        "whiteness_lags": int(whiteness_lags),
        "whiteness_stat": float(whiteness.test_statistic),
        "whiteness_pvalue": float(whiteness.pvalue),
        "whiteness_df": int(whiteness.df),
        "normality_stat": float(normality.test_statistic),
        "normality_pvalue": float(normality.pvalue),
        "arch_lags": int(arch_lags),
        "arch_pvalues": arch_pvalues,
    }


def irf_identification_note(fitted_var) -> str:
    names = ", ".join(fitted_var.names)
    return (
        "Identificacion de Cholesky (ortogonalizacion recursiva). "
        f"Orden de variables: [{names}]. Bandas de confianza al 95% aproximadas "
        "a partir del error estandar asintotico de las IRF."
    )


def granger_causality(fitted_var, caused: str, causing: list[str]) -> dict[str, object]:
    result = fitted_var.test_causality(caused=caused, causing=causing, kind="f")
    pvalue = float(result.pvalue)
    causing_label = " y ".join(causing)
    rejected = pvalue < 0.05
    return {
        "null_hypothesis": f"{causing_label} no causa-Granger a {caused}",
        "test_statistic": float(result.test_statistic),
        "pvalue": pvalue,
        "conclusion": (
            f"Se rechaza H0 al 5%: {causing_label} aporta informacion predictiva sobre {caused}."
            if rejected
            else f"No se rechaza H0 al 5%: sin evidencia de causalidad de Granger de {causing_label} hacia {caused}."
        ),
    }


def forecast_var(fitted_var, steps: int = 5) -> pd.DataFrame:
    if fitted_var.k_ar == 0:
        intercept = np.asarray(fitted_var.intercept, dtype=float)
        forecast = np.tile(intercept, (steps, 1))
    else:
        lagged_values = fitted_var.endog[-fitted_var.k_ar :]
        forecast = fitted_var.forecast(y=lagged_values, steps=steps)
    columns = [f"{name}_forecast" for name in fitted_var.names]
    forecast_df = pd.DataFrame(forecast, columns=columns)
    forecast_df.insert(0, "step", range(1, steps + 1))
    return forecast_df


def impulse_response_table(fitted_var, steps: int = 5, signif: float = IRF_SIGNIF) -> pd.DataFrame:
    if fitted_var.k_ar == 0:
        raise ValueError("Las IRF requieren al menos un rezago: VAR(k) con k >= 1.")

    irf = fitted_var.irf(steps)
    effects = irf.orth_irfs
    standard_errors = irf.stderr(orth=True)

    rows = []
    for impulse_idx, impulse_name in enumerate(fitted_var.names):
        for response_idx, response_name in enumerate(fitted_var.names):
            for step in range(steps + 1):
                effect = float(effects[step, response_idx, impulse_idx])
                std_error = float(standard_errors[step, response_idx, impulse_idx])
                rows.append(
                    {
                        "impulse": impulse_name,
                        "response": response_name,
                        "step": step,
                        "effect": effect,
                        "std_error": std_error,
                        "ci_lower": effect - Z_95 * std_error,
                        "ci_upper": effect + Z_95 * std_error,
                    }
                )
    return pd.DataFrame(rows)
