# Fuentes de precios para los ratios

> **BORRADOR EN CURSO (2026-10-04).** Todo lo que figura acá se leyó de la
> fuente desde este entorno el 2026-10-04. Lo que no se pudo leer está marcado
> **PENDIENTE DE LECTURA** y no tiene cifras. Nada de este archivo viene de
> memoria.

Este documento es el entregable del paso 0 de la fase R (ratios): evaluar, por
activo, de dónde pueden salir precios **observados**, trazables y validables,
con la misma disciplina que S2. No hay código detrás de este archivo.

Los cinco activos son los que usan los cinco pares del sitio: S&P 500, Nasdaq
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
| Términos | Lo que la fuente dice sobre publicar sus datos en un sitio. |
| Muestra | Un valor (fecha + cifra) contrastado con una segunda fuente. |

Estados posibles de una fila: **leída** (todo verificado), **parcial** (se leyó
la fuente pero falta algo, dicho cuál), **PENDIENTE DE LECTURA** (host
bloqueado o fuente caída al momento de escribir).

### La regla de la convención

Los dos lados de un ratio tienen que describir el mismo instante. Un promedio
mensual dividido por un cierre de fin de mes mezcla convenciones; es el mismo
error que costó A-S2-13 (nivel de miércoles contra promedio semanal). Por eso
la columna "Convención" es la que decide, por encima de la historia disponible.

---

## 1. Qué se pudo y qué no se pudo leer

El entorno sale a Internet por un proxy con lista de hosts permitidos. La
primera tanda de hosts se habilitó durante la sesión. Varias fuentes remiten a
otros dominios que siguen bloqueados; están listados en la sección 8.

| Host | Estado el 2026-10-04 |
| --- | --- |
| fred.stlouisfed.org | Respondió en la primera prueba (10:43 UTC: CSV de NASDAQCOM, SP500 y CBBTCUSD con HTTP 200; GOLDAMGBD228NLBM y SLVPRUSD con HTTP 404). Desde las 10:57 UTC cierra la conexión o no responde. Las páginas de metadatos y el contenido de los CSV **no se alcanzaron a guardar**. |
| shillerdata.com | Página leída. El archivo de datos está en un CDN (img1.wsimg.com) bloqueado. |
| www.lbma.org.uk | Leída. |
| www.gold.org | Leída (página de datos y términos). La descarga exige login. |
| www.bitstamp.net | API leída y probada. Página de términos detrás de un muro anti-bots (Incapsula). |
| community-api.coinmetrics.io | API leída y probada. La documentación y la licencia están en docs.coinmetrics.io, bloqueado. |
| api.blockchain.info | API leída y probada. Términos en www.blockchain.com, bloqueado. |
| api.coingecko.com | Probada. Ver sección 7. |
| stooq.com, finance.yahoo.com, data.nasdaq.com | No sirven desde un servidor. Ver sección 7. |

---

## 2. S&P 500

### 2.1 FRED `SP500` — PENDIENTE DE LECTURA

- URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500`
- Lo único verificado: el CSV existió y respondió HTTP 200 (48.941 bytes) a las
  10:43 UTC del 2026-10-04. El contenido no se guardó y FRED dejó de responder.
- Pendiente: frecuencia, convención, unidad, inicio real, nota de copyright de
  S&P en la página de la serie, y muestra.

### 2.2 Robert Shiller, `ie_data.xls` — parcial

- Página: `https://shillerdata.com/`. El archivo se sirve desde
  `https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/70fec4f5-727f-4e53-b5f1-179af109c5fa/ie_data.xls`
  (host bloqueado; el espejo `econ.yale.edu/~shiller/data/ie_data.xls`
  responde HTTP 403 desde Yale).
- Frecuencia nativa: mensual. La página dice que el conjunto "consists of
  monthly stock price, dividends, and earnings data and interest rates and the
  consumer price index, starting January 1871".
