from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series, preview_dataframe
from econometria_financiera.io import write_csv
from econometria_financiera.multivariate import forecast_var, fit_var, granger_causality, impulse_response_table
from econometria_financiera.project_config import load_series_config
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
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    series_config = load_series_config()
    bundles = [load_price_series(item.output, item.name) for item in series_config]

    write_csv(preview_dataframe(*bundles), output_dir / "series_preview.csv")

    univariate_results = [
        summarize_univariate(bundle.name, bundle.prices, bundle.returns)
        for bundle in bundles
    ]
    univariate_summaries = [summary for summary, _ in univariate_results]
    univariate_details = {
        config.name: details
        for config, (_, details) in zip(series_config, univariate_results)
    }

    univariate_df = pd.DataFrame([summary.__dict__ for summary in univariate_summaries])
    write_csv(univariate_df, output_dir / "univariate_summary.csv")

    for config, (_, details) in zip(series_config, univariate_results):
        write_csv(
            arima_forecast_frame(details["arima_model"], steps=10),
            output_dir / f"{config.slug}_arima_forecast.csv",
        )

    garch_results = [fit_garch(bundle.returns) for bundle in bundles]
    garch_summaries = [summary for summary, _ in garch_results]

    for config, (_, model) in zip(series_config, garch_results):
        write_csv(
            garch_forecast_frame(model, horizon=10),
            output_dir / f"{config.slug}_garch_forecast.csv",
        )

    returns_df = combine_returns(*bundles)
    write_csv(returns_comparison_frame(returns_df), output_dir / "returns_comparison.csv")
    write_csv(returns_df.corr(), output_dir / "returns_correlation.csv", index=True)
    var_summary, var_model = fit_var(returns_df)
    write_csv(forecast_var(var_model, steps=10), output_dir / "var_forecast.csv")
    write_csv(impulse_response_table(var_model, steps=10), output_dir / "impulse_response.csv")

    first_name, second_name = [bundle.name for bundle in bundles]
    granger = {
        f"{first_name}_to_{second_name}": granger_causality(var_model, caused=second_name, causing=[first_name]),
        f"{second_name}_to_{first_name}": granger_causality(var_model, caused=first_name, causing=[second_name]),
    }

    report = build_markdown_report(
        {
            "series": series_config,
            "univariate": univariate_summaries,
            "garch": garch_summaries,
            "var_summary": var_summary,
            "granger": granger,
            "details": univariate_details,
        }
    )
    write_report(output_dir / "analysis_report.md", report)

    print(f"Analisis completado. Revisa la carpeta {output_dir}/.")


if __name__ == "__main__":
    main(parse_args().output_dir)
