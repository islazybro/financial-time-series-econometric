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

Si ya existen `data/raw/BBVA.csv` y `data/raw/SAN.csv`, puedes usar:

```bash
python scripts/run_pipeline.py --skip-download
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
