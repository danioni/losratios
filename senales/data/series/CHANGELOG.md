# Changelog de data/series

Una entrada por corrida, de la más reciente a la más antigua.

Las secciones cuyo título no es una fecha (por ejemplo, los cambios de supuestos)
se escriben a mano, se conservan arriba y el script no las toca.

## Cambios de supuestos

Cada línea registra un cambio que altera lo que la serie mide, no cómo se
calcula. La justificación completa está en `SUPUESTOS.md`, bajo el número que se
cita.

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
