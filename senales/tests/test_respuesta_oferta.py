"""Fase N1: lectores, gates y controles, la regresión, las reglas de ventana, los rótulos y la corrida. Sin red."""

from __future__ import annotations

import math
import random
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from senales import fuentes_respuesta_oferta as fr, respuesta_oferta as ro
from senales.configuracion import (
    COLUMNAS_N1_COEFICIENTES,
    COLUMNAS_N1_FICHAS,
    COLUMNAS_N1_INSUMOS,
    COLUMNAS_N1_RESUMEN,
    ESTADO_ESTIMACION,
    ESTADO_EVIDENCIA_INSUFICIENTE,
    FILAS_FIJAS_N1,
    INSUMOS_N1,
    N1_N_MINIMO,
    PARES_N1,
    ROTULO_FIJO_N1,
    ROTULO_NO_RESPONDE,
    ROTULO_RESPONDE,
    ROTULO_RESPUESTA_NEGATIVA,
    TOLERANCIA_B103_IDENTIDAD_PP,
    ParN1,
)
from senales.fuentes_fred import ErrorDeFuente
from tests import datos_respuesta_oferta as datos

FECHA = "2026-10-14"


# --- Lectores -------------------------------------------------------------------------------


def test_interpretar_fhfa_filtra_el_area_y_exige_la_forma():
    texto = "USA,1975,1,60.04\nUSA,1975,2,61.03\nDV_ENC,1975,1,50.00\nUSA,1975,3,n/a\n"
    serie = fr.interpretar_fhfa(texto)
    assert serie.to_dict() == {"1975:Q1": 60.04, "1975:Q2": 61.03}
    assert fr.decimales_fhfa(texto) == 2
    with pytest.raises(ErrorDeFuente, match="cuatro columnas"):
        fr.interpretar_fhfa("USA,1975,1\n")
    with pytest.raises(ErrorDeFuente, match="repetido"):
        fr.interpretar_fhfa("USA,1975,1,60.04\nUSA,1975,1,60.05\n")
    with pytest.raises(ErrorDeFuente, match="no trae el área"):
        fr.interpretar_fhfa("DV_ENC,1975,1,50.00\n")


def test_interpretar_terminadas_ubica_las_hojas_y_mide_los_decimales(tmp_path):
    anual = {1968: 1319.8, 1969: 1399.0, 1970: 1418.4}
    mensual = {a: [round(v / 12, 1)] * 12 for a, v in anual.items()}
    ruta = tmp_path / "comps.xlsx"
    datos.escribir_terminadas(ruta, anual, mensual)
    terminadas = fr.leer_terminadas(ruta)
    assert terminadas.anual.to_dict() == anual
    assert terminadas.hoja_anual == "Annual" and "Not Seasonally" in terminadas.hoja_mensual
    assert len(terminadas.mensual) == 36 and terminadas.decimales_anual == 1 and terminadas.decimales_mensual == 1
    assert terminadas.fuente.startswith("Source:")
    assert ro.tolerancia_terminadas(terminadas) == pytest.approx(12 * 0.05 + 0.05)
    with pytest.raises(ErrorDeFuente, match="hoja anual"):
        fr.interpretar_terminadas({"Hoja": [("nada",)]})


def test_interpretar_bls_en_grilla_y_en_formato_largo(tmp_path):
    cpi = {f"2024-{m:02d}": 300.0 + m / 10 for m in range(1, 13)} | {"2025-01": 315.605}
    ruta = tmp_path / "bls.xlsx"
    datos.escribir_bls(ruta, cpi)
    copia = fr.leer_bls(ruta)
    assert copia.serie_id == "CUUR0000SA0" and copia.decimales == 3
    assert copia.mensual[pd.Timestamp("2024-03-01")] == 300.3 and len(copia.mensual) == 13
    assert copia.anual.to_dict() == {2024: round(sum(300.0 + m / 10 for m in range(1, 13)) / 12, 3)}
    largo = "Series Id,Year,Period,Value\nCUUR0000SA0,2024,M01,300.100\nCUUR0000SA0,2024,M02,300.200\n" + "".join(f"CUUR0000SA0,2024,M{m:02d},300.{m}00\n" for m in range(3, 13)) + "CUUR0000SA0,2024,M13,300.650\n"
    copia_larga = fr.interpretar_bls_texto(largo)
    assert len(copia_larga.mensual) == 12 and copia_larga.anual.to_dict() == {2024: 300.65}
    with pytest.raises(ErrorDeFuente, match="no se reconoció"):
        fr.interpretar_bls_texto("a,b\n1,2\n")


