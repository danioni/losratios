# Supuestos

Cada decisión que afecta un número publicado está acá, numerada y con estado.
Los estados son cuatro:

| Estado | Qué significa |
| --- | --- |
| **dato** | Medido y verificable contra una fuente externa. |
| **estimación** | Derivado de datos por un procedimiento explícito. |
| **supuesto** | Elegido por convención. Podría ser otro sin que nada quede mal. |
| **no medido** | Sin valor. No se inventa uno. |

Cambiar cualquiera de estos supuestos obliga a actualizar este archivo **y**
`data/series/CHANGELOG.md` en la misma corrida. Un supuesto que vive solo en el
código es un supuesto perdido.

---

## A-S2-1 · La liquidez neta usa solo el ON RRP doméstico

**Estado: supuesto.**

S2.1 resta únicamente `RRPONTSYD`, el reverse repo overnight con contrapartes
domésticas (fondos de money market, bancos, GSE). El repo pool de cuentas
oficiales extranjeras queda fuera.

Esto es una convención, no un hecho. El H.4.1 reporta las dos cosas como
pasivos de la Fed, y las dos drenan reservas del sistema. Quien incluya el pool
extranjero obtiene una serie distinta, y tan defendible como esta.

**Alternativa.** La línea del H.4.1 es *Reverse repurchase agreements — Foreign
official and international accounts*. El candidato en FRED es `WLRRAFOIAL`
(nivel de miércoles, millones de USD). **No se pudo verificar ese identificador
desde el entorno donde se escribió este repo** (ver A-S2-13): antes de usarlo,
confirmar el ID, la unidad y la frecuencia en la página de FRED.

Razón de la elección: el pool extranjero se mueve por decisiones de bancos
centrales ajenas al ciclo de política monetaria doméstico, y mete ruido en una
serie que se quiere leer como contexto de liquidez para activos en USD. Es un
argumento, no una prueba.

---

## A-S2-2 · La ventana de S2.2 es de 13 semanas

**Estado: supuesto.** Parametrizable en `VENTANA_VARIACION_SEMANAS`.

Trece semanas es un trimestre. No hay nada en los datos que señale 13 en vez de
8, 12 o 26. Cambiar la ventana cambia la amplitud de S2.2 y, con ella, cualquier
umbral que se defina más adelante. Si se cambia, el nombre de la columna
`s2_2_var_13s_pct` deja de decir la verdad y hay que cambiarlo también.

---

## A-S2-3 · El umbral de expansión / contracción NO ESTÁ DEFINIDO

**Estado: no medido.**

`UMBRAL_EXPANSION_CONTRACCION = None`. Mientras siga en `None`, el script
reporta **NO MEDIDO (A-S2-3)** en la consola, en el changelog y al pie del
gráfico, y no clasifica ninguna semana como expansión ni como contracción.

No se puso un valor porque no hay ninguno que se sostenga todavía. Definir el
umbral exige decidir antes: contra qué se mide el acierto, en qué horizonte, y
con qué costo de falso positivo. Nada de eso está resuelto. Un número puesto
para llenar el campo se volvería, en dos semanas, un número que nadie recuerda
haber inventado.

---

## A-S2-4 · El TGA se toma como nivel de miércoles (`WDTGAL`)

**Estado: supuesto.** Cambiado el 2026-09-22; antes era `WTREGEN`.

La serie de TGA en uso es **`WDTGAL`**, cuyo título completo en FRED es
*Liabilities and Capital: Deposits with F.R. Banks, Other Than Reserve Balances:
U.S. Treasury, General Account: **Wednesday Level***. Es semanal, referida al
miércoles, y se publica en **millones de USD**.

**Motivo del cambio.** `WALCL` es *Wednesday Level*, y el ancla del H.4.1 contra
la que se valida S2.1 también reporta niveles de miércoles. La serie anterior,
`WTREGEN`, es el promedio de la semana. Restar un promedio semanal a un nivel
puntual mezclaba dos convenciones dentro de una misma resta, y esa mezcla podía
valer decenas de miles de millones en semanas de vencimientos impositivos o de
subastas grandes — bastante más que la tolerancia de ±5 con la que se valida
S2.1. Con `WDTGAL`, los tres términos de la fórmula describen el mismo instante.

**La unidad va atada al identificador.** `WDTGAL` llega en millones y `WTREGEN`
en miles de millones. Cambiar uno sin cambiar la otra desplaza S2.1 por un factor
de 1000. Para que ese olvido no llegue a publicarse hay tests que fallan si la
declaración de `WDTGAL` en `configuracion.py` deja de decir `millones`
(`tests/test_unidades.py`).

**Alternativa.** `WTREGEN`, el TGA como promedio semanal en miles de millones de
USD. Sigue declarada en `configuracion.py` como `SERIE_TGA_PROMEDIO_SEMANAL`;
para volver a ella, apuntar `SERIE_TGA` ahí y registrar el cambio acá y en
`data/series/CHANGELOG.md`.

**Lo que este cambio no toca.** La fórmula de S2.1 sigue igual, y la tolerancia
del total sigue en ±5. Lo que sí se agregó después, a raíz de A-S2-13, es una
tolerancia por componente (A-S2-14).

**Lo que la corrida del 2026-09-22 confirmó.** El identificador `WDTGAL`, su
título y su unidad venían de la instrucción que fijó este supuesto, no de una
lectura propia: el entorno donde se escribió este repositorio no llega a
`fred.stlouisfed.org` (A-S2-13). La primera corrida con acceso los confirmó. La
serie existe, es semanal referida al miércoles, y su unidad es millones de USD:
para el 16 de septiembre de 2026 entrega 991708, que es exactamente el nivel de
miércoles del TGA que publica el H.4.1 en millones.

Ese mismo cruce mostró que el cambio de `WTREGEN` a `WDTGAL` era necesario y que
estaba incompleto. Necesario, porque la diferencia entre el promedio semanal
(877.028) y el nivel del miércoles (991.708) fue de 114.68 miles de millones esa
semana, veintitrés veces la tolerancia del gate. Incompleto, porque el ancla del
H.4.1 no se actualizó junto con la serie y quedó mezclando columnas: eso es lo
que el gate atrapó, y está documentado en A-S2-13.

---

## A-S2-5 · El ON RRP se arrastra como máximo 7 días

**Estado: supuesto.**

`RRPONTSYD` es diario. Si el miércoles no tiene dato (feriado, o la fuente no lo
publicó), se toma el último valor disponible anterior y la columna
`rrp_fecha_origen` deja constancia de qué día salió.

El arrastre tiene tope: `MAX_DIAS_ARRASTRE_RRP = 7`. Más allá de una semana, el
valor deja de describir ese miércoles y pasa a ser una invención con fecha
vieja. Ahí el dato queda vacío y se reporta como hueco.

---

## A-S2-6 · Una diferencia de 500 mil USD cuenta como revisión

**Estado: supuesto.**

`EPSILON_REVISION = 0.0005` (miles de millones). Por debajo de eso, una
diferencia entre dos corridas se trata como ruido de redondeo y no se anota en
el changelog. Por encima, se anota como revisión histórica de la fuente.

El umbral es arbitrario. Está puesto bajo a propósito: un falso positivo en el
changelog cuesta una línea de ruido; un falso negativo esconde que FRED cambió
un número publicado.

---

## A-S2-7 · S2.2 compara por fecha, no por posición

**Estado: supuesto.**

La variación a 13 semanas busca el miércoles exactamente 91 días anterior. Si esa
semana no existe en la serie, el resultado queda vacío.

La alternativa — correr 13 filas hacia atrás — daría siempre un número, incluso
saltando por encima de semanas faltantes, y ese número diría ser una variación
trimestral sin serlo. Se prefiere el vacío.

---

## A-S2-8 · La grilla semanal la define WALCL

**Estado: supuesto.**

Las fechas de la serie publicada son las de `WALCL`, porque son las fechas de
balance del H.4.1. El TGA se engancha por fecha exacta; si falta para un
miércoles, la fila queda con S2.1 vacío y el hueco se reporta. No se desplaza
ninguna serie para que coincida.

