# Changelog de data/series

Una entrada por corrida, de la más reciente a la más antigua.

Las secciones cuyo título no es una fecha (por ejemplo, los cambios de supuestos)
se escriben a mano, se conservan arriba y el script no las toca.

## Cambios de supuestos

Cada línea registra un cambio que altera lo que la serie mide, no cómo se
calcula. La justificación completa está en `SUPUESTOS.md`, bajo el número que se
cita.

- **2026-10-04 · A-R0-17 · Contexto del corte de 1968-04: coincide con el fin del
  London Gold Pool.** Hasta el 15 de marzo de 1968 los bancos centrales
  sostenían el oro de Londres entre 35.08 y 35.20 USD (Bordo, Monnet y Naef,
  NBER Working Paper 24016). Abril de 1968 es el primer mes completo sin el
  Pool. No cambia la regla, el tramo ni ningún valor.

- **2026-10-04 · A-R0-20 · Supuesto nuevo: el oro y la plata se comparan cada mes
  con el FMI, y el mes que pasa del umbral queda como valor en disputa.** El
  umbral es la tolerancia del gate anual, 0.5 % el oro y 1 % la plata. Un valor
  en disputa se publica sin cambios, con los dos números a la vista, y no entra
  a ninguna métrica. El control no detiene la corrida. Hoy marca diez meses del
  oro y diez de la plata, de 560 comparados por metal. **Ningún valor publicado
  cambia**: `precios_mensuales.csv` gana `oro_contraste_fmi` y
  `plata_contraste_fmi`; `ratios.csv`, `valor_en_disputa`; `pares.csv`,
  `meses_en_disputa`. En marzo de 1985, una tercera lectura (Engelhard, 304.34)
  le da la razón al FMI (303.94) y no al Pink Sheet (313.5), que sigue siendo
  el valor publicado.

- **2026-10-04 · A-R0-17 · Un mes con un valor en disputa no es apto para
  métricas, y no corta el tramo.** Oro/Plata sigue apto desde 1968-04, con 682
  meses en lugar de 702; BTC/Oro, desde 2013-01, con 161 en lugar de 165.

- **2026-10-04 · A-R0-16 · El FMI deja de ser solo una referencia: es el control
  mensual de A-R0-20.** Sigue sin ser el gate, porque comparte el origen con el
  Pink Sheet.

- **2026-10-04 · A-R0-15 · Se versiona un cuarto crudo: la copia del FMI.** Sus
  términos permiten redistribuir los datos con atribución y prohíben la descarga
  masiva automatizada: 619 KB, una sola copia, bajada a mano. Su atribución
  queda en `data/raw/ATRIBUCION.md`.

- **2026-10-04 · A-R0-19 · Supuesto nuevo: el oro y la plata se empalman.** Edición
  del Pink Sheet del 3 de enero de 2025, sin redondear, para 1960-01 a 2024-12;
  edición vigente desde 2025-01. **Los valores publicados de 1960-01 a 2024-12
  cambian**: pasan de redondeados a sin redondear, hasta 1.4 % en el oro y 4.3 %
  en la plata. Cambiaron 770 meses del oro, 774 de la plata, 780 de Oro/Plata y
  143 de BTC/Oro: 2467 valores. El mayor cambio de cada columna: 1.389 % en el
  oro de 1968-01 (36 -> 35.5), 4.280 % en la plata de 1962-01 (1 -> 1.0428),
  4.615 % en Oro/Plata de 1962-09 (29.1667 -> 30.5127) y 0.042 % en BTC/Oro de
  2015-06. En cada corrida, redondear la edición congelada tiene que
  reproducir la vigente en todos los meses superpuestos; si no, la corrida se
  detiene. La edición congelada está versionada en `data/raw/` y se identifica
  por su SHA-256. `precios_mensuales.csv` gana la columna `pink_sheet_edicion`.

