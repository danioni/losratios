"""El caso de validación del H.4.1 de la semana terminada el 16 de septiembre de 2026.

Niveles de miércoles: WALCL 6746.548, TGA 991.708, ON RRP 5.375
-> S2.1 = 5749.465, con tolerancia +/-5 en el total y +/-1 por componente.

El ancla original de esta serie mezclaba columnas del release (nivel de miércoles
para los activos totales, promedio semanal para el TGA y el ON RRP) y el gate la
rechazó en la primera corrida real. Varios de los tests de aquí existen para que
esa clase de error no vuelva a pasar desapercibida: ver A-S2-13 y A-S2-14.
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
    assert caso.tolerancia_componente == 1.0


def test_el_ancla_declara_de_donde_salieron_sus_numeros():
    """A-S2-13: un ancla sin procedencia no se puede auditar ni actualizar."""
    caso = VALIDACION_H41
    assert caso.fuente_url.startswith("https://")
    assert caso.fecha_publicacion.isoformat() == "2026-09-17"
    assert caso.fecha_publicacion > caso.fecha, (
        "el release se publica después del miércoles al que se refiere"
    )
    assert "miércoles" in caso.columna
    assert "6746548" in caso.fuente and "991708" in caso.fuente and "5375" in caso.fuente


def test_la_serie_reproduce_el_ancla(walcl, tga, rrp):
    tabla = construir_serie(walcl, tga, rrp)
    fila = tabla.set_index("fecha").loc[pd.Timestamp("2026-09-16")]
    assert fila["walcl"] == pytest.approx(6746.548)
    assert fila["tga"] == pytest.approx(991.708)
    assert fila["rrp"] == pytest.approx(5.375)
    assert fila["s2_1_liquidez_neta"] == pytest.approx(5749.465)


def test_el_gate_pasa_cuando_el_calculo_cuadra(walcl, tga, rrp):
    resultado = validar_caso_ancla(construir_serie(walcl, tga, rrp), VALIDACION_H41)
    assert resultado.ok
    assert resultado.ok_total and resultado.ok_componentes
    assert resultado.diferencia == pytest.approx(0.0)
    assert resultado.componentes_fuera == []
    assert resultado.resumen().startswith("OK")


def test_el_gate_tolera_un_desvio_menor_que_la_tolerancia_por_componente(walcl, tga, rrp):
    corrido = walcl.copy()
    corrido.loc[pd.Timestamp("2026-09-16")] += 0.4
    resultado = validar_caso_ancla(construir_serie(corrido, tga, rrp), VALIDACION_H41)
    assert resultado.ok
    assert resultado.diferencia == pytest.approx(0.4)


def test_un_desvio_por_componente_mayor_a_uno_no_pasa_aunque_el_total_entre_en_cinco(
    walcl, tga, rrp
):
    """A-S2-14: el total no es suficiente. Un componente corrido 1.5 lo delata."""
    corrido = walcl.copy()
    corrido.loc[pd.Timestamp("2026-09-16")] += 1.5
    resultado = validar_caso_ancla(construir_serie(corrido, tga, rrp), VALIDACION_H41)
    assert resultado.ok_total, "1.5 entra en la tolerancia de +/-5 del total"
    assert not resultado.ok_componentes
    assert not resultado.ok
    assert resultado.componentes_fuera == ["WALCL"]
    assert "fuera de +/-1.000 por componente: WALCL" in resultado.resumen()


def test_un_total_que_cuadra_por_compensacion_no_pasa(walcl, tga, rrp):
    """El caso que motivó A-S2-14.

    Con WALCL y TGA corridos lo mismo en la misma dirección, la resta da el
    esperado al milímetro y el gate viejo habría publicado la serie. Ninguno de
    los dos componentes reproduce el release, así que el ancla no está
    reproducida: es una coincidencia aritmética.
    """
    walcl_corrido, tga_corrido = walcl.copy(), tga.copy()
    walcl_corrido.loc[pd.Timestamp("2026-09-16")] += 3.0
    tga_corrido.loc[pd.Timestamp("2026-09-16")] += 3.0

    resultado = validar_caso_ancla(
        construir_serie(walcl_corrido, tga_corrido, rrp), VALIDACION_H41
    )
    assert resultado.diferencia == pytest.approx(0.0)
    assert resultado.ok_total
    assert not resultado.ok, "un total exacto con dos componentes mal no reproduce el ancla"
    assert resultado.componentes_fuera == ["WALCL", "TGA"]
    assert resultado.desvios["WALCL"] == pytest.approx(3.0)
    assert resultado.desvios["TGA"] == pytest.approx(3.0)
    assert resultado.desvios["ON RRP"] == pytest.approx(0.0)


def test_el_gate_falla_y_reporta_la_diferencia(walcl, tga, rrp):
    corrido = walcl.copy()
    corrido.loc[pd.Timestamp("2026-09-16")] += 40.0
    resultado = validar_caso_ancla(construir_serie(corrido, tga, rrp), VALIDACION_H41)
    assert not resultado.ok
    assert resultado.diferencia == pytest.approx(40.0)
    assert resultado.resumen().startswith("FALLA")
    detalle = "\n".join(resultado.detalle_componentes())
    assert "WALCL" in detalle and "6786.548" in detalle


def test_el_detalle_marca_que_componente_cierra_y_cual_no(walcl, tga, rrp):
    corrido = tga.copy()
    corrido.loc[pd.Timestamp("2026-09-16")] += 20.0
    resultado = validar_caso_ancla(construir_serie(walcl, corrido, rrp), VALIDACION_H41)
    lineas = {l.split()[0]: l for l in resultado.detalle_componentes()}
    assert lineas["WALCL"].endswith("OK")
    assert lineas["TGA"].endswith("FALLA")
    assert lineas["ON"].endswith("OK")  # "ON RRP"


def test_un_error_de_unidad_en_el_tga_no_pasa_desapercibido(walcl, tga, rrp):
    # WDTGAL llega en millones. Si alguien lo tratara como si ya viniera en miles
    # de millones, el TGA quedaría mil veces más grande y el ancla no cerraría.
    resultado = validar_caso_ancla(construir_serie(walcl, tga * 1000, rrp), VALIDACION_H41)
    assert not resultado.ok
    assert resultado.diferencia == pytest.approx(
        VALIDACION_H41.tga - VALIDACION_H41.tga * 1000, abs=1e-6
    )
    assert resultado.componentes_fuera == ["TGA"]


def test_la_alternativa_wtregen_no_reproduce_un_ancla_de_nivel_de_miercoles(
    walcl, tga_promedio_semanal, rrp
):
    """A-S2-4 y A-S2-13: esto es justamente lo que el gate tiene que atrapar.

    `WTREGEN` es el promedio de la semana. Contra un ancla de niveles de
    miércoles no cierra, y en la semana del 16 de septiembre de 2026 la brecha
    es de 114.68 miles de millones porque el TGA subió con el vencimiento
    impositivo del 15. El gate rechaza la corrida, y eso es correcto: para
    volver a `WTREGEN` habría que cambiar también el ancla, a la columna de
    promedio semanal del release.
    """
    resultado = validar_caso_ancla(
        construir_serie(walcl, tga_promedio_semanal, rrp), VALIDACION_H41
    )
    assert not resultado.ok
    assert resultado.componentes_fuera == ["TGA"]
    assert resultado.desvios["TGA"] == pytest.approx(877.028 - 991.708)
    assert resultado.diferencia == pytest.approx(114.68, abs=1e-6)


def test_sin_la_fecha_ancla_el_gate_no_da_por_buena_la_serie(walcl, tga, rrp):
    sin_ancla = walcl.drop(pd.Timestamp("2026-09-16"))
    resultado = validar_caso_ancla(construir_serie(sin_ancla, tga, rrp), VALIDACION_H41)
    assert not resultado.ok
    assert resultado.calculado is None
    assert "no está en la serie calculada" in resultado.resumen()
    # Sin fila ancla no hay componente que verificar: los tres cuentan como fuera.
    assert resultado.componentes_fuera == ["WALCL", "TGA", "ON RRP"]
