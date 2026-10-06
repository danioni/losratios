"""Fixtures compartidas. Ningún test toca la red ni escribe en data/ ni en reportes/.

Los archivos de ejemplo se llaman <ID>_ejemplo.csv, con el mismo identificador
que usa FRED. Así, cambiar qué serie es la predeterminada en configuracion.py no
obliga a editar los tests: basta con que exista el archivo de esa serie.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from senales.configuracion import (
    SERIE_RRP,
    SERIE_TGA,
    SERIE_TGA_PROMEDIO_SEMANAL,
    SERIE_WALCL,
    SerieFRED,
)
from senales.fuentes_fred import leer_csv_crudo

DIR_FIXTURES = Path(__file__).parent / "fixtures"


def ruta_de_ejemplo(serie: SerieFRED) -> Path:
    """Archivo de ejemplo de una serie, por su identificador de FRED."""
    return DIR_FIXTURES / f"{serie.id}_ejemplo.csv"


def cargar_ejemplo(serie: SerieFRED) -> pd.Series:
    """Lee el archivo de ejemplo de una serie, ya normalizado a miles de millones."""
    return leer_csv_crudo(ruta_de_ejemplo(serie), serie)


@pytest.fixture
def dir_fixtures() -> Path:
    return DIR_FIXTURES


@pytest.fixture
def walcl() -> pd.Series:
    return cargar_ejemplo(SERIE_WALCL)


@pytest.fixture
def tga() -> pd.Series:
    """El TGA de la serie predeterminada (A-S2-4: WDTGAL, nivel de miércoles)."""
    return cargar_ejemplo(SERIE_TGA)


@pytest.fixture
def tga_promedio_semanal() -> pd.Series:
    """El TGA de la alternativa documentada (A-S2-4: WTREGEN, promedio semanal)."""
    return cargar_ejemplo(SERIE_TGA_PROMEDIO_SEMANAL)


@pytest.fixture
def rrp() -> pd.Series:
    return cargar_ejemplo(SERIE_RRP)


# --- Ningún test escribe en data/ ------------------------------------------------

DIR_DATA = Path(__file__).parent.parent / "data"


def _estado_de_data() -> dict[str, tuple[int, int]]:
    """Tamaño y fecha de cada archivo versionable de data/: lo que un test no debe tocar."""
    estado = {}
    for subdirectorio in ("raw", "series"):
        base = DIR_DATA / subdirectorio
        if not base.exists():
            continue
        for ruta in base.rglob("*"):
            if ruta.is_file():
                info = ruta.stat()
                estado[str(ruta.relative_to(DIR_DATA))] = (info.st_size, info.st_mtime_ns)
    return estado


@pytest.fixture(autouse=True)
def data_intacta():
    """Falla el test que modifique, cree o borre un archivo en data/raw o data/series.

    La primera corrida del PR #4 publicó pares contra M2 calculados con datos de
    prueba porque un test escribió en data/series/. Esto lo hace imposible de
    pasar por alto: el culpable es el test que falla aquí.
    """
    antes = _estado_de_data()
    yield
    despues = _estado_de_data()
    cambios = sorted(set(antes) ^ set(despues)) + sorted(k for k in antes if k in despues and antes[k] != despues[k])
    assert not cambios, f"el test escribió en data/: {cambios}"