- **2026-10-04 · A-R0-17 · El error por redondeo pasa a ser el de la edición usada
  en cada mes, y Oro/Plata es apto para métricas desde 1968-04.** Eran 212 meses,
  desde 2009-02; son 702 de 801. En la edición sin redondear el error es media
  unidad del último decimal publicado de cada valor. Lo que corta en 1968 son
  febrero y marzo, que vienen al dólar. BTC/Oro sigue apto desde 2013-01. El
  umbral de 0.5 % y la regla del tramo final sin interrupción no cambian.

- **2026-10-04 · A-R0-16 · El gate de oro y plata, recalculado con la serie
  empalmada, sigue cerrando; las tolerancias no cambian.** Diferencia máxima de
  0.120 % en el oro y de 0.601 % en la plata; con la serie redondeada eran
  0.116 % y 0.559 %.

- **2026-10-04 · A-R0-18 · El sesgo contra Engelhard, recalculado con la serie
  empalmada.** En promedio, 0.072 % en el oro y 0.402 % en la plata; eran 0.070 %
  y 0.397 %. Las ocho diferencias siguen con el mismo signo.

- **2026-10-04 · A-R0-15 · Se versiona un tercer crudo: la edición del Pink Sheet
  del 3 de enero de 2025.** CC BY 4.0, 765 KB, una sola copia con nombre fijo. Su
  atribución queda en `data/raw/ATRIBUCION.md`.

- **2026-10-04 · A-R0-9 · El redondeo del Pink Sheet deja de alcanzar a toda la
  historia.** Pesa solo desde 2025-01, donde es de 0.02 % en el oro y de hasta
  0.16 % en la plata. Con la serie entera redondeada llegaba a 5.6 % en la plata
  de 1960.

- **2026-10-04 · A-R0-8 · La coincidencia de la plata con el FMI, medida con la
  serie empalmada.** Mediana de 0.10 % en 560 meses; con la serie redondeada era
  de 0.35 %. La plata sigue siendo estimación.

- **2026-10-04 · A-R0-18 · Dato nuevo: en los ocho contrastes anuales del gate, el
  Banco Mundial queda por debajo de Engelhard.** En promedio, 0.070 % en el oro y
  0.397 % en la plata. El FMI queda por debajo de Engelhard en los mismos ocho y
  por montos parecidos: el sesgo es de la cotización, no del procesamiento. No
  cambia el gate ni las series.

- **2026-10-04 · A-R0-17 · Supuesto nuevo: las métricas sobre un ratio solo usan
  los meses con error máximo por redondeo de hasta 0.5 %.** `precios_mensuales.csv`
  y `ratios.csv` publican ese error fila por fila (0.5/oro, 0.05/plata, y la suma
  para el ratio), y `ratios.csv` marca qué meses son aptos. Oro/Plata es apto
  desde 2009-02, 212 de 801 meses; BTC/Oro, desde 2013-01, los 165. Los meses
  anteriores se siguen publicando. Los valores de las series no cambian: se
  agregan columnas.

- **2026-10-04 · A-R0-16 · El gate de oro y plata pasa de un ancla mensual de
  LBMA, que no se pudo transcribir, a un gate anual contra el USGS; de no medido a
  dato.** El promedio de los doce meses del Pink Sheet contra el precio promedio
  anual de los *Mineral Commodity Summaries* de febrero de 2026, para 2021 a 2024.
  Las tolerancias (±0.5 % el oro, ±1 % la plata) quedaron justificadas por escrito
  antes de calcularlo. Cerró en cuatro años de cuatro: diferencia máxima de
  0.116 % en el oro y de 0.559 % en la plata, las ocho con el mismo signo.

- **2026-10-04 · A-R0-15 · El crudo de Coin Metrics pasa a versionarse.** La regla
  deja de ser "solo las fuentes abiertas" y pasa a ser "las que tienen una
  licencia que permite redistribuir": CC BY y CC BY-NC. La atribución y la
  licencia quedan en `data/raw/ATRIBUCION.md`. Los crudos de Shiller y de FRED
  `NASDAQCOM` siguen fuera del repositorio.

- **2026-10-04 · A-R0-14 · Para publicar hace falta, además de la licencia, que la
  validación externa haya cerrado.** Una serie cuyo gate no cierra se calcula y se
  publica como "NO MEDIDO: sin validación externa", igual que sus pares. Antes el
  oro y la plata se publicaban sin gate de nivel.

