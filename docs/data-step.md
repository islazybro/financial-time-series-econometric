# Paso 2: conseguir y validar datos reales

Antes de interpretar ARIMA, GARCH o VAR, necesitamos que los datos sean confiables. Este paso evita errores comunes como fechas mal leidas, columnas con nombres distintos, precios vacios o series demasiado cortas.

## Archivos que necesitamos

Guarda los datos reales en:

```text
data/raw/BBVA.csv
data/raw/SAN.csv
```

## Formato esperado

El formato minimo es:

```csv
Fecha,Cierre
2019-01-31,102.45
2019-02-28,104.18
```

Tambien se aceptan estos nombres:

- Fecha: `Fecha` o `Date`
- Precio: `Cierre`, `Close`, `Adj Close` o `Precio`

## Recomendacion de periodo

Para que el analisis sea parecido al proyecto original:

- frecuencia: mensual;
- periodo sugerido: 2019 a 2025;
- minimo recomendado: 36 observaciones por serie;
- ideal: 60 o mas observaciones.

## Validar datos

Cuando los CSV reales esten en `data/raw`, ejecuta:

```bash
python scripts/validate_data.py
```

Si todo esta bien, deberias ver algo parecido a:

```text
BBVA: OK. Observaciones=84, inicio=2019-01-31, fin=2025-12-31
Santander: OK. Observaciones=84, inicio=2019-01-31, fin=2025-12-31
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
