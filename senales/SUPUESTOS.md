# Supuestos

Cada decisión que afecta un número publicado está aquí, numerada y con estado.
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
para volver a ella, apuntar `SERIE_TGA` ahí y registrar el cambio aquí y en
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
  silencioso: hay que arreglar la configuración y anotarlo aquí.
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
molesta, la decisión a tomar es cuántas descargas conservar, y va aquí antes de
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
está en `FUENTES.md`; aquí va la decisión y lo que la haría cambiar.

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

No era la única convención posible. Hasta la fase 3 el sitio usaba el cierre de
fin de mes para índices y metales, y el borrador de `FUENTES.md` proponía el
cierre semanal del viernes. Decidió la licencia: las únicas fuentes abiertas de
oro y plata son promedios mensuales.

Hoy el sitio lee las series de `senales/` y no tiene otra fuente: lo que muestra
es esta convención, el promedio mensual de cierres diarios (`FUENTES.md`,
sección 8.1).

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
(A-R0-19). El redondeo de la vigente solo pesa desde 2025-01, donde es pequeño:
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
eso, y aquí se acepta perderlo.

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

El margen para la diferencia de cotización es pequeño a propósito. Si las dos
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

Se calculó dos veces ese día, y las dos están aquí. La primera, con la serie
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
error por redondeo sea pequeño. No corta el tramo: es una exclusión puntual y
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

**El corte coincide con el fin del London Gold Pool.** Hasta marzo de 1968 el
precio del oro en Londres no era un precio libre. Lo sostenían los principales
bancos centrales, que compraban y vendían oro en ese mercado para mantenerlo
pegado a la paridad oficial de 35 USD la onza. Bordo, Monnet y Naef lo
describen así:

- *"They coordinated their purchases and sales of gold in London to stabilize
  the gold-dollar parity on which the whole Bretton Woods system was built."*
  (p. 2)
- *"The dollar-price of gold accepted by the Gold Pool lay within a wide band
  [35.08 - 35.20]"* (p. 23).
- *"On March 15, 1968, the Gold Pool was disbanded and a two-tier arrangement
  put in its place."* (p. 47)

Fuente: Michael Bordo, Eric Monnet y Alain Naef, *The Gold Pool (1961-1968) and
the Fall of the Bretton Woods System. Lessons for Central Bank Cooperation*,
NBER Working Paper 24016, noviembre de 2017, `https://www.nber.org/papers/w24016`.
Leído el 2026-10-04. Es un documento de trabajo, sin revisión de pares, y lo
dice en su portada.

Lo que eso dice del tramo apto:

- **Abril de 1968 es el primer mes completo sin el Pool.** Antes, el numerador
  de Oro/Plata estaba sostenido administrativamente cerca de 35 USD, y el ratio
  se movía casi solo por la plata. En la serie, el oro va de 34.95 a 35.27
  entre 1960-01 y 1967-12; en abril de 1968 vale 37.86 y en mayo, 40.70.
- **La regla corta ahí por precisión, no por esto.** Lo que deja afuera a los
  meses anteriores son febrero y marzo de 1968, publicados al dólar. Pero son
  los dos últimos meses del Pool: el corte por precisión cae donde también
  cambia lo que el precio mide. Que una cosa explique la otra es una lectura;
  la fuente no lo dice.
- **El Pink Sheet de esos meses no calza con lo que describe el paper.** Trae
  34.95 de octubre a diciembre de 1967, por debajo de la banda, y 35.5 y 36
  para enero y febrero de 1968, por encima de un techo que, según el paper, el
  precio no volvió a pasar mientras el Pool operó (*"the price would never
  exceed this limit again"*, p. 23). No se contrastó mes a mes: el paper no
  publica la serie. Es una razón más para no usar esos meses.

No cambia la regla ni el tramo.

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

---

## Fase D0 · El Denominador: los supuestos A-D0-\*

Se fijaron el 2026-10-05 al aprobarse el paso 0 de la fase D0 (`FUENTES.md`,
sección D0, decisiones D0.10 y las siete del dueño del 2026-10-05), y se
completaron el 2026-10-06 al escribir `denominador.py`. La evidencia de cada
cifra está en `FUENTES.md`; aquí va la decisión y lo que la haría cambiar.

Dos de estos supuestos son **condicionales**: A-D0-8 (Banco de Japón) vale
mientras el sitio no tenga vínculo comercial, como A-R0-4; A-D0-9 (China vía la
OCDE y el BIS) vale mientras la OCDE y el BIS mantengan sus términos de
reutilización y no aparezca una restricción de terceros en sus metadatos.

---

## A-R0-21 · El precio oficial del oro es una serie de contexto: fijado por ley, no observado; fuera de las métricas y sin empalme

**Estado: supuesto.** Decisión del dueño del 2026-10-07 (`FUENTES.md`, 4.8).

`oro_precio_oficial.csv` publica, de 1900-03 a 1959-12, el precio del oro en
USD por onza troy que fijaba la ley: el dólar de 25,8 granos de oro de 9/10 de
fino (ley del 14 de marzo de 1900, sección 1) y, desde el 31 de enero de 1934,
el de 15 5/21 granos (proclamación presidencial). Cada fila lleva la etiqueta
"precio oficial fijado por ley, no precio de mercado", la norma, su fecha de
vigencia, la cita y `apto_metricas = no`. No es lado de ningún ratio, no entra
a percentiles ni tendencias, y no se empalma con el oro del Pink Sheet: en
1960-01 termina esta serie y empieza otra (A-R0-7); en el sitio son dos series.
La ficha va en `series.csv` y la conserva cada corrida de `ratios.py`.

## A-R0-22 · El mes en que cambia la norma lleva el precio anterior, con la convención publicada por la Junta

**Estado: dato la convención; supuesto adoptarla.**

La proclamación rige desde las 15:10 del 31 de enero de 1934. La Junta valúa
sus propias tablas *"at the rate of $20.67 per fine ounce of gold through
January 1934 and $35 per fine ounce thereafter"* (*Banking and Monetary
Statistics 1914–1941*, p. 522). Se adopta esa convención: enero de 1934 =
20,6718; febrero de 1934 = 35,00. No se promedia por días: sería un valor que
ninguna fuente publica.

## A-R0-23 · El precio se deriva de la fracción legal y se publica a cuatro decimales

**Estado: supuesto los decimales; dato la derivación.**

480 granos por onza troy ÷ (granos del dólar × ley de fino), con fracciones
exactas en el código: 480 ÷ (129/5 × 9/10) = 8000/387 = 20,671835…, y 480 ÷
(320/21 × 9/10) = 480 ÷ (96/7) = 35 exactos. Se publican cuatro decimales,
como la Casa de Moneda ("$20.6718", "$35.0000"); el error de redondeo es de
0,00005 USD y no importa porque la serie queda fuera de las métricas.

## A-R0-24 · La serie empieza el 14 de marzo de 1900; antes queda NO MEDIDO hasta leer la base legal

**Estado: no medido lo anterior a 1900.**

La ley de 1900 remite a la sección 3511 de los *Revised Statutes*, que
codifica las leyes de 1834, 1837 y 1873. Esas leyes están en los *Statutes at
Large* en loc.gov, que el 2026-10-07 exigía una verificación humana y no se
pudo leer. La serie se publica desde 1900-03 y la ficha dice que lo anterior
es NO MEDIDO. Extenderla hacia atrás exige leer esas leyes u otra reimpresión
oficial, y un supuesto nuevo.

## A-R0-25 · El gate del precio oficial es de nivel y de fecha, contra cuatro instituciones, con ±0,005 USD

**Estado: supuesto.** Tolerancia declarada el 2026-10-07 antes de comparar.

Para una serie escalonada de dos valores no hay una segunda medición; lo que
se valida es que el precio derivado de la norma sea el que publican otras
instituciones y que el cambio caiga en el mes que dicen. Cifras leídas a mano,
con página: Tesoro ("$20.67+" y "$35", informe de 1934, p. 120), Casa de
Moneda ("$20.6718" y "$35.0000", ejercicio 1935, p. 91), Junta ("$20.67"
hasta enero de 1934 y "$35" después, BMS 1914–1941, p. 522) y FMI (0,888671
gramos de oro fino por dólar = 35,0000, *Federal Reserve Bulletin*, enero de
1947, p. 12). Tolerancia ±0,005 USD (medio centavo) en cada cifra, mínimo
tres, y el primer mes a 35 tiene que ser 1934-02. Resultado, después de
declararla: seis cifras, diferencia máxima 0,0018; cerró. Lo que el gate no
cubre: la fecha de inicio (A-R0-24) y una norma intermedia que ninguna de las
cuatro publicaciones mencione, y no se encontró ninguna.

