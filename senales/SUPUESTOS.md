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

Lo que **no** está resuelto es cuál de los casos se dio, ni si existe una fuente
de la unidad que funcione sin clave de API. Eso se sabe en la próxima corrida con
acceso, leyendo el motivo. Alternativas a evaluar si `/data/<ID>.txt` no sirve: la
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

## A-S2-13 · La validación contra FRED en vivo: corrida, ancla corregida, reverificación pendiente

**Estado: no medido.** Pasa a **dato** cuando el gate cierre en una corrida real
con el ancla corregido.

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

1. **La corrida de reverificación.** Hasta que `python -m senales.liquidez_neta`
   cierre el gate con el ancla corregido, este supuesto sigue en **no medido** y
   lo que el script publique no debería usarse para decidir nada. Cuando cierre,
   anotar acá la fecha de la corrida y el S2.1 obtenido, y pasar el estado a
   **dato**.
2. **La unidad que declara FRED.** En la corrida del 2026-09-22 las tres series
   salieron NO VERIFICADAS en unidades, con los CSV bajando bien. Ver A-S2-9.
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