def test_interpretar_valor_unitario_ds140_usa_los_dolares_corrientes():
    filas = [
        ("GOLD STATISTICS1",), ("U.S. GEOLOGICAL SURVEY",), ("[All values are in metric tons (t) gold content unless otherwise noted]",),
        ("Last modification: November 20, 2023",),
        ("Year", "Primary production", "Unit value ($/t)", "Unit value (98$/t)", "World production"),
        (1900, 120, 609000, 11900000, 386), (1901, 120, "NA", 11900000, 395), (2022, 173, 57900000, 32300000, 3160), ("NA Not available.",),
    ]
    valor = fr.interpretar_valor_unitario_ds140(filas, "oro")
    assert valor.usd_por_t.to_dict() == {1900: 609000.0, 2022: 57900000.0}
    assert valor.usd_por_oz[2022] == pytest.approx(57900000.0 / 32150.7)
    assert valor.encabezado == "Unit value ($/t)" and "2023" in valor.modificado
    with pytest.raises(ErrorDeFuente, match="esperaba la de SILVER"):
        fr.interpretar_valor_unitario_ds140(filas, "plata")
    sin_columna = [f if f[0] != "Year" else ("Year", "Primary production", "World production") for f in filas]
    with pytest.raises(ErrorDeFuente, match="Unit value"):
        fr.interpretar_valor_unitario_ds140(sin_columna, "oro")


def test_extraer_b103_del_zip_por_nombre_o_por_la_serie_testigo(tmp_path):
    contenido = b"date,LM103164105.Q,LM103192105.Q,FL102090005.Q,FL103164106.Q\n2025:Q4,1,2,3,100.00\n"
    ruta = tmp_path / "z1.zip"
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("csv/F51_1_s.csv", b"date,LM103164105.Q\n2025:Q4,1\n")
        z.writestr("csv/otro_nombre.csv", contenido)
    assert fr.extraer_b103_del_zip(ruta) == ("csv/otro_nombre.csv", contenido)
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("csv/S11_1_b.csv", contenido)
    assert fr.extraer_b103_del_zip(ruta)[0] == "csv/S11_1_b.csv"
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("csv/F51_1_s.csv", b"date,LM103164105.Q\n")
    with pytest.raises(ErrorDeFuente, match="ningún CSV"):
        fr.extraer_b103_del_zip(ruta)


def test_interpretar_html_z1_con_decimales(tmp_path):
    b103 = {"2024:Q4": (57122.6, 12838.6, 32494.2, 215.30), "2025:Q1": (58000.0, 13000.0, 33000.0, 215.15), "2025:Q2": (1.0, 2.0, 3.0, 100.0), "2025:Q3": (1.0, 2.0, 3.0, 100.0), "2025:Q4": (59000.0, 13100.0, 33100.0, 217.82), "2026:Q1": (1.0, 2.0, 3.0, 100.0), "2026:Q2": (1.0, 2.0, 3.0, 100.0)}
    ruta = tmp_path / "b103.htm"
    datos.escribir_b103_html(ruta, b103)
    html = fr.leer_html_z1_con_decimales(ruta)
    assert html["LM103164105"]["2024"] == (57.1, 1) and html["FL103164106"]["2025"] == (217.8, 1)
    assert set(html) == {"LM103164105", "LM103192105", "FL102090005", "FL103164106"}


# --- Promedios, gates y controles ------------------------------------------------------------


def test_promedio_anual_solo_con_anios_completos():
    serie = pd.Series({pd.Timestamp(f"2024-{m:02d}-01"): float(m) for m in range(1, 13)} | {pd.Timestamp("2025-01-01"): 5.0})
    assert ro.promedio_anual(serie, 12).to_dict() == {2024: 6.5}
    trimestral = pd.Series({"2024:Q1": 1.0, "2024:Q2": 2.0, "2024:Q3": 3.0, "2024:Q4": 4.0, "2025:Q1": 9.0})
    assert ro.promedio_anual(trimestral, 4).to_dict() == {2024: 2.5}


def test_el_gate_de_construccion_de_la_b103_detiene_la_corrida_si_no_cierra():
    periodos = [f"{a}:Q{q}" for a in (2024, 2025) for q in range(1, 5)]
    tabla = pd.DataFrame(
        {"LM103164105": [57122.6] * 8, "LM103192105": [12838.6] * 8, "FL102090005": [32494.2] * 8, "FL103164106": [215.30] * 8},
        index=pd.Index(periodos, name="periodo"),
    )
    gate = ro.validar_b103_identidad(tabla)
    assert gate.ok and gate.comparados == 8 and gate.maxima < TOLERANCIA_B103_IDENTIDAD_PP
    ro.exigir_gate_de_construccion({"b103_identidad": gate})
    torcida = tabla.copy()
    torcida.loc["2025:Q4", "FL103164106"] = 194.11  # el cociente propio, sin la inversión extranjera directa
    fallido = ro.validar_b103_identidad(torcida)
    assert not fallido.ok and "2025:Q4" in fallido.fuera[0]
    with pytest.raises(ro.GateDeConstruccion, match="2025:Q4"):
        ro.exigir_gate_de_construccion({"b103_identidad": fallido})


