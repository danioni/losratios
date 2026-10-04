# Atribución y licencia de los crudos de terceros

Los archivos de este directorio son descargas tal como las entregó cada fuente,
sin modificar. Cada uno queda registrado en `data/series/descargas_ratios.csv`
con su URL, su fecha y su SHA-256.

Solo están acá los crudos cuya licencia permite redistribuirlos. Los de Shiller
y de FRED `NASDAQCOM` no están: ver A-R0-15 en `SUPUESTOS.md`.

## `coin_metrics_btc_<fecha>.json`

- **Fuente:** Coin Metrics, datos community. Métrica `PriceUSD` de BTC.
- **URL:** `https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=PriceUSD&frequency=1d&page_size=10000`
- **Licencia:** Creative Commons Attribution-NonCommercial 4.0 International
  (CC BY-NC 4.0), <https://creativecommons.org/licenses/by-nc/4.0/>.
- **Dónde lo declara la fuente:**
  <https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.md>,
  leído el 2026-10-04.
- **Condiciones:** atribución a Coin Metrics, y **uso no comercial**. Quien
  redistribuya este archivo tiene que mantener las dos.
- **Cambios:** ninguno. El archivo es la respuesta de la API, byte por byte.

## `pink_sheet_<fecha>.xlsx`

- **Fuente:** The World Bank: World Bank Commodity Price Data (The Pink Sheet),
  precios mensuales.
- **URL:** la que enlaza `https://www.worldbank.org/en/research/commodity-markets`
  como "Monthly prices" el día de la descarga; queda en el manifiesto.
- **Licencia:** Creative Commons Attribution 4.0 International (CC BY 4.0),
  <https://creativecommons.org/licenses/by/4.0/>, con los términos adicionales
  del Banco Mundial para sus conjuntos de datos.
- **Dónde lo declara la fuente:**
  <https://www.worldbank.org/ext/en/legal/terms-conditions/datasets>, leído el
  2026-10-04.
- **Condiciones:** atribución al Banco Mundial.
- **Cambios:** ninguno. El archivo es el que publica el Banco Mundial.

## Los CSV de FRED de S2 (`WALCL`, `WDTGAL`, `RRPONTSYD`)

Están documentados en el `README.md`, sección Fuentes. Este archivo no afirma
nada sobre su licencia: no se leyó para esta revisión.