- **Convención: promedio mensual de cierres diarios.** Texto literal de la
  página: *"Stock price data are monthly averages of daily closing prices."*
  Los dividendos y ganancias se llevan a mensual por interpolación lineal, y
  antes de 1926 vienen de Cowles interpolados desde datos anuales (también
  literal).
- Unidad y moneda: puntos de índice y USD por acción para dividendos
  (pendiente de confirmar en el archivo).
- Inicio real: enero de 1871 según la página; pendiente de ver en el archivo.
- Clave / registro: no.
- Términos: **no se encontró una declaración de términos en la página**. Queda
  como punto abierto.
- Muestra: pendiente (sin archivo).
- Qué permite que FRED no: retorno total mensual (precio + dividendos). Qué
  no permite: cierres. Un ratio con el S&P de Shiller en el denominador exige
  que el numerador sea también un promedio mensual.

### 2.3 Otras candidatas para S&P 500

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| S&P Dow Jones Indices (www.spglobal.com), originador | PENDIENTE DE LECTURA | Host bloqueado. Sería la fuente para validar FRED `SP500`. |
| Nasdaq (api.nasdaq.com), serie histórica SPX | PENDIENTE DE LECTURA | Host bloqueado. |
| Cboe (cdn.cboe.com), CSV histórico del SPX | PENDIENTE DE LECTURA | Host bloqueado. |
| Stooq `^spx` | **no sirve** | Ver sección 7. |
| Yahoo Finance `^GSPC`, `^SP500TR` | **no sirve** | Ver sección 7. |

---

## 3. Nasdaq Composite

### 3.1 FRED `NASDAQCOM` — PENDIENTE DE LECTURA

- URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM`
- Lo único verificado: HTTP 200 con 280.955 bytes a las 10:43 UTC del
  2026-10-04. Contenido no guardado.
- Pendiente: todo lo demás.

### 3.2 Otras candidatas

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| Nasdaq (api.nasdaq.com), serie histórica COMP, originador | PENDIENTE DE LECTURA | Host bloqueado. Sería la fuente para validar FRED `NASDAQCOM`. |
| indexes.nasdaqomx.com | PENDIENTE DE LECTURA | Host bloqueado. |
| Nasdaq Data Link (data.nasdaq.com) | **no sirve** | Ver sección 7. |

---

## 4. Oro

### 4.1 FRED `GOLDAMGBD228NLBM` y `GOLDPMGBD228NLBM` — leída (negativa)

- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=GOLDAMGBD228NLBM`
  respondió **HTTP 404** (página HTML de 28.933 bytes) a las 10:43 UTC del
  2026-10-04. FRED ya no sirve el fixing LBMA de oro. La página de la serie,
  que diría desde cuándo y por qué, no se alcanzó a leer (PENDIENTE).

### 4.2 LBMA Gold Price (www.lbma.org.uk) — leída

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
- Términos: para platino y paladio la página anuncia que desde el 1 de julio
  de 2026 *"A licence from IBA is required in order to obtain, use or
  redistribute real-time or historical ... Price data"*. Para oro y plata no
  hay una frase equivalente en la página, pero el movimiento de las tablas a
  un portal con licencia y el retiro de la historia en World Gold Council
  (4.3) apuntan en la misma dirección. Los términos de IBA (www.ice.com)
  están PENDIENTES DE LECTURA.
- Endpoint JSON histórico (`prices.lbma.org.uk/json/gold_pm.json`): host
  bloqueado; **no se pudo comprobar si existe ni qué entrega**.
- Muestra: ninguna (sin acceso a datos).

### 4.3 World Gold Council, Goldhub (www.gold.org) — leída (negativa)

- Página: `https://www.gold.org/goldhub/data/gold-prices`.
- Qué ofrece: *"gold price averages over a range of timeframes (monthly,
  quarterly, annually) going back to 1978"*. Es decir, **promedios**, no
  cierres. Se actualiza semanalmente; unidad "currency unit per troy ounce".
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
- Conclusión: no sirve para publicar en un sitio sin autorización escrita, y
  además es promedio.

