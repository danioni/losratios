"""Fase N0: el calendario de BTC, los lectores, los gates y controles, las fichas y la corrida. Sin red."""

from __future__ import annotations

import json
from datetime import date

import pandas as pd
import pytest

from senales import fuentes_numerador as fn, numerador as nm
from senales.configuracion import (
    ARCHIVO_N0_DESCARGAS,
    BTC_MAXIMO,
    COLUMNAS_N0_FICHAS,
    COLUMNAS_N0_SERIES,
    CONTROL_DENTRO,
    CONTROL_DISPUTA,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    ESTADO_DATO,
    ESTADO_ESTIMACION,
    LECTURAS_BGS,
    LECTURAS_MCS,
    PENDIENTES_N0,
    SERIES_N0,
    TOLERANCIA_BGS_PCT,
    TOLERANCIA_BTC_CALENDARIO_PCT,
    LecturaBGS,
    LecturaMCS,
)
from senales.fuentes_fred import ErrorDeFuente

SAT = 100_000_000


# --- El calendario del protocolo (A-N0-2) ------------------------------------------


def test_el_subsidio_se_parte_en_dos_cada_210000_bloques_y_llega_a_cero():
    assert nm.subsidio_sat(0) == 50 * SAT
    assert nm.subsidio_sat(209_999) == 50 * SAT
    assert nm.subsidio_sat(210_000) == 25 * SAT
    assert nm.subsidio_sat(840_000) == int(3.125 * SAT)
    assert nm.subsidio_sat(64 * 210_000) == 0
    # La suma por tramos coincide con la suma bloque a bloque.
    assert nm.suma_subsidios_sat(1, 210_000) == 209_999 * 50 * SAT + 25 * SAT
    assert nm.suma_subsidios_sat(209_998, 210_001) == sum(nm.subsidio_sat(h) for h in range(209_998, 210_002))
    assert nm.suma_subsidios_sat(5, 4) == 0


def _diaria(desde: str, hasta: str, bloques: int, emision_por_bloque: float, oferta_inicial: float = 0.0) -> pd.DataFrame:
    fechas = pd.date_range(desde, hasta, freq="D")
    emision = [bloques * emision_por_bloque] * len(fechas)
    oferta = oferta_inicial + pd.Series(emision).cumsum()
    return pd.DataFrame({"bloques": bloques, "emision": emision, "oferta": oferta.values}, index=pd.DatetimeIndex(fechas, name="fecha"))


def test_construir_btc_suma_por_anio_completo_y_deja_el_anio_en_curso_a_la_fecha():
    diaria = _diaria("2009-01-01", "2010-03-15", bloques=100, emision_por_bloque=50.0)
    construccion = nm.construir_btc(diaria)
    assert list(construccion.anual.index) == [2009]  # 2010 no está completo
    fila = construccion.anual.loc[2009]
    assert fila["bloques"] == 365 * 100
    assert fila["calendario"] == pytest.approx(365 * 100 * 50.0)
    assert fila["observada"] == pytest.approx(365 * 100 * 50.0)
    assert fila["oferta_fin"] == pytest.approx(365 * 100 * 50.0)
    assert fila["calendario_acumulado"] == pytest.approx(365 * 100 * 50.0)  # bloques 1..N, sin el génesis
    assert construccion.fecha_ultima == pd.Timestamp("2010-03-15")
    assert construccion.altura_ultima == (365 + 74) * 100


def test_el_calendario_cambia_dentro_del_anio_del_halving():
    # 2100 bloques por día: el bloque 210000 cae el día 101.
    diaria = _diaria("2012-01-01", "2012-12-31", bloques=2100, emision_por_bloque=0.0)
    construccion = nm.construir_btc(diaria)
    esperado = nm.suma_subsidios_sat(1, 366 * 2100) / SAT
    assert construccion.anual.loc[2012, "calendario"] == pytest.approx(esperado)
    assert construccion.anual.loc[2012, "calendario"] < 366 * 2100 * 50


