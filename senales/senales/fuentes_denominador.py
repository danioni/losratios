"""Descarga y lectura de las fuentes de la fase D0 (El Denominador).

Cuatro reglas que este módulo no negocia:

1. Antes de pedirle un archivo a un sitio se lee su robots.txt. Si veda al
   cliente con que se hace el pedido, no se descarga nada de ahí (regla de
   CLAUDE.md del 2026-10-05; FUENTES.md, D0.15). Un crudo que ya está en disco
   se reutiliza sin pedir nada.
2. La unidad de una serie no se asume: se declara en configuracion.py y se
   contrasta contra lo que el archivo dice de sí mismo. Si no coinciden, la
   corrida se detiene (A-S2-9).
3. Un dato faltante es un hueco. Ningún lector rellena ni interpola.
4. De cada descarga, de fuente o de contraste, queda la URL, la fecha y el
   SHA-256 en el manifiesto.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from html import unescape
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlsplit

import pandas as pd
import requests

from senales import fuentes_precios
from senales.configuracion import Descarga
from senales.fuentes_fred import ErrorDeFuente
from senales.fuentes_precios import RegistroDescarga

TIEMPO_LIMITE = 90

# El nombre con que requests se presenta si nadie le dice otra cosa. Es el que
# se contrasta contra el robots.txt de cada sitio: el pipeline no se disfraza.
AGENTE = f"python-requests/{requests.__version__}"


class AccesoVedado(ErrorDeFuente):
    """El robots.txt del sitio no admite al cliente que haría el pedido."""


class CopiaFaltante(ErrorDeFuente):
    """La fuente entra por copia bajada a mano y no hay ninguna en el directorio de crudos."""


# --- robots.txt ----------------------------------------------------------------

_robots: dict[str, robotparser.RobotFileParser] = {}


def interpretar_robots(estado: int, tipo: str, texto: str) -> robotparser.RobotFileParser:
    """Convierte la respuesta de /robots.txt en reglas.

    Sigue la lectura habitual del estándar: sin archivo (404) no hay reglas; un
    401 o un 403 vedan todo; una página HTML servida en lugar del archivo no es
    un robots.txt y tampoco pone reglas.
    """
    analizador = robotparser.RobotFileParser()
    if estado in (401, 403):
        analizador.disallow_all = True
        analizador.modified()
        return analizador
    es_texto = estado == 200 and "html" not in tipo.lower() and not texto.lstrip().startswith("<")
    analizador.parse(texto.splitlines() if es_texto else [])
    return analizador


def reglas_de(host: str, sesion=None) -> robotparser.RobotFileParser:
    """Lee el robots.txt de un host, una vez por corrida."""
    if host not in _robots:
        url = f"https://{host}/robots.txt"
        cliente = sesion or requests
        try:
            respuesta = cliente.get(url, timeout=TIEMPO_LIMITE)
        except requests.RequestException as error:
            raise ErrorDeFuente(f"no se pudo leer {url}: {error}") from error
        _robots[host] = interpretar_robots(
            respuesta.status_code, respuesta.headers.get("Content-Type", ""), respuesta.text
        )
    return _robots[host]


def exigir_acceso(url: str, sesion=None, agente: str = AGENTE) -> None:
    """Falla con AccesoVedado si el robots.txt del sitio no admite el pedido."""
    host = urlsplit(url).netloc
    if not reglas_de(host, sesion).can_fetch(agente, url):
        raise AccesoVedado(
            f"el robots.txt de {host} no admite a {agente.split('/')[0]} en {url}. No se "
            "descarga nada de ahí. Si la fuente permite bajar el archivo a mano, dejarlo en "
            "el directorio de crudos con el nombre de la descarga y la fecha (FUENTES.md, D0.15)."
        )


def descargar(
    descarga: Descarga,
    fecha_descarga: date,
    dir_abierto: Path,
    dir_privado: Path,
    manifiesto: pd.DataFrame,
    sesion=None,
) -> RegistroDescarga:
    """Como fuentes_precios.descargar, con el robots.txt leído antes del pedido.

    Si el crudo de esa fecha ya está en disco no hay pedido, y por lo tanto no
    hay nada que consultar: así entra una copia bajada a mano.
    """
    if descarga.manual:
        fecha_descarga = fecha_de_copia_manual(descarga, fecha_descarga, dir_abierto, dir_privado)
    destino = fuentes_precios.ruta_cruda(descarga, fecha_descarga, dir_abierto, dir_privado)
    if not destino.exists():
        exigir_acceso(descarga.url, sesion)
    return fuentes_precios.descargar(
        descarga, fecha_descarga, dir_abierto, dir_privado, manifiesto, sesion
    )


def fecha_de_copia_manual(
    descarga: Descarga, fecha_descarga: date, dir_abierto: Path, dir_privado: Path
) -> date:
    """La fecha de la copia a mano más reciente que no sea posterior a la corrida (A-D0-29).

    El archivo se llama <clave>_<AAAA-MM-DD>.<extensión>, como cualquier crudo.
    Si no hay ninguna, la serie queda NO MEDIDO en esa corrida.
    """
    directorio = dir_abierto if descarga.crudo_versionado else dir_privado
    patron = re.compile(rf"^{re.escape(descarga.clave)}_(\d{{4}}-\d{{2}}-\d{{2}})\.{re.escape(descarga.extension)}$")
    fechas = []
    for ruta in directorio.glob(f"{descarga.clave}_*.{descarga.extension}"):
        coincidencia = patron.match(ruta.name)
        if coincidencia:
            try:
                fecha = date.fromisoformat(coincidencia.group(1))
            except ValueError:
                continue
            if fecha <= fecha_descarga:
                fechas.append(fecha)
    if not fechas:
        raise CopiaFaltante(
            f"{descarga.clave}: no hay una copia bajada a mano en {directorio} con fecha hasta "
            f"{fecha_descarga}. Abrir {descarga.url} en un navegador, guardar la respuesta como "
            f"{descarga.clave}_<AAAA-MM-DD>.{descarga.extension} ahí, y volver a correr."
        )
    return max(fechas)


# --- Utilidades ----------------------------------------------------------------


def _numero(texto: str | None) -> float | None:
    if texto is None:
        return None
    limpio = texto.strip().replace(",", "")
    if limpio in ("", ".", "NaN", "ND", "NC", "null", "-"):
        return None
    try:
        return float(limpio)
    except ValueError:
        return None


def _serie(pares: list[tuple[pd.Timestamp, float]], nombre: str) -> pd.Series:
    if not pares:
        return pd.Series(dtype=float, name=nombre, index=pd.DatetimeIndex([], name="fecha"))
    fechas, valores = zip(*pares)
    serie = pd.Series(valores, index=pd.DatetimeIndex(fechas, name="fecha"), name=nombre)
    serie = serie[~serie.index.duplicated(keep="last")].sort_index()
    return serie.astype(float)


def _mes(texto: str) -> pd.Timestamp:
    """'2026-08', '2026-08-31' o '202608' al primer día del mes."""
    limpio = texto.strip()
    if re.fullmatch(r"\d{6}", limpio):
        limpio = f"{limpio[:4]}-{limpio[4:]}"
    return pd.Timestamp(limpio[:7] + "-01")


# --- Junta de la Reserva Federal: ZIP de XML ------------------------------------


@dataclass(frozen=True)
class SerieJunta:
    """Una serie de un XML de la Junta, con lo que el archivo dice de ella."""

    valores: pd.Series  # indexada por la fecha que trae el archivo
    multiplicador: str  # atributo UNIT_MULT, tal cual
    moneda: str  # atributo CURRENCY
    descripcion: str


def leer_xml_junta(ruta: Path, nombres: set[str]) -> dict[str, SerieJunta]:
    """Extrae del ZIP de una publicación de la Junta las series pedidas.

    El XML del H.4.1 pesa más de 100 MB: se recorre sin cargarlo entero. Una
    observación marcada "ND" (sin dato) no entra a la serie.
    """
    try:
        archivo_zip = zipfile.ZipFile(ruta)
    except zipfile.BadZipFile as error:
        raise ErrorDeFuente(f"{ruta.name} no es un ZIP: {error}") from error
    with archivo_zip:
        datos = [n for n in archivo_zip.namelist() if n.lower().endswith("_data.xml")]
        if len(datos) != 1:
            raise ErrorDeFuente(f"{ruta.name}: se esperaba un *_data.xml y hay {len(datos)}")
        encontradas: dict[str, SerieJunta] = {}
        with archivo_zip.open(datos[0]) as flujo:
            for _, elemento in ET.iterparse(flujo, events=("end",)):
                if elemento.tag.rsplit("}", 1)[-1] != "Series":
                    continue
                nombre = elemento.attrib.get("SERIES_NAME", "")
                if nombre in nombres:
                    pares, descripcion = [], ""
                    for hijo in elemento.iter():
                        etiqueta = hijo.tag.rsplit("}", 1)[-1]
                        if etiqueta == "Obs" and hijo.attrib.get("OBS_STATUS") != "ND":
                            valor = _numero(hijo.attrib.get("OBS_VALUE"))
                            if valor is not None:
                                pares.append((pd.Timestamp(hijo.attrib["TIME_PERIOD"]), valor))
                        elif etiqueta == "AnnotationText" and hijo.text and not descripcion:
                            descripcion = hijo.text.strip()
                    encontradas[nombre] = SerieJunta(
                        valores=_serie(pares, nombre),
                        multiplicador=elemento.attrib.get("UNIT_MULT", ""),
                        moneda=elemento.attrib.get("CURRENCY", ""),
                        descripcion=descripcion,
                    )
                elemento.clear()
    faltantes = sorted(nombres - set(encontradas))
    if faltantes:
        raise ErrorDeFuente(
            f"{ruta.name}: el archivo no trae las series {faltantes}. La Junta cambió los "
            "nombres o el contenido de la publicación; releer la fuente."
        )
    return encontradas


def exigir_multiplicador(serie: SerieJunta, nombre: str, esperado: float) -> None:
    """A-S2-9: el multiplicador de unidad se comprueba en cada corrida."""
    declarado = _numero(serie.multiplicador)
    if declarado is None or abs(declarado - esperado) > 1e-6 * esperado:
        raise ErrorDeFuente(
            f"{nombre}: el archivo declara UNIT_MULT={serie.multiplicador!r} y la configuración "
            f"espera {esperado:g}. Corregir configuracion.py y registrarlo en SUPUESTOS.md; no "
            "ajustar el cálculo para compensar."
        )


# --- BCE: CSV de la API del ECB Data Portal -------------------------------------


def _filas_csv(ruta: Path, codificacion: str = "utf-8") -> list[dict[str, str]]:
    texto = ruta.read_text(encoding=codificacion)
    return list(csv.DictReader(io.StringIO(texto)))


def periodo_bce(texto: str) -> pd.Timestamp:
    """'2026-08' al primer día del mes; '2026-W39' al viernes de esa semana ISO.

    La serie semanal empieza en '1998-W53', la semana del viernes 1 de enero de
    1999 (FUENTES.md, D0.7.2).
    """
    if "-W" in texto:
        anio, semana = texto.split("-W")
        try:
            return pd.Timestamp(date.fromisocalendar(int(anio), int(semana), 5))
        except ValueError:
            return pd.Timestamp(date(int(anio) + 1, 1, 1))
    return _mes(texto)


def leer_csv_bce(ruta: Path, clave: str, unidad: str = "EUR", multiplicador: str = "6") -> pd.Series:
    """Lee una serie del formato csvdata de la API del BCE y comprueba clave y unidad."""
    filas = _filas_csv(ruta)
    if not filas or "KEY" not in filas[0] or "OBS_VALUE" not in filas[0]:
        raise ErrorDeFuente(f"{ruta.name}: no es un csvdata de la API del BCE")
    claves = {fila["KEY"] for fila in filas}
    if claves != {clave}:
        raise ErrorDeFuente(f"{ruta.name}: trae las claves {sorted(claves)} y se esperaba {clave}")
    unidades = {(fila.get("UNIT", ""), fila.get("UNIT_MULT", "")) for fila in filas}
    if unidades != {(unidad, multiplicador)}:
        raise ErrorDeFuente(
            f"{ruta.name}: declara unidad y multiplicador {sorted(unidades)} y la configuración "
            f"espera {(unidad, multiplicador)}"
        )
    pares = [
        (periodo_bce(fila["TIME_PERIOD"]), valor)
        for fila in filas
        if (valor := _numero(fila["OBS_VALUE"])) is not None
    ]
    return _serie(pares, clave)


# --- Banco de Japón: CSV de la API de series ------------------------------------


def leer_csv_boj(ruta: Path, codigo: str, unidad: str = "100 million yen") -> pd.Series:
    """Lee una serie mensual de getDataCode y comprueba el estado y la unidad."""
    pares, unidades, estado = [], set(), None
    with ruta.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.reader(archivo):
            if len(fila) >= 2 and fila[0] == "STATUS":
                estado = fila[1]
            if len(fila) >= 8 and fila[0] == codigo and re.fullmatch(r"\d{6}", fila[6]):
                unidades.add(fila[2])
                valor = _numero(fila[7])
                if valor is not None:
                    pares.append((_mes(fila[6]), valor))
    if estado != "200":
        raise ErrorDeFuente(f"{ruta.name}: la API del BoJ respondió STATUS={estado!r}")
    if not pares:
        raise ErrorDeFuente(f"{ruta.name}: no trae la serie {codigo}")
    if unidades != {unidad}:
        raise ErrorDeFuente(
            f"{ruta.name}: {codigo} declara la unidad {sorted(unidades)} y se esperaba {unidad!r}"
        )
    return _serie(pares, codigo)


# --- OCDE: CSV con etiquetas de la API SDMX -------------------------------------


@dataclass(frozen=True)
class SerieOCDE:
    valores: pd.Series
    rotulo: str  # cómo llama la OCDE a la medida: va tal cual a la ficha
    ajuste: str


def leer_csv_ocde(ruta: Path, area: str, medida: str, multiplicador: str = "6") -> SerieOCDE:
    """Lee una serie de DF_MONAGG y devuelve también el rótulo que le pone la OCDE."""
    filas = _filas_csv(ruta)
    if not filas or "MEASURE" not in filas[0]:
        raise ErrorDeFuente(f"{ruta.name}: no es un CSV con etiquetas de la OCDE")
    propias = [f for f in filas if f["REF_AREA"] == area and f["MEASURE"] == medida]
    if not propias:
        raise ErrorDeFuente(f"{ruta.name}: no trae {area}.{medida}")
    for campo, esperado in (("UNIT_MEASURE", "XDC"), ("UNIT_MULT", multiplicador), ("FREQ", "M")):
        vistos = {fila[campo] for fila in propias}
        if vistos != {esperado}:
            raise ErrorDeFuente(
                f"{ruta.name}: {campo} vale {sorted(vistos)} y la configuración espera {esperado!r}"
            )
    rotulos = {fila["Measure"] for fila in propias}
    ajustes = {fila["Adjustment"] for fila in propias}
    if len(rotulos) != 1 or len(ajustes) != 1:
        raise ErrorDeFuente(f"{ruta.name}: la serie mezcla rótulos {rotulos} o ajustes {ajustes}")
    pares = [
        (_mes(fila["TIME_PERIOD"]), valor)
        for fila in propias
        if (valor := _numero(fila["OBS_VALUE"])) is not None
    ]
    return SerieOCDE(_serie(pares, f"{area}.{medida}"), rotulos.pop(), ajustes.pop())


# --- BIS: CSV de la API ---------------------------------------------------------


def leer_csv_bis_activos(ruta: Path, area: str) -> pd.Series:
    """Activos totales del banco central (WS_CBTA), en miles de millones de moneda local."""
    filas = [
        fila
        for fila in _filas_csv(ruta)
        if fila.get("REF_AREA", "").startswith(area)
        and fila.get("UNIT_MEASURE", "").startswith("XDC")
        and fila.get("TRANSFORMATION", "").startswith("N")
    ]
    if not filas:
        raise ErrorDeFuente(f"{ruta.name}: no trae activos de {area} en moneda local")
    multiplicadores = {fila.get("UNIT_MULT", "")[:1] for fila in filas}
    if multiplicadores != {"9"}:
        raise ErrorDeFuente(
            f"{ruta.name}: UNIT_MULT vale {sorted(multiplicadores)} y se esperaba 9 (miles de millones)"
        )
    pares = [
        (_mes(fila["TIME_PERIOD"]), valor)
        for fila in filas
        if (valor := _numero(fila["OBS_VALUE"])) is not None
    ]
    return _serie(pares, f"bis_cbta_{area.lower()}")


def leer_csv_bis_cambio(ruta: Path, moneda: str, coleccion: str) -> pd.Series:
    """Tipo de cambio contra el USD (WS_XRU): unidades de moneda local por dólar.

    `coleccion` es "A" (promedio del mes) o "E" (fin de mes).
    """
    filas = [
        fila
        for fila in _filas_csv(ruta)
        if fila.get("CURRENCY", "").startswith(moneda)
        and fila.get("COLLECTION", "").startswith(coleccion)
    ]
    if not filas:
        raise ErrorDeFuente(f"{ruta.name}: no trae {moneda} con la colección {coleccion}")
    pares = [
        (_mes(fila["TIME_PERIOD"]), valor)
        for fila in filas
        if (valor := _numero(fila["OBS_VALUE"])) is not None
    ]
    return _serie(pares, f"bis_xru_{moneda.lower()}_{coleccion.lower()}")


# --- Fuentes de contraste -------------------------------------------------------

MESES_INGLES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7,
    "jul": 7, "aug": 8, "sept": 9, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
MESES_CASTELLANO = {
    "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12,
}


def _texto_plano(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def interpretar_tabla_h6(html: str) -> pd.DataFrame:
    """La Tabla 1 de la publicación H.6 en HTML: M2 ajustado y sin ajustar.

    Las columnas se ubican por su encabezado, no por su posición: se busca la
    que dice "M2" debajo de "Seasonally adjusted" y la que lo dice debajo de
    "Not seasonally adjusted".
    """
    tabla = re.search(r'<table[^>]*title="Table 1"[^>]*>(.*?)</table>', html, re.S)
    if tabla is None:
        raise ErrorDeFuente("H.6: la página no tiene una tabla titulada 'Table 1'")
    cuerpo = tabla.group(1)

    def atributos(etiqueta: str) -> dict[str, str]:
        return dict(re.findall(r'([\w-]+)="([^"]*)"', etiqueta))

    encabezados: dict[str, tuple[str, str]] = {}
    for celda in re.finditer(r"<th([^>]*)>(.*?)</th>", cuerpo, re.S):
        propios = atributos(celda.group(1))
        if propios.get("class") == "colhead" and "id" in propios:
            encabezados[propios["id"]] = (_texto_plano(celda.group(2)), propios.get("headers", ""))

    columnas: dict[str, str] = {}
    for identificador, (texto, padres) in encabezados.items():
        if not re.match(r"M2\b", texto):
            continue
        padre = encabezados.get(padres.split()[-1] if padres else "", ("", ""))[0].lower()
        if padre.startswith("seasonally adjusted"):
            columnas["ajustada"] = identificador
        elif padre.startswith("not seasonally adjusted"):
            columnas["sin_ajustar"] = identificador
    if set(columnas) != {"ajustada", "sin_ajustar"}:
        raise ErrorDeFuente(f"H.6: no se ubicaron las dos columnas de M2 (se encontró {columnas})")

    filas: dict[pd.Timestamp, dict[str, float]] = {}
    for fila in re.finditer(r"<tr[^>]*>(.*?)</tr>", cuerpo, re.S):
        rotulo = next(
            (
                celda
                for celda in re.finditer(r"<th([^>]*)>(.*?)</th>", fila.group(1), re.S)
                if atributos(celda.group(1)).get("class") != "colhead"
            ),
            None,
        )
        if rotulo is None:
            continue
        partes = _texto_plano(rotulo.group(2)).replace(".", "").split()
        if len(partes) != 2 or partes[0].lower() not in MESES_INGLES or not partes[1].isdigit():
            continue
        mes = pd.Timestamp(year=int(partes[1]), month=MESES_INGLES[partes[0].lower()], day=1)
        for celda in re.finditer(r"<td([^>]*)>(.*?)</td>", fila.group(1), re.S):
            de_la_celda = atributos(celda.group(1)).get("headers", "").split()
            for nombre, identificador in columnas.items():
                if identificador in de_la_celda:
                    valor = _numero(_texto_plano(celda.group(2)))
                    if valor is not None:
                        filas.setdefault(mes, {})[nombre] = valor
    if not filas:
        raise ErrorDeFuente("H.6: la Tabla 1 no tiene filas de datos reconocibles")
    resultado = pd.DataFrame.from_dict(filas, orient="index").sort_index()
    resultado.index.name = "mes"
    return resultado


def interpretar_bde(texto: str, codigo: str) -> pd.Series:
    """Una columna de un CSV del Boletín Estadístico del Banco de España."""
    filas = list(csv.reader(io.StringIO(texto)))
    encabezado = next((fila for fila in filas if fila and fila[0].startswith("C")), None)
    if encabezado is None or codigo not in encabezado:
        raise ErrorDeFuente(f"Banco de España: el archivo no trae la serie {codigo}")
    columna = encabezado.index(codigo)
    pares = []
    for fila in filas:
        partes = fila[0].split() if fila else []
        if len(partes) == 2 and partes[0] in MESES_CASTELLANO and partes[1].isdigit():
            valor = _numero(fila[columna]) if columna < len(fila) else None
            if valor is not None:
                pares.append(
                    (pd.Timestamp(year=int(partes[1]), month=MESES_CASTELLANO[partes[0]], day=1), valor)
                )
    return _serie(pares, codigo)


def interpretar_estat(documento: dict, indicador: str) -> pd.Series:
    """Un indicador mensual del tablero estadístico del gobierno de Japón."""
    try:
        objetos = documento["GET_STATS"]["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]
    except (KeyError, TypeError) as error:
        raise ErrorDeFuente("e-Stat: la respuesta no tiene la forma esperada") from error
    pares = []
    for objeto in objetos:
        valor = objeto.get("VALUE", {})
        if valor.get("@indicator") != indicador:
            continue
        numero = _numero(valor.get("$"))
        if numero is not None:
            pares.append((_mes(valor["@time"][:6]), numero))
    if not pares:
        raise ErrorDeFuente(f"e-Stat: la respuesta no trae el indicador {indicador}")
    return _serie(pares, indicador)


def leer_json(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))
