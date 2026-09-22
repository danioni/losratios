"""S2.2: variación porcentual de S2.1 a N semanas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from senales.liquidez_neta import calcular_variacion, construir_serie


def _serie_semanal(valores, inicio="2026-01-07"):
    indice = pd.date_range(inicio, periods=len(valores), freq="W-WED")
    return pd.Series(valores, index=indice, dtype="float64")


def test_una_suba_del_diez_por_ciento_a_trece_semanas():
    valores = [1000.0] * 13 + [1100.0]
    serie = _serie_semanal(valores)
    variacion = calcular_variacion(serie, 13)
    assert variacion.iloc[-1] == pytest.approx(10.0)


def test_una_baja_del_veinticinco_por_ciento():
    valores = [800.0] * 13 + [600.0]
    variacion = calcular_variacion(_serie_semanal(valores), 13)
    assert variacion.iloc[-1] == pytest.approx(-25.0)


def test_las_primeras_trece_semanas_no_tienen_referencia():
    variacion = calcular_variacion(_serie_semanal([1000.0] * 20), 13)
    assert variacion.iloc[:13].isna().all()
    assert variacion.iloc[13:].eq(0.0).all()


def test_la_ventana_es_parametrizable():
    valores = [100.0, 110.0, 120.0, 130.0, 140.0]
    serie = _serie_semanal(valores)
    assert calcular_variacion(serie, 1).iloc[-1] == pytest.approx(140 / 130 * 100 - 100)
    assert calcular_variacion(serie, 4).iloc[-1] == pytest.approx(40.0)


def test_si_falta_la_semana_de_referencia_el_resultado_es_vacio():
    serie = _serie_semanal([1000.0] * 14)
    recortada = serie.drop(serie.index[0])
    variacion = calcular_variacion(recortada, 13)
    # La única fila con referencia posible perdió su par: no se salta a otra semana.
    assert variacion.isna().all()


def test_una_referencia_en_cero_no_produce_infinito():
    serie = _serie_semanal([0.0] + [100.0] * 13)
    variacion = calcular_variacion(serie, 13)
    assert np.isnan(variacion.iloc[-1])


def test_la_columna_de_la_tabla_usa_la_ventana_configurada(walcl, tga, rrp):
    tabla = construir_serie(walcl, tga, rrp, ventana_semanas=13).set_index("fecha")
    actual = tabla.loc[pd.Timestamp("2026-09-16"), "s2_1_liquidez_neta"]
    referencia = tabla.loc[pd.Timestamp("2026-06-17"), "s2_1_liquidez_neta"]
    esperado = (actual / referencia - 1.0) * 100.0
    assert tabla.loc[pd.Timestamp("2026-09-16"), "s2_2_var_13s_pct"] == pytest.approx(esperado)
