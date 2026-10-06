# Fuentes de precios para los ratios

> **APROBADO CON CONDICIONES (2026-10-04).** Todo lo que figura aquí se leyó de
> la fuente el 2026-10-04, en dos pasadas: la primera desde un entorno con
> proxy (10:43–11:00 UTC) y la segunda desde una máquina con salida directa
> (13:39–15:30 UTC). Cada cifra dice de cuál pasada sale cuando importa. Nada
> de este archivo viene de memoria. Lo que no se pudo leer está dicho como tal
> y no tiene cifras.
>
> Las decisiones están en la sección 9, los permisos que hay que pedir en la
> 10, y los supuestos A-R0-\* en `SUPUESTOS.md`.

Este documento es el entregable del paso 0 de la fase R (ratios): evaluar, por
activo, de dónde pueden salir precios **observados**, trazables y validables,
con la misma disciplina que S2. Este archivo no tiene código: el pipeline que usa
estas fuentes es `senales/ratios.py`, del paso 1.

Los cinco activos son los que usan los cinco pares del sitio (BTC/Oro,
Oro/S&P 500, BTC/S&P 500, Nasdaq/S&P 500, Oro/Plata): S&P 500, Nasdaq
Composite, oro, plata y BTC.

---

## 0. Cómo leer las tablas

Cada candidata tiene una fila con:

| Columna | Qué dice |
| --- | --- |
| Identificador y URL | Lo que se descarga, tal cual. |
| Frecuencia nativa | Diaria, mensual, etc. |
| Convención | **Qué instante describe el valor**: cierre del día, cierre de mes, promedio mensual, fixing AM/PM. |
| Unidad y moneda | Puntos de índice, USD por onza troy, USD por BTC. |
| Inicio real | Primera fecha con dato, leída de la descarga, no del folleto. |
| Clave / registro | Si exige API key o cuenta. |
| Licencia | Clase (a), (b) o (c) según 0.1, con la cláusula leída. |
| Muestra | Un valor (fecha + cifra) contrastado con una segunda fuente. |

Estados posibles de una fila: **leída** (todo verificado), **parcial** (se leyó
la fuente pero falta algo, dicho cuál), **no sirve** (leída, y la lectura la
descarta).

### 0.1 Clases de licencia

El sitio es de investigación pública, sin fines comerciales hoy, pero puede
enlazar en el futuro a un servicio de asesoría. Con ese criterio:

| Clase | Qué entra | Trato |
| --- | --- | --- |
| **(a)** | Abiertas: dominio público, CC BY, gratuitas con atribución. | Preferidas. |
| **(b)** | "Solo no comercial". | Aceptables solo si no hay (a). Se registran como supuesto A-R0-\* con la condición **"válido mientras el sitio no tenga vínculo comercial"**. |
| **(c)** | Licencia pagada, permiso escrito previo del dueño, o solo uso personal. | Excluidas. |

Dos casos no caben limpios en esas tres clases y se marcan aparte, sin
forzarlos:

- **Sin licencia declarada (s/d).** La fuente publica los datos y no dice nada
  sobre reutilizarlos. No es (a) por la letra, y tampoco tiene una cláusula
  restrictiva. Es el caso de Shiller.
- **(b) con reserva.** La fuente tiene dos textos que no dicen lo mismo. Es el
  caso de las series con copyright en FRED.

La clasificación es una lectura de las cláusulas, no un dictamen legal.

### 0.2 La regla de publicación

La clase de licencia decide qué fuente se usa. Qué se **publica** es más
estricto, y tiene dos filtros.

- **La licencia.** Solo las series cuya licencia permite publicar sin
  interpretación (CC BY, dominio público, o CC BY-NC dado el uso no comercial
  del sitio). Una fuente s/d o (b) con reserva puede alimentar el pipeline,
  pero lo que sale de ella se publica como **NO MEDIDO** hasta tener el
  permiso escrito del dueño.
- **La validación.** Ninguna serie se publica sin un caso de validación contra
  una segunda fuente. Si no cierra, la serie se publica como **NO MEDIDO: sin
  validación externa**.

Detalle en 9.1 y 9.6.

### 0.3 La regla de la convención

Los dos lados de un ratio tienen que describir el mismo instante. Un promedio
mensual dividido por un cierre de fin de mes mezcla convenciones; es el mismo
error que costó A-S2-13 (nivel de miércoles contra promedio semanal).

**Convención objetivo (instrucción del 2026-10-04): promedio mensual de cierres
diarios para las cinco series.** Cada fuente elegida tiene que permitir
construir exactamente eso; la sección 9.4 dice, serie por serie, qué cierre
diario entra y dónde la convención no se puede verificar del todo.

---

## 1. Qué se leyó, desde dónde y cuándo

La primera pasada salió por un proxy con lista de hosts permitidos y dejó
varias fuentes sin leer. La segunda pasada, desde una máquina con salida
directa, las leyó. Estado por host tras las dos:

| Host | Estado el 2026-10-04 |
| --- | --- |
| fred.stlouisfed.org | **Leído en la segunda pasada.** 15 pedidos con `python-requests 2.33.1` y su User-Agent por defecto, uno cada ~25 s entre 13:41 y 13:48 UTC: 14 con HTTP 200 y 1 con HTTP 404 (`PGOLDUSDM`). Ver la nota de abajo sobre los pedidos que fallaron. |
| shillerdata.com, img1.wsimg.com | Página y `ie_data.xls` leídos. |
| cdn.cboe.com, www.cboe.com | CSV del SPX y términos leídos. |
| api.nasdaq.com, www.nasdaq.com | API probada (solo responde con cabeceras de navegador; con el User-Agent de curl reinicia la conexión). Términos leídos. |
| indexes.nasdaqomx.com | La página "History for COMP" responde HTTP 200; depende de JavaScript y no se exploró más. |
| www.spglobal.com | curl recibe HTTP 403. Leída con navegador. |
| api.statistiken.bundesbank.de | API leída. La serie candidata no existe (4.4). |
| www.worldbank.org, thedocs.worldbank.org, datacatalog.worldbank.org, data.worldbank.org | Página, archivo y términos leídos. |
| www.lbma.org.uk, www.ice.com | Leídas. |
| prices.lbma.org.uk | HTTP 403 de Cloudflare ("Sorry, you have been blocked") con curl y con navegador. |
| www.gold.org | Leída en la primera pasada. |
| www.bitstamp.net | API probada en las dos pasadas. La documentación y `/legal/` se leyeron con navegador. |
| community-api.coinmetrics.io, docs.coinmetrics.io | API y documentación leídas. `coinmetrics.io/community-network-data/` y `coinmetrics.io/cm-labs/` redirigen (301) a talos.com. |
| api.blockchain.info, www.blockchain.com | API y términos leídos. |
| api.exchange.coinbase.com, docs.cdp.coinbase.com, www.coinbase.com | API, documentación y términos leídos. |
| api.kraken.com, docs.kraken.com, support.kraken.com | API y documentación leídas. No se localizaron términos sobre datos de mercado. |
| api.coingecko.com, www.coingecko.com | API probada; términos leídos. |
| query1.finance.yahoo.com, legal.yahoo.com | La API responde HTTP 200 desde la máquina con salida directa (el HTTP 429 de la primera pasada era del otro entorno). Términos leídos. |
| stooq.com | Desafío JavaScript en las dos pasadas. |
| pubs.usgs.gov, www.usgs.gov | Capítulos de oro y plata de los *Mineral Commodity Summaries* y política de derechos, leídos. |
| www.imf.org | curl recibe HTTP 403 ("Access Denied"). La página y los términos se leyeron con navegador; la planilla y la documentación, con `python-requests`. |
| archive.org | *Minerals Yearbook 1985*, volumen 1: el texto y la imagen de la página 466, leídos (4.7). |
| search.library.wisc.edu | Es donde el USGS aloja los *Minerals Yearbook* viejos. La página de la tabla responde "Browser not allowed" a curl y al navegador, y ofrece un paso de verificación. No se pasó ese control: la misma publicación se leyó en archive.org. |
| www.nber.org | Working Paper 24016, sobre el London Gold Pool: PDF leído (A-R0-17). |
| data.nasdaq.com | Leída en la primera pasada (no sirve, sección 7). No se volvió a probar. |

**Nota sobre FRED.** En la segunda pasada, los primeros cuatro pedidos se
hicieron con curl 8.21 (Schannel) y un User-Agent de Chrome: los cuatro
terminaron en conexión reiniciada (13:39–13:41 UTC) y un quinto no respondió en
90 s. El mismo pedido con `python-requests` respondió HTTP 200 a las 13:41:48
UTC, mientras curl seguía fallando. Lo observado es que FRED distingue al
cliente (**dato**); que la causa sea el desajuste entre el User-Agent declarado
y la huella TLS es una lectura de eso (**supuesto**). No se sabe si la caída de
la primera pasada tuvo la misma causa.

---

## 2. S&P 500

> **Sin niveles del índice.** El S&P 500 y el Nasdaq Composite no se publican
> (A-R0-14), y este documento es público. De cada muestra de las secciones 2,
> 3 y 8 queda la fecha, la diferencia porcentual y la fuente del contraste; el
> nivel del índice, no.

### 2.1 FRED `SP500` — leída

- URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500`
  (48.941 bytes, igual que en la primera pasada). Página de la serie:
  `https://fred.stlouisfed.org/series/SP500`.
- Frecuencia nativa: diaria. La página dice "Frequency: Daily, Close".
- **Convención: cierre del día.** La nota de la serie dice que las
  observaciones son el valor del índice al cierre del mercado y que el mercado
  cierra típicamente a las 4 PM ET, salvo feriados con cierre anticipado.
- Unidad: "Index, Not Seasonally Adjusted" (puntos de índice). Es índice de
  precio, sin dividendos; la nota lo dice.
- Inicio real: **2016-10-03**. El CSV trae 2.610 filas, 2.514 con valor y 96
  vacías, hasta el 2026-10-02. La nota explica el corte: por
  un acuerdo entre el banco y S&P Dow Jones Indices, FRED incluye 10 años de
  historia diaria de estas series.
- Clave / registro: no.
- **Licencia: (c).** Etiqueta de la serie: "Copyrighted: Pre-Approval
  Required". La nota de la serie agrega la cláusula de S&P, literal:
  *"Reproduction of S&P 500 in any form is prohibited except with the prior
  written permission of S&P Dow Jones Indices LLC"*. El permiso se pide a
  `index_services@spdji.com` (dato de la misma nota).
- Muestra: los cierres del **2026-09-30** y del **2020-03-20**, contra el CSV
  de Cboe (2.3): diferencia de 0.000 % en los dos. De 2.514 fechas comunes con
  Cboe, 8 difieren en más de 0.01 puntos; la mayor es la del 2019-02-28, donde
  FRED queda 0.283 % por debajo.

### 2.2 Robert Shiller, `ie_data.xls` — leída

- Página: `https://shillerdata.com/`. Archivo:
  `https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/70fec4f5-727f-4e53-b5f1-179af109c5fa/ie_data.xls`
  (1.674.752 bytes; cabecera `Last-Modified: Wed, 02 Sep 2026`). El espejo
  `econ.yale.edu/~shiller/data/ie_data.xls` respondió HTTP 403 en la primera
  pasada.
- Estructura: dos hojas, `Disclaimer` y `Data` (1.878 filas × 22 columnas).
  El encabezado ocupa las filas 5 a 8; la columna `P` ("S&P Comp.") es el
  precio.
- Frecuencia nativa: mensual. 1.869 filas de datos.
- **Convención: promedio mensual de cierres diarios.** Texto literal de la
  página: *"Stock price data are monthly averages of daily closing prices."*
  **Verificado contra cierres diarios** (2.3): el promedio de los cierres del
  SPX de Cboe reproduce la columna `P` en 620 meses comunes (1975-01 a
  2026-08) con diferencia relativa mediana de 0.0003 % y máxima de 0.30 %.
  Los dos meses que más se apartan son 2016-08, donde Shiller queda 0.300 %
  por debajo del promedio de los cierres, y 2024-01, donde queda 0.231 % por
  encima.
- **La última fila no es un promedio.** La fila siguiente a `2026.09` trae la
  nota literal *"Sept price is Sept 1st close"*, y el valor de esa fila
  coincide con el cierre del SPX del 2026-09-01 en Cboe (diferencia de
  0.000 %). Queda 0.495 % por debajo del promedio de los 21 cierres de
  septiembre. La última fila es provisional hasta la actualización siguiente.
- Rezago: el archivo se modificó por última vez el 2026-09-02. Al 2026-10-04
  el último mes completo que trae es **agosto de 2026**. La página no declara
  un calendario de actualización.
- Unidad y moneda: puntos de índice.
- Inicio real: **1871.01** (leído del archivo).
- Clave / registro: no.
- **Licencia: sin licencia declarada (s/d).** Ni la página ni el archivo
  tienen términos de uso. Lo único que hay es un descargo de responsabilidad:
  la hoja `Disclaimer` dice que los datos fueron *"developed by Robert J.
  Shiller using various public sources"* y niega garantías; la página repite
  un descargo equivalente. No hay cláusula que permita ni que prohíba
  republicar. El índice subyacente es de S&P (2.1).
- Muestra: **2026.08**, contra el promedio de los 21 cierres de Cboe y contra
  el de los cierres de FRED `SP500`: diferencia de 0.000 % con los dos.
  **2020.03**: 0.000 % contra FRED y 0.0001 % contra Cboe.
- Qué permite que FRED no: historia desde 1871 y retorno total mensual. Qué no
  permite: cierres, ni el mes en curso.

### 2.3 Otras candidatas para S&P 500

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| S&P Dow Jones Indices (www.spglobal.com), originador | leída, **(c)** | La página del índice muestra el nivel al 2026-10-02, que coincide con el cierre de Cboe de ese día (0.000 %), un control de exportación y rangos hasta 10 años; la exportación no se probó. Aviso legal, literal: *"Redistribution or reproduction in whole or in part are prohibited without written permission"*. |
| Cboe, `https://cdn.cboe.com/api/global/us_indices/daily_prices/SPX_History.csv` | leída, **(c)** | Diaria, columnas `DATE,SPX`, 13.047 filas del 1975-01-02 al 2026-10-02; 293.010 bytes. La página de datos históricos de Cboe enlaza los CSV de la familia VIX en esa misma ruta, pero no este: no está documentado. Términos de cboe.com: una copia para *"personal non-commercial use"* y prohibición de publicar sin consentimiento escrito. **Se usó solo como contraste.** |
| Nasdaq (api.nasdaq.com), símbolo SPX | **no sirve** | Responde `"Symbol not exists."`. |
| Stooq `^spx` | **no sirve** | Ver sección 7. |
| Yahoo Finance `^GSPC` | leída, **(c)** | Responde desde la máquina con salida directa. Es lo que usaba el sitio hasta la fase 3: ver sección 8.2. |

---

## 3. Nasdaq Composite

### 3.1 FRED `NASDAQCOM` — leída

- URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM`
  (280.955 bytes, igual que en la primera pasada). Página:
  `https://fred.stlouisfed.org/series/NASDAQCOM`.
- Frecuencia nativa: diaria ("Daily, Close").
- **Convención: cierre del día**, con la misma nota que `SP500`: valor del
  índice al cierre del mercado, típicamente 4 PM ET.
- Unidad: "Index Feb 5, 1971=100".
- Inicio real: **1971-02-05**, el día de la base del índice. 14.520 filas,
  14.033 con valor y 487 vacías (feriados), hasta el 2026-10-02.
- Clave / registro: no.
- **Licencia: (b) con reserva.** La nota de la serie dice solo *"Copyright ©
  2016, NASDAQ OMX Group, Inc."* y la etiqueta es "Copyrighted: Pre-Approval
  Required". Los términos de FRED (`https://fred.stlouisfed.org/legal/`,
  sección III) definen esa etiqueta, literal: *"Without first obtaining the
  express written permission of the copyright holder, [...] these series may
  only be used for non-commercial educational or personal use."* La reserva:
  el FAQ de la misma página y los términos de la API dicen que para cualquier
  uso que no sea el personal hay que contactar al dueño de los datos. Un sitio
  público de investigación sin fines comerciales cabe en la primera frase y no
  en la segunda. La salida limpia es pedirle el permiso a Nasdaq.
- Muestra: los cierres del **2026-09-30** y del **2020-03-20**, contra
  api.nasdaq.com (3.2): diferencia de 0.000 % en los dos.
- Contraste diario completo: 2.513 fechas comunes con api.nasdaq.com
  (2016-10-04 a 2026-10-02). 49 difieren en más de 0.01 puntos; casi todas por
  0.01 a 0.05, unas pocas por más (por ejemplo el 2019-04-25, donde FRED queda
  0.153 % por debajo), y la mayor es de 0.38 %. FRED trae además un valor
  para el 2019-04-19 que la API de Nasdaq no tiene. Sobre el **promedio
  mensual**, esas diferencias pesan como máximo 0.027 % (2023-08).
- Cierres por mes: 21 en agosto y en septiembre de 2026, 22 en marzo de 2020.
  Febrero de 1971 tiene 15: el primer mes completo es **1971-03**.

### 3.2 Otras candidatas

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| Nasdaq (api.nasdaq.com), `/api/quote/COMP/historical?assetclass=index`, originador | leída, **(c)** | Diaria, cierre. Con `fromdate=1971-01-01` devuelve 10.849 filas y la más antigua es del **1984-10-11**. API sin documentación pública; exige cabeceras de navegador. Términos de nasdaq.com: licencia *"solely for your personal, non-commercial use"* y prohibición de copiar o publicar el contenido sin aprobación escrita. **Se usó solo como contraste.** |
| indexes.nasdaqomx.com | parcial, **(c)** | La página "History for COMP" existe; no se exploró. Mismo dueño y mismos términos. |
| Nasdaq Data Link (data.nasdaq.com) | **no sirve** | Ver sección 7. |
| Yahoo Finance `^IXIC` | **(c)** | Es lo que usaba el sitio hasta la fase 3: ver sección 8.2. |

---

## 4. Oro

### 4.1 FRED — leída (negativa)

- `GOLDAMGBD228NLBM` y `GOLDPMGBD228NLBM`: el CSV respondió HTTP 404 en la
  primera pasada. La página de cada serie redirige ahora a un aviso de FRED
  News, literal: *"On January 31, 2022, FRED will no longer include data from
  ICE Benchmark Administration Limited (IBA)."* El aviso dice que las series
  se borran de la base, del complemento de Excel, de las aplicaciones y de las
  API.
- `PGOLDUSDM`: **no existe** (HTTP 404 en la página de la serie).
- Búsqueda "gold price" en FRED, primera página de resultados: ninguna serie
  de precio spot del oro. Lo que aparece son índices de precios del BLS
  (productor, importación, exportación) y un índice "Credit Suisse NASDAQ Gold
  FLOWS103".

### 4.2 LBMA Gold Price (www.lbma.org.uk) — leída, (c)

- Página: `https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices`.
- Convención: dos subastas diarias administradas por ICE Benchmark
  Administration (IBA), a las **10:30 y 15:00 hora de Londres** (texto
  literal: *"set twice daily in auctions ... commencing at 10:30 and 15:00
  London time"*). USD es la moneda de referencia; GBP y EUR son indicativos.
- Unidad: USD por onza troy (convención de la subasta; la página no lo
  escribe en esa frase).
- Acceso a la historia: **"Tables have moved to the MyLBMA Portal. ... In order
  to view this data on our Portal, you will need to have the relevant licence
  from IBA. ... If you do not hold a licence, please contact IBA to obtain
  one."** (literal). El portal es `https://portal.lbma.org.uk/`.
- **Licencia: (c).** La página de IBA
  (`https://www.ice.com/iba/lbma-gold-silver-price`) dice que los benchmarks
  *"are available under licence from IBA"*, incluso para valuación y precios,
  y remite a su equipo de licencias.
- Endpoint JSON histórico (`prices.lbma.org.uk/json/gold_pm.json`): HTTP 403
  de Cloudflare con curl y con navegador. No se pudo ver qué entrega.
- Muestra: ninguna (sin acceso a datos).

### 4.3 World Gold Council, Goldhub (www.gold.org) — leída, (c)

- Página: `https://www.gold.org/goldhub/data/gold-prices`.
- Qué ofrece: *"gold price averages over a range of timeframes (monthly,
  quarterly, annually) going back to 1978"*. Se actualiza semanalmente; unidad
  "currency unit per troy ounce".
- Historia LBMA: *"As of 18 March 2025, only limited LBMA Gold Price data is
  available on our website. Historical LBMA Gold Price data has been removed at
  the request of the ICE Benchmark Administration."* (literal).
- Descarga: el xlsx de promedios devolvió HTTP 403 con una página HTML; la
  página expone un formulario de login para descargar.
- Términos (`https://www.gold.org/terms-and-conditions`, literal): *"You are
  permitted to save, display or print out information contained on this Website
  only for your personal, non-commercial use. Except as otherwise permitted by
  these terms and conditions, you are not permitted to modify, copy, scrape,
  distribute, transmit, display, reproduce, duplicate, publish ... without the
  prior written authorisation of WGC."*
- Conclusión: uso personal y autorización escrita. Excluida.

### 4.4 Deutsche Bundesbank — leída (negativa)

- La serie candidata del borrador, `BBEX3.D.XAU.USD.EA.AC.C06`, **no existe**:
  `https://api.statistiken.bundesbank.de/rest/data/BBEX3/D.XAU.USD.EA.AC.C06`
  responde HTTP 404 ("no results matching the query").
- La consulta comodín `BBEX3/.XAU....` devuelve las únicas tres series de oro
  del conjunto: el fixing de la bolsa de Fráncfort en **marcos por kilo, hasta
  fines de 1998** (anual `A.XAU.DEM.EA.AC.C03`, diaria `D.XAU.DEM.EA.AC.C01`,
  mensual `M.XAU.DEM.EA.AC.C02`). No hay serie en USD ni fixing de Londres.
- No se leyeron los términos de uso del Bundesbank porque no hay serie útil.

### 4.5 Banco Mundial, "Pink Sheet" — leída, (a)

- Página: `https://www.worldbank.org/en/research/commodity-markets`. Archivo
  enlazado el 2026-10-04 como "Monthly prices":
  `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx`
  (586.099 bytes; `Last-Modified: Fri, 02 Oct 2026`). No se verificó que esa
  URL sea estable entre publicaciones: hay que leerla de la página.
- Estructura: hoja `Monthly Prices`, encabezado en las filas 5 (nombre) y 6
  (unidad), datos desde la fila 7. Título de la hoja: "monthly prices in
  nominal US dollars, 1960 to present", "Updated on October 02, 2026". La
  página anuncia la próxima actualización para el 3 de noviembre de 2026.
- Frecuencia nativa: mensual. 801 filas, de `1960M01` a `2026M09`.
- **Convención del oro** (hoja `Description`, literal): *"Gold, spot average of
  daily rates, from June 2025; previously (UK), 99.5% fine, London afternoon
  fixing, average of daily rates"*. Es un promedio mensual de precios diarios
  en los dos tramos, pero **el precio diario cambia de definición en junio de
  2025**: antes era el fixing de la tarde de Londres (la subasta de las 15:00
  de 4.2); desde entonces es "spot", sin hora declarada.
- Unidad y moneda: `($/troy oz)`.
- **Precisión: el archivo trae el oro redondeado al dólar entero** (las 801
  celdas son enteros). El redondeo pesa ±0.5 USD: 1.4 % con el oro a 35,
  0.03 % a 1592, 0.01 % a 4319. Por eso la serie publicada usa este archivo
  solo desde 2025-01: hasta 2024-12 sale de la edición sin redondear (5.5,
  A-R0-19).
- Inicio real: **1960M01 = 35**. En este archivo el valor es 35 hasta 1967M12
  y el primer mes distinto es 1968M01. Es efecto del redondeo: en la edición
  sin redondear el oro va de 34.95 a 35.27 en esos años.
- Clave / registro: no.
- **Licencia: (a), CC BY 4.0.** La página del Pink Sheet enlaza, bajo "Using
  this Data", los términos de los conjuntos de datos del Banco Mundial y la
  sección CC BY de su catálogo. Cláusula, literal
  (`https://www.worldbank.org/ext/en/legal/terms-conditions/datasets`):
  *"Unless specifically labeled otherwise, these Datasets are provided to you
  under a Creative Commons Attribution 4.0 International License (CC BY
  4.0)"*. El catálogo
  (`https://datacatalog.worldbank.org/public-licenses`) dice que esa licencia
  permite copiar, modificar y distribuir *"for any purpose, including
  commercial use"*. Atribución pedida: *"The World Bank: Dataset name: Data
  source (if known)"*.
- **Lo que no cierra del todo.** Los mismos términos tienen una excepción para
  datos de terceros, que *"may not be redistributed or reused without the
  consent of the original data provider"*, y dicen que cuando aplica figura en
  los metadatos. El archivo lista como fuentes del oro a Bloomberg, Kitco, el
  FMI, el mercado de Londres y otros, y **no trae ninguna etiqueta de
  restricción** para el oro ni para la plata. Con lo leído, vale la regla
  general (CC BY 4.0).