- **2026-10-04 · A-R0-12 · Del S&P 500 y del Nasdaq no queda escrito ningún nivel
  del índice.** De cada contraste se registra la cantidad de meses, la diferencia
  mediana y, del peor mes, la fecha y la diferencia; los dos valores de ese mes
  solo para BTC. Se aclara además que la diferencia se mide sobre el valor de
  contraste y que el contraste del Nasdaq usa los últimos diez años.

- **2026-10-04 · A-R0-11 · La fecha contra la que se recorta Shiller es la cabecera
  `Last-Modified` de la descarga, guardada en el manifiesto.** Si no se conoce, la
  última fila se descarta siempre.

- **2026-10-04 · A-R0-8 · Segunda evidencia de que la plata del Pink Sheet es un
  promedio mensual: coincide con la serie de LBMA del FMI.** Mediana de 0.35 % en
  560 meses. Sigue siendo estimación: el Banco Mundial no lo escribe. Desde junio
  de 2025 la diferencia mediana sube de 0.21 % a 0.63 %, sin cambio declarado.

- **2026-10-04 · A-R0-1 · La regla de mes completo se separa por tipo de fuente.**
  En una fuente diaria, un mes entra cuando la serie ya tiene una observación
  posterior a su último día; en BTC, además, tiene que traer todos sus días; en
  una fuente mensual, cuando terminó antes de la fecha en que la fuente dice
  haberse actualizado. Antes decía, para todas, "antes de la fecha de
  actualización o de descarga", y eso habría dejado entrar la última fila de
  Shiller, que es el cierre de un solo día.

- **2026-10-04 · A-R0-1 a A-R0-16 · Primera publicación de los precios mensuales
  y los ratios (fase R).** Se publican oro y plata (1960-01 a 2026-09, 801 meses)
  y BTC (2013-01 a 2026-09, 165 meses), como promedio mensual de cierres
  diarios y solo de meses completos (A-R0-1), y dos pares: Oro/Plata, con
  estado de estimación (A-R0-8), y BTC/Oro. El S&P 500 y el Nasdaq Composite se
  calculan y no se publican; sus tres pares figuran como "NO MEDIDO: pendiente
  de permiso del dueño del índice" (A-R0-14). Los tres contrastes mensuales
  cerraron: S&P 500 contra FRED, máxima de 0.232 % sobre ±0.5 %; Nasdaq contra la
  API de nasdaq.com, 0.027 % sobre ±0.1 %; BTC contra Bitstamp, 1.332 % sobre ±2 %
  (A-R0-12). El gate anual de oro y plata contra el USGS cerró (A-R0-16). El oro
  cambia de definición en junio de 2025 (A-R0-7). Los crudos que no se pueden
  redistribuir quedan fuera del repositorio, con su URL, fecha y SHA-256 en
  `descargas_ratios.csv` (A-R0-15).

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
  - pink_sheet_edicion_2025-01-03: https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx, sha256 bd89b83eeceadaecb803018c104f76b316d2df3fae28ef7afde48021100c7e11, actualizada el 2025-01-03
  - fmi_pcps: https://www.imf.org/-/media/files/research/commodityprices/monthly/external-data.xlsx, sha256 e0bc0cbbd08208e9868fb16e21992ff4b86a7676a2b5f64d32a02bdb8bdcc464
  - pink_sheet: https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx, sha256 ea1c350827878ea3bbe30e3cda16a13fd3bd5b409b8458940dc94a36b5a33154, actualizada el 2026-10-02
  - shiller_ie_data: https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/70fec4f5-727f-4e53-b5f1-179af109c5fa/ie_data.xls?ver=1788371540009, sha256 044196dafe44c3030b2facbdea023975b3f6aa68b4e52f8f9bafc403e19589c1, actualizada el 2026-09-02
  - NASDAQCOM: https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM, sha256 5f40c787ab892665ed1239b0ccad0eda45b3c725ef09a66d3c0026c25e56de04, actualizada el 2026-10-03
  - coin_metrics_btc: https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=PriceUSD&frequency=1d&page_size=10000, sha256 b1acbe3f13bf639f3f4f508a03bd722908c50ffd3e315ac0337b410669027e8a
