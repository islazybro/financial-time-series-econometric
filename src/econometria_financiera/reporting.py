from __future__ import annotations

from pathlib import Path


def _format_roots(roots) -> str:
    if not roots:
        return "[]"
    return ", ".join(
        f"{root.real:.4f}{'+' if root.imag >= 0 else '-'}{abs(root.imag):.4f}i (|z|={abs(root):.4f})"
        for root in roots
    )


def _stationarity_notes(summary) -> list[str]:
    notes = []
    adf_level_reject = summary.adf_level_pvalue < 0.05
    kpss_level_reject = summary.kpss_level_pvalue < 0.05
    adf_return_reject = summary.adf_return_pvalue < 0.05
    kpss_return_reject = summary.kpss_return_pvalue < 0.05

    if not adf_level_reject and kpss_level_reject:
        notes.append(
            "niveles: ADF no rechaza raiz unitaria y KPSS rechaza estacionariedad; "
            "evidencia concordante de no estacionariedad."
        )

    if adf_return_reject and kpss_return_reject:
        notes.append(
            "rendimientos: ADF rechaza raiz unitaria pero KPSS rechaza estacionariedad; "
            "evidencia DISCORDANTE reportada como salvedad, sin forzar una clasificacion."
        )
    elif adf_return_reject and not kpss_return_reject:
        notes.append("rendimientos: ambas pruebas son compatibles con estacionariedad.")

    return notes