def test_el_gate_de_transporte_de_la_b103_usa_medio_paso_de_lo_que_publica_el_html():
    periodos = [f"2025:Q{q}" for q in range(1, 5)]
    tabla = pd.DataFrame(
        {"LM103164105": [57122.6, 57200.0, 57300.0, 57400.0], "LM103192105": [12838.6] * 4, "FL102090005": [32494.2] * 4, "FL103164106": [215.30, 215.5, 215.6, 215.7]},
        index=pd.Index(periodos, name="periodo"),
    )
    html = {m: {"2025": (v, 1)} for m, v in (("LM103164105", 57.4), ("LM103192105", 12.8), ("FL102090005", 32.5), ("FL103164106", 215.7))}
    html["LM103164105"]["2025:Q1"] = (57.1, 1)
    gate = ro.validar_b103_html(tabla, html)
    assert gate.ok and gate.comparados == 5
    html["LM103164105"]["2025:Q1"] = (57.2, 1)  # 57.1226 contra 57.2: fuera de ±0.05
    assert not ro.validar_b103_html(tabla, html).ok
    assert not ro.validar_b103_html(tabla, {}).ok


def test_el_gate_del_cpi_compara_mes_a_mes_y_anio_a_anio(tmp_path):
    cpi = {f"{a}-{m:02d}": round(290.0 + (a - 2023) * 10 + m * 0.123, 3) for a in (2023, 2024, 2025) for m in range(1, 13)}
    serie = pd.Series({pd.Timestamp(f"{k}-01"): v for k, v in cpi.items()})
    ruta = tmp_path / "bls.xlsx"
    datos.escribir_bls(ruta, cpi)
    mensual, anual = ro.validar_cpi_bls(serie, fr.leer_bls(ruta))
    assert mensual.ok and mensual.comparados == 36 and anual.ok and anual.comparados == 3
    torcida = serie.copy()
    torcida[pd.Timestamp("2024-05-01")] += 0.001
    assert not ro.validar_cpi_bls(torcida, fr.leer_bls(ruta))[0].ok
    datos.escribir_bls(ruta, cpi, con_anual=False)
    _, sin_anual = ro.validar_cpi_bls(serie, fr.leer_bls(ruta))
    assert sin_anual.comparados == 0 and "promedio anual" in sin_anual.nota


def test_el_gate_de_la_fhfa_contra_fred_y_el_de_terminadas_por_construccion(tmp_path):
    fhfa = pd.Series({"2024:Q1": 100.11, "2024:Q2": 101.22, "2024:Q3": 102.33, "2024:Q4": 103.44})
    fred = pd.Series({pd.Timestamp("2024-01-01"): 100.11, pd.Timestamp("2024-04-01"): 101.22, pd.Timestamp("2024-07-01"): 102.33, pd.Timestamp("2024-10-01"): 103.44})
    gate = ro.validar_fhfa_fred(fhfa, fred, 2)
    assert gate.ok and gate.comparados == 4 and "±0.005" in gate.tolerancia
    fred[pd.Timestamp("2024-10-01")] = 103.45
    assert not ro.validar_fhfa_fred(fhfa, fred, 2).ok
    anual = {1968: 1319.8, 1969: 1399.0, 1970: 1418.4, 1971: 2000.0}
    mensual = {a: [round(v / 12, 1)] * 12 for a, v in anual.items()}
    mensual[1971] = [100.0] * 12  # suma 1200 contra 2000: fuera
    ruta = tmp_path / "comps.xlsx"
    datos.escribir_terminadas(ruta, anual, mensual)
    gate = ro.validar_terminadas(fr.leer_terminadas(ruta))
    assert not gate.ok and gate.comparados == 4 and gate.fuera == ["1971: hoja anual 2000, suma de los meses 1200.000"]