## A-R0-26 · De 1933-03 a 1934-01 rige la paridad legal sin convertibilidad; el precio administrado de 1933–34 es otra cosa y se declara

**Estado: dato.**

El Tesoro lo dice: *"The rate for gold other than newly mined gold ... remained
at $20.67 an ounce"* (informe de 1934, p. 204), y en el ejercicio 1934 compró
oro *"at $20.67+ per fine ounce"* y *"at $35 per fine ounce"* (p. 120). Lo que
cambió fue la convertibilidad (sin pagos en oro desde el 6 de marzo de 1933,
exportación con licencia desde el 10 de marzo, tenencia privada prohibida
desde el 5 de abril), y la serie lo dice en la columna `convertibilidad`. Del
8 de septiembre de 1933 al 31 de enero de 1934 hubo además un precio
administrado, diario, para el oro recién extraído (29,00 a 34,45 USD por
onza; informe de 1934, anexo 26, p. 205): no es el precio oficial, no está en
la serie, y la ficha y las filas de esos meses lo declaran. Si alguna vez se
publica, va como serie aparte, con su etiqueta.

## A-D0-1 · Cada serie se publica en su moneda, su unidad y su convención nativas

**Estado: supuesto.** Decisión del 2026-10-05 (D0.10.1 y D0.10.4).

Ninguna serie se convierte de convención: el M2 de EE.UU. y el de Japón son
promedios del mes porque así los publican la Junta y el BoJ; el de la Eurozona
y el de China son saldos de fin de mes; el balance de la Fed es el nivel del
último miércoles del mes y el del Eurosistema, el cierre del último viernes.
La convención, la unidad y la moneda van en `serie_D0.csv`, fila por fila.

**Lo que lo haría cambiar.** Que un emisor publique la otra convención.

## A-D0-2 · El M2 de EE.UU. es un promedio mensual de cifras diarias; no existe a fin de mes

**Estado: dato.** Leído en el H.6 (`FUENTES.md`, D0.2).

La propuesta de "fin de mes para los saldos" no se puede cumplir para EE.UU. La
consecuencia útil: Oro / M2 y BTC / M2 cumplen la regla de la convención de
`CLAUDE.md` sin excepción, porque los dos lados son promedios mensuales.

## A-D0-3 · La titular del M2 de EE.UU. es la ajustada; el agregado usa las series sin ajustar

**Estado: supuesto.**

`m2_eeuu` es `M2.M`, la ajustada por estacionalidad, como en la Tabla 1 del
H.6. Se publica además `m2_eeuu_sin_ajustar` (`M2_N.M`). El agregado en USD
suma las series sin ajustar, porque es la única versión que existe en todas
las economías y porque cada emisor ajusta con su propio método.

## A-D0-4 · El M2 y el balance de la Eurozona son de composición cambiante: cada ampliación es un salto declarado, no corregido

**Estado: dato el salto; supuesto no corregirlo.**

El área de las series es `U2`, "Euro area (changing composition)". Las nueve
ampliaciones leídas (Grecia 2001-01, Eslovenia 2007-01, Chipre y Malta 2008-01,
Eslovaquia 2009-01, Estonia 2011-01, Letonia 2014-01, Lituania 2015-01, Croacia
2023-01, Bulgaria 2026-01) van en la columna `quiebre` del mes que corresponde,
en `denominador_dinero.csv` y en `denominador_balances.csv`. El valor no se
toca: el BCE no publica un M2 de composición fija.

**Lo que lo haría cambiar.** Que el BCE publique una serie de composición fija.

## A-D0-5 · El M2 de la Eurozona de 1980-01 a 1997-08 es una estimación del BCE

**Estado: estimación.** Decisión del dueño del 2026-10-05.

El BCE lo describió así en su Boletín de febrero de 1999 (`FUENTES.md`, D0.4);
la API entrega esos meses sin marca. La columna `estado` de
`denominador_dinero.csv` dice "estimación" hasta 1997-08 y "dato" desde
1997-09. Sigue abierta la pregunta al BCE de si los valores actuales de ese
tramo siguen siendo los de aquel método (`FUENTES.md`, D0.13).

## A-D0-6 · El M2 de Japón empieza en 2003-04; M2+CDs es otra serie y no se empalma

**Estado: dato el inicio; supuesto no empalmar.**

El BoJ no construyó una serie larga enlazada porque no lo considera apropiado
(`FUENTES.md`, D0.5). Tampoco se hace aquí. Las series anteriores (M2+CDs,
1967-01 a 2008-04) están en el mismo crudo y **se publican aparte desde el
2026-10-07**, en sus dos tramos y sin empalme (A-D0-34); el agregado las usa
hasta 2003-03 con el quiebre declarado (A-D0-36).

## A-D0-7 · BCE: el dato se publica tal cual y con fuente; toda serie derivada se rotula como cálculo propio

**Estado: supuesto de licencia.**

La política de reutilización del SEBC permite reutilizar sin modificar; el
aviso de copyright del BCE admite modificar si se declara. Las series del BCE
se publican sin cambios con la cita "Source: ECB statistics". Lo que se calcula
con ellas (la conversión a USD, el agregado) lleva su propia ficha y dice que
es un cálculo propio. Hay una pregunta al BCE al respecto en `FUENTES.md`, D0.13.

## A-D0-8 · Banco de Japón: uso bajo la cláusula no comercial, con aviso y crédito por la API

**Estado: supuesto condicional.** Vale mientras el sitio no tenga vínculo
comercial, como A-R0-4.

El aviso de copyright del BoJ permite copiar y reproducir con cita de la
fuente, salvo con fines comerciales. Las instrucciones de su API piden avisar
por correo al publicar un servicio que la use y mostrar un crédito. El aviso
es un paso previo a desplegar el sitio con estas series; el crédito va en la
columna `atribucion` de `serie_D0.csv`.

## A-D0-9 · China entra por la OCDE y el BIS, con el rótulo de la fuente, fuera del agregado y sin ninguna descarga del PBoC

**Estado: supuesto condicional.** Decisión del dueño del 2026-10-05.

- El PBoC es el emisor, pero su aviso legal reserva los derechos y solo prevé
  la atribución para medios ya autorizados, y su `robots.txt` veda a todo
  agente salvo Baiduspider (`FUENTES.md`, D0.6.1). **El pipeline no pide nada a
  pbc.gov.cn.**
- El dinero amplio sale de la OCDE (`CHN.M.MABM.XDC`), que lo rotula "M3". La
  serie se llama como la fuente la llama —"Dinero amplio de China (M3 de la
  OCDE)"— y **nunca M2**. Se publica desde 2004-01, el primer año con una tabla
  del PBoC contra la cual se la comparó.
- El balance sale del BIS (`WS_CBTA`, área CN), desde 2002-01, que es desde
  cuando el BIS declara usar el balance mensual del PBoC. En esta entrega
  queda **NO MEDIDO: sin validación externa**, porque las únicas lecturas de
  la tabla del PBoC salieron de descargas automáticas de su sitio, que se
  descartaron. Dos valores leídos a mano por una persona (`ANCLAS_BALANCE_PBOC`)
  lo destraban.
- **Queda fuera del agregado** mientras no se demuestre que su definición es
  comparable con las otras tres. Lo leído dice lo contrario: el agregado del
  PBoC incluye los depósitos de instituciones financieras no depositarias
  (desde 2011-10) y las participaciones en fondos del mercado monetario (desde
  2018-01) sin los topes de monto y plazo del M2 del H.6, y la OCDE lo
  clasifica en la misma categoría que el M3 del BoJ, no que su M2.
- El gate del dinero amplio son lecturas en pantalla de la Oficina Nacional
  de Estadísticas de China, que republica al PBoC, con tolerancia de 50
  millones de yuanes: el medio paso del redondeo de la OCDE. Hay dos (2026-07
  y 2020-03) y hacen falta tres (A-D0-25): **la serie queda NO MEDIDO hasta
  tener una tercera lectura**, que el dueño hace en pantalla.

**Lo que lo haría cambiar.** Un permiso escrito del PBoC, o una lectura de las
definiciones que muestre comparabilidad.

## A-D0-10 · El agregado en USD es una serie derivada; el tipo de cambio es el del H.10, promedio o fin de mes según la convención de cada serie

**Estado: supuesto.**