Si una observación de `WALCL` no cae en miércoles, el script se detiene en vez
de decidir por su cuenta qué hacer con ella.

---

## A-S2-9 · Las unidades se verifican en cada corrida, no se asumen

**Estado: dato cuando FRED responde; supuesto cuando no.**

Las unidades configuradas son:

| Serie | Unidad declarada en la configuración | Factor a miles de millones |
| --- | --- | --- |
| `WALCL` | Millions of U.S. Dollars | ÷ 1000 |
| `WDTGAL` | Millions of U.S. Dollars | ÷ 1000 |
| `RRPONTSYD` | Billions of US Dollars | × 1 |
| `WTREGEN` *(alternativa, A-S2-4)* | Billions of U.S. Dollars | × 1 |

En cada corrida el script lee los metadatos publicados por FRED y los contrasta
con esta tabla:

- Si coinciden, la unidad queda **VERIFICADA** y así se anota en el changelog.
- Si difieren, la corrida **se detiene**. No se aplica un factor de corrección
  silencioso: hay que arreglar la configuración y anotarlo acá.
- Si no se pueden leer los metadatos (FRED caído, formato cambiado, red
  bloqueada), la unidad queda **NO VERIFICADA**, la corrida sigue y quedan como
  red dos controles: la banda de orden de magnitud de cada serie y el caso de
  validación del H.4.1.

La banda de orden de magnitud existe para atrapar un error de 1000× aunque no
haya red: si `WALCL` normalizado se sale de [500, 20000] miles de millones, algo
cambió en la fuente y la corrida se detiene.

### Limitación observada: los metadatos no llegaron

**Estado de este punto: no medido.**

En la corrida del 2026-09-22, la primera con salida real a FRED, los CSV de las
tres series bajaron bien y las tres unidades salieron **NO VERIFICADAS**. La red
no era el problema. El script pide los metadatos a
`https://fred.stlouisfed.org/data/<ID>.txt` y busca una línea que empiece con
`Units:`; algo de esa cadena no funcionó, y la versión de entonces devolvía el
mismo `None` para cualquier causa, así que la salida no permitía saber cuál.

Eso último ya está arreglado. `unidad_declarada` devuelve ahora `(unidad,
motivo)`, el motivo distingue los casos —la red no respondió, el endpoint
devolvió otro código, la respuesta llegó con HTTP 200 pero sin línea `Units:`— y
se arrastra hasta el detalle de la verificación y de ahí al changelog. Hay tests
que cubren esos casos sin tocar la red, incluido el parseo del encabezado con el
formato que publica FRED.

**Causa identificada el 2026-10-03 (dato).** Las dos corridas de reverificación
(A-S2-13) dieron el mismo motivo para las tres series:
`https://fred.stlouisfed.org/data/<ID>.txt` responde HTTP 200 con
`text/html; charset=UTF-8`, la primera línea es `<!DOCTYPE html>` y no hay línea
`Units:` en las primeras 40. Es el tercer caso de los que distingue
`unidad_declarada`: el endpoint responde, pero ya no entrega el archivo de texto
con metadatos. Que FRED haya retirado ese formato es una lectura de esa
respuesta, no algo confirmado con FRED (**supuesto**).

Lo que **no** está resuelto es si existe una fuente de la unidad que funcione
sin clave de API. Alternativas a evaluar si `/data/<ID>.txt` no sirve: la
página de la serie, o la API de FRED (`api.stlouisfed.org/fred/series`), que
exige clave y por lo tanto le agregaría una credencial a un pipeline que hoy no
necesita ninguna. Mientras no haya evidencia de cuál funciona, esto queda como
limitación abierta y no como resuelto.

Con la unidad NO VERIFICADA los controles que quedan son los dos de siempre —la
banda de orden de magnitud y el gate del H.4.1— más la verificación por
componente de A-S2-14. Para el ancla del 16 de septiembre de 2026 la unidad de
las tres series quedó confirmada igual, por otra vía: los tres niveles de
miércoles del release, expresados en millones, coinciden con lo que las series de
FRED entregan una vez normalizadas. Es una confirmación puntual de esa semana, no
un reemplazo del cruce automático en cada corrida.

---

## A-S2-10 · Las descargas crudas se conservan, no se ignoran

**Estado: supuesto.**

Cada descarga se guarda como `data/raw/<SERIE>_<fecha>.csv` y nunca se
sobrescribe. Los archivos no están en `.gitignore`: la idea es poder
reconstruir cualquier corrida pasada con exactitud, incluso después de que FRED
revise los datos.

El costo es que el repositorio crece unos cientos de KB por corrida. Si eso
molesta, la decisión a tomar es cuántas descargas conservar, y va acá antes de
tocar el `.gitignore`.

---

## A-S2-11 · El changelog guarda una entrada por día de corrida

**Estado: supuesto.**

Si se corre dos veces el mismo día, la segunda corrida **reemplaza** la entrada
de ese día en vez de agregar una nueva. El changelog refleja siempre la última
corrida de cada fecha.

La alternativa — una entrada por ejecución — sería más fiel a lo que pasó, pero
llena el archivo de entradas idénticas cada vez que alguien reintenta una
descarga fallida.

---

## A-S2-12 · La historia publicada empieza el 1 de enero de 2020

**Estado: supuesto.**

`FECHA_INICIO = date(2020, 1, 1)`. Las tres series existen desde antes, y el
script puede traer más historia cambiando ese parámetro. Se corta en 2020 porque
es donde empieza el régimen de balance que la señal describe; una serie que
arranque en 2015 mezcla dos mundos distintos en un mismo gráfico.

---

## A-S2-13 · La validación contra FRED en vivo: cerrada el 2026-10-03

**Estado: dato.** El gate cerró en dos corridas reales con el ancla corregida.
Antes de esa fecha el estado era **no medido**; la historia completa sigue abajo.

### La reverificación (2026-10-03)

Dos corridas, en este orden, desde la máquina que tiene salida a
`fred.stlouisfed.org`, con el código en `fcbebe9`:

1. `python -m senales.liquidez_neta --fecha-descarga 2026-09-22`: reproduce la
   corrida del 2026-09-22 desde sus tres descargas crudas, las mismas que
   motivaron la corrección. Código de salida 0. Serie de 2020-01-01 a
   2026-09-16, 351 filas.
2. `python -m senales.liquidez_neta`: descarga nueva del 2026-10-03. Código de
   salida 0. Serie de 2020-01-01 a 2026-09-30, 353 filas; 2 filas agregadas y 0
   revisiones históricas respecto de la corrida anterior.

En las dos, el gate del 16 de septiembre de 2026 dio:

| | Calculado | Release | Diferencia | Tolerancia | Resultado |
| --- | --- | --- | --- | --- | --- |
| Total S2.1 | 5749.465 | 5749.465 | 0.000 | ±5 | OK |
| WALCL | 6746.548 | 6746.548 | 0.000 | ±1 | OK |
| TGA (`WDTGAL`) | 991.708 | 991.708 | 0.000 | ±1 | OK |
| ON RRP | 5.375 | 5.375 | 0.000 | ±1 | OK |

Que la primera corrida cierre importa por sí sola: son los mismos datos que el
gate rechazó el 2026-09-22, y ahora cierran sin haber tocado la fórmula. Lo
único que cambió fue el ancla, leída del release. Las descargas crudas de las
dos fechas quedan versionadas en `data/raw/`, así que ambas corridas se pueden
reconstruir (A-S2-10).

