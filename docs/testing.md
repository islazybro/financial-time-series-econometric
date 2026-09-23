# Pruebas y checks

El proyecto incluye pruebas automatizadas con `pytest`.

## Instalar dependencias de desarrollo

```bash
pip install -e ".[dev]"
```

## Ejecutar pruebas

```bash
pytest
```

Referencia actual: **15 tests**.

## GitHub Actions

El repositorio incluye un workflow en:

```text
.github/workflows/tests.yml
```

Cada `push` y cada `pull request` ejecuta:

```bash
python -m pip install -e ".[dev]"
pytest
```

El workflow tambien ejecuta `ruff` para linting. Si todo pasa, GitHub muestra el estado en la pestana `Actions` y en el badge del README.

## Que cubren las pruebas

- Lectura de CSV con columnas en espanol e ingles.
- Calculo de log-precios y log-rendimientos; validacion de valores finitos.
- Alineacion de fechas entre series.
- Seleccion del orden de diferenciacion `d` con ADF.
- Que `summarize_univariate` modela la serie de log-precio correcta.
- Reconstruccion del precio desde el pronostico en log (positivo y coherente con `exp`).
- Prueba KPSS: serie estacionaria (no rechaza) y paseo aleatorio (rechaza), incluyendo el manejo del p-valor en el borde tabulado.
- Validacion de archivos limpios y deteccion de filas no numericas.
- Configuracion de series y slug de tickers.
- Escritura de CSV creando directorios.

Estas pruebas no validan toda la teoria econometrica; protegen las piezas de preparacion de datos, transformaciones y pruebas estadisticas basicas.
