# Changelog de data/series

Una entrada por corrida, de la más reciente a la más antigua.

Las secciones cuyo título no es una fecha (por ejemplo, los cambios de supuestos)
se escriben a mano, se conservan arriba y el script no las toca.

## Cambios de supuestos

Cada línea registra un cambio que altera lo que la serie mide, no cómo se
calcula. La justificación completa está en `SUPUESTOS.md`, bajo el número que se
cita.

- **2026-10-03 · A-S2-13 · El gate cerró en corridas reales con el ancla
  corregida; el supuesto pasa de no medido a dato.** Dos corridas, ambas con
  código de salida 0: la reproducción de la corrida del 2026-09-22 desde sus
  descargas crudas (serie hasta 2026-09-16, 351 filas) y una descarga nueva del
  2026-10-03 (serie hasta 2026-09-30, 353 filas, 0 revisiones históricas). En las
  dos, para el 2026-09-16: S2.1 calculado 5749.465 contra 5749.465 esperado,
  diferencia 0.000 sobre ±5, y WALCL, TGA y ON RRP con diferencia 0.000 sobre ±1
  (A-S2-14). Los mismos datos que el gate rechazó el 2026-09-22 cierran ahora sin
  haber tocado la fórmula. Primera publicación de `data/series/liquidez_neta.csv`
  y `reportes/liquidez_neta.png`. Sigue sin umbral (A-S2-3) y sin interpretación.

- **2026-10-03 · A-S2-9 · Causa de las unidades NO VERIFICADAS identificada.**
  `https://fred.stlouisfed.org/data/<ID>.txt` responde HTTP 200 con una página
  HTML, sin línea `Units:`, para las tres series. La unidad sigue sin verificarse
  contra metadatos en cada corrida; los controles que quedan son la banda de orden
  de magnitud y el gate. Elegir otra fuente de metadatos queda pendiente.

- **2026-09-22 · A-S2-13 · El ancla del H.4.1 estaba mal transcrita: mezclaba
  columnas del release.** La primera corrida contra FRED en vivo la rechazó, con
  un calculado de 5749.465 contra un esperado de 5866.000: una diferencia de
  −116.535 sobre una tolerancia de ±5. La causa no era el cálculo. El ancla tomaba
  los activos totales de la columna de nivel de miércoles, pero el TGA (877.028) y
  el ON RRP (3.999) de la columna de promedio semanal. La brecha se concentró en
  el TGA porque el 15 de septiembre es fecha de pago de impuestos corporativos
  estimados: subió de 843.705 el 9 de septiembre a 991.708 el 16, y el promedio de
  esa semana quedó muy por debajo del cierre del miércoles.
  **El pipeline reprodujo la aritmética correcta con datos reales antes de que se
  tocara nada:** ya calculaba 5749.465, que es el valor que corresponde a los tres
  niveles de miércoles. El ancla nuevo son esas tres cifras del release —activos
  totales 6746548, TGA 991708 y ON RRP, línea `Others` de reverse repurchase
  agreements, 5375, en millones de USD—, leídas de
  <https://www.federalreserve.gov/releases/h41/current/>, publicado el 17 de
  septiembre de 2026. En miles de millones: `6746.548 − 991.708 − 5.375 =
  5749.465`. La corrección viene de la lectura directa del H.4.1, **no** de
  ajustar el código para que cuadre: se movió el ancla hasta la fuente, no el
  número hasta el ancla. La fórmula de S2.1 y la tolerancia de ±5 no cambian.
  El objeto de configuración ahora guarda la URL del release, su fecha de
  publicación y de qué columna salieron las cifras.

- **2026-09-22 · A-S2-14 · El gate verifica cada componente, además del total.**
  Tolerancia nueva: ±1 mil millones de USD por componente contra su cifra del
  release, junto con los ±5 del total, que siguen igual. Motivo: el gate anterior
  miraba solo el total, y un total puede cerrar porque dos componentes se
  compensan entre sí. Ese es exactamente el modo en que un ancla con columnas
  mezcladas podría haber pasado desapercibida, así que el control que faltaba se
  agregó junto con la corrección. Un componente sin dato cuenta como fuera. La
  verificación por componente domina hoy a la del total, y el porqué está escrito
  en A-S2-14.