def build_markdown_report(context: dict) -> str:
    series = context["series"]
    data_info = context.get("data_info", {})
    univariate = context["univariate"]
    garch = context["garch"]
    var_summary = context["var_summary"]
    granger = context["granger"]
    var_diagnostics = context.get("var_diagnostics", {})
    correlation = context.get("correlation")
    irf_note = context.get("irf_note", "")

    series_names = " y ".join(item.name for item in series)

    data_section = f"""## Datos

- Series: {", ".join(f"{item.name} ({item.label})" for item in series)}
- Periodo muestral: {data_info.get('start')} a {data_info.get('end')}
- Frecuencia: mensual ({data_info.get('interval')})
- Fuente: {data_info.get('source')}
- Campo de precio: {data_info.get('price_field')}
- Observaciones por serie: {data_info.get('observations')}
- Fecha de snapshot de la corrida: {data_info.get('snapshot_date')}

Los datos provienen de Yahoo Finance y pueden ser revisados por el proveedor; las cifras corresponden al snapshot indicado y podrian cambiar en una nueva descarga."""

    stationarity_sections = []
    arima_sections = []
    for summary in univariate:
        stationarity_sections.append(
            f"""### {summary.series}

- ADF en log-precio (niveles) - H0: raiz unitaria: p-valor = {summary.adf_level_pvalue:.4f}
- KPSS en log-precio (niveles) - H0: estacionariedad: estadistico = {summary.kpss_level_statistic:.4f}, rezagos = {summary.kpss_level_lags}, p-valor = {summary.kpss_level_pvalue:.4f}
- ADF en log-rendimientos - H0: raiz unitaria: p-valor = {summary.adf_return_pvalue:.4f}
- KPSS en log-rendimientos - H0: estacionariedad: estadistico = {summary.kpss_return_statistic:.4f}, rezagos = {summary.kpss_return_lags}, p-valor = {summary.kpss_return_pvalue:.4f}
- Orden de diferenciacion (d) elegido por ADF: {summary.selected_d}
"""
        )
        notes = _stationarity_notes(summary)
        if notes:
            stationarity_sections.append("  Salvedades:\n" + "\n".join(f"  - {note}" for note in notes) + "\n")

        arima_sections.append(
            f"""### {summary.series}

- ARIMA (sobre log-precio): {summary.selected_arima}
- AIC: {summary.arima_aic:.4f}
- BIC: {summary.arima_bic:.4f}
- p-valor Ljung-Box de residuos (lag 10): {summary.ljung_box_pvalue:.4f}
"""
        )

    garch_sections = []
    for config, uni, summary in zip(series, univariate, garch):
        if summary is None:
            garch_sections.append(
                f"""### {config.name}

- ARCH-LM (media constante, lag 5): p-valor = {uni.arch_test_pvalue:.4f}
- Decision: GARCH(1,1) no estimado (sin evidencia de efectos ARCH).
"""
            )
            continue
        garch_sections.append(
            f"""### {config.name}

- ARCH-LM (media constante, lag 5): p-valor = {uni.arch_test_pvalue:.4f}
- omega: {summary.omega:.6f}
- alpha(1): {summary.alpha_1:.6f}
- beta(1): {summary.beta_1:.6f}
- alpha(1) + beta(1): {summary.persistence:.6f}
- AIC: {summary.aic:.4f}
"""
        )

    granger_sections = []
    for relation, result in granger.items():
        readable_relation = relation.replace("_to_", " -> ")
        granger_sections.append(
            f"""### {readable_relation}

- H0: {result['null_hypothesis']}
- Estadistico F: {result['test_statistic']:.4f}
- p-valor: {result['pvalue']:.4f}
- Conclusion estadistica: {result['conclusion']}
"""
        )

    selections = var_summary.selected_orders
    whiteness_pvalue = float(var_diagnostics.get("whiteness_pvalue", float("nan")))
    whiteness_conclusion = (
        "no se rechaza la ausencia de autocorrelacion residual al 5%"
        if whiteness_pvalue >= 0.05
        else "se rechaza la ausencia de autocorrelacion residual al 5%"
    )
    arch_lines = []
    for name, pvalue in var_diagnostics.get("arch_pvalues", {}).items():
        verdict = "sin efectos ARCH" if pvalue >= 0.05 else "posibles efectos ARCH"
        arch_lines.append(f"  - {name}: p-valor = {pvalue:.4f} ({verdict})")
    correlation_line = f"{correlation:.4f}" if correlation is not None else "no disponible"
    stability_text = (
        "estable: todas las raices estan fuera del circulo unitario"
        if var_summary.is_stable
        else "NO estable: hay raices dentro del circulo unitario"
    )

    return f"""# Reporte de Analisis

## Resumen ejecutivo

Este reporte resume un pipeline econometrico en Python para las series {series_names}. El objetivo es evaluar estacionariedad, dinamica de la media, volatilidad condicional e interdependencia entre ambas series.

{data_section}

## Estacionariedad

ADF contrasta H0 = raiz unitaria (no estacionariedad) y KPSS contrasta H0 = estacionariedad. Son evidencias complementarias: se reportan por separado y no se combinan en una regla automatica de clasificacion.

{chr(10).join(stationarity_sections)}

## Modelo ARIMA (log-precio)

El ARIMA se estima sobre log-precios. El orden de diferenciacion d se determina con el ADF y no por AIC, porque el AIC no es comparable entre grados de diferenciacion. Con d fijo, p y q se seleccionan minimizando AIC y se reporta tambien BIC. El pronostico se genera en log-precio y se transforma de nuevo a precio con exp(). No se comparan AIC de representaciones distintas (precio bruto vs log-precio).

{chr(10).join(arima_sections)}

## Volatilidad

El ARCH-LM se aplica a los residuos de media constante de los log-rendimientos. GARCH(1,1) se estima solo si existe evidencia de efectos ARCH (p-valor < 0.05); no se fuerza su estimacion.

{chr(10).join(garch_sections)}

## Resultados VAR

- Criterio de seleccion de rezagos: {var_summary.lag_criterion}
- Rezago seleccionado: {var_summary.selected_lag}
- Seleccion por criterio: AIC={selections.get('aic')}, BIC={selections.get('bic')}, HQIC={selections.get('hqic')}, FPE={selections.get('fpe')}
- AIC del VAR: {var_summary.aic:.4f}
- BIC del VAR: {var_summary.bic:.4f}
- HQIC del VAR: {var_summary.hqic:.4f}
- FPE del VAR: {var_summary.fpe:.4e}

### Estabilidad

- Raices del polinomio companion: {_format_roots(var_summary.roots)}
- Modulo minimo de las raices: {var_summary.min_root_modulus:.4f}
- Sistema: {stability_text}

### Diagnostico de residuos

- Autocorrelacion (Portmanteau, {var_diagnostics.get('whiteness_lags')} rezagos): estadistico = {var_diagnostics.get('whiteness_stat', float('nan')):.4f}, gl = {var_diagnostics.get('whiteness_df')}, p-valor = {whiteness_pvalue:.4f} -> {whiteness_conclusion}
- Normalidad multivariante (Jarque-Bera): estadistico = {var_diagnostics.get('normality_stat', float('nan')):.4f}, p-valor = {var_diagnostics.get('normality_pvalue', float('nan')):.4f} (diagnostico descriptivo; no es condicion de validez del VAR)
- Heterocedasticidad condicional ARCH-LM por ecuacion ({var_diagnostics.get('arch_lags')} rezagos):
{chr(10).join(arch_lines)}

### Correlacion contemporanea

- Correlacion de log-rendimientos entre las series: {correlation_line} (descriptiva; no implica causalidad economica)

### Impulso-respuesta

- {irf_note}

## Causalidad de Granger

La causalidad de Granger es predictiva: evalua si los rezagos de una serie mejoran la prediccion de la otra. No implica causalidad economica.

{chr(10).join(granger_sections)}

## Lectura economica sugerida

1. Si el ADF no rechaza raiz unitaria en log-precio, la serie no parece estacionaria en niveles.
2. Si el ADF rechaza y el KPSS no rechaza en log-rendimientos, la transformacion estabiliza la media.
3. Si el ARCH-LM no rechaza homocedasticidad, no se estima GARCH.
4. Si la causalidad de Granger no es significativa, no hay evidencia de capacidad predictiva cruzada.
5. Una correlacion contemporanea alta describe dependencia de corto plazo, no causalidad economica.
"""


def write_report(path: str | Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
