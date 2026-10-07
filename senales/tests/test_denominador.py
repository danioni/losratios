"""Fase D0: lectores, convención mensual, gates, agregado y la corrida de punta a punta.

Ningún test toca la red. Las fuentes están fabricadas en datos_denominador.py.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from senales import denominador, fuentes_denominador as fd
from senales.configuracion import (
    BCE_CLAVE_BALANCE,
    BCE_CLAVE_M2_AJUSTADA,
    BCE_CLAVE_M2_SIN_AJUSTAR,
    BDE_CODIGO_M2_AJUSTADA,
    BDE_CODIGO_M2_SIN_AJUSTAR,
    BOJ_CODIGO_BALANCE,
    BOJ_CODIGO_M2,
    CLAVE_M2CD_1967_1999,
    CLAVE_M2CD_1998_2008,
    COLUMNAS_D0_FICHAS,
    DESCARGA_BCE_M2_AJUSTADA,
    ESTAT_INDICADOR_M2,
    NO_MEDIDO_ACCESO_VEDADO,
    NO_MEDIDO_SIN_VALIDACION,
    AnclaMensual,
)
from senales.fuentes_fred import ErrorDeFuente
from tests import datos_denominador as datos

FECHA = date(2026, 10, 5)
ROBOTS_BCE = """User-agent: python-requests
Disallow: /