def test_el_control_de_la_ds140_contra_el_pink_sheet_marca_y_no_decide():
    pink = ro.PrecioPinkSheet(pd.Series({1960: 35.0, 1961: 35.1, 1962: 35.2}), {}, "x")
    ds140 = fr.ValorUnitarioDS140(pd.Series({1959: 34.0, 1960: 35.5, 1961: 40.0, 1962: 35.3}), pd.Series(dtype=float), "Unit value ($/t)", "")
    control = ro.validar_ds140_pink_sheet("oro", ds140, pink)
    assert control.clase == "control" and control.comparados == 3 and control.en_disputa == ["1961"] and control.dentro == ["1960", "1962"]


# --- La regresión (A-N1-8) --------------------------------------------------------------------


def _datos_regresion(n: int = 80, semilla: int = 7):
    generador = random.Random(semilla)
    X = [[1.0] + [generador.gauss(0.0, 0.1) for _ in range(6)] for _ in range(n)]
    betas = [0.01, 0.5, 0.3, -0.2, 0.1, 0.0, 0.05]
    y = [sum(b * x for b, x in zip(betas, fila)) + generador.gauss(0.0, 0.02) for fila in X]
    return y, X, betas


def test_los_coeficientes_son_los_de_minimos_cuadrados_y_la_covarianza_con_l_cero_es_la_de_white():
    y, X, _ = _datos_regresion()
    beta, V = ro.minimos_cuadrados_newey_west(y, X, L=0)
    esperado = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)[0]
    assert np.allclose(beta, esperado, atol=1e-10)
    Xn, yn = np.array(X), np.array(y)
    e = yn - Xn @ esperado
    bread = np.linalg.inv(Xn.T @ Xn)
    white = bread @ (Xn.T @ np.diag(e**2) @ Xn) @ bread
    assert np.allclose(np.array(V), white, atol=1e-12)


def test_newey_west_con_rezagos_suma_las_autocovarianzas_con_pesos_de_bartlett():
    y, X, _ = _datos_regresion(n=60)
    beta, V = ro.minimos_cuadrados_newey_west(y, X, L=4)
    Xn, yn = np.array(X), np.array(y)
    b = np.linalg.lstsq(Xn, yn, rcond=None)[0]
    e = yn - Xn @ b
    xe = Xn * e[:, None]
    S = xe.T @ xe
    for j in range(1, 5):
        G = xe[j:].T @ xe[:-j]
        S += (1 - j / 5) * (G + G.T)
    bread = np.linalg.inv(Xn.T @ Xn)
    assert np.allclose(np.array(V), bread @ S @ bread, atol=1e-12)
    assert np.allclose(beta, b, atol=1e-10)


def test_la_estimacion_recupera_coeficientes_conocidos_y_la_suma_usa_la_covarianza_completa():
    y, X, betas = _datos_regresion(n=400, semilla=3)
    beta, V = ro.minimos_cuadrados_newey_west(y, X)
    assert all(abs(b - esperado) < 0.05 for b, esperado in zip(beta, betas))
    estimacion = ro.Estimacion(beta, V, len(y), list(range(len(y))))
    assert estimacion.suma == pytest.approx(sum(beta[1:]))
    uno = np.ones(6)
    assert estimacion.error_suma == pytest.approx(math.sqrt(uno @ np.array(V)[1:, 1:] @ uno))
    assert estimacion.errores[1] == pytest.approx(math.sqrt(V[1][1]))


def test_los_rotulos_salen_solo_del_intervalo_de_la_suma():
    assert ro.rotulo_de(0.5, 0.1) == ROTULO_RESPONDE
    assert ro.rotulo_de(0.5, 0.3) == ROTULO_NO_RESPONDE
    assert ro.rotulo_de(-0.5, 0.1) == ROTULO_RESPUESTA_NEGATIVA
    assert ro.rotulo_de(0.0, 0.0) == ROTULO_NO_RESPONDE


# --- Ventanas, huecos y exclusiones (A-N1-8) ------------------------------------------------------


def _par(inicio: int, fin: int, activo_clave: str = "oro", deflactar: bool = True) -> ParN1:
    return ParN1("x", "X", activo_clave, "ventana", inicio, fin, "pink_sheet", deflactar, ("A-N1-8",), "serie", "cantidad", "precio")


def _niveles(anios: range, control_cantidad=None, control_precio=None, sin_cantidad=(), cpi=True, ondulado=False) -> ro.NivelesPar:
    cantidad = pd.Series({a: 100.0 * (1.01 ** (a - anios.start)) for a in anios if a not in sin_cantidad})
    onda = (lambda a: 1.0 + 0.1 * math.sin(a)) if ondulado else (lambda a: 1.0)
    precio = pd.Series({a: 10.0 * (1.02 ** (a - anios.start)) * onda(a) for a in anios})
    indice = pd.Series({a: 50.0 * (1.015 ** (a - anios.start)) for a in anios}) if cpi else None
    return ro.NivelesPar(cantidad, precio, indice, "u", "USD", {a: "dato" for a in anios}, control_cantidad or {}, control_precio or {}, {}, {a: "cita" for a in anios}, "cita precio")


