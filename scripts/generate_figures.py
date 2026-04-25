from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series
from econometria_financiera.multivariate import fit_var, impulse_response_table
from econometria_financiera.volatility import fit_garch, garch_forecast_frame


RAW_DIR = Path("data/raw")
FIGURE_DIR = Path("docs/figures")


def save_current_figure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def plot_prices(bbva, santander) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(bbva.prices.index, bbva.prices, label="BBVA.MC", linewidth=2)
    plt.plot(santander.prices.index, santander.prices, label="SAN.MC", linewidth=2)
    plt.title("Precios de cierre mensuales")
    plt.xlabel("Fecha")
    plt.ylabel("Precio ajustado")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "price_series.png")


def plot_returns(bbva, santander) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(bbva.returns.index, bbva.returns, label="BBVA.MC", linewidth=1.8)
    plt.plot(santander.returns.index, santander.returns, label="SAN.MC", linewidth=1.8)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Rendimientos logaritmicos mensuales")
    plt.xlabel("Fecha")
    plt.ylabel("Rendimiento logaritmico")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "log_returns.png")


def plot_garch_forecast(bbva, santander) -> None:
    _, bbva_garch = fit_garch(bbva.returns)
    _, santander_garch = fit_garch(santander.returns)
    bbva_forecast = garch_forecast_frame(bbva_garch, horizon=10)
    santander_forecast = garch_forecast_frame(santander_garch, horizon=10)

    plt.figure(figsize=(9, 5))
    plt.plot(bbva_forecast["step"], bbva_forecast["variance_forecast"], marker="o", label="BBVA.MC")
    plt.plot(santander_forecast["step"], santander_forecast["variance_forecast"], marker="o", label="SAN.MC")
    plt.title("Pronostico de varianza GARCH(1,1)")
    plt.xlabel("Horizonte")
    plt.ylabel("Varianza condicional pronosticada")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "garch_variance_forecast.png")


def plot_var_forecast(var_model) -> None:
    lagged_values = var_model.endog[-var_model.k_ar :]
    forecast = var_model.forecast(y=lagged_values, steps=10)
    forecast_df = pd.DataFrame(forecast, columns=var_model.names)
    forecast_df.insert(0, "step", range(1, len(forecast_df) + 1))

    plt.figure(figsize=(9, 5))
    for column in var_model.names:
        plt.plot(forecast_df["step"], forecast_df[column], marker="o", label=column)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Pronostico VAR de rendimientos")
    plt.xlabel("Horizonte")
    plt.ylabel("Rendimiento pronosticado")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current_figure(FIGURE_DIR / "var_forecast.png")


def plot_impulse_response(var_model) -> None:
    irf = impulse_response_table(var_model, steps=10)
    combinations = irf.groupby(["impulse", "response"])

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    axes = axes.flatten()

    for axis, ((impulse, response), data) in zip(axes, combinations):
        axis.plot(data["step"], data["effect"], marker="o", linewidth=1.8)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(f"Choque {impulse} -> respuesta {response}")
        axis.set_xlabel("Horizonte")
        axis.set_ylabel("Efecto")
        axis.grid(alpha=0.25)

    fig.suptitle("Funciones impulso-respuesta del VAR", y=1.02)
    save_current_figure(FIGURE_DIR / "impulse_response.png")


def main() -> None:
    bbva = load_price_series(RAW_DIR / "BBVA.csv", "BBVA")
    santander = load_price_series(RAW_DIR / "SAN.csv", "Santander")
    returns_df = combine_returns(bbva, santander)
    _, var_model = fit_var(returns_df)

    plot_prices(bbva, santander)
    plot_returns(bbva, santander)
    plot_garch_forecast(bbva, santander)
    plot_var_forecast(var_model)
    plot_impulse_response(var_model)

    print(f"Figuras generadas en {FIGURE_DIR}")


if __name__ == "__main__":
    main()
