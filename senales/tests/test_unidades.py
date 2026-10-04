"""Unidades: todo tiene que quedar en miles de millones de USD, y nada se asume."""

from __future__ import annotations

import pandas as pd
import pytest
import requests

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
    unidad_declarada,
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
    # El archivo trae 6746548 millones para el ancla; la serie tiene que dar 6746.548.
    assert walcl.loc[pd.Timestamp("2026-09-16")] == pytest.approx(6746.548)
    assert walcl.max() < 20_000


def test_el_rrp_ya_viene_en_miles_de_millones(rrp):
    assert rrp.loc[pd.Timestamp("2026-09-16")] == pytest.approx(5.375)


def test_el_tga_queda_en_miles_de_millones_venga_como_venga(tga, tga_promedio_semanal):
    # WDTGAL llega en millones y WTREGEN en miles de millones; después de
    # normalizar, las dos tienen que quedar en el mismo orden de magnitud.
    # Los valores NO coinciden, y eso es el punto de A-S2-4: 991.708 es el nivel
    # del miércoles y 877.028 el promedio de esa semana.
    nivel = tga.loc[pd.Timestamp("2026-09-16")]
    promedio = tga_promedio_semanal.loc[pd.Timestamp("2026-09-16")]
    assert nivel == pytest.approx(991.708)
    assert promedio == pytest.approx(877.028)
    assert 100.0 < nivel < 10_000.0 and 100.0 < promedio < 10_000.0


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


# --- A-S2-9: por qué no se pudo leer la unidad, no solo que no se pudo --------
#
# En la primera corrida real las tres series salieron NO VERIFICADAS y la salida
# no permitía saber si FRED había respondido 404, si la respuesta era HTML o si
# el encabezado había cambiado de formato. `unidad_declarada` devuelve ahora
# (unidad, motivo) y el motivo distingue los casos. Nada de esto toca la red.


class _RespuestaFalsa:
    def __init__(self, status_code: int, text: str, headers: dict | None = None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}


class _SesionFalsa:
    """Doble de requests.Session: devuelve una respuesta fija o levanta un error."""

    def __init__(self, respuesta=None, error: Exception | None = None):
        self._respuesta = respuesta
        self._error = error
        self.urls_pedidas: list[str] = []

    def get(self, url, timeout=None):
        self.urls_pedidas.append(url)
        if self._error is not None:
            raise self._error
        return self._respuesta


# Encabezado con el formato que publica FRED en /data/<ID>.txt. Se usa para
# probar el parseo, no para afirmar que el endpoint esté disponible: si la
# investigación de A-S2-9 encuentra que el formato real difiere, este texto es
# lo que hay que corregir, y este test es el que lo va a delatar.
ENCABEZADO_FRED = """Title:               Liabilities and Capital: Deposits with F.R. Banks, Other Than Reserve Balances: U.S. Treasury, General Account: Wednesday Level
Series ID:           WDTGAL
Source:              Board of Governors of the Federal Reserve System (US)
Release:             H.4.1 Factors Affecting Reserve Balances
Seasonal Adjustment: Not Applicable
Frequency:           Weekly, As of Wednesday
Units:               Millions of U.S. Dollars
Date Range:          2002-12-18 to 2026-09-16
Last Updated:        2026-09-17 4:31 PM CDT

DATE                 VALUE
2026-09-16           991708
"""


def test_del_encabezado_de_fred_se_lee_la_unidad_y_de_donde_salio():
    sesion = _SesionFalsa(_RespuestaFalsa(200, ENCABEZADO_FRED))
    unidad, motivo = unidad_declarada(SERIE_TGA_NIVEL_MIERCOLES, sesion)
    assert unidad == "Millions of U.S. Dollars"
    assert "WDTGAL.txt" in motivo
    # Y la unidad leída tiene que cerrar con la configurada.
    assert verificar_unidades(SERIE_TGA_NIVEL_MIERCOLES, unidad, motivo).verificada


def test_si_la_red_falla_el_motivo_nombra_el_error():
    sesion = _SesionFalsa(error=requests.ConnectionError("tunnel connection failed"))
    unidad, motivo = unidad_declarada(SERIE_WALCL, sesion)
    assert unidad is None
    assert "no respondió" in motivo
    assert "ConnectionError" in motivo and "tunnel connection failed" in motivo


def test_si_fred_responde_404_el_motivo_nombra_el_codigo():
    sesion = _SesionFalsa(_RespuestaFalsa(404, "Not Found"))
    unidad, motivo = unidad_declarada(SERIE_WALCL, sesion)
    assert unidad is None
    assert "HTTP 404" in motivo


def test_si_la_respuesta_no_trae_la_linea_de_unidades_el_motivo_lo_dice():
    sesion = _SesionFalsa(
        _RespuestaFalsa(200, "<!DOCTYPE html>\n<html><head><title>FRED</title>", {"Content-Type": "text/html"})
    )
    unidad, motivo = unidad_declarada(SERIE_WALCL, sesion)
    assert unidad is None
    assert "no hay línea 'Units:'" in motivo
    assert "text/html" in motivo
    assert "<!DOCTYPE html>" in motivo


def test_el_motivo_llega_hasta_el_detalle_de_la_verificacion():
    resultado = verificar_unidades(SERIE_WALCL, None, "https://ejemplo respondió HTTP 404")
    assert not resultado.verificada
    assert "causa: https://ejemplo respondió HTTP 404" in resultado.detalle


def test_sin_motivo_el_detalle_sigue_siendo_legible():
    """Compatibilidad: verificar_unidades se puede llamar con dos argumentos."""
    resultado = verificar_unidades(SERIE_WALCL, None)
    assert not resultado.verificada
    assert "causa:" not in resultado.detalle