def test_la_ventana_acota_las_diferencias_y_el_primer_anio_utilizable_es_inicio_mas_cinco():
    par = _par(1960, 2025)
    insumos = ro.insumos_de(par, _niveles(range(1959, 2026)))
    assert list(insumos["anio"])[:2] == [1959, 1960]
    primera = insumos.set_index("anio")
    assert primera.loc[1959, "y"] is None or pd.isna(primera.loc[1959, "y"])
    assert primera.loc[1960, "dlog_precio_real"] == pytest.approx(math.log(1.02 / 1.015))
    anios, y, X = ro.muestra_de(insumos, par.inicio)
    assert anios[0] == 1965 and anios[-1] == 2025 and len(anios) == 61 and all(len(fila) == 7 for fila in X)
    # Sin nivel del año anterior al inicio, la primera diferencia es la del inicio más uno.
    insumos = ro.insumos_de(par, _niveles(range(1960, 2026)))
    anios, _, _ = ro.muestra_de(insumos, par.inicio)
    assert anios[0] == 1966 and len(anios) == 60


def test_un_anio_en_disputa_saca_su_diferencia_y_la_del_siguiente_y_los_t_que_las_usan():
    par = _par(1960, 2025)
    insumos = ro.insumos_de(par, _niveles(range(1959, 2026), control_precio={1985: "valor en disputa"}))
    tabla = insumos.set_index("anio")
    assert pd.isna(tabla.loc[1985, "dlog_precio_real"]) and pd.isna(tabla.loc[1986, "dlog_precio_real"]) and not pd.isna(tabla.loc[1987, "dlog_precio_real"])
    assert "en disputa" in tabla.loc[1986, "motivo_exclusion"] and tabla.loc[1985, "excluido"] == "Δlog p"
    anios, _, _ = ro.muestra_de(insumos, par.inicio)
    assert all(not (1985 <= a <= 1991) for a in anios) and len(anios) == 61 - 7
    # La cantidad en disputa saca y_t de ese año y del siguiente.
    insumos = ro.insumos_de(par, _niveles(range(1959, 2026), control_cantidad={2020: "valor en disputa"}))
    tabla = insumos.set_index("anio")
    assert pd.isna(tabla.loc[2020, "y"]) and pd.isna(tabla.loc[2021, "y"]) and not pd.isna(tabla.loc[2022, "y"])
    assert tabla.loc[2020, "control"] == "cantidad: valor en disputa"


def test_un_hueco_no_se_rellena_y_sin_treinta_observaciones_es_evidencia_insuficiente():
    par = _par(1960, 2025)
    insumos = ro.insumos_de(par, _niveles(range(1959, 2026), sin_cantidad=(1990,)))
    tabla = insumos.set_index("anio")
    assert pd.isna(tabla.loc[1990, "y"]) and pd.isna(tabla.loc[1991, "y"]) and tabla.loc[1990, "excluido"] == "y"
    anios, _, _ = ro.muestra_de(insumos, par.inicio)
    assert 1990 not in anios and 1991 not in anios and len(anios) == 59
    justo = ro.insumos_de(_par(1960, 1995), _niveles(range(1959, 1996), ondulado=True))
    estimacion = ro.estimar(justo, 1960)
    assert estimacion.n == 31 and len(estimacion.beta) == 7  # 1965 a 1995: alcanza
    corto = ro.insumos_de(_par(1960, 1990), _niveles(range(1959, 1991), ondulado=True))
    estimacion = ro.estimar(corto, 1960)
    assert estimacion is not None and not estimacion.beta and estimacion.n == 26 and estimacion.n < N1_N_MINIMO
    # El arranque natural de la ventana no es una exclusión; un hueco sí.
    assert tabla.loc[1960, "motivo_exclusion"] == "" and tabla.loc[1990, "motivo_exclusion"] == "hueco: sin cantidad en 1990"
    assert tabla.loc[1991, "motivo_exclusion"] == "hueco: sin cantidad en 1990"


