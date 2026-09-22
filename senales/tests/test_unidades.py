"""Unidades: todo tiene que quedar en miles de millones de USD, y nada se asume."""

from __future__ import annotations

import pandas as pd
import pytest

from dataclasses import replace

from senales.configuracion import (
    FACTOR_A_MILES_DE_MILLONES,
    SERIE_RRP,
    SERIE_TGA,
    SERIE_TGA_NIVEL_MIERCOLES,
    SERIE_TGA_PROMEDIO_SEMANAL,
    SERIE_WALCL,
    VALIDACION_H41,
)
from senales.fuentes_fred import (
    ErrorDeFuente,
    leer_csv_crudo,
    verificar_orden_de_magnitud,
    verificar_unidades,
)
from senales.nucleo import normalizar_texto
from tests.conftest import ruta_de_ejemplo


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


def test_el_rrp_ya_viene_en_miles_de_millones(rrp):
    assert rrp.loc[pd.Timestamp("2026-09-16")] == pytest.approx(4.0)


def test_el_tga_queda_en_miles_de_millones_venga_como_venga(tga, tga_promedio_semanal):
    # WDTGAL llega en millones y WTREGEN en miles de millones; después de
    # normalizar, las dos tienen que dar el mismo orden de magnitud.
    assert tga.loc[pd.Timestamp("2026-09-16")] == pytest.approx(877.0)
    assert tga_promedio_semanal.loc[pd.Timestamp("2026-09-16")] == pytest.approx(877.0)


# --- A-S2-4: el identificador de la serie de TGA y su unidad van juntos --------
#
# WDTGAL se publica en millones de USD. Si alguien cambia el identificador y se
# olvida de la unidad, S2.1 se va por un factor de 1000 y el ancla del H.4.1
# deja de cerrar. Estos tests existen para que ese olvido no llegue a publicarse.


def test_la_serie_de_tga_predeterminada_es_el_nivel_de_miercoles():
    assert SERIE_TGA.id == "WDTGAL"
    assert SERIE_TGA is SERIE_TGA_NIVEL_MIERCOLES


def test_wdtgal_se_declara_en_millones():
    assert SERIE_TGA_NIVEL_MIERCOLES.unidad == "millones", (
        "WDTGAL se publica en millones de USD. Cambiar esta unidad sin cambiar "
        "el identificador rompe S2.1 por un factor de 1000 (A-S2-4)."
    )
    assert SERIE_TGA_NIVEL_MIERCOLES.factor == 0.001
    assert normalizar_texto(SERIE_TGA_NIVEL_MIERCOLES.unidad_fred) == "millions of u.s. dollars"


def test_la_alternativa_wtregen_sigue_declarada_en_miles_de_millones():
    assert SERIE_TGA_PROMEDIO_SEMANAL.unidad == "miles_de_millones"
    assert SERIE_TGA_PROMEDIO_SEMANAL.factor == 1.0


def test_wdtgal_leido_como_miles_de_millones_se_va_por_un_factor_de_1000():
    mal_declarada = replace(SERIE_TGA_NIVEL_MIERCOLES, unidad="miles_de_millones")
    valores = leer_csv_crudo(ruta_de_ejemplo(SERIE_TGA_NIVEL_MIERCOLES), mal_declarada)
    ancla = valores.loc[pd.Timestamp(VALIDACION_H41.fecha)]
    assert ancla == pytest.approx(VALIDACION_H41.tga * 1000)
    with pytest.raises(ErrorDeFuente, match="fuera de la banda plausible"):
        verificar_orden_de_magnitud(valores, mal_declarada)


def test_si_fred_declara_millones_y_la_config_dice_lo_contrario_la_corrida_corta():
    mal_declarada = replace(SERIE_TGA_NIVEL_MIERCOLES, unidad="miles_de_millones")
    with pytest.raises(ErrorDeFuente, match="no ajustar el cálculo"):
        verificar_unidades(mal_declarada, "Millions of U.S. Dollars")


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
