# Atribución y licencia de los crudos de terceros

Los archivos de este directorio son descargas tal como las entregó cada fuente,
sin modificar. Cada uno queda registrado en `data/series/descargas_ratios.csv`
con su URL, su fecha y su SHA-256.

Solo están acá los crudos cuya licencia permite redistribuirlos. Los de Shiller
y de FRED `NASDAQCOM` no están: ver A-R0-15 en `SUPUESTOS.md`. Los de las
fuentes de contraste de BTC y de los índices tampoco: no se guardan (A-R0-12).

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

## `pink_sheet_edicion_2025-01-03.xlsx`

- **Fuente:** The World Bank: World Bank Commodity Price Data (The Pink Sheet),
  precios mensuales, **edición del 3 de enero de 2025**. Es la última edición
  que trae el oro y la plata sin redondear, y de ella sale el tramo 1960-01 a
  2024-12 de las dos series (A-R0-19).
- **URL:**
  `https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx`.
  Es la dirección que el archivo tenía en esa edición. La página actual del
  Banco Mundial ya no la enlaza. Descargado el 2026-10-04.
- **SHA-256:** `bd89b83eeceadaecb803018c104f76b316d2df3fae28ef7afde48021100c7e11`
  (765.246 bytes).
- **Licencia:** Creative Commons Attribution 4.0 International (CC BY 4.0), la
  misma del Pink Sheet vigente, con los mismos términos adicionales del Banco
  Mundial.
- **Condiciones:** atribución al Banco Mundial, con la fecha de la edición.
- **Cambios:** ninguno. El archivo es el que publicó el Banco Mundial.
- **Es una edición congelada.** No se vuelve a descargar: el pipeline usa esta
  copia y la identifica por su hash. No recibe las revisiones que el Banco
  Mundial haga después de esa fecha; si las hay, el control del empalme las
  detecta y la corrida se detiene.

## `fmi_pcps_2026-10-04.xlsx`

- **Fuente:** International Monetary Fund, Primary Commodity Prices, base
  mensual. Es el archivo que la página enlazaba el 2026-10-04 como "Excel
  Database: September 2026"; trae de 1980M1 a 2026M8.
- **URL:**
  `https://www.imf.org/-/media/files/research/commodityprices/monthly/external-data.xlsx`,
  enlazada desde `https://www.imf.org/en/research/commodity-prices`.
  Descargado el 2026-10-04, una sola vez.
- **SHA-256:** `e0bc0cbbd08208e9868fb16e21992ff4b86a7676a2b5f64d32a02bdb8bdcc464`
  (619.264 bytes).
- **Licencia:** los términos del FMI para sus datos estadísticos, sección "The
  Use of IMF Data" de <https://www.imf.org/en/about/copyright-and-terms>
  (vigentes desde el 11 de octubre de 2024, leídos el 2026-10-04). Literal:
  *"You may download, extract, copy, create derivative works, publish,
  distribute, and use Data obtained from IMF Sites, subject to the following
  conditions"*.
- **Condiciones:**
  - Atribución: *"Source: International Monetary Fund, Primary Commodity
    Prices, https://www.imf.org/en/research/commodity-prices"*.
  - Decir si los datos se transformaron. Acá no se transforman.
  - Uso comercial: *"For any potential commercial reuse of IMF Data, please
    email copyright@imf.org to request permission."*
  - Quien redistribuya este archivo tiene que mantener la atribución y dar a
    conocer estos términos: *"Users who make IMF Data available to other Users
    through any type of distribution or download environment agree to take
    reasonable efforts to communicate and promote compliance by their users
    with these terms."*
- **No se baja solo.** Los mismos términos dicen: *"The IMF prohibits the bulk
  download of information by automated technology without explicit
  permission"*. El pipeline usa esta copia y nunca sale a buscar otra;
  actualizarla es un acto manual (A-R0-20).
- **Cambios:** ninguno. El archivo es el que publicó el FMI.
- **Para qué se usa.** No alimenta ninguna serie. Es la referencia del control
  mensual del oro y la plata: las series `PGOLD` y `PSILVER`.

## Los CSV de FRED de S2 (`WALCL`, `WDTGAL`, `RRPONTSYD`)

Están documentados en el `README.md`, sección Fuentes. Este archivo no afirma
nada sobre su licencia: no se leyó para esta revisión.
