"""Qué se publica y qué no (A-R0-14), y los gates que lo deciden (A-R0-12, A-R0-16)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from senales import bitacora, configuracion, ratios
from senales.configuracion import (
    ANCLAS_USGS,
    BANDAS_LBMA,
    COLUMNAS_INTERNO,
    COLUMNAS_PRECIOS,
    CONTRASTE_BTC,
    CONTRASTE_NASDAQ,
    CONTRASTE_SP500,
    COLUMNAS_RATIOS,
    MINIMO_ANIOS_GATE,
    NO_MEDIDO_PERMISO,
    NO_MEDIDO_SIN_VALIDACION,
    PARES,
    SERIE_BTC,
    SERIE_ORO,
    SERIE_PLATA,
    SERIES_PRECIO,
    UMBRAL_ERROR_REDONDEO_PCT,
    AnclaAnual,
)
from senales.fuentes_fred import ErrorDeFuente
from senales.ratios import (
    EntradaRatios,
    apto_desde,
    calcular_pares,
    contrastar,
    error_redondeo_pct,
    errores_de_pares,
    estado_de_serie,
    estado_del_par,
    gate_anual,
    par_publicado,
    promedio_mensual,
    serie_publicada,
    tabla_interna,
    tabla_pares,
    tabla_precios,
    tabla_ratios,
    tabla_series,
    verificar_bandas,
    verificar_redondeo,
)
from tests.datos_ratios import diaria_habil

MESES = pd.DatetimeIndex(
    [pd.Timestamp(m + "-01") for m in ("2025-04", "2025-05", "2025-06", "2025-07")], name="mes"
)

# Todas las series con su validación cerrada, y los dos metales sin ella.
TODAS = {"oro", "plata", "btc", "sp500", "nasdaq"}
SIN_METALES = {"btc", "sp500", "nasdaq"}
PARES_POR_CLAVE = {par.clave: par for par in PARES}


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


# --- Regla de publicación: licencia y validación -----------------------------


def test_por_licencia_se_pueden_publicar_oro_plata_y_btc_y_no_los_indices():
    publicables = {serie.clave for serie in SERIES_PRECIO if serie.publicable}
    assert publicables == {"oro", "plata", "btc"}


def test_con_todo_validado_se_publican_dos_pares_y_tres_esperan_permiso():
    publicados = {par.clave for par in PARES if par_publicado(par, TODAS)}
    assert publicados == {"oro_plata", "btc_oro"}
    for par in PARES:
        if "sp500" in (par.numerador, par.denominador):
            assert estado_del_par(par, TODAS) == NO_MEDIDO_PERMISO


def test_los_textos_de_no_medido_son_los_acordados():
    assert NO_MEDIDO_PERMISO == "NO MEDIDO: pendiente de permiso del dueño del índice"
    assert NO_MEDIDO_SIN_VALIDACION == "NO MEDIDO: sin validación externa"


def test_ninguna_serie_se_publica_sin_validacion_externa():
    """La regla del README: sin caso de validación, no hay publicación."""
    por_clave = {serie.clave: serie for serie in SERIES_PRECIO}
    assert not serie_publicada(por_clave["oro"], SIN_METALES)
    assert estado_de_serie(por_clave["oro"], SIN_METALES) == NO_MEDIDO_SIN_VALIDACION
    assert serie_publicada(por_clave["btc"], SIN_METALES)
    # Ni con la validación cerrada se publica una serie sin permiso.
    assert not serie_publicada(por_clave["sp500"], TODAS)
    assert estado_de_serie(por_clave["sp500"], TODAS) == NO_MEDIDO_PERMISO


def test_sin_el_oro_validado_no_se_publica_ningun_par():
    """Oro/Plata y BTC/Oro llevan oro: si el oro no tiene gate, ninguno sale."""
    assert {par.clave for par in PARES if par_publicado(par, SIN_METALES)} == set()
    assert estado_del_par(PARES_POR_CLAVE["oro_plata"], SIN_METALES) == NO_MEDIDO_SIN_VALIDACION
    assert estado_del_par(PARES_POR_CLAVE["btc_oro"], SIN_METALES) == NO_MEDIDO_SIN_VALIDACION
    # Al que además le falta el permiso, lo que se dice es el permiso.
    assert estado_del_par(PARES_POR_CLAVE["oro_sp500"], SIN_METALES) == NO_MEDIDO_PERMISO


def test_con_el_oro_validado_y_la_plata_no_solo_sale_btc_oro():
    validadas = SIN_METALES | {"oro"}
    assert {par.clave for par in PARES if par_publicado(par, validadas)} == {"btc_oro"}
    assert estado_del_par(PARES_POR_CLAVE["oro_plata"], validadas) == NO_MEDIDO_SIN_VALIDACION


def test_oro_plata_hereda_que_la_plata_es_una_estimacion():
    """A-R0-8: un ratio no es más firme que su lado más débil."""
    assert estado_del_par(PARES_POR_CLAVE["oro_plata"], TODAS) == "estimación"
    assert estado_del_par(PARES_POR_CLAVE["btc_oro"], TODAS) == "dato"


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
    tabla = tabla_ratios(calcular_pares(precios), errores_de_pares(precios), TODAS)
    assert set(tabla["par"]) == {"oro_plata", "btc_oro"}
    assert set(tabla["estado"]) == {"estimación", "dato"}
    assert tabla["valor"].notna().all()
    assert len(tabla) == 4 + 3


def test_sin_validacion_los_ratios_publicados_quedan_vacios(precios):
    tabla = tabla_ratios(calcular_pares(precios), errores_de_pares(precios), SIN_METALES)
    assert tabla.empty
    assert list(tabla.columns) == COLUMNAS_RATIOS


def test_los_precios_publicados_no_traen_ninguna_columna_de_indices(precios):
    tabla = tabla_precios(precios, TODAS)
    assert list(tabla.columns) == COLUMNAS_PRECIOS
    assert not any("sp500" in columna or "nasdaq" in columna for columna in tabla.columns)


def test_sin_validacion_las_columnas_de_los_metales_quedan_vacias(precios):
    """Las columnas son las mismas; lo que no se publica no tiene valores."""
    tabla = tabla_precios(precios, SIN_METALES)
    assert list(tabla.columns) == COLUMNAS_PRECIOS
    assert tabla["oro_usd_oz"].isna().all() and tabla["plata_usd_oz"].isna().all()
    assert set(tabla["oro_definicion"]) == {""} and set(tabla["plata_estado"]) == {""}
    assert tabla["btc_usd"].notna().all()
    assert len(tabla) == 3  # solo los meses en que BTC tiene dato


def test_la_tabla_de_pares_muestra_los_cinco_y_dice_que_le_falta_a_cada_uno(precios):
    tabla = tabla_pares(calcular_pares(precios), errores_de_pares(precios), SIN_METALES).set_index("par")
    assert len(tabla) == 5
    assert tabla.loc["oro_sp500", "estado"] == NO_MEDIDO_PERMISO
    assert tabla.loc["oro_plata", "estado"] == NO_MEDIDO_SIN_VALIDACION
    assert set(tabla["publicado"]) == {"no"}
    # El par existe y tiene historia: lo que falta no es el cálculo.
    assert tabla.loc["oro_sp500", "meses"] == 4
    assert tabla.loc["btc_oro", "ultimo_mes"] == "2025-06"


def test_la_tabla_de_series_dice_estado_y_validacion_de_cada_una(precios):
    validaciones = {clave: f"validación de {clave}" for clave in TODAS}
    tabla = tabla_series(precios, SIN_METALES, validaciones).set_index("serie")
    assert dict(tabla["publicada"]) == {
        "oro": "no", "plata": "no", "btc": "sí", "sp500": "no", "nasdaq": "no",
    }
    assert tabla.loc["oro", "estado"] == NO_MEDIDO_SIN_VALIDACION
    assert tabla.loc["nasdaq", "estado"] == NO_MEDIDO_PERMISO
    assert tabla.loc["btc", "estado"] == "dato"
    assert tabla.loc["plata", "validacion"] == "validación de plata"
    assert "The World Bank" in tabla.loc["oro", "atribucion"]


def test_todo_lo_calculado_va_a_la_tabla_interna(precios):
    tabla = tabla_interna(precios, calcular_pares(precios))
    assert list(tabla.columns) == COLUMNAS_INTERNO
    assert tabla.loc[0, "sp500"] == 5400.0
    assert tabla.loc[0, "oro"] == 3200.0
    assert tabla.loc[0, "oro_plata"] == pytest.approx(100.0)


def test_el_quiebre_del_oro_va_declarado_fila_por_fila(precios):
    """A-R0-7: junio de 2025 es el primer mes del oro 'spot'."""
    tabla = tabla_precios(precios, TODAS).set_index("mes")
    assert tabla.loc["2025-05", "oro_definicion"] == "fixing de la tarde de Londres"
    assert tabla.loc["2025-06", "oro_definicion"] == "spot"


def test_la_plata_lleva_su_estado_a_la_vista(precios):
    tabla = tabla_precios(precios, TODAS)
    assert set(tabla["plata_estado"]) == {"estimación"}


# --- Contrastes mensuales ----------------------------------------------------


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


def test_el_resumen_de_un_indice_no_trae_ningun_nivel():
    """A-R0-12: fecha del peor mes, diferencia, mediana y n. Ni un valor del índice."""
    serie = _mensual([5400.25, 5800.5, 6000.75])
    for contraste in (CONTRASTE_SP500, CONTRASTE_NASDAQ):
        resumen = contrastar(serie, serie * 1.0004, contraste).resumen()
        assert "3 meses" in resumen and "mediana" in resumen and "2025-0" in resumen
        for nivel in ("5400", "5800", "6000", "5402", "5802", "6003"):
            assert nivel not in resumen


def test_el_resumen_de_btc_si_trae_los_dos_valores():
    serie = _mensual([90000.0, 100000.0], "2025-01")
    resumen = contrastar(serie, serie * 1.01, CONTRASTE_BTC).resumen()
    assert "90000.0000 contra 90900.0000" in resumen


def test_las_tolerancias_son_las_que_se_fijaron():
    """A-R0-12 y A-R0-16. Cambiarlas es cambiar un supuesto, no arreglar una corrida."""
    assert CONTRASTE_SP500.tolerancia_pct == 0.5
    assert CONTRASTE_NASDAQ.tolerancia_pct == 0.1
    assert CONTRASTE_BTC.tolerancia_pct == 2.0
    assert configuracion.TOLERANCIA_GATE_ORO_PCT == 0.5
    assert configuracion.TOLERANCIA_GATE_PLATA_PCT == 1.0
    assert MINIMO_ANIOS_GATE == 3


# --- Oro y plata: gate anual contra el USGS ----------------------------------


def _anual(valores_por_anio: dict[int, float]) -> pd.Series:
    """Doce meses planos por año."""
    indice = pd.DatetimeIndex(
        [pd.Timestamp(year=a, month=m, day=1) for a in valores_por_anio for m in range(1, 13)]
    )
    return pd.Series([v for v in valores_por_anio.values() for _ in range(12)], index=indice)


def _anclas(valores_por_anio: dict[int, float], serie: str = "oro") -> tuple[AnclaAnual, ...]:
    return tuple(
        AnclaAnual(serie, anio, valor, "de prueba", "https://ejemplo.invalid/", date(2026, 10, 4))
        for anio, valor in valores_por_anio.items()
    )


def test_las_anclas_del_usgs_declaran_de_donde_salen():
    """Como el H.4.1: una cifra sin procedencia no se puede auditar."""
    for ancla in ANCLAS_USGS:
        assert ancla.fuente_url.startswith("https://pubs.usgs.gov/periodicals/mcs2026/")
        assert "Mineral Commodity Summaries, February 2026" in ancla.fuente
        assert "Engelhard" in ancla.fuente
        assert ancla.fecha_lectura == date(2026, 10, 4)


def test_las_anclas_son_las_cifras_transcritas_y_solo_de_anios_cerrados():
    oro = {a.anio: a.valor for a in ANCLAS_USGS if a.serie == "oro"}
    plata = {a.anio: a.valor for a in ANCLAS_USGS if a.serie == "plata"}
    assert oro == {2021: 1801.0, 2022: 1802.0, 2023: 1945.0, 2024: 2388.0}
    assert plata == {2021: 25.23, 2022: 21.88, 2023: 23.54, 2024: 28.37}
    # El 2025 de esa edición está estimado con datos de enero a noviembre.
    assert 2025 not in oro and 2025 not in plata
    assert len(oro) >= MINIMO_ANIOS_GATE and len(plata) >= MINIMO_ANIOS_GATE


def test_el_gate_anual_cierra_cuando_cierran_todos_los_anios():
    mensual = _anual({2022: 1800.0, 2023: 1940.0, 2024: 2390.0})
    resultado = gate_anual(mensual, _anclas({2022: 1802.0, 2023: 1945.0, 2024: 2388.0}), "oro", 0.5)
    assert resultado.ok
    assert (resultado.anios, resultado.cerrados) == (3, 3)
    assert all(linea.startswith("OK") for linea in resultado.lineas)
    assert "cerró en 3 de 3 años" in resultado.validacion()


def test_un_solo_anio_fuera_hace_fallar_el_gate():
    """Tienen que cerrar todos, no la mayoría."""
    mensual = _anual({2022: 1800.0, 2023: 1940.0, 2024: 2420.0})
    resultado = gate_anual(mensual, _anclas({2022: 1802.0, 2023: 1945.0, 2024: 2388.0}), "oro", 0.5)
    assert not resultado.ok
    assert resultado.cerrados == 2
    assert any(linea.startswith("FALLA") and "2024" in linea for linea in resultado.lineas)
    assert "NO cerró" in resultado.validacion()


def test_con_menos_de_tres_anios_no_hay_gate():
    mensual = _anual({2023: 1945.0, 2024: 2388.0})
    resultado = gate_anual(mensual, _anclas({2023: 1945.0, 2024: 2388.0}), "oro", 0.5)
    assert not resultado.ok
    assert "necesita al menos 3" in resultado.resumen()


def test_un_anio_al_que_le_falta_un_mes_no_se_promedia():
    mensual = _anual({2022: 1802.0, 2023: 1945.0, 2024: 2388.0}).drop(pd.Timestamp("2023-07-01"))
    resultado = gate_anual(mensual, _anclas({2022: 1802.0, 2023: 1945.0, 2024: 2388.0}), "oro", 0.5)
    assert not resultado.ok
    assert any("11 de 12 meses" in linea for linea in resultado.lineas)


def test_el_gate_usa_el_promedio_de_los_doce_meses():
    indice = pd.DatetimeIndex([pd.Timestamp(year=a, month=m, day=1) for a in (2022, 2023, 2024) for m in range(1, 13)])
    # Cada año sube de 100 a 111: el promedio es 105.5, y diciembre, 111.
    mensual = pd.Series([100.0 + m for _ in range(3) for m in range(12)], index=indice)
    cierra = gate_anual(mensual, _anclas({2022: 105.5, 2023: 105.5, 2024: 105.5}), "oro", 0.5)
    no_cierra = gate_anual(mensual, _anclas({2022: 111.0, 2023: 111.0, 2024: 111.0}), "oro", 0.5)
    assert cierra.ok and not no_cierra.ok


def test_el_gate_de_un_metal_no_mira_las_anclas_del_otro():
    mensual = _anual({2022: 21.9, 2023: 23.5, 2024: 28.4})
    anclas = _anclas({2022: 1802.0, 2023: 1945.0, 2024: 2388.0}, "oro") + _anclas(
        {2022: 21.88, 2023: 23.54, 2024: 28.37}, "plata"
    )
    assert gate_anual(mensual, anclas, "plata", 1.0).ok


def test_las_bandas_de_lbma_declaran_de_donde_salen():
    for banda in BANDAS_LBMA:
        assert banda.fuente_url.startswith("https://www.lbma.org.uk/")
        assert banda.minimo < banda.maximo
        assert banda.meses == ("2026-04", "2026-05", "2026-06")


def test_un_promedio_fuera_de_los_extremos_de_su_trimestre_falla():
    indice = pd.DatetimeIndex([pd.Timestamp(m + "-01") for m in ("2026-04", "2026-05", "2026-06")])
    dentro = pd.DataFrame({"oro": [4700.0, 4600.0, 4200.0], "plata": [76.0, 78.0, 67.0]}, index=indice)
    assert verificar_bandas(dentro, BANDAS_LBMA)[0] == {"oro": True, "plata": True}
    fuera = dentro.copy()
    fuera.loc[indice[2], "oro"] = 3900.0
    resultado, lineas = verificar_bandas(fuera, BANDAS_LBMA)
    assert resultado == {"oro": False, "plata": True}
    assert any("FUERA" in linea and "2026-06" in linea for linea in lineas)


def test_una_banda_sin_dato_no_aprueba_ni_reprueba(precios):
    resultado, lineas = verificar_bandas(precios, BANDAS_LBMA)
    assert resultado == {"oro": True, "plata": True}
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
        metales=["OK - Oro: gate anual contra el USGS"],
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


def test_una_serie_que_deja_de_publicarse_es_un_hecho_y_no_ochocientas_revisiones():
    previa = pd.DataFrame({"fecha": MESES, "oro_usd_oz": [1.0, 2.0, 3.0, 4.0], "btc_usd": [5.0, 6.0, 7.0, 8.0]})
    nueva = previa.assign(oro_usd_oz=float("nan"))
    comparables, cambios = ratios._columnas_comparables(previa, nueva, ["oro_usd_oz", "btc_usd"], True)
    assert comparables == ["btc_usd"]
    assert cambios == ["oro_usd_oz: dejó de publicarse en esta corrida"]
    _, vuelta = ratios._columnas_comparables(nueva, previa, ["oro_usd_oz", "btc_usd"], True)
    assert vuelta == ["oro_usd_oz: empezó a publicarse en esta corrida"]
    # En la primera corrida no hay nada con qué comparar.
    assert ratios._columnas_comparables(None, previa, ["oro_usd_oz"], False) == (["oro_usd_oz"], [])


# --- A-R0-17: error máximo por redondeo --------------------------------------


def test_el_error_de_cada_metal_es_medio_paso_de_redondeo_sobre_el_valor():
    """0.5/oro y 0.05/plata, en porcentaje."""
    serie = _mensual([35.0, 1592.0, 4319.0])
    assert list(error_redondeo_pct(serie, SERIE_ORO)) == pytest.approx(
        [0.5 / 35.0 * 100, 0.5 / 1592.0 * 100, 0.5 / 4319.0 * 100]
    )
    plata = _mensual([0.9, 4.2, 64.6])
    assert list(error_redondeo_pct(plata, SERIE_PLATA)) == pytest.approx(
        [0.05 / 0.9 * 100, 0.05 / 4.2 * 100, 0.05 / 64.6 * 100]
    )


def test_una_fuente_que_no_redondea_no_aporta_error():
    assert SERIE_BTC.medio_paso_redondeo is None
    assert list(error_redondeo_pct(_mensual([15.6, 80473.08]), SERIE_BTC)) == [0.0, 0.0]


def test_el_error_del_ratio_es_la_suma_de_los_de_sus_dos_lados(precios):
    errores = errores_de_pares(precios)
    mes = MESES[0]  # oro 3200, plata 32
    assert errores.loc[mes, "oro_plata"] == pytest.approx(0.5 / 3200 * 100 + 0.05 / 32 * 100)
    # BTC no redondea: el error de BTC/Oro es solo el del oro.
    assert errores.loc[mes, "btc_oro"] == pytest.approx(0.5 / 3200 * 100)
    assert errores.loc[mes, "oro_sp500"] == pytest.approx(0.5 / 3200 * 100)
    assert errores.loc[mes, "nasdaq_sp500"] == 0.0


def test_el_umbral_para_metricas_es_el_que_se_fijo():
    """A-R0-17. Es un supuesto: cambiarlo cambia qué meses entran a un percentil."""
    assert UMBRAL_ERROR_REDONDEO_PCT == 0.5


def _con_plata(valores: list[float]) -> pd.DataFrame:
    indice = pd.date_range("2008-07-01", periods=len(valores), freq="MS", name="mes")
    n = len(valores)
    return pd.DataFrame(
        {"oro": [900.0] * n, "plata": valores, "btc": [float("nan")] * n,
         "sp500": [1000.0] * n, "nasdaq": [2000.0] * n},
        index=indice,
    )


def test_cada_fila_del_ratio_dice_su_error_y_si_es_apta_para_metricas():
    # Con el oro a 900 (0.056 %), la plata tiene que estar a 11.3 o más para que
    # la suma no pase de 0.5 %.
    precios = _con_plata([18.0, 9.9, 11.2, 11.3, 12.0])
    tabla = tabla_ratios(calcular_pares(precios), errores_de_pares(precios), TODAS)
    oro_plata = tabla[tabla["par"] == "oro_plata"].set_index("mes")
    # Julio cumple el umbral, pero queda antes de la interrupción: no es apto.
    assert list(oro_plata["apto_metricas"]) == ["no", "no", "no", "sí", "sí"]
    assert oro_plata.loc["2008-07", "error_redondeo_pct"] < UMBRAL_ERROR_REDONDEO_PCT
    assert oro_plata.loc["2008-08", "error_redondeo_pct"] == pytest.approx(0.5606, abs=1e-4)
    # Un mes no apto se publica igual, con su valor y su error a la vista.
    assert oro_plata.loc["2008-08", "valor"] == pytest.approx(900.0 / 9.9)


def test_apto_desde_es_el_primer_mes_del_tramo_final_sin_interrupcion():
    precios = _con_plata([18.0, 9.9, 11.2, 11.3, 12.0])
    errores = errores_de_pares(precios)
    assert apto_desde(errores["oro_plata"]) == "2008-10"
    tabla = tabla_pares(calcular_pares(precios), errores, TODAS).set_index("par")
    assert tabla.loc["oro_plata", "apto_desde"] == "2008-10"
    # Dos meses aptos. Julio cumple el umbral, pero queda antes de la interrupción:
    # elegir meses sueltos por el precio de la plata sesgaría cualquier percentil.
    assert tabla.loc["oro_plata", "meses_aptos"] == 2
    assert tabla.loc["oro_sp500", "apto_desde"] == "2008-07"


def test_si_el_ultimo_mes_no_es_apto_no_hay_tramo_final():
    errores = errores_de_pares(_con_plata([18.0, 12.0, 9.0]))
    assert apto_desde(errores["oro_plata"]) == ""
    assert not ratios.meses_aptos(errores["oro_plata"]).any()


def test_los_precios_publicados_llevan_el_error_de_cada_metal(precios):
    tabla = tabla_precios(precios, TODAS).set_index("mes")
    assert tabla.loc["2025-04", "oro_error_redondeo_pct"] == pytest.approx(0.0156, abs=1e-4)
    assert tabla.loc["2025-04", "plata_error_redondeo_pct"] == pytest.approx(0.1563, abs=1e-4)
    sin = tabla_precios(precios, SIN_METALES)
    assert sin["oro_error_redondeo_pct"].isna().all() and sin["plata_error_redondeo_pct"].isna().all()


def test_si_la_fuente_cambia_de_precision_la_corrida_se_detiene():
    """El error que se publica sale del paso de redondeo: si cambia, deja de ser cierto."""
    verificar_redondeo(_mensual([35.0, 1592.0]), SERIE_ORO)
    verificar_redondeo(_mensual([0.9, 14.9, 64.6]), SERIE_PLATA)
    verificar_redondeo(_mensual([15.618, 80473.0792]), SERIE_BTC)
    with pytest.raises(ErrorDeFuente, match="cambió la precisión"):
        verificar_redondeo(_mensual([35.0, 1591.93]), SERIE_ORO)
    with pytest.raises(ErrorDeFuente, match="cambió la precisión"):
        verificar_redondeo(_mensual([14.9, 14.884]), SERIE_PLATA)


def _revision(mes: str, columna: str, anterior: float, nuevo: float) -> bitacora.Revision:
    return bitacora.Revision(pd.Timestamp(mes + "-01"), columna, anterior, nuevo)


def test_pocas_revisiones_se_listan_una_por_una():
    revisiones = [_revision("2026-08", "oro_usd_oz", 4400.0, 4410.0)]
    assert ratios.resumir_revisiones(revisiones) == ["2026-08-01 | oro_usd_oz: 4400.000 -> 4410.000 (10.000)"]


def test_un_cambio_masivo_se_resume_por_columna():
    """Cambiar de edición de la fuente mueve cientos de meses: no es una línea por mes."""
    meses = pd.date_range("1960-01-01", periods=60, freq="MS")
    revisiones = [_revision(f"{m:%Y-%m}", "oro_usd_oz", 35.0, 35.2) for m in meses]
    revisiones += [_revision(f"{m:%Y-%m}", "plata_usd_oz", 0.9, 0.91) for m in meses[:-1]]
    revisiones.append(_revision("1964-12", "plata_usd_oz", 1.0, 1.3))
    lineas = ratios.resumir_revisiones(revisiones)
    assert len(lineas) == 3
    assert lineas[0].startswith("oro_usd_oz: 60 meses cambiaron")
    assert "plata_usd_oz: 60 meses cambiaron" in lineas[1]
    assert "30.000 % en 1964-12 (1.0000 -> 1.3000)" in lineas[1]
    assert "120 cambios" in lineas[2] and "cambio de método" in lineas[2]
