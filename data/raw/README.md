# Datos de entrada

Coloca aqui los archivos originales:

- `BBVA.csv`
- `SAN.csv`

Formato minimo esperado:

```csv
Fecha,Cierre
2019-01-01,3.37
2019-02-01,3.57
```

Columnas aceptadas:

- Fecha: `Fecha`, `Date`
- Precio: `Cierre`, `Close`, `Adj Close`, `Precio`

La descarga por defecto usa el **precio ajustado** (`Adj Close`) de Yahoo Finance, aunque se guarde con el nombre de columna `Cierre`.

Si quieres probar el pipeline sin datos reales, ejecuta:

```bash
python scripts/generate_demo_data.py
```

Nota: los datos de Yahoo Finance pueden ser revisados; el reporte generado incluye la fecha de snapshot.
