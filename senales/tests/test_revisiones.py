"""Detección de revisiones históricas de FRED entre una corrida y la siguiente."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from senales import bitacora, fuentes_fred, liquidez_neta
from senales.bitacora import EntradaChangelog, detectar_revisiones, filas_agregadas
from senales.configuracion import COLUMNAS_REVISABLES, EPSILON_REVISION, SERIE_RRP, SERIE_TGA, SERIE_WALCL

FECHA_CORRIDA = "2026-09-22"


def _tabla(filas):
    return pd.DataFrame(
        {
            "fecha": pd.to_datetime([f[0] for f in filas]),
            "walcl": [f[1] for f in filas],
            "tga": [f[2] for f in filas],
            "rrp": [f[3] for f in filas],
            "s2_1_liquidez_neta": [f[1] - f[2] - f[3] for f in filas],
        }
    )


def test_sin_corrida_previa_no_hay_revisiones():
    nueva = _tabla([("2026-09-09", 6757.0, 889.0, 9.2)])
    assert detectar_revisiones(None, nueva, COLUMNAS_REVISABLES, EPSILON_REVISION) == []
    assert len(filas_agregadas(None, nueva)) == 1


def test_un_dato_historico_revisado_se_detecta():
    previa = _tabla([("2026-09-09", 6757.0, 889.0, 9.2)])
    nueva = _tabla([("2026-09-09", 6757.5, 889.0, 9.2)])
    revisiones = detectar_revisiones(previa, nueva, COLUMNAS_REVISABLES, EPSILON_REVISION)
    columnas = {r.columna for r in revisiones}
    assert columnas == {"walcl", "s2_1_liquidez_neta"}
    walcl = next(r for r in revisiones if r.columna == "walcl")
    assert walcl.diferencia == pytest.approx(0.5)
    assert "6757.000 -> 6757.500" in str(walcl)


def test_el_ruido_por_debajo_del_epsilon_no_se_reporta():
    previa = _tabla([("2026-09-09", 6757.0, 889.0, 9.2)])
    nueva = _tabla([("2026-09-09", 6757.0001, 889.0, 9.2)])
    assert detectar_revisiones(previa, nueva, COLUMNAS_REVISABLES, EPSILON_REVISION) == []


def test_una_fila_nueva_es_agregado_y_no_revision():
    previa = _tabla([("2026-09-09", 6757.0, 889.0, 9.2)])
    nueva = _tabla([("2026-09-09", 6757.0, 889.0, 9.2), ("2026-09-16", 6747.0, 877.0, 4.0)])
    assert detectar_revisiones(previa, nueva, COLUMNAS_REVISABLES, EPSILON_REVISION) == []
    agregadas = filas_agregadas(previa, nueva)
    assert [f.date().isoformat() for f in agregadas] == ["2026-09-16"]


def test_un_dato_que_desaparece_cuenta_como_revision():
    previa = _tabla([("2026-09-09", 6757.0, 889.0, 9.2)])
    nueva = previa.copy()
    nueva.loc[0, "walcl"] = float("nan")
    revisiones = detectar_revisiones(previa, nueva, COLUMNAS_REVISABLES, EPSILON_REVISION)
    assert any(r.columna == "walcl" for r in revisiones)


def test_la_revision_queda_escrita_en_el_changelog(tmp_path: Path):
    previa = _tabla([("2026-09-09", 6757.0, 889.0, 9.2)])
    nueva = _tabla([("2026-09-09", 6757.5, 889.0, 9.2)])
    revisiones = detectar_revisiones(previa, nueva, COLUMNAS_REVISABLES, EPSILON_REVISION)

    ruta = tmp_path / "CHANGELOG.md"
    entrada = EntradaChangelog(
        fecha_corrida=pd.Timestamp("2026-09-22").date(),
        rango_datos=(nueva["fecha"].iloc[0], nueva["fecha"].iloc[-1]),
        observaciones=len(nueva),
        agregadas=[],
        revisiones=revisiones,
        huecos=[],
        verificaciones_unidad=["WALCL: VERIFICADA"],
        resultado_validacion="OK",
        umbral="NO MEDIDO (A-S2-3)",
    )
    assert bitacora.actualizar_changelog(ruta, entrada) is True
    texto = ruta.read_text(encoding="utf-8")
    assert "Revisiones de datos históricos: 2" in texto
    assert "walcl: 6757.000 -> 6757.500 (0.500)" in texto
    # Volver a escribir lo mismo no cambia el archivo.
    assert bitacora.actualizar_changelog(ruta, entrada) is False


def test_de_punta_a_punta_una_revision_de_fred_aparece_en_el_changelog(
    tmp_path: Path, dir_fixtures: Path, monkeypatch
):
    crudo = tmp_path / "raw"
    series = tmp_path / "series"
    crudo.mkdir(parents=True)
    for serie, fixture in (
        (SERIE_WALCL, "WALCL_ejemplo.csv"),
        (SERIE_TGA, "WTREGEN_ejemplo.csv"),
        (SERIE_RRP, "RRPONTSYD_ejemplo.csv"),
    ):
        shutil.copy(dir_fixtures / fixture, crudo / f"{serie.id}_{FECHA_CORRIDA}.csv")

    monkeypatch.setattr(liquidez_neta, "DIR_CRUDO", crudo)
    monkeypatch.setattr(liquidez_neta, "DIR_SERIES", series)
    monkeypatch.setattr(liquidez_neta, "DIR_REPORTES", tmp_path / "reportes")
    monkeypatch.setattr(liquidez_neta, "ARCHIVO_SERIE", series / "liquidez_neta.csv")
    monkeypatch.setattr(liquidez_neta, "ARCHIVO_CHANGELOG", series / "CHANGELOG.md")
    monkeypatch.setattr(liquidez_neta, "ARCHIVO_GRAFICO", tmp_path / "reportes" / "g.png")
    monkeypatch.setattr(
        fuentes_fred, "unidad_declarada", lambda serie, sesion=None: serie.unidad_fred
    )

    assert liquidez_neta.main(["--fecha-descarga", FECHA_CORRIDA]) == 0

    # FRED revisa hacia atrás una semana ya publicada y se vuelve a correr al día siguiente.
    otra = "2026-09-23"
    origen = crudo / f"{SERIE_WALCL.id}_{FECHA_CORRIDA}.csv"
    revisado = origen.read_text(encoding="utf-8").replace(
        "2026-09-02,6768000", "2026-09-02,6769200"
    )
    (crudo / f"{SERIE_WALCL.id}_{otra}.csv").write_text(revisado, encoding="utf-8")
    for serie, fixture in ((SERIE_TGA, "WTREGEN_ejemplo.csv"), (SERIE_RRP, "RRPONTSYD_ejemplo.csv")):
        shutil.copy(dir_fixtures / fixture, crudo / f"{serie.id}_{otra}.csv")

    assert liquidez_neta.main(["--fecha-descarga", otra]) == 0
    texto = (series / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "2026-09-02 | walcl: 6768.000 -> 6769.200 (1.200)" in texto
    assert "Filas agregadas: 0" in texto
