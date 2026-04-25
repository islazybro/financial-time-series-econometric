# Reejecutar analisis despues de cambiar tickers

Este paso se usa cuando cambia `config/data_sources.json`, por ejemplo al pasar de `BBVA.MX` a `BBVA.MC`.

## Comandos

Ejecuta desde la carpeta principal del proyecto:

```bash
python scripts/download_prices.py
python scripts/validate_data.py
python scripts/run_analysis.py
```

## Que revisar

Despues de correr los comandos, revisa:

```text
outputs/analysis_report.md
outputs/univariate_summary.csv
outputs/var_forecast.csv
outputs/impulse_response.csv
```

## Que actualizar despues

Como `outputs/` no se sube a GitHub, la interpretacion versionable debe actualizarse en:

```text
docs/results-interpretation.md
```

## Criterio esperado

La nueva configuracion usa:

- BBVA: `BBVA.MC`
- Santander: `SAN.MC`

Esto mejora la comparabilidad porque ambas series quedan en el mismo mercado y moneda.
