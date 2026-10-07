# Changelog de data/series

Una entrada por corrida, de la más reciente a la más antigua.

Las secciones cuyo título no es una fecha (por ejemplo, los cambios de supuestos)
se escriben a mano, se conservan arriba y el script no las toca.

## Cambios de supuestos

Cada línea registra un cambio que altera lo que la serie mide, no cómo se
calcula. La justificación completa está en `SUPUESTOS.md`, bajo el número que se
cita.

- **2026-10-07 · A-N0-1 a A-N0-15 · Supuestos nuevos: la familia N0 (El Numerador),
  las series anuales de oferta de activos.** Decisión del dueño (`FUENTES.md`,
  N0.10.5). Nacen `numerador_series.csv`, `serie_N0.csv` y
  `numerador_descargas.csv`, con 32 series publicadas de 34: BTC (emisión del
  año según el calendario del protocolo por los bloques observados, oferta,
  tasa de crecimiento y porcentaje minado; gate contra Coin Metrics con
  0.001 %, fijado con el resultado del paso 0 a la vista; elasticidad cero
  por construcción), la producción minera mundial de oro y plata del USGS
  (Data Series 140 y Mineral Commodity Summaries, revisiones declaradas;
  control del BGS con ±5 %: la plata queda en disputa en 2020, 2021, 2022 y
  2024) y su cota superior de crecimiento del stock (estimación), la emisión
  neta de acciones de EE.UU. por sector (Z.1, F51.1) en USD y como % del valor
  de mercado, los títulos de deuda y la deuda no financiera de EE.UU. (Z.1,
  F3.s y D3.s) con su variación, y el parque de viviendas de EE.UU. (HVS
  Tabla 7 y Population Estimates). **La Tabla 7a del HVS queda NO MEDIDO:**
  su identidad total = vacantes + ocupadas falla en 2017 por 2 mil con la
  tolerancia de 1.5 mil fijada por construcción. Las existencias de oro y
  plata, el stock-to-flow, lo global y las elasticidades estimadas quedan NO
  MEDIDO o pendientes de prerregistro (A-N0-6, A-N0-12). No cambia ningún
  valor de otras fases.

- **2026-10-07 · A-R0-21 a A-R0-26 · Supuestos nuevos: el precio oficial del
  oro en EE.UU., 1900-03 a 1959-12, como serie de contexto.** Decisión del
  dueño. `oro_precio_oficial.csv` nace con 718 meses: 20,6718 USD por onza
  troy hasta 1934-01 (ley del 14 de marzo de 1900) y 35,00 desde 1934-02
  (proclamación del 31 de enero de 1934), derivados de la fracción legal,
  con la etiqueta "precio oficial fijado por ley, no precio de mercado",
  la convertibilidad fila por fila, el precio administrado de 1933–34
  declarado y `apto_metricas = no`. Gate de nivel y fecha contra Tesoro,
  Casa de Moneda, Junta y FMI con ±0,005 USD: cerró. Antes de 1900, NO
  MEDIDO; en 1960-01 empieza el Pink Sheet y no se empalma. `series.csv`
  suma la ficha `oro_precio_oficial_usd`. No cambia ningún valor anterior.

- **2026-10-07 · A-D0-6, A-D0-10, A-D0-11, A-D0-34 a A-D0-36 · Las series
  antiguas de Japón (M2+CDs) se publican aparte y el agregado en USD empieza
  en 1999-01.** Decisión del dueño. `m2cd_japon_1967_1999` (`MAMS1ANM2C`) y
  `m2cd_japon_1998_2008` (`MAMS3ANM2C`) entran a `denominador_dinero.csv`
  como dato, sin empalme, con gate contra la copia del FMI en FRED (±0.5 en
  100 millones de yenes, igualdad del entero, en el rango que esa copia sigue
  a cada tramo; resultado conocido al fijarla). `denominador_agregado.csv`
  retrocede de 2003-04 a 1999-01 con Japón por tramos (M2+CDs hasta 2003-03,
  M2 desde 2003-04), suma dos columnas (`serie_japon`, `quiebre`) y cambia de
  nombre; **toda la columna a tipo de cambio constante cambia de nivel**
  porque el mes de referencia pasa de 2003-04 a 1999-01 (A-D0-11). Los
  valores a tipo de cambio de cada mes de 2003-04 en adelante no cambian por
  esta decisión; lo que cambie viene de las revisiones de las fuentes en la
  corrida del día, listadas en su entrada.

- **2026-10-07 · A-D0-27 · Los crudos de `data/raw/` se guardan con los bytes
  exactos que entregó la fuente; todo el directorio pasa a `-text` en
  `.gitattributes`.** Decisión del dueño. Hasta hoy git normalizaba los
  saltos de línea al commitear y los volvía a convertir al extraer en
  Windows, y el test de los crudos contra el manifiesto (A-D0-30) fallaba.
  Cambian los bytes versionados de cuatro crudos del 2026-10-05, que la
  fuente entregó con CRLF y el repositorio guardaba con LF:
  `bce_m2_ajustada`, `bce_m2_sin_ajustar`, `bce_balance_eurosistema` (copias
  a mano del BCE) y `ocde_china_dinero_amplio`. **Ningún hash del manifiesto
  cambia:** los publicados ya eran los de los bytes originales, y los tres
  crudos del BoJ y el del BIS ya estaban guardados tal cual. Los tres CSV de
  FRED de S2 no tienen hash publicado (A-S2-10) y quedan como estaban en el
  repositorio. No cambia ningún valor publicado.

- **2026-10-07 · A-D0-17, A-D0-19, A-D0-31 a A-D0-33 · El dinero de EE.UU.
  antes de 1959 pasa de NO MEDIDO a publicado, en dos series transcritas.**
  `dinero_eeuu_1892_1946` (79 fechas de balance, millones de USD, Tabla 9 de
  *Banking and Monetary Statistics 1914–1941* y su continuación) y
  `dinero_eeuu_1947_1958` (144 meses, miles de millones de USD, Tabla 1.1 A
  del volumen 1941–1970) nacen en `dinero_eeuu_historico.csv`, con sus
  componentes y la cita de cada cifra. Dos lecturas independientes cotejadas
  celda por celda (2.082 celdas, una discrepancia resuelta releyendo la
  imagen), sumas con tolerancia cero en millones y ±0.1 en miles de
  millones, y dos gates con tolerancia fijada antes: el Censo (nueve filas
  de *Historical Statistics*, igualdad, 61 cifras iguales) y el NBER vía FRED
  (144 meses, ±0.1, máxima 0.1). La serie sin ajustar de 1947–58 queda
  transcrita y NO MEDIDO: sin segunda fuente accesible a un programa.
  Dos erratas de la fuente (1949-03 y 1950-12) se publican tal cual y en
  disputa (A-D0-33). Primera publicación: no cambia ningún valor anterior;
  en `serie_D0.csv` cambian las dos fichas NO MEDIDO y entra una tercera.

- **2026-10-06 · A-D0-25 · El mínimo de anclas pasa de 2 a 3, y el dinero amplio
  de China pasa de publicado a NO MEDIDO.** El 2 se había fijado después de ver
  que China tenía dos lecturas de la NBS: no era una tolerancia declarada a
  ciegas. Ahora rige el mismo mínimo que el gate anual de oro y plata.
  `denominador_dinero.csv` pierde las 271 filas de `dinero_amplio_china`
  hasta que haya una tercera lectura en pantalla. El mismo supuesto registra
  que el gate del balance de la Fed contra el BIS se definió sabiendo que
  cerraba, y por qué quedó así (D0.11 lo tenía como control). No cambia
  ningún valor.

