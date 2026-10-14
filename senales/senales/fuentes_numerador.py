"""Lectura de las fuentes de la fase N0 (El Numerador).

Lo mismo que no negocia fuentes_denominador.py: el robots.txt antes de cada
pedido (la descarga pasa por fuentes_denominador.descargar), la unidad y la
forma del archivo se contrastan contra lo que el archivo dice de sí mismo, un
dato faltante es un hueco, y de cada descarga queda la URL, la fecha y el
SHA-256 en el manifiesto.

Los lectores de aquí no tocan la red: reciben un archivo y devuelven series.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

from senales.fuentes_denominador import _numero
from senales.fuentes_fred import ErrorDeFuente

# --- Utilidades ---------------------------------------------------------------


def filas_de_la_primera_hoja(ruta: Path) -> list[tuple]:
    """Las filas de la primera hoja de un xlsx, con valores y no fórmulas."""
    try:
        import openpyxl

        libro = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    except Exception as error:  # openpyxl levanta de todo si el archivo no es un xlsx
        raise ErrorDeFuente(f"{ruta.name}: no se pudo abrir como xlsx ({error})") from error
    try:
        return [tuple(fila) for fila in libro.worksheets[0].iter_rows(values_only=True)]
    finally:
        libro.close()


def _texto(celda) -> str:
    return "" if celda is None else str(celda).strip()


def _valor(celda) -> float | None:
    if celda is None:
        return None
    if isinstance(celda, (int, float)):
        return float(celda)
    return _numero(str(celda))


# --- Coin Metrics: oferta, bloques y emisión diarios ----------------------------

METRICAS_OFERTA = ("SplyCur", "BlkCnt", "IssTotNtv")


def interpretar_coin_metrics_oferta(documento: dict) -> pd.DataFrame:
    """Una fila por día: bloques del día, BTC emitidos y oferta al cierre.

    La fila del día D cierra a las 00:00 UTC del día D+1 (misma convención que
    PriceUSD, FUENTES.md 6.2). Un día faltante rompería la cuenta de alturas:
    es un error de fuente, no un hueco que se pueda publicar.
    """
    if documento.get("next_page_url"):
        raise ErrorDeFuente(
            "Coin Metrics: la historia ya no entra en un solo pedido (la respuesta trae next_page_url). "
            "Leer una sola página truncaría la serie en silencio; hay que implementar la paginación."
        )
    filas = documento.get("data")
    if not isinstance(filas, list) or not filas:
        raise ErrorDeFuente("Coin Metrics: la respuesta no trae filas en 'data'")
    faltan = [m for m in METRICAS_OFERTA if m not in filas[0]]
    if faltan:
        raise ErrorDeFuente(f"Coin Metrics: la respuesta no trae las métricas {faltan}")
    registros = []
    for fila in filas:
        if fila.get("asset", "btc") != "btc":
            raise ErrorDeFuente(f"Coin Metrics: la respuesta mezcla el activo {fila.get('asset')!r}")
        oferta = _valor(fila.get("SplyCur"))
        if oferta is None:
            raise ErrorDeFuente(f"Coin Metrics: SplyCur vacío el {str(fila.get('time'))[:10]}")
        bloques = _valor(fila.get("BlkCnt")) or 0.0
        if bloques < 0 or not float(bloques).is_integer():
            raise ErrorDeFuente(f"Coin Metrics: BlkCnt no es un entero el {str(fila.get('time'))[:10]}")
        registros.append(
            (pd.Timestamp(str(fila["time"])[:10]), int(bloques), _valor(fila.get("IssTotNtv")) or 0.0, oferta)
        )
    tabla = pd.DataFrame(registros, columns=["fecha", "bloques", "emision", "oferta"]).set_index("fecha").sort_index()
    if tabla.index.duplicated().any():
        raise ErrorDeFuente("Coin Metrics: hay días repetidos en la respuesta")
    esperados = pd.date_range(tabla.index[0], tabla.index[-1], freq="D")
    if len(esperados) != len(tabla):
        raise ErrorDeFuente(
            f"Coin Metrics: faltan {len(esperados) - len(tabla)} días entre {tabla.index[0].date()} y "
            f"{tabla.index[-1].date()}; sin ellos no se puede seguir la altura de la cadena"
        )
    return tabla


def leer_coin_metrics_oferta(ruta: Path) -> pd.DataFrame:
    try:
        documento = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ErrorDeFuente(f"Coin Metrics: {ruta.name} no es JSON ({error})") from error
    return interpretar_coin_metrics_oferta(documento)


# --- USGS, Data Series 140 ------------------------------------------------------


@dataclass(frozen=True)
class DS140:
    produccion: pd.Series  # año -> toneladas, producción mundial
    modificado: str  # "Last modification: ...", tal cual
    unidad: str  # la línea que declara la unidad, tal cual


def interpretar_ds140(filas: list[tuple], metal: str) -> DS140:
    """La columna "World production" de la hoja de un metal de la Data Series 140."""
    nombre = {"oro": "GOLD", "plata": "SILVER"}[metal]
    titulo = _texto(filas[0][0]) if filas and filas[0] else ""
    if nombre not in titulo.upper():
        raise ErrorDeFuente(f"DS140: la hoja dice {titulo!r} y se esperaba la de {nombre}")
    indice = next((i for i, fila in enumerate(filas) if fila and _texto(fila[0]) == "Year"), None)
    if indice is None:
        raise ErrorDeFuente("DS140: no se encontró la fila de encabezados (empieza con 'Year')")
    encabezado = [_texto(celda) for celda in filas[indice]]
    if "World production" not in encabezado:
        raise ErrorDeFuente(f"DS140: el encabezado {encabezado} no trae 'World production'")
    columna = encabezado.index("World production")
    unidad = next((_texto(f[0]) for f in filas[:indice] if f and "metric tons" in _texto(f[0])), "")
    if not unidad:
        raise ErrorDeFuente("DS140: la hoja no declara la unidad en toneladas métricas ('metric tons')")
    modificado = next((_texto(f[0]) for f in filas[:indice] if f and _texto(f[0]).startswith("Last modification")), "")
    pares = {}
    for fila in filas[indice + 1 :]:
        if not fila or not re.fullmatch(r"\d{4}", _texto(fila[0])):
            continue
        valor = _valor(fila[columna]) if columna < len(fila) else None
        if valor is not None:
            pares[int(_texto(fila[0]))] = valor
    if not pares:
        raise ErrorDeFuente("DS140: la columna 'World production' no tiene valores")
    serie = pd.Series(pares, dtype=float).sort_index()
    serie.index.name = "anio"
    return DS140(serie, modificado, unidad)


def leer_ds140(ruta: Path, metal: str) -> DS140:
    return interpretar_ds140(filas_de_la_primera_hoja(ruta), metal)


# --- Junta de la Reserva Federal: Z.1 --------------------------------------------

PERIODO_Z1 = re.compile(r"^(\d{4}):Q([1-4])$")
PERIODO_HTML_Z1 = re.compile(r"^(\d{4})(?::Q([1-4]))?$")
MNEMONICO_Z1 = re.compile(r"^[A-Z]{2}\d{9}$")


def extraer_tablas_z1(ruta_zip: Path, tablas: tuple[str, ...]) -> dict[str, bytes]:
    """Los bytes exactos de csv/<tabla>.csv dentro del paquete z1_csv_files.zip."""
    try:
        archivo = zipfile.ZipFile(ruta_zip)
    except zipfile.BadZipFile as error:
        raise ErrorDeFuente(f"{ruta_zip.name} no es un ZIP: {error}") from error
    with archivo:
        nombres = set(archivo.namelist())
        resultado = {}
        for tabla in tablas:
            miembro = f"csv/{tabla}.csv"
            if miembro not in nombres:
                raise ErrorDeFuente(
                    f"{ruta_zip.name}: el paquete no trae {miembro}. La Junta cambió los nombres de las "
                    "tablas; releer z1_table_mapping.csv antes de apuntar a otra."
                )
            resultado[tabla] = archivo.read(miembro)
    return resultado


def interpretar_tabla_z1(texto: str, series: tuple[str, ...]) -> pd.DataFrame:
    """Una tabla del paquete CSV: índice 'AAAA:Qn', una columna por mnemónico pedido, 'ND' es NaN."""
    filas = list(csv.reader(io.StringIO(texto)))
    if not filas or not filas[0] or filas[0][0] != "date":
        raise ErrorDeFuente("Z.1: el CSV no empieza con la columna 'date'")
    encabezado = filas[0]
    columnas = {}
    for mnemonico in series:
        nombre = mnemonico if mnemonico.endswith(".Q") else f"{mnemonico}.Q"
        if nombre not in encabezado:
            raise ErrorDeFuente(
                f"Z.1: la tabla no trae la serie {nombre}. La Junta la movió o la renombró; releer el "
                "diccionario del paquete antes de apuntar a otra."
            )
        columnas[nombre.removesuffix(".Q")] = encabezado.index(nombre)
    datos = {}
    for fila in filas[1:]:
        if not fila or not PERIODO_Z1.match(fila[0]):
            continue
        datos[fila[0]] = {m: (_numero(fila[i]) if i < len(fila) else None) for m, i in columnas.items()}
    if not datos:
        raise ErrorDeFuente("Z.1: la tabla no tiene filas trimestrales")
    tabla = pd.DataFrame.from_dict(datos, orient="index", dtype=float).sort_index()
    tabla.index.name = "periodo"
    return tabla


def leer_tabla_z1(ruta: Path, series: tuple[str, ...]) -> pd.DataFrame:
    return interpretar_tabla_z1(ruta.read_text(encoding="utf-8"), series)


class _CeldasHTML(HTMLParser):
    """Las filas de todas las tablas de una página, como listas de celdas de texto."""

    def __init__(self) -> None:
        super().__init__()
        self.filas: list[list[str]] = []
        self._fila: list[str] | None = None
        self._celda: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._fila = []
        elif tag in ("td", "th") and self._fila is not None:
            self._celda = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._celda is not None and self._fila is not None:
            self._fila.append(" ".join("".join(self._celda).split()))
            self._celda = None
        elif tag == "tr" and self._fila is not None:
            self.filas.append(self._fila)
            self._fila = None

    def handle_data(self, data):
        if self._celda is not None:
            self._celda.append(data)


ENLACE_SERIE_Z1 = re.compile(r"SeriesAnalyzer\.aspx\?s=([A-Z]{2}\d{9})")


def _valor_html(texto: str) -> float | None:
    return _numero(texto) if texto.lower() not in ("n.a.", "na", "nd") else None


def interpretar_html_z1(html: str) -> dict[str, dict[str, float | None]]:
    """Una tabla del Z.1 en HTML: mnemónico -> {período: valor en miles de millones}.

    Las columnas se ubican por su encabezado (años y trimestres), no por su
    posición: la Junta cambia cuántas trae en cada publicación. Las tablas de
    la familia D (deuda por sector) vienen traspuestas, con los períodos como
    filas, y sus mnemónicos solo en los enlaces de los encabezados; para esas
    se lee el orden de los enlaces.
    """
    analizador = _CeldasHTML()
    analizador.feed(html)
    valores = _html_z1_por_filas(analizador.filas) or _html_z1_traspuesta(analizador.filas, html)
    if not valores:
        raise ErrorDeFuente("Z.1: la página no tiene una tabla con mnemónicos y columnas de período")
    return valores


def _html_z1_traspuesta(filas: list[list[str]], html: str) -> dict[str, dict[str, float | None]]:
    mnemonicos: list[str] = []
    for mnemonico in ENLACE_SERIE_Z1.findall(html):
        if mnemonico not in mnemonicos:
            mnemonicos.append(mnemonico)
    valores: dict[str, dict[str, float | None]] = {m: {} for m in mnemonicos}
    for fila in filas:
        if not fila or not PERIODO_HTML_Z1.match(fila[0]):
            continue
        numeros = [c for c in fila[1:] if c]
        if mnemonicos and len(numeros) != len(mnemonicos):
            raise ErrorDeFuente(
                f"Z.1: la fila {fila[0]} trae {len(numeros)} valores y la página enlaza {len(mnemonicos)} series; "
                "no se puede saber qué columna es cada serie"
            )
        for mnemonico, numero in zip(mnemonicos, numeros):
            valores[mnemonico][fila[0]] = _valor_html(numero)
    return {m: v for m, v in valores.items() if v}


def _html_z1_por_filas(filas: list[list[str]]) -> dict[str, dict[str, float | None]]:
    periodos: list[str] | None = None
    valores: dict[str, dict[str, float | None]] = {}
    for fila in filas:
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
        valores[fila[posicion]] = {periodo: _valor_html(numero) for periodo, numero in zip(periodos, numeros)}
    return valores


def leer_html_z1(ruta: Path) -> dict[str, dict[str, float | None]]:
    return interpretar_html_z1(ruta.read_text(encoding="utf-8", errors="replace"))


# --- Census Bureau: inventario de viviendas (HVS, Tablas 7 y 7a) ------------------

ETIQUETA_ANIO_HVS = re.compile(r"^(\d{4})(r\d*)?(\*+)?(\d)?$")


@dataclass(frozen=True)
class ColumnaHVS:
    """Una columna de la tabla: un año, en su base original o revisada."""

    anio: int
    revisada: bool
    nota: str  # marca de nota al pie de la fuente ('*', '1', ...), tal cual
    total: float | None
    vacantes: float | None
    ocupadas: float | None


@dataclass(frozen=True)
class TablaHVS:
    titulo: str
    fuente: str
    columnas: tuple[ColumnaHVS, ...]
    notas: tuple[str, ...] = field(default_factory=tuple)

    @property
    def total(self) -> dict[int, float]:
        """El valor de cada año en su base original (o la única que trae la tabla)."""
        originales = {c.anio: c.total for c in self.columnas if not c.revisada and c.total is not None}
        for columna in self.columnas:
            if columna.revisada and columna.total is not None and columna.anio not in originales:
                originales[columna.anio] = columna.total
        return dict(sorted(originales.items()))

    @property
    def revisados(self) -> dict[int, float]:
        """Los años que la tabla trae dos veces: el valor en la base revisada."""
        originales = {c.anio for c in self.columnas if not c.revisada and c.total is not None}
        return {c.anio: c.total for c in self.columnas if c.revisada and c.total is not None and c.anio in originales}

    @property
    def notas_por_anio(self) -> dict[int, str]:
        return {c.anio: c.nota for c in self.columnas if c.nota and not c.revisada}


def etiqueta_anio_hvs(celda) -> tuple[int, bool, str] | None:
    """'1979r1' -> (1979, True, ''); '19861' -> (1986, False, '1'); '2025*' -> (2025, False, '*')."""
    if celda is None:
        return None
    if isinstance(celda, (int, float)):
        return (int(celda), False, "") if float(celda).is_integer() and 1800 < celda < 2200 else None
    coincidencia = ETIQUETA_ANIO_HVS.match(str(celda).strip())
    if coincidencia is None:
        return None
    anio = int(coincidencia.group(1))
    if not 1800 < anio < 2200:
        return None
    return anio, coincidencia.group(2) is not None, (coincidencia.group(3) or "") + (coincidencia.group(4) or "")


def _rotulo(celda) -> str:
    return re.sub(r"[^a-z]", "", _texto(celda).lower())


def interpretar_hvs(filas: list[tuple]) -> TablaHVS:
    """Las Tablas 7 y 7a del HVS: 'All housing units', 'Vacant' y 'Total occupied' por columna."""
    titulo = next((_texto(f[0]) for f in filas if f and _texto(f[0]).startswith("Table 7")), "")
    if not titulo:
        raise ErrorDeFuente("HVS: la hoja no trae un título 'Table 7...'")
    fuente = next((_texto(f[0]) for f in filas if f and _texto(f[0]).startswith("Source:")), "")
    notas = tuple(_texto(f[0]) for f in filas if f and re.match(r"^(\*|r\d|\d |\d\s)", _texto(f[0])))
    encabezado: list[tuple[int, tuple[int, bool, str]]] | None = None
    por_columna: dict[tuple[int, bool], dict] = {}
    for fila in filas:
        # Una fila de años: desde la columna B, toda celda con valor es un año
        # (1965, '1979r1', '2025*'). Una fila de datos puede traer cifras entre
        # 1800 y 2200 (vacantes estacionales, por ejemplo), pero no todas.
        # Y una fila de datos lleva su rótulo en la columna A, que empieza con
        # puntos ('..Vacant') o dice 'All housing units'; la de años no.
        rotulo_a = _texto(fila[0]) if fila else ""
        es_dato = rotulo_a != "" and (rotulo_a[0] in ".…" or _rotulo(rotulo_a).startswith("allhousingunits"))
        con_valor = [(j, c) for j, c in enumerate(fila) if j > 0 and c is not None and _texto(c) != ""]
        etiquetas = [(j, etiqueta_anio_hvs(c)) for j, c in con_valor]
        if not es_dato and len(etiquetas) >= 2 and all(e is not None for _, e in etiquetas):
            encabezado = etiquetas
            continue
        if encabezado is None or not fila:
            continue
        rotulo = _rotulo(fila[0])
        if rotulo.startswith("allhousingunits"):
            campo = "total"
        elif rotulo.startswith("vacant"):
            campo = "vacantes"
        elif rotulo.startswith("totaloccupied"):
            campo = "ocupadas"
        else:
            continue
        for j, (anio, revisada, nota) in encabezado:
            valor = _valor(fila[j]) if j < len(fila) else None
            if valor is None:
                continue
            celda = por_columna.setdefault((anio, revisada), {"nota": nota})
            if campo in celda:
                raise ErrorDeFuente(f"HVS: la tabla trae dos veces la columna {anio}{'r' if revisada else ''}")
            celda[campo] = valor
    if not por_columna:
        raise ErrorDeFuente("HVS: no se encontró la fila 'All housing units' con sus años")
    columnas = tuple(
        ColumnaHVS(anio, revisada, datos.get("nota", ""), datos.get("total"), datos.get("vacantes"), datos.get("ocupadas"))
        for (anio, revisada), datos in sorted(por_columna.items())
    )
    return TablaHVS(titulo, fuente, columnas, notas)


def leer_hvs(ruta: Path) -> TablaHVS:
    return interpretar_hvs(filas_de_la_primera_hoja(ruta))


# --- Census Bureau: Population Estimates, viviendas al 1 de julio -----------------


@dataclass(frozen=True)
class Popest:
    titulo: str
    serie: pd.Series  # año -> viviendas al 1 de julio
    base: float  # la base del 1 de abril de 2020
    publicado: str  # "Release Date: ...", tal cual


def interpretar_popest(filas: list[tuple]) -> Popest:
    titulo = next((_texto(f[0]) for f in filas if f and "Housing Units" in _texto(f[0])), "")
    if "July 1" not in titulo:
        raise ErrorDeFuente(f"Population Estimates: el título {titulo!r} no dice que las cifras son al 1 de julio")
    encabezado = next(
        (f for f in filas if f and sum(1 for c in f if isinstance(c, (int, float)) and 1900 < c < 2200) >= 3), None
    )
    if encabezado is None:
        raise ErrorDeFuente("Population Estimates: no se encontró la fila con los años")
    anios = [(j, int(c)) for j, c in enumerate(encabezado) if isinstance(c, (int, float)) and 1900 < c < 2200]
    fila = next((f for f in filas if f and _texto(f[0]) == "United States"), None)
    if fila is None:
        raise ErrorDeFuente("Population Estimates: no se encontró la fila 'United States'")
    valores = {anio: _valor(fila[j]) for j, anio in anios if j < len(fila)}
    if any(v is None for v in valores.values()):
        raise ErrorDeFuente("Population Estimates: la fila 'United States' tiene años sin valor")
    base = _valor(fila[anios[0][0] - 1]) if anios[0][0] >= 1 else None
    if base is None:
        raise ErrorDeFuente("Population Estimates: no se encontró la base del 1 de abril de 2020")
    publicado = next((_texto(f[0]) for f in filas if f and _texto(f[0]).startswith("Release Date")), "")
    return Popest(titulo, pd.Series(valores, dtype=float).sort_index(), base, publicado)


def leer_popest(ruta: Path) -> Popest:
    return interpretar_popest(filas_de_la_primera_hoja(ruta))


# --- FRED: serie trimestral (contraste) ----------------------------------------------


def interpretar_fred_trimestral(texto: str, id_serie: str) -> pd.Series:
    filas = list(csv.DictReader(io.StringIO(texto)))
    if not filas or "observation_date" not in filas[0] or id_serie not in filas[0]:
        raise ErrorDeFuente(f"FRED: el CSV no trae las columnas observation_date y {id_serie}")
    pares = {
        pd.Timestamp(fila["observation_date"]): valor
        for fila in filas
        if (valor := _numero(fila[id_serie])) is not None
    }
    if not pares:
        raise ErrorDeFuente(f"FRED: {id_serie} no tiene valores")
    return pd.Series(pares, dtype=float).sort_index()


def leer_fred_trimestral(ruta: Path, id_serie: str) -> pd.Series:
    return interpretar_fred_trimestral(ruta.read_text(encoding="utf-8"), id_serie)
