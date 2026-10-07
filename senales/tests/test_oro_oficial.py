"""El precio oficial del oro antes de 1960: derivación, tramos, gate y ficha. Sin red."""

from __future__ import annotations

from fractions import Fraction

import pandas as pd
import pytest

from senales import oro_oficial as oo, ratios
from senales.configuracion import (
    ANCLAS_ORO_OFICIAL,
    ARCHIVO_ORO_OFICIAL,
    CLAVE_ORO_OFICIAL,
    COLUMNAS_ORO_OFICIAL,
    COLUMNAS_SERIES_INFO,
    ETIQUETA_ORO_OFICIAL,
    FORMATO_RATIOS,
    TRAMOS_ORO_OFICIAL,
    AnclaOroOficial,
    TramoOroOficial,
)
from senales.nucleo import escribir_csv_determinista


def test_el_precio_sale_de_la_fraccion_legal_y_no_de_un_numero_tecleado():
    viejo, nuevo = TRAMOS_ORO_OFICIAL
    assert viejo.precio == Fraction(8000, 387)  # 480 / (25.8 * 0.9)
    assert nuevo.precio == Fraction(35, 1)  # 480 / (15 5/21 * 0.9) = 480 / (96/7)
    assert oo.precio_publicado(viejo) == 20.6718
    assert oo.precio_publicado(nuevo) == 35.0
    assert float(viejo.precio) == pytest.approx(20.671835, abs=1e-6)


def test_la_serie_cubre_1900_03_a_1959_12_sin_huecos_y_cambia_en_1934_02():
    serie = oo.construir_serie()
    assert list(serie.columns) == COLUMNAS_ORO_OFICIAL
    assert serie["mes"].iloc[0] == "1900-03" and serie["mes"].iloc[-1] == "1959-12"
    assert len(serie) == 10 + 59 * 12  # 718 meses, uno por mes
    assert list(serie["mes"]) == oo.meses_entre("1900-03", "1959-12")
    precios = serie.set_index("mes")["oro_oficial_usd_oz"]
    assert precios["1934-01"] == 20.6718  # A-R0-22: el mes del cambio lleva el precio anterior
    assert precios["1934-02"] == 35.0
    assert (precios.loc[:"1934-01"] == 20.6718).all() and (precios.loc["1934-02":] == 35.0).all()
    assert (serie["etiqueta"] == ETIQUETA_ORO_OFICIAL).all()
    assert (serie["apto_metricas"] == "no").all()
    assert (serie["estado"] == "dato").all()


def test_la_convertibilidad_y_el_precio_administrado_van_fila_por_fila():
    serie = oo.construir_serie().set_index("mes")
    assert serie.loc["1933-02", "convertibilidad"] == "sí"
    assert serie.loc["1933-03", "convertibilidad"].startswith("no: paridad legal sin convertibilidad")
    assert serie.loc["1934-02", "convertibilidad"].startswith("solo bancos centrales extranjeros")
    assert serie.loc["1933-08", "nota"] == ""
    assert "precio administrado" in serie.loc["1933-09", "nota"] and "precio administrado" in serie.loc["1934-01", "nota"]
    assert serie.loc["1934-02", "nota"] == ""
    assert "14 de marzo de 1900" in serie.loc["1900-03", "norma"]
    assert serie.loc["1934-02", "vigente_desde"].startswith("1934-01-31")


def test_los_tramos_tienen_que_seguirse_sin_hueco():
    viejo, nuevo = TRAMOS_ORO_OFICIAL
    con_hueco = (viejo, TramoOroOficial(**{**nuevo.__dict__, "desde": "1934-03"}))
    with pytest.raises(ValueError, match="no se siguen"):
        oo.construir_serie(con_hueco)


def test_el_gate_cierra_con_las_anclas_publicadas_y_exige_el_mes_del_cambio():
    serie = oo.construir_serie()
    validacion = oo.validar(serie)
    assert validacion.ok and validacion.anclas == len(ANCLAS_ORO_OFICIAL) >= 3
    assert validacion.maxima == pytest.approx(0.0018, abs=1e-4)  # 20.6718 contra "20.67"
    assert "cerró en 6 cifras" in validacion.validacion()
    # Un ancla distinta no cierra; una fecha de cambio distinta tampoco.
    torcida = ANCLAS_ORO_OFICIAL + (AnclaOroOficial("1950-01", 35.01, "prueba", "u", ANCLAS_ORO_OFICIAL[0].fecha_lectura),)
    assert oo.validar(serie, torcida).fuera == ["1950-01: serie 35.0000, fuente 35.01"]
    corrida = serie.copy()
    corrida.loc[corrida["mes"] == "1934-01", "oro_oficial_usd_oz"] = 35.0
    assert not oo.validar(corrida).mes_de_cambio_ok
    assert not oo.validar(serie, ANCLAS_ORO_OFICIAL[:2]).ok  # dos anclas no deciden


def test_la_ficha_dice_lo_que_la_serie_no_es(tmp_path):
    serie = oo.construir_serie()
    fila = oo.ficha(serie, oo.validar(serie))
    assert set(fila) == set(COLUMNAS_SERIES_INFO)
    assert fila["publicada"] == "sí" and fila["meses"] == 718
    assert ETIQUETA_ORO_OFICIAL in fila["fuente"]
    assert "precio administrado" in fila["fuente"] and "antes de 1900-03: NO MEDIDO" in fila["fuente"]
    assert "1960-01" in fila["fuente"] and "Fuera de apto_metricas" in fila["atribucion"]
    # Se inserta después del oro en series.csv y es idempotente.
    ruta = tmp_path / "series.csv"
    previas = pd.DataFrame(
        [{c: "" for c in COLUMNAS_SERIES_INFO} | {"serie": clave, "meses": "1"} for clave in ("oro", "plata", "btc")],
        columns=COLUMNAS_SERIES_INFO,
    )
    previas.to_csv(ruta, index=False, lineterminator="\n")
    oo.actualizar_ficha(ruta, fila)
    oo.actualizar_ficha(ruta, fila)
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    assert list(tabla["serie"]) == ["oro", CLAVE_ORO_OFICIAL, "plata", "btc"]
    assert tabla.loc[tabla["serie"] == CLAVE_ORO_OFICIAL, "meses"].iloc[0] == "718"


def test_ratios_conserva_la_ficha_del_oro_oficial():
    previas = pd.DataFrame(
        [{c: "" for c in COLUMNAS_SERIES_INFO} | {"serie": CLAVE_ORO_OFICIAL, "nombre": "ficha previa", "publicada": "sí", "meses": "718"}],
        columns=COLUMNAS_SERIES_INFO,
    )
    conservadas = ratios.fichas_conservadas(previas)
    assert [f["serie"] for f in conservadas] == [CLAVE_ORO_OFICIAL]
    assert conservadas[0]["nombre"] == "ficha previa"
    assert ratios.fichas_conservadas(None) == []


def test_la_serie_publicada_es_la_que_dan_los_tramos(tmp_path):
    """A-D0-30: oro_precio_oficial.csv se recalcula desde configuracion.py, byte a byte."""
    ruta = tmp_path / "o.csv"
    escribir_csv_determinista(oo.construir_serie(), ruta, COLUMNAS_ORO_OFICIAL, FORMATO_RATIOS)
    assert ruta.read_bytes().replace(b"\r\n", b"\n") == ARCHIVO_ORO_OFICIAL.read_bytes().replace(b"\r\n", b"\n")
