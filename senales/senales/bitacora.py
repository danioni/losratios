"""Changelog de las series y detección de revisiones de datos históricos.

FRED revisa hacia atrás. Cada corrida compara lo que acaba de calcular contra
la serie publicada en la corrida anterior y deja constancia de toda diferencia,
no solo de las filas nuevas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from senales.nucleo import formatear

ENCABEZADO = (
    "# Changelog de data/series\n"
    "\n"
    "Una entrada por corrida, de la más reciente a la más antigua.\n"
    "\n"
    "Las secciones cuyo título no es una fecha (por ejemplo, los cambios de supuestos)\n"
    "se escriben a mano, se conservan arriba y el script no las toca.\n"
)

# Un título de entrada de corrida es una fecha ISO; cualquier otro título es
# una sección escrita a mano que hay que preservar.
PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Revision:
    """Un dato histórico que cambio respecto de la corrida anterior."""

    fecha: pd.Timestamp
    columna: str
    anterior: float
    nuevo: float

    @property
    def diferencia(self) -> float:
        return self.nuevo - self.anterior

    def __str__(self) -> str:
        return (
            f"{self.fecha.date()} | {self.columna}: "
            f"{formatear(self.anterior, 3)} -> {formatear(self.nuevo, 3)} "
            f"({formatear(self.diferencia, 3)})"
        )


def detectar_revisiones(
    previa: pd.DataFrame | None,
    nueva: pd.DataFrame,
    columnas: list[str],
    epsilon: float,
) -> list[Revision]:
    """Compara fecha por fecha las columnas revisables de dos corridas."""
    if previa is None or previa.empty:
        return []

    anterior = previa.set_index("fecha")
    actual = nueva.set_index("fecha")
    comunes = anterior.index.intersection(actual.index)

    revisiones: list[Revision] = []
    for columna in columnas:
        if columna not in anterior.columns or columna not in actual.columns:
            continue
        izquierda = pd.to_numeric(anterior.loc[comunes, columna], errors="coerce")
        derecha = pd.to_numeric(actual.loc[comunes, columna], errors="coerce")
        diferencia = (derecha - izquierda).abs()
        # Un dato que aparece o desaparece también es una revisión.
        cambio = (diferencia > epsilon) | (izquierda.isna() != derecha.isna())
        for fecha in comunes[cambio.fillna(False)]:
            revisiones.append(
                Revision(
                    fecha=fecha,
                    columna=columna,
                    anterior=izquierda.get(fecha),
                    nuevo=derecha.get(fecha),
                )
            )
    revisiones.sort(key=lambda r: (r.fecha, r.columna))
    return revisiones


def filas_agregadas(previa: pd.DataFrame | None, nueva: pd.DataFrame) -> list[pd.Timestamp]:
    """Fechas presentes en la corrida nueva que no estaban en la anterior."""
    if previa is None or previa.empty:
        return list(nueva["fecha"])
    faltantes = nueva.loc[~nueva["fecha"].isin(set(previa["fecha"])), "fecha"]
    return list(faltantes)


@dataclass
class EntradaChangelog:
    """Una corrida, tal como queda registrada en el changelog."""

    fecha_corrida: date
    rango_datos: tuple[pd.Timestamp, pd.Timestamp] | None
    observaciones: int
    agregadas: list[pd.Timestamp]
    revisiones: list[Revision]
    huecos: list[str]
    verificaciones_unidad: list[str]
    resultado_validacion: str
    umbral: str
    notas: list[str] = field(default_factory=list)

    def render(self) -> str:
        lineas = [f"## {self.fecha_corrida.isoformat()}", ""]

        if self.rango_datos is None:
            lineas.append("- Rango de datos: sin datos")
        else:
            inicio, fin = self.rango_datos
            lineas.append(
                f"- Rango de datos: {inicio.date()} a {fin.date()} "
                f"({self.observaciones} observaciones semanales)"
            )

        if self.agregadas:
            detalle = ", ".join(str(f.date()) for f in self.agregadas[-5:])
            sufijo = "" if len(self.agregadas) <= 5 else f" (últimas 5 de {len(self.agregadas)})"
            lineas.append(f"- Filas agregadas: {len(self.agregadas)} [{detalle}]{sufijo}")
        else:
            lineas.append("- Filas agregadas: 0")

        if self.revisiones:
            lineas.append(f"- Revisiones de datos históricos: {len(self.revisiones)}")
            for revision in self.revisiones:
                lineas.append(f"  - {revision}")
        else:
            lineas.append("- Revisiones de datos históricos: ninguna")

        if self.huecos:
            lineas.append(f"- Huecos: {len(self.huecos)}")
            for hueco in self.huecos:
                lineas.append(f"  - {hueco}")
        else:
            lineas.append("- Huecos: ninguno")

        lineas.append("- Verificación de unidades:")
        for verificacion in self.verificaciones_unidad:
            lineas.append(f"  - {verificacion}")

        lineas.append(f"- Validación: {self.resultado_validacion}")
        lineas.append(f"- Umbral de expansión/contracción: {self.umbral}")

        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")

        lineas.append("")
        return "\n".join(lineas)


def _separar_bloques(texto: str) -> tuple[list[str], dict[str, str]]:
    """Parte un changelog existente en secciones fijas y entradas de corrida.

    Devuelve las secciones escritas a mano en el orden en que estaban, y las
    entradas de corrida indexadas por fecha.
    """
    fijas: list[str] = []
    entradas: dict[str, str] = {}
    titulo: str | None = None
    acumulado: list[str] = []

    def guardar() -> None:
        if titulo is None:
            return
        bloque = "\n".join(acumulado).rstrip() + "\n"
        if PATRON_FECHA.match(titulo):
            entradas[titulo] = bloque
        else:
            fijas.append(bloque)

    for linea in texto.splitlines():
        if linea.startswith("## "):
            guardar()
            titulo = linea[3:].strip()
            acumulado = [linea]
        elif titulo is not None:
            acumulado.append(linea)
    guardar()
    return fijas, entradas


def actualizar_changelog(ruta: Path, entrada: EntradaChangelog) -> bool:
    """Agrega o reemplaza la entrada de esta corrida. Devuelve True si el archivo cambió.

    Idempotente: correrlo dos veces el mismo día deja una sola entrada. Si el
    segundo intento trae datos distintos, la entrada del día se reemplaza en vez
    de duplicarse, y el archivo refleja siempre la última corrida de esa fecha.

    Las secciones escritas a mano, como el registro de cambios de supuestos, se
    conservan tal cual y quedan arriba de las entradas de corrida.
    """
    previo = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
    fijas, entradas = _separar_bloques(previo)
    entradas[entrada.fecha_corrida.isoformat()] = entrada.render()

    ordenadas = sorted(entradas.items(), key=lambda par: par[0], reverse=True)
    bloques = fijas + [bloque for _, bloque in ordenadas]
    nuevo = ENCABEZADO + "\n" + "\n".join(bloque.rstrip() + "\n" for bloque in bloques)

    if nuevo == previo:
        return False
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(nuevo, encoding="utf-8")
    return True
