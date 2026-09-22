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

## A-S2-4 · WTREGEN es un promedio semanal, no el nivel del miércoles

**Estado: supuesto, con una discrepancia conocida sin resolver.**

La serie de TGA en uso es `WTREGEN`, cuyo título completo en FRED es
*«...U.S. Treasury, General Account: **Week Average**»*. Es el promedio de la
semana. `WALCL`, en cambio, es *Wednesday Level*: el nivel del miércoles.

S2.1 resta entonces un promedio semanal a un nivel puntual. Son dos convenciones
distintas mezcladas en una resta. La diferencia entre el promedio y el nivel del
TGA puede ser de decenas de miles de millones en semanas de vencimientos
impositivos o de subastas grandes — bastante más que la tolerancia de ±5 con la
que se valida S2.1.

**Alternativa.** `WDTGAL`, el TGA como nivel de miércoles en millones de USD, que
es la convención del H.4.1. Está declarada en `configuracion.py` como
`SERIE_TGA_NIVEL_MIERCOLES`; para usarla, apuntar `SERIE_TGA` ahí. Como con
A-S2-1, **ese identificador no pudo verificarse desde este entorno**.

Se dejó `WTREGEN` porque es lo que pide el marco y porque el árbitro está
puesto: si la mezcla de convenciones no entra en ±5, el gate de validación se
detiene y lo dice. No se cambia la fórmula para que cuadre.

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
| `WTREGEN` | Billions of U.S. Dollars | × 1 |
| `RRPONTSYD` | Billions of US Dollars | × 1 |

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

## A-S2-13 · La validación contra FRED en vivo todavía no se corrió

**Estado: no medido.**

El entorno donde se escribió este repositorio tiene bloqueado el acceso a
`fred.stlouisfed.org` por política de egreso. En consecuencia:

- **Sí** está probado, contra datos de prueba deterministas, que la aritmética
  reproduce el ancla del H.4.1 del 16 de septiembre de 2026
  (`6747 − 877 − 4 = 5866`), que el gate corta cuando la diferencia supera ±5, y
  que un error de unidad en el TGA no pasa desapercibido.
- **No** está probado que las series reales de FRED, con sus unidades y su
  calendario reales, produzcan ese número.

Lo segundo se resuelve corriendo `python -m senales.liquidez_neta` desde una
máquina con salida a FRED. Hasta que eso pase, este supuesto sigue en **no
medido** y lo que el script publique no debería usarse para decidir nada.
