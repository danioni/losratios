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

### 4.8 El precio oficial del oro antes de 1960 — paso 0 (2026-10-07)

**Lo que se pidió.** Verificar, leyendo fuentes primarias de dominio público,
el precio oficial del oro en USD por onza troy y sus fechas de vigencia desde
el régimen de 20,67 hasta 1960, donde empieza el Pink Sheet (4.5); evaluar si
existe un precio de mercado citable para algún tramo; y detenerse con la
propuesta. Nada está implementado. Cada pedido (48, con hora UTC, URL, código
HTTP, bytes y SHA-256) quedó en un registro fuera del repositorio, como los del
paso 0 de D0. Ningún número de esta sección viene de memoria: cada uno tiene
página.

**Qué se leyó.** `robots.txt` antes de cada host: FRASER, `Crawl-delay: 10` y
sin vedas (se respetaron 12 s entre pedidos); `www.govinfo.gov`, veda la
búsqueda y permite `/content/pkg/`; `www.nber.org`, veda `/search/`;
`www.loc.gov`, permitía las rutas pero **respondió 403 con un desafío de
Cloudflare** a todos los pedidos y pide una verificación humana en el
navegador, que no se completó; `www.bankofengland.co.uk`, **403 al propio
`robots.txt`**: no se le pidió nada más; `www.presidency.ucsb.edu` veda
explícitamente a `ClaudeBot`: nada. Documentos leídos en FRASER: once números
del *Federal Reserve Bulletin* (marzo a julio, noviembre y diciembre de 1933;
enero a marzo de 1934; enero de 1947), el *Annual Report of the Secretary of
the Treasury* de 1900 y de 1934, el *Annual Report of the Director of the
Mint* de los ejercicios 1934 y 1935, y la sección 14 ("Gold") de los dos
volúmenes de *Banking and Monetary Statistics* (D0.3.1). En govinfo: 86 Stat.
116–118 y 87 Stat. 352. **Licencias:** las leyes, proclamaciones y órdenes
ejecutivas son dominio público; los Boletines y los informes del Tesoro y de
la Casa de Moneda son publicaciones federales sin aviso de copyright (se
buscó en las páginas citadas), y que estén en dominio público es la misma
inferencia que D0.3.1 hace para *Banking and Monetary Statistics*; FRASER
pide atribución y no responde por los derechos de cada documento
(`https://fraser.stlouisfed.org/terms-of-use`).

**Los tramos del precio oficial** (480 granos por onza troy; "9/10 de fino"
= 90 % de oro puro):

| Vigencia | USD por onza troy de oro fino | Norma y cita literal | Dónde se leyó |
| --- | --- | --- | --- |
| Desde el 14 de marzo de 1900 (la paridad venía de antes: abajo) hasta el 31 de enero de 1934 a las 15:10, hora del Este | **20,671835** = 480 ÷ 23,22 = 8000/387 (20,6718346…). "20,67" es el redondeo al centavo; la Casa de Moneda publica "$20.6718" | Gold Standard Act, 14 de marzo de 1900, sección 1: *"That the dollar consisting of twenty-five and eight-tenths grains of gold nine-tenths fine, as established by section thirty-five hundred and eleven of the Revised Statutes of the United States, shall be the standard unit of value, and all forms of money issued or coined by the United States shall be maintained at a parity of value with this standard"* | *Annual Report of the Secretary of the Treasury* 1900, p. 345 (`https://fraser.stlouisfed.org/files/docs/publications/treasar/AR_TREASURY_1900.pdf`). La cita "31 Stat. 45" solo se vio citada por la proclamación de 1934: el volumen no se pudo abrir (loc.gov) |
| Desde el 31 de enero de 1934 a las 15:10 (hora del Este), sin cambios hasta el 8 de mayo de 1972 | **35,00 exactos**: 15 5/21 = 320/21 granos × 9/10 = 96/7 granos de oro fino; 480 ÷ (96/7) = 35 | Proclamación presidencial del 31 de enero de 1934, bajo la sección 43(b)(2) del Título III de la ley del 12 de mayo de 1933, reformada por la sección 12 de la Gold Reserve Act del 30 de enero de 1934: *"do hereby proclaim, order, direct, declare, and fix the weight of the gold dollar to be 15 5/21 grains nine tenths fine, from and after the date and hour of this proclamation. ... Done in the City of Washington at 3:10 o'clock in the afternoon, eastern standard time, this 31st day of January, in the year of our Lord one thousand nine hundred and thirty-four"* | *Federal Reserve Bulletin*, febrero de 1934, pp. 68–69 (`https://fraser.stlouisfed.org/files/docs/publications/FRB/1930s/frb_021934.pdf`); la fracción se comprobó en la imagen. El Tesoro: *"At this weight, the statutory value of gold is $35 per fine ounce"* (informe de 1934, p. 204). El número "2072" y la cita "48 Stat. 1730" no aparecen en lo leído: no verificados |

Comprobaciones, cada una contra la página que se nombra: (320/21) ÷ 25,8 =
0,590624, los *"59.06 plus percent"* de la declaración presidencial (Boletín,
feb. 1934, p. 67) y la devaluación de 40,94 % de BMS 1914–41, p. 522; 35 ÷
20,671835 = 1,693125, el *"69.31 per cent"* de BMS 1914–41, p. 526; 31,1034768
÷ 35 = 0,888671 gramos de oro fino por dólar, la paridad que EE.UU. declaró
al FMI el 18 de diciembre de 1946 (*"0.888671 ... 35.0000"*, Boletín, enero de
1947, p. 12); la Casa de Moneda imprime "$20.6718" y "$35.0000" (informe del
ejercicio 1935, p. 91). **Entre 1934 y 1960 no hubo ningún cambio**: BMS
1914–41 valúa a 35 *"thereafter"* hasta 1941; BMS 1941–70 dice que EE.UU.
compró y vendió *"at the established rate of $35 per fine troy ounce in effect
throughout the period"* (p. 897, con su nota 8: 38 el 8 de mayo de 1972 por
la Public Law 92-268 y 42,22 el 18 de octubre de 1973 por la Public Law
93-110, las dos leídas en govinfo: 86 Stat. 116, sección 2, *"$1 equals one
thirty-eighth of a fine troy ounce of gold"*; 87 Stat. 352, sección 1,
*"forty-two and two-ninths dollars per fine troy ounce of gold"*).

**La base anterior a 1900: NO MEDIDO.** La ley de 1900 remite a la sección
3511 de los *Revised Statutes* (1874), que codifica las leyes de 1834, 1837 y
1873. Están en los volúmenes 4, 5, 17 y 18 de los *Statutes at Large*, en
loc.gov, que no se dejó leer. Con lo leído, el tramo de 20,67 solo se sostiene
desde el 14 de marzo de 1900; extenderlo (por ejemplo a 1892-06, para alinear
con A-D0-17) exige leer esas leyes a mano u otra reimpresión oficial.

**El tránsito de 1933**, con lo verificado (reimpresiones oficiales en el
Boletín y en el informe del Tesoro de 1934):

- 9 de marzo, Emergency Banking Act: faculta a regular el oro y a exigir su
  entrega contra *"an equivalent amount of any other form of coin or
  currency"* (Boletín, marzo de 1933, p. 115). **No fija ningún precio.**
- 5 de abril, orden ejecutiva contra el atesoramiento (el número 6102 no está
  impreso en la fuente leída): entrega obligatoria antes del 1 de mayo
  (Boletín, abril de 1933, pp. 213–214). **No fija ningún precio.**
- 12 de mayo, Agricultural Adjustment Act, Título III, sección 43(b)(2):
  *"By proclamation to fix the weight of the gold dollar in grains nine tenths
  fine ... but in no event shall the weight of the gold dollar be fixed so as
  to reduce its present weight by more than 50 per centum"* (Boletín, mayo de
  1933, pp. 317–318). **Autoriza; no cambia nada por sí misma.**
- 5 de junio, Joint Resolution: anula las cláusulas oro (Boletín, junio de
  1933, p. 338). **No toca la paridad.**
- Del 8 de septiembre de 1933 al 31 de enero de 1934, **precio administrado
  del oro recién extraído**, diario, de 29,00 a 34,45: venta a la industria
  (8 de septiembre a 24 de octubre), compras de la RFC (25 de octubre a 15 de
  enero: *"ranging from $31.36 to $34.06"*) y compras del Banco de la Reserva
  Federal de Nueva York a 34,45 (16 a 31 de enero). La tabla diaria completa
  está en el informe del Tesoro de 1934, anexo 26, p. 205 (comprobada en la
  imagen) y en los Boletines de diciembre de 1933 (p. 779), enero (p. 51) y
  febrero de 1934 (p. 133); entre el anexo y las tablas del Boletín hay dos
  discrepancias menores (7 de noviembre y 23 de diciembre de 1933).
- 30 de enero de 1934, Gold Reserve Act: secciones 8 y 9 (el Secretario compra
  y vende oro *"at such rates and upon such terms and conditions as he may deem
  most advantageous"*), 12 (techo del 60 %) y 15 (mientras no se proclame otro
  peso, el dólar son 25,8 granos) (Boletín, febrero de 1934, pp. 65–67). La
  cita "48 Stat. 337" no se pudo abrir.
- 31 de enero y 1 de febrero de 1934, el Tesoro compra *"at the rate of $35 per
  fine troy ounce, less the usual mint charges and less one quarter of 1
  percent for handling charges"* y vende a bancos centrales extranjeros *"at
  $35 per fine ounce plus one quarter percent handling charge"* (Boletín,
  febrero de 1934, pp. 67–69; informe del Tesoro de 1934, pp. 201 y 204–205):
  34,9125 y 35,0875, cálculo propio.

**Respuesta a la pregunta concreta:** entre marzo de 1933 y el 31 de enero
de 1934 la paridad legal siguió siendo la de 25,8 granos, aunque el Tesoro no
vendiera oro a ese precio ni pagara en oro. Lo dice el Tesoro: *"The rate for
gold other than newly mined gold was not changed by the orders of August 29 or
October 25, or the act of the Reconstruction Finance Corporation; but
remained at $20.67 an ounce"* (informe de 1934, p. 204, punto 15); las casas
de moneda compraron en el ejercicio 1934 *"at $20.67+ per fine ounce"*
20.114.858,02 USD y *"at $35 per fine ounce"* 800.047.115,02 USD (p. 120); y la
Junta valúa *"at the rate of $20.67 per fine ounce of gold through January
1934 and $35 per fine ounce thereafter"* (BMS 1914–41, p. 522). Lo que cambió
fue la convertibilidad: sin pagos en oro desde el 6 de marzo de 1933, con
licencia para exportar desde el 10 de marzo y tenencia privada prohibida
desde el 5 de abril.

**Precio de mercado: no hay serie mensual en USD abierta y publicable antes
de 1960** entre lo leído. Los dos volúmenes de BMS no traen ninguna tabla de
precio del oro (índice y búsqueda de texto). Candidatos:

| Candidato | Fuente | Qué es | Veredicto |
| --- | --- | --- | --- |
| Precio del oro en Londres, promedio anual, 1870–1934 | *Annual Report of the Director of the Mint*, ejercicio 1935, pp. 90–91 (la misma tabla en el de 1934, p. 93); dominio público por la misma inferencia | En libras, chelines y peniques por onza *standard* hasta 1918 y por onza fina desde 1919; el "equivalente en USD" está convertido a la paridad legal, no al cambio de mercado (nota 2, literal: *"Conversions on basis of legal monetary parity; exchange not a factor"*). Leídos: 1931: £4 12s 6,23d; 1932: £5 18s 0,82d; 1933: £6 4s 10,4d; 1934: £6 17s 7,85d; equivalentes 22,5126; 28,7293; 30,3836; 33,4952 (paridad vieja) y 56,7114 (nueva) | Publicable, pero anual, en esterlinas, y su valor en USD de mercado sería un cálculo propio con el tipo de cambio del año (A-D0-7). Sirve, como mucho, de control anual de 1931 a 1939 |
| Precio administrado diario, 1933-09-08 a 1934-01-31 | Informe del Tesoro de 1934, anexo 26, p. 205; Boletines de diciembre de 1933 a febrero de 1934 | Tres regímenes administrados en una tabla, no un mercado | Citable como serie aparte con su etiqueta; con la regla de meses completos solo quedarían noviembre y diciembre de 1933 y enero de 1934 |
| NBER Macrohistory Database, capítulos IV y XIV | Listados leídos | Sin serie de precio del oro; sin licencia (A-D0-20) | Descartado |
| Banco de Inglaterra, "A millennium of macroeconomic data" | No leído: el host responde 403 al propio `robots.txt` | Un resumen de terceros habla de Open Government Licence v3.0: no verificado | **NO MEDIDO**; lectura a mano si el dueño quiere evaluarlo |
| LBMA, World Gold Council, FRED | 4.1 a 4.3 | — | Ya descartados |

**Propuesta, para aprobar o rechazar.**

1. Serie `oro_precio_oficial_usd`, USD por onza troy de oro fino, estado
   **dato**, con la etiqueta visible "precio oficial fijado por ley, no precio
   de mercado" en cada fila y en el sitio. Dos tramos: 20,6718 hasta 1934-01
   y 35,00 desde 1934-02. Inicio en **1900-03** con lo verificado; más atrás
   solo después de leer las leyes de 1837 y 1873. Fin a decidir: 1959-12 (sin
   superponerse con el Pink Sheet) o 1973-10, con los tramos de 38 y 42,22,
   donde la superposición 1960–1971 con el Pink Sheet sería en sí misma un
   control (durante el London Gold Pool el mercado debería quedar a menos de
   1 % de 35; A-R0-17).
2. El mes en que cambia la norma lleva la convención publicada por la Junta
   (*"$20.67 ... through January 1934 and $35 ... thereafter"*, BMS 1914–41,
   p. 522): enero de 1934 = 20,6718; febrero de 1934 = 35,00. Sin promedios
   ponderados por días: serían valores que ninguna fuente publica.
3. Cuatro decimales, derivados en el código de la fracción legal (480 ÷
   (granos × fino)), como los publica la Casa de Moneda; error de redondeo
   0,00005. Una columna descriptiva de convertibilidad: "sí" hasta 1933-02;
   "no" desde 1933-03; desde 1934-02, "solo bancos centrales extranjeros y
   usos licenciados" (BMS 1941–70, p. 897).