- **2026-09-22 · A-S2-9 · Queda abierto por qué no se leyeron las unidades.**
  En la corrida del 2026-09-22 los CSV de las tres series bajaron bien pero las
  tres unidades salieron NO VERIFICADAS, y la salida no permitía saber la causa:
  la lectura de metadatos devolvía el mismo `None` para la red caída, un código
  HTTP distinto o un formato de encabezado cambiado. Eso se arregló:
  `unidad_declarada` devuelve ahora `(unidad, motivo)` y el motivo llega hasta
  este changelog. Cuál de las causas fue sigue **sin resolver**, y así queda
  documentado en A-S2-9: se sabrá en la próxima corrida con acceso. No se agregó
  ninguna clave de API.

- **2026-09-22 · A-S2-4 · La serie de TGA pasa de `WTREGEN` a `WDTGAL`.**
  `WDTGAL` es el nivel de miércoles de la cuenta general del Tesoro, en millones
  de USD. Reemplaza a `WTREGEN`, que es el promedio de la semana en miles de
  millones. Motivo: `WALCL` y el ancla del H.4.1 contra la que se valida S2.1 son
  niveles de miércoles; restarles un promedio semanal mezclaba dos convenciones
  en una misma resta. `WTREGEN` queda documentada como alternativa, no como
  predeterminada. La fórmula de S2.1 y la tolerancia del gate (±5) no cambian.
  Junto con el cambio se agregaron tests que fallan si el identificador `WDTGAL`
  deja de estar declarado en millones.

## 2026-10-04 · ratios

- Descargas:
  - pink_sheet: https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx, sha256 ea1c350827878ea3bbe30e3cda16a13fd3bd5b409b8458940dc94a36b5a33154, actualizada el 2026-10-02
  - shiller_ie_data: https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/70fec4f5-727f-4e53-b5f1-179af109c5fa/ie_data.xls?ver=1788371540009, sha256 044196dafe44c3030b2facbdea023975b3f6aa68b4e52f8f9bafc403e19589c1, actualizada el 2026-09-02
  - NASDAQCOM: https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM, sha256 5f40c787ab892665ed1239b0ccad0eda45b3c725ef09a66d3c0026c25e56de04, actualizada el 2026-10-03
  - coin_metrics_btc: https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=PriceUSD&frequency=1d&page_size=10000, sha256 b1acbe3f13bf639f3f4f508a03bd722908c50ffd3e315ac0337b410669027e8a
- Series, en meses completos:
  - Oro: 1960-01 a 2026-09, 801 meses, se publica (CC BY 4.0; A-R0-7, A-R0-9)
  - Plata: 1960-01 a 2026-09, 801 meses, se publica (CC BY 4.0; A-R0-8, A-R0-9)
  - BTC: 2013-01 a 2026-09, 165 meses, se publica (CC BY-NC 4.0; A-R0-4, A-R0-5, A-R0-10)
  - S&P 500: 1871-01 a 2026-08, 1868 meses, se calcula y no se publica: NO MEDIDO: pendiente de permiso del dueño del índice (sin licencia declarada; A-R0-2, A-R0-11, A-R0-13)
  - Nasdaq Composite: 1971-03 a 2026-09, 667 meses, se calcula y no se publica: NO MEDIDO: pendiente de permiso del dueño del índice (Copyrighted: Pre-Approval Required; uso educativo no comercial; A-R0-3, A-R0-13)
- Meses descartados:
  - BTC | 2010-07: tiene 14 de 31 días
  - BTC | 2026-10: mes en curso (la última observación es del 2026-10-03)
  - BTC | 2010-08 a 2012-12: 29 meses anteriores a 2013-01, que es desde donde la serie se usa
  - S&P 500 | 2026-09: no había terminado cuando la fuente se actualizó (2026-09-02)
  - Nasdaq Composite | 1971-02: la serie empieza el 1971-02-05, con el mes empezado
  - Nasdaq Composite | 2026-10: mes en curso (la última observación es del 2026-10-02)
- Pares:
  - Oro / Plata: estimación, 1960-01 a 2026-09, 801 meses
  - BTC / Oro: dato, 2013-01 a 2026-09, 165 meses
  - Oro / S&P 500: NO MEDIDO: pendiente de permiso del dueño del índice, 1960-01 a 2026-08, 800 meses
  - BTC / S&P 500: NO MEDIDO: pendiente de permiso del dueño del índice, 2013-01 a 2026-08, 164 meses
  - Nasdaq / S&P 500: NO MEDIDO: pendiente de permiso del dueño del índice, 1971-03 a 2026-08, 666 meses