- **2026-10-06 · A-D0-30 · Supuesto nuevo: las salidas derivadas se calculan
  desde lo publicado, y `test_salidas_publicadas.py` lo comprueba.**
  `denominador_pares.csv` y `denominador_ratios.csv` se regeneran: los que
  estaban publicados salían de datos de prueba, porque la suite de tests
  escribía en `data/series/`. `denominador_agregado.csv` cambia en la
  undécima o duodécima cifra de los meses en que los insumos tenían más
  decimales que los que publica el CSV.

- **2026-10-06 · A-D0-1 a A-D0-29 · Supuestos nuevos de la fase D0 (El
  Denominador).** Trece series de dinero, balances y tipos de cambio, y un
  agregado en USD de tres economías, con la convención nativa de cada emisor
  (A-D0-1), copias bajadas a mano para el BCE porque el `robots.txt` de su API
  veda al cliente (A-D0-29), China vía la OCDE y el BIS con el rótulo de la
  fuente y fuera del agregado (A-D0-9), y el balance de la Fed tomado de la
  serie consolidada del XML del H.4.1, que coincide con `WALCL` (A-D0-15). La
  comparación de los tipos de cambio contra el BIS es un control: 2008-12 del
  USD por EUR queda en disputa (A-D0-25). Oro / M2 y BTC / M2 de EE.UU. nacen
  en `ratios.py` con la lógica de la fase R (A-D0-21). Primera publicación: no
  cambia ningún valor anterior.

- **2026-10-05 · A-R0-1 · El texto deja de decir que el sitio usa el cierre de
  fin de mes: desde la fase 3 lee las series de `senales/`.** Lo que muestra es
  el promedio mensual de cierres diarios, que es la convención de este
  supuesto. El cierre de fin de mes queda como lo que el sitio usaba hasta la
  fase 3 (`FUENTES.md`, sección 8.2). No cambia la regla ni ningún valor.

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

## 2026-10-07 · ratios D0

- Pares contra M2 de EE.UU.:
  - Oro / M2 de EE.UU.: dato, 1960-01 a 2026-08, 800 meses; apto para métricas desde 1968-04 (691 meses, menos 10 con un valor en disputa)
  - BTC / M2 de EE.UU.: dato, 2013-01 a 2026-08, 164 meses; apto para métricas desde 2013-01 (164 meses, menos 0 con un valor en disputa)
- Nota: recalculados desde precios_mensuales.csv y denominador_dinero.csv, sin descargas

## 2026-10-07 · oro oficial

- Tramos:
  - 1900-03 a 1934-01: 20.6718 USD por onza troy = 480 ÷ (129/5 × 9/10) = 8000/387; Gold Standard Act, ley del 14 de marzo de 1900, sección 1 (dólar de 25,8 granos de oro de 9/10 de fino); vigente desde 1900-03-14
  - 1934-02 a 1959-12: 35.0000 USD por onza troy = 480 ÷ (320/21 × 9/10) = 35; Proclamación presidencial del 31 de enero de 1934 (sección 43(b)(2) del Título III de la ley del 12 de mayo de 1933, reformada por la sección 12 de la Gold Reserve Act del 30 de enero de 1934): dólar de 15 5/21 granos de oro de 9/10 de fino; vigente desde 1934-01-31 15:10, hora del Este
- Serie:
  - Oro: precio oficial en EE.UU. (fijado por ley), 1900-03 a 1959-12: se publica, 1900-03 a 1959-12, 718 meses (USD por onza troy de oro fino; precio oficial fijado por ley, no precio de mercado; fuera de apto_metricas; A-R0-21 A-R0-22 A-R0-23 A-R0-24 A-R0-25 A-R0-26)
  - el mes en que cambia la norma lleva el precio vigente al cierre del mes anterior, como la Junta: '$20.67 ... through January 1934 and $35 ... thereafter' (Banking and Monetary Statistics 1914-1941, p. 522)
  - antes de 1900-03: NO MEDIDO hasta verificar la base legal (sección 3511 de los Revised Statutes y las leyes de 1834, 1837 y 1873, no leídas: loc.gov exige una verificación humana)
  - 1960-01: termina esta serie y empieza el oro del Pink Sheet (promedio mensual del fixing de Londres, A-R0-7); son dos series distintas y no se empalman
- Validación:
  - oro_precio_oficial_usd: gate de nivel y fecha contra cifras publicadas por el Tesoro, la Casa de Moneda, la Junta y el FMI cerró: 6 cifras, tolerancia ±0.005 USD, diferencia máxima 0.0018; primer mes a 35: 1934-02
- Revisiones de datos históricos: ninguna
- Nota: primera publicación de la serie: no hay corrida anterior con que comparar

## 2026-10-07 · numerador

- Descargas:
  - coin_metrics_btc_oferta: https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=SplyCur,BlkCnt,IssTotNtv&frequency=1d&page_size=10000, sha256 ae3c1339354c7a7f8613aa9a701d4b3395d354fa332c55a081c870b3ff327a24
  - usgs_ds140_oro: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-gold-2022.xlsx, sha256 025f3eb98adb606cc214b82caa70646b80cf9debdf6544dbafce361283c1c480
  - usgs_ds140_plata: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-silver-2021.xlsx, sha256 e57b952a5fd469291341bf275fbaa1c20dfd0caa9b40f383a2a19076efa9e997
  - censo_hvs_tabla7: https://www.census.gov/housing/hvs/data/histtab7.xlsx, sha256 335592c7de815c450495abeeea8a0d64d333e4760109a5b04b5eca4ee5ca8ebc
  - censo_hvs_tabla7a: https://www.census.gov/housing/hvs/data/hist_tab_7a_v2025.xlsx, sha256 3777bf395606d5564c2fce3447f5e757f0628ce59354df057db0e0bcbc3338b2
  - censo_popest_viviendas: https://www2.census.gov/programs-surveys/popest/tables/2020-2025/housing/totals/NST-EST2025-HU.xlsx, sha256 a1ff31e0dc318bb00e4ac546dbba45601adb17ab56f31893e01fc29b072f94a8
  - z1_F51_1_t: https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip#csv/F51_1_t.csv, sha256 248c042f03760a82538174b106db0229dbede1d41cc1fd4aa23dd076f1b41f74
  - z1_F51_1_s: https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip#csv/F51_1_s.csv, sha256 3c7fe82fe4ac8a0b6c9bd481cb750c0c631e7d85b447d5910d673839eb1fb851
  - z1_F3_s: https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip#csv/F3_s.csv, sha256 c492030ef2bda0c92a9e73b8fa372f53642fb53763ba07f1fb5f6a4312bdeb2b
  - z1_F3_t: https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip#csv/F3_t.csv, sha256 8420423aeacd990f3f1bdb018b3c120ad78bf769f0f72ab4a26ddc6b50c9aeea
  - z1_D3_s: https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip#csv/D3_s.csv, sha256 50e6fbbd07de3f42a4ddf1f5be8eaf16dbf94032406de870ec3eaae3793fecf7
  - z1_html_F51_1_t: https://www.federalreserve.gov/releases/z1/current/html/F51_1_t.htm, sha256 cda1b00773fc6b58cefe5be82d813f84d9a0157aefadb12b63e250b36c0fed3e
  - z1_html_F51_1_s: https://www.federalreserve.gov/releases/z1/current/html/F51_1_s.htm, sha256 0b91363c5eb7b8e7acf46ce4b8aa7b5cd44650de84caa863c198f2950f506863
  - z1_html_F3_s: https://www.federalreserve.gov/releases/z1/current/html/F3_s.htm, sha256 e228d32ec728bf94de5de98027277f49a389a5a4e9991b1be25694db15eb3305
  - z1_html_D3_s: https://www.federalreserve.gov/releases/z1/current/html/D3_s.htm, sha256 dbdd070b2533fda842b414c2b8657f0529efead4eb0b1b684e82d48d2e72a7e4
  - fred_hvs_trimestral: https://fred.stlouisfed.org/graph/fredgraph.csv?id=ETOTALUSQ176N, sha256 15e6a2d66c7e790b94f51c16e6e59cd684a4c1fac60013c9b85d593e98c0cd5b
