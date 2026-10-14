"""Lectura de las fuentes nuevas de la fase N1 (respuesta observada de la oferta al precio).

Lo mismo que no negocian fuentes_denominador.py y fuentes_numerador.py: el
robots.txt antes de cada pedido (la descarga pasa por
fuentes_denominador.descargar), la unidad y la forma del archivo se contrastan
contra lo que el archivo dice de sí mismo, un dato faltante es un hueco, y de
cada crudo queda la URL, la fecha y el SHA-256 en el manifiesto.

Los lectores de aquí no tocan la red: reciben un archivo y devuelven series.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from senales.configuracion import FHFA_AREA_EEUU, ONZAS_TROY_POR_TONELADA, Z1_B103_MIEMBROS
from senales.fuentes_denominador import _numero
from senales.fuentes_fred import ErrorDeFuente
from senales.fuentes_numerador import (
    MNEMONICO_Z1,
    PERIODO_HTML_Z1,
    _CeldasHTML,
    _texto,
    _valor,
    interpretar_fred_trimestral,
)
from senales.nucleo import normalizar_texto

MESES_INGLES_CORTOS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")


def hojas_de(ruta: Path) -> dict[str, list[tuple]]:
    """Todas las hojas de un xlsx, con valores y no fórmulas, por nombre."""
    try:
        import openpyxl

        libro = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    except Exception as error:  # openpyxl levanta de todo si el archivo no es un xlsx
        raise ErrorDeFuente(f"{ruta.name}: no se pudo abrir como xlsx ({error})") from error
    try:
        return {hoja.title: [tuple(fila) for fila in hoja.iter_rows(values_only=True)] for hoja in libro.worksheets}
    finally:
        libro.close()


def _decimales(texto: str) -> int:
    """Cuántos decimales publica una cifra escrita, para fijar medio paso por construcción."""
    limpio = texto.strip().replace(",", "")
    return len(limpio.split(".", 1)[1]) if "." in limpio else 0


# --- FHFA: índice all-transactions, EE.UU. ------------------------------------------


def interpretar_fhfa(texto: str, area: str = FHFA_AREA_EEUU) -> pd.Series:
    """El índice trimestral de un área del CSV de la FHFA: índice 'AAAA:Qn' -> valor.

    El archivo no trae encabezado: área, año, trimestre, índice (FUENTES.md,
    N0.16.1). Un trimestre repetido o fuera de 1 a 4 es un error de fuente.
    """
    filas = [f for f in csv.reader(io.StringIO(texto)) if f]
    if not filas or len(filas[0]) != 4:
        raise ErrorDeFuente("FHFA: el CSV no tiene cuatro columnas (área, año, trimestre, índice)")
    if not re.fullmatch(r"[A-Za-z][A-Za-z_]{1,9}", filas[0][0].strip()) or not re.fullmatch(r"\d{4}", filas[0][1].strip()):
        raise ErrorDeFuente(f"FHFA: la primera fila no es un dato (área, año, trimestre, índice): {filas[0]}")
    pares: dict[str, float] = {}
    areas = set()
    for fila in filas:
        if len(fila) != 4:
            raise ErrorDeFuente(f"FHFA: una fila no tiene cuatro columnas: {fila}")
        codigo, anio, trimestre, indice = (c.strip() for c in fila)
        areas.add(codigo)
        if codigo != area:
            continue
        if not re.fullmatch(r"\d{4}", anio) or trimestre not in ("1", "2", "3", "4"):
            raise ErrorDeFuente(f"FHFA: período ilegible en la fila {fila}")
        valor = _numero(indice)
        if valor is None:
            continue
        periodo = f"{anio}:Q{trimestre}"
        if periodo in pares:
            raise ErrorDeFuente(f"FHFA: el trimestre {periodo} está repetido para {area}")
        pares[periodo] = valor
    if not pares:
        raise ErrorDeFuente(f"FHFA: el CSV no trae el área {area!r} (áreas leídas: {sorted(areas)[:12]})")
    serie = pd.Series(pares, dtype=float).sort_index()
    serie.index.name = "periodo"
    return serie


def leer_fhfa(ruta: Path, area: str = FHFA_AREA_EEUU) -> pd.Series:
    return interpretar_fhfa(ruta.read_text(encoding="utf-8", errors="replace"), area)


def decimales_fhfa(texto: str, area: str = FHFA_AREA_EEUU) -> int:
    """Con cuántos decimales publica la FHFA el índice del área (para medio paso por construcción)."""
    maximo = 0
    for fila in csv.reader(io.StringIO(texto)):
        if len(fila) == 4 and fila[0].strip() == area:
            maximo = max(maximo, _decimales(fila[3]))
    return maximo


# --- FRED: series mensuales y trimestrales -----------------------------------------


def interpretar_fred(texto: str, id_serie: str) -> pd.Series:
    """Una serie de FRED (fredgraph.csv): fecha -> valor. Un punto es un hueco."""
    return interpretar_fred_trimestral(texto, id_serie)


def leer_fred(ruta: Path, id_serie: str) -> pd.Series:
    return interpretar_fred(ruta.read_text(encoding="utf-8"), id_serie)


def decimales_fred(texto: str, id_serie: str) -> int:
    maximo = 0
    for fila in csv.DictReader(io.StringIO(texto)):
        if fila.get(id_serie) and _numero(fila[id_serie]) is not None:
            maximo = max(maximo, _decimales(fila[id_serie]))
    return maximo


# --- Census Bureau: viviendas terminadas ---------------------------------------------


@dataclass(frozen=True)
class Terminadas:
    anual: pd.Series  # año -> miles, hoja anual
    mensual: pd.Series  # Timestamp (primer día del mes) -> miles, hoja mensual sin ajustar
    decimales_anual: int
    decimales_mensual: int
    hoja_anual: str
    hoja_mensual: str
    fuente: str  # la línea "Source: ..." si la hay


def _es_anio(celda) -> bool:
    return re.fullmatch(r"\d{4}", _texto(celda)) is not None


def _columna_total(encabezado: tuple) -> int | None:
    for i, celda in enumerate(encabezado):
        if normalizar_texto(_texto(celda)) in ("total", "total units", "united states", "u.s. total", "us total"):
            return i
    return None


def _decimales_de_celda(celda) -> int:
    if isinstance(celda, float) and not celda.is_integer():
        return len(repr(celda).split(".")[1]) if "." in repr(celda) and "e" not in repr(celda) else 1
    return _decimales(_texto(celda)) if not isinstance(celda, (int, float)) else 0


def _leer_hoja_anual(filas: list[tuple]) -> tuple[pd.Series, int] | None:
    """Filas (año, ..., Total, ...): la primera columna 'Total' después del año."""
    encabezado_i = next((i for i, f in enumerate(filas) if f and _columna_total(f) is not None), None)
    if encabezado_i is None:
        return None
    columna = _columna_total(filas[encabezado_i])
    pares, decimales = {}, 0
    for fila in filas[encabezado_i + 1 :]:
        if not fila or not _es_anio(fila[0]) or columna >= len(fila):
            continue
        valor = _valor(fila[columna])
        if valor is None:
            continue
        pares[int(_texto(fila[0]))] = valor
        decimales = max(decimales, _decimales_de_celda(fila[columna]))
    if len(pares) < 3:
        return None
    serie = pd.Series(pares, dtype=float).sort_index()
    serie.index.name = "anio"
    return serie, decimales


def _mes_de(celda) -> int | None:
    texto = normalizar_texto(_texto(celda))[:3]
    return MESES_INGLES_CORTOS.index(texto) + 1 if texto in MESES_INGLES_CORTOS else None


def _leer_hoja_mensual(filas: list[tuple]) -> tuple[pd.Series, int] | None:
    """Dos formas: una grilla (año en la primera columna, doce meses como columnas) o filas (año, mes, ..., Total)."""
    pares: dict[pd.Timestamp, float] = {}
    decimales = 0
    # Grilla: la fila de encabezados trae los doce meses.
    for i, fila in enumerate(filas):
        if not fila:
            continue
        meses = {j: m for j, celda in enumerate(fila) if (m := _mes_de(celda)) is not None}
        if len(meses) == 12:
            for datos in filas[i + 1 :]:
                if not datos or not _es_anio(datos[0]):
                    continue
                anio = int(_texto(datos[0]))
                for j, mes in meses.items():
                    valor = _valor(datos[j]) if j < len(datos) else None
                    if valor is not None:
                        pares[pd.Timestamp(year=anio, month=mes, day=1)] = valor
                        decimales = max(decimales, _decimales_de_celda(datos[j]))
            break
    if not pares:
        # Filas: (año, mes, ..., Total) con la columna Total en el encabezado, o un período AAAA-MM.
        encabezado_i = next((i for i, f in enumerate(filas) if f and _columna_total(f) is not None), None)
        if encabezado_i is not None:
            columna = _columna_total(filas[encabezado_i])
            anio_vigente = None
            for fila in filas[encabezado_i + 1 :]:
                if not fila or columna >= len(fila):
                    continue
                primera = _texto(fila[0])
                if isinstance(fila[0], pd.Timestamp) or re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", primera):
                    fecha = pd.Timestamp(fila[0]) if isinstance(fila[0], pd.Timestamp) else pd.Timestamp(primera[:7] + "-01")
                    mes, anio_vigente = fecha.month, fecha.year
                else:
                    if _es_anio(fila[0]):
                        anio_vigente = int(primera)
                    mes = _mes_de(fila[1]) if len(fila) > 1 else None
                    if mes is None:
                        continue
                if anio_vigente is None:
                    continue
                valor = _valor(fila[columna])
                if valor is not None:
                    pares[pd.Timestamp(year=anio_vigente, month=mes, day=1)] = valor
                    decimales = max(decimales, _decimales_de_celda(fila[columna]))
    if len(pares) < 12:
        return None
    serie = pd.Series(pares, dtype=float).sort_index()
    serie.index.name = "mes"
    return serie, decimales


def interpretar_terminadas(hojas: dict[str, list[tuple]]) -> Terminadas:
    """La hoja anual y la mensual sin ajustar del archivo de terminadas del Censo.

    Las hojas se ubican por su nombre (anual; mensual sin ajuste estacional) y,
    si el nombre no alcanza, por su forma. Una hoja ajustada a tasa anual
    nunca se usa: la suma de sus meses no es el año.
    """
    if not hojas:
        raise ErrorDeFuente("Censo (terminadas): el archivo no tiene hojas")
    nombres = {nombre: normalizar_texto(nombre) for nombre in hojas}
    anual_nombre = next((n for n, t in nombres.items() if "annual" in t or "anual" in t), None)
    mensual_nombre = next(
        (n for n, t in nombres.items() if ("not" in t and "season" in t) or "nsa" in t or "unadjusted" in t or "not sa" in t),
        None,
    )
    candidatas_anual = [anual_nombre] if anual_nombre else list(hojas)
    candidatas_mensual = [mensual_nombre] if mensual_nombre else [n for n in hojas if "saar" not in nombres[n] and "seasonally adjusted" not in nombres[n].replace("not seasonally adjusted", "")]
    anual = next(((n, r) for n in candidatas_anual if (r := _leer_hoja_anual(hojas[n])) is not None), None)
    if anual is None:
        raise ErrorDeFuente("Censo (terminadas): no se encontró una hoja anual con el año en la primera columna y una columna 'Total'")
    mensual = next(((n, r) for n in candidatas_mensual if (r := _leer_hoja_mensual(hojas[n])) is not None), None)
    if mensual is None:
        raise ErrorDeFuente("Censo (terminadas): no se encontró una hoja mensual sin ajuste estacional con doce meses por año")
    fuente = ""
    for filas in hojas.values():
        for fila in filas:
            if fila and _texto(fila[0]).lower().startswith("source"):
                fuente = _texto(fila[0])
                break
        if fuente:
            break
    return Terminadas(anual[1][0], mensual[1][0], anual[1][1], mensual[1][1], anual[0], mensual[0], fuente)


def leer_terminadas(ruta: Path) -> Terminadas:
    return interpretar_terminadas(hojas_de(ruta))


# --- BLS: la copia a mano del CPI-U (gate del deflactor) ----------------------------


@dataclass(frozen=True)
class CopiaBLS:
    mensual: pd.Series  # Timestamp (primer día del mes) -> índice
    anual: pd.Series | None  # año -> promedio anual publicado por el BLS, si la copia lo trae
    decimales: int
    serie_id: str  # el identificador que el archivo declara, si lo declara


def _interpretar_bls_filas(filas: list[tuple]) -> CopiaBLS:
    serie_id = ""
    for fila in filas[:40]:
        for celda in fila or ():
            texto = _texto(celda)
            if (m := re.search(r"\b(C[UW][SU]R?[0-9A-Z]{7,12})\b", texto)):
                serie_id = m.group(1)
                break
        if serie_id:
            break
    mensual: dict[pd.Timestamp, float] = {}
    anual: dict[int, float] = {}
    decimales = 0
    # Grilla del "SeriesReport": Year, Jan..Dec, Annual, HALF1, HALF2.
    for i, fila in enumerate(filas):
        if not fila:
            continue
        meses = {j: m for j, celda in enumerate(fila) if (m := _mes_de(celda)) is not None}
        col_anio = next((j for j, celda in enumerate(fila) if normalizar_texto(_texto(celda)) == "year"), None)
        if len(meses) == 12 and col_anio is not None:
            col_anual = next((j for j, celda in enumerate(fila) if normalizar_texto(_texto(celda)) == "annual"), None)
            for datos in filas[i + 1 :]:
                if not datos or col_anio >= len(datos) or not _es_anio(datos[col_anio]):
                    continue
                anio = int(_texto(datos[col_anio]))
                for j, mes in meses.items():
                    valor = _valor(datos[j]) if j < len(datos) else None
                    if valor is not None:
                        mensual[pd.Timestamp(year=anio, month=mes, day=1)] = valor
                        decimales = max(decimales, _decimales_de_celda(datos[j]))
                if col_anual is not None and col_anual < len(datos) and (v := _valor(datos[col_anual])) is not None:
                    anual[anio] = v
            break
    if not mensual:
        # Formato largo: Series ID, Year, Period (M01..M13), Value.
        encabezado_i = next((i for i, f in enumerate(filas) if f and {"year", "period", "value"} <= {normalizar_texto(_texto(c)) for c in f}), None)
        if encabezado_i is not None:
            columnas = {normalizar_texto(_texto(c)): j for j, c in enumerate(filas[encabezado_i])}
            for datos in filas[encabezado_i + 1 :]:
                if not datos or max(columnas["year"], columnas["period"], columnas["value"]) >= len(datos):
                    continue
                anio, periodo, valor = _texto(datos[columnas["year"]]), _texto(datos[columnas["period"]]).upper(), _valor(datos[columnas["value"]])
                if not _es_anio(anio) or valor is None:
                    continue
                if re.fullmatch(r"M(0[1-9]|1[0-2])", periodo):
                    mensual[pd.Timestamp(year=int(anio), month=int(periodo[1:]), day=1)] = valor
                    decimales = max(decimales, _decimales_de_celda(datos[columnas["value"]]))
                elif periodo == "M13":
                    anual[int(anio)] = valor
    if len(mensual) < 12:
        raise ErrorDeFuente(
            "BLS (copia a mano): no se reconoció la tabla del CPI-U. Se esperan la grilla Year, Jan..Dec[, Annual] "
            "o las columnas Year, Period, Value (M01..M13)"
        )
    serie = pd.Series(mensual, dtype=float).sort_index()
    serie.index.name = "mes"
    anual_serie = None
    if anual:
        anual_serie = pd.Series(anual, dtype=float).sort_index()
        anual_serie.index.name = "anio"
    return CopiaBLS(serie, anual_serie, decimales, serie_id)


def interpretar_bls_texto(texto: str) -> CopiaBLS:
    """Un CSV o TXT del BLS: coma o tabulador."""
    dialecto = "\t" if texto.count("\t") > texto.count(",") else ","
    filas = [tuple(c.strip() for c in fila) for fila in csv.reader(io.StringIO(texto), delimiter=dialecto)]
    return _interpretar_bls_filas(filas)


def leer_bls(ruta: Path) -> CopiaBLS:
    if ruta.suffix.lower() == ".xlsx":
        hojas = hojas_de(ruta)
        errores = []
        for nombre, filas in hojas.items():
            try:
                return _interpretar_bls_filas(filas)
            except ErrorDeFuente as error:
                errores.append(f"{nombre}: {error}")
        raise ErrorDeFuente("; ".join(errores))
    return interpretar_bls_texto(ruta.read_text(encoding="utf-8-sig", errors="replace"))


# --- USGS, Data Series 140: el valor unitario --------------------------------------


@dataclass(frozen=True)
class ValorUnitarioDS140:
    usd_por_oz: pd.Series  # año -> USD por onza troy (cálculo propio desde USD por tonelada)
    usd_por_t: pd.Series  # año -> USD por tonelada, como lo publica la hoja
    encabezado: str  # el nombre de la columna, tal cual
    modificado: str


def interpretar_valor_unitario_ds140(filas: list[tuple], metal: str) -> ValorUnitarioDS140:
    """La columna "Unit value ($/t)" (dólares corrientes) de la hoja de un metal de la DS140.

    La columna en dólares de 1998 no se usa (A-N1-3): el deflactor del USGS no
    está en la hoja.
    """
    nombre = {"oro": "GOLD", "plata": "SILVER"}[metal]
    titulo = _texto(filas[0][0]) if filas and filas[0] else ""
    if nombre not in titulo.upper():
        raise ErrorDeFuente(f"DS140: la hoja dice {titulo!r} y se esperaba la de {nombre}")
    indice = next((i for i, fila in enumerate(filas) if fila and _texto(fila[0]) == "Year"), None)
    if indice is None:
        raise ErrorDeFuente("DS140: no se encontró la fila de encabezados (empieza con 'Year')")
    encabezado = [_texto(celda) for celda in filas[indice]]
    candidatas = [i for i, c in enumerate(encabezado) if c.lower().startswith("unit value") and "98" not in c]
    if len(candidatas) != 1:
        raise ErrorDeFuente(f"DS140: el encabezado {encabezado} no trae una sola columna 'Unit value ($/t)' en dólares corrientes")
    columna = candidatas[0]
    if "$/t" not in encabezado[columna]:
        raise ErrorDeFuente(f"DS140: la columna {encabezado[columna]!r} no declara USD por tonelada ($/t)")
    modificado = next((_texto(f[0]) for f in filas[:indice] if f and _texto(f[0]).startswith("Last modification")), "")
    pares = {}
    for fila in filas[indice + 1 :]:
        if not fila or not _es_anio(fila[0]):
            continue
        valor = _valor(fila[columna]) if columna < len(fila) else None
        if valor is not None and valor > 0:
            pares[int(_texto(fila[0]))] = valor
    if not pares:
        raise ErrorDeFuente("DS140: la columna del valor unitario no tiene valores")
    por_t = pd.Series(pares, dtype=float).sort_index()
    por_t.index.name = "anio"
    por_oz = por_t / ONZAS_TROY_POR_TONELADA
    return ValorUnitarioDS140(por_oz, por_t, encabezado[columna], modificado)


def leer_valor_unitario_ds140(ruta: Path, metal: str) -> ValorUnitarioDS140:
    from senales.fuentes_numerador import filas_de_la_primera_hoja

    return interpretar_valor_unitario_ds140(filas_de_la_primera_hoja(ruta), metal)


# --- Z.1: la tabla B.103 ----------------------------------------------------------------


def extraer_b103_del_zip(ruta_zip: Path, serie_testigo: str = "FL103164106.Q", candidatos: tuple[str, ...] = Z1_B103_MIEMBROS) -> tuple[str, bytes]:
    """(miembro, bytes exactos) del CSV de la B.103 dentro del paquete: por nombre o, si no, por la serie testigo."""
    try:
        archivo = zipfile.ZipFile(ruta_zip)
    except zipfile.BadZipFile as error:
        raise ErrorDeFuente(f"{ruta_zip.name} no es un ZIP: {error}") from error
    with archivo:
        nombres = archivo.namelist()
        for candidato in candidatos:
            if candidato in nombres:
                contenido = archivo.read(candidato)
                if serie_testigo.encode() in contenido.split(b"\n", 1)[0]:
                    return candidato, contenido
        for nombre in sorted(nombres):
            if not nombre.lower().endswith(".csv"):
                continue
            with archivo.open(nombre) as miembro:
                primera = miembro.readline()
            if serie_testigo.encode() in primera:
                return nombre, archivo.read(nombre)
    raise ErrorDeFuente(
        f"{ruta_zip.name}: ningún CSV del paquete trae {serie_testigo} en su encabezado. La Junta cambió los "
        "nombres o las series de la B.103; releer z1_table_mapping.csv y el diccionario antes de apuntar a otra."
    )


def interpretar_html_z1_con_decimales(html: str) -> dict[str, dict[str, tuple[float | None, int]]]:
    """Como fuentes_numerador.interpretar_html_z1, pero conserva cuántos decimales publica cada celda.

    Sirve para fijar la tolerancia del gate de transporte por construcción:
    medio paso de la última cifra que publica el HTML, serie por serie (A-N1-5).
    Solo la forma por filas (mnemónico en la fila): la B.103 se publica así.
    """
    analizador = _CeldasHTML()
    analizador.feed(html)
    periodos: list[str] | None = None
    valores: dict[str, dict[str, tuple[float | None, int]]] = {}
    for fila in analizador.filas:
        de_periodo = [c for c in fila if PERIODO_HTML_Z1.match(c)]
        if len(de_periodo) >= 4 and not any(MNEMONICO_Z1.match(c) for c in fila):
            periodos = de_periodo
            continue
        if periodos is None:
            continue
        posicion = next((i for i, c in enumerate(fila) if MNEMONICO_Z1.match(c)), None)
        if posicion is None:
            continue
        numeros = [c for c in fila[posicion + 1 :] if c]
        if len(numeros) < len(periodos):
            continue
        numeros = numeros[-len(periodos) :]
        valores[fila[posicion]] = {
            periodo: ((_numero(texto) if texto.lower() not in ("n.a.", "na", "nd") else None), _decimales(texto))
            for periodo, texto in zip(periodos, numeros)
        }
    if not valores:
        raise ErrorDeFuente("Z.1: la página no tiene una tabla con mnemónicos y columnas de período")
    return valores


def leer_html_z1_con_decimales(ruta: Path) -> dict[str, dict[str, tuple[float | None, int]]]:
    return interpretar_html_z1_con_decimales(ruta.read_text(encoding="utf-8", errors="replace"))
