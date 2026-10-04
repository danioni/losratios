"""Alineación al miércoles y arrastre del ON RRP."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from senales.fuentes_fred import ErrorDeFuente
from senales.liquidez_neta import alinear_a_miercoles, construir_serie, detectar_huecos


def test_todas_las_observaciones_caen_en_miercoles(walcl, tga, rrp):
    tabla = alinear_a_miercoles(walcl, tga, rrp, date(2020, 1, 1))
    assert not tabla.empty
    assert (pd.to_datetime(tabla["fecha"]).dt.weekday == 2).all()


def test_el_tga_se_engancha_por_fecha_exacta(walcl, tga, rrp):
    tabla = alinear_a_miercoles(walcl, tga, rrp, date(2020, 1, 1)).set_index("fecha")
    assert tabla.loc[pd.Timestamp("2026-09-16"), "tga"] == pytest.approx(991.708)


def test_el_rrp_del_miercoles_se_toma_de_ese_dia(walcl, tga, rrp):
    tabla = alinear_a_miercoles(walcl, tga, rrp, date(2020, 1, 1)).set_index("fecha")
    fila = tabla.loc[pd.Timestamp("2026-09-16")]
    assert fila["rrp"] == pytest.approx(5.375)
    assert fila["rrp_fecha_origen"] == pd.Timestamp("2026-09-16")


def test_si_el_miercoles_no_tiene_rrp_se_usa_el_anterior_y_se_marca(walcl, tga, rrp):
    # El fixture no trae 2026-08-19, así que ese miércoles usa el dato del 18.
    tabla = alinear_a_miercoles(walcl, tga, rrp, date(2020, 1, 1)).set_index("fecha")
    fila = tabla.loc[pd.Timestamp("2026-08-19")]
    assert fila["rrp_fecha_origen"] == pd.Timestamp("2026-08-18")
    assert fila["rrp"] == pytest.approx(rrp.loc[pd.Timestamp("2026-08-18")])


def test_el_arrastre_tiene_limite_y_mas_alla_es_hueco(walcl, tga, rrp):
    recortado = rrp[rrp.index <= pd.Timestamp("2026-08-18")]
    tabla = alinear_a_miercoles(walcl, tga, recortado, date(2020, 1, 1), max_dias_arrastre=7)
    ultimo = tabla.set_index("fecha").loc[pd.Timestamp("2026-09-16")]
    assert pd.isna(ultimo["rrp"])
    assert pd.isna(ultimo["rrp_fecha_origen"])


def test_una_fecha_que_no_es_miercoles_en_walcl_corta_la_corrida(walcl, tga, rrp):
    contaminada = pd.concat([walcl, pd.Series([6700.0], index=[pd.Timestamp("2026-09-17")])])
    with pytest.raises(ErrorDeFuente, match="no caen en miércoles"):
        alinear_a_miercoles(contaminada.sort_index(), tga, rrp, date(2020, 1, 1))


def test_la_fecha_de_inicio_recorta_la_historia(walcl, tga, rrp):
    tabla = alinear_a_miercoles(walcl, tga, rrp, date(2026, 8, 1))
    assert tabla["fecha"].min() >= pd.Timestamp("2026-08-01")


def test_un_tga_faltante_queda_como_hueco_y_no_se_rellena(walcl, tga, rrp):
    sin_una_semana = tga.drop(pd.Timestamp("2026-08-26"))
    tabla = construir_serie(walcl, sin_una_semana, rrp)
    fila = tabla.set_index("fecha").loc[pd.Timestamp("2026-08-26")]
    assert pd.isna(fila["tga"])
    assert pd.isna(fila["s2_1_liquidez_neta"])
    huecos = detectar_huecos(tabla)
    assert any("2026-08-26" in h and "sin dato" in h for h in huecos)


def test_un_miercoles_sin_walcl_se_reporta_como_hueco(walcl, tga, rrp):
    sin_semana = walcl.drop(pd.Timestamp("2026-08-26"))
    tabla = construir_serie(sin_semana, tga, rrp)
    huecos = detectar_huecos(tabla)
    assert any("2026-08-26" in h and "miércoles sin observación" in h for h in huecos)


def test_el_arrastre_del_rrp_se_reporta_aunque_haya_valor(walcl, tga, rrp):
    tabla = construir_serie(walcl, tga, rrp)
    huecos = detectar_huecos(tabla)
    assert any("2026-08-19" in h and "2026-08-18" in h for h in huecos)