def test_el_gate_de_btc_exige_oferta_no_mayor_que_el_calendario_y_cercana():
    diaria = _diaria("2020-01-01", "2022-12-31", bloques=150, emision_por_bloque=50.0)  # alturas < 210000: 50 BTC
    construccion = nm.construir_btc(diaria)
    assert nm.validar_btc(construccion).ok
    # Más oferta que calendario: no cierra.
    torcida = nm.construir_btc(diaria.assign(oferta=diaria["oferta"] + 1.0))
    assert not nm.validar_btc(torcida).ok
    # Una oferta muy por debajo del calendario tampoco.
    corta = nm.construir_btc(diaria.assign(oferta=diaria["oferta"] * (1 - 2 * TOLERANCIA_BTC_CALENDARIO_PCT / 100)))
    validacion = nm.validar_btc(corta)
    assert not validacion.ok and "por debajo" in validacion.fuera[0]
    # Dos años no deciden.
    assert not nm.validar_btc(nm.construir_btc(diaria.loc[:"2021-12-31"])).ok


def test_interpretar_coin_metrics_exige_una_sola_pagina_y_dias_seguidos():
    base = {"asset": "btc", "BlkCnt": "10", "IssTotNtv": "500", "SplyCur": "500"}
    with pytest.raises(ErrorDeFuente, match="next_page_url"):
        fn.interpretar_coin_metrics_oferta({"data": [base | {"time": "2020-01-01T00:00:00Z"}], "next_page_url": "x"})
    with pytest.raises(ErrorDeFuente, match="faltan 1 días"):
        fn.interpretar_coin_metrics_oferta({"data": [base | {"time": "2020-01-01T00:00:00Z"}, base | {"time": "2020-01-03T00:00:00Z"}]})
    tabla = fn.interpretar_coin_metrics_oferta({"data": [base | {"time": "2020-01-01T00:00:00Z", "IssTotNtv": None}, base | {"time": "2020-01-02T00:00:00Z"}]})
    assert list(tabla["bloques"]) == [10, 10] and list(tabla["emision"]) == [0.0, 500.0]


# --- Oro y plata (A-N0-3, A-N0-4, A-N0-5) --------------------------------------------

FILAS_DS140 = [
    ("GOLD STATISTICS1",),
    ("U.S. GEOLOGICAL SURVEY",),
    ("[All values are in metric tons (t) gold content unless otherwise noted]",),
    ("Last modification: November 20, 2023",),
    ("Year", "Primary production", "World production"),
    ("1900", "120", "100"),
    ("1901", "120", "10"),
    ("1902", "122", "NA"),
    ("1903", "100", "12"),
]


def test_interpretar_ds140_lee_la_columna_mundial_y_exige_unidad_y_metal():
    ds140 = fn.interpretar_ds140(FILAS_DS140, "oro")
    assert ds140.produccion.to_dict() == {1900: 100.0, 1901: 10.0, 1903: 12.0}  # 1902 es un hueco
    assert ds140.modificado == "Last modification: November 20, 2023"
    with pytest.raises(ErrorDeFuente, match="esperaba la de SILVER"):
        fn.interpretar_ds140(FILAS_DS140, "plata")
    sin_unidad = [f for f in FILAS_DS140 if "metric tons" not in str(f[0])]
    with pytest.raises(ErrorDeFuente, match="metric tons"):
        fn.interpretar_ds140(sin_unidad, "oro")


def test_construir_metal_sigue_a_la_ds140_y_declara_las_revisiones_del_mcs():
    ds140 = fn.DS140(pd.Series({1900: 100.0, 1901: 10.0, 1902: 12.0}, dtype=float), "Last modification: x", "metric tons")
    lecturas = (
        LecturaMCS("oro", 1902, 11.0, False, 2004, "u", "s", 1, "c"),  # distinta de la DS140: revisión declarada
        LecturaMCS("oro", 1903, 13.0, True, 2004, "u", "s", 1, "c"),
        LecturaMCS("oro", 1903, 14.0, False, 2005, "u", "s", 1, "c"),
        LecturaMCS("oro", 1904, 15.0, True, 2005, "u", "s", 1, "c"),
    )
    serie = nm.construir_metal(ds140, "oro", lecturas)
    assert serie.produccion.to_dict() == {1900: 100.0, 1901: 10.0, 1902: 12.0, 1903: 14.0, 1904: 15.0}
    assert serie.estado[1903] == ESTADO_DATO and serie.estado[1904] == ESTADO_ESTIMACION
    assert "revisión declarada" in serie.notas[1902] and "revisión declarada" in serie.notas[1903]
    assert any("1902: se publica la DS140 (12)" in r for r in serie.revisiones)
    assert "estimado" in serie.cita[1904]


def test_la_cota_superior_es_la_produccion_sobre_lo_acumulado_hasta_el_anio_anterior():
    produccion = pd.Series({1900: 100.0, 1901: 10.0, 1902: 11.0}, dtype=float)
    cota = nm.cota_superior(produccion)
    assert cota.to_dict() == pytest.approx({1901: 10.0, 1902: 10.0})  # 10/100 y 11/110


