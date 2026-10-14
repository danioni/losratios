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
| las series del BoJ en denominador_dinero.csv y denominador_balances.csv | boj_m2 y boj_balance de data/privado/raw, con el hash del manifiesto; solo si están en disco (A-D0-27) |
| dinero_eeuu_historico.csv | las dos transcripciones de data/raw/transcripcion_junta_1892_1958/ y las filas de serie_D0.csv que dicen qué se publica |
| numerador_series.csv | los crudos versionados de N0 (Coin Metrics, Data Series 140, tablas del Z.1, Censo), las lecturas a mano de configuracion.py y las filas de serie_N0.csv que dicen qué se publica |

Qué no se puede recalcular aquí, y por qué: precios_mensuales.csv y series.csv
dependen de crudos que no viajan con el repositorio (Shiller y NASDAQCOM, A-R0-15)
y de contrastes que se leen de la red (A-R0-12); denominador_dinero.csv,
denominador_balances.csv, denominador_tipos_de_cambio.csv y serie_D0.csv
dependen de los ZIP de la Junta, de los crudos del BoJ y de las fuentes de
contraste, que quedan fuera del repositorio (A-D0-27). De esos, el manifiesto
publica URL, fecha y hash, y la corrida se rehace con `--fecha-descarga` si los
crudos están en disco. Los del BoJ son el único caso que este archivo
recalcula: cuando están en data/privado/raw, las series de Japón tienen que
salir de ellos; cuando no están (una clonación limpia), el test se omite y lo
dice. Las filas de pares.csv de los pares que no se publican dependen de las
series que no se publican, y tampoco se recalculan.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd
import pytest

from senales import denominador, dinero_historico, liquidez_neta, numerador, ratios, respuesta_oferta
from senales.configuracion import (
    ARCHIVO_D0_AGREGADO,
    ARCHIVO_D0_BALANCES,
    ARCHIVO_D0_CAMBIO,
    ARCHIVO_D0_DESCARGAS,
    ARCHIVO_D0_DINERO,
    ARCHIVO_D0_FICHAS,
    ARCHIVO_D0_PARES,
    ARCHIVO_D0_RATIOS,
    ARCHIVO_DESCARGAS,
    ARCHIVO_DINERO_HISTORICO,
    ARCHIVO_N0_DESCARGAS,
    ARCHIVO_N0_FICHAS,
    ARCHIVO_N0_SERIES,
    ARCHIVO_N1_COEFICIENTES,
    ARCHIVO_N1_DESCARGAS,
    ARCHIVO_N1_INSUMOS,
    ARCHIVO_N1_RESUMEN,
    ARCHIVO_PARES,
    ARCHIVO_RATIOS,
    ARCHIVO_SERIE,
    BOJ_CODIGO_BALANCE,
    BOJ_CODIGO_M2,
    BOJ_CODIGO_M2CD_1967_1999,
    BOJ_CODIGO_M2CD_1998_2008,
    CLAVE_M2CD_1967_1999,
    CLAVE_M2CD_1998_2008,
    COLUMNAS_D0_AGREGADO,
    COLUMNAS_D0_BALANCES,
    COLUMNAS_D0_DINERO,
    COLUMNAS_N0_SERIES,
    COLUMNAS_N1_COEFICIENTES,
    COLUMNAS_DINERO_HISTORICO,
    COLUMNAS_PARES,
    COLUMNAS_RATIOS,
    COLUMNAS_SERIE,
    DESCARGA_BOJ_BALANCE,
    DESCARGA_BOJ_M2,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    DIR_TRANSCRIPCION_JUNTA,
    FORMATO_D0,
    FORMATO_N0,
    FORMATO_N1_COEFICIENTES,
    PARES_N1,
    FORMATO_RATIOS,
    PARES,
    SERIE_RRP,
    SERIE_TGA,
    SERIE_WALCL,
)
from senales.fuentes_denominador import leer_csv_boj
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


@pytest.mark.parametrize("manifiesto", [ARCHIVO_D0_DESCARGAS, ARCHIVO_DESCARGAS, ARCHIVO_N0_DESCARGAS, ARCHIVO_N1_DESCARGAS])
def test_los_crudos_versionados_coinciden_con_su_manifiesto(manifiesto):
    """Cada crudo que viaja con el repositorio tiene el hash que publicó su manifiesto."""
    if not manifiesto.exists():
        pytest.skip(f"{manifiesto.name} todavía no existe")
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


