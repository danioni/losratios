# Atribución y licencia de los crudos de terceros

Los archivos de este directorio son descargas tal como las entregó cada fuente,
sin modificar. Cada uno queda registrado en `data/series/descargas_ratios.csv`
con su URL, su fecha y su SHA-256.

Solo están aquí los crudos cuya licencia permite redistribuirlos. Los de Shiller
y de FRED `NASDAQCOM` no están: ver A-R0-15 en `SUPUESTOS.md`. Los de las
fuentes de contraste de BTC y de los índices tampoco: no se guardan (A-R0-12).

Los CSV de FRED de S2 están desde antes de esa regla (A-S2-10). Lo que se leyó
de sus términos y la decisión de mantenerlos están al final.

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
  - Decir si los datos se transformaron. Aquí no se transforman.
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

Son las descargas de `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`
que S2 conserva (A-S2-10): dos por serie, del 2026-09-22 y del 2026-10-03. Qué
mide cada serie está en el `README.md`, sección Fuentes.

Lo que sigue se leyó el 2026-10-05, entre las 11:35 y las 11:39 UTC: la página
de cada serie en FRED, los términos de FRED y los del dueño de cada serie. Es
una lectura de las cláusulas, no un dictamen legal.

| Serie | Dueño, según la página de FRED | Publicación de origen | Etiqueta de derechos en FRED |
| --- | --- | --- | --- |
| `WALCL` | Board of Governors of the Federal Reserve System (US) | H.4.1 Factors Affecting Reserve Balances | "Public Domain: Citation Requested" |
| `WDTGAL` | Board of Governors of the Federal Reserve System (US) | H.4.1 Factors Affecting Reserve Balances | "Public Domain: Citation Requested" |
| `RRPONTSYD` | Federal Reserve Bank of New York | Temporary Open Market Operations | "Copyrighted: Citation Required" |

Páginas: `https://fred.stlouisfed.org/series/WALCL`,
`https://fred.stlouisfed.org/series/WDTGAL` y
`https://fred.stlouisfed.org/series/RRPONTSYD`. Las notas de `RRPONTSYD` no
traen ninguna línea de copyright: la etiqueta es lo único que lo dice.

- **Lo que los términos de FRED permiten.** `https://fred.stlouisfed.org/legal/`,
  resumen, sección III, "Use of Data with Copyright Restrictions". Literal:
  - "Public Domain: Citation requested": *"These series may be under copyright
    or in the public domain and may be used without permission, provided you do
    not engage in any prohibited use. When using, please cite the data source
    and acknowledge that you obtained the data from FRED [...] when displaying
    or publishing it."*
  - "Copyrighted: Citation required": *"These series are under copyright; but,
    provided you have not engaged in any prohibited uses, you may use these
    data series with proper attribution of the source and acknowledgment that
    you obtained the data from FRED [...] when displaying or publishing it."*
- **Lo que los mismos términos restringen.** Los términos completos, en la misma
  página, sección "Property Rights and Licenses". Literal:
  - *"Except as expressly provided in these Terms of Use, FRED® Content may not
    be modified, duplicated, copied, distributed, [...] republished, uploaded,
    downloaded, scraped, displayed, posted, transmitted on any Internet,
    Intranet or Extranet site [...] without the Bank's prior written
    permission"*. La definición de "FRED® Content" incluye los datos.
  - La licencia general permite *"to download or print a copy of any portion of
    the FRED® Content [...] solely for your personal, non-commercial use"*.
  - *"BEFORE USING DATA SERIES OWNED BY THIRD PARTIES FOR ANYTHING OTHER THAN
    YOUR OWN PERSONAL USE, YOU MUST CONTACT THE DATA OWNER TO OBTAIN
    PERMISSION."*
  - Entre los usos prohibidos del resumen (sección II): redistribuir contenido
    de terceros *"for commercial use"* sin permiso escrito del proveedor, y los
    métodos de extracción *"that are disruptive, or adversely impacts the
    stability, performance, or availability of the FRED® Services"*.
- **Los dos textos no dicen lo mismo, y este archivo no decide cuál rige.** El
  resumen deja usar y publicar las series de las dos etiquetas con su cita. Los
  términos completos reservan la redistribución del contenido de FRED al
  permiso escrito del banco, salvo lo que los propios términos permitan de
  forma expresa.
