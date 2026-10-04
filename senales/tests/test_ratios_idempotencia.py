"""La corrida de punta a punta: qué escribe, dónde, y que repetirla no cambia nada."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from senales import fuentes_precios, ratios
from senales.configuracion import (
    COLUMNAS_DESCARGAS,
    COLUMNAS_PRECIOS,
    DESCARGA_SHILLER,
    NO_MEDIDO_PERMISO,
    NO_MEDIDO_SIN_VALIDACION,
)
from senales.fuentes_fred import ErrorDeFuente
from senales.ratios import promedio_mensual
from tests.datos_ratios import (
    ORO,
    anclas_de_prueba,
    csv_fred,
    diaria_calendario,
    diaria_habil,
    documento_coin_metrics,
    escribir_pink_sheet,
    filas_shiller,
)

FECHA = "2026-10-04"

SHILLER = {"2026-03": 7000.0, "2026-04": 6900.0, "2026-05": 7400.0, "2026-06": 7450.0,
           "2026-07": 7480.0, "2026-08": 7700.0, "2026-09": 7630.0}

NASDAQ = pd.concat([
    pd.Series([100.0], index=pd.DatetimeIndex(["1971-02-05"])),
    diaria_habil("2026-02-02", "2026-10-02", base=20000.0, pendiente=30.0),
])
BTC = diaria_calendario("2026-02-01", "2026-10-03", base=60000.0, pendiente=80.0)


def _sembrar_crudos(crudo: Path, privado: Path, fecha: str, oro: dict | None = None) -> None:
    """Deja las cuatro descargas del día en su lugar, como si ya se hubieran bajado."""
    escribir_pink_sheet(crudo / f"pink_sheet_{fecha}.xlsx", oro=oro)
    # El .xls de Shiller no se puede fabricar sin la librería que escribe ese
    # formato. El archivo es un marcador y sus filas las entrega el doble de test.
    (privado / f"shiller_ie_data_{fecha}.xls").write_bytes(b"\xd0\xcf\x11\xe0 marcador de prueba")
    (privado / f"NASDAQCOM_{fecha}.csv").write_text(csv_fred("NASDAQCOM", NASDAQ), encoding="utf-8")
    (crudo / f"coin_metrics_btc_{fecha}.json").write_text(
        json.dumps(documento_coin_metrics(BTC)), encoding="utf-8"
    )


def _referencias(factor_btc: float = 1.01):
    """Las tres fuentes de contraste, a poca distancia de las series."""

    def obtener(fecha_descarga: date) -> dict[str, pd.Series]:
        sp500 = pd.Series(
            list(SHILLER.values()),
            index=pd.DatetimeIndex([pd.Timestamp(m + "-01") for m in SHILLER]),
        )
        return {
            "sp500": sp500 * 1.001,
            "nasdaq": promedio_mensual(NASDAQ, dias_calendario=False)[0] * 1.0005,
            "btc": promedio_mensual(BTC, dias_calendario=True)[0] * factor_btc,
        }

    return obtener


@pytest.fixture
def entorno(tmp_path: Path, monkeypatch) -> dict[str, Path]:
    crudo = tmp_path / "data" / "raw"
    series = tmp_path / "data" / "series"
    privado = tmp_path / "data" / "privado" / "raw"
    series_privado = tmp_path / "data" / "privado" / "series"
    for directorio in (crudo, series, privado, series_privado):
        directorio.mkdir(parents=True)
    _sembrar_crudos(crudo, privado, FECHA)

    # La primera corrida real deja en el manifiesto la fecha que declaró Shiller
    # en la cabecera HTTP. Acá se siembra esa fila, porque no hay descarga.
    marcador = privado / f"shiller_ie_data_{FECHA}.xls"
    fila = {
        "fecha_descarga": FECHA,
        "fuente": DESCARGA_SHILLER.clave,
        "clase_licencia": DESCARGA_SHILLER.clase_licencia,
        "licencia": DESCARGA_SHILLER.licencia,
        "url": "https://ejemplo.invalid/ie_data.xls",
        "bytes": marcador.stat().st_size,
        "sha256": fuentes_precios.sha256_de(marcador),
        "actualizada": "2026-09-02",
        "crudo_en_repo": "no",
    }
    pd.DataFrame([fila], columns=COLUMNAS_DESCARGAS).to_csv(
        series / "descargas_ratios.csv", index=False, lineterminator="\n"
    )

    rutas = {
        "DIR_CRUDO": crudo,
        "DIR_CRUDO_PRIVADO": privado,
        "DIR_SERIES": series,
        "DIR_SERIES_PRIVADO": series_privado,
        "ARCHIVO_PRECIOS": series / "precios_mensuales.csv",
        "ARCHIVO_RATIOS": series / "ratios.csv",
        "ARCHIVO_PARES": series / "pares.csv",
        "ARCHIVO_SERIES_INFO": series / "series.csv",
        "ARCHIVO_DESCARGAS": series / "descargas_ratios.csv",
        "ARCHIVO_INTERNO": series_privado / "ratios_internos.csv",
        "ARCHIVO_CHANGELOG": series / "CHANGELOG.md",
    }
    for nombre, ruta in rutas.items():
        monkeypatch.setattr(ratios, nombre, ruta)
    monkeypatch.setattr(fuentes_precios, "filas_de_xls", lambda ruta, hoja: filas_shiller(SHILLER))
    monkeypatch.setattr(ratios, "obtener_referencias", _referencias())
    # Las anclas reales del USGS son de 2021 a 2024; los datos de prueba, de 2023 a
    # 2026. Acá el gate cierra contra anclas hechas para estos datos.
    monkeypatch.setattr(ratios, "ANCLAS_USGS", anclas_de_prueba())

    def prohibido(*args, **kwargs):
        raise AssertionError("ningún test sale a la red")

    monkeypatch.setattr(fuentes_precios.requests, "get", prohibido)
    return {"crudo": crudo, "series": series, "privado": privado, "series_privado": series_privado}


def _correr(fecha: str = FECHA) -> int:
    return ratios.main(["--fecha-descarga", fecha])


PUBLICOS = (
    "precios_mensuales.csv", "ratios.csv", "pares.csv", "series.csv",
    "descargas_ratios.csv", "CHANGELOG.md",
)


def test_una_corrida_escribe_las_salidas_publicas_y_la_interna(entorno):
    assert _correr() == 0
    for nombre in PUBLICOS:
        assert (entorno["series"] / nombre).exists(), nombre
    assert (entorno["series_privado"] / "ratios_internos.csv").exists()


def test_dos_corridas_dejan_las_series_identicas(entorno):
    series = [n for n in PUBLICOS if n.endswith(".csv")]
    _correr()
    antes = {n: (entorno["series"] / n).read_bytes() for n in series}
    interno = (entorno["series_privado"] / "ratios_internos.csv").read_bytes()
    assert _correr() == 0
    assert {n: (entorno["series"] / n).read_bytes() for n in series} == antes
    assert (entorno["series_privado"] / "ratios_internos.csv").read_bytes() == interno


def test_el_changelog_refleja_la_ultima_corrida_del_dia_y_despues_no_cambia(entorno):
    """A-S2-11: la segunda corrida del día reemplaza la entrada; la tercera no la toca."""
    _correr()
    primera = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "primera publicación" in primera
    _correr()
    segunda = (entorno["series"] / "CHANGELOG.md").read_bytes()
    _correr()
    assert (entorno["series"] / "CHANGELOG.md").read_bytes() == segunda


def test_dos_corridas_dejan_una_sola_entrada_en_el_changelog(entorno):
    _correr()
    _correr()
    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert texto.count(f"## {FECHA} · ratios") == 1


def test_los_crudos_del_dia_no_se_pisan(entorno):
    rutas = list(entorno["crudo"].iterdir()) + list(entorno["privado"].iterdir())
    antes = {ruta: ruta.read_bytes() for ruta in rutas}
    _correr()
    _correr()
    assert {ruta: ruta.read_bytes() for ruta in rutas} == antes


def test_el_directorio_publico_solo_recibe_los_crudos_que_se_pueden_redistribuir(entorno):
    """A-R0-15: Pink Sheet (CC BY) y Coin Metrics (CC BY-NC). Shiller y FRED, no."""
    _correr()
    assert sorted(ruta.name for ruta in entorno["crudo"].iterdir()) == [
        f"coin_metrics_btc_{FECHA}.json",
        f"pink_sheet_{FECHA}.xlsx",
    ]
    assert sorted(ruta.name for ruta in entorno["privado"].iterdir()) == [
        f"NASDAQCOM_{FECHA}.csv",
        f"shiller_ie_data_{FECHA}.xls",
    ]


def test_lo_publicado_no_trae_ningun_numero_de_los_indices(entorno):
    """A-R0-14: los índices y sus pares se calculan, y lo que se publica es NO MEDIDO."""
    _correr()
    precios = pd.read_csv(entorno["series"] / "precios_mensuales.csv")
    assert list(precios.columns) == COLUMNAS_PRECIOS
    largos = pd.read_csv(entorno["series"] / "ratios.csv")
    assert set(largos["par"]) == {"oro_plata", "btc_oro"}

    pares = pd.read_csv(entorno["series"] / "pares.csv").set_index("par")
    for clave in ("oro_sp500", "btc_sp500", "nasdaq_sp500"):
        assert pares.loc[clave, "estado"] == NO_MEDIDO_PERMISO
        assert pares.loc[clave, "publicado"] == "no"

    interno = pd.read_csv(entorno["series_privado"] / "ratios_internos.csv")
    assert interno["sp500"].notna().any() and interno["nasdaq_sp500"].notna().any()
    # Ningún valor calculado con un índice aparece en un archivo público.
    publico = "".join(
        (entorno["series"] / n).read_text(encoding="utf-8")
        for n in ("precios_mensuales.csv", "ratios.csv", "pares.csv", "series.csv")
    )
    for valor in interno["nasdaq_sp500"].dropna():
        assert f"{valor:.10g}" not in publico


def test_cada_par_llega_hasta_el_ultimo_mes_completo_de_sus_dos_fuentes(entorno):
    """El archivo de Shiller se actualizó el 2 de septiembre: septiembre no entra."""
    _correr()
    pares = pd.read_csv(entorno["series"] / "pares.csv").set_index("par")
    assert pares.loc["oro_plata", "ultimo_mes"] == "2026-09"
    assert pares.loc["btc_oro", "ultimo_mes"] == "2026-09"
    assert pares.loc["oro_sp500", "ultimo_mes"] == "2026-08"
    assert pares.loc["nasdaq_sp500", "ultimo_mes"] == "2026-08"


def test_el_manifiesto_publica_url_fecha_y_hash_de_cada_descarga(entorno):
    _correr()
    tabla = pd.read_csv(entorno["series"] / "descargas_ratios.csv", dtype=str, keep_default_na=False)
    assert set(tabla["fuente"]) == {"pink_sheet", "shiller_ie_data", "NASDAQCOM", "coin_metrics_btc"}
    assert (tabla["fecha_descarga"] == FECHA).all()
    assert tabla["sha256"].str.fullmatch(r"[0-9a-f]{64}").all()
    en_repo = dict(zip(tabla["fuente"], tabla["crudo_en_repo"]))
    assert en_repo == {
        "pink_sheet": "sí", "shiller_ie_data": "no", "NASDAQCOM": "no", "coin_metrics_btc": "sí",
    }


def test_un_contraste_que_no_cierra_detiene_la_corrida_sin_publicar(entorno, monkeypatch, capsys):
    monkeypatch.setattr(ratios, "obtener_referencias", _referencias(factor_btc=1.05))
    assert _correr() == ratios.CODIGO_VALIDACION_FALLIDA
    assert not (entorno["series"] / "precios_mensuales.csv").exists()
    assert not (entorno["series"] / "ratios.csv").exists()
    assert not (entorno["series"] / "CHANGELOG.md").exists()
    assert not (entorno["series_privado"] / "ratios_internos.csv").exists()
    error = capsys.readouterr().err
    assert "No ajustar la tolerancia" in error
    # El manifiesto registra lo que se bajó, cierre o no la validación.
    assert len(pd.read_csv(entorno["series"] / "descargas_ratios.csv")) == 4


def test_una_fuente_de_contraste_inalcanzable_es_un_error_de_fuente(entorno, monkeypatch):
    def caida(fecha_descarga):
        raise ErrorDeFuente("no se pudo leer https://www.bitstamp.net/: sin conexión")

    monkeypatch.setattr(ratios, "obtener_referencias", caida)
    assert _correr() == ratios.CODIGO_ERROR_FUENTE
    assert not (entorno["series"] / "precios_mensuales.csv").exists()


def test_sin_el_crudo_y_sin_red_la_corrida_no_inventa_nada(entorno, monkeypatch):
    def sin_conexion(*args, **kwargs):
        raise fuentes_precios.requests.ConnectionError("sin conexión")

    monkeypatch.setattr(fuentes_precios.requests, "get", sin_conexion)
    (entorno["privado"] / f"NASDAQCOM_{FECHA}.csv").unlink()
    assert _correr() == ratios.CODIGO_ERROR_FUENTE
    assert not (entorno["series"] / "precios_mensuales.csv").exists()


def test_una_revision_de_la_fuente_queda_anotada_en_el_changelog(entorno):
    """Una corrida de otro día, con un dato histórico distinto, lo deja escrito."""
    _correr()
    otra = "2026-11-03"
    revisado = {**ORO, "2026-08": ORO["2026-08"] + 10.0}
    _sembrar_crudos(entorno["crudo"], entorno["privado"], otra, oro=revisado)
    assert _correr(otra) == 0

    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert texto.index(f"## {otra} · ratios") < texto.index(f"## {FECHA} · ratios")
    entrada = texto[texto.index(f"## {otra} · ratios") : texto.index(f"## {FECHA} · ratios")]
    assert "2026-08-01 | oro_usd_oz: 4400.000 -> 4410.000" in entrada
    assert "2026-08-01 | oro_plata" in entrada
    assert "2026-08-01 | btc_oro" in entrada


def test_cada_serie_lleva_su_atribucion_su_estado_y_con_que_se_valida(entorno):
    """CC BY y CC BY-NC exigen atribución; A-R0-8 y A-R0-16 exigen decir lo que falta."""
    _correr()
    tabla = pd.read_csv(entorno["series"] / "series.csv", keep_default_na=False).set_index("serie")
    assert list(tabla.index) == ["oro", "plata", "btc", "sp500", "nasdaq"]
    assert dict(tabla["publicada"]) == {"oro": "sí", "plata": "sí", "btc": "sí", "sp500": "no", "nasdaq": "no"}
    assert "The World Bank" in tabla.loc["oro", "atribucion"]
    assert "CC BY-NC 4.0" in tabla.loc["btc", "atribucion"]
    assert tabla.loc["plata", "estado"] == "estimación"
    for metal in ("oro", "plata"):
        assert "gate anual contra el precio promedio del USGS" in tabla.loc[metal, "validacion"]
        assert "cerró en 3 de 3 años" in tabla.loc[metal, "validacion"]
    assert "Bitstamp" in tabla.loc["btc", "validacion"]


def test_el_changelog_no_trae_ningun_nivel_de_los_indices(entorno):
    """A-R0-12: del S&P 500 y del Nasdaq queda la fecha del peor mes, la diferencia,
    la mediana y la cantidad de meses. Ningún nivel, ni propio ni de contraste."""
    _correr()
    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    lineas = [l for l in texto.splitlines() if "S&P 500 contra" in l or "Nasdaq Composite contra" in l]
    assert len(lineas) == 2
    for linea in lineas:
        assert " meses, diferencia mediana " in linea and " % en 2026-" in linea
        assert " contra " not in linea.split(" % en ", 1)[1], linea
    # El de BTC, que sí se publica, conserva sus dos valores.
    btc = next(l for l in texto.splitlines() if "BTC contra Bitstamp" in l)
    assert " contra " in btc.split(" % en ", 1)[1]
    interno = pd.read_csv(entorno["series_privado"] / "ratios_internos.csv")
    for columna in ("sp500", "nasdaq"):
        for valor in interno[columna].dropna():
            assert f"{valor:.4f}" not in texto


# --- A-R0-14 y A-R0-16: sin validación externa no se publica -----------------


def _publicos(entorno) -> dict[str, pd.DataFrame]:
    return {
        nombre: pd.read_csv(entorno["series"] / f"{nombre}.csv", keep_default_na=False)
        for nombre in ("precios_mensuales", "ratios", "pares", "series")
    }


def test_si_el_gate_del_oro_no_cierra_el_oro_y_sus_pares_salen_como_no_medido(entorno, monkeypatch, capsys):
    """El oro se aparta 2 % de su ancla: no hay validación, y no hay publicación."""
    monkeypatch.setattr(ratios, "ANCLAS_USGS", anclas_de_prueba(factor_oro=1.02))
    assert _correr() == 0, "la corrida sigue: BTC y los índices tienen su propio contraste"
    tablas = _publicos(entorno)

    precios = tablas["precios_mensuales"]
    assert set(precios["oro_usd_oz"]) == {""} and set(precios["oro_definicion"]) == {""}
    assert (precios["plata_usd_oz"] != "").any(), "la plata cerró su gate y se publica"

    assert tablas["ratios"].empty, "los dos pares publicables llevan oro"
    pares = tablas["pares"].set_index("par")
    assert pares.loc["oro_plata", "estado"] == NO_MEDIDO_SIN_VALIDACION
    assert pares.loc["btc_oro", "estado"] == NO_MEDIDO_SIN_VALIDACION
    assert pares.loc["oro_sp500", "estado"] == NO_MEDIDO_PERMISO
    assert set(pares["publicado"]) == {"no"}

    series = tablas["series"].set_index("serie")
    assert series.loc["oro", "estado"] == NO_MEDIDO_SIN_VALIDACION
    assert "NO cerró (0 de 3 años)" in series.loc["oro", "validacion"]
    assert series.loc["plata", "publicada"] == "sí"

    assert "El gate de oro no cerró" in capsys.readouterr().err
    # Se calcula igual: el oro y sus pares están en la tabla interna.
    interno = pd.read_csv(entorno["series_privado"] / "ratios_internos.csv")
    assert interno["oro"].notna().any() and interno["btc_oro"].notna().any()


def test_si_no_cierra_ningun_gate_solo_se_publica_btc(entorno, monkeypatch):
    monkeypatch.setattr(ratios, "ANCLAS_USGS", anclas_de_prueba(factor_oro=1.02, factor_plata=0.97))
    assert _correr() == 0
    tablas = _publicos(entorno)
    precios = tablas["precios_mensuales"]
    assert set(precios["oro_usd_oz"]) == {""} and set(precios["plata_usd_oz"]) == {""}
    assert (precios["btc_usd"] != "").all()
    assert tablas["ratios"].empty
    assert dict(zip(tablas["series"]["serie"], tablas["series"]["publicada"])) == {
        "oro": "no", "plata": "no", "btc": "sí", "sp500": "no", "nasdaq": "no",
    }


def test_sin_anclas_no_hay_gate_y_no_hay_publicacion(entorno, monkeypatch):
    """Sin un caso de validación externa, un metal no se publica."""
    monkeypatch.setattr(ratios, "ANCLAS_USGS", ())
    assert _correr() == 0
    series = _publicos(entorno)["series"].set_index("serie")
    assert series.loc["oro", "estado"] == NO_MEDIDO_SIN_VALIDACION
    assert series.loc["plata", "estado"] == NO_MEDIDO_SIN_VALIDACION


def test_un_gate_que_deja_de_cerrar_se_anota_como_un_solo_hecho(entorno, monkeypatch):
    """Si el oro se publicó ayer y hoy no cierra, el changelog lo dice en una línea."""
    assert _correr() == 0
    monkeypatch.setattr(ratios, "ANCLAS_USGS", anclas_de_prueba(factor_oro=1.02))
    assert _correr() == 0
    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "oro_usd_oz: dejó de publicarse en esta corrida" in texto
    assert "oro_plata: dejó de publicarse en esta corrida" in texto
    assert texto.count(" | oro_usd_oz: ") == 0, "no una revisión por cada mes"


def test_lo_publicado_lleva_el_error_por_redondeo_y_la_marca_de_apto(entorno):
    """A-R0-17."""
    _correr()
    precios = pd.read_csv(entorno["series"] / "precios_mensuales.csv")
    assert (precios["oro_error_redondeo_pct"].dropna() > 0).all()
    assert (precios["plata_error_redondeo_pct"].dropna() > 0).all()
    largos = pd.read_csv(entorno["series"] / "ratios.csv")
    assert set(largos["apto_metricas"]) <= {"sí", "no"}
    oro_plata = largos[largos["par"] == "oro_plata"]
    btc_oro = largos[largos["par"] == "btc_oro"]
    # Oro/Plata suma dos errores; BTC/Oro, solo el del oro.
    assert oro_plata["error_redondeo_pct"].min() > btc_oro["error_redondeo_pct"].max()
    pares = pd.read_csv(entorno["series"] / "pares.csv", keep_default_na=False).set_index("par")
    assert pares.loc["oro_plata", "apto_desde"] == "2023-01"
    assert int(pares.loc["oro_plata", "meses_aptos"]) == len(oro_plata)
