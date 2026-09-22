"""Unidades: todo tiene que quedar en miles de millones de USD, y nada se asume."""

from __future__ import annotations

import pandas as pd
import pytest

from senales.configuracion import (
    FACTOR_A_MILES_DE_MILLONES,
    SERIE_RRP,
    SERIE_TGA_PROMEDIO_SEMANAL,
    SERIE_WALCL,
)
from senales.fuentes_fred import (
    ErrorDeFuente,
    leer_csv_crudo,
    verificar_orden_de_magnitud,
    verificar_unidades,
)


def test_factores_declarados():
    assert FACTOR_A_MILES_DE_MILLONES["millones"] == 0.001
    assert FACTOR_A_MILES_DE_MILLONES["miles_de_millones"] == 1.0
    assert SERIE_WALCL.factor == 0.001
    assert SERIE_TGA_PROMEDIO_SEMANAL.factor == 1.0
    assert SERIE_RRP.factor == 1.0


def test_walcl_en_millones_queda_en_miles_de_millones(walcl):
    # El archivo trae 6747000 millones para el ancla; la serie tiene que dar 6747.
    assert walcl.loc[pd.Timestamp("2026-09-16")] == pytest.approx(6747.0)
    assert walcl.max() < 20_000


def test_tga_y_rrp_ya_vienen_en_miles_de_millones(tga, rrp):
    assert tga.loc[pd.Timestamp("2026-09-16")] == pytest.approx(877.0)
    assert rrp.loc[pd.Timestamp("2026-09-16")] == pytest.approx(4.0)


def test_se_acepta_el_encabezado_viejo_de_fred(dir_fixtures, walcl):
    viejo = leer_csv_crudo(dir_fixtures / "WALCL_encabezado_viejo.csv", SERIE_WALCL)
    pd.testing.assert_series_equal(viejo, walcl)


def test_un_csv_con_otra_serie_no_se_lee_en_silencio(dir_fixtures):
    with pytest.raises(ErrorDeFuente, match="se esperaba 'RRPONTSYD'"):
        leer_csv_crudo(dir_fixtures / "WALCL_ejemplo.csv", SERIE_RRP)


def test_el_punto_de_fred_es_un_hueco_no_un_cero(rrp):
    # El fixture marca 2026-07-01 con un punto: esa fecha no debe existir en la serie.
    assert pd.Timestamp("2026-07-01") not in rrp.index
    assert not (rrp == 0).any()


def test_unidad_coincidente_queda_verificada():
    resultado = verificar_unidades(SERIE_WALCL, "Millions of U.S. Dollars")
    assert resultado.verificada
    assert resultado.etiqueta == "VERIFICADA"


def test_sin_metadatos_la_unidad_queda_sin_verificar():
    resultado = verificar_unidades(SERIE_WALCL, None)
    assert not resultado.verificada
    assert resultado.etiqueta == "NO VERIFICADA"


def test_unidad_distinta_a_la_configurada_corta_la_corrida():
    with pytest.raises(ErrorDeFuente, match="no ajustar el cálculo"):
        verificar_unidades(SERIE_WALCL, "Billions of U.S. Dollars")


def test_unidad_desconocida_no_se_da_por_buena():
    resultado = verificar_unidades(SERIE_WALCL, "Thousands of Yen")
    assert not resultado.verificada


def test_la_banda_de_orden_de_magnitud_atrapa_un_error_de_1000x(walcl):
    verificar_orden_de_magnitud(walcl, SERIE_WALCL)  # no levanta
    with pytest.raises(ErrorDeFuente, match="fuera de la banda plausible"):
        verificar_orden_de_magnitud(walcl * 1000, SERIE_WALCL)
