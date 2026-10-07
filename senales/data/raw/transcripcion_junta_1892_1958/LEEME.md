# Transcripción de las tablas de la Junta, 1892–1958

Dos lecturas independientes (A y B) de cuatro tablas escaneadas de la Junta de
Gobernadores del Sistema de la Reserva Federal, hechas el 2026-10-07 según el
protocolo de A-D0-19: cada lectura se hizo sin ver la otra, a partir de
recortes distintos del mismo escaneo, y `senales/dinero_historico.py` las
compara celda por celda antes de usarlas. Lo que se leyó de cada tabla y el
resultado del cotejo están en `FUENTES.md`, D0.3.6.

| Archivo | Tabla | Publicación | Página del libro | Página del PDF de FRASER | Filas |
| --- | --- | --- | --- | --- | --- |
| `A_tabla_9.csv`, `B_tabla_9.csv` | No. 9, "Deposits and currency—adjusted deposits of all banks and currency outside banks, 1892–1941" | *Banking and Monetary Statistics, 1914–1941* (1943) | 34–35 | 43–44 | 69 fechas de balance |
| `A_continuacion_tabla_9.csv`, `B_continuacion_tabla_9.csv` | Tabla sin número de la Sección 1 que actualiza la Tabla 9 para 1941–46 | *Banking and Monetary Statistics, 1941–1970* (1976) | 5 | 12 | 12 fechas de balance |
| `A_tabla_1_1_A.csv`, `B_tabla_1_1_A.csv` | 1.1 A, "Money stock and related data, monthly, 1947–70", ajustada por estacionalidad, tramo 1947–58 | *Banking and Monetary Statistics, 1941–1970* (1976) | 17 | 24 | 144 meses |
| `A_tabla_1_1_B.csv`, `B_tabla_1_1_B.csv` | 1.1 B, la misma sin ajustar, tramo 1947–58 | *Banking and Monetary Statistics, 1941–1970* (1976) | 20 | 27 | 144 meses |

- Los PDF no viajan con el repositorio (36 y 75 MB); su URL, fecha y SHA-256
  están en `data/series/dinero_historico_descargas.csv`.
- Los números van tal como están impresos: sin separador de miles, con el
  decimal de la fuente, y una celda en blanco donde la tabla trae guiones.
  Nada se corrigió, ni siquiera cuando una fila no suma (A-D0-33).
- La columna `nota` guarda las marcas de nota al pie (`plazo_comerciales:5`)
  y las observaciones de cada lectura (zoom hecho, dígito tenue). Solo las
  marcas de nota al pie llegan a la serie publicada.
- `resoluciones.csv` lista cada celda en la que A y B difirieron, con los dos
  valores leídos, el valor que quedó y cómo se resolvió releyendo la imagen.
  Una celda distinta sin fila aquí detiene la corrida.
- `notas_tabla_9.txt` y `notas_tabla_1_1.txt` transcriben las notas al pie y
  los encabezados, literales en inglés.

Licencia: publicaciones de una agencia federal de EE.UU. sin aviso de
copyright; que estén en dominio público es una inferencia (`FUENTES.md`,
D0.3.1). La copia digital es de FRASER (Federal Reserve Bank of St. Louis), que
pide atribución; ver `data/raw/ATRIBUCION.md`.