- Muestra: **2026M08 = 4411**, **2026M09 = 4319**, **2020M03 = 1592**.
- Contraste (lectura manual de un día, no una fuente): promedio mensual de los
  cierres diarios del futuro de oro de COMEX (Yahoo `GC=F`). En 23 meses
  (2024-11 a 2026-09) el Pink Sheet queda a una mediana de 0.50 % del
  **promedio** del mes y a 1.61 % del **cierre de fin de mes** (máximos 1.56 %
  y 5.59 %). Para 2026M08: Pink Sheet 4411, promedio del futuro 4468.9, cierre
  de fin de mes 4481.5. Un futuro no es el spot, así que el contraste confirma
  que la serie es un promedio y no un cierre; no valida el nivel al centavo.

### 4.6 USGS, Mineral Commodity Summaries — leída, dominio público

Evaluada como fuente de contraste para el gate de oro y plata (9.6). Vale para
los dos metales.

- Publicación: *Mineral Commodity Summaries 2026*, de febrero de 2026
  (`https://doi.org/10.3133/mcs2026`). Capítulos:
  `https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gold.pdf` (138.864 bytes)
  y `https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-silver.pdf` (138.760
  bytes).
- Frecuencia nativa: **anual**. La tabla "Salient Statistics—United States"
  trae cinco años, de 2021 a 2025, y marca el último como estimado.
- **Convención del oro** (fila "Price, dollars per troy ounce", nota 5,
  literal): *"Engelhard's average gold price quotation for the year. In 2025,
  the price was estimated by the U.S. Geological Survey based on data from
  January through November."*
