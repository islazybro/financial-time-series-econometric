# Interpretacion de resultados

Este documento resume la lectura econometrica del analisis generado por `scripts/run_analysis.py` usando los tickers finales del proyecto.

## Datos analizados

La ejecucion usa precios mensuales descargados desde Yahoo Finance segun `config/data_sources.json`.

Configuracion:

- BBVA: `BBVA.MC`
- Santander: `SAN.MC`
- mercado: Espana
- moneda: euros
- periodo: 2019-01-01 a 2026-01-01
- frecuencia: mensual
- observaciones validas: 84 por serie

Esta seleccion mejora la comparabilidad porque ambas acciones pertenecen al mismo sector, mercado y moneda.

## Estacionariedad

La prueba ADF en niveles arroja p-valores de 1.0000 para ambas series. Esto indica que no se rechaza la hipotesis nula de raiz unitaria, por lo que los precios en niveles no parecen estacionarios.

En rendimientos logaritmicos, los p-valores son practicamente cero:

- BBVA: 0.0000
- Santander: 0.0000

Esto sugiere que los rendimientos son estacionarios y que son una transformacion adecuada para analizar volatilidad e interacciones dinamicas.

Lectura economica:

- Los precios de acciones suelen tener tendencias y choques persistentes.
- Los rendimientos eliminan gran parte de esa tendencia y permiten trabajar con series mas estables.

## Modelo ARIMA

El modelo seleccionado por AIC para ambas series fue:

```text
ARIMA(0, 2, 1)
```

Resultados principales:

- BBVA AIC: 135.9905
- Santander AIC: 44.9736

Este resultado refuerza la idea de que los precios en niveles requieren diferenciacion para modelar su media. La especificacion seleccionada es relativamente parsimoniosa dentro de la grilla probada.

## Heterocedasticidad y GARCH

Los p-valores de la prueba ARCH-LM fueron:

- BBVA: 0.2040
- Santander: 0.3945

Como ambos valores son mayores a 0.05, no se encuentra evidencia fuerte de heterocedasticidad condicional remanente en los residuos del ARIMA.

El modelo GARCH(1,1) muestra alta persistencia en la volatilidad:

- BBVA beta(1): 0.9888
- Santander beta(1): 0.9881

Lectura economica:

- La volatilidad estimada es persistente.
- Los choques de volatilidad se reducen gradualmente.
- Los pronosticos de varianza muestran una trayectoria descendente durante los diez periodos proyectados.

## Modelo VAR

El modelo VAR selecciono un rezago:

```text
VAR(1)
```

Resultados:

- AIC: -10.7840
- BIC: -10.6079

Los pronosticos de rendimientos convergen hacia valores relativamente estables, lo cual es consistente con el uso de rendimientos estacionarios.

## Causalidad de Granger

Los p-valores de causalidad de Granger fueron:

- BBVA -> Santander: 0.1944
- Santander -> BBVA: 0.5660

Como ambos p-valores son mayores a 0.05, no se encuentra evidencia estadistica de causalidad de Granger entre las series.

Interpretacion correcta:

- No significa que BBVA y Santander no esten relacionadas como empresas o activos financieros.
- Significa que, bajo esta frecuencia mensual y con el VAR estimado, los rezagos de una serie no aportan informacion predictiva estadisticamente significativa sobre la otra.

## Impulso-respuesta

Las funciones impulso-respuesta muestran efectos iniciales que se reducen rapidamente hacia cero. Esto indica que los choques tienen efectos transitorios dentro del sistema VAR.

Lectura economica:

- El sistema estimado parece estable.
- Los choques no generan efectos persistentes de largo plazo en los rendimientos.
- La interaccion dinamica existe en magnitud limitada, pero no se traduce en causalidad de Granger significativa.

## Conclusion

El analisis muestra un patron comun en series financieras:

- precios no estacionarios;
- rendimientos estacionarios;
- necesidad de transformar las series antes de modelar;
- volatilidad persistente;
- ausencia de causalidad de Granger significativa;
- choques con efectos transitorios.

En conjunto, el proyecto muestra un flujo econometrico completo: preparacion de datos, pruebas de estacionariedad, modelado ARIMA, estimacion GARCH, modelo VAR, causalidad de Granger e impulso-respuesta. La version final con `BBVA.MC` y `SAN.MC` es metodologicamente mas consistente porque compara dos bancos del mismo mercado bursatil.
