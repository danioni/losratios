"""Utilidades compartidas por todas las señales.

Este módulo es la base sobre la que se apoyan los módulos hermanos (S2.x acá,
S3.x flujos a ETFs y S4.x decaimiento de TQQQ más adelante). Cualquier serie
nueva debería escribir en data/series/ usando estas funciones, para que el
formato de salida y la idempotencia sean iguales en todo el marco.
"""

from __future__ import annotations

import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd

MIERCOLES = 2  # date.weekday(): lunes=0
FORMATO_FLOTANTE = "%.6f"


def asegurar_directorios(*directorios: Path) -> None:
    """Crea los directorios de salida si no existen."""
    for directorio in directorios:
        directorio.mkdir(parents=True, exist_ok=True)


def es_miercoles(fecha) -> bool:
    return pd.Timestamp(fecha).weekday() == MIERCOLES


def normalizar_texto(texto: str) -> str:
    """Minusculas, sin acentos y sin espacios repetidos. Para comparar unidades."""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return " ".join(sin_acentos.lower().split())


def escribir_csv_determinista(
    tabla: pd.DataFrame,
    ruta: Path,
    columnas: list[str],
    formato_flotante: str = FORMATO_FLOTANTE,
) -> None:
    """Escribe el CSV con orden de columnas, formato y saltos de linea fijos.

    Determinista a propósito: dos corridas con los mismos datos producen un
    archivo identico byte a byte, que es lo que hace que la corrida sea
    idempotente y que el diff de git muestre solo datos nuevos o revisados.
    """
    faltantes = [c for c in columnas if c not in tabla.columns]
    if faltantes:
        raise ValueError(f"faltan columnas en la tabla: {faltantes}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    tabla.loc[:, columnas].to_csv(
        temporal,
        index=False,
        float_format=formato_flotante,
        lineterminator="\n",
    )
    temporal.replace(ruta)


def leer_csv_serie(ruta: Path) -> pd.DataFrame | None:
    """Lee una serie ya publicada. Devuelve None si todavia no existe."""
    if not ruta.exists():
        return None
    tabla = pd.read_csv(ruta)
    if "fecha" in tabla.columns:
        tabla["fecha"] = pd.to_datetime(tabla["fecha"])
    return tabla


def formatear(valor, decimales: int = 2) -> str:
    """Formato de número para los reportes de texto.

    Se usa punto decimal y ningún separador de miles: el destino es un log y un
    changelog que también se leen con herramientas, y un separador de miles
    ambiguo en espanol sería peor que un número largo.
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "sin dato"
    return f"{float(valor):.{decimales}f}"


def hoy() -> date:
    return date.today()