- Series:
  - BTC: emisión del año según el calendario del protocolo: se publica, 2009 a 2025, 17 filas (flujo; BTC; suma de los bloques del año calendario (UTC); subsidio de cada bloque según Bitcoin Core, por los bloques observados del año; A-N0-1 A-N0-2 A-N0-13)
  - BTC: emisión observada del año: se publica, 2009 a 2025, 17 filas (flujo; BTC; suma de los bloques del año calendario (UTC); suma de IssTotNtv; A-N0-1 A-N0-2 A-N0-13)
  - BTC: oferta en circulación a fin de año: se publica, 2009 a 2025, 17 filas (stock; BTC; oferta al cierre del 31 de diciembre (00:00 UTC del 1 de enero), lectura de Coin Metrics; A-N0-1 A-N0-2 A-N0-13)
  - BTC: tasa de crecimiento de la oferta en circulación: se publica, 2010 a 2025, 16 filas (tasa de crecimiento de la oferta; % anual; oferta a fin de año sobre la oferta a fin del año anterior, menos uno (cálculo propio); A-N0-1 A-N0-2 A-N0-13)
  - BTC: porcentaje del máximo de 21 millones ya emitido, a fin de año: se publica, 2009 a 2025, 17 filas (proporción; % de 21000000 BTC; oferta al cierre del 31 de diciembre (00:00 UTC del 1 de enero), lectura de Coin Metrics dividida por MAX_MONEY (cálculo propio); A-N0-1 A-N0-2 A-N0-13)
  - BTC: oferta en circulación a la fecha de la descarga: se publica, 2026 a 2026, 1 filas (stock; BTC; último día con dato en la descarga, cierre a las 00:00 UTC del día siguiente; A-N0-1 A-N0-2 A-N0-13)
  - BTC: porcentaje del máximo de 21 millones ya emitido, a la fecha de la descarga: se publica, 2026 a 2026, 1 filas (proporción; % de 21000000 BTC; último día con dato en la descarga, dividido por MAX_MONEY (cálculo propio); A-N0-1 A-N0-2 A-N0-13)
  - BTC: elasticidad de la oferta respecto del precio: se publica, 2026 a 2026, 1 filas (elasticidad de la oferta; d ln(oferta) / d ln(precio); cero por construcción: el subsidio por bloque es función de la altura del bloque y de nada más (Bitcoin Core, GetBlockSubsidy); A-N0-1 A-N0-12)
  - Oro: producción minera mundial anual: se publica, 1900 a 2025, 126 filas (flujo; toneladas métricas de contenido de metal; producción de mina del año calendario; Data Series 140 en todo su rango y Mineral Commodity Summaries después, con el último año estimado; A-N0-1 A-N0-3 A-N0-4 A-N0-13)
  - Oro: cota superior de la tasa de crecimiento del stock (producción del año / producción acumulada desde 1900): se publica, 1901 a 2025, 125 filas (cota superior de la tasa de crecimiento del stock; % anual; producción del año dividida por la suma de la producción mundial de 1900 al año anterior (cálculo propio); A-N0-1 A-N0-3 A-N0-5 A-N0-6 A-N0-13)
  - Plata: producción minera mundial anual: se publica, 1900 a 2025, 126 filas (flujo; toneladas métricas de contenido de metal; producción de mina del año calendario; Data Series 140 en todo su rango y Mineral Commodity Summaries después, con el último año estimado; A-N0-1 A-N0-3 A-N0-4 A-N0-13)
  - Plata: cota superior de la tasa de crecimiento del stock (producción del año / producción acumulada desde 1900): se publica, 1901 a 2025, 125 filas (cota superior de la tasa de crecimiento del stock; % anual; producción del año dividida por la suma de la producción mundial de 1900 al año anterior (cálculo propio); A-N0-1 A-N0-3 A-N0-5 A-N0-6 A-N0-13)
  - Acciones de EE.UU.: emisión neta, todos los sectores: se publica, 1946 a 2025, 80 filas (flujo; millones de USD; flujo del año calendario a valor de transacción: hasta 1951 el dato anual de la Junta; desde 1952 la media de los cuatro trimestres a tasa anual ajustada; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: valor de mercado a fin de año, todos los sectores: se publica, 1945 a 2025, 81 filas (stock; millones de USD; saldo a fin del cuarto trimestre, a valor de mercado, sin ajuste estacional; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta como porcentaje del valor de mercado del año anterior, todos los sectores: se publica, 1946 a 2025, 80 filas (tasa de crecimiento de la oferta; % del valor de mercado de fin del año anterior; emisión neta del año dividida por el saldo a valor de mercado del cuarto trimestre del año anterior (cálculo propio); mezcla cantidades y precios y lo declara; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta, sociedades no financieras: se publica, 1946 a 2025, 80 filas (flujo; millones de USD; flujo del año calendario a valor de transacción: hasta 1951 el dato anual de la Junta; desde 1952 la media de los cuatro trimestres a tasa anual ajustada; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: valor de mercado a fin de año, sociedades no financieras: se publica, 1945 a 2025, 81 filas (stock; millones de USD; saldo a fin del cuarto trimestre, a valor de mercado, sin ajuste estacional; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta como porcentaje del valor de mercado del año anterior, sociedades no financieras: se publica, 1946 a 2025, 80 filas (tasa de crecimiento de la oferta; % del valor de mercado de fin del año anterior; emisión neta del año dividida por el saldo a valor de mercado del cuarto trimestre del año anterior (cálculo propio); mezcla cantidades y precios y lo declara; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta, sectores financieros internos: se publica, 1946 a 2025, 80 filas (flujo; millones de USD; flujo del año calendario a valor de transacción: hasta 1951 el dato anual de la Junta; desde 1952 la media de los cuatro trimestres a tasa anual ajustada; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: valor de mercado a fin de año, sectores financieros internos: se publica, 1945 a 2025, 81 filas (stock; millones de USD; saldo a fin del cuarto trimestre, a valor de mercado, sin ajuste estacional; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta como porcentaje del valor de mercado del año anterior, sectores financieros internos: se publica, 1946 a 2025, 80 filas (tasa de crecimiento de la oferta; % del valor de mercado de fin del año anterior; emisión neta del año dividida por el saldo a valor de mercado del cuarto trimestre del año anterior (cálculo propio); mezcla cantidades y precios y lo declara; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta, resto del mundo: se publica, 1946 a 2025, 80 filas (flujo; millones de USD; flujo del año calendario a valor de transacción: hasta 1951 el dato anual de la Junta; desde 1952 la media de los cuatro trimestres a tasa anual ajustada; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: valor de mercado a fin de año, resto del mundo: se publica, 1945 a 2025, 81 filas (stock; millones de USD; saldo a fin del cuarto trimestre, a valor de mercado, sin ajuste estacional; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Acciones de EE.UU.: emisión neta como porcentaje del valor de mercado del año anterior, resto del mundo: se publica, 1946 a 2025, 80 filas (tasa de crecimiento de la oferta; % del valor de mercado de fin del año anterior; emisión neta del año dividida por el saldo a valor de mercado del cuarto trimestre del año anterior (cálculo propio); mezcla cantidades y precios y lo declara; A-N0-1 A-N0-7 A-N0-9 A-N0-13)
  - Deuda de EE.UU.: títulos de deuda en circulación, todos los sectores: se publica, 1945 a 2025, 81 filas (stock; millones de USD; saldo a fin del cuarto trimestre, sin ajuste estacional; incluye los títulos emitidos por el resto del mundo en manos de residentes; A-N0-1 A-N0-8 A-N0-9 A-N0-13)
  - Deuda de EE.UU.: variación anual de los títulos de deuda en circulación: se publica, 1946 a 2025, 80 filas (tasa de crecimiento de la oferta; % anual; saldo de fin de año sobre el de fin del año anterior, menos uno (cálculo propio); A-N0-1 A-N0-8 A-N0-9 A-N0-13)
  - Deuda de EE.UU.: deuda de los sectores no financieros internos (títulos y préstamos): se publica, 1945 a 2025, 81 filas (stock; millones de USD; saldo a fin del cuarto trimestre, ajustado por estacionalidad; A-N0-1 A-N0-8 A-N0-9 A-N0-13)
  - Deuda de EE.UU.: variación anual de la deuda de los sectores no financieros internos: se publica, 1946 a 2025, 80 filas (tasa de crecimiento de la oferta; % anual; saldo de fin de año sobre el de fin del año anterior, menos uno (cálculo propio); A-N0-1 A-N0-8 A-N0-9 A-N0-13)
  - Viviendas de EE.UU.: parque total (HVS, Tabla 7): se publica, 1965 a 2025, 61 filas (stock; miles de viviendas; promedio de las estimaciones mensuales del año; cada año con el valor de su base original, y la base revisada del Censo solo como denominador de la tasa del año siguiente (A-N0-10); A-N0-1 A-N0-10 A-N0-11 A-N0-13)
  - Viviendas de EE.UU.: tasa de crecimiento del parque (HVS, Tabla 7): se publica, 1966 a 2025, 60 filas (tasa de crecimiento de la oferta; % anual; parque del año sobre el del año anterior en la misma base, menos uno (cálculo propio); A-N0-1 A-N0-10 A-N0-11 A-N0-13)
  - Viviendas de EE.UU.: parque total revisado con los controles de vivienda (HVS, Tabla 7a): no se publica: NO MEDIDO: sin validación externa
  - Viviendas de EE.UU.: tasa de crecimiento del parque revisado (HVS, Tabla 7a): no se publica: NO MEDIDO: sin validación externa
  - Viviendas de EE.UU.: parque total al 1 de julio (Population Estimates): se publica, 2020 a 2025, 6 filas (stock; viviendas; existencias al 1 de julio, estimadas desde la base del Censo de 2020 (vintage 2025); A-N0-1 A-N0-10 A-N0-11 A-N0-13)
  - Viviendas de EE.UU.: tasa de crecimiento del parque al 1 de julio (Population Estimates): se publica, 2021 a 2025, 5 filas (tasa de crecimiento de la oferta; % anual; parque al 1 de julio sobre el del 1 de julio anterior, menos uno (cálculo propio); A-N0-1 A-N0-10 A-N0-11 A-N0-13)
  - Oro: existencias sobre la superficie: no se publica: NO MEDIDO como serie: la única serie de existencias es del World Gold Council, clase (c); su cifra va como estimación de terceros en citas_terceros.csv, fuera de todo cálculo (A-N0-6, A-D0-28)
  - Oro: stock-to-flow: no se publica: NO MEDIDO como serie: sin existencias abiertas no hay cociente; la cota superior del crecimiento del stock es lo más que se puede publicar (A-N0-5, A-N0-6)
  - Plata: existencias: no se publica: NO MEDIDO: no se encontró ninguna fuente abierta de existencias de plata (FUENTES.md, N0.5.5)
  - Acciones: cantidad en circulación o emisión neta global: no se publica: NO MEDIDO: sin fuente abierta (la WFE es de clase (c), FUENTES.md D0.9); lo que hay es EE.UU. (A-N0-7)
  - Viviendas: parque global: no se publica: NO MEDIDO: UN-Habitat no se leyó y no hay otra fuente abierta leída; lo que hay es EE.UU. (A-N0-10)
  - Deuda: títulos de deuda en circulación, suma de economías: no se publica: NO MEDIDO: es la suma de 49 economías declarantes al BIS de A-D0-22, pendiente de implementar; nunca "global" (A-N0-8)
  - Deuda de EE.UU.: elasticidad de la oferta respecto del precio: no se publica: NO MEDIDO: la deuda no tiene un precio comparable (decisión del dueño, FUENTES.md N0.10.5, punto 4; A-N0-12)
  - Oro: respuesta observada de la oferta al precio: no se publica: pendiente: familia "respuesta observada de la oferta al precio"; antes de calcular, un paso 0 corto de las fuentes de precio y un prerregistro en SUPUESTOS.md con su propio commit (A-N0-12)
  - Plata: respuesta observada de la oferta al precio: no se publica: pendiente: familia "respuesta observada de la oferta al precio"; antes de calcular, un paso 0 corto de las fuentes de precio y un prerregistro en SUPUESTOS.md con su propio commit (A-N0-12)
  - Viviendas de EE.UU.: respuesta observada de la oferta al precio: no se publica: pendiente: familia "respuesta observada de la oferta al precio"; antes de calcular, un paso 0 corto de las fuentes de precio y un prerregistro en SUPUESTOS.md con su propio commit (A-N0-12)
  - Acciones de EE.UU.: respuesta observada de la oferta al precio: no se publica: pendiente: familia "respuesta observada de la oferta al precio"; antes de calcular, un paso 0 corto de las fuentes de precio y un prerregistro en SUPUESTOS.md con su propio commit (A-N0-12)
- Validación:
  - btc: gate contra el calendario del protocolo (Bitcoin Core) a la misma altura de bloque cerró: 17 comparaciones, tolerancia oferta ≤ calendario y diferencia ≤ 0.001 %, diferencia máxima 0.0004
  - oro_produccion_mundial_t: control contra el total mundial del BGS (World Mineral Production 2020-24) cerró: 5 comparaciones, tolerancia ±5 %, diferencia máxima 4.9180
  - plata_produccion_mundial_t: control contra el total mundial del BGS (World Mineral Production 2020-24) cerró: 5 comparaciones, tolerancia ±5 %, diferencia máxima 10.8589; en disputa (control): 2020, 2021, 2022, 2024
  - z1_F51_1_t: gate contra la tabla F51.1.t del Z.1 en HTML (mismo emisor) cerró: 36 comparaciones, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0480
  - z1_F51_1_s: gate contra la tabla F51.1.s del Z.1 en HTML (mismo emisor) cerró: 36 comparaciones, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0490
  - z1_F3_s: gate contra la tabla F3.s del Z.1 en HTML (mismo emisor) cerró: 9 comparaciones, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0470
  - z1_D3_s: gate contra la tabla D3.s del Z.1 en HTML (mismo emisor) cerró: 54 comparaciones, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0490
  - viviendas_eeuu_parque_hvs_miles: gate contra la identidad de la propia tabla, total = vacantes + ocupadas (gate de transporte) cerró: 66 comparaciones, tolerancia ±1.5 mil, diferencia máxima 1.0000
  - viviendas_eeuu_parque_hvs_7a_miles: gate contra la identidad de la propia tabla, total = vacantes + ocupadas (gate de transporte) NO cerró: 26 comparaciones, tolerancia ±1.5 mil, diferencia máxima 2.0000; fuera de tolerancia: 2017: 137221 contra 17381 + 119842
  - viviendas_eeuu_parque_hvs_7a_miles: control contra FRED ETOTALUSQ176N, media de los cuatro trimestres, hasta 2019 cerró: 19 comparaciones, tolerancia ±1 mil, diferencia máxima 3.7500; en disputa (control): 2001, 2002, 2004, 2006, 2007, 2011, 2017; de 2020 en adelante no se compara porque FRED no recoge la Vintage 2025; diferencia FRED menos Tabla 7a, en miles: 2020: -5.25, 2021: -20.00, 2022: -31.75, 2023: -40.25, 2024: -58.25, 2025: -24.75
  - viviendas_eeuu_parque_popest_unidades: control contra Population Estimates (parque al 1 de julio) cerró: 6 comparaciones, tolerancia ±0.5 %, diferencia máxima 0.0661
- Revisiones de datos históricos: ninguna
- Nota: las tablas del Z.1 se extraen del paquete ZIP con sus bytes exactos; el ZIP, el HTML del Z.1 y el CSV de FRED quedan fuera del repositorio, con su hash en el manifiesto (A-N0-14)
- Nota: las cifras del BGS son lecturas a mano de British Geological Survey, World Mineral Production 2020-24 (Idoine y otros, 2026), tablas "Mine production of gold" y "Mine production of silver", fila "World total", kilogramos de contenido de metal; incluye estimaciones de minería artesanal y redondea el total mundial (https://nora.nerc.ac.uk/id/eprint/541620/1/WMP_2020%20to%202024.pdf, SHA-256 260a9891d28082990e49a75b97c386da1499af1ba59aad8743407c0c57aa55c6, leído el 2026-10-07); "World Mineral Statistics contributed by permission of the British Geological Survey"

## 2026-10-07 · dinero histórico

- Fuentes:
  - junta_bms_1914_1941: https://fraser.stlouisfed.org/files/docs/publications/bms/1914-1941/BMS14-41_complete.pdf, sha256 ca7b8e3161d21ecf3bd804accd901eb3234397146f5cd091d6388e1027d2387e
  - junta_bms_1941_1970: https://fraser.stlouisfed.org/files/docs/publications/bms/1941-1970/BMS41-70_complete.pdf, sha256 c04bd75916599fcb8d1c961024012a65f39d7447b2e499ac07d0a85866c3db4d
  - censo_hsus_1960_cap_x: https://www2.census.gov/library/publications/1960/compendia/hist_stats_colonial-1957/hist_stats_colonial-1957-chX.pdf, sha256 39861a3930f44581eae24ee16bc34524048f6c7b51f0054e4dfcdf68963b9828
  - fred_nber_m14144c: https://fred.stlouisfed.org/graph/fredgraph.csv?id=M1444CUSM027SNBR, sha256 ba9316a21942961f56ba1376a04e51dc1cfbf09cf0e0a47073cc9719d6fab521
- Transcripción:
  - 2082 celdas leídas dos veces; 1 discrepancias, resueltas releyendo la imagen
  - resuelta: tabla_1_1_B 1955-11 plazo_ajustados: A=49.? B=49.8 -> 49.8 (Relectura de la celda en el escaneo ampliado a 900 ppp (Banking and Monetary Statistics 1941-1970, p. 20): el último dígito tiene una mancha de tinta; el glifo muestra dos lazos cerrados, como el 8 de las celdas vecinas, y no la cola abierta del 3. Lectura con reserva: queda registrada aquí y en el changelog; la serie sin ajustar no se publica (A-D0-31).)
  - gate de sumas: Tabla 9 y continuación, todas las identidades cuadran; superposición de 1941: igual
  - control de sumas, en disputa: tabla_1_1_A 1949-03: total = efectivo + vista: impreso 111.2, suma de componentes 113.3 (diferencia -2.1)
  - control de sumas, en disputa: tabla_1_1_B 1950-12: total = efectivo + vista: impreso 119.2, suma de componentes 118.8 (diferencia 0.4)
- Series:
  - Efectivo y depósitos en bancos comerciales de EE.UU., fechas de balance (1892-1946): se publica, 1892-06 a 1946-12, 79 observaciones (millones de USD; saldo del día de balance (call date); anual, 30 de junio, hasta 1922; semestral, junio y diciembre, desde 1923; A-D0-17 A-D0-18 A-D0-19 A-D0-31 A-D0-32 A-D0-33)
  - Efectivo y depósitos en bancos comerciales de EE.UU., mensual, ajustada por estacionalidad (1947-1958): se publica, 1947-01 a 1958-12, 144 observaciones (miles de millones de USD; promedio mensual de cifras diarias; A-D0-17 A-D0-19 A-D0-31 A-D0-32 A-D0-33)
  - Efectivo y depósitos en bancos comerciales de EE.UU., mensual, sin ajustar (1947-1958): no se publica: NO MEDIDO: sin validación externa; la segunda fuente (NBER m14144b, 1955-1969) no está en FRED y data.nber.org veda a los programas (A-D0-31)
- Validación:
  - dinero_eeuu_1892_1946: gate contra Oficina del Censo de EE.UU., Historical Statistics of the United States, Colonial Times to 1957 (1960), capítulo X, series X 266-274 (PDF), 9 filas de junio leídas a mano cerró: 9 fechas de balance, 61 cifras, tolerancia igualdad en millones de USD
  - dinero_eeuu_1947_1958: gate contra NBER m14144c vía FRED (M1444CUSM027SNBR) cerró: 144 meses, tolerancia ±0.1 miles de millones de USD, diferencia máxima 0.1000; diferencia mediana 0.00
- Revisiones de datos históricos: ninguna

## 2026-10-07 · denominador

- Descargas:
  - junta_h6: https://www.federalreserve.gov/releases/h6/data/FRB_h6_xml.zip, sha256 7ab987141ee43c5bc940f917c0c6d14e7ae8b001bea053eba440f2b13e3c0d80, actualizada el 2026-09-23
  - junta_h10: https://www.federalreserve.gov/releases/h10/data/FRB_h10_xml.zip, sha256 8b0642fb280b73e06eeaa062de7f00eb679ad0c9b508d67f5949557f3c09018d, actualizada el 2026-10-05
  - junta_h41: https://www.federalreserve.gov/releases/h41/data/FRB_h41_xml.zip, sha256 1eb4daf1ff2966cb3c7083c9703e9cba9163bbb1d41a6e2ad1af6a0c94694fe2, actualizada el 2026-10-01
  - bce_m2_ajustada: https://data-api.ecb.europa.eu/service/data/BSI/M.U2.Y.V.M20.X.1.U2.2300.Z01.E?format=csvdata, sha256 b67f33549018ce47bca486a1ccac737429b6b24b3cf78f61dfef9c63b1f364ab, copia del 2026-10-05
  - bce_m2_sin_ajustar: https://data-api.ecb.europa.eu/service/data/BSI/M.U2.N.V.M20.X.1.U2.2300.Z01.E?format=csvdata, sha256 b8aa09ee2d317382d5793c60774515753299d8eaa932ece9dce9cee067be7363, copia del 2026-10-05
  - bce_balance_eurosistema: https://data-api.ecb.europa.eu/service/data/ILM/W.U2.C.T000000.Z5.Z01?format=csvdata, sha256 1d911aa8803869fbf5086dbbeb98f561735729eb463c06383cb4e6a69946ee70, copia del 2026-10-05
  - boj_m2: https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=MD02&code=MAM1NAM2M2MO,MAM1XAM2M2MO,MAM1NAM3M3MO,MAM1NEM3M3MO,MAMS3ANM2C,MAMS3ENM2C,MAMS1ANM2C,MAMS1ENM2C, sha256 3399258c91441e1a2fbb45a41b9be4124c4d46060f32a6b71f8b41591ef14e28
  - boj_balance: https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=BS01&code=MABJMTA,MABJMA5,MABJML1,MABJML11, sha256 56fa6cab48738135cb59a070fb5e7a8f6b221f5eac8bb55196dad648cfc9c158
  - ocde_china_dinero_amplio: https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_MONAGG,/CHN.M.MABM.XDC.....?format=csvfilewithlabels, sha256 73ec664589151ff2d526d485eeb34de2ee10ac3d61d09b87d1955162bf25c93a
  - bis_cbta_cn: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.CN?format=csv, sha256 5e58f8aa8cec85e60b5d007585c2203fe0970a79bafe8b2e458c1bf9c4dd9ce3
  - junta_h6_html: https://www.federalreserve.gov/releases/h6/current/default.htm, sha256 0cb49bc0d836c460a1b3d03471eef522605d617b332f114a2a8c8733b68f0860, actualizada el 2026-09-22
  - fred_walcl: https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL, sha256 1900a650f4256dd3635ca58adf33d7f1889d4777cc8c36a562f20542c24fa6f9, actualizada el 2026-10-01
  - bis_cbta_us: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.US?format=csv, sha256 f195b26a9bdb862942a0797917fbc2bb40aa8523e4f8f4e6f1baf15560896a21
  - bde_m2_ajustada: https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0112.csv, sha256 8091dc2855f54594e6737c8a6a9891a235e5a261aa251308ae0f5dbcfd52de8c, actualizada el 2026-09-30
  - bde_m2_sin_ajustar: https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0110.csv, sha256 d1f4294b5480d600151e7d1ce132929dfa35e0cbd0633508a8441d1521cb3eb6, actualizada el 2026-09-30
  - bis_cbta_xm: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.XM?format=csv, sha256 80e2e6506782a2acc08b5c453ccdda9f168bca79d33e4cda3d1a3afff30fb7ff
  - estat_m2_japon: https://dashboard.e-stat.go.jp/api/1.0/Json/getData?Lang=EN&IndicatorCode=0702010200000010010, sha256 0cc907ef81a19f548e9ea5e28d95cceb343a33104a7112e04ec1def3881043b6
  - fred_fmi_m2_japon: https://fred.stlouisfed.org/graph/fredgraph.csv?id=MYAGM2JPM189N, sha256 f88101d7cb47244df49b70e7581d16f003fb6ea9a29d7ce31a12040721214db2, actualizada el 2020-02-25
  - bis_cbta_jp: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.JP?format=csv, sha256 273fa9135a25ebafb412a15ec5432e8f40511f3cd6268eb5c1031019422cf7f9
  - bis_xru_xm: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.XM?format=csv, sha256 5635a8dcb98926b8dea0ac3e2f991e893e9448a4012793a063290be0a5e241dd
  - bis_xru_jp: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.JP?format=csv, sha256 02a7fbcb75b1aafe40bc64af0d3b5b1ae2a9103c2d63445d02e32aced012a8d5
  - bis_xru_cn: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.CN?format=csv, sha256 fc45e7fe40ebe05dc69715628d8e872dcababdb9e6b43df82ba964ba3f27b577
- Series:
  - M2+CDs de Japón (Money Supply, sin bancos extranjeros en Japón; serie discontinuada por el BoJ, 1967–1999): se publica, 1967-01 a 1999-03, 387 meses (100 millones de JPY; promedio de saldos del mes; A-D0-1 A-D0-6 A-D0-8 A-D0-34 A-D0-35)
  - M2+CDs de Japón (Money Supply, con bancos extranjeros en Japón; serie discontinuada por el BoJ, 1998–2008): se publica, 1998-04 a 2008-04, 121 meses (100 millones de JPY; promedio de saldos del mes; A-D0-1 A-D0-6 A-D0-8 A-D0-34 A-D0-35)
  - M2 de EE.UU.: se publica, 1959-01 a 2026-08, 812 meses (miles de millones de USD; promedio mensual de cifras diarias; A-D0-1 A-D0-2 A-D0-3)
  - M2 de EE.UU., sin ajustar: se publica, 1959-01 a 2026-08, 812 meses (miles de millones de USD; promedio mensual de cifras diarias; A-D0-1 A-D0-2 A-D0-3)
  - M2 de la Eurozona: se publica, 1980-01 a 2026-08, 560 meses (millones de EUR; saldo a fin de mes; A-D0-1 A-D0-4 A-D0-5 A-D0-7)
  - M2 de la Eurozona, sin ajustar: se publica, 1980-01 a 2026-08, 560 meses (millones de EUR; saldo a fin de mes; A-D0-1 A-D0-4 A-D0-5 A-D0-7)
  - M2 de Japón: se publica, 2003-04 a 2026-08, 281 meses (100 millones de JPY; promedio de saldos del mes; A-D0-1 A-D0-6 A-D0-8)
  - Dinero amplio de China (M3 de la OCDE): no se publica: NO MEDIDO: sin validación externa
  - Balance de la Reserva Federal: total de activos, consolidado: se publica, 2002-12 a 2026-09, 286 meses (millones de USD; nivel del último miércoles del mes; A-D0-1 A-D0-14 A-D0-15)
  - Balance del Eurosistema: total de activos: se publica, 1999-01 a 2026-09, 333 meses (millones de EUR; cierre del último viernes del mes; A-D0-1 A-D0-7 A-D0-14 A-D0-16)
  - Balance del Banco de Japón: total de activos: se publica, 1998-04 a 2026-08, 341 meses (100 millones de JPY; saldo a fin de mes; A-D0-1 A-D0-8 A-D0-16)
  - Balance del Banco Popular de China: total de activos (BIS): no se publica: NO MEDIDO: sin validación externa
  - Tipo de cambio: USD por EUR: se publica, 1999-01 a 2026-09, 333 meses (USD por EUR; tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes; A-D0-1 A-D0-10)
  - Tipo de cambio: JPY por USD: se publica, 1971-01 a 2026-09, 669 meses (JPY por USD; tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes; A-D0-1 A-D0-10)
  - Tipo de cambio: CNY por USD: se publica, 1981-01 a 2026-09, 549 meses (CNY por USD; tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes; A-D0-1 A-D0-10)
  - Efectivo y depósitos en bancos comerciales de EE.UU., fechas de balance (1892-1946): se publica, 1892-06 a 1946-12, 79 meses (millones de USD; saldo del día de balance (call date); anual, 30 de junio, hasta 1922; semestral, junio y diciembre, desde 1923; A-D0-17 A-D0-18 A-D0-19 A-D0-31 A-D0-32 A-D0-33)
  - Efectivo y depósitos en bancos comerciales de EE.UU., mensual, ajustada por estacionalidad (1947-1958): se publica, 1947-01 a 1958-12, 144 meses (miles de millones de USD; promedio mensual de cifras diarias; A-D0-17 A-D0-19 A-D0-31 A-D0-32 A-D0-33)
  - Efectivo y depósitos en bancos comerciales de EE.UU., mensual, sin ajustar (1947-1958): no se publica: NO MEDIDO: sin validación externa; la segunda fuente (NBER m14144b, 1955-1969) no está en FRED y data.nber.org veda a los programas (A-D0-31)
  - Riqueza: valor de los inmuebles: no se publica: NO MEDIDO: no hay una serie global con licencia abierta; la estimación de Savills va como cifra citada (A-D0-24, A-D0-28)
  - Riqueza: oro sobre la superficie (cantidad): no se publica: NO MEDIDO: la única serie de existencias es del World Gold Council, clase (c); su cifra va como cifra citada (A-D0-24, A-D0-28)
  - Riqueza total: no se publica: NO MEDIDO: los informes de riqueza global son (c) o no se pudieron leer (A-D0-24)
  - Riqueza: títulos de deuda en circulación: no se publica: NO MEDIDO: pendiente de implementar la suma de las economías que declaran al BIS (A-D0-22)
  - Riqueza: capitalización bursátil: no se publica: NO MEDIDO: pendiente de implementar la lectura del agregado WLD del Banco Mundial (A-D0-23)
  - Riqueza: capitalización de BTC: no se publica: NO MEDIDO: pendiente de implementar la lectura de CapMrktCurUSD de Coin Metrics (A-R0-4)
- Validación:
  - m2_eeuu: gate contra la Tabla 1 del H.6 en HTML cerró: 17 meses, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0000
  - m2_eeuu_sin_ajustar: gate contra la Tabla 1 del H.6 en HTML cerró: 17 meses, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0000
  - balance_fed: gate contra BIS WS_CBTA (EE.UU.) cerró: 284 meses, tolerancia ±5 millones de USD, diferencia máxima 0.0000; control contra FRED WALCL: 1242 semanas, todas iguales
  - m2_eurozona: gate contra el Banco de España (cuadros 1.12 y 1.10) cerró: 3 meses, tolerancia ±0.5 millones de EUR, diferencia máxima 0.0000
  - m2_eurozona_sin_ajustar: gate contra el Banco de España (cuadros 1.12 y 1.10) cerró: 3 meses, tolerancia ±0.5 millones de EUR, diferencia máxima 0.4867
  - balance_eurosistema: gate contra BIS WS_CBTA (zona del euro), viernes de la última semana hábil cerró: 332 meses, tolerancia ±0.5 millones de EUR, diferencia máxima 0.0000
  - m2_japon: gate contra e-Stat Statistics Dashboard cerró: 281 meses, tolerancia ±0.5 100 millones de JPY, diferencia máxima 0.0000
  - m2cd_japon_1967_1999: gate contra FRED MYAGM2JPM189N (FMI, IFS), desde el inicio a 1998-03 cerró: 375 meses, tolerancia ±0.5 100 millones de JPY, diferencia máxima 0.0000; superposición con m2cd_japon_1998_2008: 12 meses, m2cd_japon_1998_2008 entre +0.410 % y +0.483 % (media +0.450 %); no se empalma
  - m2cd_japon_1998_2008: gate contra FRED MYAGM2JPM189N (FMI, IFS), 1998-04 a 2003-03 cerró: 60 meses, tolerancia ±0.5 100 millones de JPY, diferencia máxima 0.0000; superposición con m2_japon: 61 meses, m2_japon entre -0.590 % y -0.422 % (media -0.501 %); no se empalma
  - balance_boj: gate contra BIS WS_CBTA (Japón) cerró: 340 meses, tolerancia ±0.5 100 millones de JPY, diferencia máxima 0.0000
  - dinero_amplio_china: sin comparar contra lecturas a mano de una segunda fuente (hay 2 anclas y hacen falta 3)
  - balance_pboc: sin comparar contra lecturas a mano de una segunda fuente (hay 0 anclas y hacen falta 3)
  - usd_por_eur: control contra BIS WS_XRU, promedio mensual cerró: 332 meses, tolerancia ±0.5 %, diferencia máxima 0.6841; en disputa (control): 1 meses
  - jpy_por_usd: control contra BIS WS_XRU, promedio mensual cerró: 668 meses, tolerancia ±0.5 %, diferencia máxima 0.4879
  - cny_por_usd: control contra BIS WS_XRU, promedio mensual cerró: 548 meses, tolerancia ±0.5 %, diferencia máxima 0.1687
- Agregado:
  - Dinero amplio de tres economías en USD: M2 de EE.UU. y de la Eurozona, y de Japón M2+CDs hasta 2003-03 y M2 desde 2003-04: 1999-01 a 2026-08, 332 meses; tipo de cambio constante del 1999-01 (A-D0-11)
  - quiebre declarado: Japón pasa de m2cd_japon_1998_2008 a m2_japon, sin empalme: en este mes m2_japon es -0.422 % respecto de m2cd_japon_1998_2008, -23.9 miles de millones de USD del agregado
- Revisiones de datos históricos:
  - 281 revisiones: la fuente reescribió la historia; se resumen por serie
  - agregado_usd_tc_constante: 281 meses, de 2003-04-01 a 2026-08-01
- Nota: las series del BCE entran por copia bajada a mano (A-D0-29); los ZIP de la Junta y las fuentes de contraste quedan fuera del repositorio, con su hash en el manifiesto (A-D0-27)

## 2026-10-05 · ratios D0

- Pares contra M2 de EE.UU.:
  - Oro / M2 de EE.UU.: dato, 1960-01 a 2026-08, 800 meses; apto para métricas desde 1968-04 (691 meses, menos 10 con un valor en disputa)
  - BTC / M2 de EE.UU.: dato, 2013-01 a 2026-08, 164 meses; apto para métricas desde 2013-01 (164 meses, menos 0 con un valor en disputa)
- Nota: recalculados desde precios_mensuales.csv y denominador_dinero.csv, sin descargas

## 2026-10-05 · denominador

- Descargas:
  - junta_h6: https://www.federalreserve.gov/releases/h6/data/FRB_h6_xml.zip, sha256 7ab987141ee43c5bc940f917c0c6d14e7ae8b001bea053eba440f2b13e3c0d80
  - junta_h10: https://www.federalreserve.gov/releases/h10/data/FRB_h10_xml.zip, sha256 89b9ea2bb998c191e6cbf389afb1870fd7e8052344bb9138a55b6e284e17f22b
  - junta_h41: https://www.federalreserve.gov/releases/h41/data/FRB_h41_xml.zip, sha256 1eb4daf1ff2966cb3c7083c9703e9cba9163bbb1d41a6e2ad1af6a0c94694fe2
  - bce_m2_ajustada: https://data-api.ecb.europa.eu/service/data/BSI/M.U2.Y.V.M20.X.1.U2.2300.Z01.E?format=csvdata, sha256 b67f33549018ce47bca486a1ccac737429b6b24b3cf78f61dfef9c63b1f364ab
  - bce_m2_sin_ajustar: https://data-api.ecb.europa.eu/service/data/BSI/M.U2.N.V.M20.X.1.U2.2300.Z01.E?format=csvdata, sha256 b8aa09ee2d317382d5793c60774515753299d8eaa932ece9dce9cee067be7363
  - bce_balance_eurosistema: https://data-api.ecb.europa.eu/service/data/ILM/W.U2.C.T000000.Z5.Z01?format=csvdata, sha256 1d911aa8803869fbf5086dbbeb98f561735729eb463c06383cb4e6a69946ee70
  - boj_m2: https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=MD02&code=MAM1NAM2M2MO,MAM1XAM2M2MO,MAM1NAM3M3MO,MAM1NEM3M3MO,MAMS3ANM2C,MAMS3ENM2C,MAMS1ANM2C,MAMS1ENM2C, sha256 1247a7d57dbece8bd00defc588f954a0c267fb7111a92f9d3dbff8b0105ff57e
  - boj_balance: https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=BS01&code=MABJMTA,MABJMA5,MABJML1,MABJML11, sha256 c85c7de1508db0a9dc2aae1ef155245441448f0470d248cd484cff3f2c0dc298
  - ocde_china_dinero_amplio: https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_MONAGG,/CHN.M.MABM.XDC.....?format=csvfilewithlabels, sha256 73ec664589151ff2d526d485eeb34de2ee10ac3d61d09b87d1955162bf25c93a
  - bis_cbta_cn: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.CN?format=csv, sha256 5e58f8aa8cec85e60b5d007585c2203fe0970a79bafe8b2e458c1bf9c4dd9ce3
  - junta_h6_html: https://www.federalreserve.gov/releases/h6/current/default.htm, sha256 d8f051f22f671b33309fc3ec499a8bd71fadb470c67ae2751f2e602988979ba6
  - fred_walcl: https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL, sha256 1900a650f4256dd3635ca58adf33d7f1889d4777cc8c36a562f20542c24fa6f9
  - bis_cbta_us: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.US?format=csv, sha256 f195b26a9bdb862942a0797917fbc2bb40aa8523e4f8f4e6f1baf15560896a21
  - bde_m2_ajustada: https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0112.csv, sha256 8091dc2855f54594e6737c8a6a9891a235e5a261aa251308ae0f5dbcfd52de8c
  - bde_m2_sin_ajustar: https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0110.csv, sha256 d1f4294b5480d600151e7d1ce132929dfa35e0cbd0633508a8441d1521cb3eb6
  - bis_cbta_xm: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.XM?format=csv, sha256 80e2e6506782a2acc08b5c453ccdda9f168bca79d33e4cda3d1a3afff30fb7ff
  - estat_m2_japon: https://dashboard.e-stat.go.jp/api/1.0/Json/getData?Lang=EN&IndicatorCode=0702010200000010010, sha256 2fd33c5faa5e92ec76cbc223b0a42dd6cfc044ed1746686cee1e9837aa16cbac
  - bis_cbta_jp: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.JP?format=csv, sha256 273fa9135a25ebafb412a15ec5432e8f40511f3cd6268eb5c1031019422cf7f9
  - bis_xru_xm: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.XM?format=csv, sha256 5635a8dcb98926b8dea0ac3e2f991e893e9448a4012793a063290be0a5e241dd
  - bis_xru_jp: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.JP?format=csv, sha256 02a7fbcb75b1aafe40bc64af0d3b5b1ae2a9103c2d63445d02e32aced012a8d5
  - bis_xru_cn: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.CN?format=csv, sha256 fc45e7fe40ebe05dc69715628d8e872dcababdb9e6b43df82ba964ba3f27b577
- Series:
  - M2 de EE.UU.: se publica, 1959-01 a 2026-08, 812 meses (miles de millones de USD; promedio mensual de cifras diarias; A-D0-1 A-D0-2 A-D0-3)
  - M2 de EE.UU., sin ajustar: se publica, 1959-01 a 2026-08, 812 meses (miles de millones de USD; promedio mensual de cifras diarias; A-D0-1 A-D0-2 A-D0-3)
  - M2 de la Eurozona: se publica, 1980-01 a 2026-08, 560 meses (millones de EUR; saldo a fin de mes; A-D0-1 A-D0-4 A-D0-5 A-D0-7)
  - M2 de la Eurozona, sin ajustar: se publica, 1980-01 a 2026-08, 560 meses (millones de EUR; saldo a fin de mes; A-D0-1 A-D0-4 A-D0-5 A-D0-7)
  - M2 de Japón: se publica, 2003-04 a 2026-08, 281 meses (100 millones de JPY; promedio de saldos del mes; A-D0-1 A-D0-6 A-D0-8)
  - Dinero amplio de China (M3 de la OCDE): no se publica: NO MEDIDO: sin validación externa
  - Balance de la Reserva Federal: total de activos, consolidado: se publica, 2002-12 a 2026-09, 286 meses (millones de USD; nivel del último miércoles del mes; A-D0-1 A-D0-14 A-D0-15)
  - Balance del Eurosistema: total de activos: se publica, 1999-01 a 2026-09, 333 meses (millones de EUR; cierre del último viernes del mes; A-D0-1 A-D0-7 A-D0-14 A-D0-16)
  - Balance del Banco de Japón: total de activos: se publica, 1998-04 a 2026-08, 341 meses (100 millones de JPY; saldo a fin de mes; A-D0-1 A-D0-8 A-D0-16)
  - Balance del Banco Popular de China: total de activos (BIS): no se publica: NO MEDIDO: sin validación externa
  - Tipo de cambio: USD por EUR: se publica, 1999-01 a 2026-09, 333 meses (USD por EUR; tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes; A-D0-1 A-D0-10)
  - Tipo de cambio: JPY por USD: se publica, 1971-01 a 2026-09, 669 meses (JPY por USD; tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes; A-D0-1 A-D0-10)
  - Tipo de cambio: CNY por USD: se publica, 1981-01 a 2026-09, 549 meses (CNY por USD; tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes; A-D0-1 A-D0-10)
  - Efectivo y depósitos en bancos comerciales de EE.UU., fechas de balance (1892–1946): no se publica: NO MEDIDO: transcripción de las tablas de la Junta pendiente; se hace en un PR propio (A-D0-17, A-D0-19)
  - Efectivo y depósitos en bancos comerciales de EE.UU., mensual (1947–1958): no se publica: NO MEDIDO: transcripción de la Tabla 1.1 de la Junta pendiente; se hace en un PR propio (A-D0-17, A-D0-19)
  - Riqueza: valor de los inmuebles: no se publica: NO MEDIDO: no hay una serie global con licencia abierta; la estimación de Savills va como cifra citada (A-D0-24, A-D0-28)
  - Riqueza: oro sobre la superficie (cantidad): no se publica: NO MEDIDO: la única serie de existencias es del World Gold Council, clase (c); su cifra va como cifra citada (A-D0-24, A-D0-28)
  - Riqueza total: no se publica: NO MEDIDO: los informes de riqueza global son (c) o no se pudieron leer (A-D0-24)
  - Riqueza: títulos de deuda en circulación: no se publica: NO MEDIDO: pendiente de implementar la suma de las economías que declaran al BIS (A-D0-22)
  - Riqueza: capitalización bursátil: no se publica: NO MEDIDO: pendiente de implementar la lectura del agregado WLD del Banco Mundial (A-D0-23)
  - Riqueza: capitalización de BTC: no se publica: NO MEDIDO: pendiente de implementar la lectura de CapMrktCurUSD de Coin Metrics (A-R0-4)
- Validación:
  - m2_eeuu: gate contra la Tabla 1 del H.6 en HTML cerró: 17 meses, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0000
  - m2_eeuu_sin_ajustar: gate contra la Tabla 1 del H.6 en HTML cerró: 17 meses, tolerancia ±0.05 miles de millones de USD, diferencia máxima 0.0000
  - balance_fed: gate contra BIS WS_CBTA (EE.UU.) cerró: 284 meses, tolerancia ±5 millones de USD, diferencia máxima 0.0000; control contra FRED WALCL: 1242 semanas, todas iguales
  - m2_eurozona: gate contra el Banco de España (cuadros 1.12 y 1.10) cerró: 3 meses, tolerancia ±0.5 millones de EUR, diferencia máxima 0.0000
  - m2_eurozona_sin_ajustar: gate contra el Banco de España (cuadros 1.12 y 1.10) cerró: 3 meses, tolerancia ±0.5 millones de EUR, diferencia máxima 0.4867
  - balance_eurosistema: gate contra BIS WS_CBTA (zona del euro), viernes de la última semana hábil cerró: 332 meses, tolerancia ±0.5 millones de EUR, diferencia máxima 0.0000
  - m2_japon: gate contra e-Stat Statistics Dashboard cerró: 281 meses, tolerancia ±0.5 100 millones de JPY, diferencia máxima 0.0000
  - balance_boj: gate contra BIS WS_CBTA (Japón) cerró: 340 meses, tolerancia ±0.5 100 millones de JPY, diferencia máxima 0.0000
  - dinero_amplio_china: sin comparar contra lecturas a mano de una segunda fuente (hay 2 anclas y hacen falta 3)
  - balance_pboc: sin comparar contra lecturas a mano de una segunda fuente (hay 0 anclas y hacen falta 3)
  - usd_por_eur: control contra BIS WS_XRU, promedio mensual cerró: 332 meses, tolerancia ±0.5 %, diferencia máxima 0.6841; en disputa (control): 1 meses
  - jpy_por_usd: control contra BIS WS_XRU, promedio mensual cerró: 668 meses, tolerancia ±0.5 %, diferencia máxima 0.4879
  - cny_por_usd: control contra BIS WS_XRU, promedio mensual cerró: 548 meses, tolerancia ±0.5 %, diferencia máxima 0.1687
- Agregado:
  - M2 de tres economías (EE.UU., Eurozona y Japón), en USD: 2003-04 a 2026-08, 281 meses; tipo de cambio constante del 2003-04 (A-D0-11)
- Revisiones de datos históricos: ninguna
- Nota: primera publicación de las series: no hay corrida anterior con que comparar
- Nota: las series del BCE entran por copia bajada a mano (A-D0-29); los ZIP de la Junta y las fuentes de contraste quedan fuera del repositorio, con su hash en el manifiesto (A-D0-27)

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
