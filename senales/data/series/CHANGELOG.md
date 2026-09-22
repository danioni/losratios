# Changelog de data/series

Una entrada por corrida, de la más reciente a la más antigua.

Las secciones cuyo título no es una fecha (por ejemplo, los cambios de supuestos)
se escriben a mano, se conservan arriba y el script no las toca.

## Cambios de supuestos

Cada línea registra un cambio que altera lo que la serie mide, no cómo se
calcula. La justificación completa está en `SUPUESTOS.md`, bajo el número que se
cita.

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

## 2026-09-22

- Rango de datos: sin datos
- Filas agregadas: 0
- Revisiones de datos históricos: ninguna
- Huecos: ninguno
- Verificación de unidades:
  - no corrida: este repositorio se escribió en un entorno sin acceso a `fred.stlouisfed.org`
- Validación: NO CORRIDA contra FRED en vivo (A-S2-13)
- Umbral de expansión/contracción: NO MEDIDO (A-S2-3)
- Nota: entrada inicial escrita a mano. Todavía no hubo ninguna corrida real del
  script, así que no hay serie publicada en `data/series/liquidez_neta.csv` ni
  gráfico en `reportes/`. La primera corrida con acceso a FRED reemplaza esta
  entrada por la que genera el script.