- Meses agregados: 801 [2026-05, 2026-06, 2026-07, 2026-08, 2026-09] (últimos 5 de 801)
- Revisiones de datos históricos: ninguna
- Contrastes:
  - OK - S&P 500 contra FRED SP500, promedio mensual de los cierres diarios: 119 meses, diferencia mediana 0.000 %, máxima 0.232 % en 2024-01, tolerancia +/-0.50 %
  - OK - Nasdaq Composite contra API de nasdaq.com, promedio mensual de los cierres diarios: 119 meses, diferencia mediana 0.000 %, máxima 0.027 % en 2023-08, tolerancia +/-0.10 %
  - OK - BTC contra Bitstamp, promedio mensual de los cierres de la vela diaria UTC: 165 meses, diferencia mediana 0.044 %, máxima 1.332 % en 2017-12 (15194.1050 contra 14994.4103), tolerancia +/-2.00 %
- Oro y plata:
  - OK - Oro: gate anual contra el USGS, 4 de 4 años dentro de +/-0.50 %
  - OK - Oro 2021: promedio de los 12 meses 1799.5833 contra 1801.00 del USGS, diferencia -0.079 %, tolerancia +/-0.50 %
  - OK - Oro 2022: promedio de los 12 meses 1800.7500 contra 1802.00 del USGS, diferencia -0.069 %, tolerancia +/-0.50 %
  - OK - Oro 2023: promedio de los 12 meses 1942.7500 contra 1945.00 del USGS, diferencia -0.116 %, tolerancia +/-0.50 %
  - OK - Oro 2024: promedio de los 12 meses 2387.5833 contra 2388.00 del USGS, diferencia -0.017 %, tolerancia +/-0.50 %
  - OK - Plata: gate anual contra el USGS, 4 de 4 años dentro de +/-1.00 %
  - OK - Plata 2021: promedio de los 12 meses 25.1667 contra 25.23 del USGS, diferencia -0.251 %, tolerancia +/-1.00 %
  - OK - Plata 2022: promedio de los 12 meses 21.7833 contra 21.88 del USGS, diferencia -0.442 %, tolerancia +/-1.00 %
  - OK - Plata 2023: promedio de los 12 meses 23.4083 contra 23.54 del USGS, diferencia -0.559 %, tolerancia +/-1.00 %
  - OK - Plata 2024: promedio de los 12 meses 28.2750 contra 28.37 del USGS, diferencia -0.335 %, tolerancia +/-1.00 %
  - OK - Oro 2026-04: 4721.00 dentro de [3994.50, 4870.50] (LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am $3,994.50; Price High 17 Apr pm $4,870.50)
  - OK - Oro 2026-05: 4587.00 dentro de [3994.50, 4870.50] (LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am $3,994.50; Price High 17 Apr pm $4,870.50)
  - OK - Oro 2026-06: 4228.00 dentro de [3994.50, 4870.50] (LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am $3,994.50; Price High 17 Apr pm $4,870.50)
  - OK - Plata 2026-04: 75.90 dentro de [57.37, 86.79] (LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun $57.37; Price High 4 Apr $86.79)
  - OK - Plata 2026-05: 78.00 dentro de [57.37, 86.79] (LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun $57.37; Price High 4 Apr $86.79)
  - OK - Plata 2026-06: 66.70 dentro de [57.37, 86.79] (LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun $57.37; Price High 4 Apr $86.79)
- Nota: primera publicación de las series: no hay corrida anterior con que comparar
- Nota: los crudos que no se pueden redistribuir y las series que no se publican están fuera del repositorio (A-R0-15); de las fuentes de contraste no se guarda nada (A-R0-12)

## 2026-10-03

- Rango de datos: 2020-01-01 a 2026-09-30 (353 observaciones semanales)
- Filas agregadas: 2 [2026-09-23, 2026-09-30]
- Revisiones de datos históricos: ninguna
- Huecos: 5
  - 2020-01-01 | RRPONTSYD tomado de 2019-12-31 (el miércoles no tenía dato)
  - 2020-11-11 | RRPONTSYD tomado de 2020-11-10 (el miércoles no tenía dato)
  - 2024-06-19 | RRPONTSYD tomado de 2024-06-18 (el miércoles no tenía dato)
  - 2024-12-25 | RRPONTSYD tomado de 2024-12-24 (el miércoles no tenía dato)
  - 2025-01-01 | RRPONTSYD tomado de 2024-12-31 (el miércoles no tenía dato)
