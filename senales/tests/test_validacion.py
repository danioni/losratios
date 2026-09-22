"""El caso de validación del H.4.1 de la semana del 16 de septiembre de 2026.

WALCL 6747, TGA 877, ON RRP 4 -> S2.1 = 5866, con tolerancia +/-5.
"""

from __future__ import annotations

import pandas as pd
import pytest

from senales.configuracion import VALIDACION_H41
from senales.liquidez_neta import construir_serie, validar_caso_ancla


def test_el_ancla_esta_bien_declarada():
    caso = VALIDACION_H41
    assert caso.fecha.isoformat() == "2026-09-16"
    assert caso.walcl - caso.tga - caso.rrp == pytest.approx(caso.s2_1_esperado)
    assert caso.tolerancia == 5.0


def test_la_serie_reproduce_el_ancla(walcl, tga, rrp):
    tabla = construir_serie(walcl, tga, rrp)
    fila = tabla.set_index("fecha").loc[pd.Timestamp("2026-09-16")]
    assert fila["walcl"] == pytest.approx(6747.0)
    assert fila["tga"] == pytest.approx(877.0)
    assert fila["rrp"] == pytest.approx(4.0)
    assert fila["s2_1_liquidez_neta"] == pytest.approx(5866.0)


def test_el_gate_pasa_cuando_el_calculo_cuadra(walcl, tga, rrp):
    resultado = validar_caso_ancla(construir_serie(walcl, tga, rrp), VALIDACION_H41)
    assert resultado.ok
    assert resultado.diferencia == pytest.approx(0.0)
    assert resultado.resumen().startswith("OK")


def test_el_gate_tolera_una_diferencia_menor_a_cinco(walcl, tga, rrp):
    corrido = walcl.copy()
    corrido.loc[pd.Timestamp("2026-09-16")] += 4.0
    resultado = validar_caso_ancla(construir_serie(corrido, tga, rrp), VALIDACION_H41)
    assert resultado.ok
    assert resultado.diferencia == pytest.approx(4.0)


def test_el_gate_falla_y_reporta_la_diferencia(walcl, tga, rrp):
    corrido = walcl.copy()
    corrido.loc[pd.Timestamp("2026-09-16")] += 40.0
    resultado = validar_caso_ancla(construir_serie(corrido, tga, rrp), VALIDACION_H41)
    assert not resultado.ok
    assert resultado.diferencia == pytest.approx(40.0)
    assert resultado.resumen().startswith("FALLA")
    detalle = "\n".join(resultado.detalle_componentes())
    assert "WALCL" in detalle and "6787.000" in detalle


def test_un_error_de_unidad_en_el_tga_no_pasa_desapercibido(walcl, tga, rrp):
    # Si alguien tratara WTREGEN como si viniera en millones, el TGA quedaría
    # mil veces más chico y el ancla no cerraria.
    resultado = validar_caso_ancla(construir_serie(walcl, tga / 1000, rrp), VALIDACION_H41)
    assert not resultado.ok
    assert resultado.diferencia == pytest.approx(877.0 - 0.877, abs=1e-6)


def test_sin_la_fecha_ancla_el_gate_no_da_por_buena_la_serie(walcl, tga, rrp):
    sin_ancla = walcl.drop(pd.Timestamp("2026-09-16"))
    resultado = validar_caso_ancla(construir_serie(sin_ancla, tga, rrp), VALIDACION_H41)
    assert not resultado.ok
    assert resultado.calculado is None
    assert "no está en la serie calculada" in resultado.resumen()
