# Fuentes de precios para los ratios

> **APROBADO CON CONDICIONES (2026-10-04).** Todo lo que figura acá se leyó de
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
| Yahoo Finance `^GSPC` | leída, **(c)** | Responde desde la máquina con salida directa. Es lo que usa hoy el sitio: ver sección 8. |

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
| Yahoo Finance `^IXIC` | **(c)** | Es lo que usa hoy el sitio: ver sección 8. |

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
  0.03 % a 1592, 0.01 % a 4319.
- Inicio real: **1960M01 = 35**. El valor es 35 hasta 1967M12; el primer mes
  distinto es 1968M01.
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
  marca. De todos modos acá no se copia el documento: se transcriben ocho
  cifras, con su cita.

### 4.7 FMI, Primary Commodity Prices — leída, alternativa

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
- **Licencia: reutilización libre con atribución.** La página "Copyright and
  Usage" (`https://www.imf.org/en/about/copyright-and-terms`, vigente desde el
  2024-10-11) tiene términos especiales para los datos estadísticos, y nombra a
  *Primary Commodity Prices* entre ellos: se pueden descargar, copiar, publicar
  y distribuir, con atribución al FMI y diciendo si se transformaron. Dos
  límites: pide escribir para *"any potential commercial reuse"*, y prohíbe la
  descarga masiva por medios automatizados sin permiso.
- **Por qué no es el gate.** Comparte el origen con el Pink Sheet —el fixing de
  Londres—, así que contrasta cómo procesa el dato el Banco Mundial más que el
  precio. Y por sus términos no puede entrar a un pipeline sin transcribirla a
  mano. Queda como referencia.

Comparación de las tres fuentes sobre los años del gate. Es una lectura de un
día, no un contraste del pipeline:

| Año | Metal | Banco Mundial, doce meses | FMI, doce meses | USGS | BM contra FMI | BM contra USGS |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | Oro | 1799.58 | 1799.77 | 1801 | −0.010 % | −0.079 % |
| 2022 | Oro | 1800.75 | 1801.53 | 1802 | −0.043 % | −0.069 % |
| 2023 | Oro | 1942.75 | 1943.07 | 1945 | −0.016 % | −0.116 % |
| 2024 | Oro | 2387.58 | 2387.21 | 2388 | 0.016 % | −0.017 % |
| 2021 | Plata | 25.167 | 25.166 | 25.23 | 0.003 % | −0.251 % |
| 2022 | Plata | 21.783 | 21.771 | 21.88 | 0.057 % | −0.442 % |
| 2023 | Plata | 23.408 | 23.398 | 23.54 | 0.042 % | −0.559 % |
| 2024 | Plata | 28.275 | 28.226 | 28.37 | 0.174 % | −0.335 % |

Mes a mes, el Pink Sheet y el FMI difieren en una mediana de 0.06 % en el oro y
de 0.35 % en la plata (560 meses, 1980-01 a 2026-08). En la plata la diferencia
es del orden del redondeo del Pink Sheet, y no es pareja: 0.21 % de mediana
entre 2021 y 2024, 0.63 % desde junio de 2025, con un máximo de 3.76 % en
diciembre de 2025 (Banco Mundial 62.3, FMI 64.73).

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
  es 2003M07.
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
| Yahoo Finance `SI=F` | **(c)** | Futuro de COMEX, no spot. Es lo que usa hoy el sitio: ver sección 8. |

No apareció ninguna fuente diaria de plata que se pueda publicar. La única
fuente (a) es mensual.

### 5.5 Propuesta, sin implementar: la edición sin redondear del Pink Sheet

El Pink Sheet actual redondea el oro al dólar y la plata a un decimal, y eso
deja a Oro/Plata fuera de las métricas antes de febrero de 2009 (A-R0-17). El
propio Banco Mundial publicó la misma serie **sin redondear** hasta enero de
2025, y ese archivo sigue respondiendo.

- URL:
  `https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx`.
  Es la dirección que el archivo tenía en ediciones anteriores; la página
  actual no la enlaza. Leída el 2026-10-04.
