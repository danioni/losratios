"""Fixtures compartidas. Ningún test toca la red ni escribe en data/ ni en reportes/."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from senales.configuracion import SERIE_RRP, SERIE_TGA_PROMEDIO_SEMANAL, SERIE_WALCL
from senales.fuentes_fred import leer_csv_crudo

DIR_FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def dir_fixtures() -> Path:
    return DIR_FIXTURES


@pytest.fixture
def walcl() -> pd.Series:
    return leer_csv_crudo(DIR_FIXTURES / "WALCL_ejemplo.csv", SERIE_WALCL)


@pytest.fixture
def tga() -> pd.Series:
    return leer_csv_crudo(DIR_FIXTURES / "WTREGEN_ejemplo.csv", SERIE_TGA_PROMEDIO_SEMANAL)


@pytest.fixture
def rrp() -> pd.Series:
    return leer_csv_crudo(DIR_FIXTURES / "RRPONTSYD_ejemplo.csv", SERIE_RRP)