- Series, en meses completos:
  - Oro: 1960-01 a 2026-09, 801 meses, se publica (CC BY 4.0; A-R0-7, A-R0-9, A-R0-17, A-R0-19, A-R0-20)
  - Plata: 1960-01 a 2026-09, 801 meses, se publica (CC BY 4.0; A-R0-8, A-R0-9, A-R0-17, A-R0-19, A-R0-20)
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
  - Oro / Plata: estimación, 1960-01 a 2026-09, 801 meses; apto para métricas desde 1968-04 (682 meses: el tramo final con error de redondeo <= 0.5 %, A-R0-17, menos 20 con un valor en disputa, A-R0-20)
  - BTC / Oro: dato, 2013-01 a 2026-09, 165 meses; apto para métricas desde 2013-01 (161 meses: el tramo final con error de redondeo <= 0.5 %, A-R0-17, menos 4 con un valor en disputa, A-R0-20)
  - Oro / S&P 500: NO MEDIDO: pendiente de permiso del dueño del índice, 1960-01 a 2026-08, 800 meses
  - BTC / S&P 500: NO MEDIDO: pendiente de permiso del dueño del índice, 2013-01 a 2026-08, 164 meses
  - Nasdaq / S&P 500: NO MEDIDO: pendiente de permiso del dueño del índice, 1971-03 a 2026-08, 666 meses
- Meses agregados: 0
- Revisiones de datos históricos: ninguna
- Empalme del Pink Sheet:
  - OK - Oro: redondear la edición del 2025-01-03 reproduce la vigente en 780 de 780 meses superpuestos; 11 quedan exactamente a medio paso de redondeo: 1968-01 (35.5 y 36.0), 1971-10 (42.5 y 43.0), 1973-04 (90.5 y 91.0), 1982-12 (444.5 y 445.0), 1985-03 (313.5 y 314.0), 1985-06 (316.5 y 317.0), 1985-11 (321.5 y 322.0), 2002-02 (295.5 y 296.0), 2015-06 (1181.5 y 1182.0), 2016-02 (1199.5 y 1200.0), 2022-05 (1848.5 y 1849.0)
  - OK - Plata: redondear la edición del 2025-01-03 reproduce la vigente en 780 de 780 meses superpuestos; 1 queda exactamente a medio paso de redondeo: 2015-09 (14.75 y 14.8)
- Pink Sheet contra FMI:
  - Oro: 560 meses comparados, de 1980-01 a 2026-08; diferencia mediana 0.017 %; umbral +/-0.50 %; 10 meses en disputa: 1985-03 (Pink Sheet 313.5, FMI 303.94, diferencia 3.145 %); 1985-11 (Pink Sheet 321.5, FMI 325.24, diferencia -1.150 %); 1986-01 (Pink Sheet 347.48, FMI 345.38, diferencia 0.608 %); 1997-09 (Pink Sheet 322.82, FMI 324.4762, diferencia -0.510 %); 2000-05 (Pink Sheet 275.19, FMI 276.7409, diferencia -0.560 %); 2011-12 (Pink Sheet 1639.97, FMI 1652.3056, diferencia -0.747 %); 2015-12 (Pink Sheet 1075.74, FMI 1068.2526, diferencia 0.701 %); 2016-12 (Pink Sheet 1157.36, FMI 1151.4028, diferencia 0.517 %); 2025-05 (Pink Sheet 3309.0, FMI 3288.0095, diferencia 0.638 %); 2026-01 (Pink Sheet 4753.0, FMI 4719.7059, diferencia 0.705 %)
  - Plata: 560 meses comparados, de 1980-01 a 2026-08; diferencia mediana 0.096 %; umbral +/-1.00 %; 10 meses en disputa: 1980-01 (Pink Sheet 38.8756, FMI 39.2843, diferencia -1.040 %); 1985-07 (Pink Sheet 5.9997, FMI 6.0836, diferencia -1.379 %); 1985-08 (Pink Sheet 6.1511, FMI 6.2498, diferencia -1.580 %); 1987-04 (Pink Sheet 7.3495, FMI 7.4727, diferencia -1.649 %); 2004-04 (Pink Sheet 7.1486, FMI 7.055, diferencia 1.327 %); 2011-04 (Pink Sheet 42.6952, FMI 41.9656, diferencia 1.739 %); 2011-05 (Pink Sheet 37.3359, FMI 36.75, diferencia 1.594 %); 2020-07 (Pink Sheet 20.647, FMI 20.405, diferencia 1.186 %); 2024-12 (Pink Sheet 30.764, FMI 30.3707, diferencia 1.295 %); 2025-12 (Pink Sheet 62.3, FMI 64.7325, diferencia -3.758 %)