def test_el_control_del_bgs_marca_y_no_decide():
    produccion = pd.Series({2020: 3050.0, 2021: 3120.0, 2022: 3160.0}, dtype=float)
    lecturas = (
        LecturaBGS("oro", 2020, 3_200_000, 1),
        LecturaBGS("oro", 2021, 3_200_000, 1),
        LecturaBGS("oro", 2022, 3_400_000, 1),  # 7.6 %: en disputa
    )
    control = nm.validar_bgs("oro", produccion, lecturas)
    assert control.clase == "control" and control.ok and control.comparados == 3
    assert control.en_disputa == ["2022"] and control.dentro == ["2020", "2021"]
    assert control.maxima > TOLERANCIA_BGS_PCT
    assert "en disputa" in control.validacion()


def test_las_lecturas_configuradas_tienen_cita_hash_y_los_dos_metales():
    assert {l.metal for l in LECTURAS_MCS} == {"oro", "plata"} == {l.metal for l in LECTURAS_BGS}
    assert all(len(l.sha256) == 64 and l.url.startswith("https://pubs.usgs.gov/") and l.cita for l in LECTURAS_MCS)
    for metal in ("oro", "plata"):
        anios = [(l.anio, l.estimado) for l in LECTURAS_MCS if l.metal == metal]
        assert len(anios) == len(set(anios))  # ninguna edición repite un año con la misma marca


# --- Z.1 (A-N0-7, A-N0-8, A-N0-9) --------------------------------------------------------

CSV_Z1 = (
    "date,FA893064105.Q,FA103164105.Q\n"
    "1945:Q4,ND,ND\n"
    "1946:Q4,1139,1018\n"
    "1951:Q4,2106,2107\n"
    "1952:Q1,100,10\n"
    "1952:Q2,200,20\n"
    "1952:Q3,300,30\n"
    "1952:Q4,400,40\n"
    "1953:Q1,500,50\n"
)


def test_interpretar_tabla_z1_y_los_flujos_anuales():
    tabla = fn.interpretar_tabla_z1(CSV_Z1, ("FA893064105", "FA103164105.Q"))
    assert list(tabla.columns) == ["FA893064105", "FA103164105"]
    assert pd.isna(tabla.loc["1945:Q4", "FA893064105"])
    flujos = nm.flujos_anuales_z1(tabla, "FA893064105")
    assert flujos.to_dict() == {1946: 1139.0, 1951: 2106.0, 1952: 250.0}  # 1953 incompleto; hasta 1951 dato anual
    saldos = nm.saldos_fin_de_anio_z1(tabla, "FA103164105")
    assert saldos.to_dict() == {1946: 1018.0, 1951: 2107.0, 1952: 40.0}
    with pytest.raises(ErrorDeFuente, match="no trae la serie"):
        fn.interpretar_tabla_z1(CSV_Z1, ("FA999999999",))
    with pytest.raises(ErrorDeFuente, match="'date'"):
        fn.interpretar_tabla_z1("x,y\n1,2\n", ("x",))


HTML_Z1 = """
<table>
<tr><th>Line</th><th></th><th>2024</th><th>2025</th><th>2025:Q3</th><th>2025:Q4</th><th>2026:Q1</th></tr>
<tr><td>1</td><td>Net issues</td><td>FA893064105</td><td>905.0</td><td>1,163.8</td><td>1160.8</td><td>1890.4</td><td>1847.9</td></tr>
<tr><td>2</td><td>Nonfinancial</td><td>FA103164105</td><td>-99.4</td><td>-264.4</td><td>n.a.</td><td>-264.4</td><td>205.1</td></tr>
</table>
"""


def test_interpretar_html_z1_ubica_las_columnas_por_su_encabezado():
    valores = fn.interpretar_html_z1(HTML_Z1)
    assert valores["FA893064105"] == {"2024": 905.0, "2025": 1163.8, "2025:Q3": 1160.8, "2025:Q4": 1890.4, "2026:Q1": 1847.9}
    assert valores["FA103164105"]["2025:Q3"] is None
    with pytest.raises(ErrorDeFuente):
        fn.interpretar_html_z1("<table><tr><td>nada</td></tr></table>")


