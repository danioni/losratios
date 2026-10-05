# Revisión narrativa: lista de partida

Textos del sitio que afirman o juzgan algo sin citar una fuente. Es la lista
con la que empieza la revisión narrativa, donde cada texto se va a clasificar
como **dato** (con su fuente) o como **tesis del autor** (dicha como tal).

Se armó el 2026-10-05, leyendo `src/` en la rama del PR #3. Las líneas son las
de cada archivo después del commit `19602ba`; si se corren, vale el texto
citado. Nada de esta lista se toca antes de esa revisión, salvo lo que figura
como resuelto en la sección 4.

Los números que el sitio muestra salen de los CSV de `senales/data/series/`.
Al armar la lista no se encontró otra cifra escrita a mano en el texto visible,
fuera de las de la cita de `/fuentes` (sección 4).

## 1. Texto visible en la portada

Pendiente. Archivo: `src/components/Dashboard.tsx`, salvo donde dice otro.

| Línea | Texto | Qué tiene |
| --- | --- | --- |
| 130 | "La única forma de saber si un activo está caro o barato es compararlo con otro activo. No con dinero fiat." | Juicio absoluto. |
| 133 | "tu metro se encoge cada año… Así funciona medir activos en dólares." | Afirma que el dólar pierde valor cada año, sin cifra ni fuente. |
| 157 | "Si BTC/Oro sube, Bitcoin está capturando más valor relativo al oro." | Interpretación. |
| 190–191 | "El denominador se encoge. El numerador protege." | Interpretación. |
| 233 | "¿Cuánto market share le está sacando Bitcoin al oro como reserva de valor? Este es el ratio más importante del sitio. Cuando está bajo históricamente, el mercado duda del argumento del 'digital gold'. Cuando está alto, el argumento está ganando." | Juicios; "bajo" y "alto" sin definir. |
| 241 | "No preguntes si un activo está caro o barato. Pregunta contra qué lo estás midiendo." | Juicio. |
| 252 | "Dentro de los ganadores: ¿hard money o capital productivo?" | "Ganadores" es un juicio. |
| 255 | "cuánto está apostando el mercado a la narrativa de escasez pura (oro y Bitcoin) vs la narrativa de crecimiento productivo (acciones)" | Interpretación. Los dos pares son NO MEDIDO. |
| 268–271 | "Growth vs Quality: el ciclo dentro del ciclo"; "el Nasdaq (growth/tech) vs el S&P 500 (quality/broad market) marca otro ciclo" | Interpretación. El par es NO MEDIDO. |
| 283 | "¿Cuánto paga el mercado por escasez?" | Interpretación. |
| 286 | "Oro/Plata mide el apetito por escasez pura (oro) vs escasez con utilidad industrial (plata)"; "cuanto más inelástica la oferta, más captura el activo del debasement" | Interpretación causal. |
| 324 | "Los precios en fiat son ruido. Los ratios son señal." | Juicio. |
| 334, 340; `Footer.tsx` 7–8 | "por qué el dinero se encoge"; "por qué los activos se multiplican" | Juicios. |

Agregados al guardar la lista, que no estaban en la primera versión:

| Línea | Texto | Qué tiene |
| --- | --- | --- |
| 123–126 | "No hay precios absolutos. Solo ratios mal leídos." | Tesis. |
| 138 | "La respuesta está en los ratios." | Tesis. |

## 2. Texto oculto tras el flag de métricas

Pendiente. No se muestra hoy: aparece si `METRICAS_VERIFICADAS` pasa a `true`.

| Dónde | Texto | Qué tiene |
| --- | --- | --- |
| `src/lib/data.ts` 230 | Las etiquetas "caro" y "barato" de `generateNarrative()` | Juicio. |
| `src/components/Footer.tsx` 89 | "Un z-score extremo indica que el ratio está lejos de su media, no que vaya a revertir en un plazo determinado." | Niega una predicción, pero nombra la reversión. Agregado al guardar la lista. |

## 3. Metadatos

Pendiente.

| Dónde | Texto | Qué tiene |
| --- | --- | --- |
| `src/app/layout.tsx` 14–16 | Palabras clave "liquidez global", "M2" y "stock-to-flow" | Temas que el sitio no muestra. |

## 4. Resuelto antes de la revisión

| Texto | Qué se hizo | Commit |
| --- | --- | --- |
| "Cuando está por encima de 80, la plata históricamente está barata relativa al oro." | Eliminado. El 80 no tenía fuente y "barata" es un juicio. | `efe7b66` |
| "Cuando el Nasdaq está muy caro relativo al S&P, los quality compounders como Visa, Mastercard, Costco y Berkshire están relativamente baratos." | Eliminado. | `19602ba` |
| "No es 'compra BTC' o 'compra acciones'. Es cuánto de cada uno, y cuándo cambia el peso." | Eliminado. | `19602ba` |
| "Documentan desequilibrios históricos que tienden a revertir. Cuándo revierten — eso nadie lo sabe." | Eliminado. | `19602ba` |
| Oculto: "Los desequilibrios tienden a revertir — no predicen cuándo." (`Dashboard.tsx`) | Eliminado, para que no reaparezca al activar las métricas. | `19602ba` |
| Oculto: "Históricamente los extremos tienden a revertir; el momento no es predecible." (`data.ts`) | Eliminado, por lo mismo. | `19602ba` |
| "de uso mayormente industrial" (la plata) | Se queda, con su fuente citada en `/fuentes`. | `19602ba` |

Los textos sobre la reversión se reescriben cuando R1.5 tenga evidencia.

La fuente de "mayormente industrial" es la tabla "Silver Supply and Demand" del
Silver Institute (Source: Metals Focus), leída el 2026-10-05: en 2024, la
demanda industrial fue de 680.5 millones de onzas sobre 1164.1, el 58.5 %. La
lectura completa está en `senales/FUENTES.md`, sección 8.1.

## 5. Parámetros pendientes de supuesto numerado

Se definen en R1.2. Están en `src/lib/data.ts` y no tienen un supuesto numerado
en `senales/SUPUESTOS.md`. Hoy ningún componente los usa, porque las métricas
están ocultas. Antes de publicar una métrica que dependa de ellos, cada uno
necesita su supuesto, con estado y justificación.

| Línea | Parámetro | Valor | Para qué |
| --- | --- | --- | --- |
| 21 | `SMA_LONG` | 200 meses | Ventana de la media y del z-score. |
| 22 | `SMA_SHORT` | 50 meses | Media corta para los cruces. |
| 195 | `Z_EXTENDED` | 1 | Corte de \|z\| entre "Neutral" y "Extendido" o "Comprimido". |
| 196 | `Z_EXTREME` | 2 | Corte de \|z\| para "Extremo". |

El texto oculto del pie (`Footer.tsx` 89) describe esos mismos cortes y tiene
que cambiar con ellos.