- **Lo que dice el dueño de `RRPONTSYD`.** Federal Reserve Bank of New York,
  términos de uso (`https://www.newyorkfed.org/privacy/termsofuse`, "Last
  Updated: 6/9/2023"). Literal: *"The New York Fed grants you a non-exclusive
  license, subject to the Terms, to use, copy, and distribute Content for your
  personal or business purposes."* "Content" incluye los datos. Condiciones:
  atribuir con el formato que sigue, redistribuir con los mismos permisos y
  condiciones, y no dar a entender que el banco avala el uso. La lista de
  contenidos con restricciones propias de esos términos no nombra las
  operaciones de repo. El archivo de este directorio no se bajó de
  newyorkfed.org, sino de FRED.
- **Lo que dice el dueño de `WALCL` y `WDTGAL`.** Junta de la Reserva Federal,
  página "Disclaimer" (`https://www.federalreserve.gov/disclaimer.htm`, "Last
  Update: August 02, 2024"), apartado "Copyright/trademark", leída el
  2026-10-05 a las 12:16 UTC. Literal: *"Unless otherwise indicated,
  information on Board's website is in the public domain and may be copied and
  distributed without permission. Please cite to the Board as the source of
  the information."* El H.4.1 es una publicación de la Junta en ese sitio, y
  su página (`https://www.federalreserve.gov/releases/h41/`) no indica otra
  cosa. El archivo de este directorio no se bajó de federalreserve.gov, sino
  de FRED.
- **Atribución.** La cita que sugiere la página de cada serie:
  - *Board of Governors of the Federal Reserve System (US), Assets: Total
    Assets: Total Assets (Less Eliminations from Consolidation): Wednesday
    Level [WALCL], retrieved from FRED, Federal Reserve Bank of St. Louis;
    https://fred.stlouisfed.org/series/WALCL.*
  - *Board of Governors of the Federal Reserve System (US), Liabilities and
    Capital: Liabilities: Deposits with F.R. Banks, Other Than Reserve
    Balances: U.S. Treasury, General Account: Wednesday Level [WDTGAL],
    retrieved from FRED, Federal Reserve Bank of St. Louis;
    https://fred.stlouisfed.org/series/WDTGAL.*
  - *Federal Reserve Bank of New York, Overnight Reverse Repurchase Agreements:
    Treasury Securities Sold by the Federal Reserve in the Temporary Open
    Market Operations [RRPONTSYD], retrieved from FRED, Federal Reserve Bank of
    St. Louis; https://fred.stlouisfed.org/series/RRPONTSYD.* Y, con el formato
    que piden los términos del banco: *"© 2026 Federal Reserve Bank of New
    York. Content from the New York Fed subject to the Terms of Use at
    newyorkfed.org."*
- **Cambios:** ninguno. Cada archivo es la respuesta de FRED, byte por byte.
- **Decisión (2026-10-05).** Los seis archivos se quedan versionados. Se
  sostienen en lo que declara el dueño de cada serie, no en los términos de
  FRED: la Junta pone la información de su sitio en el dominio público y pide
  que se la cite, y el Federal Reserve Bank of New York da licencia para copiar
  y distribuir con atribución. Los términos completos de FRED siguen diciendo
  lo que dicen arriba. Por eso queda pendiente bajar S2 directamente de los
  dueños de los datos (`FUENTES.md`, sección 12).


## `bce_m2_ajustada_<fecha>.csv`, `bce_m2_sin_ajustar_<fecha>.csv`, `bce_balance_eurosistema_<fecha>.csv`

- **Fuente:** Banco Central Europeo, ECB Data Portal. Conjunto BSI, series
  `BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E` y `BSI.M.U2.N.V.M20.X.1.U2.2300.Z01.E`
  (M2 de la zona del euro, ajustada y sin ajustar); conjunto ILM, serie
  `ILM.W.U2.C.T000000.Z5.Z01` (total de activos del Eurosistema).
- **URL:** la de la API que figura en `data/series/denominador_descargas.csv`.
  **Copias bajadas a mano** (A-D0-29): el `robots.txt` de la API veda al
  cliente del pipeline, así que una persona abre la URL en el navegador y
  guarda la respuesta aquí con la fecha. Las copias del 2026-10-05 son las que
  se bajaron en el paso 0 con `python-requests`, antes de leer ese archivo.
- **Licencia:** política de reutilización de las estadísticas del SEBC:
  reutilización gratuita con cita de la fuente y sin modificar las
  estadísticas; y aviso de copyright del BCE
  (<https://www.ecb.europa.eu/services/disclaimer/html/index.en.html>). Leídos
  el 2026-10-05 (`FUENTES.md`, D0.4).
- **Condiciones:** citar "Source: ECB statistics". Quien redistribuya este
  archivo tiene que mantener la cita y no modificarlo.
- **Cambios:** ninguno. El archivo es la respuesta de la API, byte por byte.

## `boj_m2_<fecha>.csv`, `boj_balance_<fecha>.csv`

- **Fuente:** Bank of Japan, BOJ Time-Series Data Search, API `getDataCode`.
  Base MD02 (Money Stock: M2 y las series anteriores M2+CDs) y base BS01 (Bank
  of Japan Accounts: total de activos y tres rubros).
- **URL:** la que figura en `data/series/denominador_descargas.csv`.
- **Licencia:** aviso de copyright del Banco de Japón
  (<https://www.boj.or.jp/en/about/copyright.htm>) y del sitio de series
  (<https://www.stat-search.boj.or.jp/info/notice_en.html>): copia y
  reproducción permitidas citando al Banco de Japón como fuente, **salvo con
  fines comerciales**, que exigen permiso previo; el contenido no se altera.
  Instrucciones de la API (<https://www.stat-search.boj.or.jp/info/api_notice_en.pdf>):
  aviso por correo al publicar un servicio que la use, y crédito. Leídos el
  2026-10-05 (`FUENTES.md`, D0.5).
- **Condiciones:** atribución al Banco de Japón y uso no comercial (A-D0-8).
  Quien redistribuya este archivo tiene que mantener las dos.
- **Cambios:** ninguno. El archivo es la respuesta de la API, byte por byte.

## `ocde_china_dinero_amplio_<fecha>.csv`

- **Fuente:** OCDE, conjunto `DSD_STES@DF_MONAGG` (Monetary aggregates), serie
  `CHN.M.MABM.XDC`, rotulada "M3" por la OCDE. Emisor original: Banco Popular
  de China.
- **URL:** la que figura en `data/series/denominador_descargas.csv`.
- **Licencia:** términos de la OCDE
  (<https://www.oecd.org/en/about/terms-conditions.html>, sección 3, "Data",
  "Permitted Use"): extraer, copiar, adaptar y distribuir para cualquier fin
  con crédito a la OCDE, con la reserva de posibles derechos de terceros que
  el usuario debe verificar. Los metadatos de la serie no traen ninguna
  restricción. Leídos el 2026-10-05 (`FUENTES.md`, D0.6.2).
- **Condiciones:** crédito a la OCDE y mención del emisor original (A-D0-9).
- **Cambios:** ninguno. El archivo es la respuesta de la API, byte por byte.

## `bis_cbta_cn_<fecha>.csv`

- **Fuente:** Bank for International Settlements, conjunto `WS_CBTA` (Central
  bank total assets), área CN. Emisor original: Banco Popular de China; serie
  empalmada por el BIS.
- **URL:** la que figura en `data/series/denominador_descargas.csv`.
- **Licencia:** términos de uso de las estadísticas del BIS
  (<https://data.bis.org/help/legal>): uso sin restricciones citando al BIS
  como fuente, sin sugerir su respaldo y, en un producto comercial, sin cargo
  adicional por incluirlas. Leídos el 2026-10-05 (`FUENTES.md`, D0.7.5 y D0.9).
- **Condiciones:** citar al BIS como fuente.
- **Cambios:** ninguno. El archivo es la respuesta de la API, byte por byte.

Los demás crudos de la fase D0 (los ZIP de la Junta, que son de dominio público
pero pesan entre 1.4 y 9 MB, y las fuentes de contraste) no están aquí
(A-D0-27): su URL, fecha y SHA-256 están en `denominador_descargas.csv`.

## `transcripcion_junta_1892_1958/`

- **Fuente:** Board of Governors of the Federal Reserve System, *Banking and
  Monetary Statistics, 1914–1941* (1943), Tabla 9, pp. 34–35; y *Banking and
  Monetary Statistics, 1941–1970* (1976), Sección 1, p. 5 (continuación de la
  Tabla 9) y Tabla 1.1, pp. 17 y 20. Cifras transcritas a mano, dos veces, de
  los escaneos; no son descargas.
- **Copia digital:** FRASER, Federal Reserve Bank of St. Louis,
  <https://fraser.stlouisfed.org/title/banking-monetary-statistics-1914-1941-38>
  y <https://fraser.stlouisfed.org/title/banking-monetary-statistics-1941-1970-41>.
  Los PDF (36 y 75 MB) no viajan con el repositorio; su URL, fecha y SHA-256
  están en `data/series/dinero_historico_descargas.csv`.
- **Licencia:** publicaciones de una agencia federal de EE.UU. sin aviso de
  copyright; que estén en dominio público como obra del gobierno de EE.UU. es
  una inferencia (`FUENTES.md`, D0.3.1). Los términos de FRASER
  (<https://fraser.stlouisfed.org/terms-of-use>, leídos el 2026-10-07) dan
  acceso para usos no comerciales, educativos y personales, exigen atribución
  y dejan la evaluación de los derechos de cada documento a quien lo usa.
- **Condiciones:** atribución a la Junta y a FRASER, como arriba.
- **Cambios:** ninguno en las cifras. Los archivos `A_*.csv` y `B_*.csv` son
  las dos lecturas tal como se hicieron; `resoluciones.csv` dice qué celda se
  releyó y por qué (A-D0-19).

## `coin_metrics_btc_oferta_<fecha>.json`

- **Fuente:** Coin Metrics, datos community. Métricas `SplyCur`, `BlkCnt` e
  `IssTotNtv` de BTC (fase N0).
- **URL:** `https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=SplyCur,BlkCnt,IssTotNtv&frequency=1d&page_size=10000`
- **Licencia:** Creative Commons Attribution-NonCommercial 4.0 International
  (CC BY-NC 4.0), <https://creativecommons.org/licenses/by-nc/4.0/>.
- **Dónde lo declara la fuente:**
  <https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.md>,
  releído el 2026-10-07.
- **Condiciones:** atribución a Coin Metrics, y **uso no comercial**. Quien
  redistribuya este archivo tiene que mantener las dos.
- **Cambios:** ninguno. El archivo es la respuesta de la API, byte por byte.
  Se registra en `data/series/numerador_descargas.csv`.

## `usgs_ds140_oro_<fecha>.xlsx` y `usgs_ds140_plata_<fecha>.xlsx`

- **Fuente:** U.S. Geological Survey, *Data Series 140, Historical Statistics
  for Mineral and Material Commodities in the United States*: hojas "Gold"
  (1900–2022, modificada el 20 de noviembre de 2023) y "Silver" (1900–2021,
  modificada el 1 de septiembre de 2023).
- **URL:** `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-gold-2022.xlsx`
  y `.../ds140-silver-2021.xlsx`, enlazadas desde
  <https://www.usgs.gov/centers/national-minerals-information-center/historical-statistics-mineral-and-material-commodities>.
- **Licencia:** dominio público de EE.UU. Política del USGS
  (<https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits>,
  leída el 2026-10-07): *"USGS-authored or produced data and information are
  considered to be in the U.S. Public Domain."*
- **Condiciones:** ninguna; se cita al USGS como fuente.
- **Cambios:** ninguno. Entran por copia bajada a mano (A-N0-14) y se
  registran en `data/series/numerador_descargas.csv`.

## `z1_<tabla>_<fecha>.csv` (`F51_1_t`, `F51_1_s`, `F3_s`, `F3_t`, `D3_s`)

- **Fuente:** Junta de Gobernadores del Sistema de la Reserva Federal, *Z.1
  Financial Accounts of the United States*, paquete CSV de la publicación
  vigente (`z1_csv_files.zip`): el miembro `csv/<tabla>.csv` de cada tabla.
- **URL:** `https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip`;
  en el manifiesto, con el fragmento `#csv/<tabla>.csv` que dice qué miembro es.
- **Licencia:** dominio público. Descargo legal de la Junta
  (<https://www.federalreserve.gov/disclaimer.htm>, leído el 2026-10-07):
  *"Unless otherwise indicated, information on Board's website is in the
  public domain and may be copied and distributed without permission. Please
  cite to the Board as the source of the information."*
- **Condiciones:** citar a la Junta como fuente.
- **Cambios:** ninguno. Son los bytes exactos del miembro del ZIP; el ZIP
  (8.3 MB) no se versiona (A-D0-27, A-N0-14) y su hash está en
  `data/series/numerador_descargas.csv`.

## `censo_hvs_tabla7_<fecha>.xlsx`, `censo_hvs_tabla7a_<fecha>.xlsx` y `censo_popest_viviendas_<fecha>.xlsx`

- **Fuente:** U.S. Census Bureau. Las dos primeras, *Housing Vacancies and
  Homeownership (CPS/HVS)*, tablas históricas 7 y 7a; la tercera, *Population
  Estimates Program*, "Annual Estimates of Housing Units for the United
  States, Regions, States, and the District of Columbia: April 1, 2020 to
  July 1, 2025" (NST-EST2025-HU).
- **URL:** `https://www.census.gov/housing/hvs/data/histtab7.xlsx`,
  `https://www.census.gov/housing/hvs/data/hist_tab_7a_v2025.xlsx` y
  `https://www2.census.gov/programs-surveys/popest/tables/2020-2025/housing/totals/NST-EST2025-HU.xlsx`.
  Las dos últimas llevan la vintage en el nombre y cambian cada año.
- **Licencia:** dominio público. Son obras del gobierno federal de EE.UU.,
  sin copyright: 17 U.S.C. § 105(a), *"Copyright protection under this title
  is not available for any work of the United States Government"* (leído en
  <https://www.law.cornell.edu/uscode/text/17/105> el 2026-10-07). En las
  páginas del Censo leídas no hay una cláusula propia sobre reutilizar los
  archivos; la de citas (<https://www.census.gov/about/policies/citation.html>)
  da el formato de cita.
- **Condiciones:** ninguna; se cita al Censo como fuente, con la tabla y la
  fecha de publicación.
- **Cambios:** ninguno. Se registran en `data/series/numerador_descargas.csv`.
