"""Configuración central del marco de señales.

Todo parámetro que afecte un número publicado vive en este archivo, no en el
código de cálculo. Cambiar un valor de acá obliga a registrar el cambio en
SUPUESTOS.md y en data/series/CHANGELOG.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

DIR_CRUDO = RAIZ / "data" / "raw"
DIR_SERIES = RAIZ / "data" / "series"
DIR_REPORTES = RAIZ / "reportes"

URL_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
URL_METADATOS = "https://fred.stlouisfed.org/data/{id}.txt"

# Unidad declarada por FRED -> factor que la lleva a miles de millones de USD.
# La unidad de cada serie no se asume: se declara abajo y el script la contrasta
# contra los metadatos de FRED en cada corrida (ver fuentes_fred.verificar_unidades).
FACTOR_A_MILES_DE_MILLONES = {
    "millones": 0.001,
    "miles_de_millones": 1.0,
}


@dataclass(frozen=True)
class SerieFRED:
    """Una serie de FRED y todo lo que hay que saber para normalizarla."""

    id: str
    descripcion: str
    unidad: str  # clave de FACTOR_A_MILES_DE_MILLONES
    unidad_fred: str  # texto tal como FRED lo declara, para contrastar
    frecuencia: str  # "semanal_miercoles" | "diaria"
    banda_plausible: tuple[float, float]  # en miles de millones; control de orden de magnitud

    @property
    def factor(self) -> float:
        return FACTOR_A_MILES_DE_MILLONES[self.unidad]


@dataclass(frozen=True)
class CasoValidacion:
    """Ancla externa contra la que se contrasta el cálculo antes de publicar.

    Las tres cifras tienen que salir de la MISMA columna del release. El H.4.1
    publica cada partida dos veces: como nivel del miércoles y como promedio de
    la semana. Un ancla que mezcla las dos columnas no describe ningún instante,
    y la resta que sale de ahí no cuadra con nada. No es hipotético: el ancla
    original de esta serie las mezclaba, y el gate la rechazó en la primera
    corrida real. Ver la entrada del 2026-09-22 en data/series/CHANGELOG.md.

    De ahí salen dos campos que no son decorativos. `columna` deja escrito de
    qué columna vienen los números, para que el próximo que actualice el ancla
    sepa qué tiene que buscar. Y `tolerancia_componente` obliga a que cada
    término cierre por separado, no solo el total: un total que cuadra porque
    dos componentes se compensan no es un ancla reproducida.
    """

    fecha: date
    walcl: float
    tga: float
    rrp: float
    s2_1_esperado: float
    tolerancia: float
    tolerancia_componente: float
    columna: str
    fuente: str
    fuente_url: str
    fecha_publicacion: date


SERIE_WALCL = SerieFRED(
    id="WALCL",
    descripcion="Activos totales de la Fed (menos eliminaciones de consolidación), nivel de miércoles",
    unidad="millones",
    unidad_fred="Millions of U.S. Dollars",
    frecuencia="semanal_miercoles",
    banda_plausible=(500.0, 20_000.0),
)

# A-S2-4: serie de TGA predeterminada. Es el nivel de miércoles, la misma
# convención que WALCL y que el ancla del H.4.1, para que S2.1 no mezcle un
# nivel puntual con un promedio.
#
# La unidad de esta serie está acoplada al identificador: WDTGAL se publica en
# millones de USD. Cambiar el identificador sin cambiar la unidad rompe la serie
# por un factor de 1000, y hay un test que falla si esta declaración deja de
# decir "millones" (tests/test_unidades.py).
SERIE_TGA_NIVEL_MIERCOLES = SerieFRED(
    id="WDTGAL",
    descripcion=(
        "Cuenta general del Tesoro (TGA), nivel de miércoles. En FRED: "
        "Liabilities and Capital: Deposits with F.R. Banks, Other Than Reserve "
        "Balances: U.S. Treasury, General Account: Wednesday Level"
    ),
    unidad="millones",
    unidad_fred="Millions of U.S. Dollars",
    frecuencia="semanal_miercoles",
    banda_plausible=(0.0, 2_000.0),
)

# Alternativa documentada en SUPUESTOS.md (A-S2-4): el TGA como promedio de la
# semana. No es la predeterminada porque promedia días que el H.4.1 no promedia.
# Para usarla, apuntar SERIE_TGA a esta declaración y registrar el cambio.
SERIE_TGA_PROMEDIO_SEMANAL = SerieFRED(
    id="WTREGEN",
    descripcion="Cuenta general del Tesoro (TGA), promedio semanal a miércoles",
    unidad="miles_de_millones",
    unidad_fred="Billions of U.S. Dollars",
    frecuencia="semanal_miercoles",
    banda_plausible=(0.0, 2_000.0),
)

SERIE_RRP = SerieFRED(
    id="RRPONTSYD",
    descripcion="Reverse repo overnight con contrapartes domésticas (ON RRP)",
    unidad="miles_de_millones",
    unidad_fred="Billions of US Dollars",
    frecuencia="diaria",
    banda_plausible=(0.0, 3_000.0),
)

# Serie de TGA efectivamente en uso. Cambiarla es un cambio de supuesto (A-S2-4)
# y obliga a revisar la unidad declarada arriba junto con el identificador.
SERIE_TGA = SERIE_TGA_NIVEL_MIERCOLES

# Historia mínima que se publica.
FECHA_INICIO = date(2020, 1, 1)

# A-S2-2: ventana de la variación de S2.2, en semanas. Parametrizable.
VENTANA_VARIACION_SEMANAS = 13

# A-S2-3: umbral para declarar expansión o contracción. NO DEFINIDO a propósito.
# Mientras sea None, la salida reporta "NO MEDIDO". No inventar un valor acá.
UMBRAL_EXPANSION_CONTRACCION: float | None = None

# A-S2-5: cuántos días como máximo se arrastra el último ON RRP disponible cuando
# el miércoles no tiene dato. Más allá de eso es un hueco, no un valor.
MAX_DIAS_ARRASTRE_RRP = 7

# A-S2-6: diferencia mínima, en miles de millones, para considerar que FRED
# revisó un dato histórico y no que es ruido de redondeo.
EPSILON_REVISION = 0.0005

# Ancla del H.4.1. Los tres números son niveles de miércoles del 16 de septiembre
# de 2026, leídos de la misma columna del release y convertidos de millones a
# miles de millones de USD.
#
# El ancla anterior mezclaba columnas: los activos totales venían del nivel de
# miércoles, pero el TGA (877.028) y el ON RRP (3.999) venían del promedio
# semanal. La primera corrida real, el 2026-09-22, la rechazó con una diferencia
# de -116.535, casi toda concentrada en el TGA. La corrección viene de leer el
# H.4.1 publicado, no de ajustar el cálculo para que cuadre. Ver A-S2-13.
VALIDACION_H41 = CasoValidacion(
    fecha=date(2026, 9, 16),
    walcl=6746.548,
    tga=991.708,
    rrp=5.375,
    s2_1_esperado=5749.465,
    tolerancia=5.0,
    # A-S2-14: cada componente tiene que cerrar dentro de +/-1 contra el release.
    tolerancia_componente=1.0,
    columna="nivel de miércoles (Wednesday level)",
    fuente=(
        "H.4.1 de la semana terminada el 16 de septiembre de 2026, columna de "
        "nivel de miércoles. Cifras del release, en millones de USD: activos "
        "totales 6746548; TGA 991708; reverse repurchase agreements, línea "
        "\"Others\" (ON RRP doméstico, A-S2-1) 5375."
    ),
    # Enlace móvil: /current/ apunta siempre al release más reciente, así que deja
    # de mostrar esta semana en cuanto se publica la siguiente. El equivalente
    # archivado y estable todavía no se verificó desde este repositorio (A-S2-13).
    fuente_url="https://www.federalreserve.gov/releases/h41/current/",
    fecha_publicacion=date(2026, 9, 17),
)

ARCHIVO_SERIE = DIR_SERIES / "liquidez_neta.csv"
ARCHIVO_CHANGELOG = DIR_SERIES / "CHANGELOG.md"
ARCHIVO_GRAFICO = DIR_REPORTES / "liquidez_neta.png"

COLUMNAS_SERIE = [
    "fecha",
    "walcl",
    "tga",
    "rrp",
    "rrp_fecha_origen",
    "s2_1_liquidez_neta",
    "s2_2_var_13s_pct",
]

# Columnas cuyo cambio entre corridas cuenta como revisión de dato histórico.
COLUMNAS_REVISABLES = ["walcl", "tga", "rrp", "s2_1_liquidez_neta"]


# ---------------------------------------------------------------------------
# Fase R: precios mensuales y ratios.
#
# Todo lo de acá sale de FUENTES.md (qué se leyó de cada fuente) y de los
# supuestos A-R0-1 a A-R0-16 de SUPUESTOS.md (qué se decidió con eso).
# ---------------------------------------------------------------------------

# A-R0-15: los crudos cuya licencia no permite redistribuirlos, y las series que
# no se publican, van a un directorio ignorado por git.
DIR_PRIVADO = RAIZ / "data" / "privado"
DIR_CRUDO_PRIVADO = DIR_PRIVADO / "raw"
DIR_SERIES_PRIVADO = DIR_PRIVADO / "series"

# A-R0-14: texto con el que se publica un par que se calcula y no se muestra.
NO_MEDIDO_PERMISO = "NO MEDIDO: pendiente de permiso del dueño del índice"
# A-R0-14: y con el que se publica una serie cuyo gate todavía no cerró.
NO_MEDIDO_SIN_VALIDACION = "NO MEDIDO: sin validación externa"

ESTADO_DATO = "dato"
ESTADO_ESTIMACION = "estimación"

# Clases de licencia de FUENTES.md, sección 0.1. Solo la (a) es abierta.
CLASE_ABIERTA = "a"
CLASE_NO_COMERCIAL = "b"
CLASE_NO_COMERCIAL_CON_RESERVA = "b con reserva"
CLASE_SIN_DECLARAR = "sin licencia declarada"


@dataclass(frozen=True)
class Descarga:
    """Un archivo que se baja de una fuente, y dónde puede vivir su crudo."""

    clave: str  # nombre del crudo, sin fecha ni extensión
    descripcion: str
    clase_licencia: str
    licencia: str
    url: str  # el archivo, o la página que lo enlaza si hay patron_enlace
    extension: str
    # CC BY y CC BY-NC exigen atribución y decir si los datos se modificaron.
    atribucion: str
    # Algunas fuentes cambian la URL del archivo en cada publicación. Para esas
    # se baja la página y se busca el enlace: no se asume que la URL es estable.
    patron_enlace: str | None = None

    @property
    def crudo_versionado(self) -> bool:
        """A-R0-15: el crudo entra al repositorio si su licencia permite redistribuirlo.

        Eso es CC BY (clase a) y CC BY-NC (clase b), siempre con atribución. Una
        fuente sin licencia declarada, o con dos textos que no coinciden, no.
        """
        return self.clase_licencia in (CLASE_ABIERTA, CLASE_NO_COMERCIAL)


@dataclass(frozen=True)
class SeriePrecio:
    """Una serie mensual de precios y lo que decide si se publica."""

    clave: str
    nombre: str
    descarga: Descarga
    unidad: str
    estado: str
    banda_plausible: tuple[float, float]  # control de orden de magnitud
    supuestos: tuple[str, ...]
    desde: str | None = None  # primer mes que se usa, "AAAA-MM"
    # A-R0-9: medio paso del redondeo con que la fuente publica la serie, en su
    # unidad. Es el error máximo de cada valor. None si la fuente no redondea.
    medio_paso_redondeo: float | None = None

    @property
    def publicable(self) -> bool:
        """A-R0-14: se publica lo que la licencia permite publicar sin interpretarla."""
        return self.descarga.clase_licencia in (CLASE_ABIERTA, CLASE_NO_COMERCIAL)


@dataclass(frozen=True)
class Par:
    clave: str
    nombre: str
    numerador: str
    denominador: str


@dataclass(frozen=True)
class Contraste:
    """Una segunda fuente contra la que se compara una serie, mes a mes.

    A-R0-12: la fuente de contraste no alimenta nada. Se lee, se compara y se
    registra fecha, valor y diferencia. El archivo no se guarda.
    """

    serie: str
    fuente: str
    url: str
    tolerancia_pct: float
    desde: str | None = None  # primer mes que entra al contraste


@dataclass(frozen=True)
class AnclaAnual:
    """El precio promedio de un año según una segunda fuente, transcrito a mano.

    Es el ancla del gate de oro y plata, como el H.4.1 lo es de S2: una cifra
    leída de un documento publicado, con su cita, contra la que tiene que cerrar
    el promedio de los doce meses de la serie. Ver A-R0-16.
    """

    serie: str
    anio: int
    valor: float
    fuente: str
    fuente_url: str
    fecha_lectura: date


@dataclass(frozen=True)
class BandaTrimestral:
    """Mínimo y máximo de un trimestre, de una fuente pública, con su cita.

    Es más débil que un ancla: un promedio mensual fuera de los extremos de su
    trimestre es un error seguro, y uno adentro no prueba nada. Ver A-R0-16.
    """

    serie: str
    meses: tuple[str, ...]
    minimo: float
    maximo: float
    fuente: str
    fuente_url: str
    fecha_lectura: date


DESCARGA_PINK_SHEET = Descarga(
    clave="pink_sheet",
    descripcion="Banco Mundial, Commodity Price Data (The Pink Sheet), precios mensuales",
    clase_licencia=CLASE_ABIERTA,
    licencia="CC BY 4.0",
    url="https://www.worldbank.org/en/research/commodity-markets",
    extension="xlsx",
    atribucion=(
        "The World Bank: World Bank Commodity Price Data (The Pink Sheet). "
        "Licencia CC BY 4.0. Edición del 3 de enero de 2025 para 1960-01 a 2024-12 y "
        "edición vigente desde 2025-01. Los valores mensuales se publican sin cambios."
    ),
    patron_enlace=r'href="([^"]*CMO-Historical-Data-Monthly\.xlsx[^"]*)"',
)

# A-R0-19: la edición de enero de 2025 del mismo archivo, la última que el Banco
# Mundial publicó sin redondear. La URL es la que el archivo tenía entonces; la
# página actual no la enlaza. El pipeline no depende de ella: usa la copia
# versionada en data/raw/.
DESCARGA_PINK_SHEET_CONGELADA = Descarga(
    clave="pink_sheet_edicion_2025-01-03",
    descripcion=(
        "Banco Mundial, Commodity Price Data (The Pink Sheet), precios mensuales, "
        "edición del 3 de enero de 2025, sin redondear"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia="CC BY 4.0",
    url=(
        "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/"
        "related/CMO-Historical-Data-Monthly.xlsx"
    ),
    extension="xlsx",
    atribucion=(
        "The World Bank: World Bank Commodity Price Data (The Pink Sheet), edición del "
        "3 de enero de 2025. Licencia CC BY 4.0. Los valores mensuales se publican sin "
        "cambios."
    ),
)

DESCARGA_SHILLER = Descarga(
    clave="shiller_ie_data",
    descripcion="Robert Shiller, ie_data.xls",
    clase_licencia=CLASE_SIN_DECLARAR,
    licencia="sin licencia declarada",
    url="https://shillerdata.com/",
    extension="xls",
    atribucion=(
        "Robert J. Shiller, datos de Irrational Exuberance (ie_data.xls). Sin licencia "
        "declarada. Índice subyacente: S&P Dow Jones Indices LLC."
    ),
    patron_enlace=r'href="([^"]*/ie_data\.xls[^"]*)"',
)

DESCARGA_NASDAQCOM = Descarga(
    clave="NASDAQCOM",
    descripcion="FRED, NASDAQ Composite, cierre diario",
    clase_licencia=CLASE_NO_COMERCIAL_CON_RESERVA,
    licencia="Copyrighted: Pre-Approval Required; uso educativo no comercial",
    url=URL_CSV.format(id="NASDAQCOM"),
    extension="csv",
    atribucion=(
        "Nasdaq, Inc., NASDAQ Composite [NASDAQCOM], obtenido de FRED, Federal Reserve "
        "Bank of St. Louis. Copyright NASDAQ OMX Group, Inc."
    ),
)

DESCARGA_COIN_METRICS = Descarga(
    clave="coin_metrics_btc",
    descripcion="Coin Metrics community, PriceUSD de BTC, fixing diario de las 00:00 UTC",
    clase_licencia=CLASE_NO_COMERCIAL,
    licencia="CC BY-NC 4.0",
    url=(
        "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
        "?assets=btc&metrics=PriceUSD&frequency=1d&page_size=10000"
    ),
    extension="json",
    atribucion=(
        "Coin Metrics, datos community (PriceUSD). Licencia CC BY-NC 4.0. Se publica el "
        "promedio mensual de los valores diarios."
    ),
)

DESCARGAS = (
    DESCARGA_PINK_SHEET,
    DESCARGA_SHILLER,
    DESCARGA_NASDAQCOM,
    DESCARGA_COIN_METRICS,
)

# La convención del Pink Sheet es lo que su hoja Description dice que es. Si el
# Banco Mundial cambia una de estas dos frases, cambió lo que la serie mide —ya
# pasó una vez, en junio de 2025— y la corrida se detiene en vez de publicar una
# serie con otra definición bajo el mismo nombre. Ver A-R0-7 y A-R0-8.
PINK_SHEET_HOJA_PRECIOS = "Monthly Prices"
PINK_SHEET_HOJA_DESCRIPCION = "Description"
PINK_SHEET_UNIDAD = "($/troy oz)"
PINK_SHEET_DESCRIPCION_ORO = (
    "Gold, spot average of daily rates, from June 2025; previously (UK), 99.5% "
    "fine, London afternoon fixing, average of daily rates"
)
PINK_SHEET_DESCRIPCION_PLATA = (
    "Silver (UK), 99.9% refined, London afternoon fixing; prior to July 1976 "
    "Handy & Harman. Grade prior to 1962 unrefined silver."
)


@dataclass(frozen=True)
class EdicionCongelada:
    """Una edición vieja de una fuente, guardada tal cual y usada para un tramo fijo.

    El archivo está versionado en data/raw/ con un nombre fijo y se identifica
    por su SHA-256. El pipeline usa esa copia y no sale a la red a buscarla: si
    la URL deja de responder, nada cambia.
    """

    descarga: Descarga
    archivo: str  # nombre fijo dentro de data/raw/
    fecha_edicion: date  # la que la propia planilla declara
    fecha_descarga: date  # cuándo se bajó la copia versionada
    sha256: str
    ultimo_mes: str  # A-R0-19: último mes que se toma de esta edición
    descripcion_oro: str
    descripcion_plata: str


# A-R0-19: el empalme. De 1960-01 a 2024-12 el oro y la plata salen de esta
# edición, sin redondear; desde 2025-01, de la edición vigente, redondeada.
#
# La descripción del oro es la anterior al cambio de junio de 2025 (A-R0-7): en
# enero de 2025 todavía era el fixing de la tarde de Londres.
PINK_SHEET_CONGELADA = EdicionCongelada(
    descarga=DESCARGA_PINK_SHEET_CONGELADA,
    archivo="pink_sheet_edicion_2025-01-03.xlsx",
    fecha_edicion=date(2025, 1, 3),
    fecha_descarga=date(2026, 10, 4),
    sha256="bd89b83eeceadaecb803018c104f76b316d2df3fae28ef7afde48021100c7e11",
    ultimo_mes="2024-12",
    descripcion_oro="Gold (UK), 99.5% fine, London afternoon fixing, average of daily rates",
    descripcion_plata=PINK_SHEET_DESCRIPCION_PLATA,
)

# A-R0-7: primer mes del oro "spot". Antes es el fixing de la tarde de Londres.
ORO_QUIEBRE_DEFINICION = "2025-06"
ORO_DEFINICION_ANTES = "fixing de la tarde de Londres"
ORO_DEFINICION_DESPUES = "spot"

# A-R0-10: primer mes desde el cual dos fuentes independientes de BTC coinciden.
BTC_PRIMER_MES = "2013-01"

SERIE_ORO = SeriePrecio(
    clave="oro",
    nombre="Oro",
    descarga=DESCARGA_PINK_SHEET,
    unidad="USD por onza troy",
    estado=ESTADO_DATO,
    banda_plausible=(30.0, 50_000.0),
    supuestos=("A-R0-7", "A-R0-9", "A-R0-17", "A-R0-19"),
    medio_paso_redondeo=0.5,  # la edición vigente del Pink Sheet publica el oro al dólar entero
)

SERIE_PLATA = SeriePrecio(
    clave="plata",
    nombre="Plata",
    descarga=DESCARGA_PINK_SHEET,
    unidad="USD por onza troy",
    # A-R0-8: que la serie sea un promedio mensual se infiere, no está escrito.
    estado=ESTADO_ESTIMACION,
    banda_plausible=(0.5, 1_000.0),
    supuestos=("A-R0-8", "A-R0-9", "A-R0-17", "A-R0-19"),
    medio_paso_redondeo=0.05,  # y la plata, a un decimal
)

SERIE_BTC = SeriePrecio(
    clave="btc",
    nombre="BTC",
    descarga=DESCARGA_COIN_METRICS,
    unidad="USD por BTC",
    estado=ESTADO_DATO,
    banda_plausible=(1.0, 10_000_000.0),
    supuestos=("A-R0-4", "A-R0-5", "A-R0-10"),
    desde=BTC_PRIMER_MES,
)

SERIE_SP500 = SeriePrecio(
    clave="sp500",
    nombre="S&P 500",
    descarga=DESCARGA_SHILLER,
    unidad="puntos de índice",
    estado=ESTADO_DATO,
    banda_plausible=(2.0, 200_000.0),
    supuestos=("A-R0-2", "A-R0-11", "A-R0-13"),
)

SERIE_NASDAQ = SeriePrecio(
    clave="nasdaq",
    nombre="Nasdaq Composite",
    descarga=DESCARGA_NASDAQCOM,
    unidad="puntos de índice (5 de febrero de 1971 = 100)",
    estado=ESTADO_DATO,
    banda_plausible=(50.0, 1_000_000.0),
    supuestos=("A-R0-3", "A-R0-13"),
)

SERIES_PRECIO = (SERIE_ORO, SERIE_PLATA, SERIE_BTC, SERIE_SP500, SERIE_NASDAQ)

# Los cinco pares del sitio.
PARES = (
    Par("oro_plata", "Oro / Plata", "oro", "plata"),
    Par("btc_oro", "BTC / Oro", "btc", "oro"),
    Par("oro_sp500", "Oro / S&P 500", "oro", "sp500"),
    Par("btc_sp500", "BTC / S&P 500", "btc", "sp500"),
    Par("nasdaq_sp500", "Nasdaq / S&P 500", "nasdaq", "sp500"),
)

# El Nasdaq Composite arranca en 100 el 5 de febrero de 1971. Es la unidad de la
# serie, declarada por FRED, y se puede comprobar en los datos sin metadatos.
NASDAQ_FECHA_BASE = date(1971, 2, 5)
NASDAQ_VALOR_BASE = 100.0

# A-R0-12: contrastes. Las tolerancias se fijaron por encima de lo observado el
# 2026-10-04 y por debajo de lo que produce un error de convención. No se
# ajustan para que una corrida cierre.
VENTANA_CONTRASTE_NASDAQ_ANIOS = 10  # la misma ventana con la que se fijó la tolerancia

CONTRASTE_SP500 = Contraste(
    serie="sp500",
    fuente="FRED SP500, promedio mensual de los cierres diarios",
    url=URL_CSV.format(id="SP500"),
    tolerancia_pct=0.5,
)
CONTRASTE_NASDAQ = Contraste(
    serie="nasdaq",
    fuente="API de nasdaq.com, promedio mensual de los cierres diarios",
    url="https://api.nasdaq.com/api/quote/COMP/historical",
    tolerancia_pct=0.1,
)
CONTRASTE_BTC = Contraste(
    serie="btc",
    fuente="Bitstamp, promedio mensual de los cierres de la vela diaria UTC",
    url="https://www.bitstamp.net/api/v2/ohlc/btcusd/",
    tolerancia_pct=2.0,
    desde=BTC_PRIMER_MES,
)
CONTRASTES = (CONTRASTE_SP500, CONTRASTE_NASDAQ, CONTRASTE_BTC)

# A-R0-16: el gate de oro y plata. El promedio de los doce meses del Pink Sheet
# de un año tiene que cerrar contra el precio promedio anual que publica el USGS
# en sus Mineral Commodity Summaries (dominio público).
#
# Las tolerancias se fijaron el 2026-10-04 ANTES de calcular el gate, y su
# justificación está en A-R0-16: redondeo de las dos fuentes, el efecto de
# promediar promedios mensuales, y un margen para la diferencia de cotización
# (fixing de Londres contra Engelhard). No se cambian para que el gate cierre.
TOLERANCIA_GATE_ORO_PCT = 0.5
TOLERANCIA_GATE_PLATA_PCT = 1.0
MINIMO_ANIOS_GATE = 3

# Cifras transcritas a mano de la tabla "Salient Statistics—United States" de la
# edición de febrero de 2026. La columna de 2025 está marcada como estimada (con
# datos de enero a noviembre) y por eso no entra: solo años cerrados.
_MCS_2026 = "U.S. Geological Survey, Mineral Commodity Summaries, February 2026"
_MCS_2026_ORO = "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gold.pdf"
_MCS_2026_PLATA = "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-silver.pdf"
_FILA_ORO = (
    f"{_MCS_2026}, Gold, fila \"Price, dollars per troy ounce\" (Engelhard's "
    "average gold price quotation for the year)"
)
_FILA_PLATA = (
    f"{_MCS_2026}, Silver, fila \"Price, bullion, average, dollars per troy "
    "ounce\" (Engelhard's industrial bullion quotations)"
)
_LEIDO = date(2026, 10, 4)

ANCLAS_USGS = (
    AnclaAnual("oro", 2021, 1801.0, _FILA_ORO, _MCS_2026_ORO, _LEIDO),
    AnclaAnual("oro", 2022, 1802.0, _FILA_ORO, _MCS_2026_ORO, _LEIDO),
    AnclaAnual("oro", 2023, 1945.0, _FILA_ORO, _MCS_2026_ORO, _LEIDO),
    AnclaAnual("oro", 2024, 2388.0, _FILA_ORO, _MCS_2026_ORO, _LEIDO),
    AnclaAnual("plata", 2021, 25.23, _FILA_PLATA, _MCS_2026_PLATA, _LEIDO),
    AnclaAnual("plata", 2022, 21.88, _FILA_PLATA, _MCS_2026_PLATA, _LEIDO),
    AnclaAnual("plata", 2023, 23.54, _FILA_PLATA, _MCS_2026_PLATA, _LEIDO),
    AnclaAnual("plata", 2024, 28.37, _FILA_PLATA, _MCS_2026_PLATA, _LEIDO),
)

# Control adicional, más débil que el gate: los extremos del trimestre que LBMA
# publica sin licencia, en su informe trimestral.
_INFORME_LBMA_2026T2 = "https://www.lbma.org.uk/articles/lbma-precious-metals-market-report-q2-2026"
BANDAS_LBMA = (
    BandaTrimestral(
        serie="oro",
        meses=("2026-04", "2026-05", "2026-06"),
        minimo=3994.50,
        maximo=4870.50,
        fuente=(
            "LBMA Precious Metals Market Report, Q2 2026: Price Low 25 Jun am "
            "$3,994.50; Price High 17 Apr pm $4,870.50"
        ),
        fuente_url=_INFORME_LBMA_2026T2,
        fecha_lectura=date(2026, 10, 4),
    ),
    BandaTrimestral(
        serie="plata",
        meses=("2026-04", "2026-05", "2026-06"),
        minimo=57.37,
        maximo=86.79,
        fuente=(
            "LBMA Precious Metals Market Report, Q2 2026: Price Low 26 Jun "
            "$57.37; Price High 4 Apr $86.79"
        ),
        fuente_url=_INFORME_LBMA_2026T2,
        fecha_lectura=date(2026, 10, 4),
    ),
)

# A-R0-17: una métrica calculada sobre un ratio —percentiles, tendencias,
# evidencia— solo usa los meses en que el error máximo por redondeo del ratio
# no pasa de este umbral, en porcentaje. Los demás meses se publican con su
# error a la vista y marcados como no aptos. El umbral es un supuesto.
UMBRAL_ERROR_REDONDEO_PCT = 0.5

# Diferencia mínima para contar un cambio entre corridas como revisión de la
# fuente y no como redondeo del CSV.
EPSILON_REVISION_PRECIOS = 0.0005
EPSILON_REVISION_RATIOS = 0.000001

# Diez cifras significativas. Con seis decimales fijos, un ratio de 0.0094 se
# quedaría en cuatro cifras.
FORMATO_RATIOS = "%.10g"

ARCHIVO_PRECIOS = DIR_SERIES / "precios_mensuales.csv"
ARCHIVO_RATIOS = DIR_SERIES / "ratios.csv"
ARCHIVO_PARES = DIR_SERIES / "pares.csv"
ARCHIVO_SERIES_INFO = DIR_SERIES / "series.csv"
ARCHIVO_DESCARGAS = DIR_SERIES / "descargas_ratios.csv"
ARCHIVO_INTERNO = DIR_SERIES_PRIVADO / "ratios_internos.csv"

COLUMNAS_PRECIOS = [
    "mes",
    "oro_usd_oz",
    "oro_error_redondeo_pct",
    "oro_definicion",
    "plata_usd_oz",
    "plata_error_redondeo_pct",
    "plata_estado",
    "pink_sheet_edicion",
    "btc_usd",
]
COLUMNAS_RATIOS = ["mes", "par", "valor", "error_redondeo_pct", "apto_metricas", "estado"]
COLUMNAS_PARES = [
    "par",
    "nombre",
    "publicado",
    "estado",
    "primer_mes",
    "ultimo_mes",
    "meses",
    "apto_desde",
    "meses_aptos",
]
COLUMNAS_SERIES_INFO = [
    "serie",
    "nombre",
    "publicada",
    "estado",
    "unidad",
    "fuente",
    "licencia",
    "atribucion",
    "validacion",
    "supuestos",
    "primer_mes",
    "ultimo_mes",
    "meses",
]
# Todo lo que se calcula, se publique o no. Va fuera del repositorio.
COLUMNAS_INTERNO = [
    "mes",
    "oro",
    "plata",
    "btc",
    "sp500",
    "nasdaq",
    "oro_plata",
    "btc_oro",
    "oro_sp500",
    "btc_sp500",
    "nasdaq_sp500",
]
COLUMNAS_DESCARGAS = [
    "fecha_descarga",
    "fuente",
    "clase_licencia",
    "licencia",
    "url",
    "bytes",
    "sha256",
    "actualizada",
    "crudo_en_repo",
]