def test_el_gate_de_transporte_del_z1_compara_trimestres_y_anuales():
    csv = "date,FA893064105.Q\n" + "".join(f"2024:Q{q},905000\n" for q in range(1, 5)) + "".join(f"2025:Q{q},{v}\n" for q, v in zip(range(1, 5), (904700, 699500, 1160800, 1890400))) + "2026:Q1,1847900\n"
    tabla = fn.interpretar_tabla_z1(csv, ("FA893064105",))
    html = {"FA893064105": {"2024": 905.0, "2025": 1163.8, "2025:Q3": 1160.8, "2025:Q4": 1890.4, "2026:Q1": 1847.9}}
    gate = nm.validar_z1_html("F51_1_t", tabla, html, ("FA893064105",))
    assert gate.ok and gate.comparados == 5 and gate.maxima < 0.05
    html["FA893064105"]["2025:Q4"] = 1890.6
    assert not nm.validar_z1_html("F51_1_t", tabla, html, ("FA893064105",)).ok
    assert not nm.validar_z1_html("F51_1_t", tabla, {}, ("FA893064105",)).ok


# --- Viviendas (A-N0-10, A-N0-11) -------------------------------------------------------

FILAS_HVS = [
    ("Table 7. Estimates of the Total Housing Inventory for the United States: 1965 to Present",),
    ("(Numbers in thousands)",),
    (None, 1978, 1979, "1979r1", 1980, "19861", "2025*"),
    ("All housing units……", 83496, 85061, 85735, 87739, 99318, 148086),
    ("..Vacant……", 8000, 8100, 8200, 8300, 9000, 15000),
    ("..Total occupied……", 75496, 76961, 77535, 79439, 90318, 133086),
    ("Source: U.S. Census Bureau, Current Population Survey/Housing Vacancy Survey, March 24, 2026.",),
    ("*Due to a lapse in federal funding ...",),
]


def test_etiquetas_de_anio_del_hvs():
    assert fn.etiqueta_anio_hvs(1979) == (1979, False, "")
    assert fn.etiqueta_anio_hvs("1979r1") == (1979, True, "")
    assert fn.etiqueta_anio_hvs("19861") == (1986, False, "1")
    assert fn.etiqueta_anio_hvs("2025*") == (2025, False, "*")
    assert fn.etiqueta_anio_hvs("2002r") == (2002, True, "")
    assert fn.etiqueta_anio_hvs("All housing units") is None
    assert fn.etiqueta_anio_hvs(83496) is None


def test_interpretar_hvs_separa_la_base_revisada_y_la_tasa_la_usa_como_denominador():
    tabla = fn.interpretar_hvs(FILAS_HVS)
    assert tabla.total == {1978: 83496.0, 1979: 85061.0, 1980: 87739.0, 1986: 99318.0, 2025: 148086.0}
    assert tabla.revisados == {1979: 85735.0}
    assert tabla.notas_por_anio == {1986: "1", 2025: "*"}
    assert tabla.fuente.startswith("Source:")
    tasa = nm.crecimiento(pd.Series(tabla.total), tabla.revisados)
    assert tasa[1979] == pytest.approx((85061 / 83496 - 1) * 100)
    assert tasa[1980] == pytest.approx((87739 / 85735 - 1) * 100)  # sobre la base revisada
    assert 1986 not in tasa.index  # 1985 no está


def test_el_gate_de_sumas_del_hvs_cierra_al_redondeo_y_falla_si_no():
    gate = nm.validar_hvs_sumas("viviendas_eeuu_parque_hvs_miles", fn.interpretar_hvs(FILAS_HVS))
    assert gate.ok and gate.comparados == 6 and gate.maxima == 0
    rotas = [list(f) for f in FILAS_HVS]
    rotas[4][2] = 8105  # vacantes de 1979 pasan a 8105: la suma se va 5 mil
    gate = nm.validar_hvs_sumas("viviendas_eeuu_parque_hvs_miles", fn.interpretar_hvs([tuple(f) for f in rotas]))
    assert not gate.ok and gate.fuera == ["1979: 85061 contra 8105 + 76961"]


FILAS_POPEST = [
    ("Annual Estimates of Housing Units for the United States, Regions, States, and the District of Columbia: April 1, 2020 to July 1, 2025",),
    ("Geographic Area", "April 1, 2020 Estimates Base", "Housing Unit Estimate (as of July 1)"),
    (None, None, 2020, 2021, 2022),
    ("United States", 140498736, 140817690, 142193055, 143831409),
    (".Alabama", 1, 2, 3, 4),
    ("Release Date: May 2026",),
]


