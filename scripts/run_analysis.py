from __future__ import annotations

from pathlib import Path

import pandas as pd

from econometria_financiera.data import combine_returns, load_price_series, preview_dataframe
from econometria_financiera.multivariate import forecast_var, fit_var, granger_causality, impulse_response_table
from econometria_financiera.reporting import build_markdown_report, write_report
from econometria_financiera.univariate import arima_forecast_frame, returns_comparison_frame, summarize_univariate
from econometria_financiera.volatility import fit_garch, garch_forecast_frame


def main() -> None:
    raw_dir = Path("data/raw")
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    bbva_bundle = load_price_series(raw_dir / "BBVA.csv", "BBVA")
    san_bundle = load_price_series(raw_dir / "SAN.csv", "Santander")

    preview_dataframe(bbva_bundle, san_bundle).to_csv(output_dir / "series_preview.csv", index=False)

    bbva_summary, bbva_details = summarize_univariate("BBVA", bbva_bundle.prices, bbva_bundle.returns)
    san_summary, san_details = summarize_univariate("Santander", san_bundle.prices, san_bundle.returns)

    univariate_df = pd.DataFrame([bbva_summary.__dict__, san_summary.__dict__])
    univariate_df.to_csv(output_dir / "univariate_summary.csv", index=False)
    arima_forecast_frame(bbva_details["arima_model"], steps=10).to_csv(output_dir / "bbva_arima_forecast.csv", index=False)
    arima_forecast_frame(san_details["arima_model"], steps=10).to_csv(output_dir / "san_arima_forecast.csv", index=False)

    bbva_garch_summary, bbva_garch_model = fit_garch(bbva_bundle.returns)
    san_garch_summary, san_garch_model = fit_garch(san_bundle.returns)

    garch_forecast_frame(bbva_garch_model, horizon=10).to_csv(output_dir / "bbva_garch_forecast.csv", index=False)
    garch_forecast_frame(san_garch_model, horizon=10).to_csv(output_dir / "san_garch_forecast.csv", index=False)

    returns_df = combine_returns(bbva_bundle, san_bundle)
    returns_comparison_frame(returns_df).to_csv(output_dir / "returns_comparison.csv", index=False)
    returns_df.corr().to_csv(output_dir / "returns_correlation.csv")
    var_summary, var_model = fit_var(returns_df)
    forecast_var(var_model, steps=10).to_csv(output_dir / "var_forecast.csv", index=False)
    impulse_response_table(var_model, steps=10).to_csv(output_dir / "impulse_response.csv", index=False)

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

    print("Analisis completado. Revisa la carpeta outputs/.")


if __name__ == "__main__":
    main()