`denominador_agregado.csv` suma el M2 sin ajustar de EE.UU., la Eurozona y
Japón en miles de millones de USD. EE.UU. ya está en USD. La Eurozona, saldo
de fin de mes, se convierte con el USD por EUR del último día hábil del mes.
Japón, promedio de saldos, se convierte con el promedio mensual de JPY por USD
(G.5). El agregado empezaba en 2003-04, el primer mes del M2 de Japón; desde
el 2026-10-07 empieza en 1999-01, el primer mes del tipo de cambio del euro,
con Japón por tramos (A-D0-36).

## A-D0-11 · El agregado a tipo de cambio constante usa el del primer mes común

**Estado: supuesto.**

La columna `agregado_usd_tc_constante` convierte cada mes con los tipos de
cambio del primer mes común. La diferencia con `agregado_usd` es el efecto
del tipo de cambio, mes a mes, sin estimar nada. Elegir otro mes de
referencia cambia los niveles de esa columna, no los de la otra.

**El mes de referencia cambió el 2026-10-07: de 2003-04 a 1999-01**, porque
el agregado empieza ahora en 1999-01 (A-D0-36). Toda la columna a tipo de
cambio constante cambia de nivel por eso; la columna a tipo de cambio de cada
mes no cambia en los meses que ya existían.

## A-D0-12 · El agregado mezcla promedios y saldos de fin de mes; no se publica ningún ratio contra él

**Estado: dato la mezcla; supuesto la regla.** Decisión del dueño del 2026-10-05.

`CLAUDE.md` exige la misma convención en los dos lados de un ratio. Oro / M2 y
BTC / M2 de EE.UU. la cumplen; contra el agregado no se cumpliría, y por eso
esos pares no existen.

## A-D0-13 · El Índice Denominador 60/40 se elimina

**Estado: supuesto.** Decisión del dueño del 2026-10-05.

La ponderación no tenía fuente, la base 1913 no tiene dato en ninguna de las
ocho series, y el efectivo está en los dos lados (es parte de M2 y pasivo del
banco central). Las dos familias se muestran por separado.

## A-D0-14 · De semanal a mensual: el último dato semanal fechado dentro del mes, con su fecha de origen visible

**Estado: supuesto.**

Para el balance de la Fed (miércoles) y el del Eurosistema (viernes), el valor
del mes es el del último dato semanal fechado dentro del mes, y la columna
`fecha_origen` de `denominador_balances.csv` dice cuál. Un mes está completo
cuando el dato siguiente ya cae en otro mes. Coincide con la regla del BIS para
la Fed, no para el Eurosistema: el BIS toma la semana que contiene el último
día hábil, cuyo viernes puede caer en el mes siguiente. El gate contra el BIS
usa la regla del BIS.

## A-D0-15 · El balance de la Fed es la serie consolidada del XML del H.4.1; la diferencia con el total sin consolidar son las eliminaciones

**Estado: dato.** Verificado el 2026-10-06 sobre el XML del H.4.1.

El XML trae dos totales. `RESPPA_N.WW` es la suma bruta de los doce bancos de
la Reserva; `RESPPMA_N.WW` es el total consolidado, menos las eliminaciones de
partidas en proceso de cobro entre bancos (`RESPPMAX_N.WW`). Bruto menos
consolidado es igual a las eliminaciones en las 1.242 semanas, con ±1 millón
de redondeo; las eliminaciones son distintas de cero en 515 semanas, de
2002-12-18 a 2012-10-24, y cero después. El consolidado coincide con `WALCL`
de FRED en las 1.242 semanas. D0 publica el consolidado. Esto cierra la
pregunta de `FUENTES.md` D0.7.1: no eran revisiones, era definición.

## A-D0-16 · Los balances del Eurosistema y del BoJ llevan sus quiebres declarados, sin corregir

**Estado: dato el quiebre; supuesto no corregirlo.**

Eurosistema: las ampliaciones (A-D0-4) y la revalorización trimestral de oro,
divisas y títulos, que no se marca mes a mes porque afecta a todos los fines
de trimestre. BoJ: el cambio contable de las operaciones repo de 2001-04, que
hace al total no comparable con los meses anteriores. Van en `quiebre` y en
la ficha.

## A-D0-17 · EE.UU. antes de 1959: tres tramos de publicaciones de la Junta, sin empalmar, y ninguno se llama M2

**Estado: supuesto.** Decisión del dueño del 2026-10-05.

1892-06 a 1946-12 en fechas de balance (anual hasta 1922, semestral desde
1923), 1947-01 a 1958-12 mensual, y el M2 del H.6 desde 1959-01. Los tres van
como series separadas, con los dos quiebres a la vista. El concepto de los dos
primeros es "efectivo y depósitos en bancos comerciales", el que Friedman y
Schwartz llamaron M2; en la superposición de 1959-01 a 1969-09 el M2 del H.6
es entre 38 % y 49 % más grande (`FUENTES.md`, D0.3.5). **Los dos tramos
históricos se transcribieron y se publicaron el 2026-10-07** (A-D0-31 a
A-D0-33; `FUENTES.md`, D0.3.6). La superposición 1959-01 a 1969-09 de la
Tabla 1.1 sigue sin transcribir.

## A-D0-18 · Las fechas de balance de 1892 a 1946 son datos estimados en parte por la Junta

**Estado: dato, con esa reserva.**

La propia Junta lo declara: cifras reportadas para los bancos miembros y
estimadas para los no miembros. Se publican como "dato de fecha de balance,
estimado en parte", sin interpolar entre fechas.

## A-D0-19 · Las tablas de la Junta anteriores a 1959 se transcriben dos veces, de forma independiente, con página de origen por cifra y control de sumas

**Estado: supuesto.** Decisión del dueño del 2026-10-05.

Protocolo: dos transcripciones independientes comparadas valor por valor; cada
cifra lleva la página del escaneo de la que sale; cada fila tiene que cumplir
que los subtotales sumen el total publicado; una discrepancia se lista y se
resuelve releyendo la imagen, nunca eligiendo una de las dos.

**Ejecutado el 2026-10-07** (`FUENTES.md`, D0.3.6): 2.082 celdas leídas dos
veces, una discrepancia (1955-11 de la Tabla 1.1 B), resuelta releyendo la
celda a 900 ppp y registrada en
`data/raw/transcripcion_junta_1892_1958/resoluciones.csv`; las dos lecturas
viajan con el repositorio y `dinero_historico.py` las coteja en cada corrida:
una celda distinta sin resolución detiene la corrida. Las sumas cuadran en
las 81 filas de la Tabla 9 y su continuación; en la Tabla 1.1 hay dos erratas
de la fuente (A-D0-33).

## A-D0-20 · La serie mensual del NBER (1907–1946) no se usa por ahora

**Estado: supuesto.** Decisión del dueño del 2026-10-05.

Es una estimación de Friedman y Schwartz con componentes interpolados, y el
NBER no declara licencia. Si se pidiera y se obtuviera permiso, sería una
cuarta serie, también sin empalmar, con estado "estimación".

## A-D0-21 · Oro / M2 y BTC / M2 usan el M2 ajustado de EE.UU., en billones de USD

**Estado: supuesto.** Decisión del dueño del 2026-10-05.

`ratios.py` calcula los dos pares con la misma lógica de publicación que los
cinco de la fase R (A-R0-14, A-R0-17, A-R0-20). El M2 entra como `M2.M` en
billones (10¹²) de USD: la unidad del ratio es USD por onza troy (o por BTC)
por cada billón de USD de M2. El medio paso de redondeo del M2 es 0.05 miles
de millones, y entra al error del ratio (A-R0-17). Oro / M2 va desde 1960-01 y
es apto para métricas desde 1968-04, por el oro; BTC / M2 desde 2013-01
(A-R0-10). `python -m senales.ratios --solo-denominador` los recalcula desde
las salidas publicadas, sin descargar nada.

## A-D0-22 · Bonos: la suma de las economías que declaran al BIS, con panel fijo y valuación mixta

**Estado: supuesto; NO MEDIDO en esta entrega.**

Si se implementa, la serie es la suma de los títulos de deuda de las 49
economías con total en las estadísticas del BIS, trimestral, desde 2020-Q4,
rotulada "suma de 49 economías declarantes al BIS" y nunca "global", con la
valuación mixta declarada. Pendiente de implementar; sin fuente de contraste
abierta (SIFMA y la WFE son de clase (c)).

## A-D0-23 · Acciones: el agregado `WLD` del Banco Mundial es la suma de los países con dato

**Estado: dato la subcobertura; NO MEDIDO en esta entrega.**

El agregado queda entre 7 % y 13 % por debajo de la WFE en 2024 y 2025 porque
faltan plazas grandes (`FUENTES.md`, D0.9). Si se publica, lleva esa
advertencia. Pendiente de implementar; las segundas fuentes leídas (WFE,
SIFMA) son de clase (c).

