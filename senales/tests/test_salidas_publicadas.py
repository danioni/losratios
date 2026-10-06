"""Las salidas publicadas en data/series/ tienen que salir de los insumos publicados.

Cada test recalcula una salida con el código de la rama, a partir de lo que
está en el repositorio, y la compara byte a byte con la que está versionada.
Si alguien publica una salida calculada con otros insumos (lo que pasó en la
primera corrida del PR #4, cuando la suite de tests pisó los pares contra M2
con datos de prueba), el test falla.

Qué se recalcula y desde dónde:

| Salida | Insumos publicados |
| --- | --- |
| liquidez_neta.csv | los tres CSV de FRED de la última corrida, en data/raw |
| ratios.csv y pares.csv (pares publicados) | precios_mensuales.csv y series.csv |
| denominador_ratios.csv y denominador_pares.csv | precios_mensuales.csv, series.csv, denominador_dinero.csv y serie_D0.csv |
| denominador_agregado.csv | denominador_dinero.csv, denominador_tipos_de_cambio.csv y serie_D0.csv |
| crudos versionados | denominador_descargas.csv y descargas_ratios.csv (SHA-256) |

Qué no se puede recalcular aquí, y por qué: precios_mensuales.csv y series.csv
dependen de crudos que no viajan con el repositorio (Shiller y NASDAQCOM, A-R0-15)
y de contrastes que se leen de la red (A-R0-12); denominador_dinero.csv,
denominador_balances.csv, denominador_tipos_de_cambio.csv y serie_D0.csv
dependen de los ZIP de la Junta y de las fuentes de contraste, que quedan fuera
del repositorio (A-D0-27). De esos, el manifiesto publica URL, fecha y hash, y
la corrida se rehace con `--fecha-descarga` si los crudos están en disco. Las
filas de pares.csv de los pares que no se publican dependen de las series que
no se publican, y tampoco se recalculan.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd
import pytest

from senales import denominador, liquidez_neta, ratios
from senales.configuracion import (
    ARCHIVO_D0_AGREGADO,
    ARCHIVO_D0_CAMBIO,
    ARCHIVO_D0_DESCARGAS,
    ARCHIVO_D0_DINERO,
    ARCHIVO_D0_FICHAS,
    ARCHIVO_D0_PARES,
    ARCHIVO_D0_RATIOS,
    ARCHIVO_DESCARGAS,
    ARCHIVO_PARES,
    ARCHIVO_RATIOS,
    ARCHIVO_SERIE,
    COLUMNAS_D0_AGREGADO,
    COLUMNAS_PARES,
    COLUMNAS_RATIOS,
    COLUMNAS_SERIE,
    DIR_CRUDO,
    FORMATO_D0,
    FORMATO_RATIOS,
    PARES,
    SERIE_RRP,
    SERIE_TGA,
    SERIE_WALCL,
)
from senales.fuentes_fred import leer_csv_crudo
from senales.nucleo import FORMATO_FLOTANTE, escribir_csv_determinista


def _bytes(ruta: Path) -> bytes:
    return ruta.read_bytes().replace(b"\r\n", b"\n")


def _escribir(tmp_path: Path, nombre: str, tabla: pd.DataFrame, columnas: list[str], formato: str) -> bytes:
    ruta = tmp_path / nombre
    escribir_csv_determinista(tabla, ruta, columnas, formato)
    return _bytes(ruta)


def _ultima_fecha_de(serie_id: str) -> str:
    fechas = sorted(
        m.group(1)
        for ruta in DIR_CRUDO.glob(f"{serie_id}_*.csv")
        if (m := re.match(rf"{serie_id}_(\d{{4}}-\d{{2}}-\d{{2}})\.csv$", ruta.name))
    )
    assert fechas, f"no hay crudos de {serie_id} en data/raw"
    return fechas[-1]


def test_liquidez_neta_sale_de_sus_crudos(tmp_path):
    """S2: la serie publicada es la que dan los tres crudos de FRED de su última corrida."""
    fecha = _ultima_fecha_de(SERIE_WALCL.id)
    series = {
        serie.id: leer_csv_crudo(DIR_CRUDO / f"{serie.id}_{fecha}.csv", serie)
        for serie in (SERIE_WALCL, SERIE_TGA, SERIE_RRP)
    }
    tabla = liquidez_neta.construir_serie(series[SERIE_WALCL.id], series[SERIE_TGA.id], series[SERIE_RRP.id])
    recalculada = _escribir(
        tmp_path, "liquidez_neta.csv", liquidez_neta._preparar_para_csv(tabla), COLUMNAS_SERIE, FORMATO_FLOTANTE
    )
    assert recalculada == _bytes(ARCHIVO_SERIE)


def test_ratios_y_pares_publicados_salen_de_precios_mensuales(tmp_path):
    """Fase R: ratios.csv, y las filas de pares.csv de los pares publicados.

    La fase R divide los precios con todos sus decimales y publica
    precios_mensuales.csv con diez cifras significativas (FORMATO_RATIOS), así
    que el ratio recalculado desde el CSV puede diferir del publicado en la
    décima cifra. Por eso la columna `valor` se compara con una tolerancia
    relativa de 1e-9, y todo lo demás byte a byte. Que ratios.csv salga byte a
    byte de lo publicado exige recalcular la fase R desde los precios tal como
    se publican, en una corrida completa: queda para un PR propio.
    """
    precios, pasos, validadas, disputas = ratios.precios_publicados()
    pares = ratios.calcular_pares(precios, PARES)
    errores = ratios.errores_de_pares(precios, pasos, PARES)
    tabla_ratios = ratios.tabla_ratios(pares, errores, validadas, disputas, PARES)
    recalculado = _escribir(tmp_path, "ratios.csv", tabla_ratios, COLUMNAS_RATIOS, FORMATO_RATIOS).splitlines()
    publicado = _bytes(ARCHIVO_RATIOS).splitlines()
    assert len(recalculado) == len(publicado)
    for a, b in zip(recalculado, publicado):
        ca, cb = a.split(b","), b.split(b",")
        assert ca[:2] + ca[3:] == cb[:2] + cb[3:], (a, b)
        if ca[2] != cb[2]:
            assert abs(float(ca[2]) - float(cb[2])) <= 1e-9 * abs(float(cb[2])), (a, b)

    tabla_pares = ratios.tabla_pares(pares, errores, validadas, disputas, PARES)
    publicados = tabla_pares.loc[tabla_pares["publicado"] == "sí"]
    recalculado = _escribir(tmp_path, "pares.csv", publicados, COLUMNAS_PARES, FORMATO_RATIOS).splitlines()
    publicado = pd.read_csv(ARCHIVO_PARES, dtype=str, keep_default_na=False)
    assert set(publicado.loc[publicado["publicado"] == "sí", "par"]) == set(publicados["par"])
    lineas_publicadas = [
        linea for linea in _bytes(ARCHIVO_PARES).splitlines() if any(linea.startswith(f"{p},".encode()) for p in publicados["par"])
    ]
    assert recalculado[1:] == lineas_publicadas


def test_pares_contra_m2_salen_de_los_insumos_publicados(tmp_path):
    """A-D0-21: denominador_ratios.csv y denominador_pares.csv, desde los CSV publicados."""
    precios, pasos, validadas, disputas = ratios.precios_publicados()
    m2, motivo = ratios.cargar_m2_publicado(ARCHIVO_D0_FICHAS, ARCHIVO_D0_DINERO)
    tabla_ratios, tabla_pares, _ = ratios.pares_denominador(precios, pasos, validadas, disputas, m2, motivo)
    assert _escribir(tmp_path, "r.csv", tabla_ratios, COLUMNAS_RATIOS, FORMATO_RATIOS) == _bytes(ARCHIVO_D0_RATIOS)
    assert _escribir(tmp_path, "p.csv", tabla_pares, COLUMNAS_PARES, FORMATO_RATIOS) == _bytes(ARCHIVO_D0_PARES)


def test_agregado_sale_de_dinero_y_tipos_de_cambio(tmp_path):
    """A-D0-10: denominador_agregado.csv, desde las series y los tipos de cambio publicados."""
    dinero = pd.read_csv(ARCHIVO_D0_DINERO, dtype={"mes": str})
    cambio = pd.read_csv(ARCHIVO_D0_CAMBIO, dtype={"mes": str, "fecha_fin_de_mes": str})
    fichas = pd.read_csv(ARCHIVO_D0_FICHAS, dtype=str, keep_default_na=False)
    publicadas = set(fichas.loc[fichas["publicada"] == "sí", "serie"])
    series = denominador.series_desde_publicadas(dinero, cambio)
    agregado, _ = denominador.agregado(series, publicadas)
    assert _escribir(tmp_path, "a.csv", agregado, COLUMNAS_D0_AGREGADO, FORMATO_D0) == _bytes(ARCHIVO_D0_AGREGADO)


@pytest.mark.parametrize("manifiesto", [ARCHIVO_D0_DESCARGAS, ARCHIVO_DESCARGAS])
def test_los_crudos_versionados_coinciden_con_su_manifiesto(manifiesto):
    """Cada crudo que viaja con el repositorio tiene el hash que publicó su manifiesto."""
    filas = pd.read_csv(manifiesto, dtype=str, keep_default_na=False)
    versionados = filas.loc[filas["crudo_en_repo"] == "sí"]
    assert not versionados.empty
    for fila in versionados.itertuples():
        # La edición congelada del Pink Sheet lleva en el nombre la fecha de la edición,
        # no la de la descarga (A-R0-19).
        candidatos = sorted(DIR_CRUDO.glob(f"{fila.fuente}_{fila.fecha_descarga}.*")) or sorted(
            DIR_CRUDO.glob(f"{fila.fuente}.*")
        )
        assert candidatos, f"falta el crudo de {fila.fuente} del {fila.fecha_descarga}"
        assert hashlib.sha256(candidatos[0].read_bytes()).hexdigest() == fila.sha256, candidatos[0].name