- Verificación de unidades:
  - WALCL: NO VERIFICADA (no se pudo leer los metadatos de FRED; se usa la unidad configurada (millones) y quedan como control la banda de orden de magnitud y el caso de validación; causa: https://fred.stlouisfed.org/data/WALCL.txt respondió HTTP 200 (text/html; charset=UTF-8) pero no hay línea 'Units:' en las primeras 40 líneas; la primera línea con contenido es '<!DOCTYPE html>')
  - WDTGAL: NO VERIFICADA (no se pudo leer los metadatos de FRED; se usa la unidad configurada (millones) y quedan como control la banda de orden de magnitud y el caso de validación; causa: https://fred.stlouisfed.org/data/WDTGAL.txt respondió HTTP 200 (text/html; charset=UTF-8) pero no hay línea 'Units:' en las primeras 40 líneas; la primera línea con contenido es '<!DOCTYPE html>')
  - RRPONTSYD: NO VERIFICADA (no se pudo leer los metadatos de FRED; se usa la unidad configurada (miles_de_millones) y quedan como control la banda de orden de magnitud y el caso de validación; causa: https://fred.stlouisfed.org/data/RRPONTSYD.txt respondió HTTP 200 (text/html; charset=UTF-8) pero no hay línea 'Units:' en las primeras 40 líneas; la primera línea con contenido es '<!DOCTYPE html>')
- Validación: OK - 2026-09-16: calculado 5749.465 vs esperado 5749.465, diferencia 0.000, tolerancia +/-5.000
- Umbral de expansión/contracción: NO MEDIDO (A-S2-3)
- Nota: Serie de TGA en uso: WDTGAL (Cuenta general del Tesoro (TGA), nivel de miércoles. En FRED: Liabilities and Capital: Deposits with F.R. Banks, Other Than Reserve Balances: U.S. Treasury, General Account: Wednesday Level)

## 2026-09-22

- Rango de datos: 2020-01-01 a 2026-09-16 (351 observaciones semanales)
- Filas agregadas: 351 [2026-08-19, 2026-08-26, 2026-09-02, 2026-09-09, 2026-09-16] (últimas 5 de 351)
- Revisiones de datos históricos: ninguna
- Huecos: 5
  - 2020-01-01 | RRPONTSYD tomado de 2019-12-31 (el miércoles no tenía dato)
  - 2020-11-11 | RRPONTSYD tomado de 2020-11-10 (el miércoles no tenía dato)
  - 2024-06-19 | RRPONTSYD tomado de 2024-06-18 (el miércoles no tenía dato)
  - 2024-12-25 | RRPONTSYD tomado de 2024-12-24 (el miércoles no tenía dato)
  - 2025-01-01 | RRPONTSYD tomado de 2024-12-31 (el miércoles no tenía dato)
- Verificación de unidades:
  - WALCL: NO VERIFICADA (no se pudo leer los metadatos de FRED; se usa la unidad configurada (millones) y quedan como control la banda de orden de magnitud y el caso de validación; causa: https://fred.stlouisfed.org/data/WALCL.txt respondió HTTP 200 (text/html; charset=UTF-8) pero no hay línea 'Units:' en las primeras 40 líneas; la primera línea con contenido es '<!DOCTYPE html>')
  - WDTGAL: NO VERIFICADA (no se pudo leer los metadatos de FRED; se usa la unidad configurada (millones) y quedan como control la banda de orden de magnitud y el caso de validación; causa: https://fred.stlouisfed.org/data/WDTGAL.txt respondió HTTP 200 (text/html; charset=UTF-8) pero no hay línea 'Units:' en las primeras 40 líneas; la primera línea con contenido es '<!DOCTYPE html>')
  - RRPONTSYD: NO VERIFICADA (no se pudo leer los metadatos de FRED; se usa la unidad configurada (miles_de_millones) y quedan como control la banda de orden de magnitud y el caso de validación; causa: https://fred.stlouisfed.org/data/RRPONTSYD.txt respondió HTTP 200 (text/html; charset=UTF-8) pero no hay línea 'Units:' en las primeras 40 líneas; la primera línea con contenido es '<!DOCTYPE html>')
- Validación: OK - 2026-09-16: calculado 5749.465 vs esperado 5749.465, diferencia 0.000, tolerancia +/-5.000
- Umbral de expansión/contracción: NO MEDIDO (A-S2-3)
- Nota: primera publicación de la serie: no hay corrida anterior con que comparar
- Nota: Serie de TGA en uso: WDTGAL (Cuenta general del Tesoro (TGA), nivel de miércoles. En FRED: Liabilities and Capital: Deposits with F.R. Banks, Other Than Reserve Balances: U.S. Treasury, General Account: Wednesday Level)