def test_las_acciones_usan_la_tasa_en_nivel_y_la_valuacion_sin_deflactar():
    par = _par(1946, 2025, activo_clave="acciones", deflactar=False)
    niveles = _niveles(range(1946, 2026), cpi=False)
    insumos = ro.insumos_de(par, niveles)
    tabla = insumos.set_index("anio")
    assert tabla.loc[1946, "y"] == pytest.approx(100.0) and tabla.loc[1950, "y"] == pytest.approx(100.0 * 1.01**4)
    assert tabla.loc[1947, "dlog_precio_real"] == pytest.approx(math.log(1.02)) and pd.isna(tabla.loc[1946, "dlog_precio_real"])
    assert tabla["cpi"].isna().all() and tabla.loc[1950, "precio_real"] == tabla.loc[1950, "precio_nominal"]
    anios, _, _ = ro.muestra_de(insumos, par.inicio)
    assert anios[0] == 1952 and len(anios) == 74


# --- Fichas, filas fijas y el prerregistro en el código ------------------------------------------


def test_los_pares_y_las_fichas_siguen_el_prerregistro():
    assert len(PARES_N1) == 8 and len({p.clave for p in PARES_N1}) == 8
    ventanas = {p.clave: (p.inicio, p.fin) for p in PARES_N1}
    assert ventanas["oro_pink_sheet"] == (1960, 2025) and ventanas["oro_ds140_1900"] == (1900, 2022) and ventanas["oro_ds140_1971"] == (1971, 2022)
    assert ventanas["plata_ds140_1900"] == (1900, 2021) and ventanas["viviendas_eeuu_fhfa"] == (1976, 2025) and ventanas["acciones_eeuu_valuacion"] == (1946, 2025)
    acciones = next(p for p in PARES_N1 if p.activo_clave == "acciones")
    assert not acciones.deflactar and all(p.deflactar for p in PARES_N1 if p.activo_clave != "acciones")
    for par in PARES_N1:
        assert par.supuestos and "A-N1-8" in par.supuestos and "A-N1-10" in par.supuestos
        if par.activo_clave in ("viviendas", "acciones"):
            assert "de EE.UU." in par.activo
        assert "global" not in par.activo.lower()
    assert "oportunidad" not in ROTULO_FIJO_N1 and ROTULO_FIJO_N1.startswith("asociación observada")
    assert {f.clave for f in FILAS_FIJAS_N1} == {"btc", "deuda_eeuu"}
    assert len({s.clave for s in INSUMOS_N1}) == len(INSUMOS_N1)
    for insumo in INSUMOS_N1:
        assert insumo.unidad and insumo.convencion and insumo.supuestos


# --- La corrida de punta a punta, con el mundo sintético ---------------------------------------------


@pytest.fixture
def entorno(tmp_path: Path, monkeypatch) -> dict:
    mundo = datos.mundo(FECHA)
    rutas = datos.escribir_mundo(tmp_path, mundo)
    series, reportes = rutas["series"], tmp_path / "reportes"
    monkeypatch.setattr(ro, "DIR_CRUDO", rutas["crudo"])
    monkeypatch.setattr(ro, "DIR_CRUDO_PRIVADO", rutas["privado"])
    monkeypatch.setattr(ro, "DIR_SERIES", series)
    monkeypatch.setattr(ro, "DIR_REPORTES", reportes)
    monkeypatch.setattr(ro, "ARCHIVO_N1_COEFICIENTES", series / "respuesta_oferta.csv")
    monkeypatch.setattr(ro, "ARCHIVO_N1_RESUMEN", series / "respuesta_oferta_resumen.csv")
    monkeypatch.setattr(ro, "ARCHIVO_N1_INSUMOS", series / "respuesta_oferta_insumos.csv")
    monkeypatch.setattr(ro, "ARCHIVO_N1_FICHAS", series / "serie_N1.csv")
    monkeypatch.setattr(ro, "ARCHIVO_N1_DESCARGAS", series / "respuesta_oferta_descargas.csv")
    monkeypatch.setattr(ro, "ARCHIVO_N0_DESCARGAS", series / "numerador_descargas.csv")
    monkeypatch.setattr(ro, "ARCHIVO_N0_SERIES", series / "numerador_series.csv")
    monkeypatch.setattr(ro, "ARCHIVO_PRECIOS", series / "precios_mensuales.csv")
    monkeypatch.setattr(ro, "ARCHIVO_CHANGELOG", series / "CHANGELOG.md")
    # fuentes_denominador.fecha_de_copia_manual mira DIR_CRUDO del módulo de arriba para las copias versionadas.
    monkeypatch.setattr(ro.fuentes_denominador, "DIR_CRUDO", rutas["crudo"], raising=False)

    def sin_red(*args, **kwargs):
        raise AssertionError("la corrida pidió algo a la red")

    monkeypatch.setattr(ro.fuentes_denominador, "reglas_de", sin_red)
    monkeypatch.setattr(ro.fuentes_precios, "_pedir", sin_red)
    return {"mundo": mundo, "series": series, "reportes": reportes, **rutas}