- Contrastes:
  - OK - S&P 500 contra FRED SP500, promedio mensual de los cierres diarios: 119 meses, diferencia mediana 0.000 %, máxima 0.232 % en 2024-01, tolerancia +/-0.50 %
  - OK - Nasdaq Composite contra API de nasdaq.com, promedio mensual de los cierres diarios: 119 meses, diferencia mediana 0.000 %, máxima 0.027 % en 2023-08, tolerancia +/-0.10 %
  - OK - BTC contra Bitstamp, promedio mensual de los cierres de la vela diaria UTC: 165 meses, diferencia mediana 0.044 %, máxima 1.332 % en 2017-12 (15194.1050 contra 14994.4103), tolerancia +/-2.00 %
- Oro y plata:
  - OK - Oro: gate anual contra el USGS, 4 de 4 años dentro de +/-0.50 %
  - OK - Oro 2021: promedio de los 12 meses 1799.6292 contra 1801.00 del USGS, diferencia -0.076 %, tolerancia +/-0.50 %
  - OK - Oro 2022: promedio de los 12 meses 1800.6025 contra 1802.00 del USGS, diferencia -0.078 %, tolerancia +/-0.50 %
  - OK - Oro 2023: promedio de los 12 meses 1942.6658 contra 1945.00 del USGS, diferencia -0.120 %, tolerancia +/-0.50 %
  - OK - Oro 2024: promedio de los 12 meses 2387.7025 contra 2388.00 del USGS, diferencia -0.012 %, tolerancia +/-0.50 %
  - OK - Plata: gate anual contra el USGS, 4 de 4 años dentro de +/-1.00 %
  - OK - Plata 2021: promedio de los 12 meses 25.1646 contra 25.23 del USGS, diferencia -0.259 %, tolerancia +/-1.00 %
  - OK - Plata 2022: promedio de los 12 meses 21.7944 contra 21.88 del USGS, diferencia -0.391 %, tolerancia +/-1.00 %
  - OK - Plata 2023: promedio de los 12 meses 23.3986 contra 23.54 del USGS, diferencia -0.601 %, tolerancia +/-1.00 %
  - OK - Plata 2024: promedio de los 12 meses 28.2692 contra 28.37 del USGS, diferencia -0.355 %, tolerancia +/-1.00 %
  - OK - Oro 2026-04: 4721.00 dentro de [3994.50, 4870.50] (LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am $3,994.50; Price High 17 Apr pm $4,870.50)
  - OK - Oro 2026-05: 4587.00 dentro de [3994.50, 4870.50] (LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am $3,994.50; Price High 17 Apr pm $4,870.50)
  - OK - Oro 2026-06: 4228.00 dentro de [3994.50, 4870.50] (LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am $3,994.50; Price High 17 Apr pm $4,870.50)
  - OK - Plata 2026-04: 75.90 dentro de [57.37, 86.79] (LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun $57.37; Price High 4 Apr $86.79)
  - OK - Plata 2026-05: 78.00 dentro de [57.37, 86.79] (LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun $57.37; Price High 4 Apr $86.79)
  - OK - Plata 2026-06: 66.70 dentro de [57.37, 86.79] (LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun $57.37; Price High 4 Apr $86.79)
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
