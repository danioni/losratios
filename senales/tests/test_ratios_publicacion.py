"""Qué se publica y qué no (A-R0-14), y los contrastes que hacen de gate (A-R0-12)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from senales import bitacora, configuracion, ratios
from senales.configuracion import (
    ANCLA_LBMA_ORO,
    ANCLA_LBMA_PLATA,
    BANDAS_LBMA,
    COLUMNAS_INTERNO,
    COLUMNAS_PRECIOS,
    CONTRASTE_BTC,
    CONTRASTE_NASDAQ,
    CONTRASTE_SP500,
    NO_MEDIDO_PERMISO,
    PARES,
    SERIES_PRECIO,
    AnclaMensual,
)
from senales.ratios import (
    EntradaRatios,
    calcular_pares,
    contrastar,
    estado_del_par,
    par_publicable,
    promedio_mensual,
    tabla_interna,
    tabla_pares,
    tabla_precios,
    tabla_ratios,
    verificar_ancla,
    verificar_bandas,
)
from tests.datos_ratios import diaria_habil

MESES = pd.DatetimeIndex(
    [pd.Timestamp(m + "-01") for m in ("2025-04", "2025-05", "2025-06", "2025-07")], name="mes"
)


@pytest.fixture
def precios() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "oro": [3200.0, 3300.0, 3350.0, 3340.0],
            "plata": [32.0, 33.0, 36.0, 37.5],
            "btc": [90000.0, 100000.0, 105000.0, float("nan")],
            "sp500": [5400.0, 5800.0, 6000.0, 6300.0],
            "nasdaq": [16500.0, 18800.0, 19700.0, 20800.0],
        },
        index=MESES,
    )


# --- Regla de publicación ----------------------------------------------------


def test_se_publican_oro_plata_y_btc_y_no_los_indices():
    publicables = {serie.clave for serie in SERIES_PRECIO if serie.publicable}
    assert publicables == {"oro", "plata", "btc"}


def test_los_tres_pares_con_indices_no_se_publican():
    publicados = {par.clave for par in PARES if par_publicable(par)}
    assert publicados == {"oro_plata", "btc_oro"}


def test_el_texto_de_no_medido_es_el_acordado():
    assert NO_MEDIDO_PERMISO == "NO MEDIDO: pendiente de permiso del dueño del índice"
    for par in PARES:
        if "sp500" in (par.numerador, par.denominador):
            assert estado_del_par(par) == NO_MEDIDO_PERMISO


def test_oro_plata_hereda_que_la_plata_es_una_estimacion():
    """A-R0-8: un ratio no es más firme que su lado más débil."""
    estados = {par.clave: estado_del_par(par) for par in PARES}
    assert estados["oro_plata"] == "estimación"
    assert estados["btc_oro"] == "dato"


def test_btc_se_usa_desde_2013_y_las_demas_series_desde_que_existen():
    desde = {serie.clave: serie.desde for serie in SERIES_PRECIO}
    assert desde == {"oro": None, "plata": None, "btc": "2013-01", "sp500": None, "nasdaq": None}


def test_los_cinco_pares_se_calculan_aunque_no_se_publiquen(precios):
    pares = calcular_pares(precios)
    assert list(pares.columns) == [par.clave for par in PARES]
    assert pares.loc[MESES[0], "oro_sp500"] == pytest.approx(3200.0 / 5400.0)
    assert pares.loc[MESES[0], "nasdaq_sp500"] == pytest.approx(16500.0 / 5400.0)


def test_un_par_al_que_le_falta_un_lado_queda_vacio(precios):
    pares = calcular_pares(precios)
    assert pd.isna(pares.loc[MESES[3], "btc_oro"])
    assert pd.notna(pares.loc[MESES[3], "oro_plata"])


def test_los_ratios_publicados_no_traen_ningun_par_con_indices(precios):
    tabla = tabla_ratios(calcular_pares(precios))
    assert set(tabla["par"]) == {"oro_plata", "btc_oro"}
    assert set(tabla["estado"]) == {"estimación", "dato"}
    assert tabla["valor"].notna().all()
    assert len(tabla) == 4 + 3


def test_los_precios_publicados_no_traen_ninguna_columna_de_indices(precios):
    tabla = tabla_precios(precios)
    assert list(tabla.columns) == COLUMNAS_PRECIOS
    assert not any("sp500" in columna or "nasdaq" in columna for columna in tabla.columns)


def test_la_tabla_de_pares_muestra_los_cinco_y_dice_cuales_no_se_miden(precios):
    tabla = tabla_pares(calcular_pares(precios)).set_index("par")
    assert len(tabla) == 5
    assert tabla.loc["oro_sp500", "estado"] == NO_MEDIDO_PERMISO
    assert tabla.loc["oro_sp500", "publicado"] == "no"
    # El par existe y tiene historia: lo que falta es el permiso, no el cálculo.
    assert tabla.loc["oro_sp500", "meses"] == 4
    assert tabla.loc["btc_oro", "ultimo_mes"] == "2025-06"


def test_lo_que_no_se_publica_va_a_la_tabla_interna(precios):
    tabla = tabla_interna(precios, calcular_pares(precios))
    assert list(tabla.columns) == COLUMNAS_INTERNO
    assert tabla.loc[0, "sp500"] == 5400.0


def test_el_quiebre_del_oro_va_declarado_fila_por_fila(precios):
    """A-R0-7: junio de 2025 es el primer mes del oro 'spot'."""
    tabla = tabla_precios(precios).set_index("mes")
    assert tabla.loc["2025-05", "oro_definicion"] == "fixing de la tarde de Londres"
    assert tabla.loc["2025-06", "oro_definicion"] == "spot"


def test_la_plata_lleva_su_estado_a_la_vista(precios):
    tabla = tabla_precios(precios)
    assert set(tabla["plata_estado"]) == {"estimación"}


# --- Contrastes --------------------------------------------------------------


def _mensual(valores: list[float], primer_mes: str = "2025-01") -> pd.Series:
    indice = pd.date_range(primer_mes + "-01", periods=len(valores), freq="MS", name="mes")
    return pd.Series(valores, index=indice)


def test_un_contraste_dentro_de_la_tolerancia_cierra():
    serie = _mensual([100.0, 101.0, 102.0])
    resultado = contrastar(serie, serie * 1.003, CONTRASTE_SP500)
    assert resultado.ok
    assert resultado.meses == 3
    assert resultado.maxima_pct == pytest.approx(0.299, abs=0.001)
    assert "OK" in resultado.resumen()


def test_un_solo_mes_fuera_de_la_tolerancia_hace_fallar_el_contraste():
    serie = _mensual([100.0, 101.0, 102.0])
    referencia = serie.copy()
    referencia.iloc[1] *= 1.02
    resultado = contrastar(serie, referencia, CONTRASTE_SP500)
    assert not resultado.ok
    assert resultado.fuera and "2025-02" in resultado.fuera[0]
    assert "FALLA" in resultado.resumen()


def test_sin_meses_en_comun_no_hay_contraste_y_no_hay_gate():
    resultado = contrastar(_mensual([100.0], "2025-01"), _mensual([100.0], "2020-01"), CONTRASTE_SP500)
    assert not resultado.ok
    assert "ningún mes en común" in resultado.resumen()


def test_el_contraste_de_btc_empieza_donde_empieza_la_publicacion():
    """A-R0-10: antes de 2013 las dos fuentes no coinciden, y por eso no se publican."""
    serie = _mensual([10.0, 11.0, 12.0, 13.0], "2012-11")
    referencia = serie.copy()
    referencia.iloc[0] *= 1.09  # noviembre de 2012, fuera del contraste
    resultado = contrastar(serie, referencia, CONTRASTE_BTC)
    assert resultado.ok
    assert resultado.meses == 2


def test_un_cierre_de_fin_de_mes_no_pasa_por_promedio_mensual():
    """El error de convención que este gate existe para atrapar."""
    diaria = diaria_habil("2024-01-02", "2026-09-10", base=5000.0, pendiente=4.0)
    promedios, _ = promedio_mensual(diaria, dias_calendario=False)
    cierres = diaria.groupby(diaria.index.to_period("M")).last()
    cierres.index = cierres.index.to_timestamp()
    resultado = contrastar(cierres.loc[promedios.index], promedios, CONTRASTE_NASDAQ)
    assert not resultado.ok


def test_las_tolerancias_son_las_que_se_fijaron():
    """A-R0-12. Cambiarlas es cambiar un supuesto, no arreglar una corrida."""
    assert CONTRASTE_SP500.tolerancia_pct == 0.5
    assert CONTRASTE_NASDAQ.tolerancia_pct == 0.1
    assert CONTRASTE_BTC.tolerancia_pct == 2.0
    assert configuracion.TOLERANCIA_ANCLA_ORO_PCT == 0.5
    assert configuracion.TOLERANCIA_ANCLA_PLATA_PCT == 1.0


# --- Oro y plata -------------------------------------------------------------


def test_no_hay_ancla_de_lbma_inventada():
    """A-R0-16: el campo vacío es el dato. No poner un valor para llenarlo."""
    assert ANCLA_LBMA_ORO is None
    assert ANCLA_LBMA_PLATA is None


def test_sin_ancla_el_metal_se_reporta_como_no_medido(precios):
    ok, linea = verificar_ancla(precios["oro"], None, "Oro", 0.5)
    assert ok
    assert linea.startswith("NO MEDIDO (A-R0-16)")
    assert "0.50 %" in linea


def _ancla(valor: float, mes: str = "2025-05") -> AnclaMensual:
    return AnclaMensual(
        serie="oro",
        mes=mes,
        valor=valor,
        tolerancia_pct=0.5,
        fuente="un promedio de prueba",
        fuente_url="https://ejemplo.invalid/",
        fecha_lectura=date(2026, 10, 4),
    )


def test_con_ancla_el_metal_tiene_gate(precios):
    assert verificar_ancla(precios["oro"], _ancla(3310.0), "Oro", 0.5)[0]
    ok, linea = verificar_ancla(precios["oro"], _ancla(3400.0), "Oro", 0.5)
    assert not ok and linea.startswith("FALLA")


def test_un_ancla_cuyo_mes_no_esta_en_la_serie_falla(precios):
    ok, linea = verificar_ancla(precios["oro"], _ancla(3300.0, "1999-01"), "Oro", 0.5)
    assert not ok and "no está en la serie" in linea


def test_las_bandas_de_lbma_declaran_de_donde_salen():
    for banda in BANDAS_LBMA:
        assert banda.fuente_url.startswith("https://www.lbma.org.uk/")
        assert banda.minimo < banda.maximo
        assert banda.meses == ("2026-04", "2026-05", "2026-06")


def test_un_promedio_fuera_de_los_extremos_de_su_trimestre_falla():
    indice = pd.DatetimeIndex([pd.Timestamp(m + "-01") for m in ("2026-04", "2026-05", "2026-06")])
    dentro = pd.DataFrame({"oro": [4700.0, 4600.0, 4200.0], "plata": [76.0, 78.0, 67.0]}, index=indice)
    assert verificar_bandas(dentro, BANDAS_LBMA)[0]
    fuera = dentro.copy()
    fuera.loc[indice[2], "oro"] = 3900.0
    ok, lineas = verificar_bandas(fuera, BANDAS_LBMA)
    assert not ok
    assert any("FUERA" in linea and "2026-06" in linea for linea in lineas)


def test_una_banda_sin_dato_no_aprueba_ni_reprueba(precios):
    ok, lineas = verificar_bandas(precios, BANDAS_LBMA)
    assert ok
    assert all(linea.startswith("sin dato") for linea in lineas)


# --- Changelog ---------------------------------------------------------------


def _entrada(fecha: date, nota: str = "corrida de prueba") -> EntradaRatios:
    return EntradaRatios(
        fecha_corrida=fecha,
        descargas=["pink_sheet: https://ejemplo, sha256 abc"],
        series=["Oro: 1960-01 a 2026-09"],
        descartados=[],
        pares=["Oro / Plata: estimación"],
        agregados=["2026-09"],
        revisiones=[],
        contrastes=["OK - BTC"],
        metales=["NO MEDIDO (A-R0-16) - Oro"],
        notas=[nota],
    )


def test_la_entrada_de_ratios_convive_con_la_de_s2_del_mismo_dia(tmp_path):
    ruta = tmp_path / "CHANGELOG.md"
    ruta.write_text(
        bitacora.ENCABEZADO
        + "\n## Cambios de supuestos\n\n- una línea escrita a mano\n"
        + "\n## 2026-10-04\n\n- Rango de datos: la corrida de S2\n"
        + "\n## 2026-10-03\n\n- Rango de datos: otra corrida de S2\n",
        encoding="utf-8",
    )
    assert bitacora.actualizar_changelog(ruta, _entrada(date(2026, 10, 4))) is True
    texto = ruta.read_text(encoding="utf-8")
    assert texto.count("## 2026-10-04 · ratios") == 1
    assert "la corrida de S2" in texto and "otra corrida de S2" in texto
    assert "una línea escrita a mano" in texto
    # La sección escrita a mano sigue arriba; después, las corridas, la más reciente primero.
    assert texto.index("## Cambios de supuestos") < texto.index("## 2026-10-04 · ratios")
    assert texto.index("## 2026-10-04 · ratios") < texto.index("## 2026-10-03")


def test_dos_corridas_de_ratios_el_mismo_dia_dejan_una_sola_entrada(tmp_path):
    ruta = tmp_path / "CHANGELOG.md"
    bitacora.actualizar_changelog(ruta, _entrada(date(2026, 10, 4), "primera"))
    assert bitacora.actualizar_changelog(ruta, _entrada(date(2026, 10, 4), "primera")) is False
    bitacora.actualizar_changelog(ruta, _entrada(date(2026, 10, 4), "segunda"))
    texto = ruta.read_text(encoding="utf-8")
    assert texto.count("## 2026-10-04 · ratios") == 1
    assert "segunda" in texto and "primera" not in texto