## A-D0-24 · Inmuebles, cantidad de oro y riqueza total: NO MEDIDO

**Estado: no medido.**

No hay una serie global con licencia abierta para ninguna de las tres. La
capitalización de BTC (Coin Metrics, A-R0-4) queda también pendiente de
implementar en esta entrega.

## A-D0-25 · Las tolerancias de los gates salen de la precisión publicada; los tipos de cambio se comparan con un control

**Estado: supuesto.** Fijado antes de correr el pipeline, el 2026-10-06.

| Serie | Segunda fuente | Clase | Tolerancia |
| --- | --- | --- | --- |
| M2 de EE.UU. (las dos) | Tabla 1 del H.6 en HTML, 17 meses | gate | ±0.05 miles de millones (un decimal) |
| Balance de la Fed | BIS `WS_CBTA`, último miércoles del mes | gate | ±5 millones (dos decimales en miles de millones) |
| Balance de la Fed | FRED `WALCL`, semana a semana | control | ±0.5 millones |
| M2 de la Eurozona (las dos) | Banco de España, últimos 3 meses | gate | ±0.5 millones (enteros) |
| Balance del Eurosistema | BIS `WS_CBTA`, regla de semana del BIS | gate | ±0.5 millones (tres decimales) |
| M2 de Japón | e-Stat Dashboard | gate | ±0.5 (mismo entero) |
| Balance del BoJ | BIS `WS_CBTA` | gate | ±0.5 en cien millones de yenes (un decimal) |
| Dinero amplio de China | dos lecturas a mano de la NBS | gate | ±50 millones de yuanes (redondeo de la OCDE) |
| Balance del PBoC | lecturas a mano del PBoC | gate | sin anclas: NO MEDIDO |
| Tipos de cambio (los tres) | BIS `WS_XRU`, promedio mensual | control | ±0.5 % |

Un gate necesita al menos tres comparaciones, también el de anclas. Un gate
que no cierra deja la serie como "NO MEDIDO: sin validación externa"; un
control marca el mes como valor en disputa y no decide.

**El mínimo de anclas se corrigió el 2026-10-06, y hay que decirlo entero.** La
primera versión del código fijó `MINIMO_ANCLAS = 2`, y lo fijó después de saber
que China tenía exactamente dos lecturas de la NBS: no fue una tolerancia
declarada antes de ver el resultado. La revisión del PR lo detectó. Quedó en
tres, el mismo mínimo que el gate anual de oro y plata (A-R0-16), y con eso el
dinero amplio de China pasa a NO MEDIDO hasta que haya una tercera lectura.

**El gate del balance de la Fed también cambió de forma, y tampoco se fijó a
ciegas.** `FUENTES.md` D0.11 (paso 0) proponía como gate la última semana de la
publicación H.4.1 en HTML y como control el BIS, y anotaba que el BIS no cerraba
en 118 meses. Ese resultado era contra la serie bruta (`RESPPA_N.WW`). Al
elegir la serie consolidada (A-D0-15) la diferencia desapareció, y el gate se
definió como "BIS, último miércoles del mes, ±5 millones" sabiendo que
cerraba: la comparación ya estaba hecha. Lo que sí es independiente del
resultado es la tolerancia, que es el redondeo con que publica el BIS. El
gate del HTML del H.4.1 no se implementó: el BIS es un compilador distinto de
la Junta y cubre 284 meses, mientras que la tabla en HTML es del mismo emisor
y cubre una semana. FRED quedó como control semanal por decisión del dueño
(D0.10.11, punto 6). Si se prefiere la forma de D0.11, es un cambio de
supuesto, no de código: ambas comparaciones están hechas. **La comparación de los tipos
de cambio es un control, como quedó en `FUENTES.md` D0.11:** dos fijaciones a
horas distintas no son el mismo dato. En la primera corrida, el único mes
fuera del umbral es 2008-12 del USD por EUR (0.68 %), que se publica marcado.
La primera versión del código lo tenía como gate y lo habría dejado NO MEDIDO
por ese mes; se corrigió a lo aprobado, no la tolerancia.

**Lo que no prueban.** Un agregado monetario tiene un solo compilador; los
gates validan que el dato publicado sea el del emisor, sin errores de
transporte, unidad ni fecha, no la medición.

## A-D0-30 · Una salida derivada se calcula desde lo publicado, y un test lo comprueba

**Estado: supuesto.** Fijado el 2026-10-06, en la revisión del PR #4.

El agregado en USD se calcula desde los valores de dinero y de tipo de cambio
tal como quedan en sus CSV (doce cifras significativas), y los pares contra M2
desde los precios tal como quedan en `precios_mensuales.csv` (diez), no desde
los decimales que los archivos no llevan. Así `tests/test_salidas_publicadas.py`
recalcula cada salida derivada desde los archivos del repositorio y exige que
sea idéntica byte a byte: `liquidez_neta.csv` desde sus tres crudos de FRED,
`denominador_agregado.csv`, `denominador_ratios.csv` y `denominador_pares.csv`
desde los CSV publicados, y los crudos versionados contra el hash de su
manifiesto. Para `ratios.csv` de la fase R la igualdad es exacta salvo en la
décima cifra del valor, porque esa fase todavía divide los precios sin
redondear; llevarla a esta regla exige una corrida completa y va en un PR
propio. Lo que no se puede recalcular sin red ni sin crudos privados
(`precios_mensuales.csv`, `denominador_dinero.csv`, los balances, los tipos de
cambio y la ficha) queda dicho en el docstring del test.

**Por qué existe.** La primera corrida del PR #4 publicó `denominador_pares.csv`
y `denominador_ratios.csv` calculados con datos de prueba: `ratios.py` escribía
esos dos archivos en `data/series/` aunque los tests redirigieran las demás
salidas a un directorio temporal, y la suite los pisó después de la corrida
real. Se arregló en dos lugares: las salidas de D0 de `ratios.py` siguen al
directorio de salida de los ratios, y un fixture de `conftest.py` hace fallar
a cualquier test que escriba en `data/`.

## A-D0-26 · Un cambio en un mes ya publicado es una revisión y se reporta

**Estado: supuesto.**

El umbral es 0.0005 en la unidad de cada serie: cualquier cambio en la
precisión publicada cuenta. El changelog lista hasta 40 revisiones una por una
y las resume por serie si hay más. Las series del BCE y del BoJ se revisan
hacia atrás (`FUENTES.md`, D0.4 y D0.5) y las series del BIS llegan con rezago.

## A-D0-27 · Un crudo de D0 se versiona si su licencia lo permite, pesa hasta 1 MB y alimenta una serie

**Estado: supuesto.**

A-R0-15 pone la condición de licencia; esta agrega dos. Los ZIP de la Junta
(entre 1.4 y 9 MB) y las fuentes que solo se leen para comparar quedan fuera
del repositorio, con su URL, fecha y SHA-256 en `denominador_descargas.csv`.
Los CSV del BCE, del BoJ, de la OCDE y del BIS (China) se versionan en
`data/raw/`, con su atribución en `data/raw/ATRIBUCION.md`.