def test_interpretar_popest_y_el_control_contra_la_tabla_7a():
    popest = fn.interpretar_popest(FILAS_POPEST)
    assert popest.serie.to_dict() == {2020: 140817690.0, 2021: 142193055.0, 2022: 143831409.0}
    assert popest.base == 140498736.0 and popest.publicado == "Release Date: May 2026"
    tabla7a = fn.interpretar_hvs([
        ("Table 7a. Estimates ...",),
        ("Revised", 2020, 2021, 2022),
        ("All housing units", 140770, 142163, 145000),
        ("..Vacant", 14886, 15373, 15111),
        ("..Total occupied", 125884, 126790, 129889),
    ])
    control = nm.validar_popest("viviendas_eeuu_parque_hvs_7a_miles", tabla7a, popest)
    assert control.clase == "control" and control.comparados == 3
    assert control.dentro == ["2020", "2021"] and control.en_disputa == ["2022"]  # 2022 difiere 0.8 %


def test_el_control_de_fred_rige_hasta_la_ultima_vintage_cerrada():
    tabla7a = fn.interpretar_hvs([
        ("Table 7a. Estimates ...",),
        ("Revised", 2018, 2019, 2020),
        ("All housing units", 138347, 139511, 140770),
        ("..Vacant", 1, 1, 1),
        ("..Total occupied", 138346, 139510, 140769),
    ])
    fred = pd.Series(
        {pd.Timestamp(f"{a}-{m:02d}-01"): v for a, valores in ((2018, (138200, 138300, 138400, 138500)), (2019, (139069, 139360, 139655, 139961)), (2020, (140266, 140603, 140925, 141265))) for m, v in zip((1, 4, 7, 10), valores)},
        dtype=float,
    )
    control = nm.validar_hvs_fred("viviendas_eeuu_parque_hvs_7a_miles", tabla7a, fred)
    assert control.clase == "control" and control.comparados == 2  # 2020 no se compara
    assert control.en_disputa == ["2018"] and "2020" in control.nota


# --- Fichas, publicación y nombres (A-N0-1, A-N0-13) --------------------------------------


def test_cada_serie_dice_que_mide_y_ningun_nombre_dice_global():
    claves = [s.clave for s in SERIES_N0]
    assert len(claves) == len(set(claves))
    for serie in SERIES_N0:
        assert serie.mide and serie.unidad and serie.convencion and serie.supuestos
        assert "global" not in serie.nombre.lower()
        if serie.clave.startswith(("acciones_", "deuda_", "viviendas_")):
            assert "de EE.UU." in serie.nombre
    assert {p.clave for p in PENDIENTES_N0} & set(claves) == set()
    assert any(p.clave == "deuda_eeuu_elasticidad_oferta" for p in PENDIENTES_N0)


def test_estado_de_serie_exige_crudo_y_gate():
    construido = nm.Construido(motivos={"censo_hvs_tabla7": "sin copia"})
    serie_hvs = next(s for s in SERIES_N0 if s.clave == "viviendas_eeuu_parque_hvs_miles")
    publicada, estado = nm.estado_de_serie(serie_hvs, construido, {})
    assert not publicada and estado.startswith("NO MEDIDO: sin crudo")
    serie_btc = next(s for s in SERIES_N0 if s.clave == "btc_oferta_fin_de_anio_btc")
    assert nm.estado_de_serie(serie_btc, nm.Construido(), {}) == (False, "NO MEDIDO: sin validación externa")
    gate = nm.ValidacionN0("btc", "x", "y", 3, [], 0.0)
    assert nm.estado_de_serie(serie_btc, nm.Construido(), {"btc": gate}) == (True, ESTADO_DATO)
    serie_elasticidad = next(s for s in SERIES_N0 if s.clave == "btc_elasticidad_oferta")
    assert nm.estado_de_serie(serie_elasticidad, nm.Construido(), {}) == (True, ESTADO_DATO)


def test_la_fila_de_elasticidad_de_btc_es_cero_por_construccion():
    fila = nm.fila_elasticidad_btc()
    assert fila["valor"] == 0.0 and fila["estado"] == ESTADO_DATO and "GetBlockSubsidy" in fila["cita"]


# --- La corrida de punta a punta, con los crudos del repositorio -------------------------


def _fecha_de_los_crudos() -> str:
    fechas = sorted(r.stem[-10:] for r in DIR_CRUDO.glob("coin_metrics_btc_oferta_*.json"))
    assert fechas, "no hay crudos de Coin Metrics en data/raw"
    return fechas[-1]


