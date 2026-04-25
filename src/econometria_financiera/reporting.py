from __future__ import annotations

from pathlib import Path


def build_markdown_report(context: dict) -> str:
    bbva = context["bbva"]
    san = context["san"]
    bbva_garch = context["bbva_garch"]
    san_garch = context["san_garch"]
    var_summary = context["var_summary"]
    granger = context["granger"]

    return f"""# Reporte de Analisis

## Resumen ejecutivo

Este reporte resume un pipeline econometrico en Python para las acciones de BBVA y Santander. El objetivo es evaluar estacionariedad, dinamica de la media, volatilidad condicional e interdependencia entre ambas series.

## Resultados univariados

### BBVA

- p-valor ADF en niveles: {bbva.adf_level_pvalue:.4f}
- p-valor ADF en rendimientos: {bbva.adf_return_pvalue:.4f}
- ARIMA seleccionado: {bbva.selected_arima}
- AIC del ARIMA: {bbva.arima_aic:.4f}
- p-valor ARCH-LM: {bbva.arch_test_pvalue:.4f}

### Santander

- p-valor ADF en niveles: {san.adf_level_pvalue:.4f}
- p-valor ADF en rendimientos: {san.adf_return_pvalue:.4f}
- ARIMA seleccionado: {san.selected_arima}
- AIC del ARIMA: {san.arima_aic:.4f}
- p-valor ARCH-LM: {san.arch_test_pvalue:.4f}

## Resultados GARCH(1,1)

### BBVA

- omega: {bbva_garch.omega:.6f}
- alpha(1): {bbva_garch.alpha_1:.6f}
- beta(1): {bbva_garch.beta_1:.6f}
- AIC: {bbva_garch.aic:.4f}

### Santander

- omega: {san_garch.omega:.6f}
- alpha(1): {san_garch.alpha_1:.6f}
- beta(1): {san_garch.beta_1:.6f}
- AIC: {san_garch.aic:.4f}

## Resultados VAR

- Rezago seleccionado por AIC: {var_summary.selected_lag}
- AIC del VAR: {var_summary.aic:.4f}
- BIC del VAR: {var_summary.bic:.4f}

## Causalidad de Granger

- BBVA -> Santander: p-valor = {granger["bbva_to_san"]["pvalue"]:.4f}
- Santander -> BBVA: p-valor = {granger["san_to_bbva"]["pvalue"]:.4f}

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