User-agent: *
Disallow: /admin/
"""


# --- robots.txt (A-D0-29) -------------------------------------------------------


def test_robots_veda_al_cliente_nombrado_y_admite_al_resto():
    reglas = fd.interpretar_robots(200, "text/plain", ROBOTS_BCE)
    assert not reglas.can_fetch(fd.AGENTE, "https://data-api.ecb.europa.eu/service/data/BSI/x")
    assert reglas.can_fetch("senales-losratios/1.0", "https://data-api.ecb.europa.eu/service/data/BSI/x")
    assert not reglas.can_fetch("senales-losratios/1.0", "https://data-api.ecb.europa.eu/admin/x")


def test_robots_sin_archivo_no_pone_reglas_y_un_403_veda_todo():
    assert fd.interpretar_robots(404, "text/html", "<html>no</html>").can_fetch(fd.AGENTE, "https://x/y")
    assert fd.interpretar_robots(200, "text/html", "<!DOCTYPE html>").can_fetch(fd.AGENTE, "https://x/y")
    assert not fd.interpretar_robots(403, "text/plain", "").can_fetch(fd.AGENTE, "https://x/y")


def test_exigir_acceso_falla_con_acceso_vedado(monkeypatch):
    monkeypatch.setattr(fd, "_robots", {"data-api.ecb.europa.eu": fd.interpretar_robots(200, "text/plain", ROBOTS_BCE)})
    with pytest.raises(fd.AccesoVedado):
        fd.exigir_acceso("https://data-api.ecb.europa.eu/service/data/BSI/x")
    fd.exigir_acceso("https://data-api.ecb.europa.eu/service/data/BSI/x", agente="senales-losratios/1.0")


def test_copia_manual_toma_la_mas_reciente_hasta_la_fecha(tmp_path):
    for nombre in ("bce_m2_ajustada_2026-09-01.csv", "bce_m2_ajustada_2026-10-05.csv", "bce_m2_ajustada_2026-11-01.csv"):
        (tmp_path / nombre).write_text("x")
    assert fd.fecha_de_copia_manual(DESCARGA_BCE_M2_AJUSTADA, date(2026, 10, 6), tmp_path, tmp_path) == date(2026, 10, 5)
    with pytest.raises(fd.CopiaFaltante):
        fd.fecha_de_copia_manual(DESCARGA_BCE_M2_AJUSTADA, date(2026, 8, 1), tmp_path, tmp_path)


# --- Lectores -----------------------------------------------------------------


def test_leer_xml_junta_salta_nd_y_exige_las_series(tmp_path):
    ruta = tmp_path / "h.zip"
    ruta.write_bytes(
        datos.zip_junta(
            "H6_data.xml",
            {"M2.M": ({"UNIT_MULT": "1e+09", "CURRENCY": "USD"}, [("2026-01-31", 1.0), ("2026-02-28", None), ("2026-03-31", 3.0)])},
        )
    )
    series = fd.leer_xml_junta(ruta, {"M2.M"})
    assert list(series["M2.M"].valores) == [1.0, 3.0]
    assert series["M2.M"].multiplicador == "1e+09"
    fd.exigir_multiplicador(series["M2.M"], "M2.M", 1e9)
    with pytest.raises(ErrorDeFuente):
        fd.exigir_multiplicador(series["M2.M"], "M2.M", 1e6)
    with pytest.raises(ErrorDeFuente):
        fd.leer_xml_junta(ruta, {"M2.M", "NO_EXISTE"})


def test_leer_csv_bce_verifica_clave_y_unidad(tmp_path):
    ruta = tmp_path / "bce.csv"
    ruta.write_text(datos.csv_bce_m2(BCE_CLAVE_M2_AJUSTADA), encoding="utf-8")
    serie = fd.leer_csv_bce(ruta, BCE_CLAVE_M2_AJUSTADA)
    assert len(serie) == len(datos.MESES) and serie.index[0] == pd.Timestamp("2025-01-01")
    with pytest.raises(ErrorDeFuente):
        fd.leer_csv_bce(ruta, BCE_CLAVE_M2_SIN_AJUSTAR)
    ruta.write_text(datos.csv_bce(BCE_CLAVE_M2_AJUSTADA, [("2025-01", 1.0)], mult="9"), encoding="utf-8")
    with pytest.raises(ErrorDeFuente):
        fd.leer_csv_bce(ruta, BCE_CLAVE_M2_AJUSTADA)


def test_periodo_bce_semanal_es_el_viernes_y_la_semana_53_de_1998_es_el_1_de_enero():
    assert fd.periodo_bce("2026-W39") == pd.Timestamp("2026-09-25")
    assert fd.periodo_bce("1998-W53") == pd.Timestamp("1999-01-01")
    assert fd.periodo_bce("2026-08") == pd.Timestamp("2026-08-01")


def test_leer_csv_boj_exige_estado_200_y_unidad(tmp_path):
    ruta = tmp_path / "boj.csv"
    ruta.write_text(datos.csv_boj(BOJ_CODIGO_M2, datos.m2_japon()), encoding="utf-8")
    assert len(fd.leer_csv_boj(ruta, BOJ_CODIGO_M2)) == len(datos.MESES)
    with pytest.raises(ErrorDeFuente):
        fd.leer_csv_boj(ruta, "OTRO")
    ruta.write_text(datos.csv_boj(BOJ_CODIGO_M2, datos.m2_japon(), estado="500"), encoding="utf-8")
    with pytest.raises(ErrorDeFuente):
        fd.leer_csv_boj(ruta, BOJ_CODIGO_M2)


def test_leer_csv_ocde_devuelve_el_rotulo_de_la_fuente(tmp_path):
    ruta = tmp_path / "ocde.csv"
    ruta.write_text(datos.csv_ocde(datos.dinero_china()), encoding="utf-8")
    serie = fd.leer_csv_ocde(ruta, "CHN", "MABM")
    assert serie.rotulo == "M3" and serie.ajuste.startswith("Neither")
    with pytest.raises(ErrorDeFuente):
        fd.leer_csv_ocde(ruta, "JPN", "MABM")


def test_lectores_bis_bde_estat_y_tabla_h6(tmp_path):
    activos = pd.Series([1.5, 2.5], index=pd.DatetimeIndex(["2026-01-01", "2026-02-01"]))
    (tmp_path / "bis.csv").write_text(datos.csv_bis_activos("CN", activos), encoding="utf-8")
    assert list(fd.leer_csv_bis_activos(tmp_path / "bis.csv", "CN")) == [1.5, 2.5]
    (tmp_path / "xru.csv").write_text(datos.csv_bis_cambio("JPY", activos), encoding="utf-8")
    assert list(fd.leer_csv_bis_cambio(tmp_path / "xru.csv", "JPY", "A")) == [1.5, 2.5]
    with pytest.raises(ErrorDeFuente):
        fd.leer_csv_bis_cambio(tmp_path / "xru.csv", "JPY", "E")
    bde = fd.interpretar_bde(datos.csv_bde(BDE_CODIGO_M2_AJUSTADA, datos.m2_eurozona()), BDE_CODIGO_M2_AJUSTADA)
    assert bde.index[0] == pd.Timestamp("2025-01-01") and len(bde) == len(datos.MESES)
    estat = fd.interpretar_estat(json.loads(datos.json_estat(datos.m2_japon(), ESTAT_INDICADOR_M2)), ESTAT_INDICADOR_M2)
    assert estat.iloc[0] == datos.m2_japon().iloc[0]
    tabla = fd.interpretar_tabla_h6(datos.html_h6())
    assert list(tabla.columns) == ["ajustada", "sin_ajustar"] or set(tabla.columns) == {"ajustada", "sin_ajustar"}
    assert tabla["ajustada"].iloc[-1] == datos.m2_eeuu().iloc[-1]
    assert tabla["sin_ajustar"].iloc[0] == datos.m2_eeuu().iloc[0] + 10.0


# --- Convención mensual (A-D0-14) -----------------------------------------------


def test_ultimo_del_mes_toma_el_ultimo_dato_y_excluye_el_mes_incompleto():
    semanal = pd.Series(range(6), index=pd.DatetimeIndex(["2026-08-05", "2026-08-12", "2026-08-19", "2026-08-26", "2026-09-02", "2026-09-09"]))
    mensual, origen = denominador.ultimo_del_mes(semanal)
    # Agosto completo: 26 + 7 cae en septiembre. Septiembre no: 9 + 7 sigue en septiembre.
    assert list(mensual.index) == [pd.Timestamp("2026-08-01")]
    assert mensual.iloc[0] == 3 and origen.iloc[0] == pd.Timestamp("2026-08-26")


def test_fin_de_mes_excluye_el_mes_en_curso():
    diaria = pd.Series([1.0, 2.0, 3.0], index=pd.DatetimeIndex(["2026-08-28", "2026-08-31", "2026-09-01"]))
    tabla = denominador.fin_de_mes(diaria)
    assert list(tabla.index) == [pd.Timestamp("2026-08-01")]
    assert tabla["fin_de_mes"].iloc[0] == 2.0 and tabla["fecha_fin_de_mes"].iloc[0] == pd.Timestamp("2026-08-31")


def test_fin_de_semana_bis():
    # Marzo de 2020 termina un martes: su semana hábil cierra el viernes 3 de abril.
    assert denominador._fin_de_semana_bis(pd.Timestamp("2020-03-01")) == pd.Timestamp("2020-04-03")
    assert denominador._fin_de_semana_bis(pd.Timestamp("2026-07-01")) == pd.Timestamp("2026-07-31")


# --- Gates (A-D0-25) ------------------------------------------------------------


def _serie(valores: list[float], inicio: str = "2026-01-01") -> pd.Series:
    return pd.Series(valores, index=pd.date_range(inicio, periods=len(valores), freq="MS"))


def test_comparar_cierra_dentro_de_tolerancia_y_no_fuera():
    propia, ajena = _serie([10.0, 20.0, 30.0, 40.0]), _serie([10.0, 20.0, 30.4, 40.0])
    ok = denominador.comparar("s", propia, ajena, 0.5, "f", "u")
    assert ok.ok and ok.comparados == 4 and ok.maxima == pytest.approx(0.4)
    mal = denominador.comparar("s", propia, ajena, 0.3, "f", "u")
    assert not mal.ok and mal.fuera == ["2026-03"]
    assert not denominador.comparar("s", propia.iloc[:2], ajena, 0.5, "f", "u").ok  # menos de 3 meses


def test_un_control_marca_en_disputa_y_no_decide():
    propia, ajena = _serie([10.0, 20.0, 30.0, 40.0]), _serie([10.0, 20.0, 31.0, 40.0])
    control = denominador.comparar("s", propia, ajena, 0.5, "f", "%", relativa=True).como_control()
    assert control.ok and control.clase == "control" and control.en_disputa == ["2026-03"]


def test_las_anclas_exigen_tres_y_cierran_dentro_del_medio_paso():
    serie = _serie([100.0, 200.0, 300.0])
    anclas = (
        AnclaMensual("s", "2026-01", 100.4, 0.5, "f", "u", FECHA),
        AnclaMensual("s", "2026-02", 200.0, 0.5, "f", "u", FECHA),
        AnclaMensual("s", "2026-03", 300.0, 0.5, "f", "u", FECHA),
    )
    assert denominador.comparar_anclas("s", serie, anclas).ok
    # Con dos anclas no se decide (A-D0-25): es lo que deja a China NO MEDIDO hoy.
    assert not denominador.comparar_anclas("s", serie, anclas[:2]).ok
    lejos = anclas[:2] + (AnclaMensual("s", "2026-03", 301.0, 0.5, "f", "u", FECHA),)
    assert denominador.comparar_anclas("s", serie, lejos).fuera == ["2026-03"]


# --- Corrida de punta a punta -----------------------------------------------------


def _sembrar(crudo: Path, privado: Path, fecha: str, con_bce: bool = True) -> None:
    (privado / f"junta_h6_{fecha}.zip").write_bytes(datos.zip_h6())
    (privado / f"junta_h10_{fecha}.zip").write_bytes(datos.zip_h10())
    (privado / f"junta_h41_{fecha}.zip").write_bytes(datos.zip_h41())
    if con_bce:
        (crudo / f"bce_m2_ajustada_{fecha}.csv").write_text(datos.csv_bce_m2(BCE_CLAVE_M2_AJUSTADA), encoding="utf-8")
        (crudo / f"bce_m2_sin_ajustar_{fecha}.csv").write_text(datos.csv_bce_m2(BCE_CLAVE_M2_SIN_AJUSTAR, 1000.0), encoding="utf-8")
        (crudo / f"bce_balance_eurosistema_{fecha}.csv").write_text(datos.csv_bce_balance(BCE_CLAVE_BALANCE), encoding="utf-8")
    (crudo / f"boj_m2_{fecha}.csv").write_text(datos.csv_boj_m2_completo(), encoding="utf-8")
    (crudo / f"boj_balance_{fecha}.csv").write_text(datos.csv_boj(BOJ_CODIGO_BALANCE, datos.balance_boj()), encoding="utf-8")
    (crudo / f"ocde_china_dinero_amplio_{fecha}.csv").write_text(datos.csv_ocde(datos.dinero_china()), encoding="utf-8")
    balance_cn = pd.Series([40_000.0 + i for i in range(len(datos.MESES))], index=datos.meses_ts())
    (crudo / f"bis_cbta_cn_{fecha}.csv").write_text(datos.csv_bis_activos("CN", balance_cn), encoding="utf-8")
    # Contrastes, coherentes con las fuentes.
    (privado / f"junta_h6_html_{fecha}.html").write_text(datos.html_h6(), encoding="utf-8")
    (privado / f"fred_walcl_{fecha}.csv").write_text(datos.csv_fred_walcl(), encoding="utf-8")
    fed_mensual, _ = denominador.ultimo_del_mes(datos.balance_fed_semanal())
    (privado / f"bis_cbta_us_{fecha}.csv").write_text(datos.csv_bis_activos("US", fed_mensual / 1000.0), encoding="utf-8")
    semanal_bce = datos.balance_eurosistema_semanal()
    meses_bce = pd.DatetimeIndex([p.to_timestamp() for p in pd.period_range("2025-01", "2026-08", freq="M")])
    bce_bis = pd.Series([semanal_bce[denominador._fin_de_semana_bis(m)] / 1000.0 for m in meses_bce], index=meses_bce)
    (privado / f"bis_cbta_xm_{fecha}.csv").write_text(datos.csv_bis_activos("XM", bce_bis), encoding="utf-8")
    (privado / f"bde_m2_ajustada_{fecha}.csv").write_text(datos.csv_bde(BDE_CODIGO_M2_AJUSTADA, datos.m2_eurozona()), encoding="latin-1")
    (privado / f"bde_m2_sin_ajustar_{fecha}.csv").write_text(datos.csv_bde(BDE_CODIGO_M2_SIN_AJUSTAR, datos.m2_eurozona() + 1000.0), encoding="latin-1")
    (privado / f"estat_m2_japon_{fecha}.json").write_text(datos.json_estat(datos.m2_japon(), ESTAT_INDICADOR_M2), encoding="utf-8")
    (privado / f"fred_fmi_m2_japon_{fecha}.csv").write_text(datos.csv_fred_fmi_m2_japon(), encoding="utf-8")
    (privado / f"bis_cbta_jp_{fecha}.csv").write_text(datos.csv_bis_activos("JP", datos.balance_boj() / 10.0), encoding="utf-8")
    for area, moneda, base, pendiente, invertir in (("XM", "EUR", 1.10, 0.0001, True), ("JP", "JPY", 150.0, 0.01, False), ("CN", "CNY", 7.0, 0.0005, False)):
        promedio = datos.cambio_mensual_promedio(datos.cambio_diario(base, pendiente))
        promedio.index = pd.DatetimeIndex([p.to_timestamp() for p in promedio.index])
        promedio = (1.0 / promedio) if invertir else promedio
        (privado / f"bis_xru_{area.lower()}_{fecha}.csv").write_text(datos.csv_bis_cambio(moneda, promedio), encoding="utf-8")


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    crudo, privado, series = tmp_path / "raw", tmp_path / "privado", tmp_path / "series"
    for directorio in (crudo, privado, series):
        directorio.mkdir()
    monkeypatch.setattr(denominador, "DIR_CRUDO", crudo)
    monkeypatch.setattr(denominador, "DIR_CRUDO_PRIVADO", privado)
    monkeypatch.setattr(denominador, "DIR_SERIES", series)
    for nombre in ("DINERO", "BALANCES", "CAMBIO", "AGREGADO", "FICHAS", "DESCARGAS"):
        monkeypatch.setattr(denominador, f"ARCHIVO_D0_{nombre}", series / f"d0_{nombre.lower()}.csv")
    monkeypatch.setattr(denominador, "ARCHIVO_CHANGELOG", series / "CHANGELOG.md")
    china = datos.dinero_china()
    monkeypatch.setattr(
        denominador,
        "ANCLAS_CHINA",
        (
            AnclaMensual("dinero_amplio_china", "2026-08", float(china.iloc[-1]) + 20.0, 50.0, "prueba", "u", FECHA),
            AnclaMensual("dinero_amplio_china", "2025-12", float(china.loc["2025-12-01"]), 50.0, "prueba", "u", FECHA),
            AnclaMensual("dinero_amplio_china", "2025-06", float(china.loc["2025-06-01"]), 50.0, "prueba", "u", FECHA),
        ),
    )
    # Ningún test toca la red: si algo intentara pedir, el robots.txt fingido lo veda.
    monkeypatch.setattr(fd, "reglas_de", lambda host, sesion=None: fd.interpretar_robots(403, "text/plain", ""))
    return crudo, privado, series


def test_corrida_completa_publica_y_es_idempotente(entorno):
    crudo, privado, series = entorno
    _sembrar(crudo, privado, FECHA.isoformat())
    assert denominador.main(["--fecha-descarga", FECHA.isoformat()]) == 0
    fichas = pd.read_csv(series / "d0_fichas.csv", dtype=str, keep_default_na=False)
    assert list(fichas.columns) == COLUMNAS_D0_FICHAS
    publicadas = set(fichas.loc[fichas["publicada"] == "sí", "serie"])
    assert {"m2_eeuu", "m2_eurozona", "m2_japon", "dinero_amplio_china", "balance_fed", "balance_eurosistema", "balance_boj", "usd_por_eur"} <= publicadas
    # A-D0-34, A-D0-35: las series antiguas de Japón se publican, cada una con su gate contra el FMI.
    assert {CLAVE_M2CD_1967_1999, CLAVE_M2CD_1998_2008} <= publicadas
    viejo = fichas.loc[fichas["serie"] == CLAVE_M2CD_1967_1999].iloc[0]
    assert "cerró en 15 meses" in viejo["validacion"] and "superposición con m2cd_japon_1998_2008: 12 meses" in viejo["validacion"]
    nuevo = fichas.loc[fichas["serie"] == CLAVE_M2CD_1998_2008].iloc[0]
    assert "cerró en 60 meses" in nuevo["validacion"] and "superposición con m2_japon: 0 meses" not in nuevo["validacion"]
    # Sin anclas, el balance del PBoC se calcula y no se publica.
    pboc = fichas.loc[fichas["serie"] == "balance_pboc"].iloc[0]
    assert pboc["publicada"] == "no" and pboc["estado"] == NO_MEDIDO_SIN_VALIDACION
    # El rótulo de la OCDE va en el nombre, y las pendientes están como NO MEDIDO.
    assert fichas.loc[fichas["serie"] == "dinero_amplio_china", "nombre"].iloc[0] == "Dinero amplio de China (M3 de la OCDE)"
    assert fichas.loc[fichas["serie"] == "dinero_eeuu_1947_1958", "estado"].iloc[0].startswith("NO MEDIDO")

    dinero = pd.read_csv(series / "d0_dinero.csv", dtype={"mes": str})
    assert "balance_pboc" not in set(dinero["serie"])
    m2cd = dinero.loc[dinero["serie"] == CLAVE_M2CD_1998_2008]
    assert m2cd["mes"].iloc[0] == "1998-04" and m2cd["mes"].iloc[-1] == "2008-04"
    assert m2cd.loc[m2cd["mes"] == "2003-04", "quiebre"].iloc[0].startswith("empieza el M2")
    balances = pd.read_csv(series / "d0_balances.csv", dtype={"mes": str})
    fed = balances.loc[balances["serie"] == "balance_fed"]
    assert fed["mes"].iloc[-1] == "2026-09" and fed["fecha_origen"].iloc[-1] == "2026-09-30"
    agregado = pd.read_csv(series / "d0_agregado.csv", dtype={"mes": str})
    assert agregado["mes"].iloc[0] == "2025-01" and agregado["mes"].iloc[-1] == "2026-08"
    fila = agregado.iloc[0]
    assert fila["agregado_usd"] == pytest.approx(fila["m2_eeuu_usd"] + fila["m2_eurozona_usd"] + fila["m2_japon_usd"])
    assert fila["agregado_usd_tc_constante"] == pytest.approx(fila["agregado_usd"])
    # A-D0-36: sin tipo de cambio antes de 2025 en estas fuentes de prueba, Japón entra solo con el M2 actual.
    assert set(agregado["serie_japon"]) == {"m2_japon"}
    assert (agregado["quiebre"].fillna("") == "").all()
    cambio = pd.read_csv(series / "d0_cambio.csv", dtype={"mes": str})
    eur = cambio.loc[cambio["par"] == "usd_por_eur"]
    assert eur["mes"].iloc[-1] == "2026-09" and pd.isna(eur["fin_de_mes"].iloc[-1])  # mes en curso: sin fin de mes

    # Idempotencia: los CSV salen iguales byte a byte. El changelog describe la
    # corrida, y la segunda del día ya no es la primera publicación: lo que se
    # exige es que quede una sola entrada y sin revisiones.
    antes = {ruta.name: ruta.read_bytes() for ruta in series.glob("*.csv")}
    assert denominador.main(["--fecha-descarga", FECHA.isoformat()]) == 0
    despues = {ruta.name: ruta.read_bytes() for ruta in series.glob("*.csv")}
    assert antes == despues
    changelog = (series / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.count("## 2026-10-05 · denominador") == 1
    assert "Revisiones de datos históricos: ninguna" in changelog
    assert "primera publicación" not in changelog


def test_sin_copia_del_bce_la_serie_queda_no_medido_y_la_corrida_sigue(entorno):
    crudo, privado, series = entorno
    _sembrar(crudo, privado, FECHA.isoformat(), con_bce=False)
    assert denominador.main(["--fecha-descarga", FECHA.isoformat()]) == 0
    fichas = pd.read_csv(series / "d0_fichas.csv", dtype=str, keep_default_na=False)
    eurozona = fichas.loc[fichas["serie"] == "m2_eurozona"].iloc[0]
    assert eurozona["publicada"] == "no" and "copia bajada a mano" in eurozona["estado"]
    assert fichas.loc[fichas["serie"] == "m2_eeuu", "publicada"].iloc[0] == "sí"
    # Sin la Eurozona no hay agregado, y se dice.
    assert pd.read_csv(series / "d0_agregado.csv").empty
    assert "el agregado no se calcula" in (series / "CHANGELOG.md").read_text(encoding="utf-8")


def test_el_robots_veda_una_fuente_y_la_serie_lo_dice(entorno, monkeypatch):
    crudo, privado, series = entorno
    _sembrar(crudo, privado, FECHA.isoformat())
    # Falta el crudo del BoJ: habría que pedirlo, y el robots.txt fingido veda todo.
    (crudo / f"boj_m2_{FECHA.isoformat()}.csv").unlink()
    assert denominador.main(["--fecha-descarga", FECHA.isoformat()]) == 0
    fichas = pd.read_csv(series / "d0_fichas.csv", dtype=str, keep_default_na=False)
    assert fichas.loc[fichas["serie"] == "m2_japon", "estado"].iloc[0] == NO_MEDIDO_ACCESO_VEDADO


def test_un_gate_que_no_cierra_deja_la_serie_sin_publicar(entorno):
    crudo, privado, series = entorno
    _sembrar(crudo, privado, FECHA.isoformat())
    # El e-Stat dice otra cosa que el BoJ en un mes.
    torcida = datos.m2_japon().copy()
    torcida.iloc[3] += 1.0
    (privado / f"estat_m2_japon_{FECHA.isoformat()}.json").write_text(datos.json_estat(torcida, ESTAT_INDICADOR_M2), encoding="utf-8")
    assert denominador.main(["--fecha-descarga", FECHA.isoformat()]) == 0
    fichas = pd.read_csv(series / "d0_fichas.csv", dtype=str, keep_default_na=False)
    japon = fichas.loc[fichas["serie"] == "m2_japon"].iloc[0]
    assert japon["publicada"] == "no" and japon["estado"] == NO_MEDIDO_SIN_VALIDACION
    assert "2025-04" in japon["validacion"] or "1 fuera" in japon["validacion"]


# --- Japón por tramos (A-D0-34 a A-D0-36) ---------------------------------------


def _mensual(valores: dict[str, float]) -> denominador.SerieConstruida:
    indice = pd.DatetimeIndex([pd.Timestamp(f"{mes}-01") for mes in valores], name="mes")
    return denominador.SerieConstruida(pd.Series(list(valores.values()), index=indice, dtype=float))


def test_recortar_toma_los_meses_entre_dos_limites_inclusive():
    serie = _mensual({"2003-02": 1.0, "2003-03": 2.0, "2003-04": 3.0}).valores
    assert list(denominador._recortar(serie, None, "2003-03")) == [1.0, 2.0]
    assert list(denominador._recortar(serie, "2003-03", None)) == [2.0, 3.0]
    assert list(denominador._recortar(serie, "2003-03", "2003-03")) == [2.0]


def test_la_superposicion_se_mide_y_no_se_corrige():
    series = {
        CLAVE_M2CD_1998_2008: _mensual({"2003-03": 100.0, "2003-04": 100.0, "2003-05": 200.0}),
        "m2_japon": _mensual({"2003-04": 99.5, "2003-05": 199.2, "2003-06": 300.0}),
    }
    nota = denominador.superposicion(series, CLAVE_M2CD_1998_2008)
    assert nota.startswith("superposición con m2_japon: 2 meses, m2_japon entre -0.500 % y -0.400 %")
    assert nota.endswith("no se empalma")
    assert denominador.superposicion(series, "m2_japon") == ""


def test_el_dinero_de_japon_del_agregado_concatena_los_tramos_sin_empalme():
    series = {
        CLAVE_M2CD_1998_2008: _mensual({"2003-02": 100.0, "2003-03": 101.0, "2003-04": 102.0, "2003-05": 103.0}),
        "m2_japon": _mensual({"2003-03": 90.0, "2003-04": 99.0, "2003-05": 100.0}),
    }
    valores, etiquetas = denominador._dinero_del_agregado("japon", "m2_japon", series)
    assert list(valores) == [100.0, 101.0, 99.0, 100.0]  # hasta 2003-03 el tramo viejo, después el M2 actual tal cual
    assert list(etiquetas) == [CLAVE_M2CD_1998_2008, CLAVE_M2CD_1998_2008, "m2_japon", "m2_japon"]
    valores_eeuu, etiquetas_eeuu = denominador._dinero_del_agregado("eeuu", "m2_eeuu_sin_ajustar", {"m2_eeuu_sin_ajustar": _mensual({"2003-03": 1.0})})
    assert list(valores_eeuu) == [1.0] and list(etiquetas_eeuu) == ["m2_eeuu_sin_ajustar"]


def test_el_agregado_declara_el_quiebre_de_japon_en_el_mes_del_cambio():
    meses = {"2003-02": 0.0, "2003-03": 0.0, "2003-04": 0.0, "2003-05": 0.0}
    series = {
        "m2_eeuu_sin_ajustar": _mensual({m: 6000.0 for m in meses}),
        "m2_eurozona_sin_ajustar": _mensual({m: 5_000_000.0 for m in meses}),
        CLAVE_M2CD_1998_2008: _mensual({m: 6_800_000.0 for m in meses}),
        "m2_japon": _mensual({m: 6_766_000.0 for m in meses}),  # 0.5 % menos que M2+CDs
    }
    indice = pd.DatetimeIndex([pd.Timestamp(f"{m}-01") for m in meses], name="mes")
    fines = pd.DataFrame({"fin_de_mes": [1.1] * 4, "fecha_fin_de_mes": indice}, index=indice)
    series["usd_por_eur"] = denominador.SerieConstruida(pd.Series([1.1] * 4, index=indice), fin_de_mes=fines)
    series["jpy_por_usd"] = denominador.SerieConstruida(pd.Series([120.0] * 4, index=indice))
    publicadas = set(series)
    tabla, notas = denominador.agregado(series, publicadas)
    assert list(tabla["mes"]) == ["2003-02", "2003-03", "2003-04", "2003-05"]
    assert list(tabla["serie_japon"]) == [CLAVE_M2CD_1998_2008, CLAVE_M2CD_1998_2008, "m2_japon", "m2_japon"]
    assert tabla["m2_japon_usd"].iloc[1] == pytest.approx(6_800_000.0 / 120.0 / 10.0)
    assert tabla["m2_japon_usd"].iloc[2] == pytest.approx(6_766_000.0 / 120.0 / 10.0)
    quiebre = tabla.loc[tabla["mes"] == "2003-04", "quiebre"].iloc[0]
    assert quiebre.startswith("Japón pasa de m2cd_japon_1998_2008 a m2_japon, sin empalme: en este mes m2_japon es -0.500 %")
    assert (tabla.loc[tabla["mes"] != "2003-04", "quiebre"] == "").all()
    assert any("quiebre declarado" in nota for nota in notas)
    # Sin el tramo antiguo publicado, el agregado no se calcula y lo dice.
    tabla_sin, notas_sin = denominador.agregado(series, publicadas - {CLAVE_M2CD_1998_2008})
    assert tabla_sin.empty and "faltan m2cd_japon_1998_2008" in notas_sin[0]
