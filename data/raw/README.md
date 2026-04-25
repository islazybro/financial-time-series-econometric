# Datos de entrada

Coloca aqui los archivos originales:

- `BBVA.csv`
- `SAN.csv`

Formato minimo esperado:

```csv
Fecha,Cierre
2019-01-31,102.45
2019-02-28,104.18
```

Columnas aceptadas:

- Fecha: `Fecha`, `Date`
- Precio de cierre: `Cierre`, `Close`, `Adj Close`, `Precio`

Si quieres probar el pipeline sin datos reales, ejecuta:

```bash
python scripts/generate_demo_data.py
```