### 4.4 Otras candidatas para oro

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| Deutsche Bundesbank, serie `BBEX3.D.XAU.USD.EA.AC.C06` (fixing de Londres, tarde, USD por onza) | PENDIENTE DE LECTURA | Hosts api.statistiken.bundesbank.de y www.bundesbank.de bloqueados. Es la candidata principal: diaria, sin clave, de un banco central. Falta leer la serie, su inicio, su convención exacta y sus términos. |
| Banco Mundial, "Pink Sheet" (`CMO-Historical-Data-Monthly.xlsx`) | PENDIENTE DE LECTURA | Hosts bloqueados. Promedio mensual; licencia por leer. |
| FRED `PGOLDUSDM` (FMI, precio global del oro) | PENDIENTE DE LECTURA | FRED caído. Mensual, presumiblemente promedio: **por confirmar**. |
| Nasdaq Data Link `LBMA/GOLD` | **no sirve** | Ver sección 7. |

---

## 5. Plata

### 5.1 FRED `SLVPRUSD` — leída (negativa)

- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SLVPRUSD` respondió
  **HTTP 404** a las 10:43 UTC del 2026-10-04. La búsqueda de otras series de
  plata en FRED quedó PENDIENTE (FRED caído).

### 5.2 LBMA Silver Price — leída

- Misma página que 4.2. Convención: una subasta diaria a las **12:00 del
  mediodía, hora de Londres** (literal: *"set daily in an auction ...
  commencing at 12:00 noon London time"*). Mismo régimen de acceso con
  licencia de IBA que el oro.

### 5.3 Otras candidatas para plata

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| Deutsche Bundesbank (¿serie de plata?) | PENDIENTE DE LECTURA | Host bloqueado. No se sabe si publica plata; hay que mirar el catálogo. |
| Banco Mundial, "Pink Sheet" | PENDIENTE DE LECTURA | Host bloqueado. Incluye plata mensual según su índice de productos; **por confirmar leyendo el archivo**. |

Si no aparece una fuente diaria de plata que se pueda publicar, el par Oro/Plata
pasa a frecuencia mensual con promedios en los dos lados, o queda **NO MEDIDO**
en la frecuencia común. Eso se decide en la sección 9.

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
  24:00 UTC). La vela del día en curso aparece abierta: el 2026-10-04 a las
  11:00 UTC la API devolvía una vela para 2026-10-04.
- Unidad y moneda: USD por BTC.
- Inicio real: **2011-09-13** (primera vela: cierre 5.97). Un `start` del
  2011-08-01 devuelve lista vacía.
- Clave / registro: no para datos públicos. Límites declarados: 400 pedidos
  por segundo, 10.000 por 10 minutos.
- Términos (de la documentación de la API, literal): *"Companies seeking to
  utilize Bitstamp's exchange data for their own commercial purposes are
  directed to contact partners@bitstamp.net to receive and sign a commercial
  use Data License Agreement. Bitstamp allows the incorporation and
  redistribution of our exchange data for commercial purposes. This includes
  the right to create ratios, calculations, new original works, statistics,
  and similar, based on the exchange data."* La página general de términos
  no se pudo leer (muro anti-bots). Si losratios.com cuenta como uso
  comercial, hace falta ese acuerdo.
- Muestra: cierre del **2026-09-30 = 83562.58** USD; cierre del
  **2020-03-20 = 6210.14** USD. Contraste en 6.4.

### 6.2 Coin Metrics, API community, métrica `PriceUSD` — parcial

- URL: `https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=PriceUSD&start_time=<fecha>&end_time=<fecha>`.
- Frecuencia nativa: diaria.
- **Convención** (descripción oficial de la métrica, leída de
  `/v4/reference-data/asset-metrics?metrics=PriceUSD`, literal): *"The fixed
  closing price of the asset as of 00:00 UTC the following day (i.e., midnight
  UTC of the current day) denominated in USD. This price is generated by Coin
  Metrics' fixing/reference rate service."* Es un fixing a las 00:00 UTC, no
  un último trade.
- Unidad y moneda: USD.
- Inicio real: **2010-07-18** (catálogo: `min_time` 2010-07-18, `community:
  true`; primera fila devuelta: 2010-07-18 = 0.08584).
- Volumen: un solo pedido con `page_size=10000` devolvió la historia completa,
  5.922 filas del 2010-07-18 al 2026-10-03, sin paginación.
- Clave / registro: no.
- Términos: la licencia de los datos community está en docs.coinmetrics.io,
  **PENDIENTE DE LECTURA**. Hasta leerla no se puede afirmar si permite
  publicación en un sitio.
- Muestra: **2026-09-30 = 83579.67**; **2020-03-20 = 6174.15**.
- Nota: la métrica `ReferenceRateUSD` en la API community solo tiene historia
  desde 2026-09-27; para historia larga la métrica community es `PriceUSD`.

### 6.3 blockchain.info, gráfico "Market Price (USD)" — parcial

- URL: `https://api.blockchain.info/charts/market-price?timespan=all&format=csv&sampled=false`.
- Frecuencia nativa: diaria (6.484 filas entre 2009-01-03 y 2026-10-04).
- **Convención** (descripción que devuelve la propia API, literal):
  *"Average USD market price across major bitcoin exchanges."* Es un promedio
  entre exchanges, no un cierre; la hora de referencia no está declarada.