def test_la_corrida_es_idempotente_y_no_toca_la_red(tmp_path, monkeypatch):
    """Dos corridas seguidas sobre los mismos crudos versionados dejan los mismos bytes. Ningún pedido sale.

    Los contrastes (el HTML del Z.1, FRED) no viajan con el repositorio y el
    pipeline los bajaría si faltan: aquí se desactivan y el directorio privado
    apunta a uno vacío, para que el test dé lo mismo en cualquier máquina. Las
    series que dependen de un gate de transporte quedan entonces NO MEDIDO.
    """
    fecha = date.fromisoformat(_fecha_de_los_crudos())
    salidas = tmp_path / "series"
    salidas.mkdir()
    monkeypatch.setattr(nm, "ARCHIVO_N0_SERIES", salidas / "numerador_series.csv")
    monkeypatch.setattr(nm, "ARCHIVO_N0_FICHAS", salidas / "serie_N0.csv")
    monkeypatch.setattr(nm, "ARCHIVO_N0_DESCARGAS", salidas / "numerador_descargas.csv")
    monkeypatch.setattr(nm, "ARCHIVO_CHANGELOG", salidas / "CHANGELOG.md")
    monkeypatch.setattr(nm, "DIR_SERIES", salidas)
    monkeypatch.setattr(nm, "DIR_CRUDO_PRIVADO", tmp_path / "privado")
    monkeypatch.setattr(nm, "DESCARGAS_N0_CONTRASTE", ())

    def sin_red(*args, **kwargs):
        raise AssertionError("la corrida pidió algo a la red")

    monkeypatch.setattr(nm.fuentes_denominador, "reglas_de", sin_red)
    monkeypatch.setattr(nm.fuentes_precios, "_pedir", sin_red)
    assert nm.correr(fecha) == 0
    primera = {r.name: r.read_bytes() for r in salidas.iterdir()}
    assert nm.correr(fecha) == 0
    segunda = {r.name: r.read_bytes() for r in salidas.iterdir()}
    # El changelog de la segunda corrida ya no dice "primera publicación": todo lo demás es idéntico.
    assert {k: v for k, v in primera.items() if k != "CHANGELOG.md"} == {k: v for k, v in segunda.items() if k != "CHANGELOG.md"}
    changelog = segunda["CHANGELOG.md"].decode("utf-8")
    assert changelog.count(f"## {fecha.isoformat()} · numerador") == 1 and "primera publicación" not in changelog
    assert "primera publicación" in primera["CHANGELOG.md"].decode("utf-8")
    series = pd.read_csv(salidas / "numerador_series.csv", dtype={"fecha": str}, keep_default_na=False)
    fichas = pd.read_csv(salidas / "serie_N0.csv", dtype=str, keep_default_na=False)
    assert list(series.columns) == COLUMNAS_N0_SERIES and list(fichas.columns) == COLUMNAS_N0_FICHAS
    assert set(fichas["serie"]) == {s.clave for s in SERIES_N0} | {p.clave for p in PENDIENTES_N0}
    publicadas = set(fichas.loc[fichas["publicada"] == "sí", "serie"])
    assert set(series["serie"]) == publicadas
    # Sin el HTML del Z.1 no hay gate de transporte: esas series no se publican y la ficha dice por qué.
    assert "acciones_eeuu_emision_neta_total_musd" not in publicadas
    assert fichas.loc[fichas["serie"] == "acciones_eeuu_emision_neta_total_musd", "estado"].iloc[0] == "NO MEDIDO: sin validación externa"
    # BTC: lo que sale de los crudos del repositorio.
    btc = series.loc[series["serie"] == "btc_oferta_fin_de_anio_btc"].set_index("anio")["valor"]
    assert (btc.diff().dropna() > 0).all() and btc.max() < BTC_MAXIMO
    minado = series.loc[series["serie"] == "btc_porcentaje_minado_a_la_fecha_pct"]
    assert len(minado) == 1 and 90 < minado["valor"].iloc[0] < 100
    oro = series.loc[series["serie"] == "oro_produccion_mundial_t"].set_index("anio")
    assert oro.index.min() == 1900 and (oro["valor"] > 0).all()
    assert set(oro.loc[oro["control"] != "", "control"]) <= {CONTROL_DENTRO, CONTROL_DISPUTA}
    cota = series.loc[series["serie"] == "oro_crecimiento_stock_cota_superior_pct"]
    assert (cota["estado"] == ESTADO_ESTIMACION).all() and cota["anio"].min() == 1901
