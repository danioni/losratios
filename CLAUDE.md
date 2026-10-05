# Reglas del proyecto

Estas reglas valen para toda sesión de trabajo en este repositorio, sin que haya
que repetirlas. Están escritas en primera persona: quien habla es el dueño del
repositorio.

## Idioma

- Todo va en español neutro, sin voseo ni regionalismos: código, comentarios,
  documentación, mensajes de commit, descripciones de PR y respuestas en el
  chat.

## Datos e integridad

- **Ningún número sin fuente.** Si un dato no existe o no se pudo verificar
  leyendo la fuente, se escribe "NO MEDIDO", con la razón. Nada de memoria y
  nada de estimar para rellenar.
- **Toda decisión que cambie un número publicado es un supuesto numerado** en
  `senales/SUPUESTOS.md` (prefijos `A-S2-*`, `A-R0-*`, ...), con su estado:
  dato, estimación, supuesto o no medido.
- **Ningún supuesto cambia en silencio.** Cada cambio va en la sección "Cambios
  de supuestos" de `senales/data/series/CHANGELOG.md`.
- **Ninguna serie se publica sin un caso de validación** contra una fuente
  independiente, con la tolerancia declarada antes de ver el resultado. Nunca
  se ajusta el cálculo ni la tolerancia para que cuadre. Hay dos clases de
  control:
  - **Gate de publicación.** Si falla, la corrida se detiene o la serie se
    publica como NO MEDIDO.
  - **Control de consistencia.** No detiene la corrida: marca el mes como
    valor en disputa y lo excluye de las métricas.
- **La regla de la tolerancia rige desde el 2026-10-05.** Las que se fijaron
  con lo observado a la vista (A-R0-12 y el umbral de A-R0-20) quedan como
  están, porque ya lo declaran.
- **Sin interpolación ni datos sintéticos.** Un hueco es un hueco.
- **Los dos lados de un ratio usan la misma convención.** Hoy: promedio mensual
  de cierres diarios, y solo de meses completos.
- **El sitio describe, no recomienda.** No usa verbos de acción ni la palabra
  "oportunidad".

## Licencias y repositorio público

- **El repositorio es público.** Solo se versionan crudos cuya licencia permite
  redistribuirlos (dominio público, CC BY, CC BY-NC u otros términos que lo
  permitan con atribución), con su archivo de atribución. Los demás van a
  `senales/data/privado/`, que git ignora; de esos se publica la URL, la fecha
  y el SHA-256, para que la corrida sea reproducible.
- Los pares con S&P 500 o Nasdaq quedan como "NO MEDIDO: pendiente de permiso
  del dueño del índice" hasta tener el permiso escrito.
- No se publican niveles de índices en ningún archivo público. Eso incluye el
  changelog, `FUENTES.md` y los tests.
- Se respetan los términos de cada fuente. Por ejemplo, el FMI no permite la
  descarga masiva automatizada: su archivo se actualiza a mano.

## Forma de trabajo

- Ramas y PR; nunca merge sin mi aprobación.
- Commits pequeños, uno por cambio.
- Antes de cerrar: tests en verde (sin red), y build y lint sin problemas
  nuevos.
- Si una decisión no está cubierta por estas reglas ni por
  `senales/SUPUESTOS.md`, pregúntame antes de decidir.
- Al reportar, distingue lo verificado de lo inferido.

## Entorno

- Máquina principal: Windows, `C:\Users\Frank\losratios`, PowerShell.
- Python de `senales/`: usa `.\senales\.venv\Scripts\python.exe`. La política
  de ejecución bloquea `Activate.ps1`.
- A FRED, un pedido por vez, con pausas.
- Comandos, desde `senales/`: `python -m senales.liquidez_neta` (S2) y
  `python -m senales.ratios` (fase R).
