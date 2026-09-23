from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series
from econometria_financiera.multivariate import fit_var, forecast_var, impulse_response_table
from econometria_financiera.project_config import DEFAULT_FIGURE_DIR, load_series_config
from econometria_financiera.univariate import arima_forecast_frame, residual_acf_frame, summarize_univariate
from econometria_financiera.volatility import ARCH_ALPHA, arch_effects_present, fit_garch, garch_forecast_frame

FIGURE_DIR = DEFAULT_FIGURE_DIR


def save_current_figure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def plot_prices(bundles, configs) -> None:
    plt.figure(figsize=(10, 5))
    for bundle, config in zip(bundles, configs):
        plt.plot(bundle.prices.index, bundle.prices, label=config.label, linewidth=2)
    plt.title("Precios ajustados mensuales (Adj Close)")
    plt.xlabel("Fecha")
    plt.ylabel("Precio ajustado")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "price_series.png")


def plot_returns(bundles, configs) -> None:
    plt.figure(figsize=(10, 5))
    for bundle, config in zip(bundles, configs):
        plt.plot(bundle.returns.index, bundle.returns, label=config.label, linewidth=1.8)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Log-rendimientos mensuales")
    plt.xlabel("Fecha")
    plt.ylabel("Log-rendimiento")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "log_returns.png")


def plot_returns_comparison(returns_df: pd.DataFrame) -> None:
    summary = returns_df.agg(["mean", "std"]).T.rename(columns={"mean": "Media", "std": "Volatilidad"})

    ax = summary.plot(kind="bar", figsize=(8, 5))
    ax.set_title("Media y volatilidad de log-rendimientos")
    ax.set_xlabel("Serie")
    ax.set_ylabel("Log-rendimiento")
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=0)
    save_current_figure(FIGURE_DIR / "returns_comparison.png")


def plot_arima_diagnostics(bundles, univariate_results) -> None:
    diagnostics = {
        bundle.name: residual_acf_frame(pd.Series(univariate_results[bundle.name][1]["arima_model"].resid), nlags=20)
        for bundle in bundles
    }

    fig, axes = plt.subplots(1, len(diagnostics), figsize=(11, 4), sharey=True)
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for axis, (name, data) in zip(axes, diagnostics.items()):
        axis.bar(data["lag"], data["acf"], width=0.7)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(f"ACF residuos ARIMA log-precio - {name}")
        axis.set_xlabel("Rezago")
        axis.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Autocorrelacion")
    save_current_figure(FIGURE_DIR / "arima_residual_acf.png")


def plot_arima_forecast(bundles, univariate_results) -> None:
    forecasts = {
        bundle.name: arima_forecast_frame(univariate_results[bundle.name][1]["arima_model"], steps=10)
        for bundle in bundles
    }

    fig, axes = plt.subplots(1, len(forecasts), figsize=(11, 4))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for axis, (name, forecast) in zip(axes, forecasts.items()):
        axis.plot(forecast["step"], forecast["mean_price"], marker="o", label="Precio reconstruido")
        axis.fill_between(
            forecast["step"],
            forecast["price_ci_lower"],
            forecast["price_ci_upper"],
            alpha=0.2,
            label="IC 95% (precio)",
        )
        axis.set_title(f"Pronostico ARIMA log-precio - {name}")
        axis.set_xlabel("Horizonte")
        axis.set_ylabel("Precio reconstruido (exp del log-pronostico)")
        axis.legend()
        axis.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "arima_forecast.png")


def plot_garch_forecast(bundles, configs, univariate_results) -> None:
    forecasts = []
    for bundle, config in zip(bundles, configs):
        pvalue = univariate_results[bundle.name][0].arch_test_pvalue
        if not arch_effects_present(pvalue, ARCH_ALPHA):
            print(f"GARCH no estimado para {config.name}: ARCH-LM p={pvalue:.4f}.")
            continue
        _, garch = fit_garch(bundle.returns)
        forecasts.append((config, garch_forecast_frame(garch, horizon=10)))

    if not forecasts:
        print("Sin evidencia de efectos ARCH: no se genera figura GARCH.")
        return

    plt.figure(figsize=(9, 5))
    for config, forecast in forecasts:
        plt.plot(forecast["step"], forecast["variance_forecast"], marker="o", label=config.label)
    plt.title("Pronostico de varianza GARCH(1,1)")
    plt.xlabel("Horizonte")
    plt.ylabel("Varianza condicional pronosticada")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "garch_variance_forecast.png")


def plot_var_forecast(var_model) -> None:
    forecast_df = forecast_var(var_model, steps=10)

    plt.figure(figsize=(9, 5))
    for column in var_model.names:
        plt.plot(forecast_df["step"], forecast_df[f"{column}_forecast"], marker="o", label=column)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Pronostico VAR de log-rendimientos")
    plt.xlabel("Horizonte")
    plt.ylabel("Log-rendimiento pronosticado")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "var_forecast.png")


def plot_impulse_response(var_model) -> None:
    if var_model.k_ar == 0:
        print("VAR(0): sin dinamica de rezagos; se omite la figura impulso-respuesta.")
        return

    irf = impulse_response_table(var_model, steps=10)
    combinations = irf.groupby(["impulse", "response"], sort=False)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    axes = axes.flatten()

    for axis, ((impulse, response), data) in zip(axes, combinations):
        axis.plot(data["step"], data["effect"], marker="o", linewidth=1.8, label="IRF (Cholesky)")
        axis.fill_between(data["step"], data["ci_lower"], data["ci_upper"], alpha=0.2, label="IC 95%")
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(f"Choque {impulse} -> respuesta {response}")
        axis.set_xlabel("Horizonte")
        axis.set_ylabel("Efecto")
        axis.legend(fontsize=7)
        axis.grid(alpha=0.25)

    fig.suptitle("Funciones impulso-respuesta del VAR (identificacion Cholesky)", y=1.02)
    save_current_figure(FIGURE_DIR / "impulse_response.png")


def main() -> None:
    series_config = load_series_config()
    bundles = [load_price_series(item.resolved_output, item.name) for item in series_config]
    returns_df = combine_returns(*bundles)
    univariate_results = {
        bundle.name: summarize_univariate(bundle.name, bundle.log_prices, bundle.returns) for bundle in bundles
    }
    _, var_model = fit_var(returns_df)

    plot_prices(bundles, series_config)
    plot_returns(bundles, series_config)
    plot_returns_comparison(returns_df)
    plot_arima_diagnostics(bundles, univariate_results)
    plot_arima_forecast(bundles, univariate_results)
    plot_garch_forecast(bundles, series_config, univariate_results)
    plot_var_forecast(var_model)
    plot_impulse_response(var_model)

    print(f"Figuras generadas en {FIGURE_DIR}")


if __name__ == "__main__":
    main()