- Unidad y moneda: USD.
- Inicio real: filas desde 2009-01-03 con valor 0.0; **primer valor distinto
  de cero: 2010-08-18 = 0.07**.
- Clave / registro: no.
- Términos: en www.blockchain.com, **PENDIENTE DE LECTURA**.
- Muestra: **2026-09-30 = 83629.12**; **2020-03-20 = 6195.2**.

### 6.4 Contraste entre fuentes de BTC

| Fecha | Bitstamp (cierre vela UTC) | Coin Metrics (fix 00:00 UTC) | blockchain.info (promedio) | CoinGecko (00:00 UTC) |
| --- | --- | --- | --- | --- |
| 2026-09-30 | 83562.58 | 83579.67 | 83629.12 | 83640.10 (Coinbase spot con fecha: 83638.415) |
| 2020-03-20 | 6210.14 | 6174.15 | 6195.2 | sin acceso (ver 7) |

Las cuatro describen instantes o agregados distintos del mismo día. Para el
2026-09-30 la dispersión máxima es de 77.5 USD sobre ~83.600 (0.09 %); para el
2020-03-20, de 36 USD sobre ~6.200 (0.6 %), en un día de alta volatilidad. La
tolerancia de validación para BTC tiene que contemplar esa diferencia de
convención; se propone en la sección 9.

### 6.5 Otras candidatas para BTC

| Candidata | Estado | Lo verificado |
| --- | --- | --- |
| FRED `CBBTCUSD` (Coinbase) | PENDIENTE DE LECTURA | HTTP 200 con 83.836 bytes a las 10:43 UTC; contenido no guardado. Pendiente: convención (hora de cierre), inicio, notas. |
| Coinbase Exchange, velas `BTC-USD` | PENDIENTE DE LECTURA | Host api.exchange.coinbase.com bloqueado. |
| Coinbase, `api.coinbase.com/v2/prices/BTC-USD/spot?date=<fecha>` | **no sirve para historia** | Responde para fechas recientes (2026-09-30 = 83638.415) y devuelve `rate not found` para 2020-03-20, 2015-01-02 y 2014-12-01. Sirve como contraste puntual reciente, no como serie. |
| Kraken, OHLC `XBTUSD` | PENDIENTE DE LECTURA | Host bloqueado. |
| CoinGecko | **no sirve para historia** | Ver sección 7. |

### 6.6 Desde cuándo son confiables los precios de BTC