4. **Fuera de `apto_metricas`**, siempre; no es lado de ningún ratio; sin
   empalme con el Pink Sheet y con el quiebre declarado en 1960-01: dos series
   en el gráfico, no una. El par oro oficial / dinero de EE.UU. según la Junta
   (las series `dinero_eeuu_1892_1946` y `dinero_eeuu_1947_1958` del PR #6) solo como par aparte, con los quiebres de las dos series a la
   vista y también fuera de las métricas.
5. Gate de nivel y de fecha, con tolerancia **±0,005 USD** y fecha de cambio
   exacta (1934-01-31), declarada el 2026-10-07 antes de comparar, contra
   publicaciones de instituciones distintas de la que da el texto legal:
   Tesoro (informe de 1934, p. 120), Casa de Moneda (ejercicio 1935, p. 91),
   Junta (BMS 1914–41, p. 522) y FMI vía el Boletín de enero de 1947, p. 12.
   Resultado, calculado después de declararla: 20,671835 difiere 0,0018 de
   "20.67" y 0,00003 de "20.6718"; 35 difiere 0 de "35.0000". Que esto baste
   como gate es decisión del dueño.
6. La serie saldría de un archivo pequeño escrito a mano con cita por fila
   (tramos: desde, hasta, granos, fino, norma, fuente, página), como las
   anclas del H.4.1 y las cifras del USGS; nada que bajar en la corrida. Los
   PDF leídos irían a `data/privado/` con URL, fecha y SHA-256.
7. Supuestos nuevos que haría falta escribir (prefijo a decidir; la serie es
   de la fase R por el oro, y su carácter de contexto histórico sin empalme se
   parece a A-D0-17): la serie es de contexto, fijada por ley; la convención
   del mes de cambio; los decimales; el inicio en 1900 mientras no se lean las
   leyes anteriores; el gate de nivel y fecha; y que de 1933-03 a 1934-01 rige
   la paridad legal sin convertibilidad, con el precio administrado como otra
   serie si alguna vez se publica.

**Decisión del dueño (2026-10-07) y lo implementado.** Aprobado desde el 14
de marzo de 1900 hasta 1959-12; antes de 1900, NO MEDIDO hasta verificar la
base legal; el precio administrado de 1933–34 se declara como tal en la
ficha y en las filas de esos meses; etiqueta visible "precio oficial fijado
por ley, no precio de mercado". `senales/oro_oficial.py` deriva el precio de
la fracción legal, expande los dos tramos a meses con la convención de la
Junta para enero de 1934, corre el gate de nivel y fecha (±0,005 USD contra
las cuatro cifras publicadas: cerró, diferencia máxima 0,0018) y escribe
`data/series/oro_precio_oficial.csv` y la ficha en `series.csv`, que
`ratios.py` conserva. Supuestos A-R0-21 a A-R0-26. El par oro oficial /
dinero de EE.UU. según la Junta no se implementó: queda para después del
merge del PR #6, como par aparte y fuera de las métricas.

**Lo que queda abierto.** La base anterior a 1900 y las citas de volumen de
los *Statutes at Large* (loc.gov exige una verificación humana; o buscar una
reimpresión oficial de las "coinage laws" en un informe de la Casa de Moneda
del siglo XIX); el Banco de Inglaterra; si alguna publicación federal trae una
tabla mensual del precio de Londres (no se revisaron los Boletines de 1935 a
1939 ni otros informes de la Casa de Moneda); el fin de la serie y la
convención del mes de cambio, que son decisiones del dueño; y cómo rotular
todo esto en el sitio.

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
| www.nber.org, data.nber.org | Leído: Macrohistory Database (capítulo 14) y el volumen de 1970 de Friedman y Schwartz. El libro de 1963 no está en línea. **El `robots.txt` de data.nber.org, leído el 2026-10-07, veda a todo programa (`User-agent: *`, `Disallow: /`): desde entonces no se le pide nada; su serie `m14144c` se lee en FRED (D0.3.6).** |
| www2.census.gov | Leído el 2026-10-07: *Historical Statistics of the United States*, capítulo X, ediciones de 1960 y 1975, en PDF. Su `robots.txt` no veda a `User-agent: *`. Solo como segunda publicación de la Tabla 9 (D0.3.6). |
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

#### D0.3.6 La transcripción y sus gates (2026-10-07)

Lo que D0.10.6 propuso y A-D0-17 aprobó se ejecutó en el PR del tramo
histórico. Las dos series del sitio se llaman `dinero_eeuu_1892_1946` y
`dinero_eeuu_1947_1958`, y ninguna se llama M2. Todo lo de esta sección se
hizo leyendo los escaneos; los dígitos no salen de memoria de nadie.

**Qué se transcribió.** Cuatro tablas, con su página en el libro y en el PDF
de FRASER:

| Tabla | Publicación | Página del libro | Página del PDF | Filas × columnas |
| --- | --- | --- | --- | --- |
| No. 9, "Deposits and currency—adjusted deposits of all banks and currency outside banks, 1892–1941" | *Banking and Monetary Statistics, 1914–1941* (1943) | 34–35 | 43–44 | 69 fechas de balance × 10 (690 celdas, 19 en blanco: el ahorro postal no existía antes de 1911) |
| Continuación de la Tabla 9 para 1941–46, tabla sin número de la introducción de la Sección 1 (nota 3) | *Banking and Monetary Statistics, 1941–1970* (1976) | 5 | 12 | 12 fechas × 8 (96 celdas); las dos filas de 1941 repiten la Tabla 9 |
| 1.1 A, "Money stock and related data, monthly, 1947–70", ajustada, tramo 1947–58 | *Banking and Monetary Statistics, 1941–1970* (1976) | 17 | 24 | 144 meses × 4 (576 celdas) |
| 1.1 B, la misma sin ajustar, tramo 1947–58 | *Banking and Monetary Statistics, 1941–1970* (1976) | 20 | 27 | 144 meses × 5 (720 celdas) |

Las notas al pie de las dos tablas están transcritas, literales, en
`data/raw/transcripcion_junta_1892_1958/notas_tabla_9.txt` y
`notas_tabla_1_1.txt`. La que define el tramo mensual, literal: *"Unless
otherwise noted, series represent averages of daily figures"*; efectivo
*"outside the Treasury, the Federal Reserve Banks, and the vaults of all
commercial banks"*; depósitos a la vista *"at all commercial banks other than
those due to domestic commercial banks and the U.S. Govt., less cash items in
the process of collection and Federal Reserve float, and (2) foreign demand
balances at Federal Reserve Banks"*; y "time deposits adjusted" lleva la nota
*"At all commercial banks"*.

**El protocolo (A-D0-19), tal como se ejecutó.**

- Dos juegos de recortes del mismo escaneo: A, a 300 ppp en color, en bloques
  de dos años (Tabla 1.1) o de unas veinte filas (Tabla 9); B, a 260 ppp en
  escala de grises, con otros cortes (tres años y bloques distintos). Cada
  recorte lleva pegado el encabezado de columnas.
- Seis lecturas independientes (tres tablas por juego), cada una sin acceso
  a la otra, con la consigna de transcribir lo impreso sin calcular ni
  corregir, y de marcar con `?` un dígito ilegible.
- Cotejo celda por celda: **2.082 celdas, 1 discrepancia.** En 1955-11 de la
  Tabla 1.1 B (depósitos a plazo ajustados) la lectura A dejó el último
  dígito como ilegible (`49.?`, mancha de tinta) y la B leyó 49.8. Se releyó
  la celda a 900 ppp: el glifo tiene dos lazos cerrados, como el 8 de las
  celdas vecinas, y no la cola abierta del 3. Quedó 49.8, con reserva, en
  `resoluciones.csv`. No afecta a ninguna serie publicada: la 1.1 B no se
  publica (abajo).
- Un defecto del recorte, no de la lectura: el corte de la Tabla 9 dejó
  afuera la fila 1933-12-30 en los dos juegos; se hizo un recorte nuevo y las
  dos lecturas la agregaron, iguales.
- La capa de texto OCR del PDF se usó solo para ubicar las páginas. En la
  página 20 (Tabla 1.1 B) el OCR es ilegible; en las otras, tiene los errores
  que ya decía D0.3.1.

**Control de sumas, con la tolerancia fijada antes (A-D0-32).**

- Tabla 9, cuatro identidades por fila (total de depósitos = vista + gobierno
  + plazo; plazo = comerciales + cajas + postal; total con efectivo = total de
  depósitos + efectivo; vista con efectivo = vista + efectivo), tolerancia
  cero: **cuadran las 69 filas.** Un blanco de ahorro postal cuenta como cero.
- Continuación, dos identidades (money stock = efectivo + vista; plazo =
  comerciales + cajas + postal), tolerancia cero: cuadran las 12 filas, y las
  dos de 1941 son iguales a las de la Tabla 9 en las ocho columnas.
- Tabla 1.1, money stock = efectivo + vista, tolerancia 0.1 (dos componentes
  redondeados a un decimal): cuadran **143 de 144** meses en A y 143 de 144
  en B. Los dos que no cuadran son erratas de la fuente, confirmadas por las
  dos lecturas y por el zoom: **1949-03, Tabla 1.1 A**, efectivo impreso 27.7
  entre meses de 25.7 (27.7 + 85.6 = 113.3 contra 111.2 impreso); **1950-12,
  Tabla 1.1 B**, total impreso 119.2 contra 25.4 + 93.4 = 118.8. Se publican
  tal como están impresos y marcados como valor en disputa (A-D0-33).

**Segunda publicación de las fechas de balance: el Censo.** *Historical
Statistics of the United States, Colonial Times to 1957* (Oficina del Censo,
1960), capítulo X, serie X 266-274, "Deposits adjusted and currency outside
banks: 1892 to 1957", p. 646, en millones de USD *"as of June 30 or nearest
available date"*. Su nota de fuente, literal: *"1892-1941 (except series X
274, 1916-1947), Board of Governors of the Federal Reserve System, Banking and
Monetary Statistics, pp. 34-35; 1942-1947, Federal Reserve Bulletin, January
1949, p. 41; 1948-1957, September issues of Bulletin."* Es decir: la misma
cifra, reimpresa por otra agencia. Dos columnas no sirven de contraste: X 266
excluye los depósitos del gobierno (es la columna 1 de la Tabla 9 menos la 5)
y X 274 incluye depósitos en los bancos de la Reserva (nota 6 del Censo).
Se leyeron a mano nueve filas de junio (1892, 1900, 1914, 1920, 1929, 1933,
1941, 1942 y 1946), ampliadas a 600 ppp; en esa tipografía el 3 y el 8 se
confunden, así que cada fila se comprobó con las identidades del propio
Censo antes de anotarla, sin mirar la Tabla 9. Tolerancia declarada antes de
comparar: igualdad. **Resultado: 61 cifras, 61 iguales.** PDF:
`https://www2.census.gov/library/publications/1960/compendia/hist_stats_colonial-1957/hist_stats_colonial-1957-chX.pdf`
(4.456.284 bytes). También se bajó la edición de 1975 (capítulo X,
10.436.734 bytes); su PDF no tiene capa de texto y no se usó. `robots.txt` de
`www2.census.gov`: `User-agent: *` sin vedas; la pausa de 30 s rige solo para
cuatro rastreadores nombrados.

**Segunda fuente del tramo mensual: el NBER, vía FRED.** `data.nber.org`
responde en su `robots.txt` `User-agent: *` / `Disallow: /`: **veda a todo
programa**, y desde el 2026-10-07 no se le pide nada (los archivos de D0.3.3
se leyeron antes de la regla A-D0-29). FRED republica `m14144c` como
`M1444CUSM027SNBR` (1947-01 a 1969-09; `robots.txt` de FRED: pausa de 1 s y
las rutas usadas permitidas); `m14144b`, la versión sin ajustar, no está en
FRED (HTTP 404 al pedir `M1444BUSM027SNBR`). La tolerancia es la que D0.11
propuso y la documentación del NBER sostiene: ±0.1 miles de millones (el
redondeo de sus componentes). Antes de comparar quedó escrito que la serie
del NBER es anterior a la revisión de 1976 de la Tabla 1.1, y que una
diferencia mayor podía ser una revisión de la Junta y no un error de
transcripción; también que los cuatro primeros meses se vieron en el extracto
de la descarga. **Resultado: 144 meses, diferencia máxima 0.1, mediana 0.00:
cerró.** De eso se infiere que la revisión de 1976 no tocó 1947–58 más allá
del redondeo; la diferencia de 0.9 que D0.3.4 vio en 1959-01 queda del lado
de 1959 en adelante y no se investigó aquí.

**Lo que se publica** (`data/series/dinero_eeuu_historico.csv`, formato largo:
`mes, fecha, serie, componente, valor, unidad, estado, control, cita, nota`):

- `dinero_eeuu_1892_1946`: 79 fechas de balance (69 de la Tabla 9 y 10 de la
  continuación, 1942-06-30 a 1946-12-31), en millones de USD, con los tres
  componentes (efectivo fuera de bancos, depósitos a la vista ajustados,
  depósitos a plazo en bancos comerciales) y su total. Estado "dato de fecha
  de balance, estimado en parte" (A-D0-18). Cada fila cita publicación, tabla
  y página; las de 1941 llevan la nota 5 de la Tabla 9 en el componente al
  que aplica. Quiebres declarados en la ficha: 1923-06 (frecuencia), 1941-06
  (nota 5) y 1942-06 (cambio de publicación).
- `dinero_eeuu_1947_1958`: 144 meses, en miles de millones de USD, ajustada
  por estacionalidad, con efectivo, depósitos a la vista, money stock
  (impreso), depósitos a plazo ajustados y el total (money stock + plazo).
  Estado "dato". El mes 1949-03 va con sus cinco valores marcados en disputa.
- `dinero_eeuu_1947_1958_sin_ajustar`: transcrita y controlada, pero **NO
  MEDIDO: sin validación externa** (A-D0-31): su segunda fuente natural,
  `m14144b`, no está en FRED, y `data.nber.org` veda a los programas. Entra a
  la ficha con el motivo; sus valores quedan en los crudos versionados.
- La ficha (`serie_D0.csv`) la escribe `dinero_historico.py` y
  `denominador.py` la conserva en sus corridas. La columna `meses` cuenta
  observaciones: 79 fechas de balance no son meses.

**Lo que queda abierto de este tramo.** La segunda fuente de la serie sin
ajustar (una persona puede leer `m14144b` en un navegador, o buscar otra
publicación de la Junta: el *Supplement to Banking and Monetary Statistics*
de 1962 o el *Federal Reserve Bulletin* de agosto de 1962, pp. 941–51, que la
propia Junta cita); la superposición 1959-01 a 1969-09 de la Tabla 1.1, que
D0.10.6 proponía publicar y no se transcribió; y por qué la Junta imprimió
27.7 en 1949-03 y 119.2 en 1950-12.

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

- **Quiebres declarados:** abril de 1998 (entran como emisores los bancos
  extranjeros en Japón, los fideicomisos extranjeros y Shinkin Central Bank:
  cambio de tramo); junio de 2008, con datos desde 2003-04 (el M2 nuevo
  cambia los tenedores: salen las sociedades de valores, las compañías tanshi
  y los no residentes). Mayo de 1979 (nacen los certificados de depósito y el
  agregado pasa a llamarse M2+CDs) es un cambio de nombre sin cambio de
  perímetro, no un quiebre de la serie (D0.5.1).
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

#### D0.5.1 Paso 0 de la serie antigua: M2+CDs del Banco de Japón (2026-10-07)

**Lo que se pidió.** Verificar en el propio BoJ la serie de dinero amplio
que precede al M2 actual (que empieza en 2003-04): inicio, definición,
quiebres y superposición con la serie nueva, y detenerse con la propuesta
antes de implementar nada. Nada de esto está implementado: es una propuesta
para aprobar o rechazar. Cada pedido de ese día (45, con hora UTC, URL,
código HTTP, bytes y SHA-256) quedó en un registro fuera del repositorio,
como los del paso 0 (D0.1). Cliente: `urllib` con un User-Agent propio, un
pedido por vez, pausas de 2 a 5 s; sin navegador.

**Qué se leyó.** `robots.txt` antes de cualquier otro pedido: `www.boj.or.jp`,
`www.stat-search.boj.or.jp` y `dashboard.e-stat.go.jp` responden HTTP 404
(sin reglas, igual que en D0.15); `fred.stlouisfed.org`, `User-agent: *` con
pausa de 1 s y las rutas usadas permitidas. El aviso de la API del BoJ
(`api_notice_en.pdf`) tiene el mismo SHA-256 que D0.13 anotó el 2026-10-05
(`7773abb2…`): los términos no cambiaron. Documentos del BoJ: el *Final Draft
on the Revision of the Money Stock Statistics* (2008-01-30,
`https://www.boj.or.jp/en/statistics/outline/notice_2008/data/ntms23.pdf`),
el aviso de publicación de los datos retroactivos (2008-06-03,
`.../notice_2008/ntms25.htm`), el aviso de 2008-06-20 (`ntms27.htm`), los
avisos de 1998-04-16 (`.../notice_1998/ntms01.htm`), 1999-04-16
(`.../notice_1999/ntms02.htm`) y 2003-04-10 (`.../notice_2003/ntms07.htm`),
la *Guide to Japan's Money Stock Statistics* de septiembre de 2026
(`.../outline/exp/data/exms01.pdf`), las notas explicativas
(`.../outline/note/notest31.htm`), los metadatos de la base `MD02` en inglés
y japonés, y tres pedidos de datos a la API. Los valores pedidos ese día
coinciden uno por uno con el crudo `boj_m2_2026-10-05.csv` del repositorio.

**La serie antigua: ficha.** Es "M2+CDs" (Ｍ２＋ＣＤ) de la estadística que el
BoJ llama en japonés マネーサプライ ("Money Supply") y rotula en inglés
"(Reference) Money Stock". Base `MD02`, promedio de saldos del mes, sin
ajustar, en 100 millones de yenes, discontinuada (última actualización
2017-12-29), en dos tramos con nombres literales del BoJ:

| Código | Nombre en inglés (literal) | Rango | Meses |
| --- | --- | --- | --- |
| `MAMS1ANM2C` | (discontinued)M2+CDs/Average Amounts Outstanding/(Reference) Money Stock (Based on excluding Foreign Banks in Japan, etc., through March 1999) | 1967-01 a 1999-03 | 387 |
| `MAMS3ANM2C` | (discontinued)M2+CDs/Average Amounts Outstanding/(Reference) Money Stock (from April 1998 to April 2008) | 1998-04 a 2008-04 | 121 |

Hay versiones de fin de mes (`MAMS1ENM2C`, desde 1955-01; `MAMS3ENM2C`, hasta
2008-03), desestacionalizadas (`…X12`) y todos los componentes (M1,
cuasidinero, CD) en las dos bases. Primeros y últimos valores leídos:
`MAMS1ANM2C` 1967-01 = 282.500 y 1999-03 = 6.095.137; `MAMS3ANM2C` 1998-04 =
5.919.793 y 2008-04 = 7.385.144. Sin huecos. La guía (cap. 1, sección 3) dice
que los promedios de M1 y M2 *"have begun to be compiled since 1971"*, pero el
tramo trae promedios desde 1967-01: **NO MEDIDO** cómo se obtuvieron los de
1967 a 1970.

**Definición y diferencias con el M2 actual** (literal, `notest31.htm`):
M2+CDs, base 1998–2008: *"M2 + CDs = M1 + quasi-money + CDs. Quasi-money: Time
deposits + fixed savings + installment savings + nonresident yen deposits +
foreign currency deposits"*, con los mismos emisores que el M2 actual. Base
hasta 1999-03: *"Foreign banks in Japan, foreign trust banks and Shinkin
Central Bank are not included in financial institutions surveyed for M1 and
M2+CDs."* La guía de 2026 (cap. 3, sección 3) resume la diferencia: *"the
differences between the current and former series mainly derive from the
differences in the range of money holders (securities companies, tanshi
companies, and nonresidents are excluded in the current series) and the
estimation method of some data. Apart from that, M2 and 'M2+CDs' (former
series) have the same range of money issuers and financial assets (except for
nonresident yen deposits)."* Y: *"it may be reasonable to analyze M2 from 1967
onward using data of 'M2+CDs' in the former series"*. El *Final Draft* (sección
3.6.1) dice lo contrario de un empalme: *"it is not appropriate to prepare
long-term retrospective data linking the new and present balance figures,
which have different definitions, using a connected index etc."*; y explica
(3.6.2) por qué los datos retroactivos empiezan en 2003-04: *"average balance
data on postal savings are only available since the launch of Japan Post
(April 2003)"*.