def _crudo_privado_del_manifiesto(descarga) -> Path:
    """La última descarga de esa fuente según el manifiesto de D0, si su crudo está en data/privado/raw.

    El crudo no viaja con el repositorio (A-D0-27): en una clonación limpia no
    está, y el test se omite diciendo por qué. Si está, tiene que ser el del
    manifiesto, byte a byte.
    """
    filas = pd.read_csv(ARCHIVO_D0_DESCARGAS, dtype=str, keep_default_na=False)
    propias = filas.loc[filas["fuente"] == descarga.clave].sort_values("fecha_descarga", kind="stable")
    assert not propias.empty, f"el manifiesto no tiene ninguna descarga de {descarga.clave}"
    fila = propias.iloc[-1]
    assert fila["crudo_en_repo"] == "no", f"{descarga.clave} del {fila['fecha_descarga']}: el manifiesto lo da como versionado"
    ruta = DIR_CRUDO_PRIVADO / f"{descarga.clave}_{fila['fecha_descarga']}.{descarga.extension}"
    if not ruta.exists():
        pytest.skip(f"{ruta.name} no está en data/privado/raw: el crudo del BoJ no viaja con el repositorio (A-D0-27)")
    assert hashlib.sha256(ruta.read_bytes()).hexdigest() == fila["sha256"], f"{ruta.name} no es el crudo del manifiesto"
    return ruta


def test_las_series_de_japon_salen_de_los_crudos_del_boj_cuando_estan(tmp_path):
    """A-D0-27: las series del BoJ publicadas salen de los crudos de data/privado/raw, si están.

    Se recalculan las filas de esas cuatro series en denominador_dinero.csv y
    denominador_balances.csv con el código de la rama, desde la última descarga
    que registra el manifiesto, y se comparan byte a byte con las publicadas.
    """
    m2 = _crudo_privado_del_manifiesto(DESCARGA_BOJ_M2)
    balance = _crudo_privado_del_manifiesto(DESCARGA_BOJ_BALANCE)
    series = {
        CLAVE_M2CD_1967_1999: denominador.SerieConstruida(leer_csv_boj(m2, BOJ_CODIGO_M2CD_1967_1999)),
        CLAVE_M2CD_1998_2008: denominador.SerieConstruida(leer_csv_boj(m2, BOJ_CODIGO_M2CD_1998_2008)),
        "m2_japon": denominador.SerieConstruida(leer_csv_boj(m2, BOJ_CODIGO_M2)),
        "balance_boj": denominador.SerieConstruida(leer_csv_boj(balance, BOJ_CODIGO_BALANCE)),
    }
    fichas = pd.read_csv(ARCHIVO_D0_FICHAS, dtype=str, keep_default_na=False)
    publicadas = set(fichas.loc[fichas["publicada"] == "sí", "serie"]) & set(series)
    assert publicadas == set(series)
    claves = {clave.encode() for clave in series}
    for archivo, tabla, columnas in (
        (ARCHIVO_D0_DINERO, denominador.tabla_dinero(series, publicadas), COLUMNAS_D0_DINERO),
        (ARCHIVO_D0_BALANCES, denominador.tabla_balances(series, publicadas), COLUMNAS_D0_BALANCES),
    ):
        recalculadas = _escribir(tmp_path, archivo.name, tabla, columnas, FORMATO_D0).splitlines()[1:]
        publicadas_en_csv = [linea for linea in _bytes(archivo).splitlines()[1:] if linea.split(b",")[1] in claves]
        assert recalculadas, archivo.name
        assert recalculadas == publicadas_en_csv, archivo.name


def test_el_dinero_historico_sale_de_las_dos_transcripciones(tmp_path):
    """A-D0-19, A-D0-31: dinero_eeuu_historico.csv, desde los crudos versionados y las fichas publicadas."""
    transcripcion = dinero_historico.leer_transcripcion(DIR_TRANSCRIPCION_JUNTA)
    fallos = dinero_historico.verificar_sumas(transcripcion)
    series = dinero_historico.construir_series(transcripcion, fallos)
    fichas = pd.read_csv(ARCHIVO_D0_FICHAS, dtype=str, keep_default_na=False)
    publicadas = set(fichas.loc[fichas["publicada"] == "sí", "serie"]) & set(series)
    tabla = dinero_historico.publicar(series, publicadas)
    assert _escribir(tmp_path, "h.csv", tabla, COLUMNAS_DINERO_HISTORICO, FORMATO_D0) == _bytes(ARCHIVO_DINERO_HISTORICO)


def test_las_series_de_n0_salen_de_sus_crudos(tmp_path):
    """A-N0-14: numerador_series.csv, desde los crudos versionados, las lecturas de configuracion.py y las fichas publicadas.

    Los contrastes que no viajan con el repositorio (el HTML del Z.1, FRED) solo
    deciden qué se publica, y eso se lee de serie_N0.csv; ningún valor ni marca
    de control de las filas depende de ellos.
    """
    manifiesto = pd.read_csv(ARCHIVO_N0_DESCARGAS, dtype=str, keep_default_na=False)
    versionados = manifiesto.loc[manifiesto["crudo_en_repo"] == "sí"]
    fecha = versionados["fecha_descarga"].max()
    rutas = {}
    for fila in versionados.loc[versionados["fecha_descarga"] == fecha].itertuples():
        candidatos = sorted(DIR_CRUDO.glob(f"{fila.fuente}_{fila.fecha_descarga}.*"))
        assert candidatos, f"falta el crudo de {fila.fuente} del {fila.fecha_descarga}"
        rutas[fila.fuente] = candidatos[0]
    construido = numerador.construir(rutas)
    validaciones = numerador.validar(construido)
    fichas = pd.read_csv(ARCHIVO_N0_FICHAS, dtype=str, keep_default_na=False)
    publicadas = set(fichas.loc[fichas["publicada"] == "sí", "serie"])
    tabla = numerador.tabla_series(construido, validaciones, publicadas)
    assert _escribir(tmp_path, "n.csv", tabla, COLUMNAS_N0_SERIES, FORMATO_N0) == _bytes(ARCHIVO_N0_SERIES)


