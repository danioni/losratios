# señales

Marco de señales para rebalancear un portafolio entre TQQQ, BTC y
stablecoins/USD. Este repositorio construye y actualiza las series que el marco
consume; no toma decisiones de portafolio ni las sugiere.

Hoy hay dos capas implementadas: **S2.x, contexto de liquidez**, y **la fase R,
precios mensuales y ratios**, que está [más abajo](#fase-r--precios-mensuales-y-ratios).

---

## Qué mide cada serie

### S2.1 · Liquidez neta de la Fed

Cuánto dinero del balance de la Reserva Federal está efectivamente circulando
por el sistema financiero, en vez de estar estacionado en la cuenta del Tesoro o
inmovilizado en el reverse repo.

```
S2.1 = WALCL − WDTGAL − RRPONTSYD
```

- **Unidad:** miles de millones de USD.
- **Frecuencia:** una observación por miércoles.
- **Historia:** desde el 1 de enero de 2020 (A-S2-12).

Los activos totales de la Fed son el numerador bruto de la liquidez. Los otros
dos términos son drenajes: lo que el Tesoro tiene depositado en su cuenta
general (TGA) y lo que las contrapartes dejaron en el reverse repo overnight
(ON RRP) son dólares que existen en el balance pero no están en el sistema.

### S2.2 · Variación de S2.1 a 13 semanas

```
S2.2 = ( S2.1(t) / S2.1(t − 13 semanas) − 1 ) × 100
```

- **Unidad:** porcentaje.
- **Ventana:** 13 semanas, parametrizable (A-S2-2).
- La comparación es **por fecha**, no por posición: si el miércoles de hace 91
  días no existe en la serie, el resultado queda vacío en vez de saltar a otra
  semana (A-S2-7).

---

## Fuentes

Las tres series salen de [FRED](https://fred.stlouisfed.org/), sin API key, por
`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`.

| Serie | Qué es | Frecuencia | Unidad declarada |
| --- | --- | --- | --- |
| [`WALCL`](https://fred.stlouisfed.org/series/WALCL) | Activos totales de la Fed, nivel de miércoles | Semanal (miércoles) | Millones de USD |
| [`WDTGAL`](https://fred.stlouisfed.org/series/WDTGAL) | Cuenta general del Tesoro (TGA), nivel de miércoles | Semanal (miércoles) | Millones de USD |
| [`RRPONTSYD`](https://fred.stlouisfed.org/series/RRPONTSYD) | Reverse repo overnight doméstico (ON RRP) | Diaria | Miles de millones de USD |

Las tres son niveles referidos al mismo miércoles, la convención del H.4.1. La
alternativa para el TGA, [`WTREGEN`](https://fred.stlouisfed.org/series/WTREGEN),
es el promedio de la semana en miles de millones; queda documentada pero no es la
predeterminada (A-S2-4).

Todo se normaliza a miles de millones de USD. **Las unidades no se asumen:** en
cada corrida el script lee los metadatos que publica FRED y los contrasta con su
configuración. Si no coinciden, se detiene (A-S2-9).

`RRPONTSYD` es diario y hay que llevarlo al miércoles: se toma el valor de ese
día y, si no hay, el último disponible anterior dentro de 7 días, dejando
constancia de qué día salió en la columna `rrp_fecha_origen` (A-S2-5).

---

## Cómo correr

Requiere Python 3.11 o superior y salida a `fred.stlouisfed.org`.

```bash
pip install -r requirements.txt
python -m senales.liquidez_neta
```

Un solo comando descarga, verifica unidades, alinea al miércoles, calcula,
valida, escribe las salidas y actualiza el changelog.

Es idempotente: correrlo dos veces el mismo día reutiliza la descarga ya
guardada, no agrega filas duplicadas y deja una sola entrada en el changelog.

Para rehacer una corrida anterior a partir de los archivos crudos ya guardados:

```bash
python -m senales.liquidez_neta --fecha-descarga 2026-09-16
```

Códigos de salida: `0` todo bien · `1` problema con la fuente (red, formato,
unidades) · `2` la validación no cerró.

### Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Los tests no tocan la red. Cubren unidades y su normalización, el acople entre
el identificador de cada serie y su unidad, la alineación al miércoles y el
arrastre del ON RRP, el cálculo de S2.2, el caso de validación del H.4.1, la
idempotencia de punta a punta y la detección de revisiones.

---

## Salidas

| Archivo | Qué contiene |
| --- | --- |
| `data/raw/<SERIE>_<fecha>.csv` | La descarga cruda, tal como la entregó FRED. Nunca se sobrescribe (A-S2-10). |
| `data/series/liquidez_neta.csv` | La serie publicada: `fecha, walcl, tga, rrp, rrp_fecha_origen, s2_1_liquidez_neta, s2_2_var_13s_pct`. |
| `data/series/CHANGELOG.md` | Una entrada por corrida: rango de datos, filas agregadas, revisiones históricas detectadas, huecos, verificación de unidades y resultado de la validación. Las secciones cuyo título no es una fecha, como el registro de cambios de supuestos, se escriben a mano y el script las conserva (A-S2-11). |
| `reportes/liquidez_neta.png` | Dos paneles: S2.1 en nivel arriba, S2.2 en barras alrededor de cero abajo. |

FRED revisa datos hacia atrás. Cada corrida compara lo que acaba de calcular
contra la serie de la corrida anterior y lista en el changelog toda diferencia
mayor a 500 mil USD, fecha por fecha y columna por columna (A-S2-6).

**Los huecos se reportan, no se rellenan.** Si falta el TGA de un miércoles, esa
fila queda con S2.1 vacío y el hueco aparece en el changelog.

---

## Cómo se valida

El H.4.1 de la semana terminada el **16 de septiembre de 2026**, publicado el 17
de septiembre, reporta en su columna de **nivel de miércoles** activos totales
6746548, TGA 991708 y ON RRP doméstico 5375, en millones de USD. En miles de
millones:

```
6746.548 − 991.708 − 5.375 = 5749.465
```

Las tres cifras salen de la **misma columna** del release, y eso no es un detalle
de redacción. El H.4.1 publica cada partida dos veces, como nivel del miércoles y
como promedio de la semana. El ancla original de esta serie las mezclaba, el gate
la rechazó en la primera corrida real y la corrección fue releer el release. Está
contado en **A-S2-13**.

Antes de escribir nada, el script calcula esa fila y exige dos cosas:

1. que el **total** no se desvíe más de **±5** del esperado;
2. que **cada componente** no se desvíe más de **±1** de su cifra del release
   (**A-S2-14**). Un total que cuadra porque dos componentes se compensan no
   reproduce el ancla, y ese es justamente el modo en que un ancla con columnas
   mezcladas podría pasar desapercibida.

Si cualquiera de las dos falla, se detiene: no escribe la serie, ni el gráfico,
ni el changelog. Reporta la diferencia total, el desvío de cada componente con su
propio OK o FALLA, y las semanas alrededor del ancla.

Ante una falla, **no se ajusta la fórmula para que cuadre**. Lo que se revisa, en
orden, es: que las tres cifras del ancla vengan de la misma columna del release
(A-S2-13), las unidades que declara FRED, la convención de la serie de TGA
(A-S2-4) y el perímetro del ON RRP (A-S2-1).

La unidad de cada serie está atada a su identificador: `WALCL` y `WDTGAL` llegan
en millones, `RRPONTSYD` en miles de millones. Hay tests que fallan si la
declaración de `WDTGAL` deja de decir `millones`, para que cambiar la serie sin
cambiar la unidad no llegue a publicarse (A-S2-4).

> **Estado actual de la validación: cerrada el 2026-10-03.** El gate cerró en
> dos corridas reales con el ancla corregida: la reproducción de la corrida del
> 2026-09-22 desde sus descargas crudas y una corrida nueva contra FRED en vivo.
> En las dos, el total y los tres componentes del 16 de septiembre de 2026
> coinciden con el H.4.1 con diferencia 0.000. Ver **A-S2-13**.
>
> Sigue abierto un punto: las unidades salen NO VERIFICADAS porque el endpoint de
> metadatos de FRED (`/data/<ID>.txt`) devuelve una página HTML. Las unidades
> quedan controladas por la banda de orden de magnitud y por el gate. Ver
> **A-S2-9**.

---

## Lo que esta serie no dice

**No es una predicción.** S2.1 describe una condición que ya ocurrió, con el
rezago de publicación del H.4.1. Que la liquidez neta suba no implica que algo
vaya a subir después. La relación entre liquidez y precios de activos es
inestable: funciona por tramos, desaparece por trimestres enteros y no tiene un
mecanismo de transmisión que se pueda escribir en una línea.

**No discrimina entre BTC y TQQQ.** Es una sola serie macro. No dice cuál de los
dos activos responde más, ni con qué rezago, ni si el signo es el mismo para los
dos. Cualquier regla que use S2.2 para elegir entre BTC y TQQQ está agregando
una hipótesis que esta serie no contiene.

**La fórmula es una convención entre varias.** Restar TGA y ON RRP a los activos
totales es la versión más difundida, no la correcta. Hay variantes razonables
que incluyen el repo pool extranjero (A-S2-1), que usan el TGA como promedio
semanal en vez de nivel de miércoles (A-S2-4), o que además restan el circulante
o las cuentas de capital. Dan series distintas. Ninguna es la liquidez neta:
cada una es *una* liquidez neta.

**No hay umbral.** El script no clasifica ninguna semana como expansión ni como
contracción, porque no hay un valor de corte que se sostenga todavía. Donde
debería ir ese número, la salida dice **NO MEDIDO** (A-S2-3).

**Un hueco es un hueco.** Cuando falta un dato, la fila queda vacía y se reporta.
Nada se interpola.

---

## Fase R · Precios mensuales y ratios

Cinco series —oro, plata, BTC, S&P 500 y Nasdaq Composite— llevadas a una sola
convención, y los cinco pares del sitio: Oro/Plata, BTC/Oro, Oro/S&P 500,
BTC/S&P 500 y Nasdaq/S&P 500.

De dónde sale cada serie, qué dice su licencia y qué se descartó está en
**[FUENTES.md](FUENTES.md)**. Las decisiones están en `SUPUESTOS.md`, de A-R0-1 a
A-R0-16.

### La convención

**Promedio mensual de cierres diarios, y solo de meses completos** (A-R0-1). Los
dos lados de un ratio describen el mismo mes. Un promedio dividido por un cierre
de fin de mes es el error de A-S2-13 con otro nombre.

| Serie | Fuente | Qué cierre diario | Quién promedia |
| --- | --- | --- | --- |
| Oro | Banco Mundial, Pink Sheet, dos ediciones empalmadas (A-R0-19) | Fixing de la tarde de Londres hasta 2025-05; "spot" desde 2025-06 (A-R0-7) | El Banco Mundial |
| Plata | Banco Mundial, Pink Sheet, dos ediciones empalmadas (A-R0-19) | No se pudo establecer: la serie es una **estimación** (A-R0-8) | El Banco Mundial |
| BTC | Coin Metrics community, `PriceUSD` | Fixing de las 00:00 UTC, todos los días calendario (A-R0-5) | Este script |
| S&P 500 | Shiller, `ie_data.xls` | Cierre de las 16:00 de Nueva York | Shiller |
| Nasdaq Composite | FRED `NASDAQCOM` | Cierre de las 16:00 de Nueva York | Este script |

Un mes entra cuando está completo. En una fuente diaria, cuando la serie ya tiene
una observación posterior a su último día. En una que ya viene mensual, cuando el
mes terminó antes de la fecha en que la fuente dice haberse actualizado; si no
declara esa fecha, la última fila se descarta.

### Qué se publica y qué no

Una serie se publica si pasa dos filtros (A-R0-14).

**La licencia tiene que permitir publicar sin interpretarla.** La pasan el oro y
la plata (CC BY 4.0) y BTC (CC BY-NC 4.0, mientras el sitio no tenga vínculo
comercial).

**Y su validación externa tiene que haber cerrado.** Ninguna serie se publica
sin un caso de validación contra una segunda fuente. Si el gate de un metal no
cierra, el metal y los pares que lo llevan se publican como **"NO MEDIDO: sin
validación externa"** y la corrida sigue.

El S&P 500 y el Nasdaq Composite **se calculan y no se publican**. Sus tres pares
aparecen en `pares.csv` con el estado **"NO MEDIDO: pendiente de permiso del
dueño del índice"**, hasta tener el permiso escrito de S&P Dow Jones Indices y de
Nasdaq (`FUENTES.md`, sección 10). El par existe y tiene historia; lo que falta
es el permiso, no el cálculo.

### Cómo correr

```bash
pip install -r requirements.txt
python -m senales.ratios
```

Requiere salida a `worldbank.org`, `shillerdata.com`, `fred.stlouisfed.org`,
`coinmetrics.io`, `nasdaq.com` y `bitstamp.net`. Es idempotente: la segunda
corrida del día reutiliza las descargas y deja las series idénticas byte a byte.

Códigos de salida, los mismos que S2: `0` todo bien · `1` problema con una
fuente · `2` un contraste, o el control del empalme, no cerró.

### Salidas

| Archivo | Qué contiene |
| --- | --- |
| `data/series/precios_mensuales.csv` | Oro, plata y BTC, por mes. El oro lleva su definición fila por fila (A-R0-7) y la plata, su estado de estimación (A-R0-8). Los dos metales llevan su error máximo por redondeo (A-R0-17), de qué edición del Pink Sheet sale cada mes (A-R0-19) y qué resultó su control contra el FMI: "dentro del umbral", "sin comparar" o "valor en disputa", con los dos valores (A-R0-20). |
| `data/series/ratios.csv` | Los pares que se publican, en formato largo: `mes, par, valor, error_redondeo_pct, valor_en_disputa, apto_metricas, estado`. |
| `data/series/pares.csv` | Los cinco pares, publicados o no: estado, primer y último mes, desde qué mes es apto para métricas y cuántos meses tiene en disputa. Acá es donde un par sin permiso dice NO MEDIDO. |
| `data/series/series.csv` | Las cinco series: fuente, licencia, **atribución**, estado y con qué se valida cada una. Sin valores. |
| `data/series/descargas_ratios.csv` | El manifiesto: de cada descarga, la URL, la fecha, los bytes y el SHA-256. |
| `data/raw/pink_sheet_<fecha>.xlsx`, `data/raw/coin_metrics_btc_<fecha>.json` | Los crudos cuya licencia permite redistribuirlos (CC BY y CC BY-NC). |
| `data/raw/pink_sheet_edicion_2025-01-03.xlsx` | La edición del Pink Sheet del 3 de enero de 2025, la última sin redondear. Una sola copia, con nombre fijo: no se vuelve a descargar (A-R0-19). |
| `data/raw/fmi_pcps_2026-10-04.xlsx` | La base mensual de precios de materias primas del FMI, contra la que se comparan el oro y la plata. Una sola copia, bajada a mano: el pipeline nunca la baja (A-R0-20). |
| `data/raw/ATRIBUCION.md` | Atribución y licencia de esos crudos. |
| `data/privado/` | **Fuera del repositorio.** Los crudos de Shiller y de FRED `NASDAQCOM`, y `ratios_internos.csv`, con todo lo que se calcula, se publique o no. |

**Un crudo viaja con el repositorio solo si su licencia permite redistribuirlo**
(A-R0-15). De los otros viaja el manifiesto y el código: quien baje el mismo
archivo puede comprobar el hash y rehacer la serie. Si el crudo que hay en disco
no coincide con el hash publicado, la corrida se detiene.

### Cómo se valida

Cada serie se contrasta contra una segunda fuente. BTC y los índices, mes a mes,
contra una fuente llevada a la misma convención: **cada mes tiene que cerrar**,
no el promedio de los meses. El oro y la plata, año a año: **cada año tiene que
cerrar**.

| Serie | Contra qué | Tolerancia |
| --- | --- | --- |
| S&P 500 | Promedio de los cierres diarios de FRED `SP500` | ±0.5 % |
| Nasdaq Composite | Promedio de los cierres de la API de nasdaq.com, últimos 10 años | ±0.1 % |
| BTC | Promedio de los cierres diarios de Bitstamp, desde 2013-01 | ±2 % |
| Oro | Promedio de los doce meses contra el precio anual del USGS, 2021 a 2024 | ±0.5 % |
| Plata | Promedio de los doce meses contra el precio anual del USGS, 2021 a 2024 | ±1 % |

Las fuentes de contraste mensual tienen licencia cerrada: **se leen, se comparan
y no se guardan**. De cada contraste queda en el changelog la cantidad de meses,
la diferencia mediana y, del mes que más se aparta, la fecha y la diferencia.
**Del S&P 500 y del Nasdaq no queda ningún nivel del índice** (A-R0-12).

Si el contraste de BTC o de un índice no cierra, la corrida se detiene y no
escribe ninguna serie. **No se ajusta la tolerancia para que cuadre.** Se revisa,
en este orden: la fuente, la convención y el mes.

**El gate de oro y plata** (A-R0-16) es anual porque no hay una segunda fuente
mensual abierta. El USGS publica, en sus *Mineral Commodity Summaries*, el
precio promedio de cada año; es de dominio público y sale de otra cotización,
la de Engelhard, no del fixing de Londres. Las ocho cifras, 2021 a 2024, están
transcritas a mano en `configuracion.py` con su cita, como el ancla del H.4.1.
Las tolerancias se fijaron antes de calcular el gate y su justificación está en
A-R0-16. Cerró el 2026-10-04: cuatro años de cuatro en los dos metales, con una
diferencia máxima de 0.120 % en el oro y de 0.601 % en la plata.

**El empalme del oro y la plata** (A-R0-19). Las dos series salen de dos
ediciones del Pink Sheet: la del 3 de enero de 2025, sin redondear, hasta
2024-12, y la vigente, redondeada, desde 2025-01. En cada corrida, redondear la
primera tiene que reproducir la segunda en todos los meses que comparten. Los
que quedan exactamente a medio paso de redondeo se aceptan y se listan en el
changelog. Si un mes no coincide, el Banco Mundial revisó un dato viejo: la
corrida se detiene y no escribe ninguna serie. La edición de 2025 está
versionada en `data/raw/` y se identifica por su SHA-256; el pipeline no depende
de que su URL siga respondiendo.

**El control mensual contra el FMI** (A-R0-20). En cada corrida, el oro y la
plata se comparan mes a mes con las series del FMI, sobre todos los meses que
tienen en común: hoy 560, de 1980-01 a 2026-08. El mes que se aparta más que la
tolerancia del gate (0.5 % el oro, 1 % la plata) queda como **valor en
disputa**: se publica sin cambios, con los dos números a la vista, y no entra a
ninguna métrica. **Este control no detiene la corrida** ni decide cuál fuente
tiene razón. Hoy marca diez meses del oro y diez de la plata; todos van
listados en el changelog. Los términos del FMI prohíben la descarga masiva
automatizada, así que su archivo no se baja: viaja con el repositorio, y si
falta, la corrida se detiene.

Hay dos controles más sobre los metales. Los promedios del segundo trimestre de
2026 tienen que caer entre el mínimo y el máximo que LBMA publicó para ese
trimestre. Y la corrida se detiene si el Banco Mundial cambia la descripción
del oro o de la plata: ya cambió una vez, en junio de 2025.

### Lo que estas series no dicen

**Un ratio de precio no es un ratio de retorno.** Los índices no incluyen
dividendos (A-R0-13).

**El oro no es una sola serie.** Cambia de definición en junio de 2025, y que los
dos tramos sean comparables es un supuesto (A-R0-7).

**No todos los meses publicados sirven para una métrica.** Cada valor del oro y
de la plata tiene un error máximo por el redondeo con que la fuente lo publica,
y el de cada ratio va fila por fila. Un percentil o una tendencia solo pueden
usar los meses marcados como aptos, que son los del tramo final sin
interrupción con error de hasta 0.5 %, menos los que tienen un valor en disputa:
**Oro/Plata desde 1968-04** (682 de 801 meses) y **BTC/Oro desde 2013-01** (161
de 165). Lo que corta en 1968 son dos meses, febrero y marzo, que la fuente
publica al dólar, con 1.4 % de error. El corte coincide con el fin del London
Gold Pool, en marzo de 1968: hasta entonces los bancos centrales sostenían el
oro de Londres cerca de 35 USD. Los meses anteriores se publican con su error a
la vista y no son evidencia de nada (A-R0-17).

**Veinte meses tienen un valor en disputa.** Son los meses en que el Pink Sheet
y el FMI no coinciden. Se publican con el valor del Pink Sheet, sin corregir.
En dos, marzo y noviembre de 1985, una tercera fuente le da la razón al FMI; en
los demás no se sabe cuál tiene razón. Y el control no llega a toda la historia:
antes de 1980 y después de agosto de 2026 los meses dicen "sin comparar"
(A-R0-20).

**El oro y la plata tienen dos tramos de precisión.** Hasta 2024-12 vienen sin
redondear; desde 2025-01, el oro al dólar y la plata a un decimal. El tramo
viejo sale de una edición congelada, que no recibe las revisiones que el Banco
Mundial haga después (A-R0-9, A-R0-19).

**El gate de oro y plata valida cuatro años, no toda la historia.** Dice que
entre 2021 y 2024 el nivel anual del Pink Sheet es el de una cotización
independiente. No dice nada de 1960, ni de los meses posteriores al quiebre del
oro de junio de 2025 (A-R0-16).

**El S&P 500 llega tarde.** Shiller no publica un calendario; hoy va un mes por
detrás de las otras series, y sus pares llegan hasta donde llegue él (A-R0-11).

**Las licencias de tres fuentes son condicionales.** Valen mientras el sitio no
tenga vínculo comercial (A-R0-2, A-R0-3, A-R0-4).

---

## Estructura

```
senales/
├── senales/
│   ├── configuracion.py    Todo lo que decide un número publicado
│   ├── fuentes_fred.py     Descarga, cache y verificación de unidades
│   ├── nucleo.py           Utilidades compartidas entre señales
│   ├── bitacora.py         Changelog y detección de revisiones
│   ├── grafico.py          El PNG de dos paneles
│   ├── liquidez_neta.py    S2.x — punto de entrada
│   ├── fuentes_precios.py  Fase R — descarga, manifiesto y lectura de cada fuente
│   └── ratios.py           Fase R — punto de entrada
├── tests/
├── data/raw/               Descargas crudas que se pueden redistribuir, versionadas por fecha
├── data/series/            Series publicadas, manifiesto de descargas y changelog
├── data/privado/           Crudos no abiertos y series que no se publican (ignorado por git)
└── reportes/               Gráficos
```

### Agregar una serie nueva

Las capas siguientes del marco (**S3.x**, flujos a ETFs; **S4.x**, decaimiento de
TQQQ) van como módulos hermanos de `liquidez_neta.py`, no dentro de él:

1. Declarar las fuentes, unidades, parámetros y caso de validación en
   `configuracion.py`.
2. Escribir `senales/<nombre>.py` con su propio `main()`, usando
   `nucleo.escribir_csv_determinista` y `bitacora.actualizar_changelog` para que
   el formato de salida y la idempotencia sean los mismos en todo el marco.
3. Escribir en `data/series/<nombre>.csv`.
4. Numerar los supuestos nuevos en `SUPUESTOS.md` con su prefijo (`A-S3-1`, ...).
5. Ninguna serie se publica sin un caso de validación contra una fuente externa.

---

## Supuestos

Treinta y cuatro decisiones sostienen estos números —catorce de S2 y veinte de
la fase R— y ninguna es obvia. Están todas en **[SUPUESTOS.md](SUPUESTOS.md)**, numeradas
y con estado (dato / estimación / supuesto / no medido).

Las tres de S2 que más cambian el resultado:

- **A-S2-1** — solo se resta el ON RRP doméstico; el repo pool extranjero queda fuera.
- **A-S2-4** — el TGA se toma como nivel de miércoles (`WDTGAL`), la misma convención que `WALCL` y que el H.4.1.
- **A-S2-3** — no hay umbral de expansión ni de contracción: **NO MEDIDO**.

Y dos que conviene leer antes de confiar en un número publicado:

- **A-S2-13** — el ancla del H.4.1 estuvo mal transcrita; la reverificación con el ancla corregida cerró el 2026-10-03.
- **A-S2-9** — las unidades no se pueden verificar contra los metadatos de FRED; la causa está identificada y la solución, pendiente.
- **A-S2-14** — el gate verifica cada componente contra el release, no solo el total.

Y de la fase R, las que conviene leer antes que las demás:

- **A-R0-14** — solo se publica lo que la licencia permite y una segunda fuente valida; los pares con índices quedan como NO MEDIDO.
- **A-R0-1** — toda serie es un promedio mensual de cierres diarios, y solo de meses completos.
- **A-R0-16** — el gate de oro y plata es anual, contra el USGS, y valida 2021 a 2024.
- **A-R0-17** — las métricas sobre un ratio solo usan los meses con error de redondeo de hasta 0.5 %.
- **A-R0-19** — el oro y la plata se empalman: edición sin redondear del Pink Sheet hasta 2024-12, edición vigente después.
- **A-R0-20** — el oro y la plata se comparan cada mes con el FMI; el mes que pasa del umbral se publica como valor en disputa y queda fuera de las métricas.