- **Convención de la plata** (fila "Price, bullion, average, dollars per troy
  ounce", nota 4, literal): *"Engelhard's industrial bullion quotations.
  Source: S&P Global Platts Metals Week."*
- Es el promedio anual de la cotización de un comerciante de Estados Unidos, no
  del fixing de Londres. Es una cotización independiente de la que usa el Banco
  Mundial.
- Unidad y moneda: USD por onza troy. El oro viene al dólar entero y la plata
  al centavo.
- Valores leídos:

  | | 2021 | 2022 | 2023 | 2024 | 2025 (estimado) |
  | --- | --- | --- | --- | --- | --- |
  | Oro | 1801 | 1802 | 1945 | 2388 | 3300 |
  | Plata | 25.23 | 21.88 | 23.54 | 28.37 | 38 |

- Clave / registro: no.
- **Licencia: dominio público.** Política del USGS
  (`https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits`),
  literal: *"USGS-authored or produced data and information are considered to
  be in the U.S. Public Domain."* La misma página dice que el material de
  terceros con copyright suele ir marcado; la tabla de precios no lleva ninguna
  marca. De todos modos aquí no se copia el documento: se transcriben ocho
  cifras, con su cita.

### 4.7 FMI, Primary Commodity Prices — leída, (b), control mensual

- Página: `https://www.imf.org/en/research/commodity-prices`. Archivo enlazado
  como "Excel Database: September 2026":
  `https://www.imf.org/-/media/files/research/commodityprices/monthly/external-data.xlsx`
  (619.264 bytes).
- Estructura: una hoja, `External`. Las cuatro primeras filas son el código, la
  descripción, el tipo de dato y la frecuencia; los datos van de `1980M1` a
  `2026M8`, 560 filas.
- Frecuencia nativa: mensual.
- **Convención** (fila de descripción, literal). `PGOLD`: *"Gold, Fixing
  Committee of the London Bullion Market Association, London 3 PM fixed price,
  US$ per troy ounce"*. `PSILVER`: *"Silver, London Bullion Market Association,
  USD/troy ounce"*.
- Precisión: sin redondear (2024M12: 2640.6055 el oro y 30.3707 la plata).
- Clave / registro: no.
- **Licencia: (b), reutilización libre con atribución; uso comercial con
  permiso.** La página "Copyright and Usage"
  (`https://www.imf.org/en/about/copyright-and-terms`, vigente desde el
  2024-10-11) tiene términos especiales para los datos estadísticos, y nombra a
  *Primary Commodity Prices* entre ellos. Cláusulas, literales:
  - *"You may download, extract, copy, create derivative works, publish,
    distribute, and use Data obtained from IMF Sites, subject to the following
    conditions"*.
  - Atribución: *"it must appear accurately with attribution to the IMF as the
    source, e.g. 'Source: International Monetary Fund, Database Name, <<link to
    the dataset>>.'"*
  - Uso comercial: *"For any potential commercial reuse of IMF Data, please
    email copyright@imf.org to request permission."*
  - Descarga: *"The IMF prohibits the bulk download of information by automated
    technology without explicit permission"*. Está en los términos generales,
    que siguen valiendo para los datos.
- **Por qué no es el gate.** Comparte el origen con el Pink Sheet —el fixing de
  Londres—, así que contrasta cómo procesa el dato el Banco Mundial más que el
  precio.
- **Qué es: el control mensual** (A-R0-20). Cada corrida compara el oro y la
  plata publicados contra `PGOLD` y `PSILVER`, sobre los 560 meses en común.
  Por la cláusula de descarga, el pipeline no baja el archivo: usa una copia
  bajada una vez, el 2026-10-04, versionada en
  `data/raw/fmi_pcps_2026-10-04.xlsx` (sha256
  `e0bc0cbbd08208e9868fb16e21992ff4b86a7676a2b5f64d32a02bdb8bdcc464`).

Comparación de las tres fuentes sobre los años del gate. Es una lectura de un
día, no un contraste del pipeline. La columna del Banco Mundial es la serie
empalmada (5.5), que en estos años viene sin redondear:

| Año | Metal | Banco Mundial, doce meses | FMI, doce meses | USGS | BM contra FMI | BM contra USGS |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | Oro | 1799.63 | 1799.77 | 1801 | −0.008 % | −0.076 % |
| 2022 | Oro | 1800.60 | 1801.53 | 1802 | −0.051 % | −0.078 % |
| 2023 | Oro | 1942.67 | 1943.07 | 1945 | −0.021 % | −0.120 % |
| 2024 | Oro | 2387.70 | 2387.21 | 2388 | 0.021 % | −0.012 % |
| 2021 | Plata | 25.165 | 25.166 | 25.23 | −0.006 % | −0.259 % |
| 2022 | Plata | 21.794 | 21.771 | 21.88 | 0.108 % | −0.391 % |
| 2023 | Plata | 23.399 | 23.398 | 23.54 | 0.001 % | −0.601 % |
| 2024 | Plata | 28.269 | 28.226 | 28.37 | 0.153 % | −0.355 % |

Mes a mes, con la serie empalmada, el Pink Sheet y el FMI difieren en una
mediana de 0.02 % en el oro y de 0.10 % en la plata (560 meses, 1980-01 a
2026-08). Con la edición vigente redondeada, que es como se leyó primero, eran
0.06 % y 0.35 %: casi toda la diferencia era el redondeo. En la plata no es
pareja: 0.08 % de mediana hasta 2020, 0.23 % entre 2021 y 2024, y 0.63 % desde
junio de 2025, con un máximo de 3.76 % en diciembre de 2025 (Banco Mundial
62.3, FMI 64.73).

**El control mensual.** Con el umbral de A-R0-20 —la tolerancia del gate, ±0.5 %
el oro y ±1 % la plata— quedan en disputa diez meses del oro y diez de la
plata, de 560 comparados por metal. La lista, con los dos valores de cada mes,
está en A-R0-20 y en el changelog de cada corrida. El que más se aparta en el
oro es **marzo de 1985**: 313.5 en el Pink Sheet y 303.94 en el FMI, a 3.1 %.

**Marzo de 1985: el tercer valor.** Lectura puntual, del 2026-10-04.

- Fuente: U.S. Bureau of Mines, *Minerals Yearbook 1985*, volumen I, *Metals
  and Minerals*, capítulo "Gold", de J. M. Lucas, tabla 13, "U.S. gold prices"
  (*Dollars per troy ounce*), página 466. Nota 1 de la tabla, literal:
  *"Engelhard Industries daily quotation."*
- Dónde se leyó: `https://archive.org/details/pub_usgov-minerals-yearbook_1985_1`,
  la copia digitalizada del Internet Archive. Se leyó el texto y se comprobó
  contra la imagen de la página.
- La fila, literal: *March: Low 287.65 (Mar. 1); High 330.80 (Mar. 27); Average
  304.34*. Los doce promedios mensuales de la tabla promedian 317.66, que es el
  promedio anual que la misma tabla trae.
- Es una cotización **independiente** de las otras dos: la de un comerciante de
  Estados Unidos, no el fixing de Londres. Es la misma cotización contra la que
  cierra el gate anual (4.6).
- Licencia: es una publicación del gobierno federal de Estados Unidos. Aquí no
  se copia: se transcriben cifras, con su cita.

| Mes | Pink Sheet | FMI | Engelhard | Pink Sheet contra Engelhard | FMI contra Engelhard |
| --- | --- | --- | --- | --- | --- |
| 1985-03 | 313.5 | 303.94 | 304.34 | 3.01 % | −0.13 % |
| 1985-11 | 321.5 | 325.24 | 325.64 | −1.27 % | −0.12 % |

En los doce meses de 1985 el FMI queda entre −0.32 % y −0.01 % de Engelhard,
siempre un poco por debajo: es el mismo sesgo de A-R0-18. El Pink Sheet queda
entre −0.31 % y 0.46 % en diez meses, y se aparta en los dos de la tabla.

**Qué zanja.** En marzo de 1985 —y, con la misma tabla, en noviembre— **el valor
que cierra contra una cotización independiente es el del FMI.** El del Pink
Sheet queda a 3 % de las otras dos fuentes, que entre sí están a 0.13 %. La
lectura es que el valor del Pink Sheet de ese mes está mal.

**Qué no cambia.** El valor publicado. La serie sigue siendo el Pink Sheet tal
como viene: marzo de 1985 se publica como 313.5, marcado como valor en disputa
y fuera de las métricas. Lo que corresponde es reportarlo al Banco Mundial
(10.3). Los otros dieciocho meses en disputa no tienen tercera lectura.

---

## 5. Plata

### 5.1 FRED — leída (negativa)

- `SLVPRUSD`: HTTP 404 en el CSV; la página redirige al mismo aviso de retiro
  de los datos de IBA que el oro (4.1).
- Búsqueda "silver" en FRED, primera página de resultados: ninguna serie
  vigente de precio spot. Aparecen "Price of Bar Silver for London, Great
  Britain" (`A04018GB00LONA286NNBR`, no leída), un índice de precios de
  importación y un índice "Credit Suisse NASDAQ Silver FLOWS106".

### 5.2 LBMA Silver Price — leída, (c)

- Misma página que 4.2. Convención: una subasta diaria a las **12:00 del
  mediodía, hora de Londres** (literal: *"set daily in an auction ...
  commencing at 12:00 noon London time"*). Mismo régimen de licencia de IBA
  que el oro.

### 5.3 Banco Mundial, "Pink Sheet" — leída, (a)

- Mismo archivo, misma licencia y mismas salvedades que 4.5.
- **Convención** (hoja `Description`, literal): *"Silver (UK), 99.9% refined,
  London afternoon fixing; prior to July 1976 Handy & Harman. Grade prior to
  1962 unrefined silver."* Dos cosas que esa frase **no** resuelve:
  1. No dice "average of daily rates" como sí lo dice la del oro. Que la plata
     sea un promedio mensual sale del título de la hoja ("monthly prices") y
     del contraste de abajo, no de la descripción.
  2. Habla de un fixing de la tarde, y la página de LBMA dice que la subasta
     de plata es a las 12:00 del mediodía (5.2). Las dos frases están leídas;
     no se pudo establecer cuál describe el dato actual.
- Unidad y moneda: `($/troy oz)`.
- **Precisión: redondeada a un decimal** (las 801 celdas). El redondeo pesa
  ±0.05 USD: 5.6 % con la plata a 0.9, 1.2 % a 4.2, 0.34 % a 14.9, 0.08 % a
  64.6. La plata está por debajo de 5 USD en 304 de los 801 meses; el último
  es 2003M07. Como en el oro, la serie publicada usa este archivo solo desde
  2025-01 (5.5, A-R0-19).
- Inicio real: **1960M01 = 0.9**.
- Muestra: **2026M08 = 65.4**, **2026M09 = 64.6**, **2020M03 = 14.9**.
- Contraste (misma lectura manual que 4.5, con Yahoo `SI=F`): en 23 meses el
  Pink Sheet queda a una mediana de 0.18 % del **promedio** mensual de los
  cierres del futuro y a 3.79 % del **cierre de fin de mes** (máximos 3.59 % y
  14.99 %). Para 2026M08: Pink Sheet 65.4, promedio 65.28, fin de mes 66.22.
  La serie se comporta como un promedio mensual.

### 5.4 Otras candidatas para plata

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| Deutsche Bundesbank | **no sirve** | La consulta `BBEX3/.XAG....` responde HTTP 404: no publica plata. |
| Yahoo Finance `SI=F` | **(c)** | Futuro de COMEX, no spot. Es lo que usaba el sitio hasta la fase 3: ver sección 8.2. |

No apareció ninguna fuente diaria de plata que se pueda publicar. La única
fuente (a) es mensual.

### 5.5 La edición sin redondear del Pink Sheet — leída, (a)

El Pink Sheet vigente redondea el oro al dólar y la plata a un decimal. El
propio Banco Mundial publicó la misma serie **sin redondear** hasta su edición
del 3 de enero de 2025, y ese archivo sigue respondiendo. Primero fue una
propuesta; **está implementada desde el 2026-10-04** (A-R0-19).

- URL:
  `https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx`.
  Es la dirección que el archivo tenía en ediciones anteriores; la página
  actual no la enlaza. Leída el 2026-10-04.
- Edición: "Updated on January 03, 2025" (cabecera `Last-Modified` del mismo
  día). 765.246 bytes, sha256
  `bd89b83eeceadaecb803018c104f76b316d2df3fae28ef7afde48021100c7e11`.
- Cobertura: 780 meses, de `1960M01` a `2024M12`.
- Precisión: sin redondear, y **sin una precisión declarada**. Plata: 0.9137
  (1960M01), 4.1925 (1975M01), 9.8652 (2008M11), 14.884 (2020M03). Oro: 35.27,
  176.27, 760.863 y 1591.93 en esos mismos meses. Cada mes trae los decimales
  que tenga: el oro, dos en 610 de los 780 meses, uno en 80 y ninguno en 10; la
  plata, cuatro o cinco en 535 y tres en 217.
- **Es la misma serie.** Redondear esta edición reproduce la vigente en los 780
  meses del oro y en los 780 de la plata: ninguno queda a más de medio paso de
  redondeo. Doce quedan exactamente a medio paso, once del oro y uno de la
  plata: son valores terminados en ,5 justo, como 1848.5 en mayo de 2022, que
  la edición vigente publica como 1849. Ahí las dos formas de redondear son
  válidas.
- Convención: la descripción de la plata es la misma que hoy. La del oro es la
  anterior al cambio de junio de 2025: *"Gold (UK), 99.5% fine, London
  afternoon fixing, average of daily rates"*.
- Licencia: la del Pink Sheet, CC BY 4.0, clase (a). Es el mismo editor y el
  mismo conjunto de datos.

**Cómo se usa.**

1. **El empalme.** Esta edición da 1960-01 a 2024-12; la vigente, desde
   2025-01. `precios_mensuales.csv` dice de cuál sale cada mes.
2. **La copia versionada es la que vale.** El archivo está en
   `data/raw/pink_sheet_edicion_2025-01-03.xlsx` y el pipeline lo identifica por
   su hash. No depende de que la URL siga respondiendo.
3. **El control.** En cada corrida, redondear esta edición tiene que reproducir
   la vigente en todos los meses que comparten; los que quedan exactamente a
   medio paso se listan en el changelog. Si un mes no coincide, la corrida se
   detiene: quiere decir que el Banco Mundial revisó un dato anterior a 2025.
4. **El error por redondeo** de cada mes es el de la edición de la que sale. En
   esta, media unidad del último decimal publicado de cada valor.

**Qué resolvió.** Oro/Plata es apto para métricas desde 1968-04, 702 de 801
meses; con la edición vigente sola lo era desde 2009-02 (A-R0-17). Lo que corta
en 1968 son dos meses del oro, febrero y marzo, que esta edición trae sin
decimales: 36 y 37.

**Lo que no resuelve.**

1. **Es una edición congelada.** No recibe las revisiones que el Banco Mundial
   haga después de enero de 2025; lo que hay es el control, que las detecta.
2. **Desde 2025-01 la serie sigue redondeada.** Preguntarle al Banco Mundial si
   publica la serie sin redondear en algún lugar vigente sigue entre las
   preguntas de la sección 10.3.
3. **Los demás límites siguen:** el quiebre del oro de junio de 2025 y la
   convención de la plata como estimación.

**Otra candidata, más débil.** La serie `PSILVER` del FMI (4.7) también viene
sin redondear, pero arranca en 1980, no es del mismo editor, y sus términos
prohíben la descarga masiva automatizada.

---

## 6. BTC

### 6.1 Bitstamp, velas diarias BTC/USD — leída

- URL: `https://www.bitstamp.net/api/v2/ohlc/btcusd/?step=86400&limit=1000&start=<unix>`.
  Parámetros según la documentación (`https://www.bitstamp.net/api/`): `step`
  en segundos (86400 = diario), `limit` entre 1 y 1000, `start` y `end` como
  unix timestamp, `exclude_current_candle=true` para omitir la vela abierta.
- Frecuencia nativa: diaria, con `timestamp` a las **00:00 UTC** del día que
  abre la vela.
- **Convención: cierre de la vela diaria UTC** (último trade antes de las
  24:00 UTC). La vela del día en curso aparece abierta.
- Unidad y moneda: USD por BTC.
- Inicio real: **2011-08-18 (cierre 10.90)**, leído en la segunda pasada: un
  `start` del 2011-08-01 con `limit=1000` devuelve 983 velas a partir de esa
  fecha. **Corrige al borrador**, que daba 2011-09-13: esa vela existe (cierre
  5.97) pero no es la primera. La historia completa son 5.527 velas hasta el
  2026-10-04, sin días faltantes, en 6 pedidos.
- Clave / registro: no para datos públicos. Límites declarados: 400 pedidos
  por segundo, 10.000 por 10 minutos.
- **Licencia: (b) por inferencia, no por cláusula.** La documentación de la
  API (releída con navegador en la segunda pasada, mismo texto) dice, literal:
  *"Companies seeking to utilize Bitstamp's exchange data for their own
  commercial purposes are directed to contact partners@bitstamp.net to receive
  and sign a commercial use Data License Agreement. Bitstamp allows the
  incorporation and redistribution of our exchange data for commercial
  purposes. This includes the right to create ratios, calculations, new
  original works, statistics, and similar, based on the exchange data."* El
  uso comercial exige un acuerdo firmado; sobre el uso no comercial no hay
  frase. La página `/legal/` lista documentos por entidad (siete) y ninguno es
  una licencia general de datos.
- Muestra: cierre del **2026-09-30 = 83562.58** USD; cierre del
  **2020-03-20 = 6210.14** USD. Contraste en 6.4.

### 6.2 Coin Metrics, API community, métrica `PriceUSD` — leída, (b)

- URL: `https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=PriceUSD&frequency=1d&page_size=10000`.
  La documentación da como raíz de la API community
  `https://api.coinmetrics.io/v4`, sin clave; ese host no se probó.
- Frecuencia nativa: diaria.
- **Convención** (descripción oficial de la métrica, leída de
  `/v4/reference-data/asset-metrics?metrics=PriceUSD`, literal): *"The fixed
  closing price of the asset as of 00:00 UTC the following day (i.e., midnight
  UTC of the current day) denominated in USD. This price is generated by Coin
  Metrics' fixing/reference rate service."* Es un fixing a las 00:00 UTC, no
  un último trade. La fila fechada el día D describe el precio de las 00:00
  UTC del día D+1, es decir, el cierre del día D en UTC.
- Unidad y moneda: USD.
- Inicio real: **2010-07-18 = 0.08584**.
- Volumen: un solo pedido devuelve la historia completa, **5.922 filas del
  2010-07-18 al 2026-10-03, sin paginación y sin días faltantes** (segunda
  pasada; mismo conteo que en la primera).
- Clave / registro: no. Límite declarado: 10 pedidos por ventana de 6 segundos
  por IP.
- **Licencia: (b), CC BY-NC 4.0.** Página
  `https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.md`,
  literal: *"Available to the community under the Creative Commons license."*
  El enlace de esa frase apunta a
  `https://creativecommons.org/licenses/by-nc/4.0/`. La misma página remite a
  una página "Labs" para más detalle de los términos community; esa URL
  redirige hoy a talos.com y no muestra términos.
- Muestra: **2026-09-30 = 83579.67**; **2020-03-20 = 6174.15**.
- Nota: la métrica `ReferenceRateUSD` en la API community solo tiene historia
  desde 2026-09-27 (primera pasada); la documentación confirma que el acceso
  community a las tasas de referencia granulares está limitado. Para historia
  larga la métrica community es `PriceUSD`.

### 6.3 blockchain.info, gráfico "Market Price (USD)" — leída, (c)

- URL: `https://api.blockchain.info/charts/market-price?timespan=all&format=csv&sampled=false`.
- Frecuencia nativa: diaria (6.484 filas entre 2009-01-03 y 2026-10-04).
- **Convención** (descripción que devuelve la propia API, literal):
  *"Average USD market price across major bitcoin exchanges."* Es un promedio
  entre exchanges, no un cierre; la hora de referencia no está declarada.
- Unidad y moneda: USD.
- Inicio real: filas desde 2009-01-03 con valor 0.0; **primer valor distinto
  de cero: 2010-08-18 = 0.07**.
- Clave / registro: no para este endpoint.
- **Licencia: (c).** Los términos de uso de blockchain.com
  (`https://www.blockchain.com/legal/terms`) ponen el contenido a disposición
  *"for your personal, lawful, non-commercial use only"* y prohíben usarlo
  para fines públicos o comerciales. El acuerdo de la API
  (`https://www.blockchain.com/legal/api-terms`, actualizado el 2026-08-13) es
  una licencia aparte que incorpora esos términos y prohíbe copiar, almacenar
  o guardar en caché el contenido fuera de lo que el acuerdo permite.
- Muestra: **2026-09-30 = 83629.12**; **2020-03-20 = 6195.2**.

### 6.4 Contraste entre fuentes de BTC

Por día:

| Fecha | Bitstamp (cierre vela UTC) | Coin Metrics (fix 00:00 UTC) | Coinbase Exchange (cierre vela UTC) | FRED `CBBTCUSD` (5 PM PST) | blockchain.info (promedio) | CoinGecko (00:00 UTC, inicio del día) |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-30 | 83562.58 | 83579.67 | 83556.14 | 83482.51 | 83629.12 | 83640.10 |
| 2020-03-20 | 6210.14 | 6174.15 | 6206.10 | 6215.40 | 6195.2 | sin acceso (sección 7) |

Describen instantes o agregados distintos del mismo día. El valor de CoinGecko
es el del **inicio** del día: coincide con la apertura de la vela de Coinbase
(83638.42) y con el spot con fecha de Coinbase (83638.415), no con los cierres.

Por mes, que es la convención objetivo: promedio de los cierres diarios de
Bitstamp contra promedio del `PriceUSD` diario de Coin Metrics, todos los días
calendario.

| Mes | Bitstamp | Coin Metrics | Diferencia |
| --- | --- | --- | --- |
| 2026-09 (30 días) | 80472.02 | 80473.08 | 0.001 % |
| 2026-08 (31 días) | 69488.29 | 69472.36 | 0.023 % |
| 2020-03 (31 días) | 6872.22 | 6885.04 | 0.186 % |

Sobre toda la historia común (181 meses, 2011-09 a 2026-09):

| Desde | Meses | Mediana | Percentil 95 | Máxima |
| --- | --- | --- | --- | --- |
| 2011-09 | 181 | 0.052 % | 1.146 % | 8.838 % (2011-11) |
| 2012-01 | 177 | 0.050 % | 0.872 % | 2.340 % (2012-02) |
| 2013-01 | 165 | 0.044 % | 0.432 % | 1.314 % (2017-12) |
| 2015-01 | 141 | 0.035 % | 0.368 % | 1.314 % (2017-12) |

En 2011 las dos fuentes se apartan entre 4 % y 9 % por mes; desde 2013 nunca
más de 1.31 %.

### 6.5 Otras candidatas para BTC

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| FRED `CBBTCUSD` (Coinbase) | leída, **(c)** | Diaria, 7 días ("Daily, 7-Day"), USD. Nota de la serie: *"All data is as of 5 PM PST."* Inicio **2014-12-01 = 370.00**; 4.325 filas hasta 2026-10-03. La nota dice que reproducir datos de Coinbase está prohibido salvo permiso escrito de Coinbase; la etiqueta de la serie es "Copyrighted: Citation Required". Los dos textos no dicen lo mismo y vale el más restrictivo. |
| Coinbase Exchange, `https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400` | leída, **(c)** | Velas `[time, low, high, open, close, volume]`, `time` = inicio del intervalo; máximo 300 velas por pedido; la documentación advierte que la historia puede estar incompleta. Un pedido para 2015-01-01 a 2015-10-01 devuelve velas desde el **2015-07-20**. Términos de datos de mercado de Coinbase (`https://www.coinbase.com/legal/market_data`): uso *"exclusively for you or your entity's personal or research purposes"* y prohibición de redistribuir o mostrar a terceros los datos **o trabajos derivados** sin consentimiento escrito. |
| Coinbase, `api.coinbase.com/v2/prices/BTC-USD/spot?date=<fecha>` | **no sirve para historia** | Responde para fechas recientes (2026-09-30 = 83638.415) y devuelve `rate not found` para 2020-03-20, 2015-01-02 y 2014-12-01 (primera pasada). Mismos términos de Coinbase. |
| Kraken, `https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440` | **no sirve para historia por API** | La documentación dice que devuelve hasta 720 entradas, las más recientes, sin importar `since`; un pedido con `since` de 2010 devolvió velas desde el 2024-10-14. La historia completa se ofrece como archivos ZIP trimestrales (hasta el 2026-06-30, en partes de ~2 GB); no se descargaron. No se localizaron términos sobre datos de mercado. |
| CoinGecko | **no sirve para historia** | Ver secciones 7 y 8. |

### 6.6 Desde cuándo son confiables los precios de BTC

Lo que se puede decir con lo leído: hay un precio diario de un exchange que
sigue operando (Bitstamp) desde el 2011-08-18, y un fixing multi-exchange de
Coin Metrics desde el 2010-07-18. Antes de 2011-08 solo hay agregados
(blockchain.info, Coin Metrics) sin una segunda fuente independiente contra la
que contrastarlos. Entre 2011-09 y 2012-12 hay dos fuentes, pero no coinciden:
el promedio mensual difiere hasta 8.8 % (6.4). Desde 2013-01 coinciden dentro
de 1.31 %.

Fijar la fecha de "confiable" es un supuesto (A-R0-10), no un dato.

---

## 7. Fuentes que no sirven (leídas)

| Fuente | Qué pasó el 2026-10-04 |
| --- | --- |
| CoinGecko, API pública | `market_chart?days=max` y `days=3650` devuelven HTTP 401 con el mensaje literal *"Public API users are limited to querying historical data within the past 365 days. Upgrade to a paid plan to enjoy full historical data access"* (confirmado en las dos pasadas; la segunda a las 13:48 UTC). `history?date=20-03-2020` también 401. Con `days=365` responde. Sirve para los últimos 365 días, no para una serie histórica. |
| Stooq | La portada y el CSV de `^spx` devuelven un desafío JavaScript (prueba de trabajo SHA-256) en las dos pasadas. No es legible sin un navegador. |
| Yahoo Finance | Técnicamente responde desde una máquina con salida directa (HTTP 200); en la primera pasada devolvía HTTP 429. Queda fuera por sus términos, no por el acceso: ver sección 8. |
| Nasdaq Data Link (`data.nasdaq.com`), conjunto `LBMA/GOLD` | HTTP 403 con una página de Incapsula (anti-bots) incluso antes de pedir clave; la página del conjunto `LBMA` devuelve 404 (primera pasada). |
| World Gold Council | Ver 4.3: descarga con login y términos de uso personal. |
| Deutsche Bundesbank | Ver 4.4 y 5.4: no publica oro en USD ni plata. |
| FRED, oro y plata | Ver 4.1 y 5.1: series de IBA retiradas en 2022; `PGOLDUSDM` no existe. |
| Kraken, API OHLC | Ver 6.5: solo las últimas 720 velas. |

---

## 8. Fuentes que usa el sitio

**Actualizada el 2026-10-05, con la fase 3.** El sitio ya no consulta ninguna
fuente externa: ni Yahoo, ni CoinGecko, ni FRED. Lee los archivos de
`data/series/` cuando se construye y no vuelve a pedir datos: no hay precios en
vivo ni API propia. La sección 8.1 dice qué usa ahora; la 8.2 conserva, sin
cambios, la lectura del 2026-10-04 de lo que usaba antes; la 8.3 dice qué pasó
con cada cosa.

### 8.1 Lo que usa desde la fase 3

Leído el 2026-10-05 del código de la fase 3: `src/lib/series.ts`,
`src/app/page.tsx` y `src/app/fuentes/page.tsx`.

| Archivo de `data/series/` | Qué muestra el sitio con él |
| --- | --- |
| `ratios.csv` | El nivel mensual de los pares publicados (hoy Oro / Plata y BTC / Oro), su error máximo por redondeo y qué meses son aptos para métricas. |
| `pares.csv` | Los cinco pares. De los publicados: el estado, el rango de meses y el último dato. De los demás: solo el nombre y el estado NO MEDIDO, sin gráfico ni valor. |
| `series.csv` | De cada serie: fuente, unidad, licencia, **atribución** y validación, tal cual. Van bajo cada gráfico y en la página `/fuentes`. |
| `precios_mensuales.csv` | Solo las columnas `oro_contraste_fmi` y `plata_contraste_fmi`: los dos valores de un mes en disputa y qué meses están "sin comparar" (A-R0-20). |
| `descargas_ratios.csv` | La tabla de descargas de `/fuentes`: fuente, fecha, URL y SHA-256. |

Si uno de los cinco falta, está mal formado o contradice a otro, el sitio no se
construye. No hay respaldo.

Las fuentes de origen son las de la sección 9.2: el Pink Sheet para el oro y la
plata, y Coin Metrics community para BTC. Del FMI el sitio muestra los valores
de los meses en disputa, con su atribución, que viene en la columna `validacion`
de `series.csv`. Del S&P 500 y del Nasdaq Composite no muestra ningún nivel.

**Una fuente citada que no es una serie.** La portada dice que la plata es un
metal "de uso mayormente industrial", y `/fuentes` cita de dónde sale. Leído el
2026-10-05, a las 12:23 UTC: la página "Silver Supply & Demand" del Silver
Institute (`https://silverinstitute.org/silver-supply-demand/`), que dice estar
adaptada en parte del *World Silver Survey 2025*, y su tabla "Silver Supply and
Demand", en millones de onzas, con el pie "Source: Metals Focus"
(`https://silverinstitute.org/wp-content/uploads/2025/06/Silver-S-D-2025.jpg`).

- Para 2024: *Industrial (total)* 680.5 y *Total Demand* 1164.1, el 58.5 %.
- De 2016 a 2024 la partida industrial pasa de la mitad del total en siete de
  los nueve años. En 2016 (491.0 de 993.3, 49.4 %) y en 2022 (592.3 de 1284.2,
  46.1 %), no.
- Las cifras se transcribieron de la imagen de la tabla. Las de 2024 cierran
  con la suma de sus partidas y con el texto de la misma página (*"Total
  silver demand fell by 3 percent to 1.16 billion ounces (Boz) in 2024"*).
- Es una sola fuente: no se contrastó con una segunda.
- Licencia: el aviso legal del sitio
  (`https://silverinstitute.org/legal-disclaimer/`) no trae una cláusula sobre
  reutilizar los datos. Aquí no se copia la tabla: se transcriben seis cifras,
  con su cita.
- **No leído:** el *World Silver Survey 2026*, que la página de publicaciones
  ya lista.

**Las tablas de CAGR y de poder adquisitivo ya no están en el código.** El
sitio las nombra con el estado NO MEDIDO y nada más. Sus cifras eran valores de
referencia escritos a mano, sin procedencia verificada, y entre ellos había
niveles anuales del S&P 500 y del Nasdaq Composite. Se eliminaron del código
el 2026-10-05, con los componentes que solo existían para mostrarlas: las
anclas de `src/lib/data.ts` y `src/lib/currency.ts` entero. Si esas tablas se
publican, leerán de `data/series/`, como los ratios.

### 8.2 Lo que usaba hasta la fase 3: lectura del 2026-10-04

Lo que sigue se conserva como se escribió ese día, en presente. Describe un
código que la fase 3 eliminó (`src/lib/market-api.ts` y la ruta
`/api/market-data`) y un pie de página que ya no nombra esas fuentes.

Leído del código en `origin/main` (`1823a93`), archivo `src/lib/market-api.ts`,
y del pie de página (`src/components/Footer.tsx`). Sirve para saber qué hay que
reemplazar.

| Dato | Qué pide el código | Qué convención sale de ahí | Licencia |
| --- | --- | --- | --- |
| S&P 500, Nasdaq Composite | `https://query1.finance.yahoo.com/v8/finance/chart/<símbolo>?range=10y&interval=1mo` para `^GSPC` y `^IXIC`, con la cabecera `User-Agent: Mozilla/5.0`. Toma el `close` de cada vela mensual. | **Cierre de fin de mes.** Verificado: las velas mensuales de `^GSPC` de junio a septiembre de 2026 coinciden con el cierre del último día hábil de cada mes en Cboe (diferencia de 0.000 % en las cuatro). La vela del mes en curso trae el último precio. | **(c).** Ver abajo. |
| Oro, plata | El mismo endpoint para `GC=F` y `SI=F`. | Cierre de fin de mes de un **futuro de COMEX**, no del spot. Yahoo los identifica como `instrumentType: FUTURE`, bolsa `CMX`, contrato de diciembre de 2026. | **(c).** |
| BTC, historia | `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=3650&interval=daily`, sin clave. Se queda con la primera observación de cada mes. | **Precio del día 1 de cada mes a las 00:00 UTC**: una tercera convención, distinta de las dos de arriba. Pero ese pedido **responde HTTP 401** (sección 7), y con menos de 24 meses el código cae a `BTC_STATIC_ANCHORS`: 13 cifras de diciembre (2013 a 2025) escritas a mano e interpoladas. No se observó el sitio desplegado; es lo que se sigue del código y de la respuesta de hoy. | Plan gratuito: no da la historia. |
| BTC, precio actual | `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin`. Pisa el último punto de la serie. | Precio spot del momento. No se probó hoy. | Ver abajo. |
| M2 | `https://api.stlouisfed.org/fred/series/observations?series_id=M2SL&frequency=m`, con `FRED_API_KEY`. | Mensual, "Billions of Dollars, Seasonally Adjusted"; fuente: Board of Governors, H.6. Último dato: agosto de 2026 = 23342.8. | **(a).** Ver abajo. |

El sitio mezcla hoy tres convenciones en un mismo ratio: cierre de fin de mes
(índices y metales), primer día del mes (BTC, cuando CoinGecko respondía) y
anclas anuales interpoladas (BTC, hoy).

**Yahoo — (c), hay que reemplazarlo.** Términos de servicio
(`https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html`): prohíben acceder
o recolectar datos *"using any automated means"* sin permiso expreso previo,
reutilizar los servicios con fines comerciales, y reproducir o distribuir
cualquier parte de ellos, API incluidas, sin permiso escrito explícito. El
endpoint `query1.finance.yahoo.com` no es una API documentada de Yahoo, y el
código se presenta como un navegador. Afecta a las cuatro series que salen de
ahí.

**CoinGecko — no alcanza.** Los términos de la API
(`https://www.coingecko.com/en/api_terms`) dan una licencia cuyo alcance
depende del plan; exigen mostrar de forma destacada el mensaje *"Powered by
CoinGecko"* y prohíben redistribuir el acceso a la API. La página de planes
marca el plan gratuito como "Attribution required", le da un año de historia
diaria, y lista la licencia de redistribución comercial en el plan Enterprise.
El sitio nombra a CoinGecko en el pie, pero la frase exigida no aparece en
`src/`. Para la historia, el plan gratuito no sirve.

**FRED `M2SL` — (a), con un aviso que falta.** La etiqueta de la serie es
"Public Domain: Citation Requested": según los términos de FRED se puede usar
sin permiso, citando la fuente y que se obtuvo por FRED. Los términos de la API
(`https://fred.stlouisfed.org/docs/api/terms_of_use.html`) exigen además poner
de forma destacada el aviso *"This product uses the FRED® API but is not
endorsed or certified by the Federal Reserve Bank of St. Louis."* Ese aviso no
aparece en `src/`.

### 8.3 Qué pasó con cada una en la fase 3

| Lo que usaba | Qué pasó |
| --- | --- |
| Yahoo `GC=F`, `SI=F` | Se dejó de consultar. El oro y la plata salen del Pink Sheet. |
| Yahoo `^GSPC`, `^IXIC` | Se dejó de consultar. El S&P 500 y el Nasdaq Composite se calculan en el pipeline y no se muestran: sus pares figuran como NO MEDIDO. |
| CoinGecko, historia y precio actual | Se dejó de consultar. BTC sale de Coin Metrics community. El sitio no muestra un precio del momento. |
| `BTC_STATIC_ANCHORS` y la serie mensual interpolada entre anclas | Eliminadas. Las anclas anuales que quedaban en `src/lib/data.ts` para la tabla de CAGR se eliminaron después, el 2026-10-05, con la tabla (8.1). |
| FRED `M2SL` | Se dejó de consultar. El dato se pedía y se nombraba en el pie, pero ningún gráfico ni tabla lo mostraba. La sección 9.8 preveía conservarlo y agregar el aviso de la API; sin la API, el aviso no hace falta. Ningún código lee ya `FRED_API_KEY`. |

El pipeline de S2 sigue leyendo FRED por CSV, sin clave: eso no es el sitio.
---

## 9. Decisiones

**Aprobadas el 2026-10-04, con condiciones.** Los supuestos que las sostienen
están en `SUPUESTOS.md`, numerados A-R0-1 a A-R0-20; aquí va la decisión y la
evidencia.

### 9.1 Regla de publicación

Una serie se publica si pasa dos filtros (A-R0-14). **La licencia:** tiene que
permitir publicar sin interpretación (CC BY, dominio público, o CC BY-NC dado
el uso no comercial del sitio). **La validación:** su contraste contra una
segunda fuente tiene que haber cerrado (9.6). La tabla de abajo es el estado al
2026-10-04, con los tres contrastes y el gate de oro y plata cerrados; si un
gate deja de cerrar, la serie y sus pares pasan a **"NO MEDIDO: sin validación
externa"**.

| Serie | Licencia | ¿Se publica? |
| --- | --- | --- |
| Oro (Pink Sheet) | CC BY 4.0 | **Sí.** |
| Plata (Pink Sheet) | CC BY 4.0 | **Sí**, con el estado "estimación" visible en el sitio (A-R0-8). |
| BTC (Coin Metrics) | CC BY-NC 4.0 | **Sí**, mientras el sitio no tenga vínculo comercial (A-R0-4). |
| S&P 500 (Shiller) | Sin licencia declarada | **No.** Se calcula en el pipeline. |
| Nasdaq Composite (FRED) | Permiso previo; lectura "no comercial educativo" | **No.** Se calcula en el pipeline. |

| Par | Qué se publica |
| --- | --- |
| Oro / Plata | El ratio. |
| BTC / Oro | El ratio, desde 2013-01. |
| Oro / S&P 500, BTC / S&P 500, Nasdaq / S&P 500 | Se calculan en el pipeline y se publican como **"NO MEDIDO: pendiente de permiso del dueño del índice"** hasta tener el permiso escrito (sección 10). |

### 9.2 Fuente por activo

| Activo | Fuente | Clase | Supuesto | Convención | Historia |
| --- | --- | --- | --- | --- | --- |
| Oro | Banco Mundial, Pink Sheet: edición de enero de 2025 hasta 2024-12, vigente después | (a) | A-R0-7, A-R0-9, A-R0-19 | Viene como promedio mensual de precios diarios | 1960-01 |
| Plata | Banco Mundial, Pink Sheet: edición de enero de 2025 hasta 2024-12, vigente después | (a) | A-R0-8, A-R0-9, A-R0-19 | Viene como precio mensual; que sea promedio es una **estimación** | 1960-01 |
| BTC | Coin Metrics community, `PriceUSD` | (b) | A-R0-4, A-R0-5, A-R0-10 | Se promedia desde el fixing diario, todos los días calendario | 2010-07; se publica desde 2013-01 |
| Nasdaq Composite | FRED `NASDAQCOM` | (b) con reserva | A-R0-3 | Se promedia desde los cierres diarios | 1971-02 |
| S&P 500 | Shiller, `ie_data.xls` | s/d | A-R0-2, A-R0-11 | Viene como promedio mensual de cierres diarios | 1871-01 |

Los tres supuestos de licencia (A-R0-2, A-R0-3, A-R0-4) son **condicionales**:
valen mientras el sitio no tenga vínculo comercial. Solo el oro y la plata
tienen una fuente (a). Para los dos índices no hay fuente (a) ni una (b)
limpia: el nivel de un índice es propiedad de quien lo calcula, y todas las
vías leídas terminan en el permiso del dueño.

### 9.3 Orden de fuentes por activo

**S&P 500**

1. (a): ninguna.
2. (b): ninguna con cláusula.
3. s/d: **Shiller** (2.2). Sin términos; solo descargo de responsabilidad.
4. (c), excluidas: FRED `SP500` (permiso escrito de S&P, y solo 10 años);
   S&P DJI (permiso escrito); Cboe (uso personal); Yahoo `^GSPC` (sección 8).

**Nasdaq Composite**

1. (a): ninguna.
2. (b) con reserva: **FRED `NASDAQCOM`** (3.1). Cláusula: *"may only be used
   for non-commercial educational or personal use"*.
3. (c), excluidas: api.nasdaq.com e indexes.nasdaqomx.com (uso personal y
   aprobación escrita); Yahoo `^IXIC`.

**Oro**

1. (a): **Banco Mundial, Pink Sheet** (4.5 y 5.5). Cláusula: *"provided to you under
   a Creative Commons Attribution 4.0 International License (CC BY 4.0)"*.
2. (b): ninguna leída.
3. (c), excluidas: LBMA / IBA (licencia); World Gold Council (uso personal y
   autorización escrita); Yahoo `GC=F` (futuro, y sección 8).
4. No existen: Bundesbank en USD; FRED.

**Plata**

1. (a): **Banco Mundial, Pink Sheet** (5.3 y 5.5). Misma cláusula.
2. (b): ninguna leída.
3. (c), excluidas: LBMA / IBA; Yahoo `SI=F`.

**BTC**

1. (a): ninguna.
2. (b): **Coin Metrics community** (6.2). Cláusula: *"Available to the
   community under the Creative Commons license"*, con enlace a CC BY-NC 4.0.
   Segunda (b), por inferencia: Bitstamp (6.1), que queda como contraste.
3. (c), excluidas: Coinbase Exchange y FRED `CBBTCUSD` (uso personal o de
   investigación, sin redistribuir derivados); blockchain.info (uso personal);
   CoinGecko (historia solo en planes pagos).

### 9.4 La convención, fuente por fuente

Las cinco series se publican como **promedio mensual de cierres diarios, y
solo de meses completos** (A-R0-1). Qué cierre diario entra en cada promedio:

| Serie | Cierre diario | Hora y zona | Días que entran | Quién promedia |
| --- | --- | --- | --- | --- |
| S&P 500 (Shiller) | Cierre del índice | 16:00 de Nueva York (la hora la da la nota de FRED `SP500`; Shiller solo dice "daily closing prices") | Días hábiles de Nueva York: 19 a 23 por mes | Shiller |
| Nasdaq Composite (FRED) | Cierre del índice | 16:00 de Nueva York | Los días con valor en FRED | Nosotros |
| Oro (Pink Sheet) | Hasta 2025-05: fixing de la tarde de Londres. Desde 2025-06: "spot" | 15:00 de Londres hasta 2025-05 (hora leída en LBMA); **no declarada** desde 2025-06 | No declarados | Banco Mundial |
| Plata (Pink Sheet) | "London afternoon fixing" según el Banco Mundial; la subasta de LBMA es a las 12:00 | **No se pudo establecer** (5.3) | No declarados | Banco Mundial |
| BTC (Coin Metrics) | Fixing `PriceUSD` | 00:00 UTC del día siguiente | Todos los días calendario: 28 a 31 por mes | Nosotros |

Serie por serie:

- **S&P 500: la fuente ya viene así**, y el contraste contra cierres diarios lo
  confirma (2.2). La última fila del archivo no es un mes completo y se
  excluye; el mes llega con un rezago que la fuente no declara (A-R0-11).
- **Nasdaq Composite: se construye.** Cierres diarios desde 1971.
- **BTC: se construye, promediando todos los días calendario** (A-R0-5). BTC
  opera todos los días y los índices no: el promedio de todos los días y el de
  lunes a viernes difieren en una mediana de 0.30 % (percentil 95: 1.43 %;
  máximo: 3.30 %, en 2011-04; medido sobre `PriceUSD`, 2011-01 a 2026-09).
- **Oro: viene así, con un quiebre de definición en junio de 2025** que se
  declara junto a la serie (A-R0-7). El promedio no se puede recalcular: los
  precios diarios son de IBA.
- **Plata: no se puede verificar exactamente.** La descripción no dice que sea
  un promedio, y la hora del fixing que nombra no coincide con la de LBMA. La
  convención se infiere del contraste (5.3), y por eso la serie lleva el
  estado **"estimación"**, visible en el sitio (A-R0-8).

Las horas de cierre de las cinco series no coinciden entre sí (A-R0-6). Con
promedios mensuales ese desfase pesa mucho menos que con cierres, pero sigue
siendo un supuesto y va escrito.

### 9.5 Frecuencia común e historia por par

La frecuencia común es **mensual**. La propuesta semanal del borrador (cierre
del viernes) quedó descartada: las únicas fuentes (a) de oro y plata son
mensuales, y Shiller también.

| Par | Primer mes posible | Lo que limita | Se publica |
| --- | --- | --- | --- |
| Oro / Plata | 1960-01 | El oro de 1968-02 y de 1968-03 viene al dólar, con 1.4 % de error por redondeo: el par es apto para métricas desde 1968-04 (A-R0-17, A-R0-19), menos 20 meses con un valor en disputa (A-R0-20). | Sí |
| BTC / Oro | 2010-08 (primer mes completo de Coin Metrics) | Antes de 2013 las fuentes de BTC no coinciden (A-R0-10). Cuatro meses llevan el oro en disputa (A-R0-20). | Sí, desde 2013-01 |
| Oro / S&P 500 | 1960-01 | El oro casi no se mueve hasta 1967-12: va de 34.95 a 35.27. | NO MEDIDO |
| BTC / S&P 500 | 2010-08 | Como BTC / Oro. | NO MEDIDO |
| Nasdaq / S&P 500 | 1971-03 | Primer mes completo del Nasdaq. | NO MEDIDO |

El último mes de un par es el último mes completo en **las dos** fuentes. Al
2026-10-04 eso es septiembre de 2026 para Oro/Plata y BTC/Oro, y agosto de 2026
para los tres pares con S&P 500, porque el archivo de Shiller no se actualizó
desde el 2 de septiembre.

Todo ratio con índices es de **precio**, no de retorno total (A-R0-13).

### 9.6 Validación

Con la misma lógica del gate de S2: una segunda fuente independiente, una
tolerancia escrita antes de mirar el resultado, y **ninguna serie publicada sin
su caso de validación**.

| Serie | Contraste | Resultado del 2026-10-04 | Tolerancia |
| --- | --- | --- | --- |
| S&P 500 | Shiller contra el promedio de los cierres diarios de FRED `SP500` (ventana de 10 años) | 119 meses, mediana 0.000 %, máxima 0.232 % | ±0.5 % por mes |
| Nasdaq Composite | Promedio de FRED contra promedio de api.nasdaq.com (últimos 10 años) | 119 meses, mediana 0.000 %, máxima 0.027 % | ±0.1 % por mes |
| BTC | Promedio de Coin Metrics contra promedio de cierres de Bitstamp | Desde 2013-01, 165 meses: mediana 0.044 %, máxima 1.332 % | ±2 % por mes |
| Oro | Promedio de los doce meses contra el precio anual del USGS | 4 años de 4, máxima 0.120 % | ±0.5 % por año |
| Plata | Promedio de los doce meses contra el precio anual del USGS | 4 años de 4, máxima 0.601 % | ±1 % por año |
| Oro y plata, el empalme | Redondear la edición de enero de 2025 contra la edición vigente, mes a mes (5.5) | 780 meses de 780 en cada metal; 11 y 1 exactamente a medio paso | Medio paso de redondeo |
| Oro y plata, mes a mes | Pink Sheet contra el FMI, sobre todos los meses en común (4.7) | 560 meses por metal; 10 y 10 en disputa | ±0.5 % y ±1 %. No detiene la corrida: marca el mes |

**Las fuentes (c) se usan solo para contrastar.** El archivo no se guarda ni se
publica (A-R0-12). En el changelog queda, por corrida, cuántos meses se
compararon, la diferencia mediana y, del mes que más se aparta, la fecha y la
diferencia. **Del S&P 500 y del Nasdaq no queda ningún nivel del índice.**

Si el contraste de BTC o de un índice no cierra, la corrida se detiene. También
si no cierra el control del empalme (A-R0-19). Si no cierra el gate de un
metal, la corrida sigue y el metal y sus pares se publican como NO MEDIDO. El
control contra el FMI nunca la detiene: el mes que pasa del umbral se publica
sin cambios, como valor en disputa, y queda fuera de las métricas (A-R0-20).

**El gate de oro y plata** (A-R0-16). No hay una segunda fuente mensual abierta
para los metales, así que el gate es anual: el promedio de los doce meses del
Pink Sheet contra el precio promedio del año que publica el USGS (4.6), para
todos los años que la última edición trae sin estimar. Hoy son cuatro, 2021 a
2024.

| Año | Oro, Pink Sheet | Oro, USGS | Diferencia | Plata, Pink Sheet | Plata, USGS | Diferencia |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 1799.63 | 1801 | −0.076 % | 25.165 | 25.23 | −0.259 % |
| 2022 | 1800.60 | 1802 | −0.078 % | 21.794 | 21.88 | −0.391 % |
| 2023 | 1942.67 | 1945 | −0.120 % | 23.399 | 23.54 | −0.601 % |
| 2024 | 2387.70 | 2388 | −0.012 % | 28.269 | 28.37 | −0.355 % |

Es el gate con la serie empalmada (5.5). Se había calculado antes, el mismo
día, con la edición vigente redondeada: cerraba igual, con máximas de 0.116 %
en el oro y de 0.559 % en la plata. **Las tolerancias no se tocaron entre un
cálculo y otro.**

Las tolerancias se fijaron antes de calcular el gate, y están justificadas en
A-R0-16 componente por componente: redondeo de las dos fuentes, el efecto de
promediar promedios mensuales, y un margen para la diferencia entre la
cotización de Engelhard y el fixing de Londres. Las ocho diferencias tienen el
mismo signo: es esa diferencia de cotización, no ruido. Está registrado como
dato en A-R0-18, con la comparación contra el FMI que lo confirma (4.7).

El gate valida cuatro años. No dice nada de 1960 ni de los meses posteriores al
quiebre del oro de junio de 2025.

**Lo que se evaluó y no decide.** El FMI (4.7), como alternativa. El ancla
mensual de LBMA, que era la decisión original y no se pudo cumplir: la tabla de
precios de LBMA exige iniciar sesión (*"Sign in to view the tables of data"*) y
licencia de IBA, la página pública muestra solo un gráfico, y el informe
trimestral
(`https://www.lbma.org.uk/articles/lbma-precious-metals-market-report-q2-2026`)
da extremos y precios de días sueltos, no promedios. De ese informe sale un
control adicional, más débil que el gate: los promedios mensuales del segundo
trimestre de 2026 tienen que caer entre el mínimo y el máximo del trimestre
(oro 3994.50 a 4870.50; plata 57.37 a 86.79), y caen.

### 9.7 Crudos y reproducibilidad

| Fuente | Dónde vive el crudo | Qué se publica |
| --- | --- | --- |
| Con licencia que permite redistribuir: Pink Sheet (CC BY 4.0) y Coin Metrics (CC BY-NC 4.0) | En el repositorio, `data/raw/`, con su atribución y licencia en `data/raw/ATRIBUCION.md`. | El archivo, y su URL, fecha y SHA-256. |
| La edición del Pink Sheet del 3 de enero de 2025 (CC BY 4.0) | En el repositorio, `data/raw/pink_sheet_edicion_2025-01-03.xlsx`: una sola copia, con nombre fijo. No se vuelve a descargar. | El archivo, y su URL, fecha y SHA-256. El hash esperado está además en `configuracion.py`. |
| Sin esa licencia: Shiller (s/d) y FRED `NASDAQCOM` ((b) con reserva) | **Fuera del repositorio**, en `data/privado/`, ignorado por git. | URL, fecha y SHA-256 de cada descarga, y el código de transformación. |
| La copia del FMI (términos del FMI: redistribuir con atribución) | En el repositorio, `data/raw/fmi_pcps_2026-10-04.xlsx`: una sola copia, bajada a mano. El pipeline nunca la baja. | El archivo, y su URL, fecha y SHA-256. El hash esperado está además en `configuracion.py`. |
| De contraste, (c): FRED `SP500`, api.nasdaq.com, Bitstamp | En ningún lado. | Lo que dice 9.6: meses, mediana, y fecha y diferencia del peor mes. |
| De contraste, transcrita a mano: USGS | En `configuracion.py`, ocho cifras con su cita. | Las cifras, y la diferencia de cada año. |

Quien baje el mismo archivo puede comprobar el hash y rehacer la serie con el
código del repositorio. Si el crudo que hay en disco no coincide con el hash
publicado, la corrida se detiene (A-R0-15).

### 9.8 Qué reemplazar en el sitio

| Hoy | Problema | Reemplazo |
| --- | --- | --- |
| Yahoo `GC=F`, `SI=F` | (c); son futuros; cierre de fin de mes | Pink Sheet, (a) |
| Yahoo `^GSPC` | (c); cierre de fin de mes | Shiller, sin publicar hasta tener permiso |
| Yahoo `^IXIC` | (c); cierre de fin de mes | FRED `NASDAQCOM`, sin publicar hasta tener permiso |
| CoinGecko, historia | No responde; el sitio muestra anclas interpoladas | Coin Metrics community, (b) |
| CoinGecko, precio actual | Falta la atribución exigida | Fuera de la convención mensual; sin decidir |
| FRED `M2SL` | (a); falta el aviso de la API | Ya no se usa: el sitio dejó de consultarla en la fase 3 (8.3). La decisión del 2026-10-04 era conservarla y agregar el aviso. |

---

## 10. Permisos que hay que pedir

Ninguno está pedido. Mientras no lleguen, los tres pares con índices siguen
como NO MEDIDO y la plata como estimación.

### 10.1 S&P Dow Jones Indices

- **A quién.** `index_services@spdji.com`. Es la dirección que da la nota de
  la serie `SP500` en FRED para pedir permiso de reproducción.
- **Qué pedir.** Permiso escrito para publicar en losratios.com:
  1. el promedio mensual del S&P 500 (índice de precio), y
  2. los ratios Oro/S&P 500, BTC/S&P 500 y Nasdaq/S&P 500 que salen de él,
  como gráfico y como CSV descargable.
- **Qué declarar.** Que es un sitio de investigación pública sin fines
  comerciales, que a futuro puede enlazar a un servicio de asesoría; que los
  promedios mensuales salen del archivo de Robert Shiller (desde 1871) y se
  contrastan contra FRED `SP500`; que no se redistribuyen cierres diarios.
- **Qué preguntar.** El texto de atribución que exigen. Si el permiso cubre la
  historia completa o solo los 10 años que acordaron con FRED. Si cambia algo
  el día que el sitio tenga un vínculo comercial. Si permite versionar el
  archivo crudo.
- **Qué destraba.** Tres de los cinco pares, y el estado de A-R0-2.

### 10.2 Nasdaq

- **A quién.** `indexservices@nasdaq.com`, la dirección de soporte de datos de
  índices de `https://indexes.nasdaqomx.com/ContactUs`. **No se encontró una
  dirección específica para permisos de reproducción**; la otra vía leída es
  el formulario de contacto de
  `https://www.nasdaq.com/solutions/index-licensing-and-etps`.
- **Qué pedir.** Permiso escrito para publicar el promedio mensual del Nasdaq
  Composite y el ratio Nasdaq/S&P 500, como gráfico y como CSV descargable.
- **Qué declarar.** Lo mismo que a S&P DJI; que los cierres diarios se leen de
  FRED `NASDAQCOM` (desde 1971) y se contrastan contra la API de nasdaq.com.
- **Qué preguntar.** Texto de atribución; si el uso educativo no comercial que
  describe FRED alcanza para un sitio público; qué cambia con un vínculo
  comercial.
- **Qué destraba.** El par Nasdaq/S&P 500 (junto con 10.1) y el estado de
  A-R0-3.

### 10.3 Banco Mundial

No es un permiso: la licencia ya es CC BY 4.0. Es una confirmación de
convención.

- **A quién.** `data@worldbank.org`, la dirección que dan los términos de los
  conjuntos de datos para consultas.
- **Qué preguntar.**
  1. Si la plata mensual del Pink Sheet es el promedio de los precios diarios
     del mes, como dice la descripción del oro y no dice la de la plata.
  2. Qué precio diario es: la descripción habla de un fixing de la tarde de
     Londres, y la subasta de plata de LBMA es a las 12:00.
  3. Qué precio y qué hora es el "spot" del oro desde junio de 2025.
  4. Si el oro y la plata están bajo CC BY 4.0 o bajo la excepción de datos de
     terceros.
  5. Si publican los mismos precios sin redondear, y si la URL del archivo
     mensual es estable entre publicaciones.
- **Qué reportar.** El oro de marzo de 1985: el Pink Sheet trae 313.5, el FMI
  303.94 y la cotización de Engelhard 304.34 (4.7). Y el de noviembre de 1985:
  321.5, contra 325.24 y 325.64. No se reportó todavía.
- **Qué destraba.** La plata deja de ser estimación (A-R0-8) y el quiebre del
  oro queda descrito con hora (A-R0-7).

### 10.4 FMI

- **A quién.** `copyright@imf.org`, la dirección que dan sus términos.
- **Qué pedir.**
  1. Permiso para bajar `external-data.xlsx` una vez por corrida, con un
     programa. Hoy el pipeline usa una copia bajada a mano, porque los términos
     prohíben la descarga masiva automatizada sin permiso.
  2. Permiso de uso comercial, si el sitio llega a tener un vínculo comercial.
- **Qué destraba.** Que el control mensual (A-R0-20) alcance siempre al último
  mes que el FMI publique, y que deje de depender de una condición.

---

## 11. Supuestos

Están en `SUPUESTOS.md`. Índice:

| N.º | Qué fija | Estado |
| --- | --- | --- |
| A-R0-1 | Promedio mensual de cierres diarios; solo meses completos | supuesto |
| A-R0-2 | S&P 500 desde Shiller, sin licencia declarada | supuesto condicional |
| A-R0-3 | Nasdaq Composite desde FRED `NASDAQCOM`, uso educativo no comercial | supuesto condicional |
| A-R0-4 | BTC desde Coin Metrics community, CC BY-NC 4.0 | supuesto condicional |
| A-R0-5 | El mes de BTC promedia todos los días calendario UTC | supuesto |
| A-R0-6 | Los cierres diarios no son simultáneos | supuesto |
| A-R0-7 | El oro cambia de definición en junio de 2025 | dato; supuesto la continuidad |
| A-R0-8 | La plata es un promedio mensual por inferencia | estimación |
| A-R0-9 | La edición vigente del Pink Sheet viene redondeada | dato |
| A-R0-10 | Los pares con BTC se publican desde 2013-01 | supuesto |
| A-R0-11 | La última fila de Shiller no es un mes completo; rezago | dato; supuesto la regla |
| A-R0-12 | Las fuentes (c) solo contrastan; tolerancias; qué queda escrito | supuesto |
| A-R0-13 | Los ratios con índices son de precio | dato |
| A-R0-14 | Se publica lo que la licencia permite y una segunda fuente valida | supuesto |
| A-R0-15 | Un crudo entra al repositorio solo si su licencia permite redistribuirlo | supuesto |
| A-R0-16 | Gate anual de oro y plata contra el USGS; cerró el 2026-10-04 | supuesto la regla; dato el resultado |
| A-R0-17 | Las métricas solo usan meses con error de redondeo del ratio de hasta 0.5 % | dato el error; supuesto el umbral |
| A-R0-18 | En los ocho contrastes anuales el Banco Mundial queda por debajo de Engelhard | dato |
| A-R0-19 | El oro y la plata se empalman: edición de enero de 2025 hasta 2024-12, vigente después | supuesto el empalme; dato lo que lo sostiene |
| A-R0-20 | Control mensual del oro y la plata contra el FMI; el mes que pasa del umbral queda como valor en disputa | supuesto el umbral y la regla; dato lo que encuentra |

---

## 12. Lo que sigue abierto

1. **Los permisos de la sección 10.** Son cuatro pedidos y un reporte.
2. **El gate de oro y plata cubre 2021 a 2024.** El 2025 entra cuando el USGS
   lo publique sin estimar, en la edición siguiente. Hasta entonces el tramo
   "spot" del oro (desde junio de 2025) no tiene un año validado.
3. **Shiller.** No se encontró licencia ni un contacto para pedirla en la
   página.
4. **Rezago de Shiller.** Sin calendario declarado; hoy lleva un mes.
5. **Términos de Coin Metrics.** La licencia está en una línea de la
   documentación; la página a la que remite para el detalle ya no existe.
6. **La plata después de junio de 2025.** Se aparta más del FMI que antes (4.7)
   y el Banco Mundial no declara ningún cambio. Es una de las preguntas de la
   sección 10.3.
7. **La edición sin redondear del Pink Sheet es una edición congelada** (5.5,
   A-R0-19). No recibe revisiones. Si el Banco Mundial corrige un mes anterior
   a 2025, el control del empalme detiene la corrida y hay que decidir de
   nuevo de dónde sale ese tramo. Y desde 2025-01 la serie sigue redondeada.
8. **Los veinte meses en disputa** (A-R0-20). Marzo y noviembre de 1985 tienen
   una tercera lectura, que le da la razón al FMI (4.7), y siguen publicados
   con el valor del Pink Sheet hasta que el Banco Mundial los corrija. Los
   otros dieciocho no tienen tercera lectura. Cinco son diciembres, y no se
   sabe por qué.
9. **La copia del FMI llega hasta 2026-08.** Los meses posteriores se publican
   como "sin comparar" hasta que alguien baje otra edición a mano. Y el FMI
   empieza en 1980: de 1968-04 a 1979-12 el tramo apto de Oro/Plata no tiene
   control mensual.
10. **Precio actual de BTC en el sitio.** Queda fuera de la convención mensual
   y no tiene decisión.
11. **No leído:** los ZIP históricos de Kraken, los términos de datos de
   Kraken, los términos del Bundesbank, la exportación de S&P DJI, y la
   documentación técnica del FMI (se leyó la descripción de cada serie en la
   planilla).
12. **Bajar S2 directamente de los dueños de los datos.** Pendiente, sin
   implementar. Hoy S2 baja `WALCL`, `WDTGAL` y `RRPONTSYD` de FRED, y los
   términos completos de FRED reservan la redistribución de su contenido al
   permiso escrito del banco. Los crudos se quedan versionados por lo que
   declara el dueño de cada serie (`data/raw/ATRIBUCION.md`). Las dos fuentes
   de origen, leídas el 2026-10-05:
   - El H.4.1, del programa de descarga de datos de la Junta
     (`https://www.federalreserve.gov/datadownload/`), que lista "Factors
     Affecting Reserve Balances (H.4.1)".
   - El ON RRP, de la API de datos de mercados del Federal Reserve Bank of New
     York (`https://markets.newyorkfed.org/static/docs/markets-api.html`),
     que tiene una sección "Repo and Reverse Repo Operations".

   Se leyó que las dos existen. **No verificado:** que entreguen las mismas
   series que hoy se bajan de FRED, ni con qué unidad y convención. Cambiar la
   fuente de S2 es un cambio de supuesto y va con su caso de validación.

---

## D0. Fuentes de El Denominador: agregados monetarios, balances y riqueza

> **APROBADO (2026-10-05), con las decisiones del dueño que están en D0.10.11.**
> Todo lo que figura en esta sección se leyó de la fuente el 2026-10-05,
> desde una máquina con salida directa. Nada viene de memoria. Lo que no se
> pudo leer está dicho como tal y no tiene cifras. Las decisiones de D0.10
> eran propuestas; las aprobadas y las que el dueño cambió están en D0.10.11,
> y los supuestos A-D0-1 a A-D0-29 están en `SUPUESTOS.md`. D0.15 registra lo
> que el paso 1 encontró el 2026-10-06 al escribir el pipeline.

Esta sección es el entregable del paso 0 de la fase D0: evaluar de dónde
pueden salir, observadas y trazables, las series que hoy muestra
eldenominador.com. No tiene código. Usa las reglas de las secciones 0.1 a 0.3
de este archivo: las mismas clases de licencia, la misma regla de publicación
y la misma regla de la convención.

### D0.0 Qué muestra hoy el sitio

Leído de `src/lib/data.ts` del repositorio `danioni/eldenominador`, commit
`5280658`, sin modificarlo:

| Qué muestra | Cómo está hecho hoy |
| --- | --- |
| "M2 Global" de EE.UU., Eurozona, Japón y China, en billones de USD, desde 1913 | 32 años ancla escritos a mano (`historicalAnchors`); los años intermedios salen de una función `interpolate` con crecimiento exponencial |
| Balances de la Fed, el BCE, el BoJ y el PBoC | Las mismas anclas. Hay cifras para los cuatro, el BCE incluido, desde 1913 |
| "Índice Denominador" | `(M2 global / base) × 0.6 + (balances / base) × 0.4`, base 100 = 1913 |
| "Activos vs Denominador" | Oro y S&P 500 en base 100 = 1913, desde las mismas anclas |
| "Riqueza global" por clase de activo | Capitalizaciones de inmuebles, bonos, acciones, oro y BTC en las mismas anclas. El comentario del código nombra *"WGC (gold), World Bank/Siblis (equities), Savills (RE), BIS/SIFMA (bonds)"*, sin año ni enlace |

El archivo declara sus fuentes en una línea: *"Sources: FRED, ECB, BoJ, PBoC,
BIS, historical research"*. Ninguna cifra tiene identificador de serie ni
fecha de lectura. Todo eso se reemplaza.

### D0.1 Qué se leyó, desde dónde y cómo

Todo el 2026-10-05, entre las 12:46 y las 13:20 UTC, desde una máquina con
salida directa. Las descargas se hicieron con `python-requests`; lo que un
programa no pudo leer y se leyó con un navegador está dicho en cada fila. Cada
descarga quedó anotada con su URL, hora, estado HTTP, bytes y SHA-256 en
`senales/data/privado/d0_paso0/<tema>/registro.md`. Esa carpeta no se versiona
(A-R0-15): es evidencia de trabajo, y tres de sus archivos contienen la IP de
la máquina.

**Sobre las citas.** Las cláusulas y definiciones de fuentes en dominio
público o de licencia abierta van literales. Las de fuentes con derechos
reservados van **parafraseadas**, con la URL y la sección donde está el texto.
Es una diferencia con las secciones 2 a 8 de este archivo.

| Host | Estado el 2026-10-05 |
| --- | --- |
| www.federalreserve.gov | Leído: páginas del H.6, el H.10 y el H.4.1, descargo legal, y los tres ZIP de XML. |
| fred.stlouisfed.org | Leído, un pedido por vez con pausas de 20 s o más: 21 respuestas HTTP 200 y 2 HTTP 404 (identificadores que no existen). Solo como contraste. |
| fraser.stlouisfed.org | Leído: los dos volúmenes de *Banking and Monetary Statistics* en PDF y los términos de uso. |
| www.nber.org, data.nber.org | Leído: Macrohistory Database (capítulo 14) y el volumen de 1970 de Friedman y Schwartz. El libro de 1963 no está en línea. |
| data-api.ecb.europa.eu, data.ecb.europa.eu, www.ecb.europa.eu | Leído. La API devolvió HTTP 504 o 502 en 4 de unos 30 pedidos; el reintento funcionó. **El `robots.txt` de data-api.ecb.europa.eu, leído después, veda a `python-requests`, el cliente con que se hicieron esos pedidos (D0.15).** |
| www.bde.es, api.statistiken.bundesbank.de | Leído, como contraste. |
| webstat.banque-france.fr, stat.nbb.be | **No leídos.** El primero no muestra valores sin JavaScript y su API pide iniciar sesión; el segundo reinició la conexión. |
| www.boj.or.jp, www.stat-search.boj.or.jp | Leído: API, notas, guía, avisos y términos. Los comunicados de 2020 ya no están (HTTP 404); se leyó una copia en web.archive.org. |
| dashboard.e-stat.go.jp | Leído, como contraste. |
| www.pbc.gov.cn | Leído con un programa (unos 70 pedidos, HTTP 200) y con navegador. **El `robots.txt` del sitio, que se leyó después de esos pedidos, lo veda a los programas.** Desde ese momento se hicieron tres pedidos más, de diagnóstico. El pipeline no baja nada de este host. |
| data.stats.gov.cn, www.stats.gov.cn | El servicio de consultas responde HTTP 403 a un programa. El portal y los términos se leyeron con navegador. |
| sdmx.oecd.org | API leída. |
| www.oecd.org | La página de términos responde HTTP 403 con una verificación a un programa. Se leyó con navegador, que la cargó sin intervención. |
| stats.bis.org, data.bis.org | Leído. Una página de términos de www.bis.org responde "Access denied"; los términos se leyeron en data.bis.org. |
| api.worldbank.org, www.worldbank.org | Leído. |
| community-api.coinmetrics.io, api.blockchain.info | Leído. |
| impacts.savills.com, www.savills.co.uk | Informes leídos. Los términos responden HTTP 403 a un programa; se leyeron con navegador. |
| www.gold.org | Página y términos leídos. El archivo de la serie y la metodología responden HTTP 403 y piden una cuenta. |
| www.usgs.gov, pubs.usgs.gov | Leído. |
| www.world-exchanges.org, www.sifma.org, www.ubs.com | Leído. El portal de estadísticas de la WFE pide una cuenta. |
| www.mckinsey.com | Corta la conexión a un programa. Los términos y la página del informe se leyeron con navegador. **Los términos prohíben extraer datos del sitio: no se usa ninguna cifra suya.** |
| wid.world | **No leído:** el dominio mostraba una página de estacionamiento. Se leyó la copia de web.archive.org del 2026-10-01. |
| www.imf.org | Solo la página de términos. No se usó ninguna API ni descarga del FMI. |

### D0.2 EE.UU.: M2 de la Junta de la Reserva Federal (H.6) — leída, dominio público

- **Identificador y URL.** Publicación estadística H.6, "Money Stock Measures".
  Página: `https://www.federalreserve.gov/releases/h6/current/default.htm`
  (publicación del 22 de septiembre de 2026). Archivo con la historia
  completa, enlazado desde esa página como "XML":
  `https://www.federalreserve.gov/releases/h6/data/FRB_h6_xml.zip`
  (1.419.255 bytes; trae `H6_data.xml`, fechado el 22 de septiembre de 2026).
  Series, por su `SERIES_NAME`: **`M2.M`** (ajustada por estacionalidad) y
  **`M2_N.M`** (sin ajustar).
- Emisor original: Junta de Gobernadores del Sistema de la Reserva Federal.
- Frecuencia nativa: mensual. Existe además una semanal sin ajustar
  (`M2_N.WM`, 1981-01-05 a 2026-08-31); la semanal ajustada quedó
  discontinuada el 1 de febrero de 2021.
- **Convención: promedio mensual de cifras diarias, no saldo de fin de mes.**
  Literal, de las preguntas técnicas del H.6
  (`https://www.federalreserve.gov/releases/h6/h6_technical_qa.htm`):
  *"Release items on the monthly H.6 statistical release will be presented as
  monthly average levels"*. Y de la página "About"
  (`https://www.federalreserve.gov/releases/h6/about.htm`): *"Monthly average
  data are available back to January 1959."* El XML fecha cada mes en su
  último día (`1959-01-31`), pero el valor es el promedio del mes. **La Junta
  no publica un M2 de fin de mes.**
- Unidad y moneda: miles de millones de USD (`UNIT_MULT="1e+09"`,
  `CURRENCY="USD"`), con un decimal.
- **Inicio real: 1959-01 = 286.6** (ajustada) y **289.8** (sin ajustar).
  Último dato: 2026-08 = 23342.8 y 23284.3. Son 812 meses en cada serie, sin
  huecos.
- **Definición** (nota 2 de la publicación, literal): *"M2 consists of M1 plus
  (1) small-denomination time deposits (time deposits in amounts of less than
  $100,000) and (2) balances in retail money market funds (MMFs), less
  individual retirement account (IRA) and Keogh account balances at depository
  institutions and MMFs."*
- **Quiebres y cambios de método leídos:**
  - **Mayo de 2020: quiebre de M1, no de M2.** Los depósitos de ahorro pasaron
    a M1. Literal: *"Recognizing savings deposits as a transaction account as
    of May 2020 will cause a series break in the M1 monetary aggregate. [...]
    M2 will remain unchanged."*
  - **Febrero de 2021: la publicación pasó de semanal a mensual.** Literal:
    *"Publish the H.6 statistical release at a monthly rather than weekly
    frequency and retain only monthly average data on the release itself."*
  - **28 de julio de 2026: cambio en cómo se restan los saldos IRA y Keogh**
    (ahora a nivel del agregado, antes en cada componente). Literal: *"The
    revised netting methodology was applied retroactively to the beginning of
    each time series (1959 for small time deposits and 1973 for retail money
    market funds, both at a monthly frequency)"*. Cambia los componentes; la
    Junta no dice ahí que cambie el total de M2.
  - **No leído:** la historia de las redefiniciones de M2 anteriores a 2020
    (la de 1980, entre otras). La serie vigente llega a 1959 con la definición
    actual aplicada hacia atrás por la Junta; el documento que lo describe no
    se leyó.
- Calendario: cuarto martes de cada mes, en general a las 13:00 (*"published
  on the fourth Tuesday of every month, generally at 1 p.m."*). El mes llega
  con unas tres semanas de rezago.
- Clave / registro: no.
- **Licencia: (a), dominio público.** Cláusula, literal
  (`https://www.federalreserve.gov/disclaimer.htm`, última actualización del
  2 de agosto de 2024): *"Unless otherwise indicated, information on Board's
  website is in the public domain and may be copied and distributed without
  permission. Please cite to the Board as the source of the information."*
- **Muestra: 2020-03 = 16034.4** y **2026-08 = 23342.8** (ajustada).
- **Contraste.** Dos lecturas más, las dos del mismo emisor:
  - La tabla 1 de la publicación en HTML trae 2026-08 = 23,342.8 (ajustada) y
    23,284.3 (sin ajustar): igual que el XML.
  - FRED `M2SL` y `M2NS` (bajadas con `python-requests`, una por vez): 812
    meses comunes con `M2.M` y `M2_N.M`, **812 idénticos** en cada par.
- **Lo que el contraste no prueba.** El HTML, el XML y FRED son tres canales
  del mismo dato. Confirman que la serie se transcribe bien; no hay un segundo
  compilador del M2 de EE.UU. contra el cual validar la medición.

**El programa de descarga de la Junta se retira.** Aviso en la página del
H.6, literal: *"During the week of November 9, the 'Build Your Package'
feature in the Data Download Program (DDP) will be removed in preparation for
the eventual retirement of the DDP."* El detalle
(`https://www.federalreserve.gov/data/data-download-fred-information.htm`,
16 de julio de 2026) dice que *"Historical data will remain available for
download as XML files on statistical release pages"* y que la Junta planea
*"removal of the preformatted data packages and the eventual retirement of
the DDP"*. Para la descarga con programa remite a FRED, cuya API pide clave
(*"Users interested in using this new feature to make data requests will need
an API key"*). Consecuencia para el pipeline: **la vía directa que queda en
el dueño del dato es el ZIP de XML de cada publicación**, sin clave. Es lo
que propone esta sección para H.6, H.10 y H.4.1.

### D0.3 EE.UU.: la oferta monetaria antes de 1959

El M2 del H.6 empieza en enero de 1959. Para la historia anterior se leyeron
tres fuentes. Lo que dicen, en una línea: **antes de 1947 no existe una serie
mensual observada**. La Junta solo tiene fechas de balance; la serie mensual
de Friedman y Schwartz es una reconstrucción que sus autores describen como
tal.

#### D0.3.1 Junta de Gobernadores, *Banking and Monetary Statistics* — leída

Dos volúmenes, leídos en FRASER (la biblioteca digital del Federal Reserve
Bank of St. Louis):

- *Banking and Monetary Statistics, 1914–1941* (1943; reimpreso en 1976).
  `https://fraser.stlouisfed.org/title/banking-monetary-statistics-1914-1941-38`;
  PDF completo:
  `https://fraser.stlouisfed.org/files/docs/publications/bms/1914-1941/BMS14-41_complete.pdf`
  (36.270.375 bytes).
- *Banking and Monetary Statistics, 1941–1970* (1976).
  `https://fraser.stlouisfed.org/title/banking-monetary-statistics-1941-1970-41`;
  PDF completo:
  `https://fraser.stlouisfed.org/files/docs/publications/bms/1941-1970/BMS41-70_complete.pdf`
  (74.978.023 bytes).

**Tabla 9 del primer volumen** ("Deposits and currency—adjusted deposits of
all banks and currency outside banks", en millones de USD):

- **Qué mide.** Depósitos en todos los bancos del territorio continental y
  efectivo fuera de los bancos, en fechas de balance (*call dates*). Columnas:
  efectivo fuera de bancos; depósitos a la vista ajustados; depósitos del
  gobierno; depósitos a plazo, separados en bancos comerciales, cajas de
  ahorro mutuas y sistema de ahorro postal.
- **Frecuencia por tramo** (descrita por la propia Junta en el segundo
  volumen, literal): *"This table shows data for both demand and time deposits
  and currency for June call dates from 1892 to 1922 and for June and December
  call dates for 1923–41."* Es decir: **anual (30 de junio) de 1892 a 1922;
  semestral (junio y diciembre) de 1923 a 1941.** El segundo volumen la
  extiende con las mismas columnas hasta el 31 de diciembre de 1946.
- **No es un promedio ni está interpolada:** es el saldo de un día. Sin ajuste
  estacional.
- **Estado: dato de fecha de balance, estimado en parte.** Literal: *"Deposit
  figures are for all banks in the United States and are partly estimated"*.
  De 1892 a 1913 son *"unpublished estimates [...] made by the Board's
  staff"*; desde 1914, *"totals of reported figures for member banks and
  partly estimated figures for nonmember banks"*.
- **Por qué no hay mensual.** Literal, del segundo volumen: *"Data on the
  money stock, previously available only for call dates, were published
  thereafter as a part of this consolidated statement"* (desde 1948–49), y
  *"the Board in late 1960 introduced a new measure of the money stock based
  on averages of daily figures. This series was estimated back to 1947."* En
  nota: *"the monthly series for the money stock does not begin until 1947"*.

**Tabla 1.1 del segundo volumen** ("Money stock and related data, monthly,
1947–70", en miles de millones de USD):

- **Mensual desde 1947-01, promedio de cifras diarias**, con y sin ajuste
  estacional. Trae el "money stock" (efectivo más depósitos a la vista: el M1
  de entonces) y los depósitos a plazo ajustados de los bancos comerciales.
  Desde 1959 trae además los agregados M1, M2 y M3 según la definición de
  1976.
- Muestra leída: **1947-01: 109.5 + 33.3 = 142.8** (ajustada).

**Licencia.** Ninguno de los dos volúmenes trae aviso de copyright (se buscó
en el texto completo). Son publicaciones de una agencia federal. Que estén en
dominio público como obra del gobierno de EE.UU. es una **inferencia**: no es
una cláusula leída en el documento. FRASER, que aloja la copia, tiene términos
propios (`https://fraser.stlouisfed.org/terms-of-use`, primer párrafo y
sección "Property Rights and Licenses"): da acceso para usos no comerciales,
educativos y personales, exige atribución, y deja en manos de quien usa cada
documento la evaluación de sus derechos de autor, porque el banco no es dueño
de la mayoría de lo que aloja. Los términos de FRASER rigen su servicio y sus
copias; las cifras son de la Junta.

**Calidad de la copia.** Los PDF son escaneos con texto reconocido por
máquina, y el reconocimiento falla: en la Tabla 9 se lee "1890" por 1899 y
"1801" por 1901, y en su continuación de 1941 a 1946 la columna de los bancos
comerciales sale corrida una fila. Cada fila se puede comprobar con su propia
suma (total = efectivo + depósitos; depósitos a plazo = comerciales + cajas
de ahorro + ahorro postal), y así se comprobaron las cuatro de D0.3.4. **Usar
estas tablas exige transcribirlas a mano y verificar fila por fila.**

#### D0.3.2 Friedman y Schwartz — leída en el volumen de 1970

- ***A Monetary History of the United States, 1867–1960* (1963): no leída.**
  La página del NBER
  (`https://www.nber.org/books-and-chapters/monetary-history-united-states-1867-1960`)
  no ofrece los capítulos; el libro es de Princeton University Press. Las
  tablas del apéndice A no se pudieron leer.
- ***Monetary Statistics of the United States: Estimates, Sources, Methods*
  (NBER, 1970): leída.** Los capítulos están en PDF en
  `https://www.nber.org/books-and-chapters/monetary-statistics-united-states-estimates-sources-methods`.
  La introducción (`https://www.nber.org/system/files/chapters/c5278/c5278.pdf`,
  1.118.937 bytes) trae la **Tabla 1**: "Currency, Deposits, and Savings and
  Loan Shares Held by the Public, and Consolidated Totals, 1867–1968", en
  miles de millones de USD, ajustada por estacionalidad (pp. 4–53; notas en
  pp. 54–58). Los autores dicen que parte de los componentes de efectivo y
  depósitos de la tabla A-1 del libro de 1963 (nota 1, p. 3), con dos cambios:
  las columnas hasta 1946 están ajustadas para dar un total consolidado, y
  desde 1947 incorporan revisiones de la Reserva Federal.
- **Definición de los agregados** (encabezado de la Tabla 1):
  - M1 = efectivo en poder del público + depósitos a la vista ajustados en
    bancos comerciales.
  - **M2 = M1 + depósitos a plazo en bancos comerciales.** No incluye las
    cajas de ahorro mutuas, el ahorro postal ni las asociaciones de ahorro y
    préstamo.
  - M3 = M2 + depósitos en cajas de ahorro mutuas y en el sistema de ahorro
    postal.
  - M4 = M3 + participaciones en asociaciones de ahorro y préstamo.
- **Frecuencia por tramo** (leída de las fechas de la Tabla 1 y de la
  documentación de las series 14183 y 14186 del NBER): una fecha por año, en
  enero, de 1867 a 1872; en febrero, 1873 y 1874; febrero y agosto de 1875 a
  1881; junio de 1882 a 1906; **mensual desde mayo de 1907**. Las
  participaciones en asociaciones de ahorro y préstamo (y con ellas M4) son
  anuales, de diciembre, hasta 1949; trimestrales de 1950 a 1954; mensuales
  desde 1955.
- **Estado: estimación, por declaración de los autores.** Tres afirmaciones
  suyas, parafraseadas:
  - Antes de 1947 no hay cifras sin ajuste estacional de efectivo y depósitos,
    porque algunos componentes se interpolaron a partir de cifras de otras
    fechas (p. 75).
  - Para los meses usaron directamente los datos mensuales que existían y
    completaron el resto interpolando desde su serie de fechas de balance
    (p. 79).
  - Describen la Tabla 1 como un producto "highly synthetic" (p. 79), sin
    garantía de exactitud en el detalle, y advierten que no hay que darle peso
    a los movimientos aislados de un mes a otro.
- Desde 1947 la tabla usa los promedios mensuales de cifras diarias de la
  Reserva Federal, ajustados por estacionalidad por la propia Reserva (notas
  de las columnas 1 a 3, pp. 54–55).
- **Licencia: (c) por la letra.** El volumen lleva aviso de copyright de 1970
  del NBER con todos los derechos reservados (portadilla), y la página del
  libro ofrece un formulario para pedir permiso de reimpresión.

#### D0.3.3 NBER Macrohistory Database, capítulo 14 — leída, s/d

- Página: `https://www.nber.org/research/data/nber-macrohistory-database`;
  capítulo 14: `https://www.nber.org/research/data/nber-macrohistory-xiv-money-and-banking`.
  Archivos de texto sin clave en
  `https://data.nber.org/databases/macrohistory/rectdata/14/` (`.dat`) y su
  documentación en `.../rectdata/14/docs/` (`.txt`).
- **Series leídas** (miles de millones de USD):

  | Serie | Qué es, según su documentación | Rango con dato | Convención declarada | Fuente declarada |
  | --- | --- | --- | --- | --- |
  | `m14144a` | Oferta monetaria: depósitos en bancos comerciales más efectivo en poder del público, ajustada por estacionalidad | 1907-05 a 1946-12, 476 meses sin huecos | El miércoles más cercano al fin de mes | Calculada por el NBER como suma de sus series 14125 y 14145; remite a Friedman y Schwartz (1970) |
  | `m14144c` | Depósitos a la vista y a plazo ajustados de todos los bancos comerciales, más efectivo en poder del público, ajustada por estacionalidad | 1947-01 a 1969-09, 273 meses sin huecos | Promedio mensual de cifras diarias | Junta de la Reserva Federal: tabla inédita (1947–1961) y *Federal Reserve Bulletin* (1962–1969) |
  | `m14144b` | La misma, sin ajuste estacional | 1955-01 a 1969-09 | Promedio mensual de cifras diarias | La misma |
  | `m14175a` | La de `m14144a` más cajas de ahorro mutuas y ahorro postal (el M3 de Friedman y Schwartz) | 1907-05 a 1946-12 | Fin de mes | Friedman y Schwartz (1963) |

- Es el **M2 de Friedman y Schwartz**: efectivo más depósitos en bancos
  comerciales. No es el M2 del H.6.
- Notas de `m14144c` que importan (archivo `docs/m14144c.txt`): los años 1947
  a 1954 los derivó el NBER promediando cifras quincenales, con diferencias
  de una décima contra el *Federal Reserve Bulletin* de junio de 1964; y desde
  junio de 1966 hay una reclasificación que saca 1.140 millones de USD de los
  depósitos a plazo.
- Muestra: `m14144a` **1907-05 = 11.66**, **1914-06 = 16.15**, **1929-06 =
  45.92**, **1933-06 = 30.09**, **1946-12 = 141.5**. `m14144c` **1947-01 =
  142.7**, **1959-01 = 207.6**, **1969-09 = 393.2**.
- Clave / registro: no.
- **Licencia: sin licencia declarada (s/d).** La página de la base no trae
  términos de uso ni pide una cita. FRED republica la serie como
  `M1444AUSM027SNBR`, la etiqueta como protegida por derecho de autor con cita
  obligatoria y avisa que hay que revisar las notas antes de compartirla; las
  notas de la serie no agregan condiciones. Con la regla 0.2, una fuente s/d
  puede alimentar el
  pipeline pero **no se publica sin permiso escrito del dueño**.

#### D0.3.4 Contraste entre las tres

| Fecha | Junta (*Banking and Monetary Statistics*) | NBER `m14144` | Friedman y Schwartz (1970), Tabla 1, col. 9 | Lectura |
| --- | --- | --- | --- | --- |
| 1920-06-30 | 4.105 + 19.616 + 10.509 = **34.230** millones | 34.71 | no leída | La Junta queda 1.4 % por debajo |
| 1929-06-29 | 3.639 + 22.540 + 19.557 = **45.736** millones | 45.92 | 46.27 | La Junta queda 0.4 % por debajo del NBER |
| 1933-06-30 | 4.761 + 14.411 + 10.849 = **30.021** millones | 30.09 | no leída | La Junta queda 0.2 % por debajo |
| 1946-12-31 | 26.730 + 83.314 + 33.808 = **143.852** millones | 141.5 | no leída | La Junta queda 1.7 % por encima |
| 1947-01 | 109.5 + 33.3 = **142.8** | 142.7 | no leída | Diferencia de 0.1, la que la documentación del NBER anuncia |
| 1959-01 | M2 de 1976: 208.5 | 207.6 | 207.6 | NBER y Friedman y Schwartz, iguales |

- Las cifras de la Junta hasta 1946 son la suma de efectivo fuera de bancos,
  depósitos a la vista ajustados y depósitos a plazo en bancos comerciales,
  leídos de la Tabla 9 y de su continuación, y comprobados con la suma de
  cada fila. Es el mismo concepto que el M2 de Friedman y Schwartz, pero **no
  es el mismo dato**: la Junta da el saldo del día, sin ajuste estacional; el
  NBER da una estimación ajustada del miércoles más cercano al fin de mes.
- **NBER contra Friedman y Schwartz (1970), 33 meses (1927-09 a 1930-05).**
  La columna 9 de la Tabla 1 queda entre 0.34 y 0.43 por encima de `m14144a`
  en los 33 meses. La diferencia coincide con la columna 10 de la misma tabla
  (las duplicaciones, de 0.34 a 0.43 en esas filas): es el ajuste de
  consolidación que el volumen de 1970 agregó. `m14144a` corresponde entonces
  a la versión sin consolidar. Desde 1947 la columna 10 vale cero y las dos
  fuentes coinciden (1959-01 y 1959-12: 207.6 y 209.3 en ambas).

#### D0.3.5 La superposición con el M2 del H.6

`m14144c` llega hasta 1969-09 y el M2 del H.6 empieza en 1959-01: hay **129
meses comunes**, los dos como promedio mensual de cifras diarias y ajustados
por estacionalidad.

| Mes | M2 del H.6 (`M2.M`) | NBER `m14144c` | Cociente |
| --- | --- | --- | --- |
| 1959-01 | 286.6 | 207.6 | 1.3805 |
| 1959-12 | 297.8 | 209.3 | 1.4228 |
| 1960-12 | 312.4 | 214.0 | 1.4598 |
| 1962-12 | 362.7 | 245.2 | 1.4792 |
| 1965-12 | 459.2 | 313.4 | 1.4652 |
| 1968-12 | 566.9 | 399.7 | 1.4183 |
| 1969-09 | 582.1 | 393.2 | 1.4804 |

- **El M2 del H.6 es entre 38 % y 49 % más grande** (mínimo 1.3805, máximo
  1.4889 en los 129 meses), **y el cociente no es constante.** La diferencia
  es de definición: el M2 del H.6 incluye depósitos en entidades de ahorro
  que el concepto de Friedman y Schwartz deja fuera.
- **Un empalme por factor distorsionaría la serie:** cualquier factor fijo
  elegido entre 1.38 y 1.49 mueve el tramo histórico hasta ocho puntos
  porcentuales según el mes que se use para calcularlo.
- **El agregado histórico más cercano al M2 del H.6 es el M4 de Friedman y
  Schwartz.** En 1959-01 vale 288.3 contra 286.6 del H.6 (0.6 % de
  diferencia), y en 1959-12, 297.4 contra 297.8. Pero M4 es anual hasta 1949
  y solo está en el PDF del volumen de 1970, que es (c).

### D0.4 Eurozona: M2 del BCE (conjunto BSI) — leída, (a)

- **Identificador y URL.** ECB Data Portal, conjunto BSI (balance de las
  instituciones financieras monetarias). Dos series de saldo:
  - Ajustada por estacionalidad y días hábiles, la titular del comunicado del
    BCE: **`BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E`**.
  - Sin ajustar: **`BSI.M.U2.N.V.M20.X.1.U2.2300.Z01.E`**.

  Descarga:
  `https://data-api.ecb.europa.eu/service/data/BSI/M.U2.Y.V.M20.X.1.U2.2300.Z01.E?format=csvdata`
  (y la misma con `N`). Metadatos:
  `https://data.ecb.europa.eu/data/datasets/bsi/data-information`.
- Emisor original: BCE y bancos centrales nacionales del Eurosistema.
- Frecuencia nativa: mensual.
- **Convención: saldo a fin de mes.** El título completo de la serie dice que
  son saldos vivos al final del período, y la ficha del conjunto precisa que
  se refieren al último día del mes, hábil o calendario según la práctica de
  cada país.
- Unidad y moneda: millones de EUR. El comunicado publica en miles de
  millones.
- **Inicio real: 1980-01 = 1070496** (ajustada). Último dato: 2026-08 =
  16447405 (provisional). 560 meses en cada serie, sin huecos.
- **Lo anterior a septiembre de 1997 es una estimación, y la serie no lo
  marca.** La API entrega los meses de 1980 a 1997 con el mismo estado
  ("valor normal") que los actuales. Lo único leído sobre cómo se hicieron es
  el Boletín Mensual del BCE de febrero de 1999
  (`https://www.ecb.europa.eu/pub/pdf/other/p.29_46_mb199902en.pdf`): el
  balance consolidado existe con el mismo detalle desde septiembre de 1997;
  hacia atrás, las series se construyeron agregando contribuciones nacionales
  estimadas, con mucha estimación en las fechas más antiguas, convertidas a
  euros con los tipos irrevocables del 31 de diciembre de 1998. El boletín
  pide tratarlas con cautela. **No verificado:** que los valores que hoy da la
  API para 1980–1997 sigan siendo los de ese método.
- **Quiebre de perímetro: composición cambiante.** El área de la serie es
  `U2`, "Euro area (changing composition)": en cada fecha suma a los países
  que ya tenían el euro. El manual de estas estadísticas (sección 7.3.1) dice
  que eso produce un salto de nivel en cada ampliación, y que hay que
  tratarlo como una reclasificación que no afecta a los flujos ni a las tasas
  de crecimiento. **La serie de saldos no marca esos saltos.** Su tamaño,
  medido con la serie de reclasificaciones (`...M20.X.5...`, sin ajustar):

  | Ampliación | Reclasificación del mes (millones de EUR) | Sobre el saldo previo |
  | --- | --- | --- |
  | 2001-01 (Grecia) | +101868 | 2.37 % |
  | 2007-01 (Eslovenia) | +15400 | 0.23 % |
  | 2008-01 (Chipre y Malta) | +43871 | 0.59 % |
  | 2009-01 (Eslovaquia) | +46487 | 0.57 % |
  | 2011-01 (Estonia) | +8789 | 0.10 % |
  | 2014-01 (Letonia) | +9837 | 0.11 % |
  | 2015-01 (Lituania) | +17453 | 0.18 % |
  | 2023-01 (Croacia) | +51437 | 0.34 % |
  | 2026-01 (Bulgaria) | +102678 | 0.64 % |

  Es la reclasificación total de cada mes: puede incluir otros conceptos. Hay
  además nueve reclasificaciones de más de 15.000 millones fuera de las
  ampliaciones (la mayor, +85849 en 2014-12), de causa no leída.
- No existe un M2 de composición fija: el BCE solo publica estas dos series de
  saldo. Sí publica un índice de saldos nocionales (`...M20.X.I...`), que
  corrige reclasificaciones, y las transacciones (`...M20.X.4...`).
- **Revisiones: materiales y hacia atrás.** El valor de 2020-03 que el BCE
  publicó en abril de 2020 era 12774 miles de millones; hoy la API da
  12791700 millones, 0.14 % más. La API no devolvió las versiones anteriores.
- Calendario: decimonoveno día hábil después del mes de referencia. Próximas:
  2026-10-27 (septiembre) y 2026-11-26.
- Clave / registro: no. La ayuda de la API no declara límites. Devolvió HTTP
  504 o 502 en 4 de unos 30 pedidos; el reintento funcionó siempre.
- **Licencia: (a), gratuita con atribución, con una condición sobre los
  datos modificados.** Dos textos:
  - Política de reutilización de las estadísticas del SEBC
    (`https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html`):
    acceso y reutilización gratuitos de todas las estadísticas publicadas, a
    condición de citar la fuente y de no modificar las estadísticas ni sus
    metadatos. No cubre datos de terceros.
  - Aviso de copyright del sitio
    (`https://www.ecb.europa.eu/services/disclaimer/html/index.en.html`): uso
    libre de la información citando al BCE y reproduciéndola con exactitud; si
    el usuario la modifica (el aviso pone como ejemplo calcular tasas de
    crecimiento), tiene que decirlo de forma explícita.

  **Los dos textos no dicen lo mismo sobre las series derivadas.** Convertir a
  USD o dividir un precio por el M2 es modificar. Con lo leído, vale publicar
  el dato del BCE tal cual, con su fuente, y rotular cada derivada como
  cálculo propio. Es una lectura de las cláusulas, y va como supuesto.
- **Muestra: 2026-08 = 16447405; 2020-03 = 12791700** (ajustada).
- Contraste:
  - El anexo del comunicado del BCE del 25 de septiembre de 2026
    (`https://www.ecb.europa.eu/press/pdf/md/ecb.md2608_annex~1dd30faa76.en.pdf`)
    da 16447 miles de millones para 2026-08: igual, al redondeo.
  - El Banco de España republica las dos series
    (`https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0112.csv`
    y `be0110.csv`): idénticas a la API de 2026-06 a 2026-08, y distintas en
    meses anteriores (hasta 0.53 % en 2022-05). Que la diferencia sea porque
    no recarga las revisiones es una **inferencia**.
  - FRED `MYAGM2EZM196N` (origen FMI) terminó en marzo de 2017.
- **Lo que el contraste no prueba.** No hay una medición del M2 de la zona del
  euro independiente del BCE. El contraste es producto contra producto.

### D0.5 Japón: M2 del Banco de Japón (Money Stock) — leída, (b)

- **Identificador y URL.** Base `MD02` de "BOJ Time-Series Data Search", serie
  **`MAM1NAM2M2MO`** (M2, promedio de saldos). Descarga con la API pública,
  abierta el 2026-02-18
  (`https://www.boj.or.jp/en/statistics/outline/notice_2026/not260218a.htm`):
  `https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=MD02&code=MAM1NAM2M2MO`.
  Metadatos: `.../api/v1/getMetadata?format=csv&lang=en&db=MD02`. Notas
  explicativas: `https://www.boj.or.jp/en/statistics/outline/note/notest31.htm`;
  guía metodológica: `https://www.boj.or.jp/en/statistics/outline/exp/data/exms01.pdf`.
  El BoJ no ofrece archivos planos del Money Stock: fuera de la API solo están
  los PDF de los últimos doce comunicados.
- Emisor original: Banco de Japón, Departamento de Investigación y
  Estadística.
- Frecuencia nativa: mensual.
- **Convención: promedio de saldos del mes. El M2 vigente no se publica a fin
  de mes.** De las 42 series del bloque, las de fin de período son solo M1, M3
  y sus componentes. La guía explica que el promedio es la cifra titular
  porque el saldo de fin de mes fluctúa con el día de la semana. Para las
  instituciones que solo informan fin de mes, el "promedio" es la media del
  fin de mes actual y el anterior (guía, sección sobre el cálculo de
  promedios). **No leído:** una frase que diga que para el resto es un
  promedio diario.
- Unidad y moneda: 100 millones de yenes.
- **Inicio real: 2003-04 = 6767067.** Último dato: 2026-08 = 12963895
  (preliminar, publicado el 2026-09-09). 281 meses, sin huecos.
- **Definición.** Efectivo más depósitos (a la vista, cuasidinero y
  certificados de depósito) en los bancos con licencia nacional sin Japan Post
  Bank, los bancos extranjeros en Japón, las cooperativas shinkin, Shinkin
  Central Bank, Norinchukin y Shoko Chukin. Tenedores: empresas no
  financieras, hogares y gobiernos locales (notas explicativas y guía).
- **Quiebres.** Desde 2003-04 no hay ninguno declarado: la serie se compiló
  hacia atrás con la definición de 2008. El quiebre está contra la serie
  anterior (ver abajo).
- **Revisiones: toda la serie es revisable.** Los avisos del BoJ del
  2025-03-11 y del 2025-07-09 revisaron desde 2003-04 y desde 2005-01. El
  valor de 2020-03 que el BoJ publicó en mayo de 2020 (1045.4 billones de
  yenes) hoy es 10442899: 0.1 % menos. Cada descarga hay que versionarla.
- Calendario: preliminar el séptimo día hábil del mes siguiente (noveno para
  marzo y septiembre), 8:50 de Tokio; definitivo un mes después. Próxima:
  2026-10-14.
- Clave / registro: no. Límites declarados en el manual de la API: 250 códigos
  y 60.000 puntos por pedido; pide espaciar los pedidos repetidos.
- **Licencia: (b), solo no comercial, con dos condiciones propias.** Aviso de
  copyright del sitio (`https://www.boj.or.jp/en/about/copyright.htm`,
  sección "Copyright") y del sitio de series
  (`https://www.stat-search.boj.or.jp/info/notice_en.html`, punto 1): el
  contenido está protegido; se puede copiar y reproducir citando al Banco de
  Japón como fuente, **salvo con fines comerciales**, que exigen permiso
  previo; y el contenido no se puede alterar sin permiso. Instrucciones de la
  API (`https://www.stat-search.boj.or.jp/info/api_notice_en.pdf`, secciones
  I y II): quien publique un servicio que use la API tiene que **avisar por
  correo** al Departamento de Investigación y Estadística y mostrar un crédito
  con un texto fijo. El aviso no define "fines comerciales".
- **Muestra: 2026-08 = 12963895; 2020-03 = 10442899.**
- Contraste: el comunicado del BoJ de agosto de 2026
  (`https://www.boj.or.jp/en/statistics/money/ms/ms2608.pdf`) da 1296.4
  billones de yenes: igual, al redondeo. El tablero estadístico del gobierno
  japonés (e-Stat Dashboard, indicador `0702010200000010010`) trae los 281
  meses **idénticos**; es una republicación del dato del BoJ.

**La serie anterior: M2+CDs.** En la misma base, todas discontinuadas:

| Serie | Qué es | Rango con dato |
| --- | --- | --- |
| `MAMS1ENM2C` | M2+CDs, fin de período, sin bancos extranjeros | 1955-01 a 1999-03 |
| `MAMS1ANM2C` | M2+CDs, promedio, sin bancos extranjeros | 1967-01 a 1999-03 |
| `MAMS3ANM2C` | M2+CDs, promedio, con bancos extranjeros | 1998-04 a 2008-04 |
| `MAMS3ENM2C` | M2+CDs, fin de período, con bancos extranjeros | 1998-04 a 2008-03 |

- **Quiebres declarados:** mayo de 1979 (nacen los certificados de depósito:
  el agregado pasa a ser M2+CDs); abril de 1998 (entran como emisores los
  bancos extranjeros en Japón y Shinkin Central Bank); junio de 2008, con
  datos desde 2003-04 (el M2 nuevo cambia los tenedores: salen las sociedades
  de valores, las compañías tanshi y los no residentes).
- **Superposición medida en la descarga.** M2 nuevo contra M2+CDs (promedio):
  61 meses comunes (2003-04 a 2008-04), con el M2 nuevo entre 0.42 % y 0.59 %
  por debajo. M2+CDs con y sin bancos extranjeros: 12 meses comunes (1998-04 a
  1999-03), con 0.41 % a 0.48 % de diferencia.
- **Postura del BoJ.** No construyó una serie larga enlazada porque no lo
  considera apropiado desde la exactitud estadística; mantiene las series
  viejas en línea y dice que el M2 puede analizarse desde 1967 con M2+CDs
  porque la diferencia es pequeña (borrador final de la revisión de 2008,
  `https://www.boj.or.jp/en/statistics/outline/notice_2008/data/ntms23.pdf`).
  Sí publica una serie de variación interanual empalmada
  (`MAM1YAM2M2MO`, desde 1968-01).
- Contraste histórico: FRED `MYAGM2JPM189S` (origen FMI) coincide con las
  series desestacionalizadas del BoJ en las cinco fechas probadas entre 1990 y
  2003. Esa serie de FRED terminó en 2017-02; la de origen OCDE, en 2013-12.

### D0.6 China: M2

La pregunta era si existe una fuente oficial con términos claros y descarga
reproducible. **Con el PBoC como fuente, no: falla la licencia.** Hay un
republicador con términos abiertos, la OCDE, con tres salvedades.

#### D0.6.1 Banco Popular de China, tabla "Money Supply" — leída, sin permiso de reutilización

- **Identificador y URL.** Fila `货币和准货币（M2）` de la tabla 货币供应量, una
  tabla por año. Índice de 2026:
  `https://www.pbc.gov.cn/diaochatongjisi/116219/116319/2026ntjsj/hbtjgl/index.html`;
  lista de años: `https://www.pbc.gov.cn/diaochatongjisi/116219/116319/index.html`.
  El archivo del año en curso el 2026-10-05:
  `https://www.pbc.gov.cn/diaochatongjisi/attachDir/2026/09/2026091418181718462.xlsx`.
  **El sitio en inglés está detenido:** no tiene sección 2026 y su tabla de
  2025 termina en octubre. El vigente es el chino.
- Emisor original: PBoC, Departamento de Estadística y Análisis.
- Frecuencia nativa: mensual.
- Convención: saldo a fin de mes. Lo dicen el informe mensual del PBoC, el
  nombre del indicador en la Oficina Nacional de Estadísticas (valor de fin de
  período) y el calendario de publicación del PBoC.
- Unidad y moneda: `Unit:100 Million Yuan` (cien millones de yuanes).
- **Inicio real: la tabla "Money Supply" existe desde 2004.** De 2000 a 2003
  solo hay un balance monetario mensual ("Monetary Survey") con una fila
  parecida, que no es la misma serie. Último dato: **2026-08 = 3568083.60**,
  publicado el 2026-09-14. No se leyeron todos los años: faltan 2005,
  2007–2010, 2012–2014, 2016 y 2019.
- **Quiebres declarados por el PBoC** en las notas al pie de sus tablas:
  - **2011-10:** M2 pasa a incluir los depósitos de los centros del fondo de
    vivienda y los de instituciones financieras no depositarias.
  - **2018-01:** cambia el tratamiento de los fondos del mercado monetario. La
    tabla de 2017 ya trae el M2 revisado y comparable.
  - **2022-12:** el efectivo en circulación incluye el yuan digital. La nota
    dice que el crecimiento de M2 no cambia de forma apreciable.
  - **2025-01:** redefinición de **M1**. La nota no menciona a M2.
  - **2001-06** (entran los depósitos de garantía de clientes de sociedades de
    valores): lo declara la Oficina Nacional de Estadísticas, no una tabla del
    PBoC. Un quiebre en 2002 no se encontró en ninguna fuente.
- **Una anomalía en la fuente.** En la tabla de 2004, la columna de julio
  repite los valores de mayo en M2, M1 y M0.
- Calendario: mensual, hacia mediados del mes siguiente. Próximas:
  2026-10-16 y 2026-11-16.
- Clave / registro: no. Un programa recibe HTTP 200 sin desafío.
- **Obstáculos de acceso:**
  - **`robots.txt` excluye a todos los programas.** El archivo
    (`https://www.pbc.gov.cn/robots.txt`) permite el sitio a Baiduspider y lo
    veda a cualquier otro agente. No bloquea técnicamente; declara que el
    sitio no admite descargas automáticas.
  - Las direcciones de los archivos llevan un sello de fecha y cambian: hay
    que leer el índice de cada año cada vez.
  - Hubo dos HTTP 404 transitorios en unos 70 pedidos, y un informe de 2020
    que ya no está en su dirección original.
- **Licencia: derechos reservados, sin permiso general.** Aviso legal en
  chino (`https://www.pbc.gov.cn/rmyh/109345/index.html`, numeral 1): todo el
  material del sitio es propiedad intelectual del PBoC, y la atribución solo
  está prevista para los medios y sitios **ya autorizados** por el banco,
  que deben indicar el origen. El numeral 5 dice que prevalece la versión
  china. El sitio en inglés no declara nada. No encaja en (a) ni en (b): pide
  permiso previo, que es la clase (c).
- **Muestra: 2026-07 = 3555077.24; 2020-03 = 2080923.41.**
- Contraste: la Oficina Nacional de Estadísticas y la OCDE dan los mismos
  valores para las dos fechas. Las dos republican al PBoC.

#### D0.6.2 OCDE, "Monetary aggregates" — leída, (a) con reserva

- **Identificador y URL.** Conjunto `DSD_STES@DF_MONAGG`, serie
  `CHN.M.MABM.XDC`:
  `https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_MONAGG,/CHN.M.MABM.XDC.....?format=csvfilewithlabels`.
  API pública, sin clave.
- Emisor original: el PBoC (el metadato dice "National Central Banks"); la
  OCDE republica.
- Frecuencia: mensual. Unidad: millones de yuanes.
- Rango en la descarga: 1999-01 a 2026-07, 331 meses.
- **Tres salvedades:**
  1. **La OCDE la rotula "M3".** Desde 2004 coincide con el M2 del PBoC, al
     redondeo, en las 25 fechas comparadas, con dos excepciones: 2004-07 (la
     anomalía del PBoC) y 2017.
  2. **2017 no está revisado.** La OCDE conserva los valores anteriores a la
     revisión del PBoC: queda entre 0.52 % y 0.80 % por debajo de la tabla
     revisada, y el salto le cae en 2018-01.
  3. **Rezago:** el 2026-10-05 llegaba a julio; el PBoC ya tenía agosto.
- De 1999 a 2003 no hay tabla "Money Supply" del PBoC contra la cual
  comparar; contra su balance monetario, la OCDE difiere entre 1.0 % y 4.2 %.
- **Licencia: (a), con reserva.** Términos de la OCDE
  (`https://www.oecd.org/en/about/terms-conditions.html`, sección 3, "Data",
  "Permitted Use"): permite extraer, copiar, adaptar y distribuir los datos
  para cualquier fin, incluso comercial, dando crédito a la OCDE. **La
  reserva:** los mismos términos advierten que puede haber derechos de
  terceros, que le toca verificar al usuario. La serie de China no trae
  ninguna restricción en sus metadatos. Es el mismo caso del Pink Sheet
  (sección 4.5): con lo leído, vale la regla general.
- **No establecido:** si los derechos que el PBoC reserva sobre su sitio
  alcanzan a las cifras que la OCDE republica.
- Muestra: **2026-07 = 355507700; 2020-03 = 208092300** (millones de yuanes).

#### D0.6.3 Otras candidatas

- **Oficina Nacional de Estadísticas de China:** trae M2 de fin de período
  hasta 2026-07. Su servicio de consultas responde HTTP 403 a un programa, y
  sus términos limitan la reproducción. Solo sirve para un contraste a mano.
- **FMI:** en su conjunto de agregados monetarios, el filtro de país no
  ofrece China continental. Sus términos prohíben la descarga masiva
  automatizada.
- **FRED:** `MYAGM2CNM189N` (origen FMI) terminó en 2019-08, y la de origen
  OCDE en 2013-12. No hay ninguna serie vigente de M2 de China.

### D0.7 Balances de bancos centrales

Cuatro balances y una segunda fuente común, el BIS.

#### D0.7.1 Reserva Federal: total de activos (H.4.1) — leída, dominio público

- **Identificador y URL.** Publicación H.4.1, "Factors Affecting Reserve
  Balances". Página:
  `https://www.federalreserve.gov/releases/h41/current/default.htm`. Archivo
  con la historia: `https://www.federalreserve.gov/releases/h41/data/FRB_h41_xml.zip`
  (9.069.679 bytes; `H41_data.xml` fechado el 1 de octubre de 2026). Serie:
  **`RESPPA_N.WW`**, "Assets: Total Assets: Total assets: Wednesday level".
- Emisor original: Junta de Gobernadores del Sistema de la Reserva Federal.
- Frecuencia nativa: semanal.
- Convención: **nivel del miércoles**. No es fin de mes ni promedio.
- Unidad y moneda: millones de USD (`UNIT_MULT="1000000"`).
- Inicio real: **2002-12-18 = 720761**. Último dato: 2026-09-30 = 6743031.
  1.242 semanas.
- Clave / registro: no.
- Licencia: (a), dominio público. La misma cláusula de D0.2.
- Muestra: **2020-03-25 = 5254278**; **2026-09-30 = 6743031**.
- **Contraste, y una diferencia que no se conocía.** S2 baja hoy esta serie de
  FRED como `WALCL` (copia del repositorio del 2026-10-03). Contra el XML de
  la Junta: 1.242 semanas comunes, **725 idénticas y 517 distintas**. Todas
  las distintas están entre 2002-12-18 y 2013-12-04; desde 2013-12-11
  coinciden. La diferencia máxima es de 0.42 % (2007-07-11: 873060 en la
  Junta, 869407 en FRED). El título de `WALCL` en FRED dice *"Total Assets
  (Less Eliminations from Consolidation)"*, según el título ya registrado en
  `data/raw/ATRIBUCION.md`. **Verificado el 2026-10-06 (D0.15, A-D0-15):** la
  diferencia es exactamente la serie de eliminaciones de consolidación
  (`RESPPMAX_N.WW`), y el XML sí trae el total consolidado, `RESPPMA_N.WW`,
  igual a `WALCL` en las 1.242 semanas. **D0 publica `RESPPMA_N.WW`**, no la
  serie bruta que nombra el primer punto de esta ficha. S2 publica desde
  2020-01 y no se ve afectado.

#### D0.7.2 Eurosistema: total de activos (estado financiero semanal) — leída, (a)

- **Identificador y URL.** ECB Data Portal, conjunto ILM, serie
  **`ILM.W.U2.C.T000000.Z5.Z01`** ("Total assets/liabilities - Eurosystem").
  Descarga:
  `https://data-api.ecb.europa.eu/service/data/ILM/W.U2.C.T000000.Z5.Z01?format=csvdata`.
- Emisor original: BCE y bancos centrales nacionales.
- Frecuencia nativa: semanal, identificada por semana ISO (`2026-W39`).
- **Convención: saldo al cierre del viernes.** La guía del estado semanal
  (`https://www.ecb.europa.eu/pub/pdf/other/wfs-userguide.en.html`) dice que
  se publica los martes y describe el cierre del viernes anterior. No es fin
  de mes. Los estados extra de fin de año (31 de diciembre y apertura del 1 de
  enero) no están en la serie.
- Unidad y moneda: millones de EUR.
- **Inicio real: `1998-W53` = 697160** (la semana del 1 de enero de 1999).
  Último dato: `2026-W39` = 5897262 (25 de septiembre de 2026). 1.448 semanas,
  sin huecos.
- **Quiebres, ninguno marcado en la serie:**
  - **Composición cambiante**, como el M2. Al entrar Bulgaria, el total pasó
    de 6293178 (31 de diciembre de 2025) a 6332374 en el estado de apertura
    del 1 de enero de 2026: +0.62 %.
  - **Revalorización trimestral.** El oro, las divisas y los títulos se
    revalorizan a precios de mercado al cierre de cada trimestre; dentro del
    trimestre se anotan a precio de transacción. El estado del 31 de diciembre
    de 2025 separa −9614 de transacciones y +139041 de ajustes de fin de
    trimestre.
- Calendario: martes a las 15:00 de Fráncfort; el primero de cada trimestre,
  miércoles.
- Clave / registro y licencia: como D0.4.
- **Muestra: `2026-W39` = 5897262; `2020-W13` = 5062687** (27 de marzo de
  2020).
- Contraste: el estado semanal en HTML del BCE coincide en tres de las cuatro
  semanas probadas; la cuarta (2 de enero de 2026) salió con 6321445 y la API
  da 6321626, una revisión de 181 millones. FRED `ECBASSETSW` es un espejo
  exacto (1.448 de 1.448). BIS `WS_CBTA`: ver D0.7.5.

#### D0.7.3 Banco de Japón: total de activos — leída, (b)

- **Identificador y URL.** Base `BS01` ("Bank of Japan Accounts"), serie
  **`MABJMTA`** (total de activos). Descarga:
  `https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=BS01&code=MABJMTA`.
  Notas: `https://www.boj.or.jp/en/statistics/outline/note/notest1.htm`.
- Emisor original: Banco de Japón.
- Frecuencia nativa: mensual en la base. El balance se publica además tres
  veces al mes (días 10, 20 y fin de mes) como páginas HTML, en miles de
  yenes (`https://www.boj.or.jp/en/statistics/boj/other/acmai/index.htm`); esa
  frecuencia no está en la API.
- **Convención: saldo a fin de mes.** Los metadatos en inglés no lo dicen con
  esas palabras; sale de la nota en japonés (habla de los datos de fin de
  marzo y de septiembre), de que la serie coincide con los balances de fin de
  mes de 2020-04 y 2026-08, y de que el BIS la describe así.
- Unidad y moneda: 100 millones de yenes.
- **Inicio real: 1998-04 = 800652.** Último dato: 2026-08 = 6446620. 341
  meses, sin huecos. El BIS tiene la misma serie desde 1953-01 (D0.7.5).
- **Quiebre: abril de 2001.** Cambio contable de las operaciones repo: hasta
  marzo de 2001 el total incluye títulos en custodia y títulos tomados en
  préstamo. La nota (s) de la serie dice que el total no es comparable entre
  antes y después.
- Revisiones: marzo y septiembre se publican primero como preliminares y unos
  tres meses después como definitivos (2020-03: 0.009 % de diferencia).
- Calendario: comienzos del mes siguiente. Próxima: 2026-10-08.
- Clave / registro y licencia: como D0.5.
- **Muestra: 2026-08 = 6446620; 2020-03 = 6044846.**
- Contraste: el balance del BoJ al 31 de agosto de 2026
  (`.../acmai/release/2026/ac260831.htm`) da 644662019610 miles de yenes:
  igual, al truncar. BIS `WS_CBTA`: 340 meses comunes, **340 idénticos**.

#### D0.7.4 Banco Popular de China: total de activos — leída, sin permiso de reutilización

- **Identificador y URL.** Fila `总资产 Total Assets` de la tabla 货币当局资产负债表
  ("Balance Sheet of Monetary Authority"), en el mismo índice de D0.6.1.
  Archivo de 2026:
  `https://www.pbc.gov.cn/diaochatongjisi/attachDir/2026/09/2026091418164535833.xlsx`.
- Emisor original: PBoC.
- Frecuencia nativa: mensual. Convención: saldo a fin de mes.
- Unidad y moneda: cien millones de yuanes.
- **Inicio real: la fila de total aparece en la tabla de 2002** (2002-01 =
  45311.03). Las tablas de 1999 y 2000 no traen total; la de 2001 no se leyó.
  Último dato: **2026-08 = 498567.28**.
- Quiebres declarados en las notas: 2011-01 (cambia la definición de la base
  monetaria; no altera el total); 2017 (las cuentas en yuanes con organismos
  internacionales pasan a posición neta); 2021-08 (la asignación de DEG del
  FMI suma 267.900 millones de yuanes a los activos externos); 2022-12 (la
  emisión incluye el yuan digital).
- Acceso y licencia: los de D0.6.1.
- **Muestra: 2026-06 = 494334.98; 2020-03 = 365374.74.**
- Contraste: BIS `WS_CBTA` da 49433.5 y 36537.47 miles de millones de yuanes:
  igual, al redondeo. El BIS declara que usa el balance mensual del PBoC desde
  enero de 2002.
- **Alternativa con términos abiertos:** el BIS (D0.7.5), con las mismas
  cifras, un rezago de dos meses y los términos de uso de D0.9.

#### D0.7.5 BIS, activos totales de bancos centrales (`WS_CBTA`) — leída, (a), contraste

Es la segunda fuente de los cuatro balances: la compila un organismo distinto
y se baja con un programa.

- URL: `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.{área}?format=csv`,
  con `US`, `XM` (zona del euro), `JP` y `CN`. Sin clave. Las filas en moneda
  local son las de `UNIT_MEASURE=XDC` y `TRANSFORMATION=N`.
- Frecuencia: mensual. Unidad: miles de millones de la moneda local.
- Licencia: (a). Los términos de D0.9 (bonos) son los mismos.
- Lo que trae y cómo se compara con el dueño del dato:

  | Área | Rango | Origen declarado por el BIS | Comparación hecha el 2026-10-05 |
  | --- | --- | --- | --- |
  | `US` | 1914-11 a 2026-07 | H.4.1 desde marzo de 1989; antes, una reconstrucción académica del balance semanal desde 1914 (Bao y otros, 2018), tomada de FRED | Igual al **último miércoles del mes** de FRED `WALCL` en 284 de 284 meses. Contra el XML de la Junta difiere en 118 meses, todos entre 2002-12 y 2012-09 (hasta 0.23 %) |
  | `XM` | 1998-12 a 2026-07 | Estado financiero semanal del Eurosistema | Igual al BCE en 332 de 332 meses, tomando **el viernes de la semana que contiene el último día hábil del mes**. Ese viernes puede caer en el mes siguiente: para marzo de 2020 es el 3 de abril |
  | `JP` | 1953-01 a 2026-07 | Banco de Japón, empalmado por el BIS | Igual al BoJ en 340 de 340 meses |
  | `CN` | 1999-12 a 2026-06 | Balance mensual del PBoC desde enero de 2002; antes, otras fuentes | Ver D0.7.4 |

- **El BIS no usa la misma regla para pasar de semanal a mensual en EE.UU. y
  en la zona del euro.** La de la zona del euro la declara en sus metadatos
  (toma la última semana hábil del mes); la de EE.UU. sale de la comparación.
- **Rezago.** El 2026-10-05 el BIS llegaba a 2026-07, y a 2026-06 en China.
  Los dueños ya tenían agosto y septiembre.
- **Las series del BIS están empalmadas** (`METHOD_REF = BIS-spliced`). Sirven
  de contraste en el tramo que coincide con el dueño. Usar su historia más
  larga (la Fed desde 1914, el BoJ desde 1953) sería publicar un empalme
  ajeno: no se propone.

### D0.8 Tipos de cambio

#### D0.8.1 Junta de la Reserva Federal, H.10 y G.5 — leída, dominio público

- **Identificador y URL.** Publicación H.10, "Foreign Exchange Rates". Página:
  `https://www.federalreserve.gov/releases/h10/current/default.htm`
  (publicación del 28 de septiembre de 2026). Archivo con la historia:
  `https://www.federalreserve.gov/releases/h10/data/FRB_h10_xml.zip`
  (2.082.528 bytes; `H10_data.xml` fechado el 1 de octubre de 2026).
- Emisor original: Junta de Gobernadores; las tasas las certifica el Federal
  Reserve Bank of New York.
- **Convención** (página "About",
  `https://www.federalreserve.gov/releases/h10/about.htm`, literal): *"The
  data are noon buying rates in New York for cable transfers payable in the
  listed currencies."* La serie mensual es el promedio del mes (*"G.5
  provides the monthly release and contains monthly averages of bilateral
  exchange rates"*).
- Series leídas del XML:

  | Moneda | Diaria | Inicio real | Mensual (promedio) | Inicio real | Unidad |
  | --- | --- | --- | --- | --- | --- |
  | Euro | `RXI$US_N.B.EU` | 1999-01-04 = 1.1812 | `RXI$US_N.M.EU` | 1999-01 = 1.1591 | **USD por EUR** |
  | Yen | `RXI_N.B.JA` | 1971-01-04 = 357.73 | `RXI_N.M.JA` | 1971-01 = 358.02 | JPY por USD |
  | Yuan | `RXI_N.B.CH` | 1981-01-02 = 1.5341 | `RXI_N.M.CH` | 1981-01 = 1.5518 | CNY por USD |

  El euro viene al revés que las otras dos: la publicación marca con asterisco
  las monedas cotizadas en USD por unidad.
- Último dato el 2026-10-05: diario, 2026-09-25; mensual, 2026-09 (1.1505,
  156.4171 y 6.7084). La diaria tiene días sin dato (feriados): 6.955 de 7.235
  filas con valor en el euro.
- Calendario: los datos por país se actualizan *"weekly on Mondays at 4:15
  p.m."*
- Clave / registro: no.
- Licencia: (a), dominio público. La misma cláusula de D0.2.
- Muestra: **2020-03**, promedio mensual: 1.1046 USD por EUR, 107.6673 JPY por
  USD, 7.0205 CNY por USD.
- Contraste: FRED `EXUSEU`, `EXJPUS` y `EXCHUS` contra las tres mensuales del
  XML: 333, 669 y 549 meses comunes, **todos idénticos**. Es el mismo emisor
  por otro canal. El contraste independiente es el tipo de referencia del BCE
  (D0.8.2).

#### D0.8.2 BCE, tipo de cambio de referencia del euro — leída, (a), contraste

- Series: diaria `EXR.D.USD.EUR.SP00.A`; mensual promedio
  `EXR.M.USD.EUR.SP00.A`; mensual de fin de período `EXR.M.USD.EUR.SP00.E`.
  Descarga: `https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata`.
- Convención: tipo de referencia del BCE, fijado hacia las 14:15 de Fráncfort
  (el título de la serie dice "2.15 pm (C.E.T.)"; el marco vigente, de junio
  de 2026, dice hacia las 14:10). Unidad: USD por EUR.
- Inicio real: 1999-01-04 = 1.1789. Último dato: 2026-10-02 = 1.1225. La
  mensual promedio va de 1999-01 a 2026-09, 333 meses.
- Licencia: la de D0.4. El BCE advierte que estos tipos son informativos y
  desaconseja usarlos para transacciones.
- Contraste entre el BCE y el H.10, que son fijaciones a horas distintas:

  | Qué | BCE | H.10 | Diferencia |
  | --- | --- | --- | --- |
  | Promedio de 2020-03 | 1.1063 | 1.1046 | 0.16 % |
  | Promedio de 2026-09 | 1.1513 | 1.1505 | 0.07 % |
  | Diario, 2020-03-31 | 1.0956 | 1.1016 | 0.55 % |
  | Promedios mensuales, todos los meses comunes | | | media 0.06 %, máxima 0.31 % |
  | Diarios, 6.613 días comunes | | | media 0.25 %, percentil 99 de 1.15 %, máxima 2.73 % |

  El promedio mensual casi borra la diferencia de hora; el dato de un solo
  día, no.
- El Bundesbank republica la serie diaria (7.106 valores idénticos).

### D0.9 Riqueza por clase de activo

El criterio es el de 0.2 más uno propio de esta sección: hace falta una
**serie** (la misma definición repetida en el tiempo), no un número de un
informe. Resumen de lo leído; el detalle sigue abajo.

| Clase | Mejor candidata | ¿Serie? | Licencia | Lo que cubre de verdad |
| --- | --- | --- | --- | --- |
| Inmuebles | Savills, informe bienal | No: estimación puntual, reexpresada en cada edición | (c) | "Global", según el informe |
| Bonos | BIS, títulos de deuda (`WS_NA_SEC_DSS`) | Sí, trimestral, por economía | (a) | 49 economías declarantes; el BIS no publica un total mundial |
| Acciones | Banco Mundial `CM.MKT.LCAP.CD`, agregado `WLD` | Sí, anual, 1975 a 2025 | (a), CC BY 4.0 | La suma de los países con dato; faltan plazas grandes |
| Oro (cantidad) | World Gold Council | Sí, pero detrás de una cuenta | (c) | Existencias sobre la superficie |
| BTC | Coin Metrics community, `CapMrktCurUSD` | Sí, diaria, desde 2010-07-18 | (b), CC BY-NC 4.0 | Toda la oferta emitida |
| Riqueza total | UBS, McKinsey, WID | Informes; WID no se pudo leer | (c) / s/d | 56 y 23 economías |

**Inmuebles.**

- Savills publica una estimación cada dos años, aproximadamente
  (`https://impacts.savills.com/market-trends/how-much-is-global-real-estate-worth.html`,
  septiembre de 2025): 393.3 billones de USD a fin de 2024, sumando
  residencial, comercial y tierra agrícola. Las ediciones anteriores leídas
  dan 379.7 (fin de 2022), 326.5 (2020) y 280.6 (fin de 2017).
- **No es una serie:** cada edición reexpresa la historia. El valor de 2019
  implícito es de unos 311, 320 o 324 billones según se lo deduzca de la
  edición de 2021, de 2023 o de 2025 (cálculo propio sobre las variaciones
  que cada una declara).
- Licencia: (c). Los términos
  (`https://www.savills.co.uk/footer/terms-and-conditions.aspx`, sección 3,
  "Intellectual Property") prohíben reproducir el contenido o incorporarlo a
  otro sitio; solo admiten copias temporales para uso personal no comercial.
- **Alternativa abierta, solo de EE.UU.:** cuentas financieras de la Reserva
  Federal (Z.1), serie `LM155035005.Q`, inmuebles de hogares e instituciones
  sin fines de lucro a valor de mercado. Trimestral desde 1952 (anual de 1945
  a 1951), fin de período, millones de USD, dominio público. Muestra:
  2026:Q2 = 54073947; FRED `HNOREMQ027S` da lo mismo.
- La OCDE (tabla 9B, balances de activos no financieros) tiene viviendas y
  tierra por país, en moneda nacional, para 34 países; no están China, India
  ni Brasil. No da un total mundial.

**Bonos.**

- BIS, "Debt securities statistics": `https://data.bis.org/topics/DSS`;
  descarga masiva `https://data.bis.org/static/bulk/WS_NA_SEC_DSS_csv_col.zip`;
  API sin clave. Trimestral, fin de período, en miles de millones de USD.
  Última publicación: 2026-09-14, con datos hasta 2026-Q1.
- **No hay área "mundo".** El total de títulos de deuda de todos los emisores
  existe para 49 de las 59 economías. Muestra: EE.UU., 2025-Q4 = 61130.116.
- **La suma es un cálculo propio, no un dato del BIS:** las 49 economías dan
  145068 a 2024-Q4 y 160441 a 2025-Q4. SIFMA, que reempaqueta al BIS, publica
  145308.3 y 160704.1 para esos años (0.2 % de diferencia).
- **Dos quiebres que impiden llamarla "global":** la cobertura crece (15
  economías en 1989, 41 entre 2008 y 2014, 49 desde 2020-Q4) y la valuación es
  mixta. El BIS lo declara en la definición: unas cifras van a valor de
  mercado y otras a valor nominal.
- Licencia: (a). Términos de uso de las estadísticas del BIS
  (`https://data.bis.org/help/legal`, "Terms of permitted use of BIS
  statistics"): uso sin restricciones si se cita al BIS como fuente, no se
  sugiere su respaldo y, en un producto comercial, no se cobra un cargo
  adicional por incluirlas.

**Acciones.**

- Banco Mundial, indicador `CM.MKT.LCAP.CD`, agregado `WLD`:
  `https://api.worldbank.org/v2/country/WLD/indicator/CM.MKT.LCAP.CD?format=json`.
  Anual, fin de año, USD corrientes. Emisor original: World Federation of
  Exchanges. Con dato de 1975 a 2025, sin huecos. Muestra: **2024 =
  115086929890000; 2025 = 141297217290000.**
- **Quiebre de fuente** (metadato del indicador): hasta 2013 los datos eran de
  Standard & Poor's; en diciembre de 2015 el Banco Mundial reemplazó las
  series por las de la WFE.
- **Subcobertura.** El agregado es la suma de los países con dato, y en los
  años recientes faltan, entre otros, Reino Unido (2015 a 2020 y 2023 a 2025),
  Francia (desde 2019), Italia (desde 2015) y Países Bajos (desde 2018). Queda
  7 % por debajo del total que la WFE publica para fin de 2025, y 13 % por
  debajo del que SIFMA atribuye a la WFE para 2024.
- Licencia: (a). El metadato de la serie declara `License_Type: "CC BY-4.0"`,
  sin restricción de terceros.
- La WFE directamente es (c): su portal pide cuenta y su aviso exige contactar
  a la Secretaría antes de reproducir cualquier dato.

**Oro.** El precio ya está (Pink Sheet, sección 4.5). Falta la cantidad.

- World Gold Council
  (`https://www.gold.org/goldhub/data/how-much-gold`, 18 de agosto de 2026):
  222.600 toneladas sobre la superficie a fin del segundo trimestre de 2026.
  Anuncia una serie anual de 2010 a 2026, pero el archivo responde HTTP 403 y
  pide iniciar sesión. Licencia: (c), la misma lectura de la sección 4.3.
- USGS, dominio público: **no publica existencias.** Los *Mineral Commodity
  Summaries* de 2025 y 2026 no traen el oro total extraído. La página de
  preguntas frecuentes
  (`https://www.usgs.gov/faqs/how-much-gold-has-been-found-world`) dice,
  literal: *"About 244,000 metric tons of gold has been discovered to date
  (187,000 metric tons historically produced plus current underground reserves
  of 57,000 metric tons)."* No tiene fecha. La serie histórica (Data Series
  140) trae la producción mundial anual de 1900 a 2022: es un flujo, no un
  acervo.

**BTC.**

- Coin Metrics community, métricas `CapMrktCurUSD` (capitalización) y
  `SplyCur` (oferta emitida), sin clave, en la misma API de la sección 6.2.
  Diarias, a fin del día en UTC. Capitalización con dato desde 2010-07-18;
  oferta desde 2009-01-03. Sin huecos.
- Muestra: **2026-10-04 = 1738496872160.74 USD**, con 20093398.00 BTC.
  Contraste: blockchain.com da 0.19 % menos de capitalización y la misma
  oferta (0.0004 %).
- La capitalización es el producto de la oferta por `PriceUSD`, al error de
  redondeo. Licencia: la misma (b) de A-R0-4.

**Riqueza total.**

- UBS, *Global Wealth Report 2026*: informe anual en PDF, 56 mercados, sin
  datos descargables. Avisa que cambió de método y que no siempre se puede
  comparar con ediciones previas. (c): el PDF prohíbe reproducirlo sin permiso
  escrito.
- McKinsey Global Institute, "The global balance sheet 2026": 23 economías,
  sin datos descargables. (c): sus términos prohíben extraer datos del sitio
  por cualquier medio sin permiso expreso. **No se usa ninguna cifra suya.**
- World Inequality Database: **no leída.** El 2026-10-05 `wid.world` mostraba
  una página de dominio estacionado. En la copia archivada del 2026-10-01 no
  hay declaración de licencia para los datos.
- **Alternativa abierta, solo de EE.UU.:** Z.1, `FL152090005.Q`, patrimonio
  neto de hogares e instituciones sin fines de lucro. Mismas frecuencia,
  convención y licencia que la serie de inmuebles. Muestra: 2026:Q2 =
  195870496 millones de USD; FRED `TNWBSHNO` da lo mismo.

### D0.10 Decisiones propuestas

**Ninguna está tomada.** Cada una dice qué se propone, con qué evidencia, y
qué alternativa hay. Las que se aprueben pasan a `SUPUESTOS.md` con el número
que les asigna D0.12.

#### D0.10.1 Moneda y nombre

- **Propuesta.** Cada M2 se publica en su moneda y en su unidad nativa, con
  su variación interanual calculada al lado y rotulada como cálculo propio. El
  agregado en USD es una serie **derivada**, aparte.
- **Nombre.** Deja de llamarse "M2 Global". Con China (D0.10.10) es "M2 de
  cuatro economías"; sin China, "M2 de tres economías (EE.UU., Eurozona y
  Japón)". **Quedó en tres (D0.10.11).**
- **Tipo de cambio.** H.10 de la Junta (D0.8.1): promedio mensual para las
  series que son promedios (EE.UU., Japón) y último dato diario del mes para
  las que son saldos de fin de mes (Eurozona, China).
- **Cómo declarar el efecto del tipo de cambio.** Junto al agregado a tipo de
  cambio de cada mes, publicar el mismo agregado a tipo de cambio constante
  (el del primer mes común). La diferencia entre los dos es el efecto del
  tipo de cambio, mes a mes, sin estimar nada. Elegir el mes de referencia es
  un supuesto.
- **Ajuste estacional.** El agregado suma las series **sin ajustar**. EE.UU.,
  la Eurozona y Japón publican además una ajustada; de China solo se leyó
  una serie. Para EE.UU. solo, se publican las dos y la titular es la
  ajustada, como en el H.6.

#### D0.10.2 Historia: desde cuándo queda cada serie

Cada serie empieza donde empieza su fuente oficial. Sin 1913 y sin
interpolación.

| Serie | Primer dato | Notas |
| --- | --- | --- |
| M2 de EE.UU. (H.6) | **1959-01** | Lo anterior es otro agregado y va aparte (D0.10.6) |
| M2 de la Eurozona (BCE) | **1980-01** en la fuente | De 1980-01 a 1997-08, estado "estimación" (D0.4). Alternativa: publicar solo desde 1997-09 |
| M2 de Japón (BoJ) | **2003-04** | M2+CDs (1967-01 a 2008-04) es otra serie; el BoJ no las empalma |
| M2 de China | **2004-01**, si se aprueba la vía de la OCDE (D0.10.10) | Con el PBoC como fuente: NO MEDIDO |
| Agregado en USD | **2004-01** con China; **2003-04** sin China | Lo limita la serie que empieza más tarde |
| Balance de la Fed (H.4.1) | **2002-12** | Con 118 meses en disputa hasta 2012-09 (D0.10.8) |
| Balance del Eurosistema | **1999-01** | Con los saltos de D0.7.2 declarados |
| Balance del BoJ | **1998-04** | Quiebre contable en 2001-04 |
| Balance del PBoC | **2002-01**, si se aprueba la vía del BIS (D0.10.10) | Con el PBoC como fuente: NO MEDIDO |
| USD por EUR (H.10) | 1999-01 | |
| JPY por USD (H.10) | 1971-01 | |
| CNY por USD (H.10) | 1981-01 | |

Antes de 1999 no hay tipo de cambio del euro: la Eurozona no puede entrar en
un agregado en USD antes de esa fecha.

#### D0.10.3 Índice Denominador 60/40

- **Propuesta: eliminarlo.**
- **Por qué.** Tres razones:
  1. La ponderación 60/40 no tiene fuente: es una constante del código.
  2. La base 100 = 1913 no tiene dato. De las ocho series que lo componen,
     en las fuentes leídas solo hay una cifra de 1913: la fecha de balance de
     EE.UU. del 30 de junio, que es otro agregado (D0.3.1). Las otras siete
     no existen.
  3. Los dos lados se superponen. El efectivo es parte de M2 (definición del
     H.6, D0.2) y a la vez es un pasivo del banco central: el mismo H.6 lo
     publica como componente de la base monetaria. Un índice que suma M2 y
     balances cuenta dos veces esa parte, y además mezcla pasivos del sistema
     bancario con activos del banco central.
- **En su lugar:** las dos familias se muestran por separado, cada una con su
  ficha.
- **Si se quisiera conservar**, sería un supuesto con la ponderación y la base
  declaradas, y con la base en un mes que tenga dato en todas las series. No
  se propone.

#### D0.10.4 Convención y frecuencia

La frecuencia común es **mensual**. La convención no puede ser una sola: la
fija cada emisor.

| Serie | Convención nativa | ¿Existe la otra? |
| --- | --- | --- |
| M2 de EE.UU. | Promedio mensual de cifras diarias | No hay fin de mes |
| M2 de la Eurozona | Saldo a fin de mes | No hay promedio |
| M2 de Japón | Promedio de saldos del mes | No hay fin de mes para M2 |
| M2 de China | Saldo a fin de mes | No |
| Balance de la Fed | Nivel del miércoles | El H.4.1 trae promedios semanales; no se evaluaron |
| Balance del Eurosistema | Cierre del viernes | No |
| Balance del BoJ | Saldo a fin de mes | Sí: días 10 y 20, solo en HTML |
| Oro y BTC de `senales/` | Promedio mensual de precios diarios | — |

- **La propuesta inicial ("fin de mes para saldos") no se puede cumplir** para
  EE.UU. ni para Japón: sus bancos centrales publican el M2 como promedio.
- **Propuesta.** Cada serie se publica en su convención nativa, declarada en
  su ficha. No se convierte una convención en otra.
- **De semanal a mensual** (Fed y Eurosistema): el último dato semanal fechado
  dentro del mes, con su fecha de origen visible en el CSV, como hace A-S2-5
  con el ON RRP. Para la Fed coincide con lo que hace el BIS; para el
  Eurosistema no (D0.7.5), y el gate tiene que usar la regla del BIS o
  comparar semana contra semana.
- **Cómo convive con la regla de los ratios.** `CLAUDE.md` exige que los dos
  lados de un ratio usen la misma convención, hoy promedio mensual.
  - **Oro / M2 de EE.UU. y BTC / M2 de EE.UU. la cumplen sin excepción:** los
    dos lados son promedios mensuales de cifras diarias.
  - **Contra el agregado no se cumple:** el agregado mezcla promedios (EE.UU.,
    Japón) con saldos de fin de mes (Eurozona, China). Publicar un ratio
    contra el agregado exige una excepción escrita a esa regla. **No se
    propone en esta fase.**
  - Alternativa que se descarta: aproximar el promedio de la Eurozona con la
    media de dos fines de mes consecutivos. Es fabricar un valor que el BCE no
    publica.

#### D0.10.5 "Activos vs Denominador"

- **Propuesta.** Dos pares nuevos en `ratios.py`, con la misma lógica de
  publicación que los actuales:

  | Par | Primer mes posible | Lo que limita |
  | --- | --- | --- |
  | Oro / M2 de EE.UU. | 1960-01 | El Pink Sheet empieza en 1960-01. Hereda los meses no aptos por redondeo (A-R0-17) y los meses en disputa (A-R0-20) del oro |
  | BTC / M2 de EE.UU. | 2013-01 | A-R0-10 |

- **Unidad.** Precio en USD dividido por M2 en billones (10¹²) de USD. Llevar
  el resultado a base 100 es presentación del sitio, no un dato: se decide en
  la parte B.
- **M2 que entra en el ratio:** la serie ajustada (`M2.M`), que es la titular
  de la Junta. Es un supuesto.
- El último mes del par es el último mes completo en las dos fuentes. El M2
  llega con unas tres semanas de rezago: el 2026-10-05 el último era agosto.
- **Contra el agregado:** no en esta fase (D0.10.4).
- **S&P 500 / M2: NO MEDIDO**, pendiente de permiso del dueño del índice. Sin
  cambios respecto de la sección 9.1.

#### D0.10.6 EE.UU. antes de 1959

**Lo que se pidió:** una serie de oferta monetaria desde 1914 o antes,
observada, sin interpolar, con su quiebre visible.

**Lo que las fuentes permiten** (D0.3):

- Serie mensual observada: **solo desde 1947-01**, de la Junta.
- Antes de 1947, observado: **fechas de balance** de la Junta. Una por año
  (30 de junio) de 1892 a 1922; dos por año (junio y diciembre) de 1923 a
  1946.
- Mensual antes de 1947: solo la reconstrucción de Friedman y Schwartz (desde
  1907-05), que sus autores declaran interpolada en parte, y cuya versión en
  archivo de datos (NBER) no tiene licencia declarada.
- Con la definición del M2 actual: nada antes de 1959.

**Propuesta: tres tramos de publicaciones de la Junta, sin empalmar.**

| Tramo | Serie | Qué es | Frecuencia | Estado | Fuente |
| --- | --- | --- | --- | --- | --- |
| 1892-06 a 1946-12 | Efectivo y depósitos en bancos comerciales, en fechas de balance | Efectivo fuera de bancos + depósitos a la vista ajustados + depósitos a plazo en bancos comerciales. Saldo del día, sin ajuste estacional | Anual hasta 1922; semestral desde 1923 | **Dato de fecha de balance, estimado en parte** (lo declara la Junta) | Tabla 9 del volumen 1914–1941 y su continuación en el volumen 1941–1970 |
| 1947-01 a 1958-12 | Efectivo y depósitos en bancos comerciales, mensual | El mismo concepto: "money stock" + depósitos a plazo ajustados | Mensual, promedio de cifras diarias | **Dato de la Junta**, que declara haberlo estimado hacia atrás hasta 1947 | Tabla 1.1 del volumen 1941–1970 |
| 1959-01 en adelante | M2 (H.6) | Definición actual | Mensual, promedio de cifras diarias | Dato | D0.2 |

- **Los tres tramos van como series separadas.** No se multiplica ninguna por
  un factor. Hay dos quiebres declarados y visibles:
  - **1946 / 1947:** cambia la frecuencia, la convención (de saldo de un día a
    promedio del mes) y el ajuste estacional. El concepto es el mismo.
  - **1958 / 1959:** cambia la definición.
- **La superposición se publica.** El tramo mensual se publica hasta 1969-09
  o hasta donde llegue la Tabla 1.1, para que la diferencia de definición
  quede a la vista: 129 meses en los que el M2 actual es entre 38 % y 49 %
  más grande (D0.3.5).
- **Ningún tramo se llama "M2".** El nombre propuesto es "efectivo y depósitos
  en bancos comerciales", con la aclaración de que es el concepto que
  Friedman y Schwartz llamaron M2.
- **Lo que cuesta.** Las dos tablas son escaneos: hay que transcribirlas a
  mano. Son unas 80 fechas de balance y 144 meses hasta 1958; 273 meses si
  también se transcribe la superposición hasta 1969-09. El control propuesto
  está en D0.11.
- **Lo que no se obtiene.** Una curva mensual continua de 1914 a hoy. Entre
  1914 y 1946 la serie tiene uno o dos puntos por año, y así se muestra: un
  hueco es un hueco.

**Alternativa: la serie mensual del NBER desde 1907-05** (`m14144a`,
`m14144c`). Es mensual y ya está en archivos de datos. Tiene dos condiciones:
el tramo 1907–1946 llevaría el estado **"estimación"** (D0.3.2), y **no se
puede publicar sin permiso escrito del NBER** (regla 0.2: fuente sin licencia
declarada). Si se pide y se obtiene el permiso, puede publicarse como una
cuarta serie, también sin empalmar. Mientras tanto se calcula en el pipeline
como control de consistencia de las otras dos.

**Otras economías.** No se reconstruye nada anterior a la fuente oficial. Un
caso aparte, que no es una reconstrucción: el BoJ mantiene publicada su serie
anterior, M2+CDs, de 1967-01 a 2008-04. Se puede publicar como serie separada
del M2 actual, con los 61 meses de superposición. No se propone para la
primera versión; queda como decisión.

#### D0.10.7 Riqueza por clase de activo

- **Propuesta: eliminar "riqueza global" y su distribución porcentual.** No
  se puede calcular una distribución cuando dos de las cinco clases no están
  medidas y otras dos cubren solo una parte del mundo.
- En su lugar, una tarjeta por clase, con lo que hay:

  | Clase | Qué se muestra | Estado |
  | --- | --- | --- |
  | Inmuebles | Sin valor | **NO MEDIDO:** no hay una serie global con licencia abierta |
  | Bonos | Suma de las 49 economías que declaran al BIS, trimestral, desde 2020-Q4 (panel fijo) | Dato del BIS por economía; **la suma es cálculo propio**. No se rotula "global" |
  | Acciones | Banco Mundial, agregado `WLD`, anual, 1975 a 2025 | Dato, con la advertencia de subcobertura (7 % a 13 % por debajo de la WFE en 2024 y 2025) |
  | Oro | Sin valor | **NO MEDIDO:** falta la cantidad. La única serie de existencias es (c) |
  | BTC | Capitalización de Coin Metrics | Dato, bajo A-R0-4 |
  | Riqueza total | Sin valor | **NO MEDIDO** |

- **Las estimaciones puntuales de Savills y del World Gold Council no se
  muestran como valor.** Las dos son (c), y A-R0-12 limita las fuentes (c) a
  contrastar. Mostrarlas con el estado "estimación", año y cita es una
  decisión que cambia esa regla.
- **Opción solo de EE.UU.**, si se quiere una serie abierta de inmuebles y de
  patrimonio: las dos del Z.1 (D0.9), rotuladas "hogares de EE.UU.". No
  reemplazan a la riqueza global: son otra cosa.

#### D0.10.8 Balances de bancos centrales

- **Propuesta.** Cada balance en su moneda y con su convención nativa. La suma
  en USD, si se quiere, es una serie derivada con las mismas reglas del
  agregado de M2.
- **El balance de la Fed antes de 2013-12.** El XML de la Junta y FRED
  `WALCL` no coinciden en 517 semanas, y el BIS coincide con FRED (D0.7.1,
  D0.7.5). Propuesta: publicar desde el XML de la Junta, que es el dueño del
  dato, y que el control de consistencia contra el BIS marque esos meses como
  valor en disputa. Y preguntarle a la Junta cuál es la diferencia (D0.13).
- **No se publica la historia empalmada del BIS** (la Fed desde 1914, el BoJ
  desde 1953).

#### D0.10.9 De dónde se baja cada serie

- **Propuesta: del dueño del dato, sin FRED en el camino.** El ZIP de XML de
  cada publicación de la Junta (H.6, H.10, H.4.1), la API del BCE, la API del
  BoJ. FRED y el BIS quedan como contraste.
- Resuelve para D0 el punto 12 de la sección 12, que seguía abierto para S2.
  Cambiar la fuente de S2 sigue siendo un cambio de supuesto aparte.

#### D0.10.10 China

- **Con el PBoC como fuente, el M2 de China y el balance del PBoC quedan NO
  MEDIDO.** La fuente oficial existe y se puede leer, pero su aviso legal
  reserva los derechos y solo prevé la atribución para quien ya tiene permiso
  (D0.6.1), y su `robots.txt` veda los programas. Es lo que manda la regla
  fijada para este paso.
- **Alternativa, que es una decisión de alcance:** publicar China desde los
  organismos que la republican con términos abiertos. El M2 desde la OCDE,
  desde 2004-01; el balance desde el BIS, desde 2002-01. Iría como supuesto
  condicional, con cuatro cosas visibles en la ficha:
  1. La fuente es la OCDE (o el BIS), y el emisor original es el PBoC.
  2. La OCDE rotula la serie "M3", y no revisó 2017: el salto de definición le
     cae en 2018-01.
  3. Llega con uno o dos meses de rezago respecto del PBoC.
  4. No se estableció si los derechos que el PBoC reserva alcanzan a las
     cifras republicadas.
- En las dos variantes, **el pipeline no baja nada de pbc.gov.cn con un
  programa.** El PBoC queda como contraste leído a mano, como el FMI en
  A-R0-20.
- Si no se aprueba la alternativa: China va como tarjeta NO MEDIDO y el
  agregado es de tres economías.

#### D0.10.11 Lo que decidió el dueño (2026-10-05 y 2026-10-06)

Aprobó el paso 0 con estas decisiones, que mandan sobre las propuestas de
arriba donde difieren:

1. **China:** publicar vía OCDE (dinero amplio, con el rótulo exacto de la
   fuente, "M3", nunca como M2) y BIS (balance). Entra al agregado solo si el
   paso 1 demuestra que su definición es comparable; si no, se muestra aparte.
   Cero descargas desde el sitio del PBoC. *El paso 1 no lo demostró: lo leído
   dice lo contrario (A-D0-9). China se muestra aparte y el agregado es de
   tres economías.*
2. **EE.UU. antes de 1959:** tres tramos de la Junta, sin empalmar y con
   quiebres visibles. Transcripción doble e independiente, página de origen
   por cifra, control de sumas; las discrepancias se listan y se resuelven
   releyendo la imagen. El NBER no se usa por ahora. *El 2026-10-06 lo dejó
   fuera de esta entrega: NO MEDIDO, se hace en un PR propio.*
3. **Eurozona:** desde 1980, tramo hasta 1997-08 con estado "estimación".
4. **Savills, WGC y similares:** solo como cifra puntual citada (año, fuente,
   página), fuera del pipeline y de cualquier cálculo, con estado "estimación
   de terceros" (A-D0-28). McKinsey, excluido.
5. **Convención nativa por serie,** declarada en su ficha. Oro / M2 EE.UU. y
   BTC / M2 EE.UU. aprobados; contra el agregado, no.
6. **Balance de la Fed:** fuente principal el XML de la Junta; FRED como
   control de consistencia; explicar la diferencia de las 517 semanas antes
   de publicar. *Explicada: D0.15 y A-D0-15.*
7. **`CLAUDE.md`:** la regla de leer `robots.txt` y términos antes de
   cualquier pedido automatizado. *Hecha, en su propio commit.*
8. **BCE (2026-10-06):** no cambiar el User-Agent. Copias bajadas a mano una
   vez al mes; el pipeline verifica el hash y, si falta o no coincide, la
   serie queda NO MEDIDO en esa corrida. Consulta al BCE redactada, sin
   enviar (D0.13).
9. **Balance del PBoC (2026-10-06):** NO MEDIDO ("sin validación externa") en
   esta entrega.
10. **Riqueza (2026-10-06):** bonos, acciones y BTC entran si alcanzan con
    calidad; si no, NO MEDIDO con motivo. *Quedaron NO MEDIDO: pendientes de
    implementar.*

### D0.11 Validación propuesta

Con la regla de `CLAUDE.md`: una segunda fuente por serie y una tolerancia
escrita antes de ver el resultado.

**Una advertencia sobre esa regla.** El paso 0 pide contrastar una muestra de
cada serie, así que varios resultados ya están a la vista (están en las
fichas de arriba). Para que la tolerancia no salga de lo observado, la
propuesta es fijarla **por construcción**: la precisión con que cada fuente
publica el dato. Donde eso no alcanza, se dice.

**Otra, de fondo.** Un agregado monetario o un balance tiene un solo
compilador: el banco central. No existe una segunda medición. Lo que sí se
puede validar es que el dato publicado sea el del emisor, sin errores de
transporte, de unidad ni de fecha. Los gates de esta fase validan eso, y así
lo tiene que decir la ficha de cada serie.

| Serie | Fuente | Segunda fuente | Clase | Tolerancia propuesta |
| --- | --- | --- | --- | --- |
| M2 de EE.UU. | XML del H.6 | Tabla 1 de la publicación en HTML (17 meses) | Gate | Igualdad a un decimal (0.1 miles de millones) |
| | | FRED `M2SL` y `M2NS`, toda la historia | Control | Igualdad |
| M2 de la Eurozona | API del BCE | Anexo del comunicado mensual, último mes | Gate | ±0.5 miles de millones de EUR (el anexo redondea a la unidad) |
| | | Banco de España, últimos tres meses | Control | Igualdad |
| M2 de Japón | API del BoJ | Comunicado mensual en PDF, dos últimos meses | Gate | ±0.05 billones de yenes (el PDF publica un decimal) |
| | | e-Stat Dashboard, toda la historia | Control | Igualdad |
| M2 de China (si se aprueba) | API de la OCDE | Tabla del PBoC, leída a mano | Control manual | Igualdad al millón de yuanes. Sin lectura, el mes sale "sin comparar" |
| Balance del PBoC (si se aprueba) | BIS `WS_CBTA` | Tabla del PBoC, leída a mano | Control manual | Igualdad a 0.1 miles de millones de yuanes |
| Balance de la Fed | XML del H.4.1 | BIS `WS_CBTA`, último miércoles del mes | Control | Igualdad a 0.01 miles de millones. **Ya se sabe que no cierra en 118 meses** (D0.10.8) |
| | | Tabla de la publicación H.4.1 en HTML, última semana | Gate | Igualdad en millones |
| Balance del Eurosistema | API del BCE | Estado semanal en HTML, última semana | Gate | ±0.01 %: se observó una revisión de 0.003 % (D0.7.2) |
| | | BIS `WS_CBTA`, con su regla de semana | Control | Igualdad a 0.001 miles de millones |
| Balance del BoJ | API del BoJ | Balance de fin de mes en HTML | Gate | Igualdad al truncar a 100 millones de yenes; ±0.01 % en marzo y septiembre, que salen preliminares |
| | | BIS `WS_CBTA` | Control | Igualdad |
| USD por EUR | XML del H.10 | BCE, promedio mensual | Control | ±0.5 % en el promedio mensual. **Fijada con el resultado a la vista:** la diferencia máxima observada es 0.31 % |
| JPY y CNY por USD | XML del H.10 | FRED, mismo emisor | Control | Igualdad |
| Efectivo y depósitos, 1947–1958 | Transcripción de la Tabla 1.1 | NBER `m14144c` | Gate de transcripción | ±0.1 miles de millones: es la diferencia de redondeo que la documentación del NBER declara |
| Efectivo y depósitos, fechas de balance | Transcripción de la Tabla 9 | La suma de cada fila contra su total impreso | Gate de transcripción | Igualdad |
| | | NBER `m14144a`, mismo mes | Control | Por declarar en el paso 1. **Ya se vieron cuatro fechas:** −1.4 %, −0.4 %, −0.2 % y +1.7 % |
| Oro / M2 y BTC / M2 | — | Heredan los gates del oro, de BTC y del M2 | — | — |

- **Sin segunda fuente independiente:** JPY y CNY por USD. Las series de FRED
  son el mismo dato de la Junta. Un contraste independiente exigiría leer el
  tipo de cambio del BoJ y el del PBoC, que no se leyeron.
- **Revisiones.** El M2 de la Eurozona y el de Japón se revisan hacia atrás
  (0.14 % y 0.1 % en el valor de 2020-03). Cada corrida guarda su descarga con
  SHA-256, y un cambio en un mes ya publicado se reporta como revisión, como
  hace S2 (A-S2-6). El umbral de qué cuenta como revisión es un supuesto por
  declarar.

### D0.12 Supuestos A-D0-\*

Están en `SUPUESTOS.md`, A-D0-1 a A-D0-29, escritos el 2026-10-06 con las
decisiones de D0.10.11. El índice de abajo es el propuesto en el paso 0; los
números coinciden hasta el A-D0-26, y se agregaron A-D0-27 (crudos de D0),
A-D0-28 (cifras puntuales de terceros) y A-D0-29 (`robots.txt` y copias a
mano). A-D0-9, A-D0-15, A-D0-19, A-D0-20 y A-D0-24 cambiaron de contenido con
D0.10.11: vale lo que dice `SUPUESTOS.md`.

| N.º | Qué fija | Estado propuesto |
| --- | --- | --- |
| A-D0-1 | Cada serie se publica en su moneda, su unidad y su convención nativas; la convención va en la ficha | supuesto |
| A-D0-2 | El M2 de EE.UU. es un promedio mensual de cifras diarias; no existe a fin de mes | dato |
| A-D0-3 | La titular del M2 de EE.UU. es la ajustada (`M2.M`); el agregado usa las series sin ajustar | supuesto |
| A-D0-4 | El M2 de la Eurozona es de composición cambiante: cada ampliación es un salto de nivel declarado, no corregido | dato el salto; supuesto no corregirlo |
| A-D0-5 | El M2 de la Eurozona de 1980-01 a 1997-08 es una estimación del BCE | estimación |
| A-D0-6 | El M2 de Japón empieza en 2003-04; M2+CDs es otra serie y no se empalma | dato; supuesto no empalmar |
| A-D0-7 | BCE: el dato se publica tal cual y con fuente; toda derivada se rotula como cálculo propio | supuesto de licencia |
| A-D0-8 | BoJ: uso bajo la cláusula no comercial, con aviso y crédito por la API | supuesto condicional |
| A-D0-9 | China, con el PBoC como fuente: NO MEDIDO. Alternativa: M2 desde la OCDE y balance desde el BIS, con el PBoC como contraste a mano | no medido; supuesto condicional la alternativa |
| A-D0-10 | El agregado en USD es una serie derivada; tipo de cambio del H.10, promedio o fin de mes según la convención de cada serie | supuesto |
| A-D0-11 | El agregado a tipo de cambio constante usa el del primer mes común | supuesto |
| A-D0-12 | El agregado mezcla promedios y saldos de fin de mes; no se publican ratios contra él | dato la mezcla; supuesto la regla |
| A-D0-13 | El Índice Denominador 60/40 se elimina | supuesto |
| A-D0-14 | De semanal a mensual: último dato semanal fechado dentro del mes, con fecha de origen visible | supuesto |
| A-D0-15 | El balance de la Fed sale del XML de la Junta; los meses que no coinciden con el BIS quedan en disputa | supuesto la regla; dato la diferencia |
| A-D0-16 | Los balances del Eurosistema y del BoJ llevan sus quiebres declarados (ampliaciones, revalorización trimestral, cambio contable de 2001-04), sin corregir | dato; supuesto no corregir |
| A-D0-17 | EE.UU. antes de 1959: tres tramos de la Junta, sin empalmar; ninguno se llama M2 | supuesto |
| A-D0-18 | Las fechas de balance de 1892 a 1946 son datos estimados en parte por la Junta | dato, con esa reserva |
| A-D0-19 | Las tablas de la Junta anteriores a 1959 se transcriben a mano; gate de transcripción contra la suma de cada fila y contra el NBER | supuesto |
| A-D0-20 | La serie mensual del NBER (1907–1946) es una estimación y no se publica sin permiso | estimación; supuesto condicional |
| A-D0-21 | Oro / M2 y BTC / M2 usan el M2 ajustado de EE.UU.; unidad: USD por cada billón de USD de M2 | supuesto |
| A-D0-22 | Bonos: suma de las economías que declaran al BIS, panel fijo desde 2020-Q4, valuación mixta | dato cada economía; supuesto la suma |
| A-D0-23 | Acciones: el agregado `WLD` del Banco Mundial es la suma de los países con dato | dato, con la subcobertura declarada |
| A-D0-24 | Inmuebles, cantidad de oro y riqueza total: NO MEDIDO | no medido |
| A-D0-25 | Las tolerancias de los gates se fijan por la precisión publicada; las que se fijaron con el resultado a la vista lo declaran | supuesto |
| A-D0-26 | Un cambio en un mes ya publicado es una revisión y se reporta; umbral por declarar | supuesto |

### D0.13 Permisos, avisos y preguntas

Ninguno se envió.

1. **Banco de Japón: aviso por usar la API.** Sus instrucciones piden avisar
   por correo cuando se publica un servicio que la usa, y mostrar un crédito
   con un texto fijo. Va antes de publicar la serie de Japón. Y una pregunta:
   si un sitio de investigación sin ingresos cae fuera de "fines comerciales",
   y si publicar series derivadas cuenta como alterar el contenido.
2. **NBER: permiso para publicar las series 14144 de la Macrohistory
   Database.** La página de la base da `data@nber.org` para reportar errores;
   la de los libros tiene un formulario de permisos. Destraba la alternativa
   mensual de D0.10.6.
3. **Junta de la Reserva Federal: una pregunta.** Por qué el total de activos
   del XML del H.4.1 (`RESPPA_N.WW`) difiere de `WALCL` antes de 2013-12-11.
4. **BCE: una pregunta.** Si los valores de M2 de 1980 a 1997 que entrega hoy
   la API son las estimaciones descritas en el Boletín de febrero de 1999, y
   cómo concilia su política de reutilización, que pide no modificar las
   estadísticas, con las series derivadas.
5. **BCE: consulta sobre el cliente de la API.** Borrador, sin enviar:

   > Asunto: ECB Data Portal API, robots.txt y clientes identificados.
   >
   > Mantenemos un repositorio público de investigación (danioni/losratios)
   > que publica series del ECB Data Portal con la cita "Source: ECB
   > statistics", bajo la política de reutilización del SEBC. La ayuda de la
   > API ("Useful tips") da ejemplos con Python requests, curl y wget contra
   > data-api.ecb.europa.eu. El robots.txt del mismo host lista a
   > python-requests, curl y wget con "Disallow: /", y admite a cualquier
   > otro agente. Por respeto a ese archivo hoy bajamos los tres archivos a
   > mano, una vez al mes. ¿Acepta el BCE un cliente automatizado que se
   > identifique con un User-Agent propio del proyecto y un contacto, con un
   > pedido mensual por serie? Series: BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E,
   > BSI.M.U2.N.V.M20.X.1.U2.2300.Z01.E e ILM.W.U2.C.T000000.Z5.Z01. Y una
   > segunda pregunta: ¿los valores de M2 anteriores a septiembre de 1997 que
   > entrega hoy la API siguen siendo las estimaciones descritas en el
   > Boletín Mensual de febrero de 1999?

   Destraba la descarga automática del BCE. Mientras tanto rige A-D0-29.
6. **PBoC: permiso de reutilización.** Su aviso legal lo prevé para medios y
   sitios autorizados. Destraba usar al emisor como fuente. No se leyó a quién
   se le pide.

### D0.14 Lo que sigue abierto

1. **Las decisiones de D0.10.** Ninguna está tomada.
2. **Los avisos y preguntas de D0.13.** Ninguno se envió.
3. **El retiro del programa de descarga de la Junta.** Los ZIP de XML siguen
   en las páginas de cada publicación, pero la Junta anuncia más cambios para
   2027. Si los retira, la vía que queda es la API de FRED, que pide clave.
4. **La API del BoJ puede cambiar sin aviso** (lo dicen sus instrucciones), y
   la del BCE falla de a ratos. El pipeline necesita reintentos con espera.
5. **Las series se revisan.** M2 de la Eurozona y de Japón, hacia atrás y sin
   versiones anteriores en la API. Solo se conserva lo que cada corrida
   guarde.
6. **El XML del H.4.1 contra `WALCL`:** explicado el 2026-10-06 (D0.15,
   A-D0-15). Cerrado.
7. **Las tablas de la Junta anteriores a 1959 solo se leyeron por muestra.**
   Cuatro fechas de la Tabla 9 y de su continuación, y dos meses de la
   Tabla 1.1. La transcripción
   completa es trabajo del paso 1.
8. **No leído, EE.UU.:** el apéndice A de Friedman y Schwartz (1963); la
   historia de las redefiniciones del M2 antes de 2020; los promedios
   semanales del H.4.1.
9. **No leído, Eurozona:** un documento vigente sobre cómo están hechos los
   valores de 1980 a 1997; la causa de las reclasificaciones grandes fuera de
   las ampliaciones; la política de revisiones del estado semanal.
10. **No leído, Japón:** una definición literal del "promedio" del M2; qué
    entiende el BoJ por "fines comerciales"; los términos de la OCDE desde un
    programa.
11. **No leído, China:** las tablas del PBoC de 2005, 2007–2010, 2012–2014,
    2016 y 2019; a quién se le pide el permiso; la serie completa de la OCDE
    contra el PBoC (se compararon 25 fechas).
12. **Sin contraste independiente:** los tipos de cambio del yen y del yuan.
13. **Riqueza:** la World Inequality Database no se pudo leer; la serie del
    World Gold Council y el portal de la WFE piden cuenta; la diferencia entre
    el Z.1 y la OCDE para los inmuebles de EE.UU. quedó sin reconciliar.
14. **Lecturas hechas con navegador** porque el sitio rechaza a un programa:
    términos de la OCDE, de Savills y de McKinsey, y las páginas de la Oficina
    Nacional de Estadísticas de China. De esas hay transcripción, no la
    respuesta HTTP.
15. **Los pedidos al PBoC.** Se hicieron unos 70 con un programa antes de leer
    su `robots.txt`, que los veda. No se repite: el PBoC queda como lectura a
    mano.
16. **Los pedidos al BCE.** Unos 30 con `python-requests` en el paso 0, antes
    de leer el `robots.txt` de su API, que veda a ese cliente (D0.15). No se
    repiten: las series del BCE entran por copia a mano (A-D0-29), y la
    consulta al BCE está redactada en D0.13.
17. **El aviso al Banco de Japón** por el uso de su API, antes de desplegar el
    sitio con esas series (A-D0-8).

### D0.15 Lo que encontró el paso 1 (2026-10-06)

El paso 1 escribió `denominador.py` y corrió el pipeline una vez con los crudos
leídos el 2026-10-05. Lo que cambió respecto de las fichas de arriba:

**Los `robots.txt` de los trece hosts.** Leídos el 2026-10-05 antes de escribir
una línea de descarga, por la regla nueva de `CLAUDE.md`:

| Host | Qué dice sobre un programa |
| --- | --- |
| www.federalreserve.gov, www.stat-search.boj.or.jp, www.boj.or.jp, sdmx.oecd.org, dashboard.e-stat.go.jp, api.worldbank.org, community-api.coinmetrics.io | Sin `robots.txt` (HTTP 404): sin reglas. |
| stats.bis.org | Devuelve una página HTML en lugar del archivo: sin reglas. |
| data.bis.org, www.bde.es, www.ecb.europa.eu | `User-agent: *` con exclusiones de buscador y descargas; las rutas usadas están permitidas. www.ecb.europa.eu pide 5 segundos entre pedidos. |
| fred.stlouisfed.org | `User-agent: *` permitido con 1 segundo de pausa; a GPTBot, ChatGPT-User y Google-Extended les pone una pausa de 30 días. |
| **data-api.ecb.europa.eu** | **Veda con `Disallow: /` a `python-requests`, `curl`, `Wget`, `Scrapy` y otros clientes genéricos, y a los agentes de Anthropic (`ClaudeBot`, `Claude-Web`, `anthropic-ai`), OpenAI y Common Crawl. Admite a `User-agent: *` salvo rutas de administración.** La ayuda de la misma API ("Useful tips") da ejemplos con `requests`, `curl` y `wget`. Los dos textos se contradicen. |
| www.pbc.gov.cn | Veda a todo agente salvo Baiduspider (D0.6.1). |

**Consecuencias.** En el paso 0, el agente que leyó la Eurozona hizo unos 30
pedidos a `data-api.ecb.europa.eu` con `python-requests`, sin haber leído ese
`robots.txt`; las copias de ese día son las que usa la primera corrida. Desde
entonces no se le pidió nada más al BCE. Decisión del dueño del 2026-10-06:
**el pipeline no cambia su User-Agent; las tres series del BCE entran por copia
bajada a mano** (A-D0-29, README). La consulta al BCE está en D0.13.

**El balance de la Fed: no eran revisiones, era definición (A-D0-15).** El XML
del H.4.1 trae el total bruto de los doce bancos (`RESPPA_N.WW`) y el total
consolidado (`RESPPMA_N.WW`, "less eliminations from consolidation"). La
diferencia es exactamente la serie de eliminaciones de partidas en proceso de
cobro (`RESPPMAX_N.WW`) en las 1.242 semanas, con ±1 millón de redondeo; vale
cero desde noviembre de 2012. El consolidado coincide con `WALCL` de FRED en
las 1.242 semanas. **D0 publica el consolidado.** La ficha D0.7.1 nombra la
serie bruta: queda corregida en `serie_D0.csv`.

**Una segunda fuente independiente para los tipos de cambio.** El BIS publica
tipos de cambio contra el USD (`WS_XRU`), promedio del mes y fin de mes, para
el yen (desde 1957-01), el yuan (1957-01) y el euro (1974-06). Leído el
2026-10-05; las tres descargas están en el manifiesto. Es el control de los
tres tipos de cambio (A-D0-25).

**Resultado de la primera corrida (crudos del 2026-10-05), antes de la
revisión del PR:** 12 de 13 series publicadas; después de la revisión, 11
(China pasa a NO MEDIDO, abajo). Todos los gates cerraron: M2 de EE.UU. contra la Tabla 1 en HTML
(17 meses, diferencia 0); balance de la Fed contra el BIS (284 meses, 0) y
contra FRED (1.242 semanas, todas iguales); M2 de la Eurozona contra el Banco
de España (3 meses, 0 y 0.49 millones); balance del Eurosistema contra el BIS
(332 meses, 0); M2 de Japón contra e-Stat (281 meses, 0); balance del BoJ
contra el BIS (340 meses, 0); dinero amplio de China contra dos lecturas de la
NBS (41 millones de diferencia, con 50 de tolerancia). El control de los tipos
de cambio deja **un mes en disputa: 2008-12 del USD por EUR, 0.68 %** contra el
BIS; el yen llega a 0.49 % y el yuan a 0.17 %. El agregado va de 2003-04 a
2026-08, 281 meses. Oro / M2 va de 1960-01 a 2026-08 (800 meses, apto desde
1968-04) y BTC / M2 de 2013-01 a 2026-08 (164 meses).

**Lo que la revisión del PR encontró (2026-10-06).**

- `denominador_pares.csv` y `denominador_ratios.csv` estaban publicados con
  datos de prueba: `ratios.py` escribía esos archivos en `data/series/`
  aunque los tests redirigieran las demás salidas, y la suite los pisó después
  de la corrida real. Se regeneraron desde un estado limpio; las salidas de D0
  de `ratios.py` siguen ahora al directorio de los ratios; un fixture hace
  fallar a cualquier test que escriba en `data/`; y
  `tests/test_salidas_publicadas.py` recalcula cada salida derivada desde los
  archivos del repositorio y exige igualdad byte a byte (A-D0-30).
- `MINIMO_ANCLAS = 2` se había fijado después de ver que China tenía dos
  lecturas. Pasó a tres, y el dinero amplio de China queda **NO MEDIDO hasta
  una tercera lectura en pantalla** (A-D0-25).

**Lo que quedó NO MEDIDO en esta entrega, y por qué.**

- Dinero amplio de China: dos anclas, y hacen falta tres (A-D0-25).
- Balance del PBoC: sin validación externa. Las únicas lecturas de su tabla
  salieron de descargas automáticas de su sitio (paso 0), descartadas por la
  regla de `robots.txt`. Dos valores leídos a mano por una persona lo
  destraban (`ANCLAS_BALANCE_PBOC` en `configuracion.py`).
- EE.UU. antes de 1959, los dos tramos: la transcripción con doble lectura
  (A-D0-19) se hace en un PR propio.
- Riqueza por clase: bonos, acciones y BTC quedan pendientes de implementar;
  inmuebles, cantidad de oro y total no tienen serie (A-D0-22 a A-D0-24). Las
  cifras de Savills y del World Gold Council van en
  `data/series/citas_terceros.csv` como "estimación de terceros" (A-D0-28).
