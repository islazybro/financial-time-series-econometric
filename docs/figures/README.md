# Figuras

Esta carpeta contiene graficas generadas por:

```bash
python scripts/generate_figures.py
```

Figuras actuales:

- `price_series.png`: precios ajustados mensuales (`Adj Close`).
- `log_returns.png`: log-rendimientos mensuales.
- `returns_comparison.png`: media y volatilidad de log-rendimientos.
- `arima_residual_acf.png`: ACF de residuos del ARIMA sobre log-precio.
- `arima_forecast.png`: pronostico ARIMA reconstruido a precio.
- `var_forecast.png`: pronostico VAR de log-rendimientos.
- `impulse_response.png`: impulso-respuesta Cholesky con IC 95%.

La figura de varianza GARCH solo se genera si existe evidencia de efectos ARCH. En la ejecucion actual no hay efectos ARCH, por lo que no se incluye.

Las imagenes se versionan porque forman parte de la presentacion del proyecto en GitHub.