Lo que se puede decir con lo leído: hay un precio diario de un exchange que
sigue operando (Bitstamp) desde el 2011-09-13, y un fixing multi-exchange de
Coin Metrics desde el 2010-07-18. Antes de 2011-09 solo hay agregados
(blockchain.info, Coin Metrics) cuyos constituyentes no se pudieron leer
(documentación bloqueada). Fijar la fecha de "confiable" es un supuesto
(A-R0-*), no un dato; la propuesta está en la sección 9.

---

## 7. Fuentes que no sirven desde un servidor (leídas)

| Fuente | Qué pasó el 2026-10-04 |
| --- | --- |
| CoinGecko, API pública | `market_chart?days=max` devuelve HTTP 401 con el mensaje literal *"Public API users are limited to querying historical data within the past 365 days. Upgrade to a paid plan to enjoy full historical data access"*. `history?date=20-03-2020` también 401. Con `days=365` responde (366 puntos a las 00:00 UTC). Sirve para los últimos 365 días, no para una serie histórica. |
| Stooq | La portada devuelve un desafío JavaScript (prueba de trabajo SHA-256) y el CSV de `^spx` cierra la conexión. No es legible sin un navegador. |
| Yahoo Finance (`query1`/`query2.finance.yahoo.com`) | HTTP 429 "Too Many Requests" al primer pedido en query1; query2 bloqueado por el proxy. |
| Nasdaq Data Link (`data.nasdaq.com`), conjunto `LBMA/GOLD` | HTTP 403 con una página de Incapsula (anti-bots) incluso antes de pedir clave; la página del conjunto `LBMA` devuelve 404. |
| World Gold Council | Ver 4.3: descarga con login y términos de uso personal. |

---

## 8. Hosts bloqueados que faltan leer

| Host | Qué hay ahí |
| --- | --- |
| img1.wsimg.com | El `ie_data.xls` de Shiller. |
| api.statistiken.bundesbank.de, www.bundesbank.de | Fixing de oro en USD, diario; catálogo (plata); términos. |
| thedocs.worldbank.org, www.worldbank.org | Pink Sheet: oro y plata mensuales; licencia. |
| api.nasdaq.com | Históricos de COMP y SPX del originador del Nasdaq Composite. |
| www.spglobal.com | S&P DJI, originador del S&P 500. |
| cdn.cboe.com | CSV histórico diario del SPX. |
| docs.coinmetrics.io, coinmetrics.io | Licencia community y metodología de la tasa de referencia. |
| www.blockchain.com | Términos de la API de blockchain.info. |
| prices.lbma.org.uk | Endpoint JSON histórico de LBMA. |
| www.ice.com | Términos de licencia de IBA. |

---

## 9. Recomendación por activo, frecuencia común y supuestos

**PENDIENTE.** Esta sección se escribe cuando estén leídas las filas
pendientes. Lo que ya se puede adelantar, porque no depende de ellas:

- La frecuencia común candidata es **semanal, cierre del viernes** (último día
  hábil de la semana para los mercados de Nueva York), sin interpolar, con
  arrastre máximo declarado y columna de fecha de origen, como RRP en A-S2-5.
- Los cinco activos cierran a horas distintas del mismo día: índices a las
  16:00 de Nueva York; oro a las 15:00 y plata a las 12:00 de Londres; BTC a
  las 00:00 UTC del día siguiente (Coin Metrics) o al cierre de la vela UTC
  (Bitstamp). El desfase máximo dentro de un mismo viernes es de varias horas
  y va como supuesto numerado, con el número exacto una vez elegidas las
  fuentes.
- Shiller solo sirve en un ratio donde el otro lado sea también un promedio
  mensual. Se propone como **serie secundaria mensual** para historia larga y
  retorno total, nunca mezclada con cierres.
- Precio frente a retorno total: con lo leído, solo Shiller trae dividendos.
  Todo ratio con índices a frecuencia semanal sería de **precio**, y lo dirá.
