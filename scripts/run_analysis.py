from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series, preview_dataframe
from econometria_financiera.io import write_csv
from econometria_financiera.multivariate import forecast_var, fit_var, granger_causality, impulse_response_table
from econometria_financiera.reporting import build_markdown_report, write_report
from econometria_financiera.univariate import arima_forecast_frame, returns_comparison_frame, summarize_univariate
from econometria_financiera.volatility import fit_garch, garch_forecast_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta el analisis econometrico del proyecto.")
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Carpeta donde se guardan reportes y CSV generados.",
    )
    return parser.parse_args()


def main(output_dir: str | Path = "outputs") -> None:
    raw_dir = Path("data/raw")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bbva_bundle = load_price_series(raw_dir / "BBVA.csv", "BBVA")
    san_bundle = load_price_series(raw_dir / "SAN.csv", "Santander")

    write_csv(preview_dataframe(bbva_bundle, san_bundle), output_dir / "series_preview.csv")

    bbva_summary, bbva_details = summarize_univariate("BBVA", bbva_bundle.prices, bbva_bundle.returns)
    san_summary, san_details = summarize_univariate("Santander", san_bundle.prices, san_bundle.returns)

    univariate_df = pd.DataFrame([bbva_summary.__dict__, san_summary.__dict__])
    write_csv(univariate_df, output_dir / "univariate_summary.csv")
    write_csv(arima_forecast_frame(bbva_details["arima_model"], steps=10), output_dir / "bbva_arima_forecast.csv")
    write_csv(arima_forecast_frame(san_details["arima_model"], steps=10), output_dir / "san_arima_forecast.csv")

    bbva_garch_summary, bbva_garch_model = fit_garch(bbva_bundle.returns)
    san_garch_summary, san_garch_model = fit_garch(san_bundle.returns)

    write_csv(garch_forecast_frame(bbva_garch_model, horizon=10), output_dir / "bbva_garch_forecast.csv")
    write_csv(garch_forecast_frame(san_garch_model, horizon=10), output_dir / "san_garch_forecast.csv")

    returns_df = combine_returns(bbva_bundle, san_bundle)
    write_csv(returns_comparison_frame(returns_df), output_dir / "returns_comparison.csv")
    write_csv(returns_df.corr(), output_dir / "returns_correlation.csv", index=True)
    var_summary, var_model = fit_var(returns_df)
    write_csv(forecast_var(var_model, steps=10), output_dir / "var_forecast.csv")
    write_csv(impulse_response_table(var_model, steps=10), output_dir / "impulse_response.csv")

    granger = {
        "bbva_to_san": granger_causality(var_model, caused="Santander", causing=["BBVA"]),
        "san_to_bbva": granger_causality(var_model, caused="BBVA", causing=["Santander"]),
    }

    report = build_markdown_report(
        {
            "bbva": bbva_summary,
            "san": san_summary,
            "bbva_garch": bbva_garch_summary,
            "san_garch": san_garch_summary,
            "var_summary": var_summary,
            "granger": granger,
            "details": {
                "bbva": bbva_details,
                "san": san_details,
            },
        }
    )
    write_report(output_dir / "analysis_report.md", report)

    print(f"Analisis completado. Revisa la carpeta {output_dir}/.")


if __name__ == "__main__":
    main(parse_args().output_dir)