- Edición: "Updated on January 03, 2025" (cabecera `Last-Modified` del mismo
  día). 765.246 bytes, sha256
  `bd89b83eeceadaecb803018c104f76b316d2df3fae28ef7afde48021100c7e11`.
- Cobertura: 780 meses, de `1960M01` a `2024M12`.
- Precisión: sin redondear. Plata: 0.9137 (1960M01), 4.1925 (1975M01), 9.8652
  (2008M11), 14.884 (2020M03). Oro: 35.27, 176.27, 760.863 y 1591.93 en esos
  mismos meses.
- **Es la misma serie.** Redondear esta edición reproduce la actual en los 780
  meses de la plata y en 775 de los 780 del oro. Los cinco que no coinciden
  terminan exactamente en ,5 (por ejemplo 1848.5 en mayo de 2022, que la edición
  actual publica como 1849): es el criterio de redondeo, y ninguno queda a más
  de medio paso.
- Convención: la descripción de la plata es la misma que hoy. La del oro es la
  anterior al cambio de junio de 2025: *"Gold (UK), 99.5% fine, London
  afternoon fixing, average of daily rates"*.
- Licencia: la del Pink Sheet, CC BY 4.0, clase (a). Es el mismo editor y el
  mismo conjunto de datos.

**Qué resolvería.** El error por redondeo de los dos metales desaparece hasta
diciembre de 2024. Oro/Plata dejaría de estar limitado por el redondeo desde
1960; los demás límites siguen (el oro fijo en 35 hasta 1967, la convención de
la plata como estimación).

**Lo que hay que decidir antes de implementarla.**

1. **Es una edición congelada.** No recibe las revisiones que el Banco Mundial
   haga después de enero de 2025. Habría que versionar ese crudo —CC BY lo
   permite— y no depender de que la URL siga respondiendo.
2. **El empalme.** La serie quedaría con dos tramos: sin redondear hasta
   2024-12 y redondeada desde 2025-01, con su error a la vista. La regla del
   empalme es un supuesto nuevo.
3. **Cuál manda donde las dos tienen dato.** Hoy coinciden salvo por el
   redondeo; si el Banco Mundial revisa un mes viejo, dejarían de coincidir.
4. **Preguntarle al Banco Mundial** si publica la serie sin redondear en algún
   lugar vigente. Ya está entre las preguntas de la sección 10.3.

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

## 8. Fuentes que usa hoy el sitio

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

---

## 9. Decisiones

**Aprobadas el 2026-10-04, con condiciones.** Los supuestos que las sostienen
están en `SUPUESTOS.md`, numerados A-R0-1 a A-R0-16; acá va la decisión y la
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
| Oro | Banco Mundial, Pink Sheet | (a) | A-R0-7, A-R0-9 | Viene como promedio mensual de precios diarios | 1960-01 |
| Plata | Banco Mundial, Pink Sheet | (a) | A-R0-8, A-R0-9 | Viene como precio mensual; que sea promedio es una **estimación** | 1960-01 |
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

1. (a): **Banco Mundial, Pink Sheet** (4.5). Cláusula: *"provided to you under
   a Creative Commons Attribution 4.0 International License (CC BY 4.0)"*.
2. (b): ninguna leída.
3. (c), excluidas: LBMA / IBA (licencia); World Gold Council (uso personal y
   autorización escrita); Yahoo `GC=F` (futuro, y sección 8).
4. No existen: Bundesbank en USD; FRED.

**Plata**

1. (a): **Banco Mundial, Pink Sheet** (5.3). Misma cláusula.
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
| Oro / Plata | 1960-01 | El redondeo de la plata pesa más de 1 % mientras esté por debajo de 5 USD; hasta 2003-07 hay meses así (A-R0-9). | Sí |
| BTC / Oro | 2010-08 (primer mes completo de Coin Metrics) | Antes de 2013 las fuentes de BTC no coinciden (A-R0-10). | Sí, desde 2013-01 |
| Oro / S&P 500 | 1960-01 | El oro vale 35 fijo hasta 1967-12. | NO MEDIDO |
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
| Oro | Promedio de los doce meses contra el precio anual del USGS | 4 años de 4, máxima 0.116 % | ±0.5 % por año |
| Plata | Promedio de los doce meses contra el precio anual del USGS | 4 años de 4, máxima 0.559 % | ±1 % por año |

