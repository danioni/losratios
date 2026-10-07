"""El dinero de EE.UU. antes de 1959: cotejo de las dos transcripciones, sumas, gates y fichas.

Ningún test toca la red. Los que usan la transcripción real leen los crudos
versionados en data/raw/transcripcion_junta_1892_1958/ y no escriben nada.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from senales import denominador, dinero_historico as dh
from senales.configuracion import (
    ANCLAS_HSUS_1960,
    CLAVE_DINERO_1892_1946,
    CLAVE_DINERO_1947_1958,
    CLAVE_DINERO_1947_1958_SIN_AJUSTAR,
    COLUMNAS_D0_FICHAS,
    COLUMNAS_DINERO_HISTORICO,
    DIR_TRANSCRIPCION_JUNTA,
    NO_MEDIDO_SIN_AJUSTAR_1947_1958,
    VALOR_EN_DISPUTA,
)

# --- Tablas fabricadas, con filas reales para que las identidades cuadren ------------

TABLA_9 = (
    "fecha,total_depositos_y_efectivo,total_vista_y_efectivo,total_depositos,vista_ajustados,gobierno,"
    "plazo_total,plazo_comerciales,plazo_cajas,plazo_postal,efectivo,nota\n"
    "1892-06-30,5838,3895,4823,2880,14,1929,470,1459,,1015,\n"
    "1941-06-30,74153,45521,65949,37317,753,27879,15928,10648,1303,8204,plazo_comerciales:5;plazo_cajas:5\n"
)
CONTINUACION = (
    "fecha,money_stock_total,efectivo,vista_ajustados,plazo_total,plazo_comerciales,plazo_cajas,plazo_postal,gobierno,nota\n"
    "1941-06-30,45521,8204,37317,27879,15928,10648,1303,753,\n"
    "1942-06-30,52806,10936,41870,27320,15610,10395,1315,1837,\n"
)
TABLA_1_1_A = "mes,total,efectivo,vista,plazo_ajustados,nota\n1947-01,109.5,26.7,82.8,33.3,\n1947-02,109.7,26.7,83.0,33.5,\n"
TABLA_1_1_B = (
    "mes,total,efectivo,vista,plazo_ajustados,gobierno_vista,nota\n"
    "1947-01,111.9,26.7,85.2,33.2,2.6,\n"
    "1950-12,119.2,25.4,93.4,36.4,2.4,\n"  # errata de la fuente: 25.4 + 93.4 = 118.8
)
TEXTOS = {
    "tabla_9": TABLA_9,
    "continuacion_tabla_9": CONTINUACION,
    "tabla_1_1_A": TABLA_1_1_A,
    "tabla_1_1_B": TABLA_1_1_B,
}


def escribir_transcripcion(directorio: Path, cambios_b: dict[str, tuple[str, str]] | None = None, resoluciones: str = "") -> Path:
    """Escribe A y B iguales, salvo los reemplazos de texto que se pidan para B."""
    cambios_b = cambios_b or {}
    for tabla, (nombre_a, nombre_b, _) in dh.TABLAS.items():
        texto = TEXTOS[tabla]
        (directorio / nombre_a).write_text(texto, encoding="utf-8")
        if tabla in cambios_b:
            viejo, nuevo = cambios_b[tabla]
            assert viejo in texto
            texto = texto.replace(viejo, nuevo)
        (directorio / nombre_b).write_text(texto, encoding="utf-8")
    if resoluciones:
        (directorio / dh.ARCHIVO_RESOLUCIONES).write_text(
            "tabla,fecha,columna,valor_A,valor_B,valor_resuelto,como_se_resolvio\n" + resoluciones, encoding="utf-8"
        )
    return directorio


@pytest.fixture
def transcripcion(tmp_path) -> dh.Transcripcion:
    return dh.leer_transcripcion(escribir_transcripcion(tmp_path))


# --- Cotejo de las dos lecturas (A-D0-19) -------------------------------------------


def test_las_dos_lecturas_iguales_se_leen_y_se_cuentan(transcripcion):
    assert set(transcripcion.tablas) == set(dh.TABLAS)
    assert transcripcion.celdas_comparadas == 2 * 10 + 2 * 8 + 2 * 4 + 2 * 5
    assert transcripcion.resueltas == []
    tabla_9 = transcripcion.tablas["tabla_9"]
    assert tabla_9.loc["1892-06-30", "efectivo"] == 1015
    assert pd.isna(tabla_9.loc["1892-06-30", "plazo_postal"])
    assert tabla_9.loc["1941-06-30", "nota"] == "plazo_comerciales:5;plazo_cajas:5"


def test_una_celda_distinta_sin_resolucion_detiene(tmp_path):
    directorio = escribir_transcripcion(tmp_path, {"tabla_1_1_A": ("82.8", "82.6")})
    with pytest.raises(dh.ErrorDeTranscripcion, match="1947-01 vista: A='82.8' B='82.6'"):
        dh.leer_transcripcion(directorio)


def test_una_celda_distinta_con_resolucion_toma_el_valor_releido(tmp_path):
    directorio = escribir_transcripcion(
        tmp_path,
        {"tabla_1_1_A": ("82.8", "8?.8")},
        "tabla_1_1_A,1947-01,vista,82.8,8?.8,82.8,relectura ampliada\n",
    )
    leida = dh.leer_transcripcion(directorio)
    assert leida.tablas["tabla_1_1_A"].loc["1947-01", "vista"] == 82.8
    assert len(leida.resueltas) == 1 and "82.8" in leida.resueltas[0]


def test_una_resolucion_que_no_coincide_con_lo_leido_no_vale(tmp_path):
    directorio = escribir_transcripcion(
        tmp_path,
        {"tabla_1_1_A": ("82.8", "82.6")},
        "tabla_1_1_A,1947-01,vista,82.8,82.9,82.8,relectura\n",  # valor_B no es lo que leyó B
    )
    with pytest.raises(dh.ErrorDeTranscripcion):
        dh.leer_transcripcion(directorio)


def test_un_digito_ilegible_en_las_dos_lecturas_detiene(tmp_path):
    directorio = escribir_transcripcion(tmp_path)
    for nombre in ("A_tabla_1_1_A.csv", "B_tabla_1_1_A.csv"):
        ruta = directorio / nombre
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("82.8", "8?.8"), encoding="utf-8")
    with pytest.raises(dh.ErrorDeTranscripcion, match="ilegible"):
        dh.leer_transcripcion(directorio)


def test_filas_distintas_entre_a_y_b_detienen(tmp_path):
    directorio = escribir_transcripcion(tmp_path)
    ruta = directorio / "B_tabla_9.csv"
    ruta.write_text(ruta.read_text(encoding="utf-8").replace("1892-06-30", "1893-06-30"), encoding="utf-8")
    with pytest.raises(dh.ErrorDeTranscripcion, match="no tienen las mismas filas"):
        dh.leer_transcripcion(directorio)


# --- Sumas y superposición (A-D0-32) -------------------------------------------------


def test_las_identidades_impresas_cuadran_y_la_errata_queda_en_el_control(transcripcion):
    fallos = dh.verificar_sumas(transcripcion)
    assert fallos["tabla_9"] == [] and fallos["continuacion_tabla_9"] == [] and fallos["tabla_1_1_A"] == []
    assert len(fallos["tabla_1_1_B"]) == 1
    fallo = fallos["tabla_1_1_B"][0]
    assert (fallo.fecha, fallo.impreso, fallo.suma) == ("1950-12", 119.2, 118.8)
    assert dh.verificar_superposicion_1941(transcripcion) == []


def test_una_cifra_mal_transcrita_rompe_una_identidad_de_la_tabla_9(tmp_path):
    directorio = escribir_transcripcion(tmp_path)
    for nombre in ("A_tabla_9.csv", "B_tabla_9.csv"):
        ruta = directorio / nombre
        ruta.write_text(ruta.read_text(encoding="utf-8").replace(",470,", ",478,"), encoding="utf-8")
    fallos = dh.verificar_sumas(dh.leer_transcripcion(directorio))
    assert [f.identidad for f in fallos["tabla_9"]] == ["plazo_total = plazo_comerciales + plazo_cajas + plazo_postal"]


def test_la_tolerancia_de_la_tabla_1_1_es_el_redondeo(tmp_path):
    directorio = escribir_transcripcion(tmp_path)
    for nombre in ("A_tabla_1_1_A.csv", "B_tabla_1_1_A.csv"):
        ruta = directorio / nombre
        texto = ruta.read_text(encoding="utf-8").replace("109.5,26.7,82.8", "109.6,26.7,82.8")  # 0.1: redondeo
        texto = texto.replace("109.7,26.7,83.0", "109.9,26.7,83.0")  # 0.2: errata o error
        ruta.write_text(texto, encoding="utf-8")
    fallos = dh.verificar_sumas(dh.leer_transcripcion(directorio))
    assert [f.fecha for f in fallos["tabla_1_1_A"]] == ["1947-02"]


def test_la_continuacion_tiene_que_repetir_1941(tmp_path):
    directorio = escribir_transcripcion(tmp_path)
    for nombre in ("A_continuacion_tabla_9.csv", "B_continuacion_tabla_9.csv"):
        ruta = directorio / nombre
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("1941-06-30,45521", "1941-06-30,45522"), encoding="utf-8")
    fallas = dh.verificar_superposicion_1941(dh.leer_transcripcion(directorio))
    assert fallas and fallas[0].startswith("1941-06-30 money_stock_total")


# --- Construcción de las series ----------------------------------------------------


def test_las_fechas_de_balance_salen_de_la_tabla_9_y_de_su_continuacion(transcripcion):
    series = dh.construir_series(transcripcion, dh.verificar_sumas(transcripcion))
    historica = series[CLAVE_DINERO_1892_1946]
    assert list(historica.columns) == COLUMNAS_DINERO_HISTORICO
    totales = dh.total_de(historica)
    assert list(totales.index) == ["1892-06-30", "1941-06-30", "1942-06-30"]
    assert totales["1892-06-30"] == 1015 + 2880 + 470
    assert totales["1942-06-30"] == 10936 + 41870 + 15610
    fila_1941 = historica.loc[historica["fecha"] == "1941-06-30"].set_index("componente")
    assert "Tabla 9, p. 35" in fila_1941.loc["total", "cita"]
    assert fila_1941.loc["plazo_comerciales", "nota"].startswith("nota 5 de la Tabla 9: excluye")
    assert fila_1941.loc["total", "nota"] == fila_1941.loc["plazo_comerciales", "nota"]
    assert fila_1941.loc["efectivo", "nota"] == "" and fila_1941.loc["vista_ajustados", "nota"] == ""
    fila_1942 = historica.loc[historica["fecha"] == "1942-06-30"]
    assert fila_1942["cita"].str.contains("Sección 1, p. 5").all()
    assert (historica["mes"] == historica["fecha"].str[:7]).all()


def test_el_tramo_mensual_suma_money_stock_y_plazo_y_marca_la_errata(transcripcion):
    fallos = dh.verificar_sumas(transcripcion)
    series = dh.construir_series(transcripcion, fallos)
    ajustada = series[CLAVE_DINERO_1947_1958].set_index(["mes", "componente"])
    assert ajustada.loc[("1947-01", "total"), "valor"] == pytest.approx(142.8)
    assert ajustada.loc[("1947-01", "money_stock"), "valor"] == pytest.approx(109.5)
    assert (series[CLAVE_DINERO_1947_1958]["control"] == "").all()
    sin_ajustar = series[CLAVE_DINERO_1947_1958_SIN_AJUSTAR].set_index(["mes", "componente"])
    assert sin_ajustar.loc[("1950-12", "total"), "valor"] == pytest.approx(119.2 + 36.4)
    assert sin_ajustar.loc[("1950-12", "total"), "control"].startswith(VALOR_EN_DISPUTA)
    assert sin_ajustar.loc[("1947-01", "total"), "control"] == ""
    assert (series[CLAVE_DINERO_1947_1958]["fecha"] == "").all()


# --- Gates contra la segunda publicación ---------------------------------------------


def test_las_anclas_del_censo_cierran_con_igualdad(transcripcion, monkeypatch):
    anclas = tuple(a for a in ANCLAS_HSUS_1960 if a.fecha in ("1892-06-30", "1941-06-30", "1942-06-30"))
    monkeypatch.setattr(dh, "ANCLAS_HSUS_1960", anclas)
    validacion = dh.validar_anclas_hsus(transcripcion)
    assert validacion.ok and validacion.comparados == 3 and validacion.cifras == 6 + 7 + 7
    assert "cerró en 3 fechas de balance (20 cifras)" in validacion.validacion()


def test_un_ancla_del_censo_distinta_no_cierra(transcripcion, monkeypatch):
    anclas = tuple(a for a in ANCLAS_HSUS_1960 if a.fecha in ("1892-06-30", "1941-06-30", "1942-06-30"))
    monkeypatch.setattr(dh, "ANCLAS_HSUS_1960", anclas)
    transcripcion.tablas["continuacion_tabla_9"].loc["1942-06-30", "efectivo"] = 10937
    validacion = dh.validar_anclas_hsus(transcripcion)
    assert not validacion.ok
    assert validacion.fuera == ["1942-06-30 efectivo: transcrito 10937, Censo 10936"]


def test_menos_de_tres_anclas_no_deciden(transcripcion, monkeypatch):
    monkeypatch.setattr(dh, "ANCLAS_HSUS_1960", tuple(a for a in ANCLAS_HSUS_1960 if a.fecha == "1892-06-30"))
    assert not dh.validar_anclas_hsus(transcripcion).ok


def test_el_contraste_del_nber_cierra_con_una_decima(transcripcion):
    series = dh.construir_series(transcripcion, dh.verificar_sumas(transcripcion))
    contraste = pd.Series({"1947-01": 142.7, "1947-02": 143.2, "1947-03": 143.9})
    validacion = dh.validar_nber(series[CLAVE_DINERO_1947_1958], contraste)
    assert validacion.comparados == 2 and validacion.fuera == []
    assert validacion.maxima == pytest.approx(0.1)
    assert not validacion.ok  # dos meses no llegan al mínimo de tres


def test_el_contraste_del_nber_no_cierra_con_dos_decimas(transcripcion):
    series = dh.construir_series(transcripcion, dh.verificar_sumas(transcripcion))
    contraste = pd.Series({"1947-01": 142.6, "1947-02": 143.2})
    validacion = dh.validar_nber(series[CLAVE_DINERO_1947_1958], contraste)
    assert validacion.fuera == ["1947-01 (142.8 contra 142.6)"]


def test_sin_contraste_no_hay_validacion(transcripcion):
    series = dh.construir_series(transcripcion, dh.verificar_sumas(transcripcion))
    validacion = dh.validar_nber(series[CLAVE_DINERO_1947_1958], None, "robots.txt")
    assert validacion.comparados == 0 and not validacion.ok
    assert validacion.validacion().startswith("sin validación externa")


def test_leer_contraste_fred_salta_los_huecos(tmp_path):
    ruta = tmp_path / "fred.csv"
    ruta.write_text("observation_date,M1444CUSM027SNBR\n1947-01-01,142.7\n1947-02-01,.\n1947-03-01,143.9\n", encoding="utf-8")
    serie = dh.leer_contraste_fred(ruta)
    assert serie.to_dict() == {"1947-01": 142.7, "1947-03": 143.9}
    ruta.write_text("observation_date,OTRA\n1947-01-01,1\n", encoding="utf-8")
    with pytest.raises(Exception, match="columnas inesperadas"):
        dh.leer_contraste_fred(ruta)


# --- Fichas ---------------------------------------------------------------------------


def _fichas_de_prueba(transcripcion, nber_ok: bool):
    fallos = dh.verificar_sumas(transcripcion)
    series = dh.construir_series(transcripcion, fallos)
    contraste = pd.Series({"1947-01": 142.8, "1947-02": 143.2 if nber_ok else 143.5})
    validaciones = {
        CLAVE_DINERO_1892_1946: dh.validar_anclas_hsus(transcripcion),
        CLAVE_DINERO_1947_1958: dh.validar_nber(series[CLAVE_DINERO_1947_1958], contraste),
    }
    validaciones[CLAVE_DINERO_1947_1958].minimo = 2
    return series, dh.fichas(series, validaciones, fallos), validaciones


def test_la_ficha_dice_que_se_publica_y_la_sin_ajustar_queda_no_medido(transcripcion, monkeypatch):
    monkeypatch.setattr(dh, "ANCLAS_HSUS_1960", tuple(a for a in ANCLAS_HSUS_1960 if a.fecha[:4] in ("1892", "1941", "1942")))
    _, filas, _ = _fichas_de_prueba(transcripcion, nber_ok=True)
    por_clave = {f["serie"]: f for f in filas}
    assert set(por_clave) == {CLAVE_DINERO_1892_1946, CLAVE_DINERO_1947_1958, CLAVE_DINERO_1947_1958_SIN_AJUSTAR}
    assert por_clave[CLAVE_DINERO_1892_1946]["publicada"] == "sí"
    assert por_clave[CLAVE_DINERO_1892_1946]["meses"] == 3
    assert por_clave[CLAVE_DINERO_1947_1958]["publicada"] == "sí"
    assert "1 mes en disputa" not in por_clave[CLAVE_DINERO_1947_1958]["validacion"]
    assert por_clave[CLAVE_DINERO_1947_1958_SIN_AJUSTAR]["publicada"] == "no"
    assert por_clave[CLAVE_DINERO_1947_1958_SIN_AJUSTAR]["estado"] == NO_MEDIDO_SIN_AJUSTAR_1947_1958
    assert "1 mes en disputa" in por_clave[CLAVE_DINERO_1947_1958_SIN_AJUSTAR]["validacion"]
    assert all(set(f) == set(COLUMNAS_D0_FICHAS) for f in filas)


def test_si_el_gate_del_nber_no_cierra_la_serie_queda_no_medido(transcripcion, monkeypatch):
    monkeypatch.setattr(dh, "ANCLAS_HSUS_1960", tuple(a for a in ANCLAS_HSUS_1960 if a.fecha[:4] in ("1892", "1941", "1942")))
    series, filas, validaciones = _fichas_de_prueba(transcripcion, nber_ok=False)
    ficha = next(f for f in filas if f["serie"] == CLAVE_DINERO_1947_1958)
    assert ficha["publicada"] == "no" and ficha["estado"].startswith("NO MEDIDO")
    publicadas = {clave for clave, v in validaciones.items() if v.ok}
    assert set(dh.publicar(series, publicadas)["serie"]) == {CLAVE_DINERO_1892_1946}


def test_actualizar_fichas_reemplaza_en_su_lugar_y_agrega_la_sin_ajustar(tmp_path):
    ruta = tmp_path / "serie_D0.csv"
    previas = pd.DataFrame(
        [
            {c: "" for c in COLUMNAS_D0_FICHAS} | {"serie": "m2_eeuu", "publicada": "sí", "meses": "812"},
            {c: "" for c in COLUMNAS_D0_FICHAS} | {"serie": CLAVE_DINERO_1892_1946, "publicada": "no", "meses": "0"},
            {c: "" for c in COLUMNAS_D0_FICHAS} | {"serie": CLAVE_DINERO_1947_1958, "publicada": "no", "meses": "0"},
            {c: "" for c in COLUMNAS_D0_FICHAS} | {"serie": "riqueza_total", "publicada": "no", "meses": "0"},
        ],
        columns=COLUMNAS_D0_FICHAS,
    )
    previas.to_csv(ruta, index=False, lineterminator="\n")
    nuevas = [
        {c: "" for c in COLUMNAS_D0_FICHAS} | {"serie": clave, "publicada": "sí", "meses": 5}
        for clave in (CLAVE_DINERO_1892_1946, CLAVE_DINERO_1947_1958, CLAVE_DINERO_1947_1958_SIN_AJUSTAR)
    ]
    dh.actualizar_fichas(ruta, nuevas)
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    assert list(tabla["serie"]) == [
        "m2_eeuu",
        CLAVE_DINERO_1892_1946,
        CLAVE_DINERO_1947_1958,
        CLAVE_DINERO_1947_1958_SIN_AJUSTAR,
        "riqueza_total",
    ]
    assert list(tabla["meses"]) == ["812", "5", "5", "5", "0"]
    dh.actualizar_fichas(ruta, nuevas)  # idempotente
    assert list(pd.read_csv(ruta, dtype=str)["serie"]) == list(tabla["serie"])


def test_denominador_conserva_las_fichas_del_tramo_historico(tmp_path):
    previas = pd.DataFrame(
        [
            {c: "" for c in COLUMNAS_D0_FICHAS}
            | {"serie": clave, "nombre": f"ficha de {clave}", "familia": "dinero", "publicada": "sí", "meses": "7"}
            for clave in (CLAVE_DINERO_1892_1946, CLAVE_DINERO_1947_1958, CLAVE_DINERO_1947_1958_SIN_AJUSTAR)
        ],
        columns=COLUMNAS_D0_FICHAS,
    )
    con_previas = denominador.tabla_fichas({}, {}, {}, previas).set_index("serie")
    assert con_previas.loc[CLAVE_DINERO_1892_1946, "publicada"] == "sí"
    assert con_previas.loc[CLAVE_DINERO_1947_1958_SIN_AJUSTAR, "nombre"] == f"ficha de {CLAVE_DINERO_1947_1958_SIN_AJUSTAR}"
    claves = list(con_previas.index)
    assert claves.index(CLAVE_DINERO_1947_1958_SIN_AJUSTAR) == claves.index(CLAVE_DINERO_1947_1958) + 1
    sin_previas = denominador.tabla_fichas({}, {}, {}, None).set_index("serie")
    assert sin_previas.loc[CLAVE_DINERO_1892_1946, "publicada"] == "no"
    assert sin_previas.loc[CLAVE_DINERO_1892_1946, "estado"].startswith("NO MEDIDO")
    assert CLAVE_DINERO_1947_1958_SIN_AJUSTAR not in sin_previas.index
    # Leída del CSV, una ficha conserva sus vacíos y sus enteros tal cual.
    ruta = tmp_path / "serie_D0.csv"
    previas.to_csv(ruta, index=False, lineterminator="\n")
    desde_csv = denominador.tabla_fichas({}, {}, {}, denominador._leer_fichas(ruta)).set_index("serie")
    assert desde_csv.loc[CLAVE_DINERO_1892_1946, "meses"] == "7"
    assert desde_csv.loc[CLAVE_DINERO_1892_1946, "quiebres"] == ""


# --- La transcripción real, versionada ------------------------------------------------


def test_la_transcripcion_versionada_cierra_sus_gates_sin_red():
    """Las dos lecturas reales coinciden salvo una celda resuelta; las sumas y las anclas cierran."""
    leida = dh.leer_transcripcion(DIR_TRANSCRIPCION_JUNTA)
    assert leida.celdas_comparadas == 69 * 10 + 12 * 8 + 144 * 4 + 144 * 5
    assert len(leida.resueltas) == 1 and leida.resueltas[0].startswith("tabla_1_1_B 1955-11 plazo_ajustados")
    assert len(leida.tablas["tabla_9"]) == 69 and len(leida.tablas["continuacion_tabla_9"]) == 12
    assert len(leida.tablas["tabla_1_1_A"]) == 144 and len(leida.tablas["tabla_1_1_B"]) == 144
    fallos = dh.verificar_sumas(leida)
    assert fallos["tabla_9"] == [] and fallos["continuacion_tabla_9"] == []
    assert [f.fecha for f in fallos["tabla_1_1_A"]] == ["1949-03"]  # errata impresa: efectivo 27.7
    assert [f.fecha for f in fallos["tabla_1_1_B"]] == ["1950-12"]  # errata impresa: total 119.2
    assert dh.verificar_superposicion_1941(leida) == []
    anclas = dh.validar_anclas_hsus(leida)
    assert anclas.ok and anclas.comparados == 9 and anclas.cifras == 61
    series = dh.construir_series(leida, fallos)
    assert len(dh.total_de(series[CLAVE_DINERO_1892_1946])) == 79
    assert len(dh.total_de(series[CLAVE_DINERO_1947_1958])) == 144
