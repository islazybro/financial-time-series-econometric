# Interpretacion de resultados

Este documento resume la lectura econometrica del analisis generado por `scripts/run_analysis.py` usando los tickers actuales. Las cifras corresponden a la ejecucion actual y pueden cambiar si Yahoo Finance revisa los datos.

## Datos analizados

- BBVA: `BBVA.MC`
- Santander: `SAN.MC`
- mercado: Espana
- moneda: euros
- fuente: Yahoo Finance (via `yfinance`)
- campo de precio: precio ajustado (`Adj Close`)
- periodo: 2019-01-01 a 2026-09-01
- frecuencia: mensual
- observaciones: 93 precios y 92 log-rendimientos por serie
- fecha de snapshot: 2026-09-22

Ambas acciones pertenecen al mismo sector, mercado y moneda, lo que mejora la comparabilidad.

## Estacionariedad (ADF y KPSS)

ADF contrasta H0 = raiz unitaria; KPSS contrasta H0 = estacionariedad.

En log-precio (niveles):

| Serie | ADF p-valor | KPSS p-valor | Lectura |
| --- | --- | --- | --- |
| BBVA | 0.9902 (no rechaza) | 0.0100 (rechaza) | Concordante: no estacionario |
| Santander | 0.9905 (no rechaza) | 0.0100 (rechaza) | Concordante: no estacionario |

En log-rendimientos:

| Serie | ADF p-valor | KPSS p-valor | Lectura |
| --- | --- | --- | --- |
| BBVA | ~0 (rechaza) | 0.1000 (no rechaza) | Compatible con estacionariedad |
| Santander | ~0 (rechaza) | 0.0452 (rechaza) | **Discordante** |

Salvedad importante: en Santander, el ADF rechaza la raiz unitaria pero el KPSS rechaza la estacionariedad al 5% (p=0.0452). La discordancia puede deberse al tamano muestral, a cambios de nivel o a autocorrelacion. No se fuerza una clasificacion automatica; se reportan ambas evidencias. En BBVA el KPSS de rendimientos queda en el borde superior tabulado (p=0.1000), por lo que se interpreta como "no se rechaza".

Lectura economica:

- Los log-precios de acciones tienen tendencias y choques persistentes, coherente con raiz unitaria.
- Los log-rendimientos eliminan gran parte de esa tendencia; la evidencia es mayoritariamente favorable a estacionariedad, con la salvedad de Santander.

## Modelo ARIMA (log-precio)

El ARIMA se estima sobre log-precios. `d` se determina por ADF (=1 en ambas series) y, con `d` fijo, `p` y `q` se seleccionan por AIC/BIC.

| Serie | Modelo | AIC | BIC | Ljung-Box (lag 10) |
| --- | --- | --- | --- | --- |
| BBVA | ARIMA(0, 1, 0) | -154.2675 | -151.7457 | 0.9981 |
| Santander | ARIMA(0, 1, 0) | -163.4534 | -160.9316 | 0.9696 |

ARIMA(0,1,0) es un paseo aleatorio: la mejor prediccion de la media es el ultimo log-precio observado. Los p-valores de Ljung-Box son altos, por lo que no se detecta autocorrelacion residual.

El pronostico se genera en log-precio y se transforma a precio con `exp()`; por construccion es plano en el log y su intervalo en precio es asimetrico. No se comparan AIC de representaciones distintas (precio bruto vs log-precio).

Los resultados se guardan en:

- `outputs/bbva_mc_arima_forecast.csv` (columnas `mean_log` y `mean_price`)
- `outputs/san_mc_arima_forecast.csv`
- `docs/figures/arima_residual_acf.png`
- `docs/figures/arima_forecast.png`

## Comparativo de rendimientos

- BBVA: media mensual 0.0218, volatilidad 0.1017.
- Santander: media mensual 0.0152, volatilidad 0.0978.
- Correlacion contemporanea de log-rendimientos: 0.8790.

La correlacion alta describe dependencia de corto plazo; no implica causalidad economica.

Los resultados se guardan en:

- `outputs/returns_comparison.csv`
- `outputs/returns_correlation.csv`
- `docs/figures/returns_comparison.png`

## Heterocedasticidad y GARCH

El ARCH-LM se aplica a los residuos de media constante de los log-rendimientos:

- BBVA: p = 0.9565
- Santander: p = 0.8810

En ambos casos no se rechaza la homocedasticidad, por lo que **no hay evidencia de efectos ARCH**. En consecuencia, **GARCH(1,1) no se estima**. No se reporta persistencia de volatilidad porque no hay base estadistica para ello en estos datos y esta especificacion.

## Modelo VAR

- Criterio de seleccion: AIC.
- Rezago seleccionado: VAR(1). AIC=-10.7704, BIC=-10.6048, HQIC=-10.7036, FPE=2.10e-05.
- Estabilidad: raices del companion con modulo 6.6963 (> 1); el sistema es estable.
- Portmanteau (10 rezagos): p = 0.6394; sin autocorrelacion residual.
- Normalidad multivariante (Jarque-Bera): p ~ 0. Es un diagnostico descriptivo (colas gruesas); no invalida el VAR.
- ARCH-LM por ecuacion: BBVA p=0.9658; Santander p=0.6601 (sin efectos ARCH).

## Causalidad de Granger

| Relacion | H0 | Estadistico F | p-valor | Conclusion |
| --- | --- | --- | --- | --- |
| BBVA -> Santander | BBVA no causa-Granger a Santander | 2.7176 | 0.1010 | No se rechaza H0 |
| Santander -> BBVA | Santander no causa-Granger a BBVA | 0.1263 | 0.7228 | No se rechaza H0 |

Interpretacion correcta:

- La causalidad de Granger es **predictiva**: evalua si los rezagos de una serie mejoran la prediccion de la otra.
- No encontrar causalidad de Granger no significa que BBVA y Santander no esten relacionadas como empresas; significa que, a esta frecuencia y con este VAR, los rezagos no aportan informacion predictiva significativa al 5%.
- BBVA -> Santander queda en p=0.1010, cercano pero por encima del 5%; no se fuerza significancia.

## Impulso-respuesta

- Identificacion: **Cholesky** (ortogonalizacion recursiva).
- Orden: **BBVA -> Santander**.
- Bandas de confianza: 95% (error estandar asintotico).
- Los efectos son pequenos y transitorios; los intervalos al 95% de las respuestas cruzadas incluyen 0 en todos los horizontes.
- El orden importa: se verifico la sensibilidad al invertir el orden y la conclusion cualitativa se mantiene.

## Conclusion

El analisis muestra un patron comun en series financieras:

- log-precios no estacionarios y log-rendimientos mayoritariamente estacionarios (con la salvedad de Santander en KPSS);
- un paseo aleatorio para la media (ARIMA(0,1,0) sobre log-precio);
- sin evidencia de efectos ARCH, por lo que no se estima GARCH;
- VAR(1) estable y con residuos sin autocorrelacion;
- sin causalidad de Granger significativa al 5%;
- choques con efectos pequenos y transitorios.

En conjunto, el proyecto muestra un flujo econometrico completo y reproducible. Para el alcance y las limitaciones, consulta `docs/limitations.md`.
