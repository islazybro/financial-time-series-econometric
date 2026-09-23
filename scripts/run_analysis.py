from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series, preview_dataframe
from econometria_financiera.io import clean_analysis_outputs, write_csv
from econometria_financiera.multivariate import (
    fit_var,
    forecast_var,
    granger_causality,
    impulse_response_table,
    irf_identification_note,
    var_residual_diagnostics,
)
from econometria_financiera.project_config import DEFAULT_OUTPUT_DIR, load_data_config, resolve_path
from econometria_financiera.reporting import build_markdown_report, write_report
from econometria_financiera.univariate import arima_forecast_frame, returns_comparison_frame, summarize_univariate
from econometria_financiera.volatility import ARCH_ALPHA, arch_effects_present, fit_garch, garch_forecast_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta el analisis econometrico del proyecto.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Carpeta donde se guardan reportes y CSV generados.",
    )
    return parser.parse_args()


def main(output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    output_dir = resolve_path(output_dir)
    clean_analysis_outputs(output_dir)

    data_config = load_data_config()
    series_config = data_config.series
    bundles = [load_price_series(item.resolved_output, item.name) for item in series_config]

    write_csv(preview_dataframe(*bundles), output_dir / "series_preview.csv")

    univariate_results = [
        summarize_univariate(bundle.name, bundle.log_prices, bundle.returns)
        for bundle in bundles
    ]
    univariate_summaries = [summary for summary, _ in univariate_results]

    univariate_df = pd.DataFrame([summary.__dict__ for summary in univariate_summaries])
    write_csv(univariate_df, output_dir / "univariate_summary.csv")

    for config, (_, details) in zip(series_config, univariate_results):
        write_csv(
            arima_forecast_frame(details["arima_model"], steps=10),
            output_dir / f"{config.slug}_arima_forecast.csv",
        )

    garch_results = []
    for bundle, summary in zip(bundles, univariate_summaries):
        if arch_effects_present(summary.arch_test_pvalue):
            garch_results.append(fit_garch(bundle.returns))
        else:
            print(
                f"GARCH no estimado para {bundle.name}: ARCH-LM p={summary.arch_test_pvalue:.4f} "
                f">= {ARCH_ALPHA:.2f}, no hay evidencia de efectos ARCH con media constante."
            )
            garch_results.append(None)
    garch_summaries = [result[0] if result is not None else None for result in garch_results]

    for config, result in zip(series_config, garch_results):
        if result is None:
            continue
        _, model = result
        write_csv(
            garch_forecast_frame(model, horizon=10),
            output_dir / f"{config.slug}_garch_forecast.csv",
        )

    returns_df = combine_returns(*bundles)
    write_csv(returns_comparison_frame(returns_df), output_dir / "returns_comparison.csv")
    write_csv(returns_df.corr(), output_dir / "returns_correlation.csv", index=True)
    var_summary, var_model = fit_var(returns_df)
    var_diagnostics = var_residual_diagnostics(var_model)
    write_csv(forecast_var(var_model, steps=10), output_dir / "var_forecast.csv")
    if var_model.k_ar > 0:
        write_csv(impulse_response_table(var_model, steps=10), output_dir / "impulse_response.csv")
    else:
        print("VAR(0): sin dinamica de rezagos; se omite la tabla de impulso-respuesta.")

    first_name, second_name = [bundle.name for bundle in bundles]
    granger = {
        f"{first_name}_to_{second_name}": granger_causality(var_model, caused=second_name, causing=[first_name]),
        f"{second_name}_to_{first_name}": granger_causality(var_model, caused=first_name, causing=[second_name]),
    }
    correlation = float(returns_df.corr().iloc[0, 1])

    data_info = {
        "source": data_config.source,
        "price_field": data_config.price_field,
        "interval": data_config.interval,
        "start": str(bundles[0].prices.index.min().date()),
        "end": str(bundles[0].prices.index.max().date()),
        "observations": int(len(bundles[0].prices)),
        "snapshot_date": str(pd.Timestamp.today().date()),
        "tickers": ", ".join(item.label for item in series_config),
    }

    report = build_markdown_report(
        {
            "series": series_config,
            "data_info": data_info,
            "univariate": univariate_summaries,
            "garch": garch_summaries,
            "var_summary": var_summary,
            "var_diagnostics": var_diagnostics,
            "granger": granger,
            "correlation": correlation,
            "irf_note": irf_identification_note(var_model),
        }
    )
    write_report(output_dir / "analysis_report.md", report)

    print(f"Analisis completado. Revisa la carpeta {output_dir}/.")


if __name__ == "__main__":
    main(parse_args().output_dir)