Lo que este cierre **no** dice: que la serie anticipe algo (ver "Lo que esta
serie no dice" en el README) ni que las unidades estén verificadas contra los
metadatos de FRED (A-S2-9).

### Lo que la primera corrida real estableció

El 2026-09-22 el pipeline se corrió por primera vez desde una máquina con salida
a `fred.stlouisfed.org`. Las tres series bajaron, la aritmética corrió sobre
datos reales y **el gate rechazó el ancla**: calculado 5749.465 contra un
esperado de 5866.000, una diferencia de −116.535 sobre una tolerancia de ±5.

El problema era el ancla, no el cálculo. Sus tres cifras mezclaban dos columnas
distintas del H.4.1:

| Componente | Ancla original | De qué columna salía | Nivel de miércoles real |
| --- | --- | --- | --- |
| Activos totales | 6747.0 | nivel de miércoles | 6746.548 |
| TGA | 877.0 | **promedio semanal** (877.028) | 991.708 |
| ON RRP | 4.0 | **promedio semanal** (3.999) | 5.375 |

La brecha del TGA es la grande porque el 15 de septiembre es fecha de pago de
impuestos corporativos estimados: el TGA subió de 843.705 el 9 de septiembre a
991.708 el 16, y el promedio de esa semana quedó muy por debajo del cierre del
miércoles. Un ancla que mezcla columnas no describe ningún instante, y la resta
que sale de ahí no cuadra con nada.

### La corrección

El ancla nuevo son los tres niveles de miércoles del release, leídos de
<https://www.federalreserve.gov/releases/h41/current/>, publicado el 17 de
septiembre de 2026: activos totales 6746548, TGA 991708 y ON RRP —línea
`Others` de *reverse repurchase agreements*, el perímetro doméstico de A-S2-1—
5375, los tres en millones de USD. En miles de millones:

```
6746.548 − 991.708 − 5.375 = 5749.465
```

La corrección viene de leer el release, no de ajustar el cálculo para que cuadre.
Importa el orden en que pasaron las cosas: el cálculo ya daba 5749.465 con datos
reales **antes** de que nadie tocara el ancla. Se movió el ancla hasta la fuente,
no el número hasta el ancla.

### Lo que falta

1. ~~**La corrida de reverificación.**~~ Hecha el 2026-10-03; ver arriba.
2. **La unidad que declara FRED.** Causa identificada el 2026-10-03; la solución
   sigue abierta. Ver A-S2-9.
3. **Un enlace estable al release.** `fuente_url` apunta a `/current/`, que deja
   de mostrar esta semana en cuanto se publica la siguiente. El equivalente
   archivado y fechado sería mejor ancla documental, pero no se verificó desde
   este repositorio y no se pone una URL que nadie leyó.

### Lo que sí está probado sin red

Contra datos de prueba deterministas: que la aritmética reproduce el ancla
corregido, que el gate corta cuando el total se desvía más de ±5, que corta
cuando un componente se desvía más de ±1 aunque el total cierre (A-S2-14), que
un total que cuadra por compensación entre dos componentes no pasa, que
`WTREGEN` no reproduce un ancla de niveles de miércoles, que un error de unidad
en el TGA no pasa desapercibido, y que la unidad declarada para `WDTGAL` no se
puede cambiar sin que falle un test (A-S2-4).

---

## A-S2-14 · El gate verifica cada componente, no solo el total

**Estado: supuesto.** Tolerancia por componente: ±1 mil millones de USD, en
`tolerancia_componente` dentro de `CasoValidacion`.

Antes el gate comparaba solo el total de S2.1 contra el esperado. Eso deja pasar
un ancla reproducida por casualidad: si dos componentes se desvían lo mismo en la
misma dirección —porque los dos salieron de la columna equivocada del release,
por ejemplo— la resta da el número correcto y el gate publica una serie que no
reproduce nada. Es el error de A-S2-13 visto desde el lado del control que
faltaba.

Ahora el gate exige las dos cosas: el total dentro de ±5 y **cada componente**
dentro de ±1 contra su cifra del release. Un componente sin dato cuenta como
fuera: no se da por buena una resta a la que le falta un término.

El ±1 es una convención, no una medición. Sale de que las cifras del H.4.1 se
leen en millones y se comparan en miles de millones, así que el redondeo de la
transcripción vive en el tercer decimal, muy por debajo de 1. Un desvío de más de
mil millones en un componente no es redondeo: es otra serie, otra columna u otra
unidad.

Las dos condiciones no son independientes, y conviene tenerlo escrito. Como S2.1
es exactamente `walcl − tga − rrp` y el esperado sale de esa misma resta sobre
las cifras del release, el desvío del total es la suma de los desvíos de los
componentes. Si los tres entran en ±1, el total no puede desviarse más de 3, que
cabe en ±5: hoy la verificación por componente **domina** a la del total. La del
total queda como respaldo de dos cosas que sí pueden cambiar: que falte la fecha
ancla, y que alguien afloje la tolerancia por componente o toque la fórmula de
S2.1 sin notar que el total dejó de estar acotado.

---

## Fase R · Ratios: los supuestos A-R0-\*

Se fijaron el 2026-10-04, al cerrar el paso 0 de la fase R y **antes de
escribir código**. La evidencia de cada cifra —qué se leyó, de dónde y cuándo—
está en `FUENTES.md`; acá va la decisión y lo que la haría cambiar.

Tres de estos supuestos son **condicionales**: A-R0-2, A-R0-3 y A-R0-4 valen
**mientras el sitio no tenga vínculo comercial**. El día que lo tenga, dejan de
valer los tres a la vez y hay que volver a `FUENTES.md` antes de publicar nada.

---

## A-R0-1 · Las cinco series son promedios mensuales de cierres diarios, y solo de meses completos

**Estado: supuesto.** Fijado por instrucción del 2026-10-04.

S&P 500, Nasdaq Composite, oro, plata y BTC se llevan a una sola convención: el
promedio de los cierres diarios de cada mes calendario. Así los dos lados de un
ratio describen el mismo mes. Mezclar un promedio con un cierre de fin de mes es
el error de A-S2-13 con otro nombre.

No era la única convención posible. El sitio usa hoy el cierre de fin de mes
para índices y metales, y el borrador de `FUENTES.md` proponía el cierre semanal
del viernes. Decidió la licencia: las únicas fuentes abiertas de oro y plata son
promedios mensuales.

**Solo entran meses completos.** La regla depende de cómo viene la fuente:

- En una fuente diaria, un mes está completo cuando la serie ya tiene una
  observación posterior a su último día. Si la serie arranca con el mes
  empezado, ese primer mes tampoco entra.
- En BTC, que opera todos los días, el mes además tiene que traer todos sus
  días. Si falta uno, el mes no se publica y se reporta.
- En una fuente que ya viene mensual, un mes está completo cuando terminó antes
  de la fecha en que la fuente dice haberse actualizado. Si no declara esa
  fecha, la última fila se descarta.

El mes en curso no se publica, y el último mes de un par es el último mes
completo en sus dos fuentes.

---

## A-R0-2 · El S&P 500 sale de Shiller, que no declara licencia

**Estado: supuesto, condicional.** Válido mientras el sitio no tenga vínculo
comercial.

La serie es la columna `P` de `ie_data.xls`, de Robert Shiller. Ya viene como
promedio mensual de cierres diarios, y eso está verificado: en 620 meses
comunes, el promedio de los cierres diarios del índice la reproduce con una
diferencia mediana de 0.0003 % y máxima de 0.30 %.

Ni la página ni el archivo tienen términos de uso: solo un descargo de
responsabilidad. No hay cláusula que permita republicar ni que lo prohíba. El
índice subyacente es de S&P Dow Jones Indices, que sí exige permiso escrito para
reproducirlo. Por eso esta serie **se calcula y no se publica** (A-R0-14) hasta
tener ese permiso.

**Alternativa.** FRED `SP500`: cierres diarios, pero solo 10 años de historia y
con la cláusula de S&P a la vista. Queda como fuente de contraste (A-R0-12).

---

## A-R0-3 · El Nasdaq Composite sale de FRED, bajo la lectura de uso educativo no comercial

**Estado: supuesto, condicional.** Válido mientras el sitio no tenga vínculo
comercial.

La serie es `NASDAQCOM`: cierres diarios desde el 5 de febrero de 1971, que el
pipeline promedia por mes. El primer mes completo es marzo de 1971.

FRED la etiqueta "Copyrighted: Pre-Approval Required", y sus términos dicen dos
cosas. La sección III dice que, sin permiso escrito del dueño, estas series solo
se pueden usar para uso educativo no comercial o personal. El FAQ y los términos
de la API dicen que para todo uso que no sea el personal hay que contactar al
dueño. Este supuesto se apoya en la primera frase. La segunda es la razón por la
que la serie **se calcula y no se publica** (A-R0-14) hasta tener el permiso de
Nasdaq.

---

## A-R0-4 · BTC sale de Coin Metrics community, bajo CC BY-NC 4.0

**Estado: supuesto, condicional.** Válido mientras el sitio no tenga vínculo
comercial.

La serie es la métrica `PriceUSD` de la API community: un fixing diario a las
00:00 UTC, desde el 18 de julio de 2010, sin días faltantes. La documentación
pone los datos community bajo Creative Commons y enlaza a la licencia
BY-NC 4.0: se puede publicar con atribución mientras el uso sea no comercial.

Es la única de las tres condicionales que **se publica** (A-R0-14), porque su
licencia permite publicar sin interpretarla. La condición no es una formalidad:
un enlace a un servicio de asesoría convierte el uso en comercial y deja a los
pares con BTC sin fuente.

---

## A-R0-5 · El mes de BTC promedia todos los días calendario

**Estado: supuesto.**

BTC opera todos los días; los índices, solo los hábiles de Nueva York. El mes de
BTC promedia sus 28 a 31 fixings, en UTC. El mes del S&P 500 promedia 19 a 23
cierres. No es exactamente el mismo conjunto de días a los dos lados del ratio.

Se midió cuánto pesa. Sobre `PriceUSD`, de 2011-01 a 2026-09, el promedio de
todos los días y el de lunes a viernes difieren en una mediana de 0.30 %, con
percentil 95 de 1.43 % y máximo de 3.30 % (abril de 2011).

**Alternativa.** Promediar solo de lunes a viernes. Se parece más al calendario
de los índices, pero tira a la basura dos de cada siete observaciones de un
mercado que sí operó, y sigue sin coincidir con los feriados de Nueva York ni
con los de Londres.

---

## A-R0-6 · Los cierres diarios no son simultáneos

**Estado: supuesto.**

Dentro de un mismo día, cada serie cierra a otra hora: los índices a las 16:00
de Nueva York; el oro a las 15:00 de Londres hasta mayo de 2025 y sin hora
declarada después (A-R0-7); la plata en un fixing de Londres cuya hora no se
pudo establecer (A-R0-8); BTC a las 00:00 UTC. Entre el primero y el último hay
varias horas.

Con promedios mensuales ese desfase pesa mucho menos que con cierres, porque el
ruido de unas horas se promedia entre veinte o treinta días. No desaparece, y no
se midió.

---

## A-R0-7 · El oro del Pink Sheet cambia de definición en junio de 2025

**Estado: dato el cambio; supuesto la continuidad.**

La descripción que publica el Banco Mundial dice que el oro es un promedio de
precios diarios en los dos tramos, pero que el precio diario cambia: hasta mayo
de 2025 es el fixing de la tarde de Londres, y desde junio de 2025 es "spot",
sin hora declarada.

La serie se publica como una sola, **con el quiebre declarado junto a ella**. Que
los dos tramos sean comparables es un supuesto: no se pudo medir el salto, porque
los precios diarios de la subasta de Londres son de IBA y exigen licencia.

---

## A-R0-8 · La plata del Pink Sheet es un promedio mensual por inferencia

**Estado: estimación.** El sitio lo muestra junto a la serie.

La descripción de la plata no dice que sea un promedio de precios diarios, como
sí lo dice la del oro. Y habla de un fixing de la tarde de Londres, cuando la
subasta de plata de LBMA es a las 12:00.

Que la serie es un promedio mensual se infiere de un contraste: en 23 meses
(2024-11 a 2026-09) queda a una mediana de 0.18 % del promedio mensual de los
cierres del futuro de plata, y a 3.79 % del cierre de fin de mes. El contraste
es fuerte pero indirecto —un futuro no es el spot— y por eso el estado es
estimación y no dato.

Hay una segunda evidencia, también indirecta. La serie mensual de plata del FMI,
que declara ser el precio de LBMA, coincide con la del Pink Sheet con una
diferencia mediana de 0.10 % en 560 meses (1980-01 a 2026-08). No es pareja en
el tiempo: la mediana es de 0.08 % hasta 2020, de 0.23 % entre 2021 y 2024, y
sube a 0.63 % desde junio de 2025, con un mes a 3.76 % (diciembre de 2025). El
Banco Mundial no declara ningún cambio en la plata en esa fecha; el del oro sí
está declarado (A-R0-7).

Esos números son con la serie empalmada (A-R0-19). Con la serie redondeada, que
es como se midió primero, la mediana de los 560 meses era de 0.35 %: casi toda
esa diferencia era el redondeo a un decimal.

Pasa a **dato** cuando el Banco Mundial confirme la convención por escrito
(`FUENTES.md`, sección 10.3).

---

## A-R0-9 · La edición vigente del Pink Sheet viene redondeada

**Estado: dato.**

La edición vigente trae el oro redondeado al dólar entero y la plata a un
decimal, en todas sus filas. El redondeo pesa ±0.5 USD en el oro y ±0.05 USD en
la plata.

No siempre fue así. Hasta su edición del 3 de enero de 2025 el Banco Mundial
publicaba la misma serie sin redondear, y por eso el redondeo ya no alcanza a
toda la historia: de 1960-01 a 2024-12 el oro y la plata salen de esa edición
(A-R0-19). El redondeo de la vigente solo pesa desde 2025-01, donde es chico:
0.02 % en el oro y hasta 0.16 % en la plata.

Con la serie entera redondeada, que es como se publicó primero, el error llegaba
a 5.6 % en la plata de 1960 y a 7 % en el ratio Oro/Plata.

No se corrige ni se suaviza. El error máximo de cada valor va publicado fila por
fila, y decide qué meses pueden entrar a una métrica: A-R0-17.

---

## A-R0-10 · Los pares con BTC se publican desde enero de 2013

**Estado: supuesto.**

Coin Metrics tiene precio desde julio de 2010, y Bitstamp desde agosto de 2011.
Hay datos antes de 2013; lo que no hay es acuerdo entre las dos fuentes. El
promedio mensual difiere entre 4 % y 9 % en los cuatro últimos meses de 2011, y
hasta 2.3 % en 2012. Desde enero de 2013 nunca difiere más de 1.31 %, en 165
meses.

Publicar desde 2013-01 es elegir el primer mes a partir del cual una segunda
fuente independiente respalda el número. La fecha es una convención: con una
tolerancia más laxa empezaría antes.

---

## A-R0-11 · La última fila de Shiller no es un mes completo, y el S&P 500 llega con rezago

**Estado: dato la fila y el rezago; supuesto la regla.**

El archivo descargado el 2026-10-04 se modificó por última vez el 2 de
septiembre de 2026. Su última fila, septiembre de 2026, es el cierre del 1 de
septiembre: lo dice el propio archivo, y coincide con el cierre de ese día en
Cboe. Queda 0.495 % por debajo del promedio de los 21 cierres de ese mes.

Por A-R0-1, esa fila se excluye: septiembre no había terminado cuando el archivo
se actualizó. La regla no depende de leer la nota del archivo, que es texto
libre y puede cambiar de redacción. La fecha de actualización es la cabecera
`Last-Modified` de la descarga, y queda guardada en el manifiesto; si no se
conoce, la última fila se descarta siempre.

**El rezago.** La fuente no publica un calendario de actualización. Al 2026-10-04
el último mes completo del S&P 500 es agosto de 2026, un mes por detrás del oro,
la plata y BTC. Los tres pares con S&P 500 llegan hasta donde llegue Shiller.

---

## A-R0-12 · Las fuentes de clase (c) solo sirven para contrastar

**Estado: supuesto.**

Una fuente con licencia paga, permiso previo o uso personal no alimenta ninguna
serie. Se usa para contrastar la serie que sí se publica o se calcula, y de cada
contraste se registra **la fecha, el valor y la diferencia. El archivo no se
guarda ni se publica.**

Los contrastes y sus tolerancias, por mes:

| Serie | Contra qué | Tolerancia | Lo observado al fijarla |
| --- | --- | --- | --- |
| S&P 500 | Promedio de los cierres diarios de FRED `SP500` | ±0.5 % | Máxima de 0.30 % en 620 meses |
| Nasdaq Composite | Promedio de los cierres de la API de nasdaq.com | ±0.1 % | Máxima de 0.027 % en 119 meses |
| BTC | Promedio de los cierres diarios de Bitstamp | ±2 % | Máxima de 1.31 % en 165 meses, desde 2013-01 |
| Oro, plata | El precio promedio anual del USGS, transcrito a mano, contra el promedio de los doce meses | ±0.5 % y ±1 % | Fijadas antes de calcular el gate: A-R0-16 |

Las tolerancias son convenciones. Están puestas por encima de lo observado y por
debajo de lo que produce un error de convención: un cierre de fin de mes se
aparta del promedio de su mes una mediana de 1.36 % en el S&P 500, 1.81 % en el
Nasdaq y 6.25 % en BTC. Un mes suelto puede caer dentro de la tolerancia por
casualidad (pasa en el 19 %, el 3 % y el 19 % de los meses), y por eso el
contraste se hace sobre todos los meses comunes y no sobre uno.

Si un contraste no cierra, la corrida se detiene. **No se ajusta la tolerancia
para que cuadre**: se revisa la fuente, la convención y el mes, en ese orden.

**Qué queda escrito de cada contraste.** En el changelog, por corrida: cuántos
meses se compararon, la diferencia mediana y, del mes que más se aparta, la
fecha y la diferencia. De BTC, que se publica, quedan además los dos valores de
ese mes.

**Del S&P 500 y del Nasdaq no queda ningún nivel del índice**, ni el propio ni
el de contraste. Son series que no se publican (A-R0-14), y un nivel en el
changelog sería publicarlas de a un mes por corrida.

De ninguna queda la serie de contraste mes a mes: eso sería republicar,
promediada, una fuente que no se puede redistribuir.

La diferencia se mide sobre el valor de contraste. Con esa base, la máxima de
BTC en la primera corrida fue de 1.33 % (diciembre de 2017); el 1.31 % de la
tabla es la misma distancia medida sobre Coin Metrics. El contraste del Nasdaq
usa los últimos diez años, la ventana con la que se fijó su tolerancia.

---

## A-R0-13 · Los ratios con índices son de precio, no de retorno total

**Estado: dato.**

El S&P 500 de Shiller y el Nasdaq Composite de FRED son índices de precio: no
incluyen dividendos. Un ratio contra oro o contra BTC, que no pagan nada, deja
afuera una parte del retorno de las acciones, y esa parte se acumula con los
años. El par lo dice junto a su título.

Shiller trae además una columna de retorno total. No se usa.

---

## A-R0-14 · Solo se publica lo que la licencia permite y una segunda fuente valida

**Estado: supuesto.**

Una serie se publica si pasa dos filtros.

**La licencia.** Se publican las series con licencia CC BY, de dominio público, o
CC BY-NC dado el uso no comercial del sitio. Por licencia pueden publicarse tres:
oro y plata (CC BY 4.0) y BTC (CC BY-NC 4.0).

El S&P 500 y el Nasdaq Composite **se calculan en el pipeline y no se publican**.
Los pares que los llevan —Oro/S&P 500, BTC/S&P 500 y Nasdaq/S&P 500— se publican
con el texto **"NO MEDIDO: pendiente de permiso del dueño del índice"**, hasta
tener el permiso escrito de S&P Dow Jones Indices y de Nasdaq.

La alternativa era publicarlos apoyándose en A-R0-2 y A-R0-3. Esos supuestos
alcanzan para calcular, no para publicar: uno descansa en una fuente que no dice
nada sobre su licencia, y el otro en la más favorable de dos frases que no
coinciden.

**La validación.** Ninguna serie se publica sin un caso de validación contra una
segunda fuente, que es la regla de todo el marco. BTC tiene su contraste mensual
(A-R0-12); el oro y la plata, su gate anual (A-R0-16). Si el gate de un metal no
cierra, el metal y los pares que lo llevan se calculan y se publican con el texto
**"NO MEDIDO: sin validación externa"**. Si a un par le faltan las dos cosas, lo
que dice es el permiso.

Los dos textos están en `data/series/pares.csv`, que lista los cinco pares, y en
`data/series/series.csv`, que lista las cinco series. `data/series/ratios.csv` y
`data/series/precios_mensuales.csv` solo traen valores de lo que se publica.

Publicar "NO MEDIDO" donde hay un número calculado es incómodo y es a propósito.
Dice dos cosas ciertas: que el par existe, y que falta algo para mostrarlo.

---

## A-R0-15 · Un crudo entra al repositorio solo si su licencia permite redistribuirlo

**Estado: supuesto.** Excepción a A-S2-10 para las fuentes de la fase R.

| Fuente | Licencia | Dónde vive el crudo |
| --- | --- | --- |
| Pink Sheet, edición vigente | CC BY 4.0 | `data/raw/`, versionado, uno por descarga |
| Pink Sheet, edición del 3 de enero de 2025 | CC BY 4.0 | `data/raw/`, versionado, una sola copia con nombre fijo (A-R0-19) |
| FMI, Primary Commodity Prices | Términos del FMI: redistribuir con atribución; uso comercial con permiso | `data/raw/`, versionado, una sola copia bajada a mano (A-R0-20) |
| Coin Metrics | CC BY-NC 4.0 | `data/raw/`, versionado |
| Shiller | Sin licencia declarada | `data/privado/`, ignorado por git |
| FRED `NASDAQCOM` | Permiso previo del dueño | `data/privado/`, ignorado por git |

CC BY y CC BY-NC permiten redistribuir con atribución. La atribución y la
licencia de cada crudo versionado están en `data/raw/ATRIBUCION.md`, junto a los
archivos. El de Coin Metrics arrastra además su condición: quien redistribuya el
repositorio tiene que mantener el uso no comercial.

En `data/privado/` van también las series y los pares que se calculan y no se
publican.

Para que la corrida siga siendo reproducible sin los crudos que no viajan, por
cada descarga se publica la **URL, la fecha y el SHA-256** en
`data/series/descargas_ratios.csv`, y el código de transformación está en el
repositorio. Quien baje el mismo archivo puede comprobar el hash y rehacer la
serie. Si el crudo que hay en disco no coincide con el hash publicado, la corrida
se detiene.

El costo es real para los dos crudos que quedan afuera: si la fuente revisa o
retira el archivo, la corrida vieja ya no se puede reconstruir desde el
repositorio, solo verificar que el archivo cambió. A-S2-10 existe para evitar
eso, y acá se acepta perderlo.

Y hay un costo de tamaño para los que entran: el crudo de Coin Metrics pesa medio
megabyte y trae la historia completa en cada descarga. La edición congelada del
Pink Sheet pesa 765 KB y la copia del FMI, 619 KB, una sola vez cada una.

---

## A-R0-16 · El gate de oro y plata es anual, contra el USGS

**Estado: supuesto la regla y las tolerancias. El resultado está al final.**

Ninguna serie se publica sin un caso de validación externa (A-R0-14). Para el oro
y la plata no hay una segunda fuente mensual abierta, así que el gate es anual:
**el promedio de los doce meses del Pink Sheet de un año contra el precio
promedio de ese año que publica el USGS** en sus *Mineral Commodity Summaries*,
que es de dominio público. Las cifras del USGS se transcriben a mano, con su
cita, como el ancla del H.4.1.

**Qué años.** Todos los que la última edición trae sin marca de estimado. La de
febrero de 2026 trae 2021, 2022, 2023 y 2024; el 2025 está estimado con datos de
enero a noviembre y no entra. Tienen que ser al menos tres, y tienen que cerrar
todos.

**La convención no es la misma, y está dicho.** El USGS publica el promedio anual
de la cotización de Engelhard, un comerciante de metales de Estados Unidos. El
Pink Sheet promedia el fixing de Londres y, desde junio de 2025, un precio spot
(A-R0-7). Son dos cotizaciones del mismo metal, no la misma cotización. Por eso
el contraste es independiente, y por eso necesita tolerancia.

### Las tolerancias: ±0.5 % el oro, ±1 % la plata

Se fijaron el 2026-10-04, **antes de calcular el gate**, y no se cambian después
de ver el resultado. De qué están hechas:

| Componente | Oro | Plata | De dónde sale |
| --- | --- | --- | --- |
| Redondeo del Pink Sheet (A-R0-9) | ≤ 0.03 % | ≤ 0.23 % | ±0.5 USD sobre 1801 y ±0.05 USD sobre 21.88, los precios anuales más bajos de la ventana. Es el peor caso: los doce meses redondeados para el mismo lado. |
| Redondeo del USGS | ≤ 0.03 % | ≤ 0.02 % | Publica el oro al dólar y la plata al centavo. |
| Promediar doce promedios mensuales en lugar de todos los días del año | ≤ 0.27 % | ≤ 0.27 % | Medido sobre un sustituto, los cierres diarios del Nasdaq Composite de 1972 a 2025: mediana 0.05 %, máximo 0.27 %. El Nasdaq es más volátil que el oro, así que la cota es holgada. |
| **Suma de lo acotado** | **0.33 %** | **0.52 %** | |
| Margen para la diferencia de cotización, fixing de Londres contra Engelhard | 0.17 % | 0.48 % | No se pudo medir. Es lo que el gate pone a prueba. |

El margen para la diferencia de cotización es chico a propósito. Si las dos
cotizaciones se apartan más que eso, el gate no cierra, y eso también es un
resultado: quiere decir que el Pink Sheet y el USGS no describen el mismo precio
con esta precisión. **No se ensancha la tolerancia para que cierre.**

### Si no cierra

El metal y los pares que lo llevan se calculan y se publican como **"NO MEDIDO:
sin validación externa"** (A-R0-14). La corrida no se detiene: BTC y los índices
tienen su propio contraste.

### Lo que se evaluó y no decide

- **El FMI, Primary Commodity Prices.** Existe, es mensual y sin redondear, y
  declara su convención: el oro es el fixing de las 3 PM de Londres y la plata,
  el precio de LBMA. Sus términos permiten reutilizar los datos con atribución.
  No es el gate porque comparte el origen con el Pink Sheet, el fixing de
  Londres: contrasta cómo procesa el dato el Banco Mundial más que el precio.
  Para eso sí sirve, y es el control mensual de A-R0-20. Como sus términos
  prohíben la descarga masiva automatizada sin permiso, entra al pipeline como
  una copia bajada a mano, no como una descarga.
- **El ancla mensual de LBMA.** Era la decisión original y no se pudo cumplir:
  LBMA no publica promedios mensuales fuera de su portal con licencia.
- **Las bandas trimestrales de LBMA.** Siguen como control adicional: un
  promedio mensual no puede caer fuera del mínimo y el máximo que LBMA publicó
  para su trimestre. Un promedio fuera es un error seguro; uno adentro no prueba
  nada.

### El resultado

**Estado: dato.** El gate cerró el 2026-10-04, con las tolerancias ya escritas.

Se calculó dos veces ese día, y las dos están acá. La primera, con la serie
redondeada de la edición vigente. La segunda, después del empalme con la edición
sin redondear (A-R0-19), y es la que vale: los cuatro años del gate caen en el
tramo sin redondear. **Las tolerancias no se tocaron entre una y otra.**

| Año | Oro, doce meses | USGS | Diferencia | Antes del empalme | Plata, doce meses | USGS | Diferencia | Antes del empalme |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 1799.63 | 1801 | −0.076 % | −0.079 % | 25.165 | 25.23 | −0.259 % | −0.251 % |
| 2022 | 1800.60 | 1802 | −0.078 % | −0.069 % | 21.794 | 21.88 | −0.391 % | −0.442 % |
| 2023 | 1942.67 | 1945 | −0.120 % | −0.116 % | 23.399 | 23.54 | −0.601 % | −0.559 % |
| 2024 | 2387.70 | 2388 | −0.012 % | −0.017 % | 28.269 | 28.37 | −0.355 % | −0.335 % |

Cuatro años de cuatro en los dos metales, en las dos pasadas: el oro dentro de
±0.5 % y la plata dentro de ±1 %.

Cuatro cosas que el resultado muestra y que no cambian el gate:

- **Las ocho diferencias tienen el mismo signo.** El Pink Sheet queda siempre por
  debajo de Engelhard. Es la diferencia de cotización para la que se reservó el
  margen, y está registrada como dato en A-R0-18.
- **La plata usa más margen del que se le reservó.** La diferencia llega a
  0.60 % en 2023, por encima del 0.48 % reservado para la diferencia de
  cotización. Cierra dentro de ±1 % porque el redondeo y el efecto del
  calendario no consumieron sus cotas.
- **Un componente de la tolerancia ya no aplica en estos años.** Con la serie
  empalmada, 2021 a 2024 vienen sin redondear, y el redondeo del Pink Sheet
  (0.03 % en el oro, 0.23 % en la plata) deja de contar. La tolerancia no se
  achica por eso: no se cambia después de ver el resultado, para ningún lado.
  Pero sin ese componente quedarían ±0.47 % y ±0.77 %, y el gate cierra igual:
  0.120 % y 0.601 %.
- **El gate valida cuatro años, no toda la historia.** Dice que entre 2021 y 2024
  el nivel anual del Pink Sheet es el de una cotización independiente. No dice
  nada de 1960, ni de los meses posteriores al quiebre de junio de 2025
  (A-R0-7), que el USGS todavía no publica sin estimar.

---

## A-R0-17 · Las métricas sobre un ratio solo usan los meses con error de redondeo de hasta 0.5 %

**Estado: dato el error; supuesto el umbral y la regla.**

Cada valor del oro y de la plata tiene un error máximo por el redondeo con que
la fuente lo publica: medio paso de redondeo sobre el valor.

```
error de un valor = medio paso de redondeo / valor × 100
error del ratio   = suma de los errores de sus dos lados
```

La suma es la cota de primer orden del error relativo de un cociente. El medio
paso depende de qué edición del Pink Sheet se usó en ese mes (A-R0-19):

- **Edición vigente, desde 2025-01.** Declara su precisión: 0.5 USD el oro y
  0.05 USD la plata.
- **Edición del 3 de enero de 2025, hasta 2024-12.** No declara ninguna y trae
  cada mes con los decimales que tenga. El medio paso es el del último decimal
  publicado de ese valor: 35.27 lleva 0.005 y 36 lleva 0.5.

BTC no aporta: Coin Metrics no redondea. El error va publicado junto a cada
valor, en `precios_mensuales.csv` y en `ratios.csv`.

**El umbral.** Una métrica calculada sobre un ratio —un percentil, una
tendencia, cualquier cosa que se presente como evidencia— solo usa los meses en
que el error máximo del ratio no pasa de **0.5 %**. El número es una convención:
con 1 % entrarían más meses y con 0.25 %, menos.

**La regla.** Entran los meses del tramo final sin interrupción, no todos los
que cumplen el umbral de a uno. Los meses anteriores a ese tramo **se publican,
con su error a la vista**, y quedan fuera de percentiles, tendencias y
evidencia. En `ratios.csv` es la columna `apto_metricas`; en `pares.csv`, la
columna `apto_desde`.

**Un valor en disputa tampoco entra.** Un mes en que el Pink Sheet y el FMI se
apartan más que el umbral de A-R0-20 queda fuera de las métricas, aunque su
error por redondeo sea chico. No corta el tramo: es una exclusión puntual y
declarada, mes por mes, no un hueco de precisión. Los meses de antes y de
después siguen siendo aptos, y `apto_desde` no cambia.

Al 2026-10-04:

| Par | Apto desde | Meses del tramo | En disputa (A-R0-20) | Meses aptos | Error máximo en el tramo | Error máximo |
| --- | --- | --- | --- | --- | --- | --- |
| Oro / Plata | **1968-04** | 702 | 20 | 682 de 801 | 0.31 % (1970-05) | 1.39 % (1968-02) |
| BTC / Oro | **2013-01** | 165 | 4 | 161 de 165 | 0.02 % (2025-01) | 0.02 % (2025-01) |

**Lo que corta en 1968 son dos meses.** La edición sin redondear publica el oro
de febrero y de marzo de 1968 como 36 y 37, sin decimales: al dólar, con 1.4 %
de error. Son los dos únicos meses de toda la serie que pasan el umbral. Los 97
anteriores, de enero de 1960 a enero de 1968, lo cumplen de a uno y quedan
afuera por la regla del tramo sin interrupción.

No se supone que 36 quiera decir 36.00. Diez de los 780 valores del oro de esa
edición no traen decimales, y no hay forma de saber cuáles son un promedio que
cayó justo en un entero y cuáles un dato publicado al dólar. A los diez se les
asigna medio dólar de error. En ocho no pesa, porque el oro valía de 163 USD
para arriba; en los dos de 1968, con el oro a 36 y 37, pasa el umbral.

**Antes del empalme** el tramo apto de Oro/Plata empezaba en 2009-02, con 212
meses: toda la serie estaba redondeada y la plata tenía que valer unos 11 USD
para cumplir el umbral. Ahí la regla del tramo final importaba por otra razón:
había 44 meses sueltos que cumplían el umbral porque la plata estaba cara, y
usarlos habría sido elegir meses por el valor de lo que se mide.

**La precisión se comprueba, no se asume.** En cada corrida el script verifica
que todos los valores de la edición vigente sean enteros en el oro y múltiplos
de 0.1 en la plata. Si el Banco Mundial cambia la precisión con que publica, el
error declarado deja de ser cierto y la corrida se detiene.

**Lo que este error no es.** Es la cota del redondeo y nada más. Que un mes sea
apto no quiere decir que la serie sea homogénea hasta ahí: no cubre el cambio de
definición del oro (A-R0-7), ni que la convención de la plata sea una estimación
(A-R0-8), ni la diferencia de horas entre cierres (A-R0-6).

---

## A-R0-18 · En los ocho contrastes anuales, el Banco Mundial queda por debajo de Engelhard

**Estado: dato.** Es una observación, no un problema.

El gate de oro y plata (A-R0-16) compara el promedio de doce meses del Pink
Sheet contra el precio anual del USGS, que es la cotización de Engelhard. Son
ocho contrastes, cuatro años por dos metales, y en los ocho el Pink Sheet queda
por debajo:

| Año | Oro | Plata |
| --- | --- | --- |
| 2021 | −0.076 % | −0.259 % |
| 2022 | −0.078 % | −0.391 % |
| 2023 | −0.120 % | −0.601 % |
| 2024 | −0.012 % | −0.355 % |
| Promedio | −0.072 % | −0.402 % |

Son los números con la serie sin redondear (A-R0-19). Con la serie redondeada,
que es como se observó primero, los promedios eran −0.070 % y −0.397 %: el
redondeo no cambia el sesgo.

Ocho de ocho con el mismo signo no es ruido de redondeo, que no tiene
preferencia de lado. Es un sesgo.

**De dónde sale.** De la cotización, no de cómo procesa los datos el Banco
Mundial. La serie del FMI, que declara ser el fixing de Londres y viene sin
redondear, queda por debajo de Engelhard en los mismos ocho contrastes y por
montos parecidos: de −0.03 % a −0.10 % en el oro y de −0.25 % a −0.60 % en la
plata. Y el Pink Sheet y el FMI quedan entre sí a menos de 0.06 % en el oro y de
0.16 % en la plata. Las dos series de Londres están juntas, y Engelhard está un
poco más arriba que las dos.

Que la cotización de un comerciante quede por encima de un fixing de mercado es
esperable, y el margen de la tolerancia del gate estaba reservado para eso. Lo
que no está medido es por qué el sesgo de la plata es más de cinco veces el del
oro: no se leyó cómo forma Engelhard su cotización.

**Qué implica.**

- **Para el gate, nada.** Cierra dentro de la tolerancia en los ocho. El sesgo
  consume margen, sobre todo en la plata, donde llega a 0.60 % de un 1 %.
- **Para leer el gate.** Una diferencia de signo contrario, o una que crezca,
  sería una señal más fuerte que una del mismo signo y tamaño parecido. Si un
  año futuro da positivo, conviene mirarlo aunque cierre.
- **Para las series.** No se corrige nada. Las series publicadas son las del
  Banco Mundial tal como vienen; no se les suma el sesgo para acercarlas a
  Engelhard. El gate dice que las dos cotizaciones describen el mismo precio
  dentro de la tolerancia, no que sean iguales.

---

## A-R0-19 · El oro y la plata se empalman: edición de enero de 2025 hasta 2024-12, edición vigente después

**Estado: supuesto el empalme; dato lo que lo sostiene.**

El oro y la plata salen de dos ediciones del mismo archivo del Banco Mundial:

| Tramo | Edición | Precisión |
| --- | --- | --- |
| 1960-01 a 2024-12 | La del 3 de enero de 2025, congelada | Sin redondear |
| Desde 2025-01 | La vigente, que se descarga en cada corrida | Oro al dólar, plata a un decimal |

El corte no se eligió: diciembre de 2024 es el último mes que trae la edición
congelada. `precios_mensuales.csv` dice, fila por fila, de cuál sale cada mes.

**Por qué se pueden empalmar.** Porque son la misma serie, publicada con distinta
precisión, y eso se comprueba en cada corrida: **redondear la edición congelada
tiene que reproducir la vigente en todos los meses que tienen en común.** Un mes
coincide si la congelada queda a no más de medio paso de redondeo de la vigente.
El 2026-10-04 coincidieron los 780 meses del oro y los 780 de la plata.

Los que quedan *exactamente* a medio paso —un valor terminado en ,5 justo— se
aceptan y se listan en el changelog, porque ahí las dos formas de redondear son
válidas. Son doce:

- Oro, once: 1968-01, 1971-10, 1973-04, 1982-12, 1985-03, 1985-06, 1985-11,
  2002-02, 2015-06, 2016-02 y 2022-05.
- Plata, uno: 2015-09.

**Si el control falla, la corrida se detiene** y no escribe ninguna serie. Un mes
que no coincide quiere decir que el Banco Mundial revisó ese dato después de
enero de 2025, y entonces la edición congelada ya no es la versión sin redondear
de la vigente: es otra serie. No se corrige a mano. Hay que releer la fuente y
decidir de nuevo de dónde sale ese tramo.

**La edición congelada no depende de su URL.** El archivo está versionado en
`data/raw/` con nombre fijo, y el pipeline usa esa copia, identificada por su
SHA-256. No sale a buscarla. La dirección de la que se bajó es la que el archivo
tenía en enero de 2025, y la página actual del Banco Mundial ya no la enlaza: si
deja de responder, nada cambia. Solo si la copia falta el script la descarga, y
la acepta únicamente si el hash es el esperado.

**La precisión de la edición congelada no está declarada.** Trae cada mes con
los decimales que tenga:

| Decimales | Meses del oro | Meses de la plata |
| --- | --- | --- |
| Ninguno | 10 | 0 |
| 1 | 80 | 1 |
| 2 | 610 | 22 |
| 3 | 73 | 217 |
| 4 o 5 | 0 | 535 |
| 10 u 11 | 7 | 5 |

Por eso el error por redondeo de ese tramo no es cero: es media unidad del
último decimal publicado de cada valor (A-R0-17). En casi todos los meses es
despreciable. En dos no: febrero y marzo de 1968, que vienen sin decimales y con
el oro a 36 y 37 USD.

**Lo que el empalme cuesta.**

- La edición congelada **no recibe revisiones**. Si el Banco Mundial corrige un
  mes anterior a 2025, la serie publicada no lo sabe; lo que hay es el control,
  que detiene la corrida.
- Los dos tramos **no tienen la misma precisión**, y el salto está en enero de
  2025. Va declarado en cada fila.
- El archivo pesa 765 KB en el repositorio.

**Lo que el empalme no arregla.** El cambio de definición del oro de junio de
2025 (A-R0-7) cae entero en la edición vigente. Y la convención de la plata
sigue siendo una estimación (A-R0-8): la edición congelada trae la misma
descripción que la vigente.

**Alternativa.** Usar solo la edición vigente, redondeada, para toda la historia.
Es como se publicó primero. Con ella Oro/Plata es apto para métricas desde
2009-02 en lugar de 1968-04.

---

## A-R0-20 · El oro y la plata se comparan cada mes con el FMI; el mes que pasa del umbral queda como valor en disputa

**Estado: supuesto el umbral y la regla; dato lo que el control encuentra.**

**De dónde sale.** Al rehacer la comparación con el FMI con la serie empalmada
apareció un mes del oro que no cierra: marzo de 1985, con 313.5 en el Pink Sheet
y 303.94 en el FMI. El gate anual (A-R0-16) no lo ve: cubre 2021 a 2024. Hacía
falta un control que mirara toda la historia.

**Qué compara.** En cada corrida, el oro y la plata que se publican contra las
series `PGOLD` y `PSILVER` del FMI, mes a mes, sobre todos los meses que tienen
en común. Hoy son 560 por metal, de 1980-01 a 2026-08. La diferencia se mide
sobre el valor del FMI.

**Qué le pasa a un mes que pasa del umbral.** Queda como **valor en disputa**:

- Se publica **sin cambios**, con el valor del Pink Sheet. Si está mal, se
  reporta; no se corrige en silencio.
- `precios_mensuales.csv` lo dice junto al valor, con los dos números y la
  diferencia. Los demás meses dicen "dentro del umbral" o "sin comparar".
- **No entra a ninguna métrica**, ni él ni los ratios que lo llevan. `ratios.csv`
  dice qué lado del par está en disputa.
- **No corta el tramo apto** (A-R0-17). Es una exclusión puntual y declarada.
- Queda listado en el changelog de la corrida, con los dos valores.

**No detiene la corrida.** No es un gate: no cierra ni deja de cerrar. Y no
decide cuál de las dos fuentes tiene razón.

### El umbral: ±0.5 % el oro, ±1 % la plata

Es la tolerancia del gate anual (A-R0-16). No es un número nuevo, y esa es la
razón de usarlo: **cuando se fijó el umbral, la comparación ya estaba hecha.**
Se conocía el caso de marzo de 1985 y se conocía la distribución de las
diferencias. Elegir un número en ese momento habría sido elegirlo mirando el
resultado. La tolerancia del gate estaba escrita desde antes, con su
justificación, y es la medida que este proyecto ya usa para decir que dos
cotizaciones de un metal describen el mismo precio.

Lo que daría otro umbral, para que se vea cuánto pesa la elección:

| Umbral | Meses del oro en disputa | Meses de la plata en disputa |
| --- | --- | --- |
| 0.25 % | 32 | 143 |
| 0.5 % | **10** | 59 |
| 1 % | 2 | **10** |
| 2 % | 1 | 1 |

En negrita, lo que rige. No se ajusta para que un mes entre o salga.

### Lo que encontró el 2026-10-04

Diferencia mediana de 0.017 % en el oro y de 0.096 % en la plata. Veinte meses
en disputa, diez por metal:

| Oro | Pink Sheet | FMI | Diferencia | Plata | Pink Sheet | FMI | Diferencia |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1985-03 | 313.5 | 303.94 | 3.145 % | 1980-01 | 38.8756 | 39.2843 | −1.040 % |
| 1985-11 | 321.5 | 325.24 | −1.150 % | 1985-07 | 5.9997 | 6.0836 | −1.379 % |
| 1986-01 | 347.48 | 345.38 | 0.608 % | 1985-08 | 6.1511 | 6.2498 | −1.580 % |
| 1997-09 | 322.82 | 324.4762 | −0.510 % | 1987-04 | 7.3495 | 7.4727 | −1.649 % |
| 2000-05 | 275.19 | 276.7409 | −0.560 % | 2004-04 | 7.1486 | 7.055 | 1.327 % |
| 2011-12 | 1639.97 | 1652.3056 | −0.747 % | 2011-04 | 42.6952 | 41.9656 | 1.739 % |
| 2015-12 | 1075.74 | 1068.2526 | 0.701 % | 2011-05 | 37.3359 | 36.75 | 1.594 % |
| 2016-12 | 1157.36 | 1151.4028 | 0.517 % | 2020-07 | 20.647 | 20.405 | 1.186 % |
| 2025-05 | 3309 | 3288.0095 | 0.638 % | 2024-12 | 30.764 | 30.3707 | 1.295 % |
| 2026-01 | 4753 | 4719.7059 | 0.705 % | 2025-12 | 62.3 | 64.7325 | −3.758 % |

Ningún mes coincide entre los dos metales. Oro/Plata pierde los veinte y queda
con 682 meses aptos de 801; BTC/Oro pierde los cuatro del oro desde 2013 y queda
con 161 de 165.

Cinco de los veinte son diciembres: 2011, 2015 y 2016 en el oro, 2024 y 2025 en
la plata. No se estableció por qué.

### Marzo de 1985

Tiene una tercera lectura. El *Minerals Yearbook 1985* del Bureau of Mines trae
el promedio mensual de la cotización de Engelhard, que es independiente del
fixing de Londres: **304.34** para marzo. El FMI queda a −0.13 % de ese valor y
el Pink Sheet, a +3.0 %.

La misma tabla trae los otros once meses del año. El FMI queda siempre entre
−0.32 % y −0.01 % de Engelhard. El Pink Sheet queda dentro de ±0.5 % en diez y
se aparta en dos, que son justo los dos del oro de 1985 que el control marca:
marzo y noviembre (321.5, contra 325.64 de Engelhard y 325.24 del FMI).

La lectura es que en esos dos meses el valor correcto es el del FMI y que el del
Pink Sheet está mal. **El valor publicado no se cambia:** marzo sigue siendo
313.5 y noviembre 321.5, marcados como valor en disputa, y lo que corresponde
es reportarlos al Banco Mundial (`FUENTES.md`, secciones 4.7 y 10.3). Los otros
dieciocho no tienen tercera lectura: de esos no se sabe cuál fuente tiene razón.

### Lo que el control no hace

- **No valida el nivel.** El Pink Sheet y el FMI declaran el mismo origen, el
  mercado de Londres. Coincidir con el FMI no prueba que el precio sea el
  correcto: prueba que el Banco Mundial no se apartó de él al procesarlo. El
  nivel lo valida el gate, contra una cotización independiente.
- **No cubre toda la historia.** El FMI empieza en 1980 y su copia llega hasta
  agosto de 2026. Los 240 meses anteriores a 1980 y los posteriores a la copia
  quedan como **"sin comparar"**: ni en disputa ni confirmados. Del tramo apto
  de Oro/Plata, los 141 meses de 1968-04 a 1979-12 no tienen control.
- **No corrige.** Un mes en disputa conserva su valor.

### La copia del FMI

Los términos del FMI para sus datos estadísticos permiten redistribuirlos:
*"You may download, extract, copy, create derivative works, publish, distribute,
and use Data obtained from IMF Sites"*, con atribución. Y prohíben bajarlos en
masa con un programa: *"The IMF prohibits the bulk download of information by
automated technology without explicit permission"*.

Un archivo por corrida no es evidentemente una descarga masiva. Pero decidir eso
es interpretar la cláusula, y la regla de este proyecto es no depender de una
interpretación. Por eso:

- El archivo se bajó **una vez**, el 2026-10-04, y está versionado en
  `data/raw/fmi_pcps_2026-10-04.xlsx`, con su atribución en `ATRIBUCION.md`.
- El pipeline lo identifica por su SHA-256 y **nunca sale a buscarlo**. Si la
  copia falta o cambió, la corrida se detiene con un error de fuente y dice de
  dónde bajarla a mano. No sigue sin el control: el control decide qué meses
  entran a las métricas.
- **Actualizarla es un acto manual:** bajar la edición nueva, y cambiar en
  `configuracion.py` el nombre, la fecha y el hash. Hasta entonces, los meses
  nuevos se publican como "sin comparar".
- La descripción de cada serie se verifica contra la que se leyó. Si el FMI la
  cambia, la corrida se detiene.

**Condición.** Los mismos términos piden permiso para el uso comercial: *"For
any potential commercial reuse of IMF Data, please email copyright@imf.org to
request permission."* Como A-R0-2, A-R0-3 y A-R0-4, esto vale **mientras el
sitio no tenga vínculo comercial**.

**Alternativa.** Pedirle permiso al FMI para bajar el archivo en cada corrida
(`FUENTES.md`, sección 10.4). Con eso el control alcanzaría siempre al último
mes que el FMI publique.
