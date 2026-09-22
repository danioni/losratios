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
