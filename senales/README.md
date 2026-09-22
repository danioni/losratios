# señales

Marco de señales para rebalancear un portafolio entre TQQQ, BTC y
stablecoins/USD. Este repositorio construye y actualiza las series que el marco
consume; no toma decisiones de portafolio ni las sugiere.

Hoy hay una capa implementada: **S2.x, contexto de liquidez**.

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

El H.4.1 de la semana del **16 de septiembre de 2026** reporta activos totales
6747, TGA 877 y ON RRP 4 (miles de millones). Entonces:

```
6747 − 877 − 4 = 5866
```

Antes de escribir nada, el script calcula esa fila y la compara con 5866. Si la
diferencia supera **±5**, se detiene: no escribe la serie, ni el gráfico, ni el
changelog. Reporta la diferencia total, el desvío de cada componente por
separado y las tres semanas alrededor del ancla.

Ante una falla, **no se ajusta la fórmula para que cuadre**. Lo que se revisa,
en orden, es: las unidades que declara FRED, la convención de la serie de TGA
(A-S2-4) y el perímetro del ON RRP (A-S2-1).

La unidad de cada serie está atada a su identificador: `WALCL` y `WDTGAL` llegan
en millones, `RRPONTSYD` en miles de millones. Hay tests que fallan si la
declaración de `WDTGAL` deja de decir `millones`, para que cambiar la serie sin
cambiar la unidad no llegue a publicarse (A-S2-4).

> **Estado actual de la validación: no corrida contra FRED en vivo.** El entorno
> donde se escribió este repositorio tiene bloqueado el acceso a
> `fred.stlouisfed.org`. La aritmética está probada contra datos de prueba
> deterministas, pero nadie verificó todavía que las series reales produzcan
> 5866 ese miércoles. Ver **A-S2-13**.

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

## Estructura

```
senales/
├── senales/
│   ├── configuracion.py    Todo lo que decide un número publicado
│   ├── fuentes_fred.py     Descarga, cache y verificación de unidades
│   ├── nucleo.py           Utilidades compartidas entre señales
│   ├── bitacora.py         Changelog y detección de revisiones
│   ├── grafico.py          El PNG de dos paneles
│   └── liquidez_neta.py    S2.x — punto de entrada
├── tests/
├── data/raw/               Descargas crudas, versionadas por fecha
├── data/series/            Series publicadas y su changelog
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

Trece decisiones sostienen estos números, y ninguna es obvia. Están todas en
**[SUPUESTOS.md](SUPUESTOS.md)**, numeradas y con estado (dato / estimación /
supuesto / no medido).

Las tres que más cambian el resultado:

- **A-S2-1** — solo se resta el ON RRP doméstico; el repo pool extranjero queda fuera.
- **A-S2-4** — el TGA se toma como nivel de miércoles (`WDTGAL`), la misma convención que `WALCL` y que el H.4.1.
- **A-S2-3** — no hay umbral de expansión ni de contracción: **NO MEDIDO**.