**Quiebres y superposición** (API del BoJ, 2026-10-07):

- Serie antigua termina en 2008-04; la nueva empieza en 2003-04: **61 meses
  comunes**. El M2 nuevo queda por debajo de M2+CDs entre 0.422 % (2003-04:
  6.767.067 contra 6.795.761) y 0.590 %, media 0.501 %; 2008-03: 7.299.474
  contra 7.340.702 (−0.562 %). La diferencia crece con el tiempo.
- Dentro de la serie antigua, 12 meses comunes entre los dos tramos
  (1998-04 a 1999-03): el tramo con bancos extranjeros queda entre 0.410 % y
  0.483 % por encima (1998-04: 5.919.793 contra 5.892.568).
- 1979-05 nacen los CD (guía, cap. 1): el componente CD empieza ese mes
  (1.716) y antes no existe. **No es un quiebre de la serie:** es un cambio de
  nombre del agregado sin cambio de perímetro; lo que D0.5 llama "quiebre de
  mayo de 1979" debería reescribirse así.
- 2003-04, giro postal (`ntms07.htm`): afecta a M3+CDs y a la liquidez amplia,
  no a M2+CDs.
- Identidad M1 + cuasidinero + CD = M2+CDs: cuadra en los 121 meses del tramo
  1998–2008 y, en el tramo 1967–1999, desde 1974-10; **falla de 1967-01 a
  1974-09** (M2+CDs supera a la suma entre 86 y 313, del orden de 0.03 % a
  0.1 %; por ejemplo 1967-01: 282.500 contra 282.344). **NO MEDIDO** por qué.
- La tabla de comparación a marzo de 2008 que anuncia el aviso de 2008-06-03
  ya no está en la página (0 tablas en el HTML): **NO MEDIDO** la cifra
  oficial; se reemplaza por el cálculo con la API (−0.562 % en 2008-03).
- El propio BoJ empalma su serie interanual `MAM1YAM2M2MO` (desde 1968-01)
  usando `MAMS1ANM2C` hasta 1999-03, `MAMS3ANM2C` hasta 2004-03 y el M2 nuevo
  desde 2004-04, sin ajuste de nivel: cada tramo contra su propio año
  anterior. Verificado: 0 meses fuera de ±0.05 puntos en 704.

