# Paso 2: conseguir y validar datos reales

Antes de interpretar ADF, KPSS, ARIMA, GARCH o VAR, necesitamos que los datos sean confiables. Este paso evita errores comunes como fechas mal leidas, columnas con nombres distintos, precios vacios o series demasiado cortas.

## Archivos que necesitamos

Guarda los datos reales en:

```text
data/raw/BBVA.csv
data/raw/SAN.csv
```

## Opcion recomendada: descargar desde Yahoo Finance

El proyecto incluye un script para descargar precios mensuales. Por defecto usa el **precio ajustado** (`Adj Close`):

```bash
pip install -e .
```

```bash
python scripts/download_prices.py
```

El primer comando instala las dependencias del proyecto, incluyendo `yfinance`.

La configuracion vive en `config/data_sources.json`, que incluye `start`, `end`, `interval`, `source` y `price_field`, ademas de la lista de series.

Configuracion actual:

- BBVA: `BBVA.MC`
- Santander: `SAN.MC`
- periodo: 2019-01-01 a 2026-09-23 (`end` exclusivo; el ultimo dato disponible es 2026-09-01)
- frecuencia: mensual (`1mo`)
- fuente: Yahoo Finance (via `yfinance`)
- precio: `Adj Close`

Importante: si quieres analizar otro mercado, cambia los tickers en `config/data_sources.json`.

Si aparece un error como `No module named yfinance`, vuelve a ejecutar:

```bash
pip install -e .
```

Si la descarga no devuelve datos, revisa el ticker en Yahoo Finance y actualiza `config/data_sources.json`.

Si el validador indica que se descartaron filas, vuelve a ejecutar la descarga. Esto puede pasar si el archivo quedo con encabezados extra o filas no numericas.

## Formato esperado

El formato minimo es:

```csv
Fecha,Cierre
2019-01-01,3.37
2019-02-01,3.57
```

Tambien se aceptan estos nombres:

- Fecha: `Fecha` o `Date`
- Precio: `Cierre`, `Close`, `Adj Close` o `Precio`

El script de descarga guarda la columna de precio como `Cierre`, pero el valor corresponde al `Adj Close` de Yahoo Finance.

## Recomendacion de periodo

- frecuencia: mensual;
- minimo recomendado: 36 observaciones por serie;
- ideal: 60 o mas observaciones.

La muestra actual tiene 93 observaciones (2019-01 a 2026-09).

## Validar datos

Cuando los CSV reales esten en `data/raw`, ejecuta:

```bash
python scripts/validate_data.py
```

Si todo esta bien, deberias ver algo parecido a:

```text
BBVA: OK. Observaciones=93, inicio=2019-01-01, fin=2026-09-01, precio_min=1.72, precio_max=25.03
Santander: OK. Observaciones=93, inicio=2019-01-01, fin=2026-09-01, precio_min=1.27, precio_max=12.70
```

## Despues de validar

Si la validacion sale bien, ejecutamos:

```bash
python scripts/run_analysis.py
```

El reporte se genera en:

```text
outputs/analysis_report.md
```

## Nota para GitHub

Los archivos `BBVA.csv` y `SAN.csv` reales no se suben a GitHub porque `.gitignore` los excluye. En GitHub se suben los ejemplos `.csv.example` y la documentacion para que otra persona sepa como preparar sus propios datos.

## Nota de reproducibilidad

Yahoo Finance puede revisar el historico de `Adj Close`. El reporte generado incluye la fecha de snapshot; las cifras pueden cambiar en una nueva descarga.