def test_la_corrida_es_idempotente_no_toca_la_red_y_publica_los_ocho_pares(entorno):
    fecha = date.fromisoformat(FECHA)
    assert ro.correr(fecha) == 0
    series = entorno["series"]
    primera = {r.name: r.read_bytes() for r in series.iterdir() if r.name.startswith(("respuesta_oferta", "serie_N1"))}
    assert ro.correr(fecha) == 0
    segunda = {r.name: r.read_bytes() for r in series.iterdir() if r.name.startswith(("respuesta_oferta", "serie_N1"))}
    assert primera == segunda
    changelog = (series / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.count(f"## {FECHA} · respuesta_oferta") == 1 and "primera publicación" not in changelog
    assert ROTULO_FIJO_N1 in changelog

    coeficientes = pd.read_csv(series / "respuesta_oferta.csv", keep_default_na=False)
    resumen = pd.read_csv(series / "respuesta_oferta_resumen.csv", keep_default_na=False)
    insumos = pd.read_csv(series / "respuesta_oferta_insumos.csv", keep_default_na=False)
    fichas = pd.read_csv(series / "serie_N1.csv", dtype=str, keep_default_na=False)
    assert list(coeficientes.columns) == COLUMNAS_N1_COEFICIENTES and list(resumen.columns) == COLUMNAS_N1_RESUMEN
    assert list(insumos.columns) == COLUMNAS_N1_INSUMOS and list(fichas.columns) == COLUMNAS_N1_FICHAS
    assert len(coeficientes) == 8 * 6 and (coeficientes["rotulo_fijo"] == ROTULO_FIJO_N1).all() and (coeficientes["desvio_del_prerregistro"] == "no").all()
    estimados = resumen.loc[resumen["estado"] == ESTADO_ESTIMACION]
    assert len(estimados) == 8 and set(estimados["rotulo"]) <= {ROTULO_RESPONDE, ROTULO_NO_RESPONDE, ROTULO_RESPUESTA_NEGATIVA}
    por_ventana = resumen.set_index(["activo", "ventana"])
    # n esperado con las exclusiones del mundo sintético: 1985-03 en disputa (siete t por metal), la plata
    # con cuatro años de producción en disputa (seis t más), 1968 y 1969 fuera en el control de la DS140 (ocho t).
    n = lambda activo, ventana: int(por_ventana.loc[(activo, ventana), "n"])
    assert n("Oro", "(a) Pink Sheet 1960–2025") == 60 - 7
    assert n("Plata", "(a) Pink Sheet 1960–2025") == 60 - 7 - 6
    assert n("Oro", "(b) DS140 1900–2022") == 104 - 8
    assert n("Oro", "(b) DS140 1971–2022") == 47
    assert n("Plata", "(b) DS140 1900–2021") == 103 - 8 - 2  # solo 2020 y 2021 caen en la ventana
    assert n("Viviendas de EE.UU.", "1976–2025") == 45
    assert n("Acciones de EE.UU.", "1946–2025") == 74
    assert por_ventana.loc[("Oro", "(a) Pink Sheet 1960–2025"), "anios_excluidos"] == "1985, 1986"
    assert por_ventana.loc[("Acciones de EE.UU.", "1946–2025"), "anios_excluidos"] == ""
    assert por_ventana.loc[("Oro", "(b) DS140 1900–2022"), "anios_excluidos"] == "1968, 1969, 1970"
    # BTC y la deuda están en el resumen sin coeficientes (A-N1-7).
    btc = resumen.loc[resumen["activo"] == "BTC"].iloc[0]
    assert btc["rotulo"].startswith("no aplica") and btc["estado"] == "dato" and btc["n"] == "" and btc["suma"] == ""
    deuda = resumen.loc[resumen["activo"] == "Deuda de EE.UU."].iloc[0]
    assert deuda["estado"] == "NO MEDIDO"
    # El mundo sintético responde con β_1 = 0.3 al precio real rezagado un año: el coeficiente lo recupera.
    oro = coeficientes.loc[(coeficientes["activo"] == "Oro") & (coeficientes["ventana"] == "(b) DS140 1900–2022")].set_index("rezago")
    assert abs(oro.loc[1, "coeficiente"] - 0.3) < 0.1 and oro.loc[1, "intervalo_inferior"] < 0.3 < oro.loc[1, "intervalo_superior"]
    # Las fichas: insumos usados, ocho resultados publicados y dos filas fijas.
    de_insumos = fichas.loc[fichas["serie"].isin({i.clave for i in INSUMOS_N1})]
    assert len(de_insumos) == len(INSUMOS_N1) and (de_insumos["publicada"] == "sí").sum() == len(INSUMOS_N1) - 1  # todos menos el gate
    assert fichas.loc[fichas["serie"] == "acciones_eeuu_valuacion_junta_fl103164106_pct", "estado"].iloc[0] == "gate de construcción: cerró"
    assert set(fichas.loc[fichas["serie"].str.startswith("respuesta_oferta_") & (fichas["publicada"] == "sí"), "serie"]) == {f"respuesta_oferta_{p.clave}" for p in PARES_N1}
    assert all(ROTULO_FIJO_N1 in q for q in fichas.loc[fichas["serie"].str.startswith("respuesta_oferta_"), "quiebres"])
    # Un PNG por par estimado.
    assert len(list(entorno["reportes"].glob("respuesta_oferta_*.png"))) == 8
    # El manifiesto registra la copia del BLS fuera del repositorio y los crudos versionados dentro.
    manifiesto = pd.read_csv(series / "respuesta_oferta_descargas.csv", dtype=str, keep_default_na=False)
    assert manifiesto.loc[manifiesto["fuente"] == "bls_cpi_u", "crudo_en_repo"].iloc[0] == "no"
    assert manifiesto.loc[manifiesto["fuente"] == "fhfa_hpi_at_eeuu", "crudo_en_repo"].iloc[0] == "sí"
    assert set(manifiesto["fuente"]) >= {"fhfa_hpi_at_eeuu", "censo_viviendas_terminadas", "fred_cpiaucns", "z1_b103", "bls_cpi_u", "fred_ussthpi", "z1_html_b103", "usgs_ds140_oro", "usgs_ds140_plata"}


def test_sin_la_copia_del_bls_los_tres_pares_deflactados_quedan_no_medido_y_las_acciones_se_calculan(entorno):
    (entorno["privado"] / f"bls_cpi_u_{FECHA}.xlsx").unlink()
    assert ro.correr(date.fromisoformat(FECHA), con_graficos=False) == ro.CODIGO_FUENTE_FALTANTE
    resumen = pd.read_csv(entorno["series"] / "respuesta_oferta_resumen.csv", keep_default_na=False).set_index(["activo", "ventana"])
    for activo, ventana in (("Oro", "(a) Pink Sheet 1960–2025"), ("Plata", "(b) DS140 1971–2021"), ("Viviendas de EE.UU.", "1976–2025")):
        assert resumen.loc[(activo, ventana), "estado"] == "NO MEDIDO" and "deflactor" in resumen.loc[(activo, ventana), "motivo"]
    assert resumen.loc[("Acciones de EE.UU.", "1946–2025"), "estado"] == ESTADO_ESTIMACION
    fichas = pd.read_csv(entorno["series"] / "serie_N1.csv", dtype=str, keep_default_na=False).set_index("serie")
    assert fichas.loc["cpi_u_eeuu_promedio_anual", "publicada"] == "no" and "copia del BLS" in fichas.loc["cpi_u_eeuu_promedio_anual", "estado"]


def test_si_el_gate_de_construccion_de_la_b103_no_cierra_la_corrida_se_detiene_sin_escribir(entorno):
    ruta = entorno["crudo"] / f"z1_b103_{FECHA}.csv"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    campos = lineas[-1].split(",")
    campos[-1] = f"{float(campos[-1]) - 1.0:.2f}"
    lineas[-1] = ",".join(campos)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    assert ro.correr(date.fromisoformat(FECHA), con_graficos=False) == ro.CODIGO_GATE_DE_CONSTRUCCION
    assert not (entorno["series"] / "respuesta_oferta_resumen.csv").exists()


def test_un_crudo_cuyo_hash_no_coincide_con_el_manifiesto_no_se_usa(entorno):
    fecha = date.fromisoformat(FECHA)
    assert ro.correr(fecha, con_graficos=False) == 0
    ruta = entorno["crudo"] / f"fhfa_hpi_at_eeuu_{FECHA}.csv"
    ruta.write_bytes(ruta.read_bytes().replace(b"\n", b"\r\n"))  # finales de línea de Windows: otros bytes
    assert ro.correr(fecha, con_graficos=False) == ro.CODIGO_FUENTE_FALTANTE
    resumen = pd.read_csv(entorno["series"] / "respuesta_oferta_resumen.csv", keep_default_na=False).set_index(["activo", "ventana"])
    assert resumen.loc[("Viviendas de EE.UU.", "1976–2025"), "estado"] == "NO MEDIDO"
    assert "sha256" in resumen.loc[("Viviendas de EE.UU.", "1976–2025"), "motivo"]