**Segunda fuente.** FRED `MYAGM2JPM189N` ("M2 for Japan", FMI, *International
Financial Statistics*, 1967-01 a 2017-02, sin ajuste, múltiplos de 10⁸ yenes;
la ficha dice *"Copyright © 2016, International Monetary Fund. Reprinted with
permission"*) reproduce exactamente los dos tramos antiguos: con tolerancia
±0.5 en 100 millones de yenes, declarada antes de comparar, **435 de 435
meses** iguales (1967-01 a 1998-03 contra `MAMS1ANM2C`; 1998-04 a 2003-03
contra `MAMS3ANM2C`); coincide con el M2 nuevo hasta 2012-10 y difiere después
(revisiones del BoJ). **El tablero de e-Stat no tiene M2+CDs** (su API, en
inglés y en japonés, solo devuelve el M2 actual, su interanual y la liquidez
amplia). Los términos del FMI para ese crudo: **NO LEÍDOS**.

**Implicaciones para la suma de tres economías.** Verificado en
`serie_D0.csv`: `m2_eeuu` desde 1959-01, `m2_eurozona` desde 1980-01
(estimación hasta 1997-08), `jpy_por_usd` desde 1971-01, `usd_por_eur` desde
1999-01. **El cuello de botella es el tipo de cambio del euro, 1999-01,** no
Japón: con M2+CDs el agregado podría retroceder de 2003-04 a 1999-01 (51
meses), todos del tramo `MAMS3ANM2C`, el que comparte emisores con el M2
actual. El salto que heredaría en 2003-04 es el 0.422 % de la parte japonesa:
unos 23,8 de los 17.237,89 miles de millones de USD del agregado de ese mes,
el 0.14 %. Japón solo, en USD, podría ir desde 1971-01.

**Propuesta, para aprobar o rechazar.**

1. Dos series nuevas, separadas y sin empalmar (A-D0-6): `m2cd_japon_1998_2008`
   (`MAMS3ANM2C`, 1998-04 a 2008-04) y `m2cd_japon_1967_1999` (`MAMS1ANM2C`,
   1967-01 a 1999-03), con los nombres literales del BoJ en inglés y japonés,
   el rótulo "M2+CDs (Money Supply)" y nunca "M2" solo; estado **dato**;
   promedio de saldos del mes, sin ajustar, 100 millones de yenes; quiebres en
   la ficha: 1979-05 (nombre, sin cambio de perímetro), 1998-04 (perímetro:
   diferencia de 0.41 % a 0.48 % en 12 meses comunes), 2003-04 (empieza el M2
   nuevo: 61 meses comunes, de 0.42 % a 0.59 % por debajo). No hace falta
   ninguna descarga nueva: `DESCARGA_BOJ_M2` ya pide los cuatro códigos y el
   crudo del 2026-10-05 los trae. Misma licencia (b), mismo crédito de la API
   y mismo aviso pendiente (A-D0-8, D0.13).
2. Gate contra FRED `MYAGM2JPM189N`, tolerancia ±0.5 en 100 millones de yenes
   (la resolución con que FRED publica), con la declaración de que el
   resultado ya se conoce, como A-D0-25 lo dice del balance de la Fed. El
   crudo de FRED iría a `data/privado/` mientras no se lean los términos del
   FMI. Controles, sin detener la corrida: la identidad de componentes (±0.5;
   marcaría en disputa 1967-01 a 1974-09) y la variación interanual contra
   `MAM1YAM2M2MO` (±0.05 puntos).
3. El agregado, tres opciones: (a) no tocarlo; (b) un segundo agregado con
   nombre propio desde 1999-01, con el quiebre de 2003-04 declarado y sin
   corregir, como las ampliaciones de la Eurozona (A-D0-4); (c) extender
   `agregado_usd` hacia atrás con el quiebre declarado y otro nombre para el
   tramo anterior. En (b) y (c) cambia el mes base del tipo de cambio
   constante (A-D0-11), lo que mueve toda esa columna: supuesto numerado y
   changelog obligatorios.
4. Supuestos nuevos que haría falta escribir: las series separadas y sus
   nombres; el gate contra FRED con su declaración; qué hace el agregado; el
   crudo del FMI como privado. Retoques: A-D0-6 (quitar "queda como decisión
   pendiente") y el "quiebre de mayo de 1979" de D0.5.

**Decisión del dueño (2026-10-07) y lo implementado.** Aprobado como series
separadas sin empalme: `m2cd_japon_1967_1999` y `m2cd_japon_1998_2008`,
estado dato, con sus quiebres (A-D0-34); gate contra FRED `MYAGM2JPM189N` con
±0.5 en 100 millones de yenes, en el rango que la copia del FMI sigue a cada
tramo, y el resultado declarado como conocido (A-D0-35); el agregado en USD
de tres economías desde 1999-01, con Japón por tramos y el salto de 2003-04
en la columna `quiebre`, sin euro sintético antes de esa fecha (A-D0-36). Los
controles de identidad de componentes y de variación interanual no se
implementaron: harían falta más códigos en la descarga del BoJ.

**Lo que queda abierto.** La anomalía 1967–1974 (candidata a consulta al BoJ:
`post.rsd5@boj.or.jp` según la guía); los promedios de 1967–1970; qué cambió
el 2017-12-29 (FRED, congelado en 2017-07, coincide con lo de hoy: no fueron
valores del tramo antiguo); los términos del FMI; el tipo de cambio del euro
antes de 1999 y del yen antes de 1971; y el aviso al BoJ, que vale igual para
estas series.

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
| M2+CDs de Japón, dos tramos (A-D0-34) | API del BoJ, mismo crudo | FRED `MYAGM2JPM189N` (FMI, IFS), hasta 1998-03 el tramo viejo y de 1998-04 a 2003-03 el nuevo | Gate | ±0.5 en 100 millones de yenes (múltiplos de 10⁸ yenes en FRED); resultado conocido al fijarla (A-D0-35) |
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

   Dirección y asunto, citados de "Notice Regarding the Use of the API
   Service" (`https://www.stat-search.boj.or.jp/info/api_notice_en.pdf`,
   leído el 2026-10-05, SHA-256
   `7773abb22c8a863038a0926001253e4b2cc4cb3a56db234772b64bad8c8b5fd6`),
   sección I, "Notification on the Release of Services using the API":

   > E-mail: post.rsd17@boj.or.jp
   > Subject: [Release of the service using the API]

   El destinatario es el Departamento de Investigación y Estadística
   ("Research and Statistics Department"). El crédito de la sección II,
   "Credit", palabra por palabra:

   > "This service uses the API provided by the "Bank of Japan Time-Series
   > Data Search." The Bank of Japan does not guarantee the content of the
   > service."

   La misma sección dice que no hay un lugar obligatorio para mostrarlo,
   siempre que los usuarios del servicio puedan encontrarlo con facilidad.
   El sitio lo muestra junto a las dos series de Japón y en el pie, con ese
   texto exacto (`src/lib/creditos.ts` de eldenominador).
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
7. **Las tablas de la Junta anteriores a 1959: transcritas y publicadas el
   2026-10-07** (D0.3.6, A-D0-31). Sigue abierta la segunda fuente de la
   serie sin ajustar de 1947–58 (`m14144b` no está en FRED y data.nber.org
   veda a los programas) y la superposición 1959-01 a 1969-09 de la
   Tabla 1.1, que no se transcribió.
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
18. **El test de los crudos contra el manifiesto fallaba en Windows** (visto el
    2026-10-07, también en `main`): `core.autocrlf=true` extraía los CSV de
    `data/raw/` con CRLF, y los hashes publicados de `bce_m2_ajustada`,
    `bce_m2_sin_ajustar`, `bce_balance_eurosistema` y
    `ocde_china_dinero_amplio` del 2026-10-05 correspondían al contenido con
    CRLF que entregó la fuente, mientras que el repositorio los guardaba con
    LF. **Cerrado el mismo día por decisión del dueño:** el archivo canónico
    son los bytes exactos de la fuente; todo `data/raw/` es `-text` y esos
    cuatro crudos volvieron a sus bytes originales. Ningún hash cambió
    (A-D0-27, changelog).

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
- El gate del balance de la Fed contra el BIS: D0.11 lo proponía como control
  y decía que no cerraba en 118 meses; el PR lo informó como gate que cerró.
  Las dos cosas son ciertas de dos series distintas: la bruta no cierra, la
  consolidada (A-D0-15) sí, y el gate se definió sabiendo eso. Qué quedó y por
  qué está en A-D0-25.

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

---

## N0. Fuentes de El Numerador: oferta de activos, su tasa de crecimiento y su elasticidad

> **PASO 0, SIN CÓDIGO (2026-10-07).** Todo lo que figura aquí se leyó de la
> fuente el 2026-10-07, entre las 16:31 y las 16:43 UTC, desde una máquina con
> salida directa, con `python-requests 2.33.1` y su User-Agent por defecto, salvo
> donde la ficha diga otra cosa. Cada descarga quedó anotada con su URL, hora,
> estado HTTP, bytes y SHA-256 en `senales/data/privado/n0_paso0/<tema>/registro.md`
> (carpeta que git ignora, A-R0-15). Nada viene de memoria. Lo que no se pudo
> leer está dicho como tal y no tiene cifras.
>
> **Ninguna decisión está tomada.** Las propuestas van en N0.10, la validación
> propuesta en N0.11 y el índice de supuestos A-N0-\* propuestos en N0.12.

Este documento es el entregable del paso 0 de la familia N0 (El Numerador,
`elnumerador.com`): evaluar, por activo, de dónde puede salir una serie
**observada** de la oferta (cuánto hay y cuánto se agrega por año), con la misma
disciplina que las fases R y D0. Los activos son los cinco que el sitio ordena en
su "jerarquía": efectivo y bonos, acciones, inmuebles, oro y Bitcoin. La plata
entra porque ya tiene precio en la fase R y el USGS la publica junto al oro. El
dinero (M2) ya está en D0 y no se duplica.

**La corrección conceptual que estas series tienen que reflejar.** Dos cosas
distintas:

- **Tasa de crecimiento de la oferta:** cuánto crece el stock por año. Es un
  cociente entre lo que se agregó en el año y lo que había. Es un dato cuando el
  flujo y el stock están medidos.
- **Elasticidad de la oferta:** cuánto responde la oferta a un cambio del
  precio. Es una pendiente estimada, con rezago, con intervalo. Nunca es un
  número único y nunca es un dato.

Cada serie de N0 dice cuál de las dos mide. El sitio hoy las mezcla (N0.0, fila
11). Y BTC no está en 0 %: su emisión anual es positiva y decreciente; lo que es
cero es su elasticidad, por construcción del protocolo (N0.3).

**Sobre las citas.** Como en D0: las cláusulas de fuentes en dominio público o
abiertas van literales; las de fuentes con derechos reservados van
parafraseadas, con la URL. Ningún nivel de índice bursátil se reproduce aquí
(regla de `CLAUDE.md`), tampoco los que trae el código del sitio.

### N0.0 Qué afirma hoy el sitio

Leído en el repositorio `danioni/elnumerador`, rama `master`, commit
`3ac29061d225dd6d67ef13164cc19f9b2bfabe58` (2026-10-06T15:15:51Z), por la API de
GitHub. Los textos salen de `src/components/Dashboard.tsx` (último cambio
`2bf08c1`, 2026-03-03) y las cifras de `src/lib/data.ts` (último cambio
`ad06489`, 2026-02-18). La portada desplegada (`https://elnumerador.com/`,
leída a las 16:31 UTC, 30.358 bytes, SHA-256
`bdb471cc7bf46157e157e9e988427bfc7b556b3d0d98616ee9ee6ac47a70e08e`) muestra
exactamente los textos de `master`: no hay otra versión publicada.

**Cómo produce sus cifras `data.ts`.** Tiene 18 "anclas" anuales escritas a
mano (1913, 1929, 1945, 1960, 1971, 1980, 1990, 2000, 2009, 2012, 2015, 2017,
2020 a 2025), interpola geométricamente entre ellas para cada año, y de ahí
deriva índices, stock-to-flow, "dilución" interanual y una "elasticidad". El
comentario de cabecera cita como fuentes "World Gold Council, WFE, UN-Habitat,
BIS, SIFMA, blockchain data", sin URL, sin fecha y sin tabla de origen. **Nada
de eso cumple la regla "ningún número sin fuente".**

| N.º | Afirmación (literal) | Dónde | De qué sale |
| --- | --- | --- | --- |
| 1 | "Bonos se emiten al ritmo de la impresora. Acciones, 3-5% anual. Inmuebles, 2-3%. Oro, 1.5%." | `Dashboard.tsx`, texto de portada | Texto fijo |
| 2 | "Cash / Bonos · Nivel 1 — Es el denominador · 7-15% anual · expansión de oferta" | `Dashboard.tsx`, `ASSET_TIERS` | Texto fijo |
| 3 | "Acciones · Nivel 2 — Elasticidad alta · ~3-5% anual"; "la emisión neta global es positiva" | ídem | Texto fijo |
| 4 | "Inmuebles · Nivel 3 — Elasticidad moderada · ~2-3% anual" | ídem | Texto fijo |
| 5 | "Oro · Nivel 4 — Elasticidad baja · ~1.5% anual"; "Stock-to-flow alto (~60 años), pero no infinito" | ídem | Texto fijo |
| 6 | "Bitcoin · Nivel 5 — Elasticidad cero · 0% · expansión de oferta"; etiqueta "Supply fijo"; "La emisión se reduce a la mitad cada ~4 años hasta converger a cero" | ídem | Texto fijo |
| 7 | "21 millones de unidades"; "se reduce a la mitad cada 210,000 bloques (~4 años)" | `Dashboard.tsx` | Texto fijo |
| 8 | "Cuando el precio sube, no se produce más Bitcoin. En cualquier otro activo, el alza incentiva producción" | `Dashboard.tsx`, "El caso límite" | Texto fijo |
| 9 | Producción minera de oro, en toneladas: 1913 = 690, 1929 = 600, 1945 = 800, 1960 = 1050, 1971 = 1250, 1980 = 1220, 1990 = 2180, 2000 = 2590, 2009 = 2600, 2012 = 2860, 2015 = 3100, 2017 = 3300, 2020 = 3200, 2021 = 3560, 2022 = 3612, 2023 = 3644, 2024 = 3700, 2025 = 3500 | `data.ts`, `gold_production` | Anclas a mano; comparadas con el USGS en N0.4.6 |
| 10 | Oro sobre la superficie, en toneladas: 1913 = 35000 … 2024 = 212000, 2025 = 215000; stock-to-flow 2025 = 215000 / 3500 = 61.4; proyección a 2050 con la producción cayendo 1 % por año ("peak gold") | `data.ts`, `gold_stock_tonnes`, `generateS2FProjection` | Anclas a mano y un supuesto sin fuente |
| 11 | "Cada activo tiene una tasa a la que se crean nuevas unidades — su elasticidad de oferta" | `Dashboard.tsx`, "La jerarquía de la elasticidad" | Define la elasticidad como la tasa de crecimiento: son dos cosas distintas |
| 12 | `elasticity_gold`, `elasticity_equities`, `elasticity_realestate`, `elasticity_bonds`: cociente entre la variación porcentual del índice de oferta y la del índice de precio en ventanas de 10 años | `data.ts`, tercer pase | Cálculo sobre anclas interpoladas, sin rezago y sin intervalo |
| 13 | Oferta de BTC: 2009 = 1623400, 2012 = 10625050, 2015 = 15027800, 2017 = 16774575, 2020 = 18587000, 2021 = 18897000, 2022 = 19240000, 2023 = 19570000, 2024 = 19790000, 2025 = 19830000; de ahí `btc_pct_mined` 2025 = 94.4 %; emisión anual = 2628000 / 2^(halvings), con 52560 bloques por año | `data.ts` | Anclas a mano con interpolación lineal; comparadas con Coin Metrics en N0.3 |
| 14 | "Global shares outstanding (billions)": 1913 = 5 … 2025 = 325; "Companies listed globally": 2000 … 43500 | `data.ts`, `equities_shares_billion`, `equities_companies` | Anclas "estimated from market cap / avg price ratios, WFE data post-1990" |
| 15 | "Global housing units (millions)": 1913 = 250 … 2025 = 1900 | `data.ts`, `realestate_units_million` | Anclas "UN-Habitat, census data" |
| 16 | "Global debt outstanding (trillions USD)": 1913 = 0.03 … 2024 = 145, 2025 = 150 | `data.ts`, `bonds_outstanding` | Anclas "BIS, SIFMA, historical US Treasury data" |
| 17 | "El S&P 500 subió ~750x desde 1913. El denominador subió ~3,400x"; "Multiplicó 10x desde 2000 vs. un denominador que multiplicó 7x"; "$100,000 ahorrados en 2000 compran hoy lo que $45,000" | `Dashboard.tsx` | Precio y M2: fuera del alcance de N0 (fases R y D0) |

**Lo que el encargo parafraseó y no está en `master`.** El pedido del paso 0
cita "bonos y acciones entre 3 % y 8 %", "Bitcoin se acerca a cero" y
stock-to-flow "Oro ~62, Acciones ~20, Bonos ~12". En `master` del 2026-10-06 no
aparece ninguna de esas tres frases: los rangos publicados son los de las filas
1 a 6; el stock-to-flow del oro que calcula el código es 61.4 (fila 10) y el
texto dice "~60 años"; no hay stock-to-flow de acciones ni de bonos en el código;
y "converger a cero" (fila 6) es lo más cercano a "se acerca a cero". El
"94,4 %" sí sale del código (fila 13). Es posible que esas frases hayan estado
en una versión anterior del sitio; el historial de `Dashboard.tsx` tiene diez
commits entre el 2026-02-08 y el 2026-03-03 y no se revisaron uno por uno.

### N0.1 Qué se leyó, desde dónde y cómo

**`robots.txt` antes de cada host**, con una excepción que se declara en la
tabla (nora.nerc.ac.uk). Un host sin `robots.txt` (HTTP 404) se trata como sin
reglas, igual que en D0.15.

| Host | `robots.txt` | Estado el 2026-10-07 |
| --- | --- | --- |
| api.github.com (vía `gh api`) | No aplica: API autenticada, no el sitio | Leídos los archivos de `danioni/elnumerador` (`master`) y de `bitcoin/bitcoin` (`master`). |
| elnumerador.com | Sin archivo (HTTP 404) | Portada leída. |
| pubs.usgs.gov | `User-agent: *`, `Disallow: /archive/` | Dos capítulos de los *Mineral Commodity Summaries 2026*, fuera de `/archive/`. |
| www.usgs.gov | Veda `/search/`, `/admin/` y rutas de Drupal; nada de lo pedido | Política de derechos, página de la *Data Series 140* y dos páginas de archivos. |
| d9-wret.s3.us-west-2.amazonaws.com | `robots.txt` responde HTTP 403 (`AccessDenied`): no hay archivo legible | Es donde www.usgs.gov aloja los xlsx de la *Data Series 140*. Dos descargas. Se trata como sin reglas; se declara. |
| www.federalreserve.gov | Sin archivo (HTTP 404) | Índice del Z.1, descargo legal, fechas de publicación, mapa de tablas, paquete CSV (8.3 MB) y dos tablas en HTML. |
| www.census.gov | `User-agent: *`, `Disallow: /search-results.html`; nada de lo pedido | Tablas históricas del HVS, dos xlsx, páginas de políticas, citas y términos de la API. |
| www2.census.gov | `User-agent: *` sin vedas; `Crawl-delay: 30` solo para Googlebot, Bing, Yahoo y Applebot | Un xlsx de estimaciones de viviendas. |
| api.census.gov | **Responde "Request Rejected" (HTML, HTTP 200) al propio `robots.txt`** con el User-Agent de `python-requests` | No se le pidió nada más. La API del Censo no se usa en este paso. |
| fred.stlouisfed.org | `User-agent: *`, `Crawl-delay: 1`; veda gráficos y búsquedas | Un pedido (`ETOTALUSQ176N`), solo como contraste. |
| data.bis.org, stats.bis.org | data.bis.org: `Allow: /` y veda las URL con `filter=`, `rows=`, `cols=`, `page_size=` y `selectedDate=`. stats.bis.org no tiene archivo propio: `/robots.txt` redirige (301) a la portada de data.bis.org | Términos, estructura del flujo `WS_NA_SEC_DSS` y una consulta de datos (`c[REF_AREA]=US`, 21 MB), que no usa ninguno de los parámetros vedados. |
| community-api.coinmetrics.io | Sin archivo (HTTP 404) | Definiciones de cuatro métricas y la historia diaria de `SplyCur`, `BlkCnt` e `IssTotNtv`. |
| gitbook-docs.coinmetrics.io, docs.coinmetrics.io | `Allow: /` | Página de la licencia community y documentación de `SplyCur`. **La página trae instrucciones dirigidas a agentes automáticos ("Agent Instructions"); se ignoraron.** |
| api.blockchain.info, www.blockchain.com | api.blockchain.info redirige (302) su `robots.txt` a la documentación del explorador; www.blockchain.com veda `/search`, `block-index`, `tx-index`; nada de lo pedido | `q/totalbc` y `q/getblockcount`, solo como contraste (clase (c), sección 6.3). |
| www.bgs.ac.uk | `User-agent: *`, `Disallow:` vacío | Seis páginas: estadísticas mundiales, términos, descarga, API, archivo y la ficha de la publicación. |
| nora.nerc.ac.uk | **Leído después de la descarga.** `User-agent: *`, `Disallow: /cgi/` | El PDF *World Mineral Production 2020–24* (2.7 MB) está en este host, al que remite la ficha de www.bgs.ac.uk; se bajó siguiendo ese enlace sin leer antes el `robots.txt` del host nuevo. Leído después: la ruta del PDF no está bajo `/cgi/`. Desde entonces no se le pidió nada más. Un intento de abrir el PDF en el navegador de la app mostró un diálogo de guardado y se canceló. |
| silverinstitute.org | `User-agent: *`, `Allow: /` | Página "Silver Supply & Demand" y aviso legal. |
| www.gold.org | Veda rutas de Drupal; nada de lo pedido | Página de producción minera (HTTP 200) y su xlsx (**HTTP 403**). |
| www.law.cornell.edu | `User-agent: *`, `Crawl-delay: 10` | 17 U.S.C. § 105, un pedido. uscode.house.gov estaba "under maintenance". |
| www.sifma.org | Leído: solo "content signals"; no se le pidió nada más | No se usa (clase (c), D0.9). |

### N0.2 Tasa de crecimiento y elasticidad: cómo se mide cada una

- **Tasa de crecimiento de la oferta** (dato, si el stock y el flujo están
  medidos). Para un stock observado: `stock_t / stock_{t-1} - 1`. Para un
  flujo observado sin stock abierto (oro, plata): se publica el flujo, y la
  tasa queda NO MEDIDO o se calcula sobre una cifra de terceros declarada
  (A-D0-28), fuera de las métricas.
- **Elasticidad de la oferta** (estimación, siempre). Pendiente de la
  variación del flujo respecto de la variación del precio, con rezagos,
  estimada sobre una serie larga y publicada como intervalo. El método, los
  rezagos y las submuestras se fijan antes de calcular (N0.10.2). Para BTC es
  cero **por construcción**: el subsidio por bloque es función de la altura y
  de nada más (N0.3.1); eso es un dato del protocolo, no una estimación.
- Lo que el sitio llama "elasticidad" (fila 12 de N0.0) es un cociente de
  variaciones a diez años sin rezago sobre anclas interpoladas. No es ni una
  tasa de crecimiento observada ni una elasticidad estimada.

### N0.3 BTC

#### N0.3.1 Calendario de emisión del protocolo: Bitcoin Core — leído, MIT

- Leído de `bitcoin/bitcoin`, rama `master`, commit
  `9dfde64cc3262329051fd05fffe40eecc786a99f` (2026-10-07T12:54:56Z):
  - `src/kernel/chainparams.cpp`, línea 114 (red principal):
    `consensus.nSubsidyHalvingInterval = 210000;`
  - `src/validation.cpp`, líneas 1833–1844, literal:

    ```
    CAmount GetBlockSubsidy(int nHeight, const Consensus::Params& consensusParams)
    {
        int halvings = nHeight / consensusParams.nSubsidyHalvingInterval;
        // Force block reward to zero when right shift is undefined.
        if (halvings >= 64)
            return 0;

        CAmount nSubsidy = 50 * COIN;
        // Subsidy is cut in half every 210,000 blocks which will occur approximately every 4 years.
        nSubsidy >>= halvings;
        return nSubsidy;
    }
    ```

  - `src/consensus/amount.h`, líneas 15 y 26: `COIN{100'000'000}` y
    `MAX_MONEY{21'000'000 * COIN}`.
- **Qué es:** una función determinista de la altura del bloque. El subsidio es
  50 BTC en los bloques 0 a 209999, 25 en los 210000 a 419999, 12.5, 6.25 y
  3.125 (desde el bloque 840000). La suma de todos los subsidios tiende a 21
  millones y nunca los alcanza. El calendario no depende del precio ni de
  ninguna otra variable: **la elasticidad es cero por construcción.**
- **Lo que el calendario no da:** fechas. El tiempo entre bloques es aleatorio
  alrededor de diez minutos; cuántos bloques caen en un año calendario es un
  dato observado (N0.3.2), no del protocolo. La emisión anual "del protocolo"
  es subsidio × bloques del año, y los bloques del año se leen de la cadena.
- Licencia: MIT (`COPYING`). Se citan diez líneas de código con su commit.

#### N0.3.2 Oferta observada: Coin Metrics community, `SplyCur`, `IssTotNtv`, `BlkCnt` — leída, (b)

- URL: `https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=SplyCur,BlkCnt,IssTotNtv&frequency=1d&page_size=10000`
  (773.293 bytes, SHA-256
  `ae3c1339354c7a7f8613aa9a701d4b3395d354fa332c55a081c870b3ff327a24`).
  Definiciones en `/v4/reference-data/asset-metrics?metrics=SplyCur,BlkCnt,IssTotNtv,SplyExpFut10yr`.
- **Definiciones oficiales, literales:**
  - `SplyCur`: *"The sum of all native units ever created and visible on the
    ledger (i.e., issued) at the end of that interval."* La documentación
    agrega: *"For UTXO chains, current supply is the sum of all unspent output
    values."*
  - `IssTotNtv`: *"The sum of all new native units issued that interval."*
  - `BlkCnt`: *"The sum count of blocks created that interval that were included
    in the main (base) chain."*
- Frecuencia: diaria, cierre a las 00:00 UTC del día siguiente (misma
  convención que `PriceUSD`, sección 6.2).
- Unidad: BTC (unidades nativas).
- **Inicio real:** 2009-01-03 con `SplyCur = 0` y `BlkCnt = 0`; el primer día
  con oferta es **2009-01-09: 19 bloques, 950 BTC emitidos, `SplyCur = 950`.**
  El bloque génesis (2009-01-03) no cuenta ni como bloque ni como oferta: sus
  50 BTC no están en el conjunto de salidas no gastadas. Es una diferencia de
  definición respecto del calendario, no un error.
- Volumen: **6.486 filas del 2009-01-03 al 2026-10-06, sin paginación y sin
  días faltantes.**
- Último dato: 2026-10-06, `SplyCur = 20094435.50075681`, 155 bloques, 484.375
  BTC emitidos.
- Clave / registro: no. Límite: 10 pedidos por 6 segundos por IP.
- **Licencia: (b), CC BY-NC 4.0**, la misma de A-R0-4 (página
  `gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.md`, releída
  hoy: *"Available to the community under the Creative Commons license"*, con
  enlace a `creativecommons.org/licenses/by-nc/4.0/`).
- **Lo que dicen los datos (cálculo propio sobre la descarga):**

  | Año | Bloques | Emisión (`IssTotNtv`, BTC) | Oferta al 31-12 (`SplyCur`, BTC) | Tasa de crecimiento |
  | --- | --- | --- | --- | --- |
  | 2019 | 54232 | 677900.000 | 18133617.32 | 3.884 % |
  | 2020 | 53222 | 453287.500 | 18586896.44 | 2.500 % |
  | 2021 | 52686 | 329287.500 | 18916168.79 | 1.772 % |
  | 2022 | 53188 | 332425.000 | 19248585.15 | 1.757 % |
  | 2023 | 53999 | 337493.750 | 19586074.25 | 1.753 % |
  | 2024 | 53473 | 217756.250 | 19803829.62 | 1.112 % |
  | 2025 | 53082 | 165881.250 | 19969701.16 | 0.838 % |
  | 2026 | 39915 | 124734.375 | — (hasta el 2026-10-06) | — |

  La emisión de 2025 (165881.25 BTC) es exactamente 53082 bloques × 3.125:
  en 2025 ningún bloque reclamó menos que el subsidio. Con 52560 bloques (el
  supuesto de `data.ts`) la emisión habría sido 164250. **La tasa de
  crecimiento observada de la oferta fue 0.838 % en 2025 y 1.112 % en 2024:
  positiva, decreciente, y no 0 %.**

- **Contraste con el calendario del protocolo (cálculo propio).** Si `N` es la
  suma de `BlkCnt` hasta un día, la suma de los subsidios de los bloques 1 a
  `N` (sin el génesis) es la oferta máxima que el calendario permite ese día.
  La diferencia `SplyCur - calendario`:

  | Fecha | `BlkCnt` acumulado (N) | Calendario, bloques 1..N (BTC) | `SplyCur` (BTC) | Diferencia (BTC) | Diferencia |
  | --- | --- | --- | --- | --- | --- |
  | 2012-11-28 | 210063 | 10501550.000 | 10501539.94351183 | -10.056 | -0.00010 % |
  | 2016-07-09 | 420052 | 15750612.500 | 15750598.60474103 | -13.895 | -0.00009 % |
  | 2020-05-11 | 630028 | 18375131.250 | 18375098.57078164 | -32.679 | -0.00018 % |
  | 2024-04-20 | 840133 | 19687868.750 | 19687799.24271483 | -69.507 | -0.00035 % |
  | 2024-12-31 | 877263 | 19803900.000 | 19803829.62409340 | -70.376 | -0.00036 % |
  | 2025-12-31 | 930345 | 19969781.250 | 19969701.15996540 | -80.090 | -0.00040 % |
  | 2026-10-06 | 970260 | 20094515.625 | 20094435.50075681 | -80.124 | -0.00040 % |

  La diferencia es siempre negativa (nunca hay más oferta que la que el
  calendario permite) y crece lentamente: son los subsidios que algún minero
  no reclamó enteros y las salidas que ya no están en el conjunto no gastado.
  Que `BlkCnt` acumulado sea la altura del último bloque (es decir, que no
  cuente al génesis) es una **inferencia**: con la otra convención la
  diferencia de 2012-11-28 sería positiva, y eso es imposible.
- **Lo que esta fuente no es:** no es "la cadena". Es la lectura que hace Coin
  Metrics de su nodo. Para contrastar hay una segunda lectura (N0.3.3) y el
  calendario (N0.3.1).

#### N0.3.3 blockchain.com, `q/totalbc` y `q/getblockcount` — leída, (c), contraste

- `https://api.blockchain.info/q/totalbc` respondió `2009485300000000`
  satoshis = **20094853.00 BTC** y `q/getblockcount` respondió **970363**, a las
  16:34 UTC del 2026-10-07.
- El calendario del protocolo hasta el bloque 970363 inclusive suma
  20094887.5 BTC con el génesis y 20094837.5 sin él (cálculo propio). El valor
  de blockchain.com cae entre los dos: no coincide con la suma de salidas no
  gastadas de Coin Metrics ni con el calendario exacto; es, por lo que se ve,
  una cuenta propia de ese sitio. No se leyó su método.
- No es comparable día a día con Coin Metrics sin alinear la altura: el dato de
  Coin Metrics del 2026-10-06 cierra en 970260 bloques acumulados y el de
  blockchain.com está 103 bloques más adelante. La comparación a igual altura
  queda para el paso 1 (N0.11).
- Licencia: (c), la lectura de la sección 6.3. Solo sirve para contrastar.

### N0.4 Oro

#### N0.4.1 USGS, *Mineral Commodity Summaries 2026*, capítulo "Gold" — leída, dominio público

- `https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gold.pdf` (138.864 bytes,
  SHA-256 `c2fef62f665d3334302b8b9bd32e2da6f40b3f8136d1ae00ffa102e196943627`;
  los mismos bytes que en 4.6).
- Frecuencia: anual; cada edición trae dos años de producción mundial (el
  último, estimado) y cinco de estadísticas de EE.UU.
- Convención y unidad: toneladas métricas de contenido de oro, producción de
  mina del año calendario. Nota 1: *"One metric ton (1,000 kilograms) =
  32,150.7 troy ounces."*
- **Valores leídos** (tabla "World Mine Production and Reserves" y texto
  "Events, Trends, and Issues", literal: *"In 2025, worldwide gold mine
  production was an estimated 3,300 tons compared with 3,280 tons in 2024."*):

  | | 2024 | 2025 (estimado) |
  | --- | --- | --- |
  | Mundo (redondeado) | 3280 | 3300 |
  | EE.UU. | 163 | 160 |

  Y en "Salient Statistics—United States", producción de mina: 2021 = 187,
  2022 = 173, 2023 = 170, 2024 = 163, 2025e = 160.
- Quiebres: el último año es siempre estimado y la edición siguiente lo
  revisa. La lectura de la tabla por país no es confiable con `pdftotext`
  (mezcla columnas); el total mundial y la fila de EE.UU. se confirmaron con
  el texto corrido.
- Clave / registro: no.
- **Licencia: dominio público.** `https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits`,
  releída hoy, literal: *"USGS-authored or produced data and information are
  considered to be in the U.S. Public Domain."*

#### N0.4.2 USGS, *Data Series 140*, "Gold statistics", 1900–2022 — leída, dominio público

- Página: `https://www.usgs.gov/centers/national-minerals-information-center/historical-statistics-mineral-and-material-commodities`
  → `https://www.usgs.gov/media/files/gold-historical-statistics-data-series-140`
  → archivo `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-gold-2022.xlsx`
  (40.809 bytes, SHA-256
  `025f3eb98adb606cc214b82caa70646b80cf9debdf6544dbafce361283c1c480`),
  "Last modification: November 20, 2023".
- Frecuencia: anual. Columnas: producción primaria y secundaria de EE.UU.,
  importaciones, exportaciones, consumo, valor unitario en USD por tonelada
  (corriente y en dólares de 1998) y **producción mundial**.
- Unidad: toneladas métricas de contenido de oro.
- **Inicio real: 1900 = 386 t.** Último: 2022 = 3160 t. 123 años sin huecos en
  la columna mundial.
- Valores leídos en los años ancla del sitio: 1913 = 694, 1929 = 609,
  1945 = 762, 1960 = 1190, 1971 = 1450, 1980 = 1220, 1990 = 2180, 2000 = 2590,
  2009 = 2490, 2012 = 2740, 2015 = 3100, 2017 = 3260, 2020 = 3050, 2021 = 3120,
  2022 = 3160.
- La suma de la columna mundial 1900–2022 da 175343 t (cálculo propio). **No es
  el stock sobre la superficie:** falta todo lo anterior a 1900 y la serie no
  resta nada. Se anota solo para dejar claro que de aquí no sale un stock.
- Es un flujo, no un acervo. También trae un precio anual desde 1900 (valor
  unitario), útil para una estimación de elasticidad (N0.10.2).
- Licencia: la misma de N0.4.1.

#### N0.4.3 British Geological Survey, *World Mineral Production 2020–24* — leída, contraste, términos restrictivos

- Ficha: `https://www.bgs.ac.uk/mineralsuk/statistics/world-mineral-statistics/world-mineral-statistics-archive/`
  → `https://nora.nerc.ac.uk/id/eprint/541620/` → PDF
  `https://nora.nerc.ac.uk/id/eprint/541620/1/WMP_2020%20to%202024.pdf`
  (2.770.234 bytes, SHA-256
  `260a9891d28082990e49a75b97c386da1499af1ba59aad8743407c0c57aa55c6`),
  "First Published 2026", ISBN 978-0-85272-803-1.
- Frecuencia: anual; cada edición trae cinco años por país.
- Unidad: kilogramos de contenido de metal. Convención: producción de mina
  del año calendario; el BGS **incluye estimaciones de minería artesanal** y
  dice que por eso redondea más el total mundial (texto previo a la tabla).
- **Valores leídos** (página 37 del PDF, impresa 27, tabla "Mine production of
  gold", fila "World total", extraída con `pdftotext -raw`; la extracción con
  `-layout` mezcla columnas y no se usó para las cifras):

  | | 2020 | 2021 | 2022 | 2023 | 2024 |
  | --- | --- | --- | --- | --- | --- |
  | Mundo (kg) | 3200000 | 3200000 | 3300000 | 3300000 | 3300000 |
  | EE.UU. (kg) | 193000 | 187000 | 173000 | 170000 | 159000 (estimado) |

- **Contraste con el USGS.** 2024: BGS 3300 t contra USGS 3280 t (0.6 %, dentro
  del redondeo del BGS). Pero 2021: BGS 3200 contra USGS 3120 (2.6 %), y 2022:
  BGS 3300 contra USGS 3160 (4.4 %). Los dos compiladores no miden lo mismo:
  el BGS suma estimaciones artesanales que el USGS no declara. Para EE.UU. el
  BGS usa las cifras del USGS (coinciden en 2021 a 2023) con una estimación
  propia para 2024 (159 contra 163).
- Clave / registro: no.
- **Licencia: términos propios, restrictivos.** Página
  `https://www.bgs.ac.uk/mineralsuk/statistics/world-mineral-statistics/bgs-mineral-statistics-terms-and-conditions-ipr/`:
  el copyright es del NERC; **se permite adaptar y usar las tablas para fines
  académicos y de investigación no comerciales**; cualquier uso comercial, o
  entregarlas a un tercero, exige permiso (contacto `ipr@bgs.ac.uk`); y hay que
  mostrar el reconocimiento *"World Mineral Statistics contributed by
  permission of the British Geological Survey"*. El PDF agrega que las
  compilaciones no pueden reproducirse sin permiso del Director. Publicar la
  serie en un sitio público puede leerse como "entregarla a terceros": se trata
  como **(c) para publicar y válida para contrastar** (A-R0-12), y se pregunta
  (N0.13).
- La herramienta de datos del BGS (API OGC) cubre 1970 a 2021 y está en beta;
  no se usó. El archivo tiene PDF desde 1913.

#### N0.4.4 El stock sobre la superficie: World Gold Council — (c), ya citado; y lo que no existe

- La cifra del World Gold Council (222600 t a fin del segundo trimestre de
  2026) ya está en `data/series/citas_terceros.csv` como "estimación de
  terceros" (A-D0-28, leída el 2026-10-05, D0.9). Su serie anual pide cuenta y
  responde HTTP 403.
- Hoy se leyó además `https://www.gold.org/goldhub/data/gold-production-by-country`
  (producción minera anual por país desde 2010, "Updated annually, in
  conjunction with the publication of Metals Focus' Gold Focus report"): la
  página responde HTTP 200 y su xlsx
  (`/download/file/7593/Gold-Mining-Production-Volumes-Data-2025.xlsx`)
  responde **HTTP 403**. Clase (c), la lectura de 4.3.
- El USGS no publica existencias (D0.9): su página de preguntas frecuentes da
  "about 187,000 metric tons historically produced", sin fecha.
- **Conclusión:** no hay ninguna serie abierta del oro sobre la superficie. El
  stock y el stock-to-flow quedan **NO MEDIDO como serie**; se pueden mostrar
  como cifra citada de terceros, fuera de todo cálculo (A-D0-28). Con la cifra
  del WGC, 3300 / 222600 = 1.48 % y 222600 / 3300 = 67.5 (cálculo sobre una
  cifra de terceros, no un dato); con los 187000 t del USGS, 56.7. El "~60
  años" del sitio cae entre las dos, y las dos son estimaciones ajenas.

#### N0.4.5 Minerals Yearbook — no leído en este paso

- Los capítulos "Gold" y "Silver" del *Minerals Yearbook* (USGS, dominio
  público) traen la producción por país con uno o dos años más de rezago que
  los *Mineral Commodity Summaries*, y son la fuente de la *Data Series 140*.
  No se leyeron hoy: la *Data Series 140* ya cubre 1900–2022 y los *Summaries*
  2024–2025. Quedan para el paso 1 si hace falta el detalle por país o la
  revisión de 2023.

#### N0.4.6 Las anclas del sitio contra el USGS

| Año | `data.ts` (t) | USGS (t) | Fuente USGS |
| --- | --- | --- | --- |
| 1913 | 690 | 694 | DS140 |
| 1929 | 600 | 609 | DS140 |
| 1945 | 800 | 762 | DS140 |
| 1960 | 1050 | 1190 | DS140 |
| 1971 | 1250 | 1450 | DS140 |
| 1980 | 1220 | 1220 | DS140 |
| 1990 | 2180 | 2180 | DS140 |
| 2000 | 2590 | 2590 | DS140 |
| 2009 | 2600 | 2490 | DS140 |
| 2012 | 2860 | 2740 | DS140 |
| 2015 | 3100 | 3100 | DS140 |
| 2017 | 3300 | 3260 | DS140 |
| 2020 | 3200 | 3050 | DS140 |
| 2021 | 3560 | 3120 | DS140 |
| 2022 | 3612 | 3160 | DS140 |
| 2023 | 3644 | no leído (BGS: 3300) | — |
| 2024 | 3700 | 3280 | MCS 2026 |
| 2025 | 3500 | 3300 (estimado) | MCS 2026 |

Cuatro anclas coinciden con el USGS (1980, 1990, 2000, 2015); las de 2021 a
2025 están entre 6 % y 14 % por encima de lo que publica el USGS y no
coinciden tampoco con el BGS. No se sabe de dónde salen.

### N0.5 Plata

#### N0.5.1 USGS, *Mineral Commodity Summaries 2026*, capítulo "Silver" — leída, dominio público

- `https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-silver.pdf` (138.760
  bytes, SHA-256
  `f0dfe407304855a51f7647fc711f6c32081188a86269d011cd45e297aa673855`; los
  mismos bytes que en 4.6).
- Misma frecuencia, convención, unidad y licencia que N0.4.1.
- **Valores leídos** (texto, literal: *"World silver mine production increased
  slightly in 2025 to an estimated 26,000 tons compared with 25,300 tons in
  2024."*; tabla "Salient Statistics—United States", producción de mina):

  | | 2021 | 2022 | 2023 | 2024 | 2025 (estimado) |
  | --- | --- | --- | --- | --- | --- |
  | Mundo (redondeado) | | | | 25300 | 26000 |
  | EE.UU. | 1020 | 1010 | 1020 | 1050 | 1100 |

- **No es del todo independiente del Silver Institute:** la nota 8 del
  capítulo cita como fuente *"Metals Focus, 2025, World silver survey 2025:
  Silver Institute, prepared by Metals Focus"* (para la partida que lleva esa
  nota). Se declara al proponer el contraste (N0.11).

#### N0.5.2 USGS, *Data Series 140*, "Silver statistics", 1900–2021 — leída, dominio público

- `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-silver-2021.xlsx`
  (38.604 bytes, SHA-256
  `e57b952a5fd469291341bf275fbaa1c20dfd0caa9b40f383a2a19076efa9e997`),
  "Last modification: September 1, 2023".
- Columnas: producción de mina, primaria y secundaria de EE.UU., envíos,
  importaciones, exportaciones, existencias, consumo aparente, valor unitario
  (corriente y en dólares de 1998) y **producción mundial**.
- **Inicio real: 1900 = 5400 t.** Último: 2021 = 25000 t. 122 años.
- Valores leídos: 1913 = 7010, 1945 = 5040, 1980 = 10700, 2000 = 18100,
  2015 = 27600, 2020 = 24100, 2021 = 25000.
- Un año más corta que la del oro (2021 contra 2022).

#### N0.5.3 The Silver Institute, "Silver Supply & Demand" (Metals Focus) — leída, s/d, contraste

- `https://silverinstitute.org/silver-supply-demand/`, sección "Mine
  Production", literal: *"In 2024, global silver mine production rose by 0.9
  percent to 819.7 Moz"*. "Material and statistics in this section were adapted
  in part from the Silver Institute's World Silver Survey 2025."
- Unidad: millones de onzas troy. 819.7 Moz × 31.1034768 g = **25496 t**
  (cálculo propio), contra 25300 t del USGS: **0.77 %**.
- Licencia: s/d. El aviso legal (`https://silverinstitute.org/legal-disclaimer/`,
  releído hoy) solo trae un descargo y la propiedad de las marcas; no dice nada
  sobre reutilizar los datos. Es la misma lectura de 8.1. Aquí se transcribe
  una cifra, con su cita.
- El *World Silver Survey 2026* no se leyó (8.1 ya lo anotaba).

#### N0.5.4 British Geological Survey — leída, contraste

- Misma publicación de N0.4.3, página 74 del PDF (impresa 64), tabla "Mine
  production of silver", fila "World total", en kilogramos de contenido de
  metal (`pdftotext -raw`): 2020 = 26717000, 2021 = 26895000,
  2022 = 26945000, 2023 = 26754000, **2024 = 27815000**.
- Contra el USGS: 2024, 27815 contra 25300 t (**9.9 %**); 2021, 26895 contra
  25000 (7.6 %). La brecha es sistemática y mucho mayor que en el oro. No se
  leyó la explicación; las notas de la tabla hablan de producción de
  fundición o refinería en algunos países. **El BGS no sirve como gate de la
  plata**; se anota como contexto.

#### N0.5.5 El stock de plata

No se encontró ninguna fuente abierta de existencias de plata. El Silver
Institute menciona "above ground stocks" en su encuesta anual (clase s/d, PDF
no leído). **NO MEDIDO.**

### N0.6 Acciones: emisión neta en EE.UU. (Z.1)

#### N0.6.1 Junta de la Reserva Federal, *Financial Accounts of the United States* (Z.1), tablas F51.1 y D3 — leída, dominio público

- Publicación: `https://www.federalreserve.gov/releases/z1/`, "Release Date:
  September 11, 2026", datos a 2026:Q2. Trimestral; el calendario
  (`/releases/z1/release-dates.htm`) muestra una publicación por trimestre,
  unas diez semanas después del cierre.
- Descarga: paquete `https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip`
  (8.336.582 bytes, SHA-256
  `b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6`): un CSV
  por tabla (307 archivos) más un diccionario con la descripción de cada
  serie. El mapa de nombres `current/z1_table_mapping.csv` (9.737 bytes) dice
  que **F51.1 es la antigua F.224/L.224 "Corporate equities"** (la F.223 de hoy
  es "Direct investment intercompany debt": el número que daba el encargo ya no
  es el de acciones) y que F3 es la antigua F.208/L.208 "Debt securities".
  También existe el paquete completo `/releases/z1/data/FRB_Z1_csv.zip` y el
  programa de descarga (DDP); no se usaron.
- **Series** (diccionario del paquete, literal):

  | Serie | Descripción | Tabla | Unidad y convención |
  | --- | --- | --- | --- |
  | `FA893064105.Q` | All sectors; corporate equities; asset | F51.1.t, línea 1 ("Net issues" en el HTML) | Millions of dollars; transactions at a seasonally adjusted annual rate |
  | `FA103164105.Q` | Nonfinancial corporate business; corporate equities; liability | F51.1.t, línea 2 | ídem |
  | `FA793164105.Q` | Domestic financial sectors; corporate equities; liability | F51.1.t, línea 3 | ídem |
  | `LM893064105.Q` | All sectors; corporate equities; asset | F51.1.s, línea 1 | Millions of dollars; amounts outstanding end of period, market value, not seasonally adjusted |
  | `LM103164105.Q` | Nonfinancial corporate business; corporate equities; liability | F51.1.s, línea 2 | ídem |

  Los flujos sin ajuste estacional están en `F51_1_t_tu.csv` (prefijo `FU`).
- **Inicio real:** los flujos empiezan en **1946:Q4** (anuales hasta 1951,
  trimestrales desde 1952:Q1); los saldos en **1945:Q4**. 305 observaciones
  hasta 2026:Q2.
- **Muestra, contrastada con la tabla en HTML del mismo emisor**
  (`/releases/z1/current/html/F51_1_t.htm`): `FA893064105` 2026:Q2 = 2952979
  en el CSV y 2953.0 (miles de millones) en el HTML; anuales 2024 = 905.0 y
  2025 = 1163.8 en el HTML, 905 y 1164 sumando los cuatro trimestres del CSV
  y dividiendo por cuatro (cálculo propio). Igual. Es un contraste de
  transporte, no una segunda medición: el Z.1 tiene un solo compilador.
- **Lo que dicen los datos (cálculo propio: emisión neta del año sobre el
  valor de mercado de fin del año anterior):**

  | Año | Soc. no financieras, emisión neta (miles de millones) | Sobre el valor de mercado previo | Todos los sectores, emisión neta | Sobre el valor previo |
  | --- | --- | --- | --- | --- |
  | 2015 | −506 | −2.00 % | −95 | −0.26 % |
  | 2016 | −442 | −1.81 % | −108 | −0.30 % |
  | 2017 | −328 | −1.27 % | 217 | 0.55 % |
  | 2018 | −628 | −2.09 % | −216 | −0.46 % |
  | 2019 | −340 | −1.22 % | −194 | −0.45 % |
  | 2020 | −74 | −0.21 % | 781 | 1.46 % |
  | 2021 | −54 | −0.12 % | 920 | 1.44 % |
  | 2022 | −553 | −1.02 % | 236 | 0.30 % |
  | 2023 | −603 | −1.43 % | 34 | 0.05 % |
  | 2024 | −397 | −0.77 % | 905 | 1.18 % |
  | 2025 | −348 | −0.55 % | 1164 | 1.26 % |

  **En EE.UU. las sociedades no financieras retiraron acciones netas en los
  once años**: las recompras superaron a las emisiones. El total de todos los
  sectores (que suma financieras y acciones extranjeras compradas por
  residentes) fue positivo en siete de once años y nunca pasó de 1.5 % del
  valor de mercado. No es lo que dice la fila 3 de N0.0.
- **Lo que esta serie no mide.** Es un flujo en dólares a valor de transacción,
  no una cantidad de acciones: la "oferta" en unidades no existe en el Z.1. La
  tasa `emisión neta / valor de mercado` mezcla cantidades y precios. La serie
  se publica como lo que es ("emisión neta de acciones, EE.UU., en USD") y
  lo dice en su ficha.
- Cobertura: **solo EE.UU.** Una serie global de acciones en circulación no
  tiene fuente abierta: la WFE es (c) (D0.9). Se llama "EE.UU." y nada más.
- **Licencia: dominio público.** `https://www.federalreserve.gov/disclaimer.htm`,
  releída hoy, literal: *"Unless otherwise indicated, information on Board's
  website is in the public domain and may be copied and distributed without
  permission. Please cite to the Board as the source of the information."*
- Revisiones: cada publicación revisa la historia. Cada corrida guarda su
  descarga con SHA-256 y reporta los cambios (A-D0-26).

### N0.7 Bonos y deuda

#### N0.7.1 Z.1, tablas F3 (títulos de deuda) y D3 (deuda por sector) — leída, dominio público

- Mismo paquete, misma licencia y mismo contraste de transporte que N0.6.1
  (`/releases/z1/current/html/F3_s.htm`: `FL894122005` 2025:Q4 = 65485.7 en
  el HTML y 65485674 en el CSV).
- **Series** (diccionario, literal):

  | Serie | Descripción | Tabla | Unidad y convención |
  | --- | --- | --- | --- |
  | `FL894122005.Q` | All sectors; total debt securities; liability | F3.s, línea 1 | Millions of dollars; amounts outstanding end of period, not seasonally adjusted |
  | `FA894122005.Q` | All sectors; total debt securities; liability | F3.t, línea 1 | Millions of dollars; transactions at a seasonally adjusted annual rate |
  | `LA384104005.Q` | Domestic nonfinancial sectors; debt securities and loans; liability | D3.s, línea 1 | Millions of dollars; amounts outstanding end of period, seasonally adjusted |

- **Inicio real:** saldos desde **1945:Q4** (`FL894122005` = 248814;
  `LA384104005` = 352402); flujos desde 1946:Q4.
- **Lo que dicen los datos (cálculo propio, variación de fin de año a fin de
  año):**

  | Año | Títulos de deuda, todos los sectores (millones) | Variación | Deuda de sectores no financieros internos (millones) | Variación |
  | --- | --- | --- | --- | --- |
  | 2019 | 44282743 | 5.00 % | 55358189 | 4.74 % |
  | 2020 | 50509459 | 14.06 % | 62136630 | 12.24 % |
  | 2021 | 53986280 | 6.88 % | 66688878 | 7.33 % |
  | 2022 | 56049381 | 3.82 % | 70647649 | 5.94 % |
  | 2023 | 59214983 | 5.65 % | 74283380 | 5.15 % |
  | 2024 | 62105061 | 4.88 % | 77718783 | 4.62 % |
  | 2025 | 65485674 | 5.44 % | 81810789 | 5.27 % |

  Entre 3.8 % y 14.1 % en siete años; 5.4 % en 2025. La fila 2 de N0.0 dice
  "7-15 %" para "Cash / Bonos" sin decir de qué país ni de qué agregado.
- "Total debt securities" incluye los títulos emitidos por el resto del mundo
  en manos de residentes; el Z.1 no publica en F3 una fila solo de emisores
  residentes. Cobertura: EE.UU.

#### N0.7.2 BIS, *Debt securities statistics* (`WS_NA_SEC_DSS`) — leída, (a), contraste y suma de economías

- Consulta: `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_NA_SEC_DSS/1.0/all?c[REF_AREA]=US&format=csv`
  (20.987.658 bytes, SHA-256
  `6c979607d5266388d6b1d015953a4a5766eae75b0bc3bbdec3937fffff38b9de`; 84207
  filas, 291 series de EE.UU.). Sin clave.
- Series de EE.UU. que importan (clave SDMX y título del BIS, literal):
  - `Q.N.US.XW.S1.S1.N.L.LE.F3.T._Z.USD._T.N.V.N._T`: *"United States - Debt
    sec, issued by residents, all markets, all original maturities, all
    currencies, nominal value, stocks"*: **2025-Q4 = 61130.116** miles de
    millones de USD. Es la cifra que D0.9 ya había leído.
  - La misma a valor de mercado (`...M.V.N._T`): 2025-Q4 = 58807.766.
- Contra el Z.1 (`FL894122005` 2025:Q4 = 65485.674 miles de millones): el BIS
  queda **6.65 % por debajo** a valor nominal. No es un error: el BIS cuenta
  solo emisores residentes y el Z.1 suma los del resto del mundo. **No sirve
  como gate de igualdad**; sirve como comparación declarada.
- Trimestral desde 1952-Q1 (vista en la primera fila de la descarga), con
  rezago de dos trimestres (D0.9).
- La suma de las 49 economías declarantes es la de A-D0-22, ya propuesta y NO
  MEDIDA en D0; no se repite aquí.
- **Licencia: (a).** `https://data.bis.org/help/legal`, "Terms of permitted use
  of BIS statistics", releída hoy: uso sin restricciones si se cita al BIS como
  fuente, no se sugiere su respaldo y, en un producto comercial, no se cobra un
  cargo adicional por incluirlas (paráfrasis; el texto es del BIS).

### N0.8 Inmuebles: el parque de viviendas de EE.UU. (Censo)

#### N0.8.1 Census Bureau, *Housing Vacancies and Homeownership* (CPS/HVS), Tabla 7 — leída, dominio público

- `https://www.census.gov/housing/hvs/data/histtabs.html` → Tabla 7,
  `https://www.census.gov/housing/hvs/data/histtab7.xlsx` (32.041 bytes,
  SHA-256 `335592c7de815c450495abeeea8a0d64d333e4760109a5b04b5eca4ee5ca8ebc`),
  "Table 7. Estimates of the Total Housing Inventory for the United States:
  1965 to Present", "Source: U.S. Census Bureau, Current Population
  Survey/Housing Vacancy Survey, March 24, 2026".
- Frecuencia: anual. Convención: promedio de las estimaciones mensuales del
  año; **2025 promedia 11 meses** (nota literal: *"Due to a lapse in federal
  funding, the Current Population Survey/Housing Vacancy Survey (CPS/HVS) did
  not collect data for the month of October 2025. The Annual 2025 estimates
  are based on the remaining 11 months of data."*).
- Unidad: miles de viviendas ("All housing units").
- **Inicio real: 1965 = 64213.** Último: 2024 = 146835; 2025 = 148086.
- **Quiebres declarados por la fuente:** columnas revisadas 1979r1 (cambios de
  1980), 1981r2, 1989r3 (incluye casas móviles vacantes), 1993r4 (Censo de
  1990), 2002r5 (Censo de 2000); 1986 y 1987 con notas sobre vacantes
  estacionales. Cada revisión aparece como una columna doble: la serie no
  está empalmada por el Censo.
- **Tabla 7a** (`hist_tab_7a_v2025.xlsx`, 35.983 bytes, SHA-256
  `3777bf395606d5564c2fce3447f5e757f0628ce59354df057db0e0bcbc3338b2`): el
  mismo inventario 2000–2025 **revisado con los controles de vivienda de las
  vintages 2010, 2020 y 2025** (Population Estimates). Difiere de la Tabla 7:
  2024 = 146770 contra 146835; 2025 = 148163 contra 148086. Son dos series del
  mismo emisor con distinta base; no se mezclan.
- Clave / registro: no.
- **Licencia: dominio público por ley.** En las páginas del Censo leídas
  (políticas, citas, términos de la API) no se encontró una cláusula propia
  sobre reutilizar los archivos. Lo que rige es 17 U.S.C. § 105(a), leído en
  `https://www.law.cornell.edu/uscode/text/17/105`, literal: *"Copyright
  protection under this title is not available for any work of the United
  States Government"*. La página de citas del Censo
  (`/about/policies/citation.html`) da el formato de cita, que se usará. Los
  términos de la API (`/data/developers/about/terms-of-service.html`) exigen un
  aviso ("This product uses the Census Bureau Data API but is not endorsed or
  certified by the Census Bureau") **solo para quien use la API**; aquí no se
  usa.

#### N0.8.2 Census Bureau, Population Estimates, viviendas 2020–2025 (`NST-EST2025-HU`) — leída, dominio público

- `https://www2.census.gov/programs-surveys/popest/tables/2020-2025/housing/totals/NST-EST2025-HU.xlsx`
  (16.894 bytes, SHA-256
  `a1ff31e0dc318bb00e4ac546dbba45601adb17ab56f31893e01fc29b072f94a8`),
  "Annual Estimates of Housing Units for the United States, Regions, States,
  and the District of Columbia: April 1, 2020 to July 1, 2025", "Release Date:
  May 2026".
- Frecuencia: anual. Convención: **existencias al 1 de julio**, estimadas
  desde la base del Censo de 2020 con permisos de construcción, pérdidas y
  registros administrativos. Unidad: viviendas (unidades).
- Valores leídos: base 2020-04-01 = 140498736; 2020 = 140817690;
  2021 = 142193055; 2022 = 143831409; 2023 = 145398445; 2024 = 146829273;
  **2025 = 148260882**.
- Inicio real de esta vintage: 2020. Las vintages anteriores (2010–2019,
  2000–2009) están en otras tablas, no leídas; cada vintage reexpresa su
  década.
- Es la fuente de los "controles" de la Tabla 7a: no son independientes.

#### N0.8.3 FRED `ETOTALUSQ176N` — leída, contraste de transporte

- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=ETOTALUSQ176N`
  (1.921 bytes): "Housing Inventory Estimate: Total Housing Units in the United
  States", trimestral, miles, 2000-Q2 = 116047 a **2026-Q2 = 149454**; 105
  observaciones. Es el HVS trimestral reempaquetado; emisor original: el
  Censo.
- 2025-Q3 = 148300 contra 148260.882 del 1 de julio (Population Estimates):
  0.03 %.

#### N0.8.4 Lo que dicen los datos (cálculo propio)

| Año | Tabla 7 | Tabla 7a | Population Estimates (1 de julio) |
| --- | --- | --- | --- |
| 2020 | 0.83 % | 0.90 % | — |
| 2021 | 0.81 % | 0.99 % | 0.98 % |
| 2022 | 1.06 % | 1.12 % | 1.15 % |
| 2023 | 1.33 % | 1.09 % | 1.09 % |
| 2024 | 1.02 % | 1.00 % | 0.98 % |
| 2025 | 0.85 % | 0.95 % | 0.98 % |

Tasa compuesta 1965–2025 (Tabla 7): 1.40 % anual; 2000–2025 (Tabla 7a):
0.98 %. **Entre 0.8 % y 1.3 % por año en 2020–2025, no "2-3 %".** Cobertura:
solo EE.UU. "Global housing units" (fila 15 de N0.0) no tiene fuente abierta
leída: UN-Habitat no se leyó. Si se publica, la serie se llama "parque de
viviendas de EE.UU." y nada más.

### N0.9 Dinero

El crecimiento del M2 de EE.UU. (y de la Eurozona y Japón) ya se publica en
D0 con su variación interanual. No se duplica. La fila 2 de N0.0 ("Cash /
Bonos, 7-15 % anual") mezcla el dinero con los bonos; lo que N0 puede decir de
los bonos está en N0.7, y lo del dinero en D0.

### N0.10 Decisiones propuestas

**Ninguna está tomada.**

#### N0.10.1 Por activo: qué se puede medir, con qué cobertura y desde cuándo

| Activo | Serie propuesta | Qué mide | Cobertura | Desde | Fuente | Licencia | Estado propuesto |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BTC | Emisión anual del calendario | Flujo que el protocolo permite, por bloques observados del año | Red principal | 2009 | Bitcoin Core (subsidio) × Coin Metrics `BlkCnt` | MIT / CC BY-NC | dato |
| BTC | Oferta observada y su tasa de crecimiento | Stock a fin de año (`SplyCur`) y `stock_t / stock_{t-1} - 1` | Red principal | 2009 | Coin Metrics `SplyCur` | CC BY-NC | dato; **reemplaza "0 %"** |
| BTC | Elasticidad | Cero por construcción | — | — | Bitcoin Core | MIT | dato del protocolo, no estimación |
| Oro | Producción minera mundial anual | Flujo | Mundo | 1900 | USGS DS140 (1900–2022) + MCS (2023 en adelante, con el último año estimado) | dominio público | dato |
| Oro | Stock sobre la superficie y stock-to-flow | Acervo | — | — | WGC (c), USGS (sin fecha) | — | **NO MEDIDO como serie**; cifra de terceros (A-D0-28) |
| Oro | Tasa de crecimiento del stock | Flujo / acervo | — | — | — | — | NO MEDIDO (sin acervo abierto) |
| Plata | Producción minera mundial anual | Flujo | Mundo | 1900 | USGS DS140 (1900–2021) + MCS | dominio público | dato |
| Plata | Stock | Acervo | — | — | — | — | NO MEDIDO |
| Acciones | Emisión neta de acciones, EE.UU., en USD | Flujo en dólares (no en acciones) | EE.UU. | 1946 (anual), 1952 (trimestral) | Z.1 `FA103164105` y `FA893064105` | dominio público | dato, con su limitación declarada |
| Acciones | Valor de mercado, EE.UU. | Acervo a valor de mercado | EE.UU. | 1945:Q4 | Z.1 `LM893064105`, `LM103164105` | dominio público | dato (contexto del flujo) |
| Acciones | Acciones en circulación o emisión global | — | Mundo | — | WFE (c) | — | NO MEDIDO |
| Bonos | Títulos de deuda en circulación, EE.UU., y su variación | Acervo y tasa | EE.UU. | 1945:Q4 | Z.1 `FL894122005` | dominio público | dato |
| Bonos | Deuda de sectores no financieros internos, EE.UU. | Acervo | EE.UU. | 1945:Q4 | Z.1 `LA384104005` | dominio público | dato |
| Bonos | Suma de 49 economías | Acervo | 49 economías | 2020-Q4 (panel fijo) | BIS | (a) | lo que ya dice A-D0-22 |
| Inmuebles | Parque de viviendas de EE.UU., HVS Tabla 7 | Acervo, promedio anual | EE.UU. | 1965 | Censo | dominio público | dato, con sus revisiones declaradas |
| Inmuebles | Parque de viviendas, Population Estimates | Acervo al 1 de julio | EE.UU. | 2020 (esta vintage) | Censo | dominio público | dato (contexto); vintages anteriores por leer |
| Inmuebles | Viviendas globales | — | Mundo | — | UN-Habitat (no leído) | — | NO MEDIDO |
| Dinero | M2 | — | — | — | D0 | — | ya publicado en D0; no se duplica |

**Lo que se propone que diga cada nombre:** "EE.UU." donde la cobertura es
EE.UU.; "mundo" solo para la producción minera del USGS, que así lo declara;
"49 economías" para el BIS. Ningún nombre dice "global".

#### N0.10.2 Elasticidad: estimar o NO MEDIDO

Dos opciones, para que elija el dueño. **Recomendación: la B ahora, y la A
como un paso aparte (N1), si se quiere.**

- **Opción A: estimar, solo para oro y plata**, que son los únicos activos con
  flujo y precio anuales abiertos y largos (USGS DS140, 1900–2022: producción
  mundial y valor unitario en dólares de 1998; o el Pink Sheet desde 1960 para
  el precio, sección 4.5). Método fijado aquí, antes de calcular, y sin
  retoques después:
  - Regresión por mínimos cuadrados de `Δln(producción_t)` sobre
    `Δln(precio real_{t-k})`, con `k` de 0 a 5, todos los rezagos en la misma
    ecuación, con constante y errores robustos a autocorrelación.
  - Se publican los seis coeficientes y su suma, cada uno con su intervalo del
    95 %, en dos submuestras fijadas ahora: 1900–2022 y 1971–2022.
  - La serie se rotula "elasticidad estimada (cálculo propio)", con
    `apto_metricas = no`, y si el intervalo incluye el cero se dice así.
  - Para inmuebles haría falta un índice de precios abierto (el de la FHFA es
    candidato; no se leyó) y queda para después. Para acciones y bonos la
    "oferta" del Z.1 está en dólares: no hay forma de separar cantidad de
    precio, y la elasticidad queda **NO MEDIDO**. Para BTC es cero por
    construcción (dato).
- **Opción B: NO MEDIDO para todos** salvo BTC (cero por construcción). El
  sitio publica tasas de crecimiento observadas y deja de hablar de
  elasticidades hasta que exista una estimación aprobada.

#### N0.10.3 Frecuencia y convención

- **Frecuencia: anual** para toda la familia. El USGS y el HVS son anuales;
  BTC se suma por año calendario; el Z.1 se toma a fin de año (y queda
  disponible trimestral para quien lo quiera, sin ratio contra nada).
- **Convención de cada serie, en su ficha:** BTC, stock al 31 de diciembre
  (00:00 UTC del 1 de enero); USGS, producción del año calendario; HVS,
  promedio de meses del año (11 meses en 2025); Population Estimates, 1 de
  julio; Z.1, saldo de fin de período (flujos: suma de los cuatro trimestres
  a tasa anual, dividida por cuatro).
- **La tasa de crecimiento** es siempre `stock_t / stock_{t-1} - 1` con la
  convención de la serie; donde solo hay flujo (oro, plata) no se publica
  tasa.
- Ninguna de estas series entra a un ratio contra precio ni contra M2 en este
  paso.

#### N0.10.4 Afirmación actual del sitio → lo que dicen las fuentes → estado propuesto

| Afirmación (N0.0) | Lo que dicen las fuentes leídas | Estado propuesto |
| --- | --- | --- |
| 1, 5: "Oro, 1.5 %" anual | USGS: producción 3280 t (2024) y 3300 t (2025, estimado). No hay stock abierto. Con la cifra de terceros del WGC, 3300 / 222600 = 1.48 %; no es un dato | Publicar la producción (dato). La tasa de crecimiento del stock, NO MEDIDO; mostrar el 1.48 % solo como cálculo sobre una cifra de terceros, fuera de las métricas |
| 5, 10: stock-to-flow "~60 años" / 61.4; proyección a 2050 | 222600 / 3300 = 67.5 con el WGC; 187000 / 3300 = 56.7 con el USGS (sin fecha). La producción cayendo 1 % anual no tiene fuente | NO MEDIDO como serie; sin proyección |
| 9: producción de oro de `data.ts` | Difiere del USGS en 14 de 18 anclas; 2021–2025 entre 6 % y 14 % por encima | Reemplazar por el USGS |
| 1, 3: "Acciones, 3-5 % anual"; "la emisión neta global es positiva" | Z.1, EE.UU.: emisión neta de las sociedades no financieras negativa en 2015–2025 (−0.12 % a −2.09 % del valor de mercado previo); todos los sectores, entre −0.46 % y +1.46 %. Global: sin fuente abierta | Publicar la serie de EE.UU. en USD, con su limitación; global, NO MEDIDO |
| 14: "Global shares outstanding", "Companies listed" | Sin fuente abierta (WFE, (c)) | NO MEDIDO |
| 1, 4: "Inmuebles, 2-3 %" | Censo, EE.UU.: 0.8 % a 1.3 % por año en 2020–2025; 1.40 % compuesto 1965–2025 | Publicar el parque de EE.UU. (dato); global, NO MEDIDO |
| 15: "Global housing units" 250 → 1900 millones | Sin fuente leída (UN-Habitat no leído). EE.UU. 2025: 148.1 millones (HVS) o 148.3 millones (1 de julio) | NO MEDIDO |
| 2: "Cash / Bonos, 7-15 % anual"; 1: "al ritmo de la impresora" | Z.1, EE.UU.: títulos de deuda +3.8 % a +14.1 % por año en 2019–2025 (+5.4 % en 2025); deuda no financiera +4.6 % a +12.2 %. Dinero: D0 | Publicar las dos series del Z.1 (dato); el dinero se queda en D0 |
| 16: "Global debt outstanding" 145 billones (2024) | BIS, suma propia de 49 economías: 145068 miles de millones a 2024-Q4 (D0.9); EE.UU. (Z.1): 62105 | Lo de A-D0-22; nunca "global" |
| 6: "Bitcoin, 0 %", "Supply fijo", "converger a cero" | Coin Metrics: +1.112 % en 2024, +0.838 % en 2025; 165881.25 BTC emitidos en 2025; el calendario sigue positivo hasta más allá de 2100 | Publicar la emisión anual y la tasa observada (dato); "0 %" se reemplaza; la elasticidad es cero por construcción (dato del protocolo) |
| 7: "21 millones", "cada 210,000 bloques" | `MAX_MONEY = 21'000'000 * COIN`; `nSubsidyHalvingInterval = 210000` | dato |
| 13: "94,4 %" minado | Oferta al 2025-12-31: 19969701.16 BTC = 95.09 % de 21 millones; al 2026-10-06: 20094435.50 = 95.69 % | dato observado, con fecha |
| 8: "Cuando el precio sube, no se produce más Bitcoin" | El subsidio es función de la altura (N0.3.1) | dato; se enuncia como elasticidad cero por construcción |
| 11: elasticidad = tasa de crecimiento | Son dos magnitudes distintas (N0.2) | Corregir el texto; A-N0-1 |
| 12: `elasticity_*` a 10 años | No es una estimación (sin rezago, sobre anclas interpoladas) | NO MEDIDO hasta que se apruebe un método (N0.10.2) |
| 17: múltiplos del S&P 500, del denominador y del oro | Precio y M2 | Fuera de N0; fases R y D0 |

#### N0.10.5 Lo que decidió el dueño (2026-10-07)

Aprobó N0 con estas decisiones; rigen sobre las propuestas de N0.10.1 a
N0.10.4 donde difieren.

1. **Expansión neta de la oferta (dato) para todos los activos medibles.**
   BTC: emisión del año según el protocolo, sobre la oferta en circulación
   observada. Acciones de EE.UU.: emisión neta en monto y como porcentaje del
   valor de mercado, por sector y total (Z.1, F51.1), sin interpretar. Bonos
   de EE.UU.: variación anual del stock de títulos de deuda (Z.1). Viviendas
   de EE.UU.: variación anual del parque (Censo). **Frecuencia anual.**
   Acciones, bonos y viviendas se llaman "de EE.UU." en todas partes.
2. **BTC.** El calendario del protocolo es el dato; la oferta observada de
   Coin Metrics es el gate, con la tolerancia fijada antes de comparar. Se
   publica también el porcentaje minado a la fecha.
3. **Oro y plata.** Producción minera anual en toneladas, con el USGS como
   fuente principal (MCS y *Data Series 140*). El BGS es control de
   consistencia contra el USGS (marca, no bloquea), con tolerancia fijada
   antes de comparar; la diferencia por minería artesanal se declara en la
   ficha. **Cota superior de la tasa de crecimiento del stock** = producción
   del año / producción acumulada desde 1900 (USGS DS140), con estado
   "estimación" y el supuesto declarado (pérdidas despreciables; en plata,
   declarar que el consumo industrial la hace menos informativa). Nunca se
   presenta como la tasa real. El stock sobre tierra va solo como cifra
   citada de terceros, fuera de todo cálculo.
4. **Elasticidad, en dos niveles.** BTC: cero por construcción (la emisión
   depende de la altura del bloque, no del precio); dato. Deuda de EE.UU.:
   NO MEDIDO (no tiene un precio comparable). Oro, plata, viviendas de EE.UU.
   y acciones de EE.UU.: nueva familia "respuesta observada de la oferta al
   precio", estado "estimación" (punto 5).
5. **Respuesta observada de la oferta al precio.** Antes de descargar o
   cruzar precios, se prerregistra en `SUPUESTOS.md` la especificación
   completa (variables, deflactor, rezagos de 0 a 5 años, ventana, método,
   cómo se reportan los intervalos y qué resultado se leería como "responde"
   o "no responde"), en un commit propio **antes** de calcular. Pares: oro y
   plata (producción contra precio real), viviendas de EE.UU. (construcción
   contra el índice de precios de la FHFA; el Case-Shiller tiene licencia de
   S&P y queda fuera) y acciones de EE.UU. (emisión neta contra valuación).
   Rótulo fijo: "asociación observada, no elasticidad causal: precio y
   cantidad se determinan juntos". Intervalos, no un número único. Si alguna
   fuente necesaria (FHFA, deflactor, valuación) no está verificada en N0,
   primero un paso 0 corto para ella, con parada para mostrarla.
6. **Tabla en el PR:** "afirmación actual del sitio (lista N0.0) → dato o
   estimación → estado", sin interpretar.

Y el encargo del paso 1: `numerador.py`, gates y tolerancias fijados antes
de comparar, tests sin red, `test_salidas_publicadas`, supuestos A-N0-\*,
changelog y README; commits pequeños y PR sin merge.

### N0.11 Validación propuesta

> **Lo que cambió al implementar (paso 1, 2026-10-07): ver N0.15.** El gate de
> viviendas pasó a ser la identidad de la propia tabla y FRED quedó como
> control; la Tabla 7a no cerró y queda NO MEDIDO.

Con la regla de `CLAUDE.md`: una segunda fuente por serie y una tolerancia
escrita antes de ver el resultado. **Advertencia, como en D0.11:** el paso 0
exige contrastar una muestra, así que varios resultados ya están a la vista.
Donde la tolerancia sale de la precisión publicada ("por construcción") se
dice; donde se fija con el resultado conocido, también.

| Serie | Fuente | Segunda fuente | Clase | Tolerancia propuesta | Cómo se fijó |
| --- | --- | --- | --- | --- | --- |
| BTC, oferta observada | Coin Metrics `SplyCur` | Calendario del protocolo a la misma altura (`BlkCnt` acumulado) | Gate | `SplyCur` nunca mayor que el calendario, y calendario − `SplyCur` ≤ 0.001 % del calendario | **Con el resultado a la vista:** la diferencia es −80 BTC (−0.0004 %) al 2026-10-06. Lo que no depende del resultado es el signo |
| BTC, oferta observada | Coin Metrics `SplyCur` | blockchain.com `q/totalbc`, a igual altura | Control | Por fijar en el paso 1, antes de comparar a igual altura | La comparación de hoy fue a alturas distintas (103 bloques) y no sirve para fijarla |
| BTC, emisión anual | Suma de `IssTotNtv` | Subsidio × `BlkCnt` del año | Gate | Igualdad en 2025; en años con bloques que reclamaron menos, `IssTotNtv` ≤ subsidio × bloques | Por construcción |
| Oro, producción mundial | USGS (DS140 y MCS) | BGS, total mundial | Control | ±5 % | **Con el resultado a la vista:** 0.6 % (2024), 2.6 % (2021), 4.4 % (2022). ±50 t (medio redondeo del BGS) habría sido "por construcción" y falla en 2021 y 2022: los dos compiladores no miden lo mismo (artesanal). Por eso es control, no gate |
| Oro, producción mundial | USGS MCS (último año) | USGS DS140 o MCS siguiente (revisión) | Control de revisión | Se reporta la diferencia; sin tolerancia que decida | — |
| Plata, producción mundial | USGS | Silver Institute (Metals Focus), convertido de Moz | Control | ±2 % | **Con el resultado a la vista:** 0.77 % (2024). Y no son independientes del todo (nota 8 del USGS) |
| Plata, producción mundial | USGS | BGS | Contexto | Sin tolerancia; se publica la diferencia (9.9 % en 2024) | — |
| Acciones y bonos (Z.1) | CSV del paquete | Tabla en HTML del mismo emisor, mismos trimestres | Gate de transporte | Igualdad a 0.1 miles de millones (el HTML redondea a un decimal) | Por construcción |
| Acciones y bonos (Z.1) | CSV del paquete | FRED (`BOGZ1…`), mismo emisor | Control | Igualdad | Por construcción; **FRED no se leyó en este paso** |
| Bonos (Z.1) | `FL894122005` | BIS, emisores residentes, nominal | Comparación declarada | Sin tolerancia; se publica la diferencia (−6.65 % en 2025-Q4) y su causa | Conceptos distintos |
| Viviendas, HVS Tabla 7a | xlsx del Censo | FRED `ETOTALUSQ176N`, promedio de los cuatro trimestres del año | Gate de transporte | ±0.5 mil (redondeo a miles) | Por construcción; **no se comparó todavía** |
| Viviendas, HVS Tabla 7 | xlsx del Censo | Tabla 7a | Comparación declarada | Sin tolerancia; se publican las dos series y su diferencia | Dos bases distintas por decisión del Censo |
| Viviendas | HVS (promedio anual) | Population Estimates (1 de julio) | Control | ±0.5 % | **Con el resultado a la vista:** −0.07 % y −0.12 % en 2025. Conceptos distintos (promedio contra 1 de julio) |

- **Mínimo de comparaciones: tres**, como en A-R0-16 y A-D0-25. Un gate que no
  cierra deja la serie como "NO MEDIDO: sin validación externa"; un control
  marca el año como valor en disputa y no decide.
- **Sin segunda fuente independiente:** acciones (Z.1 es el único compilador;
  el HTML y FRED son el mismo dato), y el parque de viviendas (la Tabla 7a y
  Population Estimates comparten los controles). Las fichas lo dicen.
- **Revisiones:** cada corrida guarda su descarga con SHA-256 y reporta los
  cambios en años ya publicados (A-D0-26). El Z.1 y el MCS revisan siempre el
  último año.

### N0.12 Supuestos A-N0-\* propuestos

Ninguno está escrito en `SUPUESTOS.md` todavía. Si se aprueban, van allí con
estos números.

| N.º | Qué fija | Estado propuesto |
| --- | --- | --- |
| A-N0-1 | Tasa de crecimiento de la oferta y elasticidad son magnitudes distintas; cada serie declara cuál mide y el sitio no usa una por la otra | supuesto |
| A-N0-2 | BTC: la emisión anual sale del calendario del protocolo por los bloques observados del año y se contrasta con `SplyCur`; la tasa de crecimiento publicada es la observada (0.838 % en 2025), no "0 %"; la elasticidad es cero por construcción | dato |
| A-N0-3 | Oro y plata: la producción minera mundial es la del USGS (DS140 y MCS); el último año es estimado y se marca; el stock y el stock-to-flow quedan NO MEDIDO como serie y solo se citan como cifra de terceros (A-D0-28) | dato la producción; no medido el stock |
| A-N0-4 | Acciones: emisión neta en USD de EE.UU. (Z.1), rotulada así, con su limitación (dólares, no acciones); global NO MEDIDO | dato con limitación; no medido global |
| A-N0-5 | Bonos: títulos de deuda y deuda no financiera de EE.UU. (Z.1); la suma del BIS es la de A-D0-22 | dato |
| A-N0-6 | Inmuebles: parque de viviendas de EE.UU. (HVS Tabla 7, con sus revisiones como columnas, y Tabla 7a aparte); Population Estimates como contexto; global NO MEDIDO | dato; no medido global |
| A-N0-7 | Frecuencia anual y convención por serie (N0.10.3); ninguna serie de N0 entra a un ratio en este paso | supuesto |
| A-N0-8 | Elasticidad: la opción que elija el dueño en N0.10.2; si es A, el método, los rezagos (0 a 5) y las submuestras (1900–2022 y 1971–2022) quedan fijados antes de calcular | supuesto (A) o no medido (B) |
| A-N0-9 | Las tolerancias de N0.11; las que se fijaron con el resultado a la vista lo declaran | supuesto |
| A-N0-10 | BGS y blockchain.com son fuentes de contraste, no de publicación (términos restrictivos); el `robots.txt` de nora.nerc.ac.uk se leyó después de la descarga y se declara | supuesto de licencia |
| A-N0-11 | Crudos: se versionan en `data/raw/` los del USGS (dos PDF y dos xlsx), los del Censo (tres xlsx), los CSV de las tablas usadas del Z.1 (no el ZIP de 8.3 MB, que supera el tope de A-D0-27 y se registra por hash) y la descarga de Coin Metrics (CC BY-NC); el CSV del BIS (21 MB), el PDF del BGS y las respuestas de blockchain.com van a `data/privado/` con URL, fecha y SHA-256 | supuesto |
| A-N0-12 | Ningún nombre de serie dice "global"; dice "EE.UU.", "mundo" (solo el USGS) o "49 economías" | supuesto |

### N0.13 Permisos, avisos y preguntas

Ninguno se envió.

1. **BGS (`ipr@bgs.ac.uk`):** si citar los totales mundiales de oro y plata
   en un sitio público de investigación sin ingresos cuenta como "provide them
   to a third party", y si basta el reconocimiento que piden. Destraba usar al
   BGS como gate publicado y no solo como contraste privado.
2. **World Gold Council:** permiso para la serie anual de existencias sobre la
   superficie (hoy detrás de una cuenta y con términos de uso personal).
   Destraba el stock y el stock-to-flow del oro.
3. **Silver Institute:** si sus cifras de producción minera pueden citarse
   como serie (su aviso legal no lo dice).
4. **Nada que pedir** a la Junta, al USGS ni al Censo (dominio público), ni a
   Coin Metrics (CC BY-NC, con la condición de A-R0-4).

### N0.14 Lo que sigue abierto

- **Los *Minerals Yearbook* de oro y plata** (detalle por país, revisión de
  2023) no se leyeron; el MCS 2025 tampoco (para ver cuánto revisa el MCS 2026).
- **FRED como espejo del Z.1** (`BOGZ1…`) y del HVS trimestral: leído solo el
  HVS; el control de N0.11 para el Z.1 queda por hacer.
- **UN-Habitat** (viviendas globales) y **la WFE** (acciones listadas) no se
  leyeron; la segunda ya es (c) por D0.9.
- **Un índice de precios de vivienda abierto** (FHFA) para una eventual
  elasticidad de los inmuebles: no leído.
- **El método de blockchain.com** para `q/totalbc`: no leído; su cifra no
  coincide con la suma de salidas no gastadas ni con el calendario exacto.
- **La reconciliación exacta** entre `SplyCur` y el calendario (qué bloques
  reclamaron menos, qué salidas no cuentan) queda para el paso 1; hoy solo se
  sabe que la diferencia es negativa y de −80 BTC.
- **Las vintages anteriores de Population Estimates** (2000–2009, 2010–2019)
  para alargar esa serie hacia atrás.
- **El historial del sitio:** las frases que el encargo citó y no están en
  `master` (N0.0) podrían estar en un commit anterior; no se buscó.

### N0.15 Lo que encontró el paso 1 (2026-10-07)

El paso 1 (`numerador.py`, `fuentes_numerador.py`, el bloque N0 de
`configuracion.py` y sus tests) se corrió el 2026-10-07 con los crudos de ese
día. Lo que cambió respecto de la propuesta de N0.11, con el porqué, y lo que
se leyó de más.

**Lo que se leyó de más** (mismos hosts que N0.1, salvo que se diga; cada
descarga quedó en el registro de `data/privado/n0_paso0/`):

| Fuente | Qué | Resultado |
| --- | --- | --- |
| pubs.usgs.gov | *Mineral Commodity Summaries* 2024 y 2025, capítulos de oro y plata (`mcs2024-gold.pdf`, 743.608 bytes, SHA-256 `3b551dcc…`; `mcs2024-silver.pdf`, 808.370, `7c74bb6f…`; `mcs2025-gold.pdf`, 743.291, `d4ec1750…`; `mcs2025-silver.pdf`, 744.783, `1aa6e68c…`) | Fila "World total (rounded)" leída con `pdftotext -raw` y cotejada con la frase del texto: oro 2022 = 3060 y 2023e = 3000 (MCS 2024), 2023 = 3250 y 2024e = 3300 (MCS 2025); plata 2022 = 25600 y 2023e = 26000 (MCS 2024), 2023 = 25500 y 2024e = 25000 (MCS 2025). Con el MCS 2026 (N0.4.1, N0.5.1) completan 2022 a 2025 |
| www.federalreserve.gov | Las tablas F51.1.s y D3.s en HTML (`F51_1_s.htm`, 159.833 bytes, SHA-256 `0b91363c…`; `D3_s.htm`, 102.357, `dbdd070b…`) | Gate de transporte de las dos series que faltaban. La D3.s viene traspuesta (períodos como filas) y con los `<th>` de los mnemónicos fuera de su `<tr>`; el lector toma el orden de los enlaces "SeriesAnalyzer" |
| fred.stlouisfed.org | `https://fred.stlouisfed.org/data/ETOTALUSQ176N.txt` (las notas de la serie) | Respondió una página HTML, no el texto. No se usó |

**Las revisiones del USGS entre ediciones.** La *Data Series 140* dice 3160 t
de oro en 2022 y el MCS 2024 dice 3060; el MCS 2024 estimó 3000 para 2023 y el
MCS 2025 publicó 3250; el MCS 2025 estimó 3300 para 2024 y el MCS 2026 publicó
3280. En plata, 26000 estimado y 25500 final para 2023, 25000 estimado y
25300 final para 2024. La serie toma la DS140 en todo su rango y después cada
año de la edición más reciente que lo publica como final; nada se corrige y
cada fila lleva la nota (A-N0-3).

**Lo que cambió respecto de N0.11:**

1. **El gate de viviendas no es FRED: es la identidad de la propia tabla.**
   Antes de correr, la comparación de la Tabla 7a con la media de los cuatro
   trimestres de FRED mostró diferencias de hasta 3.75 mil en 2001–2019 (en
   siete años más que el redondeo de ±1 mil), y de 5 a 58 mil desde 2020 (la
   Tabla 7a está en la Vintage 2025 y FRED no). FRED no reproduce los promedios
   de la Tabla 7a y no se sabe por qué. Se fijó entonces, antes de correr, un
   gate de transporte por construcción: "All housing units" = "Vacant" +
   "Total occupied" en cada columna, ±1.5 mil (tres cifras redondeadas a
   miles), y FRED pasó a control. La clase de FRED se decidió con ese resultado
   a la vista, y queda dicho (A-N0-11).
2. **La Tabla 7a no cerró su gate y queda NO MEDIDO.** En 2017 el total
   (137221) difiere en 2 mil de la suma de vacantes (17381) y ocupadas
   (119842); en 2016 difiere 1 y en 2018, 0. La Tabla 7 cerró en sus 66
   columnas (máxima 1.0). La tolerancia no se tocó. Si el dueño prefiere que
   esa identidad sea un control, es un cambio de supuesto (A-N0-11).
3. **El BGS es control para los dos metales, con ±5 %**, como decidió el
   dueño; la plata queda en disputa en 2020, 2021, 2022 y 2024 (2023 a 4.9 %)
   y el oro pasa en los cinco años (máxima 4.92 %, en 2020). No se ajustó la
   tolerancia (A-N0-4).
4. **La *Data Series 140* entra por copia a mano.** El host de los xlsx
   (`d9-wret.s3.us-west-2.amazonaws.com`) responde HTTP 403 al propio
   `robots.txt`, y `fuentes_denominador.interpretar_robots` lee un 403 como
   veda total, una lectura más estricta que la de N0.1 ("sin archivo legible,
   sin reglas"). Se sigue la del código: el pipeline no pide esos archivos;
   las copias del 2026-10-07 son las que se bajaron en el paso 0 (A-N0-14).
5. **blockchain.com no entró como control** (alturas distintas, N0.3.3); queda
   abierto, como la comparación del Z.1 con FRED y con el BIS.

**Resultados de la corrida del 2026-10-07** (`CHANGELOG.md`, entrada
"2026-10-07 · numerador"): 32 series publicadas de 34. BTC: gate cerrado en
17 años, diferencia máxima 0.0004 %; 2025 tuvo 53082 bloques y 165881.25 BTC
emitidos, igual al calendario. Z.1: cuatro gates cerrados (36, 36, 9 y 54
comparaciones; máxima 0.049 contra 0.05). Tabla 7: cerró. Tabla 7a: no cerró
(punto 2). Population Estimates contra la Tabla 7a: máxima 0.07 %.
