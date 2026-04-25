# Seleccion de mercado y tickers

La seleccion de tickers es una decision metodologica, no solo tecnica. En Yahoo Finance, una misma empresa puede tener varios tickers segun el mercado donde cotiza.

## Configuracion anterior

El proyecto inicio con esta configuracion:

```json
{
  "name": "BBVA",
  "ticker": "BBVA.MX"
}
```

y:

```json
{
  "name": "Santander",
  "ticker": "SAN.MC"
}
```

Esta configuracion compara BBVA en Mexico con Santander en Espana. Puede ser util si se quiere estudiar relacion entre mercados, pero no es la comparacion mas limpia si el objetivo es analizar dos bancos bajo el mismo mercado bursatil.

## Configuracion actual para comparacion sectorial

Para comparar bancos europeos del mismo sector y mercado, el archivo `config/data_sources.json` usa:

```json
{
  "name": "BBVA",
  "ticker": "BBVA.MC"
}
```

y:

```json
{
  "name": "Santander",
  "ticker": "SAN.MC"
}
```

Con esta seleccion, ambas series corresponden al mercado continuo espanol y estan denominadas en euros.

## Configuracion alternativa para enfoque mexicano

Si se quiere mantener un enfoque centrado en Mexico, conviene revisar que ambas series representen activos comparables en el mismo mercado. BBVA Mexico cotiza como `BBVA.MX`, pero Santander Mexico no siempre esta disponible con la misma continuidad en Yahoo Finance. En ese caso, puede ser mejor explicar el proyecto como una comparacion internacional.

## Recomendacion para este analisis

Para una comparacion sectorial consistente, esta es la opcion mas defendible:

- BBVA: `BBVA.MC`
- Santander: `SAN.MC`

Motivo: mantiene el analisis en el mismo sector, mercado y moneda, lo que hace mas clara la interpretacion del VAR, la causalidad de Granger y las funciones impulso-respuesta.
