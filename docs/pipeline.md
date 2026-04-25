# Pipeline completo

El proyecto puede ejecutarse por etapas o con un solo comando.

## Ejecutar todo

```bash
python scripts/run_pipeline.py
```

Este comando ejecuta:

1. descarga de precios;
2. validacion de datos;
3. analisis econometrico;
4. generacion de figuras.

## Ejecutar sin descargar

Si ya existen los CSV definidos en `config/data_sources.json`, puedes usar:

```bash
python scripts/run_pipeline.py --skip-download
```

## Cambiar acciones analizadas

El pipeline lee las series desde `config/data_sources.json`. Para reutilizar el proyecto con otros dos activos, cambia `name`, `ticker` y `output` en ese archivo y vuelve a ejecutar:

```bash
python scripts/run_pipeline.py
```

La version actual esta disenada para comparar exactamente dos series. Los resultados univariados usan nombres dinamicos derivados del ticker, por ejemplo `aapl_arima_forecast.csv` o `msft_garch_forecast.csv`.

### Ejemplo: Apple vs Microsoft

Edita `config/data_sources.json`:

```json
{
  "start": "2019-01-01",
  "end": "2026-01-01",
  "interval": "1mo",
  "series": [
    {
      "name": "Apple",
      "ticker": "AAPL",
      "output": "data/raw/AAPL.csv"
    },
    {
      "name": "Microsoft",
      "ticker": "MSFT",
      "output": "data/raw/MSFT.csv"
    }
  ]
}
```

Despues ejecuta:

```bash
python scripts/run_pipeline.py
```

El pipeline descargara los nuevos datos, validara los CSV, ejecutara el analisis y generara resultados en `outputs/`.

Archivos esperados para este ejemplo:

```text
outputs/aapl_arima_forecast.csv
outputs/aapl_garch_forecast.csv
outputs/msft_arima_forecast.csv
outputs/msft_garch_forecast.csv
outputs/analysis_report.md
outputs/returns_comparison.csv
outputs/var_forecast.csv
outputs/impulse_response.csv
```

En PowerShell, para listar o abrir resultados:

```powershell
dir outputs
notepad outputs\analysis_report.md
explorer outputs
```

## Ejecutar sin figuras

Si solo quieres actualizar los archivos de `outputs/`, usa:

```bash
python scripts/run_pipeline.py --skip-figures
```

## Ejecutar por etapas

```bash
python scripts/download_prices.py
python scripts/validate_data.py
python scripts/run_analysis.py
python scripts/generate_figures.py
```

El comando unico es util para reproduccion rapida. Los comandos por etapa son utiles cuando se quiere revisar o depurar una parte especifica.