**Los bytes de un crudo son los de la fuente, sin conversión** (decisión del
dueño del 2026-10-07). Todo `data/raw/` lleva `-text` en `.gitattributes`:
git no normaliza saltos de línea al commitear ni al extraer, en ningún
sistema, y el SHA-256 del manifiesto es el de esos bytes. Los cuatro crudos
del 2026-10-05 que la fuente entregó con CRLF (los tres del BCE y el de la
OCDE) se volvieron a guardar así; ningún hash cambió (changelog, "Cambios de
supuestos").
## A-D0-28 · Las cifras puntuales de terceros van como "estimación de terceros", citadas y fuera de todo cálculo

**Estado: supuesto.** Decisión del dueño del 2026-10-05.

Savills (valor de los inmuebles) y el World Gold Council (oro sobre la
superficie) publican estimaciones puntuales, no series, bajo términos de clase
(c). Se citan en `data/series/citas_terceros.csv` con año, fuente, URL,
sección y fecha de lectura, con el estado "estimación de terceros". No entran
al pipeline ni a ningún cálculo, y no se interpolan. McKinsey queda excluido:
sus términos prohíben extraer datos de su sitio.

## A-D0-29 · El robots.txt se lee antes de cada descarga; el BCE entra por copia bajada a mano

**Estado: supuesto.** Regla de `CLAUDE.md` del 2026-10-05, decisión del dueño
del 2026-10-06 para el BCE.

`fuentes_denominador.descargar` lee el `robots.txt` del host antes de pedir un
crudo que no está en disco, con el nombre con que `requests` se presenta. Si
lo veda, no pide, y la serie queda "NO MEDIDO: el robots.txt de la fuente veda
la descarga y no hay copia a mano". El `robots.txt` de `data-api.ecb.europa.eu`
veda a `python-requests` (y a los agentes de Anthropic), aunque la ayuda de la
API del BCE dé ejemplos con ese cliente. **El pipeline no cambia su
User-Agent.** Las tres series del BCE entran por copia a mano: una persona
abre la URL de la API en el navegador, guarda la respuesta como
`data/raw/<clave>_<AAAA-MM-DD>.csv` (`bce_m2_ajustada`, `bce_m2_sin_ajustar`,
`bce_balance_eurosistema`) y el pipeline usa la copia más reciente, verifica su
hash contra el manifiesto, y si falta o no coincide deja la serie NO MEDIDO en
esa corrida. Las copias del 2026-10-05 son las que se bajaron en el paso 0,
antes de leer ese `robots.txt`.

## A-D0-31 · El dinero de EE.UU. antes de 1959 se publica en dos series transcritas; la sin ajustar queda NO MEDIDO

**Estado: supuesto.** Ejecución del 2026-10-07 de lo decidido en A-D0-17 y A-D0-19.

Lo que `dinero_historico.py` publica en `data/series/dinero_eeuu_historico.csv`:

| Serie | Qué es | Unidad y convención | Observaciones | Estado |
| --- | --- | --- | --- | --- |
| `dinero_eeuu_1892_1946` | Efectivo fuera de bancos + depósitos a la vista ajustados + depósitos a plazo en bancos comerciales, Tabla 9 de *Banking and Monetary Statistics 1914–1941* (1892-06-30 a 1941-12-31) y su continuación en el volumen 1941–1970 (1942-06-30 a 1946-12-31) | millones de USD; saldo del día de balance; anual hasta 1922, semestral desde 1923 | 79 fechas de balance | dato de fecha de balance, estimado en parte (A-D0-18) |
| `dinero_eeuu_1947_1958` | Money stock (efectivo + depósitos a la vista ajustados) + depósitos a plazo ajustados en bancos comerciales, Tabla 1.1 A del volumen 1941–1970 | miles de millones de USD; promedio mensual de cifras diarias; ajustada por estacionalidad | 144 meses | dato |
| `dinero_eeuu_1947_1958_sin_ajustar` | La misma suma, Tabla 1.1 B, sin ajustar | miles de millones de USD; promedio mensual de cifras diarias | 144 meses, transcritos y no publicados | **NO MEDIDO: sin validación externa** |

- Cada valor publicado lleva su componente, su cita (publicación, tabla y
  página) y, si corresponde, la nota al pie de la Junta. Los componentes se
  publican junto al total para que cualquiera rehaga la suma.
- Las dos lecturas independientes viajan con el repositorio en
  `data/raw/transcripcion_junta_1892_1958/`, con `resoluciones.csv` y las
  notas al pie literales. La serie publicada se recalcula desde ellas en
  `tests/test_salidas_publicadas.py` (A-D0-30).
- La serie sin ajustar no tiene segunda fuente accesible a un programa: la
  versión sin ajustar del NBER (`m14144b`, desde 1955-01) no está en FRED y
  `data.nber.org` veda a todo programa en su `robots.txt` (A-D0-29). Queda
  en la ficha como NO MEDIDO hasta que una persona la lea en un navegador o
  aparezca otra publicación de la Junta; la transcripción ya está hecha y
  controlada por sus sumas.
- Las fichas de las tres series en `serie_D0.csv` las escribe
  `dinero_historico.py`; `denominador.py` las conserva en cada corrida. La
  columna `meses` de la ficha cuenta observaciones, y 79 fechas de balance no
  son meses.
- Ninguna de las tres se empalma con el M2 del H.6 ni entre sí (A-D0-17). La
  superposición 1959-01 a 1969-09 de la Tabla 1.1, que D0.10.6 proponía
  publicar para dejar a la vista la diferencia de definición, no se
  transcribió: queda abierta.

## A-D0-32 · Los gates del tramo histórico: sumas, el Censo y el NBER, con tolerancias fijadas antes de comparar

**Estado: supuesto.** Tolerancias fijadas el 2026-10-07 antes de correr los gates, con una salvedad que se dice abajo.

| Control | Clase | Tolerancia | Por qué esa | Resultado |
| --- | --- | --- | --- | --- |
| Las dos lecturas, celda por celda (A-D0-19) | gate | igualdad; una celda distinta solo pasa con una fila en `resoluciones.csv` que diga los dos valores y cómo se releyó | es el protocolo | 2.082 celdas, 1 resuelta |
| Tabla 9 y continuación: cada total impreso contra la suma de sus componentes impresos; las dos filas de 1941 contra la Tabla 9 | gate | igualdad en millones | la Junta imprime millones enteros y sus totales son sumas | cuadran las 81 filas |
| Tabla 1.1 A y B: money stock contra efectivo + vista | control | ±0.1 miles de millones | dos componentes redondeados a un decimal | 143 de 144 en cada una; el mes que no cuadra se publica en disputa (A-D0-33) |
| Fechas de balance contra *Historical Statistics of the United States* (Censo, 1960), serie X 266-274, nueve filas de junio leídas a mano | gate | igualdad en millones; mínimo tres fechas | es la misma cifra reimpresa por otra agencia; la propia nota del Censo lo dice | 9 fechas, 61 cifras, todas iguales |
| Tramo mensual ajustado contra NBER `m14144c` vía FRED (`M1444CUSM027SNBR`), mes a mes | gate | ±0.1 miles de millones; mínimo tres meses | la documentación del NBER declara diferencias de una décima por redondeo (`FUENTES.md`, D0.3.3); ya era la tolerancia propuesta en D0.11 | 144 meses, diferencia máxima 0.1, mediana 0.00 |

- **La salvedad.** Antes de comparar quedó escrito que la serie del NBER es
  anterior a la revisión de 1976 de la Tabla 1.1 y que una diferencia mayor
  podía ser una revisión de la Junta y no un error de transcripción; en ese
  caso la serie quedaba NO MEDIDO y la causa se investigaba, sin tocar la
  tolerancia. No hizo falta. Y los cuatro primeros meses de `m14144c` se
  vieron en el extracto de la descarga antes de correr el gate; no cambiaron
  nada de lo declarado.
- Las anclas del Censo se leyeron en el escaneo ampliado a 600 ppp; en esa
  tipografía el 3 y el 8 se confunden, y cada fila se comprobó con las
  identidades del propio Censo antes de anotarla, sin mirar la Tabla 9.
- Un gate que no cierra deja la serie como "NO MEDIDO: sin validación
  externa" y no detiene la corrida; una lectura que no coincide o una
  identidad de la Tabla 9 que no cuadra detienen la corrida sin escribir nada
  (código de salida 2), porque entonces la transcripción no sirve.

## A-D0-33 · Una errata de la fuente se publica tal como está impresa y se marca como valor en disputa

**Estado: supuesto.** Decisión del 2026-10-07.

La Tabla 1.1 trae dos filas cuyo money stock impreso no es la suma de sus
componentes impresos: **1949-03** de la parte A (efectivo 27.7 entre meses de
25.7; 27.7 + 85.6 = 113.3 contra 111.2) y **1950-12** de la parte B (total
119.2 contra 25.4 + 93.4 = 118.8). Las dos lecturas y el zoom confirman que
así está impreso. No se sabe qué cifra es la errada, así que no se corrige
ninguna: la fila se publica con sus cinco valores tal cual y con la columna
`control` en "valor en disputa", con la cuenta a la vista. Un mes en disputa
no entra a ninguna métrica, igual que los del control contra el FMI en la
fase R (A-R0-20). La suma publicada (money stock + plazo) usa el money stock
impreso, no la suma de componentes.

## A-D0-34 · Las series antiguas de Japón (M2+CDs) se publican aparte, en sus dos tramos, sin empalme y sin llamarse M2

**Estado: supuesto.** Decisión del dueño del 2026-10-07 (`FUENTES.md`, D0.5.1).

| Serie | Código del BoJ | Rango | Qué cambia respecto del siguiente tramo |
| --- | --- | --- | --- |
| `m2cd_japon_1967_1999` | `MAMS1ANM2C` | 1967-01 a 1999-03 | sin los bancos extranjeros en Japón, los fideicomisos extranjeros ni Shinkin Central Bank; en los 12 meses comunes el tramo siguiente queda 0.41 % a 0.48 % por encima |
| `m2cd_japon_1998_2008` | `MAMS3ANM2C` | 1998-04 a 2008-04 | el M2 actual (`m2_japon`) cambia los tenedores (salen sociedades de valores, tanshi y no residentes) y saca los depósitos en yenes de no residentes; en los 61 meses comunes queda 0.42 % a 0.59 % por debajo |

- Nombre: "M2+CDs de Japón (Money Supply, …)", con el rótulo japonés
  マネーサプライ en `FUENTES.md`; nunca "M2" a secas. Estado **dato**: son cifras
  publicadas por el emisor, hoy congeladas (última actualización 2017-12-29).
  Promedio de saldos del mes, sin ajustar, 100 millones de yenes (A-D0-1).
- Quiebres en la ficha: 1979-05 (nacen los CD y el agregado pasa a llamarse
  M2+CDs, sin cambio de perímetro: es un cambio de nombre, no de la serie),
  1998-04 (perímetro: cambio de tramo) y 2003-04 (empieza el M2 actual).
- La superposición se mide en cada corrida y se publica en la validación de la
  ficha (meses comunes, mínimo, máximo y media de la diferencia); no se corrige.
- Ninguna descarga nueva: `DESCARGA_BOJ_M2` ya pide los cuatro códigos de
  M2+CDs. Misma licencia (b), mismo crédito de la API y mismo aviso pendiente
  al BoJ (A-D0-8, D0.13).
- Las versiones de fin de mes (`MAMS1ENM2C`, desde 1955-01) no se publican:
  otra convención, y el agregado usa promedios.

## A-D0-35 · El gate de las series antiguas de Japón es la copia del FMI en FRED, en el tramo que esa copia sigue, con igualdad del entero

**Estado: supuesto.** Tolerancia fijada el 2026-10-07; el resultado se conocía al fijarla, y se dice.

- Segunda fuente: FRED `MYAGM2JPM189N` ("M2 for Japan", FMI, *International
  Financial Statistics*, 1967-01 a 2017-02, en yenes). Otro compilador que
  republica el dato del BoJ, como e-Stat para el M2 actual. e-Stat no tiene
  M2+CDs.
- Tolerancia: **±0.5 en 100 millones de yenes**, la resolución con que FRED
  publica (múltiplos de 10⁸ yenes): es exigir el mismo entero. Mínimo tres
  meses (A-D0-25).
- Rangos: FRED sigue al tramo sin bancos extranjeros **hasta 1998-03**, al
  tramo con bancos extranjeros **de 1998-04 a 2003-03**, y al M2 actual desde
  2003-04. Cada serie se compara solo en su rango; fuera de él no hay
  contraste (los 12 meses de 1998-04 a 1999-03 de `m2cd_japon_1967_1999` y los
  61 de 2003-04 a 2008-04 de `m2cd_japon_1998_2008` quedan sin comparar, y lo
  dice la ficha). El rango es una observación del paso 0 (`FUENTES.md`,
  D0.5.1), no una elección para que cuadre.
- **El resultado ya se conocía:** el paso 0 midió 435 de 435 meses iguales.
  La tolerancia no sale de ahí (es la resolución de FRED), pero la
  comparación no es a ciegas, como A-D0-25 lo dice del balance de la Fed.
- El crudo de FRED lleva derechos del FMI ("reprinted with permission") y los
  términos del FMI no se leyeron: va a `data/privado/`, con URL, fecha y
  SHA-256 en el manifiesto, como los demás contrastes (A-D0-27).

## A-D0-36 · El agregado en USD empieza en 1999-01: Japón entra con M2+CDs hasta 2003-03 y con el M2 actual desde 2003-04, con el quiebre declarado

**Estado: supuesto.** Decisión del dueño del 2026-10-07.

- El primer mes es el del tipo de cambio del euro en el H.10 (1999-01). **No
  se construye ningún euro sintético** anterior a esa fecha; la historia de la
  Eurozona desde 1980 y la de Japón desde 1967 quedan como series, no como
  agregado.
- Japón entra por tramos (`TRAMOS_AGREGADO`): `m2cd_japon_1998_2008` hasta
  2003-03 y `m2_japon` desde 2003-04, cada uno tal cual, sin factor. La
  columna `serie_japon` dice qué serie entró cada mes, y la columna `quiebre`
  lleva en 2003-04 el salto medido en ese mes: cuánto es el M2 nuevo respecto
  de M2+CDs en porcentaje y en miles de millones de USD del agregado. Se
  publica y no se corrige, como las ampliaciones de la Eurozona (A-D0-4).
- El nombre del agregado deja de decir "M2 de tres economías": "Dinero amplio
  de tres economías en USD: M2 de EE.UU. y de la Eurozona, y de Japón M2+CDs
  hasta 2003-03 y M2 desde 2003-04".
- El mes de referencia del tipo de cambio constante pasa de 2003-04 a 1999-01
  (A-D0-11): toda esa columna cambia de nivel.
- El tramo `m2cd_japon_1967_1999` no entra al agregado mientras el euro no
  tenga tipo de cambio anterior a 1999.

## Fase N0 · El Numerador: los supuestos A-N0-\*

Las decisiones de la familia N0, las series anuales de oferta de activos que
alimentan elnumerador.com. Salen del paso 0 (`FUENTES.md`, sección N0) y de lo
que decidió el dueño el 2026-10-07 (`FUENTES.md`, N0.10.5). El código es
`senales/numerador.py`; las fuentes, `senales/fuentes_numerador.py`; la
configuración, el bloque N0 de `configuracion.py`.

## A-N0-1 · Tasa de crecimiento y elasticidad son magnitudes distintas; cada serie declara qué mide

**Estado: supuesto.** Decisión del dueño del 2026-10-07.

La tasa de crecimiento de la oferta es cuánto crece el stock por año: un
cociente entre lo que se agregó y lo que había, y un dato cuando los dos están
medidos. La elasticidad es cuánto responde la oferta a un cambio del precio:
una pendiente estimada, con rezago y con intervalo, nunca un número único.
El sitio hoy usa una por la otra ("Cada activo tiene una tasa a la que se crean
nuevas unidades — su elasticidad de oferta", `FUENTES.md` N0.0, fila 11).

Cada fila de `serie_N0.csv` lleva la columna `mide` con uno de: flujo, stock,
tasa de crecimiento de la oferta, cota superior de la tasa de crecimiento del
stock, proporción, elasticidad de la oferta. El sitio no llama "elasticidad" a
una tasa ni "tasa" a una elasticidad.

## A-N0-2 · BTC: el calendario del protocolo es el dato; la oferta observada de Coin Metrics es el gate

**Estado: dato el calendario y los bloques; supuesto el gate y su tolerancia.**
Decisión del dueño del 2026-10-07.

- **El subsidio por bloque** sale de Bitcoin Core (`GetBlockSubsidy`: 50 BTC,
  partidos en dos cada 210000 bloques; `MAX_MONEY` = 21 millones), leído en el
  commit `9dfde64cc3262329051fd05fffe40eecc786a99f` del 2026-10-07 (`FUENTES.md`,
  N0.3.1). Es una función de la altura del bloque y de nada más.
- **Cuántos bloques caen en cada año** es un dato observado: `BlkCnt` de Coin
  Metrics, sumado por año calendario en UTC. La emisión del año según el
  calendario es la suma del subsidio de cada bloque minado ese año.
- **`BlkCnt` acumulado es la altura del último bloque del día**, es decir, no
  cuenta al bloque génesis, cuyos 50 BTC no están en el conjunto de salidas no
  gastadas. Es una inferencia: con la otra convención la oferta observada de
  2012-11-28 superaría al calendario, y eso es imposible (`FUENTES.md`,
  N0.3.2).
- **El gate**, por año completo: la emisión observada (`IssTotNtv`) no supera
  la del calendario; la oferta al 31 de diciembre (`SplyCur`) no supera la
  suma de subsidios de los bloques 1 a N; y lo que le falta a la oferta
  respecto del calendario no pasa de **0.001 %**. Mínimo tres años. **La
  tolerancia se fijó con el resultado del paso 0 a la vista:** la diferencia
  era de −80 BTC (−0.0004 %) al 2026-10-06. Lo que no depende del resultado es
  el signo, que es lo que el gate exige primero.
- Se publica también el porcentaje minado (oferta sobre 21 millones) a fin de
  cada año y a la fecha de la descarga, con su fecha.
- **La elasticidad de BTC es cero por construcción** y se publica como dato
  (A-N0-12). La tasa de crecimiento observada (0.838 % en 2025) reemplaza al
  "0 %" del sitio.
- blockchain.com no entró como control: su cifra no es comparable sin alinear
  la altura (`FUENTES.md`, N0.3.3). Queda abierto.

## A-N0-3 · Oro y plata: la producción minera mundial del USGS, con la Data Series 140 en todo su rango y los Mineral Commodity Summaries después

**Estado: dato; supuesto la regla de empalme entre publicaciones.** Decisión
del dueño del 2026-10-07.

- La *Data Series 140* (oro 1900–2022, plata 1900–2021) se usa en todo su
  rango. Para los años posteriores, cada año toma la cifra de la edición más
  reciente de los *Mineral Commodity Summaries* que lo publica como final; si
  solo hay estimaciones, la más reciente, con estado "estimación" (hoy, 2025).
- Las cifras de los *Summaries* se transcriben a mano en `configuracion.py`
  (`LECTURAS_MCS`), con la edición, la URL, el SHA-256 y el tamaño del PDF y
  la frase del texto que las confirma. Los PDF se leyeron con `pdftotext` en
  modo `-raw` (el modo `-layout` mezcla columnas) y la fila "World total
  (rounded)" se cotejó con la frase del texto corrido.
- **Las revisiones se declaran y no se corrigen.** Oro 2022: la DS140 publica
  3160 t y el MCS 2024 publica 3060; se publica la DS140, con la nota. Oro
  2023: 3000 estimado (MCS 2024) y 3250 final (MCS 2025). Oro 2024: 3300
  estimado (MCS 2025) y 3280 final (MCS 2026). Plata 2023: 26000 estimado y
  25500 final. Plata 2024: 25000 estimado y 25300 final. Cada fila publicada
  lleva la nota "revisión declarada" cuando otra edición dijo otra cosa.
- El USGS cita el *World Silver Survey* (Silver Institute, Metals Focus) en
  una nota del capítulo de plata: las dos fuentes no son del todo
  independientes.

## A-N0-4 · El BGS es control de consistencia de la producción, con ±5 %, y la plata queda en disputa

**Estado: supuesto.** Decisión del dueño del 2026-10-07; tolerancia fijada el
2026-10-07 antes de correr el pipeline.

- El total mundial de *World Mineral Production 2020–24* del British
  Geological Survey (kilogramos de contenido de metal, 2020 a 2024) se compara
  con la producción del USGS año a año. Es un **control**: marca el año como
  "valor en disputa" y no decide la publicación. Mínimo tres comparaciones.
- **La tolerancia, ±5 %, se fijó antes de correr y con los resultados del
  paso 0 a la vista:** oro entre 0.6 % y 4.4 % en 2021–2024 (y 4.9 % en 2020,
  que se vio en la corrida), plata entre 7.6 % y 9.9 %. Se sabía que la plata
  iba a quedar en disputa: 2020, 2021, 2022 y 2024 (2023 queda a 4.9 %). No se
  ajustó la tolerancia para que cerrara.
- **Por qué difieren.** El BGS suma estimaciones de minería artesanal que el
  USGS no declara, y en plata incluye producción de fundición o refinería en
  algunos países. La ficha de las dos series lo dice; "valor en disputa" aquí
  significa que los dos compiladores no miden lo mismo, no un error de
  transporte.
- Las diez cifras del BGS se transcriben en `configuracion.py` (`LECTURAS_BGS`)
  con la URL y el SHA-256 del PDF. Sus términos permiten el uso académico y de
  investigación no comercial y exigen el reconocimiento *"World Mineral
  Statistics contributed by permission of the British Geological Survey"*, que
  el changelog y la ficha llevan; publicar la serie del BGS en el sitio puede
  leerse como entregarla a terceros, y por eso es contraste y no fuente
  (`FUENTES.md`, N0.4.3 y N0.13). El PDF no se versiona.

## A-N0-5 · La cota superior de la tasa de crecimiento del stock de oro y plata: producción del año sobre la acumulada desde 1900

**Estado: estimación.** Decisión del dueño del 2026-10-07.

- `producción_t / Σ_{1900}^{t−1} producción`, en %, desde 1901, sobre la serie
  de A-N0-3. Estado "estimación" en todas las filas.
- **Es una cota superior, no la tasa real,** porque el denominador excluye
  todo lo producido antes de 1900 (el stock real es mayor) y supone que las
  pérdidas son despreciables. Para el oro los dos supuestos van en la misma
  dirección y la cota vale. **Para la plata no es una cota:** el consumo
  industrial no recuperado reduce el stock real, en la dirección contraria, y
  la cifra es solo indicativa. La ficha y la nota de cada fila lo dicen.
- Nunca se presenta como la tasa real ni entra a ninguna métrica.

## A-N0-6 · Las existencias de oro y plata y el stock-to-flow quedan NO MEDIDO como serie

**Estado: no medido.** Decisión del dueño del 2026-10-07.

No hay ninguna serie abierta de existencias sobre la superficie: el World Gold
Council exige cuenta y sus términos son de uso personal (`FUENTES.md`, N0.4.4);
de plata no se encontró ninguna (N0.5.5). La cifra del World Gold Council
(222600 t a fin del segundo trimestre de 2026) sigue en
`data/series/citas_terceros.csv` como estimación de terceros, fuera de todo
cálculo (A-D0-28). Sin existencias no hay stock-to-flow: no se publica, ni se
proyecta.

## A-N0-7 · Acciones de EE.UU.: la emisión neta del Z.1 por sector, en millones de USD y como porcentaje del valor de mercado del año anterior

**Estado: dato, con limitación declarada; no medido lo global.** Decisión del
dueño del 2026-10-07.

- Fuente: Z.1, tabla F51.1 (la antigua F.224/L.224). Cuatro sectores: todos
  los sectores (`FA893064105`, la línea "Net issues"), sociedades no
  financieras (`FA103164105`), sectores financieros internos (`FA793164105`)
  y resto del mundo (`FA263164105`), con sus saldos a valor de mercado
  (`LM...`).
- **El flujo anual:** hasta 1951 la Junta publica un dato por año (fechado
  :Q4) y se toma tal cual; desde 1952 es la media de los cuatro trimestres a
  tasa anual ajustada por estacionalidad (la suma dividida por cuatro). Solo
  años con los cuatro trimestres.
- **El porcentaje:** la emisión neta del año sobre el saldo a valor de mercado
  del cuarto trimestre del año anterior, del mismo sector. Mezcla cantidades y
  precios y lo declara. Sin interpretar: un valor negativo es más recompras
  que emisiones en ese año.
- **La limitación:** es un flujo en dólares a valor de transacción, no una
  cantidad de acciones; la cantidad no existe en el Z.1.
- Una serie global no tiene fuente abierta (la WFE es (c), D0.9): NO MEDIDO.

## A-N0-8 · Deuda de EE.UU.: los títulos de deuda (F3.s) y la deuda de los sectores no financieros (D3.s), saldo de fin de año y variación

**Estado: dato.** Decisión del dueño del 2026-10-07.

- `FL894122005` (F3.s, línea 1: todos los sectores, títulos de deuda, pasivo),
  saldo del cuarto trimestre, sin ajuste estacional, y su variación anual.
  Incluye los títulos emitidos por el resto del mundo en manos de residentes;
  el BIS queda 6.65 % por debajo en 2025-Q4 porque cuenta solo emisores
  residentes (`FUENTES.md`, N0.7.2). Es una comparación declarada; no se
  implementó como control.
- `LA384104005` (D3.s, línea 1: sectores no financieros internos, títulos y
  préstamos), saldo del cuarto trimestre, ajustado, y su variación.
- La suma de las 49 economías declarantes al BIS es la de A-D0-22, pendiente.

## A-N0-9 · El gate de transporte del Z.1: el CSV del paquete contra la tabla en HTML, ±0.05 miles de millones

**Estado: supuesto.** Tolerancia fijada el 2026-10-07 antes de correr, por
construcción.

- Cada tabla del paquete `z1_csv_files.zip` que alimenta una serie (F51.1.t,
  F51.1.s, F3.s, D3.s) se compara con la misma tabla en HTML del mismo
  emisor, trimestre a trimestre y en las columnas anuales. El HTML publica
  miles de millones con un decimal: la tolerancia es medio paso, 0.05.
  Mínimo tres comparaciones. Un gate que no cierra deja las series de esa
  tabla como "NO MEDIDO: sin validación externa".
- Es un gate de transporte: la Junta es el único compilador y no existe una
  segunda medición (como en D0.11).
- Las tablas de la familia D vienen traspuestas en el HTML (períodos como
  filas) y con los mnemónicos solo en los enlaces de los encabezados; el
  lector los toma del orden de esos enlaces.
- FRED como espejo del Z.1 queda como control pendiente.

## A-N0-10 · Viviendas de EE.UU.: la Tabla 7 del HVS con sus bases revisadas, la Tabla 7a aparte y Population Estimates como contexto

**Estado: dato; supuesto el trato de las bases revisadas.** Decisión del
dueño del 2026-10-07.

- **Tabla 7** (1965 a hoy, promedio de las estimaciones mensuales del año,
  miles): el Censo trae cinco años dos veces, en la base original y en la
  revisada (1979r1, 1981r2, 1989r3, 1993r4, 2002r5). Se publica el valor
  original de cada año, y la base revisada se usa solo como denominador de
  la tasa del año siguiente, que es lo que la hace comparable; la fila lo
  dice. 2025 promedia once meses (el HVS no relevó octubre de 2025) y la fila
  lo dice.
- **Tabla 7a** (2000 a hoy) es el mismo inventario revisado con los controles
  de vivienda de las vintages 2010, 2020 y 2025: se publica aparte, no se
  mezcla con la Tabla 7. Hoy queda NO MEDIDO por A-N0-11.
- **Population Estimates** (viviendas al 1 de julio, 2020 a 2025, unidades):
  otra estimación del Censo, con otra convención; se publica como contexto y
  sirve de control.
- Un parque global no tiene fuente leída (UN-Habitat no se leyó): NO MEDIDO.
  Los nombres dicen "de EE.UU." (A-N0-13).

## A-N0-11 · Los gates y controles de viviendas: la identidad de la tabla como gate; FRED y Population Estimates como controles

**Estado: supuesto.** Tolerancias fijadas el 2026-10-07 antes de correr; la
clase de la comparación con FRED, con el resultado a la vista, y se dice.

| Comparación | Clase | Tolerancia | Cómo se fijó | Resultado del 2026-10-07 |
| --- | --- | --- | --- | --- |
| "All housing units" = "Vacant" + "Total occupied", en cada columna de la tabla | gate de transporte | ±1.5 mil (tres cifras redondeadas a miles) | por construcción | Tabla 7: cerró, 66 columnas, máxima 1.0. **Tabla 7a: no cerró: en 2017 el total (137221) difiere en 2 mil de la suma (17381 + 119842)** |
| Tabla 7a contra la media de los cuatro trimestres de FRED `ETOTALUSQ176N`, hasta 2019 | control | ±1 mil | por construcción la tolerancia; **la clase, con el resultado a la vista**: en 2001–2019 la diferencia llega a 3.75 mil en siete años | siete años en disputa |
| Population Estimates (1 de julio) contra la Tabla 7a (promedio del año) | control | ±0.5 % | **con el resultado a la vista:** −0.07 % en 2025 | cerró, máxima 0.07 % |

- **La Tabla 7a queda NO MEDIDO: sin validación externa.** El archivo del
  Censo no cumple su propia identidad en 2017 por 2 mil, más que el redondeo
  de tres cifras. La tolerancia no se tocó. Si el dueño prefiere que esa
  identidad sea un control (marcar 2017 en disputa y publicar el resto), es un
  cambio de supuesto, no de código.
- **FRED no reproduce la Tabla 7a al redondeo** (hasta 3.75 mil, 0.003 %) y no
  se sabe por qué; por eso es control y no gate. De 2020 en adelante no se
  compara: la Tabla 7a reexpresa esos años con la Vintage 2025 y FRED trae los
  trimestres como se publicaron (diferencias de 5 a 58 mil, vistas en el paso
  0). La diferencia de cada año va a la ficha.
- Population Estimates y el HVS comparten los controles de vivienda: el
  control prueba la consistencia de dos estimaciones del mismo emisor, no una
  medición independiente.

## A-N0-12 · Elasticidad: BTC cero por construcción; deuda NO MEDIDO; oro, plata, viviendas y acciones esperan el prerregistro de la familia "respuesta observada de la oferta al precio"

**Estado: dato (BTC); no medido (deuda); pendiente (los demás).** Decisión del
dueño del 2026-10-07.

- **BTC:** cero por construcción. La emisión depende de la altura del bloque y
  no del precio (A-N0-2). Se publica como dato, con la cita del código.
- **Deuda de EE.UU.:** NO MEDIDO. No tiene un precio comparable.
- **Oro, plata, viviendas de EE.UU. y acciones de EE.UU.:** van en una familia
  nueva, "respuesta observada de la oferta al precio", con estado
  "estimación", que no se calcula en esta entrega. Antes de descargar o cruzar
  precios hay que prerregistrar aquí la especificación completa: variables,
  deflactor, rezagos de 0 a 5 años, ventana, método (por ejemplo, regresión en
  logaritmos con errores robustos), cómo se reportan los intervalos y qué
  resultado se leería como "responde" o "no responde", en un commit propio
  anterior al cálculo. Pares: oro y plata (producción contra precio real),
  viviendas de EE.UU. (construcción contra el índice de precios de la FHFA; el
  Case-Shiller tiene licencia de S&P y queda fuera) y acciones de EE.UU.
  (emisión neta contra valuación). Rótulo fijo: "asociación observada, no
  elasticidad causal: precio y cantidad se determinan juntos". Intervalos, no
  un número único. Las fuentes que N0 no verificó (FHFA, deflactor, valuación)
  pasan primero por un paso 0 corto, con parada para mostrarlo.
- Lo que el sitio llama `elasticity_*` (un cociente de variaciones a diez años
  sobre anclas interpoladas) no se reproduce.

## A-N0-13 · Frecuencia anual, solo años completos, convención por serie y nombres "de EE.UU."

**Estado: supuesto.** Decisión del dueño del 2026-10-07.

- Toda la familia es anual. BTC se suma por año calendario en UTC y el año en
  curso no se publica como anual (solo las dos filas "a la fecha", con su
  fecha); el USGS es anual; el Z.1 se toma a fin de año; el HVS es el promedio
  del año; Population Estimates, el 1 de julio.
- La convención de cada serie va en su ficha (`convencion`) y la tasa de
  crecimiento es siempre el valor del año sobre el del año anterior en la
  misma convención, menos uno.
- Acciones, deuda y viviendas se llaman "de EE.UU." en todas partes; "mundo"
  solo la producción minera del USGS, que así lo declara; ningún nombre dice
  "global".
- Ninguna serie de N0 entra a un ratio contra precio ni contra M2 en esta
  entrega.

## A-N0-14 · Crudos de N0: qué se versiona, qué entra a mano y qué queda fuera

**Estado: supuesto.** Con A-R0-15 y A-D0-27.

- **Se versionan en `data/raw/`:** la descarga de Coin Metrics (CC BY-NC,
  773 KB), los dos xlsx de la *Data Series 140* y los tres del Censo (dominio
  público), y los CSV de las cinco tablas del Z.1 (dominio público) extraídos
  del paquete ZIP con sus bytes exactos; su URL en el manifiesto es la del
  ZIP con el fragmento `#csv/<tabla>.csv`.
- **La *Data Series 140* entra por copia bajada a mano** (como las series del
  BCE, A-D0-29): el host que la aloja (`d9-wret.s3.us-west-2.amazonaws.com`)
  responde HTTP 403 al propio `robots.txt`, y la regla de
  `fuentes_denominador.interpretar_robots` lee un 403 como veda total. Las
  copias del 2026-10-07 se bajaron con `python-requests` en el paso 0, antes
  de aplicar esa lectura; se declara. El pipeline no vuelve a pedirlas.
- **Quedan fuera del repositorio, con su hash en el manifiesto:** el ZIP del
  Z.1 (8.3 MB), el HTML de las cuatro tablas del Z.1 y el CSV de FRED (solo
  contraste), el PDF del BGS (términos restrictivos) y los PDF de los
  *Mineral Commodity Summaries* (leídos a mano; su hash está en
  `configuracion.py`).
- Las URL del Censo llevan la vintage en el nombre (`hist_tab_7a_v2025.xlsx`,
  `NST-EST2025-HU.xlsx`) y cambian cada año: cambiarlas es un cambio de
  configuración que se registra en el changelog.

## A-N0-15 · Un cambio en un año ya publicado es una revisión y se reporta

**Estado: supuesto.**

El umbral es 0.0005 en la unidad de cada serie, por (serie, año); el changelog
lista hasta 40 revisiones y resume el resto. El Z.1 revisa la historia en cada
publicación; el USGS revisa el último año en cada edición; el HVS reexpresa
por vintage.
