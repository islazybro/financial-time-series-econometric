from __future__ import annotations

from pathlib import Path


def build_markdown_report(context: dict) -> str:
    series = context["series"]
    univariate = context["univariate"]
    garch = context["garch"]
    var_summary = context["var_summary"]
    granger = context["granger"]

    series_names = " y ".join(item.name for item in series)
    univariate_sections = []
    for summary in univariate:
        univariate_sections.append(
            f"""### {summary.series}

- p-valor ADF en niveles: {summary.adf_level_pvalue:.4f}
- p-valor ADF en rendimientos: {summary.adf_return_pvalue:.4f}
- ARIMA seleccionado: {summary.selected_arima}
- AIC del ARIMA: {summary.arima_aic:.4f}
- p-valor Ljung-Box residuos ARIMA: {summary.ljung_box_pvalue:.4f}
- p-valor ARCH-LM: {summary.arch_test_pvalue:.4f}
"""
        )

    garch_sections = []
    for config, summary in zip(series, garch):
        garch_sections.append(
            f"""### {config.name}

- omega: {summary.omega:.6f}
- alpha(1): {summary.alpha_1:.6f}
- beta(1): {summary.beta_1:.6f}
- AIC: {summary.aic:.4f}
"""
        )

    granger_lines = []
    for relation, result in granger.items():
        readable_relation = relation.replace("_to_", " -> ")
        granger_lines.append(f"- {readable_relation}: p-valor = {result['pvalue']:.4f}")

    return f"""# Reporte de Analisis

## Resumen ejecutivo

Este reporte resume un pipeline econometrico en Python para las series {series_names}. El objetivo es evaluar estacionariedad, dinamica de la media, volatilidad condicional e interdependencia entre ambas series.

## Resultados univariados

{chr(10).join(univariate_sections)}

## Resultados GARCH(1,1)

{chr(10).join(garch_sections)}

## Resultados VAR

- Rezago seleccionado por AIC: {var_summary.selected_lag}
- AIC del VAR: {var_summary.aic:.4f}
- BIC del VAR: {var_summary.bic:.4f}

## Causalidad de Granger

{chr(10).join(granger_lines)}

## Lectura economica sugerida

1. Si el p-valor ADF en niveles es alto, la serie no parece estacionaria en niveles.
2. Si el p-valor ADF en rendimientos es bajo, la transformacion ayuda a estabilizar la media.
3. Si el ARCH-LM rechaza homocedasticidad, tiene sentido modelar volatilidad.
4. Si la causalidad de Granger no es significativa, no hay evidencia fuerte de capacidad predictiva cruzada.
"""


def write_report(path: str | Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