**Las fuentes (c) se usan solo para contrastar.** El archivo no se guarda ni se
publica (A-R0-12). En el changelog queda, por corrida, cuántos meses se
compararon, la diferencia mediana y, del mes que más se aparta, la fecha y la
diferencia. **Del S&P 500 y del Nasdaq no queda ningún nivel del índice.**

Si el contraste de BTC o de un índice no cierra, la corrida se detiene. Si no
cierra el gate de un metal, la corrida sigue y el metal y sus pares se publican
como NO MEDIDO.

**El gate de oro y plata** (A-R0-16). No hay una segunda fuente mensual abierta
para los metales, así que el gate es anual: el promedio de los doce meses del
Pink Sheet contra el precio promedio del año que publica el USGS (4.6), para
todos los años que la última edición trae sin estimar. Hoy son cuatro, 2021 a
2024.

| Año | Oro, Pink Sheet | Oro, USGS | Diferencia | Plata, Pink Sheet | Plata, USGS | Diferencia |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 1799.58 | 1801 | −0.079 % | 25.167 | 25.23 | −0.251 % |
| 2022 | 1800.75 | 1802 | −0.069 % | 21.783 | 21.88 | −0.442 % |
| 2023 | 1942.75 | 1945 | −0.116 % | 23.408 | 23.54 | −0.559 % |
| 2024 | 2387.58 | 2388 | −0.017 % | 28.275 | 28.37 | −0.335 % |

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
| Sin esa licencia: Shiller (s/d) y FRED `NASDAQCOM` ((b) con reserva) | **Fuera del repositorio**, en `data/privado/`, ignorado por git. | URL, fecha y SHA-256 de cada descarga, y el código de transformación. |
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
| FRED `M2SL` | (a); falta el aviso de la API | Se conserva; agregar el aviso |

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
- **Qué destraba.** La plata deja de ser estimación (A-R0-8) y el quiebre del
  oro queda descrito con hora (A-R0-7).

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
| A-R0-9 | El Pink Sheet viene redondeado | dato |
| A-R0-10 | Los pares con BTC se publican desde 2013-01 | supuesto |
| A-R0-11 | La última fila de Shiller no es un mes completo; rezago | dato; supuesto la regla |
| A-R0-12 | Las fuentes (c) solo contrastan; tolerancias; qué queda escrito | supuesto |
| A-R0-13 | Los ratios con índices son de precio | dato |
| A-R0-14 | Se publica lo que la licencia permite y una segunda fuente valida | supuesto |
| A-R0-15 | Un crudo entra al repositorio solo si su licencia permite redistribuirlo | supuesto |
| A-R0-16 | Gate anual de oro y plata contra el USGS; cerró el 2026-10-04 | supuesto la regla; dato el resultado |
| A-R0-17 | Las métricas solo usan meses con error de redondeo del ratio de hasta 0.5 % | dato el error; supuesto el umbral |
| A-R0-18 | En los ocho contrastes anuales el Banco Mundial queda por debajo de Engelhard | dato |

---

## 12. Lo que sigue abierto

1. **Los tres permisos de la sección 10.**
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
7. **La edición sin redondear del Pink Sheet** (5.5). Está propuesta y no
   implementada. Sin ella, Oro/Plata es apto para métricas desde 2009-02.
8. **Precio actual de BTC en el sitio.** Queda fuera de la convención mensual
   y no tiene decisión.
9. **No leído:** los ZIP históricos de Kraken, los términos de datos de
   Kraken, los términos del Bundesbank, la exportación de S&P DJI, y la
   documentación técnica del FMI (se leyó la descripción de cada serie en la
   planilla).