@pytest.mark.parametrize("manifiesto", [ARCHIVO_D0_DESCARGAS, ARCHIVO_DESCARGAS, ARCHIVO_N0_DESCARGAS, ARCHIVO_N1_DESCARGAS])
def test_los_crudos_privados_que_estan_en_disco_coinciden_con_su_manifiesto(manifiesto):
    """A-N1-11: cada crudo de data/privado/raw que esté en disco tiene el hash que publicó su manifiesto.

    Los crudos que no viajan con el repositorio (los ZIP de la Junta, el BoJ,
    el HTML del Z.1, la copia del BLS) no están en una clonación limpia y
    entonces no hay nada que comprobar. Cuando están, un byte distinto (por
    ejemplo, finales de línea convertidos por Windows, como pasó el 2026-10-14
    con las copias del BoJ) los deja fuera: el pipeline no los usa y este test
    falla con el nombre del archivo.
    """
    if not manifiesto.exists():
        pytest.skip(f"{manifiesto.name} todavía no existe")
    filas = pd.read_csv(manifiesto, dtype=str, keep_default_na=False)
    privados = filas.loc[filas["crudo_en_repo"] == "no"]
    fallos, comprobados = [], 0
    for fila in privados.itertuples():
        for ruta in sorted(DIR_CRUDO_PRIVADO.glob(f"{fila.fuente}_{fila.fecha_descarga}.*")):
            comprobados += 1
            if hashlib.sha256(ruta.read_bytes()).hexdigest() != fila.sha256:
                fallos.append(ruta.name)
    assert not fallos, f"crudos de data/privado/raw que no son los del manifiesto {manifiesto.name}: {fallos}"
    if privados.empty or not comprobados:
        pytest.skip(f"ningún crudo privado de {manifiesto.name} está en data/privado/raw")


def test_los_coeficientes_de_n1_salen_de_sus_insumos_publicados(tmp_path):
    """A-N1-11, A-D0-30: respuesta_oferta.csv se recalcula, byte a byte, desde respuesta_oferta_insumos.csv.

    La regresión es aritmética pura de Python (A-N1-8): dos máquinas dan los
    mismos bytes a partir de los mismos insumos. El resumen lleva además los
    motivos de lo NO MEDIDO, que dependen de la corrida y no se recalculan aquí;
    de él se comprueban la suma, el intervalo, el n y el rótulo de cada par
    estimado.
    """
    if not ARCHIVO_N1_INSUMOS.exists() or not ARCHIVO_N1_COEFICIENTES.exists():
        pytest.skip("la familia N1 todavía no tiene salidas publicadas")
    insumos = pd.read_csv(ARCHIVO_N1_INSUMOS, dtype=str, keep_default_na=False)
    coeficientes = pd.read_csv(ARCHIVO_N1_COEFICIENTES, dtype=str, keep_default_na=False)
    resumen = pd.read_csv(ARCHIVO_N1_RESUMEN, dtype=str, keep_default_na=False)
    fechas = set(resumen["fecha_corrida"])
    assert len(fechas) == 1, fechas
    fecha = pd.Timestamp(fechas.pop()).date()
    resultados = []
    for par in PARES_N1:
        propios = insumos.loc[(insumos["activo"] == par.activo) & (insumos["ventana"] == par.ventana)].copy()
        fila_resumen = resumen.loc[(resumen["activo"] == par.activo) & (resumen["ventana"] == par.ventana)].iloc[0]
        if propios.empty or fila_resumen["estado"] != "estimación":
            continue
        propios["anio"] = propios["anio"].astype(int)
        for columna in ("y", "dlog_precio_real"):
            propios[columna] = [float(v) if v != "" else None for v in propios[columna]]
        estimacion = respuesta_oferta.estimar(propios, par.inicio)
        assert estimacion is not None and estimacion.beta, par.clave
        resultados.append(respuesta_oferta.ResultadoPar(par, "estimación", "", propios, estimacion))
        assert int(fila_resumen["n"]) == estimacion.n and fila_resumen["rotulo"] == respuesta_oferta.rotulo_de(estimacion.suma, estimacion.error_suma), par.clave
        for columna, valor in (("suma", estimacion.suma), ("error_estandar", estimacion.error_suma)):
            assert f"{round(valor, 6):.6f}" == fila_resumen[columna], (par.clave, columna)
    tabla = respuesta_oferta.tabla_coeficientes(resultados, fecha)
    assert _escribir(tmp_path, "c.csv", tabla, COLUMNAS_N1_COEFICIENTES, FORMATO_N1_COEFICIENTES) == _bytes(ARCHIVO_N1_COEFICIENTES)
