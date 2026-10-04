"""Correr dos veces el mismo día no duplica filas ni entradas del changelog."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from senales import fuentes_fred, grafico, liquidez_neta
from senales.configuracion import COLUMNAS_SERIE, SERIE_RRP, SERIE_TGA, SERIE_WALCL
from tests.conftest import ruta_de_ejemplo

FECHA_CORRIDA = "2026-09-22"


@pytest.fixture
def entorno(tmp_path: Path, monkeypatch) -> dict[str, Path]:
    """Un arbol de salida aislado con las descargas del día ya presentes.

    Al dejar los archivos crudos en su lugar se ejercita el camino real de cache
    de descargar_csv, que devuelve el archivo existente sin tocar la red.
    """
    crudo = tmp_path / "data" / "raw"
    series = tmp_path / "data" / "series"
    reportes = tmp_path / "reportes"
    crudo.mkdir(parents=True)

    for serie in (SERIE_WALCL, SERIE_TGA, SERIE_RRP):
        shutil.copy(ruta_de_ejemplo(serie), crudo / f"{serie.id}_{FECHA_CORRIDA}.csv")

    monkeypatch.setattr(liquidez_neta, "DIR_CRUDO", crudo)
    monkeypatch.setattr(liquidez_neta, "DIR_SERIES", series)
    monkeypatch.setattr(liquidez_neta, "DIR_REPORTES", reportes)
    monkeypatch.setattr(liquidez_neta, "ARCHIVO_SERIE", series / "liquidez_neta.csv")
    monkeypatch.setattr(liquidez_neta, "ARCHIVO_CHANGELOG", series / "CHANGELOG.md")
    monkeypatch.setattr(liquidez_neta, "ARCHIVO_GRAFICO", reportes / "liquidez_neta.png")
    monkeypatch.setattr(
        fuentes_fred,
        "unidad_declarada",
        lambda serie, sesion=None: (serie.unidad_fred, "declarada por el doble de test"),
    )
    return {"crudo": crudo, "series": series, "reportes": reportes}


def _correr() -> int:
    return liquidez_neta.main(["--fecha-descarga", FECHA_CORRIDA])


def test_una_corrida_escribe_las_tres_salidas(entorno):
    assert _correr() == 0
    assert (entorno["series"] / "liquidez_neta.csv").exists()
    assert (entorno["series"] / "CHANGELOG.md").exists()
    assert (entorno["reportes"] / "liquidez_neta.png").exists()


def test_las_columnas_son_las_acordadas(entorno):
    _correr()
    tabla = pd.read_csv(entorno["series"] / "liquidez_neta.csv")
    assert list(tabla.columns) == COLUMNAS_SERIE


def test_dos_corridas_dejan_el_csv_identico(entorno):
    _correr()
    primera = (entorno["series"] / "liquidez_neta.csv").read_bytes()
    _correr()
    segunda = (entorno["series"] / "liquidez_neta.csv").read_bytes()
    assert primera == segunda
    assert len(pd.read_csv(entorno["series"] / "liquidez_neta.csv")) == 20


def test_dos_corridas_dejan_una_sola_entrada_en_el_changelog(entorno):
    _correr()
    _correr()
    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert texto.count(f"## {FECHA_CORRIDA}") == 1


def test_una_segunda_corrida_no_vuelve_a_descargar(entorno, monkeypatch):
    def prohibido(*args, **kwargs):
        raise AssertionError("no debería salir a la red: la descarga del día ya existe")

    monkeypatch.setattr(fuentes_fred.requests, "get", prohibido)
    assert _correr() == 0
    assert _correr() == 0


def test_el_archivo_crudo_del_dia_no_se_pisa(entorno):
    ruta = entorno["crudo"] / f"{SERIE_WALCL.id}_{FECHA_CORRIDA}.csv"
    antes = ruta.read_bytes()
    _correr()
    _correr()
    assert ruta.read_bytes() == antes


def test_una_corrida_de_otro_dia_agrega_su_propia_entrada(entorno):
    _correr()
    otra = "2026-09-23"
    for serie in (SERIE_WALCL, SERIE_TGA, SERIE_RRP):
        shutil.copy(ruta_de_ejemplo(serie), entorno["crudo"] / f"{serie.id}_{otra}.csv")
    assert liquidez_neta.main(["--fecha-descarga", otra]) == 0
    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert texto.count("## 2026-09-2") == 2
    # Más reciente primero.
    assert texto.index(f"## {otra}") < texto.index(f"## {FECHA_CORRIDA}")


def test_el_umbral_sin_definir_se_reporta_como_no_medido(entorno, capsys):
    _correr()
    salida = capsys.readouterr().out
    assert "NO MEDIDO (A-S2-3)" in salida
    texto = (entorno["series"] / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "NO MEDIDO (A-S2-3)" in texto


def test_si_la_validacion_falla_no_se_escribe_ninguna_serie(entorno):
    ruta = entorno["crudo"] / f"{SERIE_WALCL.id}_{FECHA_CORRIDA}.csv"
    texto = ruta.read_text(encoding="utf-8").replace("2026-09-16,6746548", "2026-09-16,6800000")
    ruta.write_text(texto, encoding="utf-8")

    assert liquidez_neta.main(["--fecha-descarga", FECHA_CORRIDA]) == 2
    assert not (entorno["series"] / "liquidez_neta.csv").exists()
    assert not (entorno["series"] / "CHANGELOG.md").exists()
    assert not (entorno["reportes"] / "liquidez_neta.png").exists()


def test_las_secciones_escritas_a_mano_sobreviven_a_las_corridas(entorno):
    """El registro de cambios de supuestos vive en el changelog y no lo pisa el script."""
    archivo = entorno["series"] / "CHANGELOG.md"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(
        "# Changelog de data/series\n"
        "\n"
        "## Cambios de supuestos\n"
        "\n"
        "- 2026-09-22 · A-S2-4: la serie de TGA pasa de WTREGEN a WDTGAL.\n",
        encoding="utf-8",
    )

    assert _correr() == 0
    texto = archivo.read_text(encoding="utf-8")
    assert "## Cambios de supuestos" in texto
    assert "A-S2-4: la serie de TGA pasa de WTREGEN a WDTGAL." in texto
    assert f"## {FECHA_CORRIDA}" in texto
    # La sección escrita a mano queda arriba de las entradas de corrida.
    assert texto.index("## Cambios de supuestos") < texto.index(f"## {FECHA_CORRIDA}")

    # Y sigue ahí después de una segunda corrida.
    assert _correr() == 0
    assert archivo.read_text(encoding="utf-8").count("## Cambios de supuestos") == 1


def test_el_grafico_nombra_las_series_configuradas(entorno, monkeypatch):
    """El título del gráfico sale de la configuración, no de un texto fijo.

    Si estuviera escrito a mano, cambiar la serie de TGA (A-S2-4) dejaría el
    gráfico nombrando una serie que ya no se usa.
    """
    capturado: dict[str, str] = {}
    original = grafico.dibujar

    def espia(*args, **kwargs):
        capturado.update(kwargs)
        return original(*args, **kwargs)

    monkeypatch.setattr(liquidez_neta.grafico, "dibujar", espia)
    assert _correr() == 0

    esperada = f"{SERIE_WALCL.id} \N{MINUS SIGN} {SERIE_TGA.id} \N{MINUS SIGN} {SERIE_RRP.id}"
    assert capturado["formula"] == esperada
    for serie in (SERIE_WALCL, SERIE_TGA, SERIE_RRP):
        assert serie.id in capturado["fuente"]
