"""Configuración central del marco de señales.

Todo parámetro que afecte un número publicado vive en este archivo, no en el
código de cálculo. Cambiar un valor de aquí obliga a registrar el cambio en
SUPUESTOS.md y en data/series/CHANGELOG.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from fractions import Fraction
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
# Mientras sea None, la salida reporta "NO MEDIDO". No inventar un valor aquí.
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
# Todo lo de aquí sale de FUENTES.md (qué se leyó de cada fuente) y de los
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
    # A-D0-27: la licencia es condición necesaria, no suficiente. Un crudo de más
    # de 1 MB, o el de una fuente que solo sirve de contraste, no se versiona
    # aunque se pueda: queda fuera del repositorio, con su hash en el manifiesto.
    versionar: bool = True
    # A-D0-29: el crudo no se pide nunca con un programa; lo deja una persona en el
    # directorio de crudos. El pipeline usa la copia más reciente y verifica su hash.
    manual: bool = False

    @property
    def crudo_versionado(self) -> bool:
        """A-R0-15: el crudo entra al repositorio si su licencia permite redistribuirlo.

        Eso es CC BY (clase a) y CC BY-NC (clase b), siempre con atribución. Una
        fuente sin licencia declarada, o con dos textos que no coinciden, no.
        """
        return self.versionar and self.clase_licencia in (CLASE_ABIERTA, CLASE_NO_COMERCIAL)


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

# A-R0-20: la base mensual de precios de materias primas del FMI. No alimenta
# ninguna serie: es la referencia del control mensual del oro y la plata. Los
# términos del FMI dejan redistribuir sus datos con atribución y prohíben la
# descarga masiva por medios automatizados. Por eso es una copia bajada una vez,
# versionada en data/raw/, y el pipeline nunca sale a buscarla.
DESCARGA_FMI = Descarga(
    clave="fmi_pcps",
    descripcion="FMI, Primary Commodity Prices, base mensual (external-data.xlsx)",
    clase_licencia=CLASE_NO_COMERCIAL,
    licencia=(
        "Términos del FMI para datos estadísticos: uso libre con atribución; "
        "reuso comercial con permiso"
    ),
    url="https://www.imf.org/-/media/files/research/commodityprices/monthly/external-data.xlsx",
    extension="xlsx",
    atribucion=(
        "Source: International Monetary Fund, Primary Commodity Prices, "
        "https://www.imf.org/en/research/commodity-prices. Los valores se citan sin cambios."
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


@dataclass(frozen=True)
class CopiaManual:
    """Un archivo de referencia bajado una vez, a mano, que viaja con el repositorio.

    A diferencia de una edición congelada, el pipeline nunca sale a buscarlo: si
    la copia falta, la corrida se detiene y dice de dónde bajarla.
    """

    descarga: Descarga
    archivo: str  # nombre fijo dentro de data/raw/
    edicion: str  # como la nombra la fuente
    fecha_descarga: date
    sha256: str


# A-R0-20: la copia del FMI contra la que se compara el Pink Sheet. La
# descripción de cada serie es la que la planilla traía al leerla; si cambia,
# cambió lo que la serie mide y la corrida se detiene.
FMI_HOJA = "External"
FMI_CODIGO_ORO = "PGOLD"
FMI_DESCRIPCION_ORO = (
    "Gold, Fixing Committee of the London Bullion Market Association, London 3 PM "
    "fixed price, US$ per troy ounce"
)
FMI_CODIGO_PLATA = "PSILVER"
FMI_DESCRIPCION_PLATA = "Silver, London Bullion Market Association, USD/troy ounce"

FMI_COPIA = CopiaManual(
    descarga=DESCARGA_FMI,
    archivo="fmi_pcps_2026-10-04.xlsx",
    edicion="Excel Database: September 2026",
    fecha_descarga=date(2026, 10, 4),
    sha256="e0bc0cbbd08208e9868fb16e21992ff4b86a7676a2b5f64d32a02bdb8bdcc464",
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
    supuestos=("A-R0-7", "A-R0-9", "A-R0-17", "A-R0-19", "A-R0-20"),
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
    supuestos=("A-R0-8", "A-R0-9", "A-R0-17", "A-R0-19", "A-R0-20"),
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

# A-R0-20: control mensual del oro y la plata contra el FMI, sobre todo el
# historial que tienen en común. Un mes cuya diferencia pasa del umbral queda
# como "valor en disputa": se publica sin cambios y no entra a ninguna métrica.
# No detiene la corrida.
#
# El umbral es la tolerancia del gate anual (A-R0-16), que ya estaba fijada: no
# se eligió un número nuevo después de ver la comparación. No se ajusta para que
# un mes entre o salga.
UMBRAL_DISPUTA_PCT = {"oro": TOLERANCIA_GATE_ORO_PCT, "plata": TOLERANCIA_GATE_PLATA_PCT}
VALOR_EN_DISPUTA = "valor en disputa"
CONTRASTE_FMI_DENTRO = "dentro del umbral"
CONTRASTE_FMI_SIN_COMPARAR = "sin comparar"

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
    "oro_contraste_fmi",
    "plata_usd_oz",
    "plata_error_redondeo_pct",
    "plata_estado",
    "plata_contraste_fmi",
    "pink_sheet_edicion",
    "btc_usd",
]
COLUMNAS_RATIOS = [
    "mes",
    "par",
    "valor",
    "error_redondeo_pct",
    "valor_en_disputa",
    "apto_metricas",
    "estado",
]
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
    "meses_en_disputa",
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


# ---------------------------------------------------------------------------
# Fase D0: El Denominador (dinero, balances de bancos centrales y tipos de cambio)
#
# Todo lo de aquí sale de FUENTES.md, sección D0 (qué se leyó de cada fuente),
# y de los supuestos A-D0-* de SUPUESTOS.md (qué se decidió con eso).
# ---------------------------------------------------------------------------

# A-D0-29: lo que se publica cuando el robots.txt de la fuente veda la descarga
# y nadie dejó una copia bajada a mano.
NO_MEDIDO_ACCESO_VEDADO = "NO MEDIDO: el robots.txt de la fuente veda la descarga y no hay copia a mano"

FAMILIA_DINERO = "dinero"
FAMILIA_BALANCE = "balance"
FAMILIA_CAMBIO = "tipo de cambio"

_JUNTA = "Board of Governors of the Federal Reserve System (US)"
_LICENCIA_JUNTA = "Dominio público (Junta de la Reserva Federal)"
_ATRIBUCION_JUNTA = (
    _JUNTA + ", {publicacion}. Dominio público; la Junta pide que se la cite como fuente. "
    "Los valores se publican sin cambios."
)
_LICENCIA_BCE = "Gratuita con atribución (política de reutilización de las estadísticas del SEBC)"
_ATRIBUCION_BCE = (
    "Source: ECB statistics (ECB Data Portal, {conjunto}). Los valores se publican sin "
    "cambios; toda serie derivada se rotula como cálculo propio (A-D0-7)."
)
_LICENCIA_BOJ = "Reproducción con cita de la fuente, salvo fines comerciales (Banco de Japón)"
_ATRIBUCION_BOJ = (
    "Fuente: Bank of Japan, BOJ Time-Series Data Search ({base}). Este servicio usa la API "
    "de «BOJ Time-Series Data Search»; el Banco de Japón no garantiza su contenido. Los "
    "valores se publican sin cambios. Válido mientras el sitio no tenga vínculo comercial "
    "(A-D0-8)."
)
_LICENCIA_BIS = "Términos de uso de las estadísticas del BIS: uso libre citando al BIS"
_LICENCIA_OCDE = "Términos de la OCDE: uso libre con crédito, con reserva por derechos de terceros"


def _descarga_junta(clave: str, publicacion: str, archivo: str) -> Descarga:
    return Descarga(
        clave=clave,
        descripcion=f"Junta de la Reserva Federal, {publicacion}, historia completa en XML",
        clase_licencia=CLASE_ABIERTA,
        licencia=_LICENCIA_JUNTA,
        url=f"https://www.federalreserve.gov/releases/{archivo}",
        extension="zip",
        atribucion=_ATRIBUCION_JUNTA.format(publicacion=publicacion),
        versionar=False,  # A-D0-27: entre 1.4 y 9 MB cada uno
    )


def _descarga_bce(clave: str, conjunto: str, serie: str, que: str) -> Descarga:
    """A-D0-29: el robots.txt de data-api.ecb.europa.eu veda a python-requests.

    La URL es la que una persona abre en el navegador para guardar el archivo;
    el pipeline nunca la pide.
    """
    return Descarga(
        clave=clave,
        descripcion=f"BCE, ECB Data Portal, conjunto {conjunto}: {que} (copia bajada a mano)",
        clase_licencia=CLASE_ABIERTA,
        licencia=_LICENCIA_BCE,
        url=f"https://data-api.ecb.europa.eu/service/data/{conjunto}/{serie}?format=csvdata",
        extension="csv",
        atribucion=_ATRIBUCION_BCE.format(conjunto=conjunto),
        manual=True,
    )


def _contraste(clave: str, descripcion: str, url: str, extension: str) -> Descarga:
    """Una fuente que solo se lee para comparar. Su crudo no se versiona (A-D0-27)."""
    return Descarga(
        clave=clave,
        descripcion=descripcion,
        clase_licencia=CLASE_ABIERTA,
        licencia="solo contraste: no alimenta ninguna serie",
        url=url,
        extension=extension,
        atribucion="",
        versionar=False,
    )


DESCARGA_H6 = _descarga_junta("junta_h6", "H.6 Money Stock Measures", "h6/data/FRB_h6_xml.zip")
DESCARGA_H10 = _descarga_junta("junta_h10", "H.10 Foreign Exchange Rates", "h10/data/FRB_h10_xml.zip")
DESCARGA_H41 = _descarga_junta(
    "junta_h41", "H.4.1 Factors Affecting Reserve Balances", "h41/data/FRB_h41_xml.zip"
)

BCE_CLAVE_M2_AJUSTADA = "BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E"
BCE_CLAVE_M2_SIN_AJUSTAR = "BSI.M.U2.N.V.M20.X.1.U2.2300.Z01.E"
BCE_CLAVE_BALANCE = "ILM.W.U2.C.T000000.Z5.Z01"
DESCARGA_BCE_M2_AJUSTADA = _descarga_bce(
    "bce_m2_ajustada", "BSI", "M.U2.Y.V.M20.X.1.U2.2300.Z01.E", "M2 de la zona del euro, ajustada"
)
DESCARGA_BCE_M2_SIN_AJUSTAR = _descarga_bce(
    "bce_m2_sin_ajustar", "BSI", "M.U2.N.V.M20.X.1.U2.2300.Z01.E", "M2 de la zona del euro, sin ajustar"
)
DESCARGA_BCE_BALANCE = _descarga_bce(
    "bce_balance_eurosistema", "ILM", "W.U2.C.T000000.Z5.Z01", "total de activos del Eurosistema"
)

_API_BOJ = "https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en"
BOJ_CODIGO_M2 = "MAM1NAM2M2MO"
BOJ_CODIGO_BALANCE = "MABJMTA"
DESCARGA_BOJ_M2 = Descarga(
    clave="boj_m2",
    descripcion="Banco de Japón, Money Stock (base MD02): M2 y series anteriores",
    clase_licencia=CLASE_NO_COMERCIAL,
    licencia=_LICENCIA_BOJ,
    url=_API_BOJ + "&db=MD02&code=MAM1NAM2M2MO,MAM1XAM2M2MO,MAM1NAM3M3MO,MAM1NEM3M3MO,"
    "MAMS3ANM2C,MAMS3ENM2C,MAMS1ANM2C,MAMS1ENM2C",
    extension="csv",
    atribucion=_ATRIBUCION_BOJ.format(base="Money Stock, MD02"),
)
DESCARGA_BOJ_BALANCE = Descarga(
    clave="boj_balance",
    descripcion="Banco de Japón, Bank of Japan Accounts (base BS01): total de activos",
    clase_licencia=CLASE_NO_COMERCIAL,
    licencia=_LICENCIA_BOJ,
    url=_API_BOJ + "&db=BS01&code=MABJMTA,MABJMA5,MABJML1,MABJML11",
    extension="csv",
    atribucion=_ATRIBUCION_BOJ.format(base="Bank of Japan Accounts, BS01"),
)

OCDE_AREA_CHINA = "CHN"
OCDE_MEDIDA_DINERO_AMPLIO = "MABM"
DESCARGA_OCDE_CHINA = Descarga(
    clave="ocde_china_dinero_amplio",
    descripcion="OCDE, Monetary aggregates (DF_MONAGG): dinero amplio de China, serie CHN.M.MABM.XDC",
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_OCDE,
    url="https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_MONAGG,"
    "/CHN.M.MABM.XDC.....?format=csvfilewithlabels",
    extension="csv",
    atribucion=(
        "OECD (2026), Monetary aggregates, serie CHN.M.MABM.XDC. Emisor original: Banco "
        "Popular de China. La serie lleva el rótulo que le pone la OCDE (A-D0-9). Los "
        "valores se publican sin cambios."
    ),
)


def _descarga_bis_activos(area: str, versionar: bool) -> Descarga:
    return Descarga(
        clave=f"bis_cbta_{area.lower()}",
        descripcion=f"BIS, Central bank total assets (WS_CBTA), área {area}",
        clase_licencia=CLASE_ABIERTA,
        licencia=_LICENCIA_BIS,
        url=f"https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.{area}?format=csv",
        extension="csv",
        atribucion=(
            "Fuente: BIS, Central bank total assets (WS_CBTA). Emisor original: Banco "
            "Popular de China. Serie empalmada por el BIS. Los valores se publican sin cambios."
            if versionar
            else ""
        ),
        versionar=versionar,
    )


DESCARGA_BIS_ACTIVOS_CN = _descarga_bis_activos("CN", versionar=True)
DESCARGA_BIS_ACTIVOS_US = _descarga_bis_activos("US", versionar=False)
DESCARGA_BIS_ACTIVOS_XM = _descarga_bis_activos("XM", versionar=False)
DESCARGA_BIS_ACTIVOS_JP = _descarga_bis_activos("JP", versionar=False)

# Fuentes que solo se leen para comparar.
CONTRASTE_H6_HTML = _contraste(
    "junta_h6_html",
    "Junta de la Reserva Federal, H.6, Tabla 1 de la publicación vigente en HTML",
    "https://www.federalreserve.gov/releases/h6/current/default.htm",
    "html",
)
CONTRASTE_FRED_WALCL = _contraste(
    "fred_walcl",
    "FRED, serie WALCL (Federal Reserve Bank of St. Louis)",
    "https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL",
    "csv",
)
BDE_CODIGO_M2_AJUSTADA = "D_MU2YVM20X1U22300Z01E"
BDE_CODIGO_M2_SIN_AJUSTAR = "D_MUM200LIPBIF"  # "Agregados monetarios de la UEM. M2. Saldos", sin ajustar
CONTRASTE_BDE_AJUSTADA = _contraste(
    "bde_m2_ajustada",
    "Banco de España, Boletín Estadístico, cuadro 1.12 (agregados de la UEM, ajustados)",
    "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0112.csv",
    "csv",
)
CONTRASTE_BDE_SIN_AJUSTAR = _contraste(
    "bde_m2_sin_ajustar",
    "Banco de España, Boletín Estadístico, cuadro 1.10 (agregados de la UEM, sin ajustar)",
    "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be0110.csv",
    "csv",
)
ESTAT_INDICADOR_M2 = "0702010200000010010"
CONTRASTE_ESTAT = _contraste(
    "estat_m2_japon",
    "e-Stat Statistics Dashboard (gobierno de Japón), indicador Money stock (M2)",
    "https://dashboard.e-stat.go.jp/api/1.0/Json/getData?Lang=EN&IndicatorCode=" + ESTAT_INDICADOR_M2,
    "json",
)


def _contraste_cambio(area: str) -> Descarga:
    return _contraste(
        f"bis_xru_{area.lower()}",
        f"BIS, US dollar exchange rates (WS_XRU), área {area}",
        f"https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.{area}?format=csv",
        "csv",
    )


CONTRASTE_BIS_CAMBIO_XM = _contraste_cambio("XM")
CONTRASTE_BIS_CAMBIO_JP = _contraste_cambio("JP")
CONTRASTE_BIS_CAMBIO_CN = _contraste_cambio("CN")


@dataclass(frozen=True)
class Quiebre:
    """Un cambio de definición o de perímetro que la fuente declara, con su mes."""

    mes: str  # "AAAA-MM"
    texto: str


@dataclass(frozen=True)
class SerieD0:
    """Una serie de la fase D0 y lo que va en su ficha."""

    clave: str
    nombre: str
    familia: str
    descarga: Descarga
    identificador: str  # el nombre de la serie en la fuente
    emisor: str
    unidad: str
    convencion: str
    frecuencia_nativa: str
    ajuste: str
    estado: str
    supuestos: tuple[str, ...]
    banda_plausible: tuple[float, float]  # control de orden de magnitud, en la unidad de la serie
    quiebres: tuple[Quiebre, ...] = ()
    # A-D0-5: hasta este mes inclusive, la serie es una estimación de su emisor.
    estimacion_hasta: str | None = None
    # Primer mes que se publica, si la fuente trae historia que no se usa.
    desde: str | None = None

    @property
    def publicable(self) -> bool:
        """A-R0-14: se publica lo que la licencia permite publicar sin interpretarla."""
        return self.descarga.clase_licencia in (CLASE_ABIERTA, CLASE_NO_COMERCIAL)


# A-D0-4: las ampliaciones de la zona del euro, leídas del manual de las
# estadísticas BSI del BCE (sección 5.7.3) y de su comunicado del 1 de enero de
# 2026. Cada una es un salto de nivel que la serie de saldos no marca.
AMPLIACIONES_EUROZONA = (
    Quiebre("2001-01", "ampliación de la zona del euro: Grecia"),
    Quiebre("2007-01", "ampliación de la zona del euro: Eslovenia"),
    Quiebre("2008-01", "ampliación de la zona del euro: Chipre y Malta"),
    Quiebre("2009-01", "ampliación de la zona del euro: Eslovaquia"),
    Quiebre("2011-01", "ampliación de la zona del euro: Estonia"),
    Quiebre("2014-01", "ampliación de la zona del euro: Letonia"),
    Quiebre("2015-01", "ampliación de la zona del euro: Lituania"),
    Quiebre("2023-01", "ampliación de la zona del euro: Croacia"),
    Quiebre("2026-01", "ampliación de la zona del euro: Bulgaria"),
)
EUROZONA_ESTIMACION_HASTA = "1997-08"

_SUP_EEUU = ("A-D0-1", "A-D0-2", "A-D0-3")
_SUP_EUROZONA = ("A-D0-1", "A-D0-4", "A-D0-5", "A-D0-7")
_EMISOR_JUNTA = "Junta de Gobernadores del Sistema de la Reserva Federal"
_EMISOR_BCE = "BCE y bancos centrales nacionales del Eurosistema"

SERIE_M2_EEUU = SerieD0(
    clave="m2_eeuu",
    nombre="M2 de EE.UU.",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_H6,
    identificador="M2.M",
    emisor=_EMISOR_JUNTA,
    unidad="miles de millones de USD",
    convencion="promedio mensual de cifras diarias",
    frecuencia_nativa="mensual",
    ajuste="ajustada por estacionalidad",
    estado=ESTADO_DATO,
    supuestos=_SUP_EEUU,
    banda_plausible=(200.0, 200_000.0),
)
SERIE_M2_EEUU_SIN_AJUSTAR = SerieD0(
    clave="m2_eeuu_sin_ajustar",
    nombre="M2 de EE.UU., sin ajustar",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_H6,
    identificador="M2_N.M",
    emisor=_EMISOR_JUNTA,
    unidad="miles de millones de USD",
    convencion="promedio mensual de cifras diarias",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=_SUP_EEUU,
    banda_plausible=(200.0, 200_000.0),
)
SERIE_M2_EUROZONA = SerieD0(
    clave="m2_eurozona",
    nombre="M2 de la Eurozona",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BCE_M2_AJUSTADA,
    identificador=BCE_CLAVE_M2_AJUSTADA,
    emisor=_EMISOR_BCE,
    unidad="millones de EUR",
    convencion="saldo a fin de mes",
    frecuencia_nativa="mensual",
    ajuste="ajustada por estacionalidad y días hábiles",
    estado=ESTADO_DATO,
    supuestos=_SUP_EUROZONA,
    banda_plausible=(500_000.0, 200_000_000.0),
    quiebres=AMPLIACIONES_EUROZONA,
    estimacion_hasta=EUROZONA_ESTIMACION_HASTA,
)
SERIE_M2_EUROZONA_SIN_AJUSTAR = SerieD0(
    clave="m2_eurozona_sin_ajustar",
    nombre="M2 de la Eurozona, sin ajustar",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BCE_M2_SIN_AJUSTAR,
    identificador=BCE_CLAVE_M2_SIN_AJUSTAR,
    emisor=_EMISOR_BCE,
    unidad="millones de EUR",
    convencion="saldo a fin de mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=_SUP_EUROZONA,
    banda_plausible=(500_000.0, 200_000_000.0),
    quiebres=AMPLIACIONES_EUROZONA,
    estimacion_hasta=EUROZONA_ESTIMACION_HASTA,
)
SERIE_M2_JAPON = SerieD0(
    clave="m2_japon",
    nombre="M2 de Japón",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BOJ_M2,
    identificador=BOJ_CODIGO_M2,
    emisor="Banco de Japón",
    unidad="100 millones de JPY",
    convencion="promedio de saldos del mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=("A-D0-1", "A-D0-6", "A-D0-8"),
    banda_plausible=(1_000_000.0, 100_000_000.0),
)

# A-D0-34: las series antiguas del BoJ (estadística "Money Supply", マネーサプライ;
# el BoJ las rotula en inglés "(Reference) Money Stock"), separadas y sin
# empalmar con el M2 actual (A-D0-6). Vienen en el mismo crudo que el M2.
BOJ_CODIGO_M2CD_1967_1999 = "MAMS1ANM2C"
BOJ_CODIGO_M2CD_1998_2008 = "MAMS3ANM2C"
CLAVE_M2CD_1967_1999 = "m2cd_japon_1967_1999"
CLAVE_M2CD_1998_2008 = "m2cd_japon_1998_2008"
_SUP_M2CD = ("A-D0-1", "A-D0-6", "A-D0-8", "A-D0-34", "A-D0-35")
SERIE_M2CD_JAPON_1967_1999 = SerieD0(
    clave=CLAVE_M2CD_1967_1999,
    nombre=(
        "M2+CDs de Japón (Money Supply, sin bancos extranjeros en Japón; serie discontinuada por el "
        "BoJ, 1967–1999)"
    ),
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BOJ_M2,
    identificador=BOJ_CODIGO_M2CD_1967_1999,
    emisor="Banco de Japón",
    unidad="100 millones de JPY",
    convencion="promedio de saldos del mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=_SUP_M2CD,
    banda_plausible=(100_000.0, 10_000_000.0),
    quiebres=(
        Quiebre(
            "1979-05",
            "nacen los certificados de depósito y el agregado pasa a llamarse M2+CDs; el perímetro no cambia",
        ),
        Quiebre(
            "1998-04",
            "entran los bancos extranjeros en Japón, los fideicomisos extranjeros y Shinkin Central Bank: la "
            "historia sigue en m2cd_japon_1998_2008, que en los 12 meses comunes queda entre 0.41 % y 0.48 % "
            "por encima",
        ),
    ),
)
SERIE_M2CD_JAPON_1998_2008 = SerieD0(
    clave=CLAVE_M2CD_1998_2008,
    nombre=(
        "M2+CDs de Japón (Money Supply, con bancos extranjeros en Japón; serie discontinuada por el "
        "BoJ, 1998–2008)"
    ),
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BOJ_M2,
    identificador=BOJ_CODIGO_M2CD_1998_2008,
    emisor="Banco de Japón",
    unidad="100 millones de JPY",
    convencion="promedio de saldos del mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=_SUP_M2CD,
    banda_plausible=(1_000_000.0, 100_000_000.0),
    quiebres=(
        Quiebre(
            "2003-04",
            "empieza el M2 de las Money Stock Statistics (m2_japon), con otro perímetro de tenedores y sin "
            "los depósitos en yenes de no residentes; en los 61 meses comunes el M2 nuevo queda entre "
            "0.42 % y 0.59 % por debajo",
        ),
    ),
)

# A-D0-35: la segunda fuente de las series antiguas es la copia del FMI en FRED
# (International Financial Statistics, en yenes, múltiplos de 10^8). Se lee y se
# compara; el crudo queda en data/privado mientras no se lean los términos del FMI.
FRED_SERIE_FMI_M2_JAPON = "MYAGM2JPM189N"
CONTRASTE_FRED_FMI_JAPON = Descarga(
    clave="fred_fmi_m2_japon",
    descripcion=(
        "FRED, serie MYAGM2JPM189N: M2 de Japón según el FMI (International Financial Statistics), "
        "sin ajustar, en yenes, 1967-01 a 2017-02"
    ),
    clase_licencia=CLASE_SIN_DECLARAR,
    licencia=(
        "FMI, derechos reservados; FRED la publica 'reprinted with permission'. Términos del FMI no "
        "leídos. Solo contraste: no alimenta ninguna serie y su crudo no se versiona"
    ),
    url=URL_CSV.format(id=FRED_SERIE_FMI_M2_JAPON),
    extension="csv",
    atribucion="",
    versionar=False,
)
# FRED publica múltiplos de 10^8 yenes: medio paso en 100 millones de yenes es
# exigir el mismo entero. La copia del FMI sigue a cada tramo del BoJ en un
# rango que se observó en el paso 0 (FUENTES.md, D0.5.1) y se declara aquí:
# hasta 1998-03 al tramo sin bancos extranjeros, de 1998-04 a 2003-03 al tramo
# con bancos extranjeros, y desde 2003-04 al M2 actual. Fuera de esos rangos
# no se compara. El resultado de esta comparación ya se conocía al fijar la
# tolerancia (435 meses iguales); la tolerancia no depende de él.
TOLERANCIA_FRED_FMI_JAPON = 0.5
RANGO_CONTRASTE_M2CD = {
    CLAVE_M2CD_1967_1999: (None, "1998-03"),
    CLAVE_M2CD_1998_2008: ("1998-04", "2003-03"),
}
# A-D0-9: no se llama M2. El nombre lleva el rótulo que le pone la OCDE, que
# se lee del archivo en cada corrida. Se publica desde el primer mes en que el
# PBoC tiene una tabla de oferta monetaria contra la cual se la comparó.
SERIE_DINERO_AMPLIO_CHINA = SerieD0(
    clave="dinero_amplio_china",
    nombre="Dinero amplio de China ({rotulo} de la OCDE)",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_OCDE_CHINA,
    identificador="CHN.M.MABM.XDC",
    emisor="Banco Popular de China, republicado por la OCDE",
    unidad="millones de CNY",
    convencion="saldo a fin de mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=("A-D0-1", "A-D0-9"),
    banda_plausible=(1_000_000.0, 5_000_000_000.0),
    quiebres=(
        Quiebre(
            "2011-10",
            "cambio de definición declarado por el PBoC: entran los depósitos de instituciones "
            "financieras no depositarias y del fondo de vivienda",
        ),
        Quiebre(
            "2018-01",
            "cambio de definición declarado por el PBoC (fondos del mercado monetario); la "
            "OCDE no revisó 2017 y el salto le cae en este mes",
        ),
    ),
    desde="2004-01",
)
SERIE_BALANCE_FED = SerieD0(
    clave="balance_fed",
    nombre="Balance de la Reserva Federal: total de activos, consolidado",
    familia=FAMILIA_BALANCE,
    descarga=DESCARGA_H41,
    identificador="RESPPMA_N.WW",
    emisor=_EMISOR_JUNTA,
    unidad="millones de USD",
    convencion="nivel del último miércoles del mes",
    frecuencia_nativa="semanal",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=("A-D0-1", "A-D0-14", "A-D0-15"),
    banda_plausible=(500_000.0, 50_000_000.0),
)
SERIE_BALANCE_EUROSISTEMA = SerieD0(
    clave="balance_eurosistema",
    nombre="Balance del Eurosistema: total de activos",
    familia=FAMILIA_BALANCE,
    descarga=DESCARGA_BCE_BALANCE,
    identificador=BCE_CLAVE_BALANCE,
    emisor=_EMISOR_BCE,
    unidad="millones de EUR",
    convencion="cierre del último viernes del mes",
    frecuencia_nativa="semanal",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=("A-D0-1", "A-D0-7", "A-D0-14", "A-D0-16"),
    banda_plausible=(500_000.0, 50_000_000.0),
    quiebres=AMPLIACIONES_EUROZONA,
)
SERIE_BALANCE_BOJ = SerieD0(
    clave="balance_boj",
    nombre="Balance del Banco de Japón: total de activos",
    familia=FAMILIA_BALANCE,
    descarga=DESCARGA_BOJ_BALANCE,
    identificador=BOJ_CODIGO_BALANCE,
    emisor="Banco de Japón",
    unidad="100 millones de JPY",
    convencion="saldo a fin de mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=("A-D0-1", "A-D0-8", "A-D0-16"),
    banda_plausible=(500_000.0, 50_000_000.0),
    quiebres=(
        Quiebre(
            "2001-04",
            "cambio contable de las operaciones repo: el total no es comparable con los "
            "meses anteriores",
        ),
    ),
)
SERIE_BALANCE_PBOC = SerieD0(
    clave="balance_pboc",
    nombre="Balance del Banco Popular de China: total de activos (BIS)",
    familia=FAMILIA_BALANCE,
    descarga=DESCARGA_BIS_ACTIVOS_CN,
    identificador="WS_CBTA, M.CN, moneda local",
    emisor="Banco Popular de China, republicado por el BIS",
    unidad="miles de millones de CNY",
    convencion="saldo a fin de mes",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=("A-D0-1", "A-D0-9"),
    banda_plausible=(1_000.0, 500_000.0),
    # El BIS declara que usa el balance mensual del PBoC desde enero de 2002.
    desde="2002-01",
)


def _serie_cambio(clave: str, nombre: str, identificador: str, unidad: str, banda) -> SerieD0:
    return SerieD0(
        clave=clave,
        nombre=nombre,
        familia=FAMILIA_CAMBIO,
        descarga=DESCARGA_H10,
        identificador=identificador,
        emisor=_EMISOR_JUNTA,
        unidad=unidad,
        convencion="tipo comprador del mediodía en Nueva York: promedio del mes y último día del mes",
        frecuencia_nativa="diaria",
        ajuste="no aplica",
        estado=ESTADO_DATO,
        supuestos=("A-D0-1", "A-D0-10"),
        banda_plausible=banda,
    )


SERIE_USD_POR_EUR = _serie_cambio(
    "usd_por_eur", "Tipo de cambio: USD por EUR", "RXI$US_N.M.EU y RXI$US_N.B.EU", "USD por EUR", (0.5, 2.5)
)
SERIE_JPY_POR_USD = _serie_cambio(
    "jpy_por_usd", "Tipo de cambio: JPY por USD", "RXI_N.M.JA y RXI_N.B.JA", "JPY por USD", (50.0, 500.0)
)
SERIE_CNY_POR_USD = _serie_cambio(
    "cny_por_usd", "Tipo de cambio: CNY por USD", "RXI_N.M.CH y RXI_N.B.CH", "CNY por USD", (1.0, 20.0)
)

SERIES_DINERO = (
    SERIE_M2CD_JAPON_1967_1999,
    SERIE_M2CD_JAPON_1998_2008,
    SERIE_M2_EEUU,
    SERIE_M2_EEUU_SIN_AJUSTAR,
    SERIE_M2_EUROZONA,
    SERIE_M2_EUROZONA_SIN_AJUSTAR,
    SERIE_M2_JAPON,
    SERIE_DINERO_AMPLIO_CHINA,
)
SERIES_BALANCE = (SERIE_BALANCE_FED, SERIE_BALANCE_EUROSISTEMA, SERIE_BALANCE_BOJ, SERIE_BALANCE_PBOC)
SERIES_CAMBIO = (SERIE_USD_POR_EUR, SERIE_JPY_POR_USD, SERIE_CNY_POR_USD)
SERIES_D0 = SERIES_DINERO + SERIES_BALANCE + SERIES_CAMBIO

# Las series de la Junta, por su nombre en el XML, y su multiplicador de unidad.
JUNTA_SERIES_H6 = {"m2_eeuu": "M2.M", "m2_eeuu_sin_ajustar": "M2_N.M"}
JUNTA_MULTIPLICADOR_H6 = 1e9
JUNTA_SERIE_BALANCE = "RESPPMA_N.WW"  # A-D0-15: total de activos menos eliminaciones
JUNTA_SERIE_BALANCE_SIN_CONSOLIDAR = "RESPPA_N.WW"
JUNTA_SERIE_ELIMINACIONES = "RESPPMAX_N.WW"
JUNTA_MULTIPLICADOR_H41 = 1e6
# clave de la serie -> (serie mensual, serie diaria)
JUNTA_SERIES_H10 = {
    "usd_por_eur": ("RXI$US_N.M.EU", "RXI$US_N.B.EU"),
    "jpy_por_usd": ("RXI_N.M.JA", "RXI_N.B.JA"),
    "cny_por_usd": ("RXI_N.M.CH", "RXI_N.B.CH"),
}
JUNTA_MULTIPLICADOR_H10 = 1.0

# --- Validación (A-D0-25) ----------------------------------------------------
#
# Las tolerancias salen de la precisión con que cada fuente publica el dato, no
# de lo observado. Están en la unidad de la serie salvo las que dicen "_PCT".
TOLERANCIA_H6_HTML = 0.05  # la Tabla 1 publica un decimal
TOLERANCIA_BDE = 0.5  # el Banco de España publica en millones enteros
TOLERANCIA_ESTAT = 0.5  # e-Stat publica el mismo entero que el BoJ
TOLERANCIA_BIS_FED = 5.0  # el BIS publica dos decimales en miles de millones: medio paso, 5 millones
TOLERANCIA_BIS_EUROSISTEMA = 0.5  # tres decimales: medio paso, 0.5 millones
TOLERANCIA_BIS_BOJ = 0.5  # un decimal en miles de millones de JPY: 0.5 en la unidad del BoJ
TOLERANCIA_FRED_WALCL = 0.5  # FRED publica en millones enteros
# Dos fijaciones distintas del mismo tipo de cambio. El 0.5 % se fijó en el
# paso 0 con el euro a la vista (máximo observado: 0.31 %) y se extendió al yen
# y al yuan antes de compararlos.
TOLERANCIA_CAMBIO_PCT = 0.5
# La comparación de los tipos de cambio es un control (FUENTES.md, D0.11): el
# mes que pasa del umbral se publica marcado como valor en disputa.
# Cuántas comparaciones hacen falta, como mínimo, para que un gate cuente.
MINIMO_COMPARACIONES_GATE = 3
MESES_GATE_BDE = 3  # el Banco de España no recarga las revisiones viejas (FUENTES.md, D0.4)


@dataclass(frozen=True)
class AnclaMensual:
    """Un valor de un mes leído a mano de una segunda fuente, con su cita."""

    serie: str
    mes: str
    valor: float  # en la unidad de la serie
    tolerancia: float  # medio paso del redondeo de la serie, en su unidad
    fuente: str
    fuente_url: str
    fecha_lectura: date


# A-D0-9: el contraste del dinero amplio de China no puede ser una descarga del
# PBoC. Son valores leídos en pantalla de la Oficina Nacional de Estadísticas
# de China, que republica al PBoC en cien millones de yuanes; aquí van en
# millones. La OCDE publica redondeado a cien millones: medio paso son 50.
_NBS = "Oficina Nacional de Estadísticas de China, 国家数据, 货币和准货币 (M2) 供应量_期末值"
_NBS_URL = "https://data.stats.gov.cn/dg/website/page.html#/pc/national/monthData"
ANCLAS_CHINA = (
    AnclaMensual("dinero_amplio_china", "2026-07", 355_507_724.0, 50.0, _NBS, _NBS_URL, date(2026, 10, 5)),
    AnclaMensual("dinero_amplio_china", "2020-03", 208_092_341.0, 50.0, _NBS, _NBS_URL, date(2026, 10, 5)),
)
# El balance del PBoC no tiene todavía una lectura a mano que no venga de una
# descarga automática de su sitio. Mientras esta lista esté vacía, la serie se
# calcula y se publica como NO MEDIDO: sin validación externa.
ANCLAS_BALANCE_PBOC: tuple[AnclaMensual, ...] = ()
# Cuántas anclas hacen falta para que el gate decida: las mismas que el gate
# anual de oro y plata (MINIMO_ANIOS_GATE). La primera versión decía 2, fijado
# después de ver que China tenía dos lecturas; se corrigió el 2026-10-06
# (A-D0-25, changelog). Con dos anclas, el dinero amplio de China queda NO
# MEDIDO hasta que alguien lea una tercera en pantalla.
MINIMO_ANCLAS = MINIMO_ANIOS_GATE

# --- Agregado (A-D0-10, A-D0-11, A-D0-12) ------------------------------------

# Las economías que entran al agregado en USD: nombre, serie de dinero y tipo
# de cambio. A-D0-9: China queda fuera mientras no se demuestre que su
# definición es comparable.
ECONOMIAS_AGREGADO = (
    ("eeuu", "m2_eeuu_sin_ajustar", None),
    ("eurozona", "m2_eurozona_sin_ajustar", "usd_por_eur"),
    ("japon", "m2_japon", "jpy_por_usd"),
)
# A-D0-36: Japón entra al agregado por tramos, sin empalme: M2+CDs (con bancos
# extranjeros) hasta 2003-03 y el M2 actual desde 2003-04. El salto de 2003-04
# se declara en la columna quiebre, no se corrige. Con eso el agregado empieza
# donde empieza el tipo de cambio del euro (1999-01); no se construye ningún
# euro sintético anterior.
TRAMOS_AGREGADO = {"japon": ((CLAVE_M2CD_1998_2008, "2003-03"), ("m2_japon", None))}
NOMBRE_AGREGADO = (
    "Dinero amplio de tres economías en USD: M2 de EE.UU. y de la Eurozona, y de Japón M2+CDs hasta "
    "2003-03 y M2 desde 2003-04"
)

# --- Salidas -----------------------------------------------------------------

EPSILON_REVISION_D0 = 0.0005
# Doce cifras significativas: los saldos del BCE traen millones con decimales
# largos, y con menos cifras la relectura del CSV inventaría revisiones.
FORMATO_D0 = "%.12g"

ARCHIVO_D0_DINERO = DIR_SERIES / "denominador_dinero.csv"
ARCHIVO_D0_BALANCES = DIR_SERIES / "denominador_balances.csv"
ARCHIVO_D0_CAMBIO = DIR_SERIES / "denominador_tipos_de_cambio.csv"
ARCHIVO_D0_AGREGADO = DIR_SERIES / "denominador_agregado.csv"
ARCHIVO_D0_FICHAS = DIR_SERIES / "serie_D0.csv"
ARCHIVO_D0_DESCARGAS = DIR_SERIES / "denominador_descargas.csv"
ARCHIVO_D0_RATIOS = DIR_SERIES / "denominador_ratios.csv"
ARCHIVO_D0_PARES = DIR_SERIES / "denominador_pares.csv"

COLUMNAS_D0_DINERO = ["mes", "serie", "valor", "estado", "quiebre"]
COLUMNAS_D0_BALANCES = ["mes", "serie", "valor", "fecha_origen", "estado", "quiebre"]
COLUMNAS_D0_CAMBIO = ["mes", "par", "promedio_mensual", "fin_de_mes", "fecha_fin_de_mes", "contraste"]
COLUMNAS_D0_AGREGADO = [
    "mes",
    "m2_eeuu_usd",
    "m2_eurozona_usd",
    "m2_japon_usd",
    "serie_japon",
    "agregado_usd",
    "agregado_usd_tc_constante",
    "quiebre",
    "estado",
]
COLUMNAS_D0_FICHAS = [
    "serie",
    "nombre",
    "familia",
    "publicada",
    "estado",
    "unidad",
    "convencion",
    "frecuencia_nativa",
    "ajuste_estacional",
    "emisor",
    "fuente",
    "identificador",
    "url",
    "licencia",
    "atribucion",
    "validacion",
    "supuestos",
    "quiebres",
    "primer_mes",
    "ultimo_mes",
    "meses",
]

# --- Oro / M2 y BTC / M2 (A-D0-21) --------------------------------------------

# El M2 entra al ratio en billones (10^12) de USD: el archivo lo trae en miles
# de millones, con un decimal.
M2_EEUU_A_BILLONES = 1000.0
M2_EEUU_MEDIO_PASO = 0.05 / M2_EEUU_A_BILLONES
PARES_D0 = (
    Par("oro_m2_eeuu", "Oro / M2 de EE.UU.", "oro", "m2_eeuu"),
    Par("btc_m2_eeuu", "BTC / M2 de EE.UU.", "btc", "m2_eeuu"),
)


@dataclass(frozen=True)
class SeriePendiente:
    """Algo que el sitio muestra o mostraría y que no tiene serie: va a la ficha como NO MEDIDO."""

    clave: str
    nombre: str
    familia: str
    estado: str
    fuente: str
    supuestos: tuple[str, ...]


SERIES_PENDIENTES = (
    SeriePendiente(
        "dinero_eeuu_1892_1946",
        "Efectivo y depósitos en bancos comerciales de EE.UU., fechas de balance (1892–1946)",
        FAMILIA_DINERO,
        "NO MEDIDO: transcripción de las tablas de la Junta pendiente; se hace en un PR propio (A-D0-17, A-D0-19)",
        "Junta de la Reserva Federal, Banking and Monetary Statistics 1914–1941 (Tabla 9) y 1941–1970",
        ("A-D0-17", "A-D0-18", "A-D0-19"),
    ),
    SeriePendiente(
        "dinero_eeuu_1947_1958",
        "Efectivo y depósitos en bancos comerciales de EE.UU., mensual (1947–1958)",
        FAMILIA_DINERO,
        "NO MEDIDO: transcripción de la Tabla 1.1 de la Junta pendiente; se hace en un PR propio (A-D0-17, A-D0-19)",
        "Junta de la Reserva Federal, Banking and Monetary Statistics 1941–1970 (Tabla 1.1)",
        ("A-D0-17", "A-D0-19"),
    ),
    SeriePendiente(
        "riqueza_inmuebles",
        "Riqueza: valor de los inmuebles",
        "riqueza",
        "NO MEDIDO: no hay una serie global con licencia abierta; la estimación de Savills va como cifra citada (A-D0-24, A-D0-28)",
        "",
        ("A-D0-24", "A-D0-28"),
    ),
    SeriePendiente(
        "riqueza_oro_cantidad",
        "Riqueza: oro sobre la superficie (cantidad)",
        "riqueza",
        "NO MEDIDO: la única serie de existencias es del World Gold Council, clase (c); su cifra va como cifra citada (A-D0-24, A-D0-28)",
        "",
        ("A-D0-24", "A-D0-28"),
    ),
    SeriePendiente(
        "riqueza_total",
        "Riqueza total",
        "riqueza",
        "NO MEDIDO: los informes de riqueza global son (c) o no se pudieron leer (A-D0-24)",
        "",
        ("A-D0-24",),
    ),
    SeriePendiente(
        "riqueza_bonos",
        "Riqueza: títulos de deuda en circulación",
        "riqueza",
        "NO MEDIDO: pendiente de implementar la suma de las economías que declaran al BIS (A-D0-22)",
        "BIS, Debt securities statistics (WS_NA_SEC_DSS)",
        ("A-D0-22",),
    ),
    SeriePendiente(
        "riqueza_acciones",
        "Riqueza: capitalización bursátil",
        "riqueza",
        "NO MEDIDO: pendiente de implementar la lectura del agregado WLD del Banco Mundial (A-D0-23)",
        "Banco Mundial, indicador CM.MKT.LCAP.CD, agregado WLD",
        ("A-D0-23",),
    ),
    SeriePendiente(
        "riqueza_btc",
        "Riqueza: capitalización de BTC",
        "riqueza",
        "NO MEDIDO: pendiente de implementar la lectura de CapMrktCurUSD de Coin Metrics (A-R0-4)",
        "Coin Metrics, API community, CapMrktCurUSD",
        ("A-R0-4",),
    ),
)


# ---------------------------------------------------------------------------
# Fase D0, tramo histórico: el dinero de EE.UU. antes de 1959, transcrito de
# las publicaciones de la Junta (A-D0-17, A-D0-18, A-D0-19, A-D0-31 a A-D0-33).
#
# Lo que se leyó de cada fuente está en FUENTES.md, D0.3 y D0.3.6. Nada de esto
# se descarga como serie: son cifras leídas dos veces de un escaneo y
# comparadas; el pipeline exige que las dos lecturas coincidan antes de usarlas.
# ---------------------------------------------------------------------------

DIR_TRANSCRIPCION_JUNTA = DIR_CRUDO / "transcripcion_junta_1892_1958"
ARCHIVO_DINERO_HISTORICO = DIR_SERIES / "dinero_eeuu_historico.csv"
ARCHIVO_DINERO_HISTORICO_DESCARGAS = DIR_SERIES / "dinero_historico_descargas.csv"

COLUMNAS_DINERO_HISTORICO = [
    "mes",
    "fecha",
    "serie",
    "componente",
    "valor",
    "unidad",
    "estado",
    "control",
    "cita",
    "nota",
]

CLAVE_DINERO_1892_1946 = "dinero_eeuu_1892_1946"
CLAVE_DINERO_1947_1958 = "dinero_eeuu_1947_1958"
CLAVE_DINERO_1947_1958_SIN_AJUSTAR = "dinero_eeuu_1947_1958_sin_ajustar"
CLAVES_DINERO_HISTORICO = (
    CLAVE_DINERO_1892_1946,
    CLAVE_DINERO_1947_1958,
    CLAVE_DINERO_1947_1958_SIN_AJUSTAR,
)

# A-D0-18: lo declara la propia Junta en la Tabla 9.
ESTADO_FECHA_DE_BALANCE = "dato de fecha de balance, estimado en parte"

CITA_BMS_1914_1941 = (
    "Junta de Gobernadores del Sistema de la Reserva Federal, Banking and Monetary "
    "Statistics, 1914-1941 (1943), Tabla 9, p. {pagina}"
)
CITA_BMS_1941_1970_CONTINUACION = (
    "Junta de Gobernadores del Sistema de la Reserva Federal, Banking and Monetary "
    "Statistics, 1941-1970 (1976), Sección 1, p. 5 (continuación de la Tabla 9 para 1941-46)"
)
CITA_BMS_1941_1970_TABLA_1_1 = (
    "Junta de Gobernadores del Sistema de la Reserva Federal, Banking and Monetary "
    "Statistics, 1941-1970 (1976), Tabla 1.1 {parte}, p. {pagina}"
)
# Página del libro y del PDF de FRASER de cada tabla transcrita.
PAGINAS_TRANSCRIPCION = {
    "tabla_9": {"libro": "34-35", "pdf": "43-44"},
    "continuacion_tabla_9": {"libro": "5", "pdf": "12"},
    "tabla_1_1_A": {"libro": "17", "pdf": "24"},
    "tabla_1_1_B": {"libro": "20", "pdf": "27"},
}

# Los dos volúmenes escaneados. Son copias bajadas a mano (A-D0-29: la
# transcripción no las necesita para correr; si están en disco, su hash queda en
# el manifiesto). No se versionan: 36 y 75 MB (A-D0-27). La licencia es una
# inferencia: obra de una agencia federal sin aviso de copyright (FUENTES.md,
# D0.3.1); FRASER pide atribución por la copia.
_LICENCIA_JUNTA_INFERIDA = (
    "Dominio público (publicación de la Junta sin aviso de copyright; inferencia, FUENTES.md D0.3.1)"
)
_ATRIBUCION_BMS = (
    "Board of Governors of the Federal Reserve System, {titulo}. Copia digital: FRASER, Federal "
    "Reserve Bank of St. Louis, {url}. Cifras transcritas a mano; se publican sin cambios."
)
DESCARGA_BMS_1914_1941 = Descarga(
    clave="junta_bms_1914_1941",
    descripcion="Junta de la Reserva Federal, Banking and Monetary Statistics, 1914-1941 (PDF de FRASER)",
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_JUNTA_INFERIDA,
    url="https://fraser.stlouisfed.org/files/docs/publications/bms/1914-1941/BMS14-41_complete.pdf",
    extension="pdf",
    atribucion=_ATRIBUCION_BMS.format(
        titulo="Banking and Monetary Statistics, 1914-1941 (1943)",
        url="https://fraser.stlouisfed.org/title/banking-monetary-statistics-1914-1941-38",
    ),
    versionar=False,
    manual=True,
)
DESCARGA_BMS_1941_1970 = Descarga(
    clave="junta_bms_1941_1970",
    descripcion="Junta de la Reserva Federal, Banking and Monetary Statistics, 1941-1970 (PDF de FRASER)",
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_JUNTA_INFERIDA,
    url="https://fraser.stlouisfed.org/files/docs/publications/bms/1941-1970/BMS41-70_complete.pdf",
    extension="pdf",
    atribucion=_ATRIBUCION_BMS.format(
        titulo="Banking and Monetary Statistics, 1941-1970 (1976)",
        url="https://fraser.stlouisfed.org/title/banking-monetary-statistics-1941-1970-41",
    ),
    versionar=False,
    manual=True,
)
# La segunda publicación de las fechas de balance: la Oficina del Censo
# reimprime la Tabla 9 (y su continuación, tomada del Federal Reserve Bulletin
# de enero de 1949) como series X 266-274. Copia bajada a mano; 4 MB.
DESCARGA_HSUS_1960 = Descarga(
    clave="censo_hsus_1960_cap_x",
    descripcion=(
        "Oficina del Censo de EE.UU., Historical Statistics of the United States, Colonial "
        "Times to 1957 (1960), capítulo X, series X 266-274 (PDF)"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia="Dominio público (publicación de la Oficina del Censo de EE.UU.)",
    url="https://www2.census.gov/library/publications/1960/compendia/hist_stats_colonial-1957/hist_stats_colonial-1957-chX.pdf",
    extension="pdf",
    atribucion=(
        "U.S. Bureau of the Census, Historical Statistics of the United States, Colonial Times "
        "to 1957 (1960), series X 266-274, p. 646. Cifras leídas a mano como anclas."
    ),
    versionar=False,
    manual=True,
)
# La segunda fuente del tramo mensual: la serie m14144c del NBER (Friedman y
# Schwartz), republicada por FRED. Se lee y se compara; no se versiona
# (sin licencia declarada, FUENTES.md D0.3.3) y su crudo queda en data/privado.
# data.nber.org veda a todo programa en su robots.txt: no se pide ahí.
FRED_SERIE_NBER_M14144C = "M1444CUSM027SNBR"
DESCARGA_FRED_NBER_M14144C = Descarga(
    clave="fred_nber_m14144c",
    descripcion=(
        "FRED, serie M1444CUSM027SNBR: NBER Macrohistory m14144c, depósitos a la vista y a "
        "plazo ajustados en bancos comerciales más efectivo, ajustada por estacionalidad, "
        "promedio mensual de cifras diarias, 1947-1969"
    ),
    clase_licencia=CLASE_SIN_DECLARAR,
    licencia="Sin licencia declarada por el NBER; FRED la marca con cita obligatoria. Solo contraste.",
    url=URL_CSV.format(id=FRED_SERIE_NBER_M14144C),
    extension="csv",
    atribucion=(
        "National Bureau of Economic Research, Macrohistory Database, serie m14144c, vía FRED. No se publica."
    ),
    versionar=False,
)
DESCARGAS_DINERO_HISTORICO = (
    DESCARGA_BMS_1914_1941,
    DESCARGA_BMS_1941_1970,
    DESCARGA_HSUS_1960,
    DESCARGA_FRED_NBER_M14144C,
)

# --- Tolerancias (A-D0-32), fijadas antes de comparar ------------------------
#
# La Tabla 9 y su continuación imprimen millones enteros y sus totales son
# sumas exactas de sus componentes: la tolerancia de las identidades es cero.
# La Tabla 1.1 imprime un decimal en miles de millones: dos componentes
# redondeados pueden apartarse del total impreso hasta 0.1 (dos medios pasos),
# y más que eso es un error de transcripción o una errata de la fuente.
TOLERANCIA_SUMA_MILLONES = 0.0
TOLERANCIA_SUMA_MILES_DE_MILLONES = 0.1
# Las anclas del Censo son la misma cifra, en los mismos millones: igualdad.
TOLERANCIA_ANCLAS_HSUS = 0.0
# El NBER declara diferencias de una décima contra el Federal Reserve Bulletin
# por el redondeo de sus componentes (FUENTES.md, D0.3.3). Es la tolerancia del
# gate del tramo mensual, y se fijó antes de comparar. Se sabe también, antes de
# comparar, que la serie del NBER es anterior a la revisión de 1976 que trae la
# Tabla 1.1: una diferencia mayor puede ser una revisión de la Junta y no un
# error de transcripción; si el gate no cierra, la serie queda NO MEDIDO y la
# causa se investiga, no se cambia la tolerancia.
TOLERANCIA_NBER_MILES_DE_MILLONES = 0.1
# Un gate necesita al menos tres comparaciones (A-D0-25).
MINIMO_COMPARACIONES_DINERO_HISTORICO = MINIMO_COMPARACIONES_GATE


@dataclass(frozen=True)
class AnclaFechaDeBalance:
    """Una fila de una segunda publicación, leída a mano, con su cita.

    Los valores van por componente de la Tabla 9, en millones de USD. Las
    columnas X 266 y X 274 del Censo no se usan: X 266 excluye los depósitos
    del gobierno y X 274 incluye depósitos en los bancos de la Reserva, de modo
    que ninguna de las dos es una columna de la Tabla 9.
    """

    fecha: str  # la fecha de balance de la Tabla 9 a la que corresponde la fila
    valores: dict[str, float]  # componente -> millones de USD
    fuente: str
    fuente_url: str
    fecha_lectura: date


_HSUS_1960 = (
    "Oficina del Censo, Historical Statistics of the United States, Colonial Times to 1957 "
    "(1960), series X 266-274, Deposits adjusted and currency outside banks: 1892 to 1957, "
    "p. 646, fila {anio}; fuente declarada por el Censo: Banking and Monetary Statistics "
    "pp. 34-35 para 1892-1941 y Federal Reserve Bulletin de enero de 1949 para 1942-1947"
)
_HSUS_LEIDO = date(2026, 10, 7)


def _ancla_hsus(fecha, vista_y_efectivo, vista, efectivo, plazo_total, plazo_comerciales, plazo_cajas, plazo_postal):
    valores = {
        "total_vista_y_efectivo": vista_y_efectivo,
        "vista_ajustados": vista,
        "efectivo": efectivo,
        "plazo_total": plazo_total,
        "plazo_comerciales": plazo_comerciales,
        "plazo_cajas": plazo_cajas,
    }
    if plazo_postal is not None:
        valores["plazo_postal"] = plazo_postal
    return AnclaFechaDeBalance(
        fecha=fecha,
        valores=valores,
        fuente=_HSUS_1960.format(anio=fecha[:4]),
        fuente_url=DESCARGA_HSUS_1960.url,
        fecha_lectura=_HSUS_LEIDO,
    )


# Nueve filas de junio leídas a mano en el escaneo del Censo, ampliado a 600 ppp.
# En esa tipografía el 3 y el 8 se confunden: cada fila se comprobó con las
# identidades del propio Censo (X 267 = X 268 + X 269; X 266 = X 267 + X 270;
# X 270 = X 271 + X 272 + X 273) antes de anotarla, sin mirar la Tabla 9.
# Las dos últimas corresponden a la continuación (fuente del Censo: Bulletin de
# enero de 1949), y entran al mismo gate con la misma tolerancia.
ANCLAS_HSUS_1960 = (
    _ancla_hsus("1892-06-30", 3895, 2880, 1015, 1929, 470, 1459, None),
    _ancla_hsus("1900-06-30", 5751, 4420, 1331, 3015, 881, 2134, None),
    _ancla_hsus("1914-06-30", 11615, 10082, 1533, 8350, 4441, 3866, 43),
    _ancla_hsus("1920-06-30", 23721, 19616, 4105, 15834, 10509, 5168, 157),
    _ancla_hsus("1929-06-29", 26179, 22540, 3639, 28611, 19557, 8905, 149),
    _ancla_hsus("1933-06-30", 19172, 14411, 4761, 21656, 10849, 9621, 1186),
    _ancla_hsus("1941-06-30", 45521, 37317, 8204, 27879, 15928, 10648, 1303),
    _ancla_hsus("1942-06-30", 52806, 41870, 10936, 27320, 15610, 10395, 1315),
    _ancla_hsus("1946-06-29", 105992, 79476, 26516, 51829, 32429, 16281, 3119),
)

# --- Las series (A-D0-17, A-D0-31) --------------------------------------------

_SUP_HISTORICO = ("A-D0-17", "A-D0-18", "A-D0-19", "A-D0-31", "A-D0-32", "A-D0-33")
_SUP_MENSUAL = ("A-D0-17", "A-D0-19", "A-D0-31", "A-D0-32", "A-D0-33")

SERIE_DINERO_1892_1946 = SerieD0(
    clave=CLAVE_DINERO_1892_1946,
    nombre="Efectivo y depósitos en bancos comerciales de EE.UU., fechas de balance (1892-1946)",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BMS_1914_1941,
    identificador=(
        "Tabla 9 (1892-1941) y su continuación (1941-46): efectivo fuera de bancos + depósitos a la "
        "vista ajustados + depósitos a plazo en bancos comerciales"
    ),
    emisor=_EMISOR_JUNTA,
    unidad="millones de USD",
    convencion=(
        "saldo del día de balance (call date); anual, 30 de junio, hasta 1922; semestral, junio y "
        "diciembre, desde 1923"
    ),
    frecuencia_nativa="fechas de balance",
    ajuste="sin ajustar",
    estado=ESTADO_FECHA_DE_BALANCE,
    supuestos=_SUP_HISTORICO,
    banda_plausible=(1_000.0, 1_000_000.0),
    quiebres=(
        Quiebre("1923-06", "la frecuencia pasa de anual (junio) a semestral (junio y diciembre)"),
        Quiebre(
            "1941-06",
            "tres cajas de ahorro mutuas pasan a ser miembros del Sistema de la Reserva y salen de los "
            "bancos comerciales (nota 5 de la Tabla 9)",
        ),
        Quiebre("1942-06", "cambia la publicación: de la Tabla 9 (1943) a su continuación en el volumen de 1976"),
    ),
)
SERIE_DINERO_1947_1958 = SerieD0(
    clave=CLAVE_DINERO_1947_1958,
    nombre="Efectivo y depósitos en bancos comerciales de EE.UU., mensual, ajustada por estacionalidad (1947-1958)",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BMS_1941_1970,
    identificador=(
        "Tabla 1.1 A: money stock (efectivo + depósitos a la vista ajustados) + depósitos a plazo "
        "ajustados en bancos comerciales"
    ),
    emisor=_EMISOR_JUNTA,
    unidad="miles de millones de USD",
    convencion="promedio mensual de cifras diarias",
    frecuencia_nativa="mensual",
    ajuste="ajustada por estacionalidad",
    estado=ESTADO_DATO,
    supuestos=_SUP_MENSUAL,
    banda_plausible=(100.0, 1_000.0),
)
SERIE_DINERO_1947_1958_SIN_AJUSTAR = SerieD0(
    clave=CLAVE_DINERO_1947_1958_SIN_AJUSTAR,
    nombre="Efectivo y depósitos en bancos comerciales de EE.UU., mensual, sin ajustar (1947-1958)",
    familia=FAMILIA_DINERO,
    descarga=DESCARGA_BMS_1941_1970,
    identificador=(
        "Tabla 1.1 B: money stock (efectivo + depósitos a la vista ajustados) + depósitos a plazo "
        "ajustados en bancos comerciales"
    ),
    emisor=_EMISOR_JUNTA,
    unidad="miles de millones de USD",
    convencion="promedio mensual de cifras diarias",
    frecuencia_nativa="mensual",
    ajuste="sin ajustar",
    estado=ESTADO_DATO,
    supuestos=_SUP_MENSUAL,
    banda_plausible=(100.0, 1_000.0),
)
SERIES_DINERO_HISTORICO = (SERIE_DINERO_1892_1946, SERIE_DINERO_1947_1958, SERIE_DINERO_1947_1958_SIN_AJUSTAR)

# A-D0-31: la serie sin ajustar no tiene segunda fuente accesible a un
# programa (m14144b no está en FRED y data.nber.org veda a los programas), así
# que se transcribe, se controla con sus sumas y se publica como NO MEDIDO.
NO_MEDIDO_SIN_AJUSTAR_1947_1958 = (
    "NO MEDIDO: sin validación externa; la segunda fuente (NBER m14144b, 1955-1969) no está en FRED "
    "y data.nber.org veda a los programas (A-D0-31)"
)


# ---------------------------------------------------------------------------
# Fase R, contexto histórico: el precio oficial del oro en EE.UU. antes de 1960
# (A-R0-21 a A-R0-26). Fijado por ley, no observado en un mercado: es una serie
# de contexto, fuera de las métricas, sin empalme con el Pink Sheet.
#
# Lo leído de cada norma, con página, está en FUENTES.md, sección 4.8.
# ---------------------------------------------------------------------------

ARCHIVO_ORO_OFICIAL = DIR_SERIES / "oro_precio_oficial.csv"
CLAVE_ORO_OFICIAL = "oro_precio_oficial_usd"
ETIQUETA_ORO_OFICIAL = "precio oficial fijado por ley, no precio de mercado"
COLUMNAS_ORO_OFICIAL = [
    "mes",
    "oro_oficial_usd_oz",
    "etiqueta",
    "norma",
    "vigente_desde",
    "convertibilidad",
    "estado",
    "apto_metricas",
    "cita",
    "nota",
]
GRANOS_POR_ONZA_TROY = 480
# A-R0-23: cuatro decimales, como los publica la Casa de Moneda.
DECIMALES_ORO_OFICIAL = 4


@dataclass(frozen=True)
class TramoOroOficial:
    """Un tramo del precio oficial: la norma que fija el peso del dólar en oro.

    El precio por onza troy se deriva en el código, con fracciones exactas:
    480 granos por onza ÷ (granos del dólar × ley de fino). No se teclea.
    """

    desde: str  # primer mes publicado con este precio, "AAAA-MM" (A-R0-22)
    hasta: str  # último mes publicado con este precio
    granos: Fraction  # granos de oro estándar por dólar
    fino: Fraction  # ley de fino del oro estándar
    norma: str
    vigente_desde: str  # fecha y hora de vigencia de la norma, literal
    cita: str
    fuente_url: str

    @property
    def precio(self) -> Fraction:
        return Fraction(GRANOS_POR_ONZA_TROY) / (self.granos * self.fino)


_FRASER_TESORO_1900 = "https://fraser.stlouisfed.org/files/docs/publications/treasar/AR_TREASURY_1900.pdf"
_FRASER_BOLETIN_1934_02 = "https://fraser.stlouisfed.org/files/docs/publications/FRB/1930s/frb_021934.pdf"

# A-R0-24: la serie empieza con la ley de 1900 porque es la primera norma que
# se pudo leer; la paridad venía de antes (sección 3511 de los Revised
# Statutes), y ese tramo anterior queda NO MEDIDO hasta leer esas leyes.
TRAMOS_ORO_OFICIAL = (
    TramoOroOficial(
        desde="1900-03",
        hasta="1934-01",
        granos=Fraction(129, 5),  # 25.8 granos
        fino=Fraction(9, 10),
        norma="Gold Standard Act, ley del 14 de marzo de 1900, sección 1 (dólar de 25,8 granos de oro de 9/10 de fino)",
        vigente_desde="1900-03-14",
        cita=(
            "Annual Report of the Secretary of the Treasury, 1900, informe del Director de la Casa de Moneda, "
            "'The gold-standard law', p. 345; texto literal de la sección 1"
        ),
        fuente_url=_FRASER_TESORO_1900,
    ),
    TramoOroOficial(
        desde="1934-02",
        hasta="1959-12",
        granos=Fraction(320, 21),  # 15 5/21 granos
        fino=Fraction(9, 10),
        norma=(
            "Proclamación presidencial del 31 de enero de 1934 (sección 43(b)(2) del Título III de la ley del "
            "12 de mayo de 1933, reformada por la sección 12 de la Gold Reserve Act del 30 de enero de 1934): "
            "dólar de 15 5/21 granos de oro de 9/10 de fino"
        ),
        vigente_desde="1934-01-31 15:10, hora del Este",
        cita="Federal Reserve Bulletin, febrero de 1934, pp. 68-69; la fracción se comprobó en la imagen",
        fuente_url=_FRASER_BOLETIN_1934_02,
    ),
)

# A-R0-22: enero de 1934 lleva el precio viejo. Es la convención publicada por
# la Junta: "calculated at the rate of $20.67 per fine ounce of gold through
# January 1934 and $35 per fine ounce thereafter" (BMS 1914-1941, p. 522).
CONVENCION_MES_DE_CAMBIO = (
    "el mes en que cambia la norma lleva el precio vigente al cierre del mes anterior, como la Junta: "
    "'$20.67 ... through January 1934 and $35 ... thereafter' (Banking and Monetary Statistics 1914-1941, p. 522)"
)

# A-R0-26: la paridad legal siguió en 20,67 mientras no hubo convertibilidad, y
# el precio administrado del oro recién extraído de 1933-34 es otra cosa.
CONVERTIBILIDAD_ORO_OFICIAL = (
    ("1900-03", "1933-02", "sí"),
    (
        "1933-03",
        "1934-01",
        "no: paridad legal sin convertibilidad desde el 6 de marzo de 1933 (feriado bancario); exportación con "
        "licencia desde el 10 de marzo; tenencia privada prohibida desde el 5 de abril",
    ),
    (
        "1934-02",
        "1959-12",
        "solo bancos centrales extranjeros y usos licenciados: el Tesoro compra a 35 menos 1/4 % y vende a 35 más "
        "1/4 % (Federal Reserve Bulletin, febrero de 1934, pp. 67-69)",
    ),
)
NOTA_PRECIO_ADMINISTRADO = (
    "del 8 de septiembre de 1933 al 31 de enero de 1934 rigió además un precio administrado, diario, para el oro "
    "recién extraído (29,00 a 34,45 USD por onza; Annual Report of the Secretary of the Treasury 1934, anexo 26, "
    "p. 205): no es el precio oficial y no está en esta serie"
)
MESES_PRECIO_ADMINISTRADO = ("1933-09", "1934-01")


@dataclass(frozen=True)
class AnclaOroOficial:
    """Una cifra publicada por otra institución, leída a mano, contra la que cierra el precio derivado."""

    mes: str  # un mes del tramo que confirma
    valor: float  # USD por onza troy de oro fino, como lo imprime la fuente
    fuente: str
    fuente_url: str
    fecha_lectura: date


# A-R0-25: tolerancia ±0.005 USD (medio centavo), declarada el 2026-10-07 antes
# de comparar; las cifras publicadas con dos decimales caben en ella y las de
# cuatro, también. El gate también exige que el primer mes a 35 sea 1934-02.
TOLERANCIA_ORO_OFICIAL = 0.005
PRIMER_MES_A_35 = "1934-02"
_LEIDO_ORO = date(2026, 10, 7)
ANCLAS_ORO_OFICIAL = (
    AnclaOroOficial(
        "1933-06",
        20.67,
        "Tesoro de EE.UU., Annual Report of the Secretary of the Treasury 1934, p. 120: compras de las casas de moneda "
        "'at $20.67+ per fine ounce' en el ejercicio 1934",
        "https://fraser.stlouisfed.org/title/annual-report-secretary-treasury-state-finances-194/annual-report-secretary-treasury-state-finances-fiscal-year-ended-june-30-1934-5587",
        _LEIDO_ORO,
    ),
    AnclaOroOficial(
        "1934-06",
        35.0,
        "Tesoro de EE.UU., Annual Report of the Secretary of the Treasury 1934, p. 120: compras 'at $35 per fine ounce'",
        "https://fraser.stlouisfed.org/title/annual-report-secretary-treasury-state-finances-194/annual-report-secretary-treasury-state-finances-fiscal-year-ended-june-30-1934-5587",
        _LEIDO_ORO,
    ),
    AnclaOroOficial(
        "1931-06",
        20.6718,
        "Casa de Moneda de EE.UU., Annual Report of the Director of the Mint, ejercicio 1935, p. 91: precio por onza fina "
        "a la paridad antigua, '$20.6718'",
        "https://fraser.stlouisfed.org/title/annual-report-director-mint-182/annual-report-director-mint-fiscal-year-ended-june-30-1935-5760",
        _LEIDO_ORO,
    ),
    AnclaOroOficial(
        "1935-06",
        35.0,
        "Casa de Moneda de EE.UU., Annual Report of the Director of the Mint, ejercicio 1935, p. 91: paridad nueva, '$35.0000'",
        "https://fraser.stlouisfed.org/title/annual-report-director-mint-182/annual-report-director-mint-fiscal-year-ended-june-30-1935-5760",
        _LEIDO_ORO,
    ),
    AnclaOroOficial(
        "1934-01",
        20.67,
        "Junta de la Reserva Federal, Banking and Monetary Statistics 1914-1941, p. 522: '$20.67 per fine ounce of gold "
        "through January 1934 and $35 per fine ounce thereafter'",
        "https://fraser.stlouisfed.org/title/banking-monetary-statistics-1914-1941-38",
        _LEIDO_ORO,
    ),
    AnclaOroOficial(
        "1946-12",
        35.0,
        "FMI, paridad declarada por EE.UU. el 18 de diciembre de 1946: 0,888671 gramos de oro fino por dólar, '35.0000' "
        "(Federal Reserve Bulletin, enero de 1947, p. 12)",
        "https://fraser.stlouisfed.org/files/docs/publications/FRB/1940s/frb_011947.pdf",
        _LEIDO_ORO,
    ),
)
MINIMO_ANCLAS_ORO_OFICIAL = MINIMO_ANIOS_GATE

# El quiebre con el Pink Sheet: a la izquierda un precio fijado por ley; a la
# derecha, desde 1960-01, el promedio mensual del fixing de Londres (A-R0-7).
QUIEBRE_ORO_OFICIAL = (
    "1960-01: termina esta serie y empieza el oro del Pink Sheet (promedio mensual del fixing de Londres, "
    "A-R0-7); son dos series distintas y no se empalman"
)
NO_MEDIDO_ORO_ANTES_DE_1900 = (
    "antes de 1900-03: NO MEDIDO hasta verificar la base legal (sección 3511 de los Revised Statutes y las leyes "
    "de 1834, 1837 y 1873, no leídas: loc.gov exige una verificación humana)"
)


# ---------------------------------------------------------------------------
# Fase N0: El Numerador. La oferta de los activos, su tasa de crecimiento y su
# elasticidad. Lo que se leyó de cada fuente está en FUENTES.md, sección N0;
# las decisiones, en SUPUESTOS.md, A-N0-1 en adelante.
# ---------------------------------------------------------------------------

FAMILIA_BTC = "btc"
FAMILIA_METALES = "metales"
FAMILIA_ACCIONES = "acciones"
FAMILIA_DEUDA = "deuda"
FAMILIA_VIVIENDAS = "viviendas"
FAMILIA_ELASTICIDAD = "elasticidad"

# A-N0-1: cada serie dice qué mide. Una tasa de crecimiento y una elasticidad
# son magnitudes distintas y el sitio no usa una por la otra.
MIDE_FLUJO = "flujo"
MIDE_STOCK = "stock"
MIDE_TASA = "tasa de crecimiento de la oferta"
MIDE_COTA = "cota superior de la tasa de crecimiento del stock"
MIDE_PROPORCION = "proporción"
MIDE_ELASTICIDAD = "elasticidad de la oferta"

ESTADO_NO_MEDIDO = "NO MEDIDO"

_LICENCIA_USGS = "Dominio público (USGS)"
_ATRIBUCION_USGS = (
    "U.S. Geological Survey, {publicacion}. Dominio público: \"USGS-authored or produced data and "
    "information are considered to be in the U.S. Public Domain.\""
)
_LICENCIA_CENSO = "Dominio público (obra del gobierno federal de EE.UU., 17 U.S.C. § 105)"
_ATRIBUCION_CENSO = (
    "U.S. Census Bureau, {producto}. Obra del gobierno federal de EE.UU., sin copyright "
    "(17 U.S.C. § 105). Los valores se publican sin cambios; las tasas son cálculo propio."
)
_LICENCIA_COIN_METRICS = "CC BY-NC 4.0"
_ATRIBUCION_COIN_METRICS_OFERTA = (
    "Coin Metrics, Community Network Data: SplyCur, BlkCnt e IssTotNtv de BTC, CC BY-NC 4.0 "
    "(https://creativecommons.org/licenses/by-nc/4.0/). Los valores diarios se publican sin cambios; "
    "las sumas anuales, las tasas y el calendario del protocolo son cálculo propio. "
    "Válido mientras el sitio no tenga vínculo comercial (A-R0-4)."
)

# --- Descargas ---------------------------------------------------------------

DESCARGA_COIN_METRICS_OFERTA = Descarga(
    clave="coin_metrics_btc_oferta",
    descripcion=(
        "Coin Metrics, API community: oferta en circulación (SplyCur), bloques (BlkCnt) y "
        "emisión (IssTotNtv) diarios de BTC"
    ),
    clase_licencia=CLASE_NO_COMERCIAL,
    licencia=_LICENCIA_COIN_METRICS,
    url=(
        "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
        "?assets=btc&metrics=SplyCur,BlkCnt,IssTotNtv&frequency=1d&page_size=10000"
    ),
    extension="json",
    atribucion=_ATRIBUCION_COIN_METRICS_OFERTA,
)

# A-N0-14: el host que aloja los xlsx de la Data Series 140 responde HTTP 403 al
# propio robots.txt, y la regla de fuentes_denominador.interpretar_robots lee
# un 403 como veda total. Los archivos entran por copia bajada a mano, como las
# series del BCE (A-D0-29): usgs_ds140_<metal>_<AAAA-MM-DD>.xlsx en data/raw.
_URL_DS140 = (
    "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/"
    "media/files/ds140-{metal}-{anio}.xlsx"
)
DESCARGA_USGS_DS140_ORO = Descarga(
    clave="usgs_ds140_oro",
    descripcion=(
        "USGS, Data Series 140, Gold statistics (1900-2022): producción mundial anual en toneladas "
        "(copia bajada a mano)"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_USGS,
    url=_URL_DS140.format(metal="gold", anio=2022),
    extension="xlsx",
    atribucion=_ATRIBUCION_USGS.format(publicacion="Data Series 140, Historical Statistics for Mineral and Material Commodities, Gold"),
    manual=True,
)
DESCARGA_USGS_DS140_PLATA = Descarga(
    clave="usgs_ds140_plata",
    descripcion=(
        "USGS, Data Series 140, Silver statistics (1900-2021): producción mundial anual en toneladas "
        "(copia bajada a mano)"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_USGS,
    url=_URL_DS140.format(metal="silver", anio=2021),
    extension="xlsx",
    atribucion=_ATRIBUCION_USGS.format(publicacion="Data Series 140, Historical Statistics for Mineral and Material Commodities, Silver"),
    manual=True,
)

_Z1 = "Z.1 Financial Accounts of the United States"
Z1_URL_BASE = "https://www.federalreserve.gov/releases/z1/current/"
DESCARGA_Z1_ZIP = Descarga(
    clave="z1_csv_files",
    descripcion=f"Junta de la Reserva Federal, {_Z1}: paquete CSV de la publicación vigente (un CSV por tabla)",
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_JUNTA,
    url=Z1_URL_BASE + "z1_csv_files.zip",
    extension="zip",
    atribucion=_ATRIBUCION_JUNTA.format(publicacion=_Z1),
    versionar=False,  # A-D0-27: pesa 8 MB; se versionan los CSV de las tablas usadas
)
# Las tablas del paquete que alimentan series. F51.1 es la antigua F.224/L.224
# (acciones); F3, la antigua F.208/L.208 (títulos de deuda); D3, la D.3.
Z1_TABLAS = ("F51_1_t", "F51_1_s", "F3_s", "F3_t", "D3_s")


def _descarga_z1_tabla(tabla: str) -> Descarga:
    """A-N0-14: el CSV de una tabla, con los bytes exactos del miembro csv/<tabla>.csv del ZIP."""
    return Descarga(
        clave=f"z1_{tabla}",
        descripcion=(
            f"Junta de la Reserva Federal, {_Z1}, tabla {tabla.replace('_', '.')}: CSV extraído del "
            f"paquete z1_csv_files.zip (miembro csv/{tabla}.csv, bytes sin cambios)"
        ),
        clase_licencia=CLASE_ABIERTA,
        licencia=_LICENCIA_JUNTA,
        url=f"{DESCARGA_Z1_ZIP.url}#csv/{tabla}.csv",
        extension="csv",
        atribucion=_ATRIBUCION_JUNTA.format(publicacion=_Z1),
    )


DESCARGAS_Z1_TABLAS = tuple(_descarga_z1_tabla(tabla) for tabla in Z1_TABLAS)
DESCARGA_Z1_POR_TABLA = {tabla: descarga for tabla, descarga in zip(Z1_TABLAS, DESCARGAS_Z1_TABLAS)}

# A-N0-9: la misma tabla en HTML, del mismo emisor, como gate de transporte.
Z1_TABLAS_HTML = ("F51_1_t", "F51_1_s", "F3_s", "D3_s")
CONTRASTES_Z1_HTML = {
    tabla: _contraste(
        f"z1_html_{tabla}",
        f"Junta de la Reserva Federal, {_Z1}, tabla {tabla.replace('_', '.')} en HTML: gate de transporte del CSV",
        Z1_URL_BASE + f"html/{tabla}.htm",
        "htm",
    )
    for tabla in Z1_TABLAS_HTML
}

# A-N0-14: las URL del Censo llevan la vintage en el nombre y cambian cada año.
DESCARGA_CENSO_HVS_T7 = Descarga(
    clave="censo_hvs_tabla7",
    descripcion=(
        "Census Bureau, Housing Vacancies and Homeownership (CPS/HVS), Tabla 7: estimaciones del "
        "inventario total de viviendas de EE.UU., 1965 a hoy, en miles"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_CENSO,
    url="https://www.census.gov/housing/hvs/data/histtab7.xlsx",
    extension="xlsx",
    atribucion=_ATRIBUCION_CENSO.format(producto="Current Population Survey/Housing Vacancy Survey, Table 7"),
)
DESCARGA_CENSO_HVS_T7A = Descarga(
    clave="censo_hvs_tabla7a",
    descripcion=(
        "Census Bureau, Housing Vacancies and Homeownership (CPS/HVS), Tabla 7a: inventario total de "
        "viviendas de EE.UU., 2000 a hoy, revisado con los controles de vivienda de las vintages 2010, "
        "2020 y 2025"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_CENSO,
    url="https://www.census.gov/housing/hvs/data/hist_tab_7a_v2025.xlsx",
    extension="xlsx",
    atribucion=_ATRIBUCION_CENSO.format(producto="Current Population Survey/Housing Vacancy Survey, Table 7a"),
)
DESCARGA_CENSO_POPEST = Descarga(
    clave="censo_popest_viviendas",
    descripcion=(
        "Census Bureau, Population Estimates, NST-EST2025-HU: estimaciones anuales de viviendas de "
        "EE.UU. al 1 de julio, 2020 a 2025"
    ),
    clase_licencia=CLASE_ABIERTA,
    licencia=_LICENCIA_CENSO,
    url="https://www2.census.gov/programs-surveys/popest/tables/2020-2025/housing/totals/NST-EST2025-HU.xlsx",
    extension="xlsx",
    atribucion=_ATRIBUCION_CENSO.format(producto="Population Estimates Program, Annual Estimates of Housing Units (NST-EST2025-HU)"),
)
FRED_ID_HVS = "ETOTALUSQ176N"
CONTRASTE_FRED_HVS = _contraste(
    "fred_hvs_trimestral",
    f"FRED {FRED_ID_HVS}: inventario de viviendas del HVS, trimestral, en miles (emisor: Censo); "
    "gate de transporte de la Tabla 7a",
    URL_CSV.format(id=FRED_ID_HVS),
    "csv",
)

DESCARGAS_N0_FUENTE = (
    DESCARGA_COIN_METRICS_OFERTA,
    DESCARGA_USGS_DS140_ORO,
    DESCARGA_USGS_DS140_PLATA,
    DESCARGA_CENSO_HVS_T7,
    DESCARGA_CENSO_HVS_T7A,
    DESCARGA_CENSO_POPEST,
)
DESCARGAS_N0_CONTRASTE = tuple(CONTRASTES_Z1_HTML.values()) + (CONTRASTE_FRED_HVS,)

# --- El protocolo de Bitcoin (dato) --------------------------------------------

# A-N0-2: leído de Bitcoin Core. El subsidio por bloque es función de la altura
# y de nada más: por eso la elasticidad de la oferta es cero por construcción.
BTC_SUBSIDIO_INICIAL_SAT = 50 * 100_000_000
BTC_INTERVALO_HALVING = 210_000
BTC_SATOSHIS_POR_BTC = 100_000_000
BTC_MAXIMO = 21_000_000
BTC_CITA_PROTOCOLO = (
    "Bitcoin Core (bitcoin/bitcoin, master, commit 9dfde64cc3262329051fd05fffe40eecc786a99f, "
    "2026-10-07): src/validation.cpp, líneas 1833-1844, GetBlockSubsidy (50 * COIN, >>= halvings); "
    "src/kernel/chainparams.cpp, línea 114, nSubsidyHalvingInterval = 210000; "
    "src/consensus/amount.h, líneas 15 y 26, COIN = 100000000 y MAX_MONEY = 21000000 * COIN. Licencia MIT."
)
BTC_FECHA_CITA_PROTOCOLO = "2026-10-07"

# --- Lecturas a mano del USGS (Mineral Commodity Summaries) --------------------


@dataclass(frozen=True)
class LecturaMCS:
    """La producción mundial de un año, leída de una edición de los Mineral Commodity Summaries.

    `estimado` es la marca "e" de la propia tabla: el último año de cada edición.
    """

    metal: str
    anio: int
    valor_t: float
    estimado: bool
    edicion: int
    url: str
    sha256: str
    bytes: int
    cita: str


_MCS_URL = "https://pubs.usgs.gov/periodicals/mcs{edicion}/mcs{edicion}-{metal}.pdf"
_MCS_LEIDO = date(2026, 10, 7)


def _mcs(metal: str, edicion: int, sha256: str, bytes_: int, previo: tuple[int, float], estimado: tuple[int, float], frase: str) -> tuple[LecturaMCS, LecturaMCS]:
    nombre = {"oro": "gold", "plata": "silver"}[metal]
    url = _MCS_URL.format(edicion=edicion, metal=nombre)
    cita = (
        f"USGS, Mineral Commodity Summaries {edicion}, capítulo {nombre.capitalize()}, tabla \"World Mine "
        f"Production and Reserves\", fila \"World total (rounded)\"; texto: \"{frase}\". Leído el {_MCS_LEIDO}."
    )
    return (
        LecturaMCS(metal, previo[0], previo[1], False, edicion, url, sha256, bytes_, cita),
        LecturaMCS(metal, estimado[0], estimado[1], True, edicion, url, sha256, bytes_, cita),
    )


LECTURAS_MCS: tuple[LecturaMCS, ...] = (
    *_mcs(
        "oro", 2024, "3b551dcc4dbc7e21b3b1789c4552dab12d370e7a839288744196105e4767946c", 743608,
        (2022, 3060), (2023, 3000),
        "In 2023, worldwide gold mine production was estimated to be essentially unchanged compared with that in 2022.",
    ),
    *_mcs(
        "oro", 2025, "d4ec1750249005b4ad91dd59aaa7978932ecb7b7a410d8f6a135e6f8f8cc136f", 743291,
        (2023, 3250), (2024, 3300),
        "In 2024, worldwide gold mine production was an estimated 3,300 tons compared with 3,250 tons in 2023.",
    ),
    *_mcs(
        "oro", 2026, "c2fef62f665d3334302b8b9bd32e2da6f40b3f8136d1ae00ffa102e196943627", 138864,
        (2024, 3280), (2025, 3300),
        "In 2025, worldwide gold mine production was an estimated 3,300 tons compared with 3,280 tons in 2024.",
    ),
    *_mcs(
        "plata", 2024, "7c74bb6f756c5b801882a487aac1053d1791af2d91a20c4fbc260ca678d72336", 808370,
        (2022, 25600), (2023, 26000),
        "World silver mine production increased slightly in 2023 to an estimated 26,000 tons",
    ),
    *_mcs(
        "plata", 2025, "1aa6e68c9700f88e97d4cbf31fc039d45d4b1b738a09f6bfece8edac0ec59b24", 744783,
        (2023, 25500), (2024, 25000),
        "World silver mine production decreased in 2024 to an estimated 25,000 tons compared with 25,500 tons in 2023.",
    ),
    *_mcs(
        "plata", 2026, "f0dfe407304855a51f7647fc711f6c32081188a86269d011cd45e297aa673855", 138760,
        (2024, 25300), (2025, 26000),
        "World silver mine production increased slightly in 2025 to an estimated 26,000 tons compared with 25,300 tons in 2024.",
    ),
)

# --- Lecturas a mano del BGS (control de consistencia, A-N0-4) ----------------


@dataclass(frozen=True)
class LecturaBGS:
    metal: str
    anio: int
    valor_kg: float
    pagina_pdf: int


BGS_PUBLICACION = (
    "British Geological Survey, World Mineral Production 2020-24 (Idoine y otros, 2026), tablas "
    "\"Mine production of gold\" y \"Mine production of silver\", fila \"World total\", kilogramos de "
    "contenido de metal; incluye estimaciones de minería artesanal y redondea el total mundial"
)
BGS_URL = "https://nora.nerc.ac.uk/id/eprint/541620/1/WMP_2020%20to%202024.pdf"
BGS_SHA256 = "260a9891d28082990e49a75b97c386da1499af1ba59aad8743407c0c57aa55c6"
BGS_LEIDO = date(2026, 10, 7)
# Texto de reconocimiento que exigen los términos del BGS.
BGS_RECONOCIMIENTO = "World Mineral Statistics contributed by permission of the British Geological Survey"
LECTURAS_BGS: tuple[LecturaBGS, ...] = (
    LecturaBGS("oro", 2020, 3_200_000, 37),
    LecturaBGS("oro", 2021, 3_200_000, 37),
    LecturaBGS("oro", 2022, 3_300_000, 37),
    LecturaBGS("oro", 2023, 3_300_000, 37),
    LecturaBGS("oro", 2024, 3_300_000, 37),
    LecturaBGS("plata", 2020, 26_717_000, 74),
    LecturaBGS("plata", 2021, 26_895_000, 74),
    LecturaBGS("plata", 2022, 26_945_000, 74),
    LecturaBGS("plata", 2023, 26_754_000, 74),
    LecturaBGS("plata", 2024, 27_815_000, 74),
)

# A-N0-5: la cota superior empieza en el primer año de la DS140.
METALES_ANIO_BASE = 1900

# --- Z.1: series y sectores ------------------------------------------------------

# (clave del sector, flujo F51.1.t, saldo F51.1.s, cómo lo llama la Junta)
SECTORES_ACCIONES = (
    ("total", "FA893064105", "LM893064105", "All sectors; corporate equities; asset (línea \"Net issues\")"),
    ("no_financieras", "FA103164105", "LM103164105", "Nonfinancial corporate business; corporate equities; liability"),
    ("financieras", "FA793164105", "LM793164105", "Domestic financial sectors; corporate equities; liability"),
    ("resto_del_mundo", "FA263164105", "LM263164105", "Rest of the world; corporate equities; liability"),
)
Z1_TITULOS_DEUDA = "FL894122005"  # F3.s, línea 1: All sectors; total debt securities; liability
Z1_DEUDA_NO_FINANCIERA = "LA384104005"  # D3.s, línea 1: Domestic nonfinancial sectors; debt securities and loans; liability
# Hasta 1951 las tablas de flujos traen una fila por año (fechada :Q4); desde
# 1952 son trimestrales y el flujo anual es la media de los cuatro trimestres a
# tasa anual (A-N0-7).
Z1_ULTIMO_ANIO_ANUAL = 1951
Z1_PUBLICACION = "Z.1, publicación del 11 de septiembre de 2026 (2026:Q2)"

# --- Tolerancias (A-N0-2, A-N0-4, A-N0-9, A-N0-11), fijadas antes de comparar ---

# BTC: la oferta observada nunca puede superar lo que el calendario permite, y
# lo que falta (subsidios no reclamados enteros, salidas fuera del conjunto no
# gastado) tiene que ser ínfimo. Fijada con el resultado del paso 0 a la vista:
# -80 BTC (-0.0004 %) al 2026-10-06 (FUENTES.md, N0.3.2).
TOLERANCIA_BTC_CALENDARIO_PCT = 0.001
# Oro y plata contra el BGS: los dos compiladores no miden lo mismo (el BGS suma
# minería artesanal y, en plata, producción de fundición en algunos países).
# Fijada antes de correr, con lo visto en el paso 0: oro entre 0.6 % y 4.4 %,
# plata entre 7.6 % y 9.9 %. La plata va a quedar en disputa; se declara.
TOLERANCIA_BGS_PCT = 5.0
# Z.1: el HTML publica miles de millones con un decimal; medio paso.
TOLERANCIA_Z1_HTML_MILES_DE_MILLONES = 0.05
# A-N0-11, gate de transporte de las tablas del HVS: la identidad de la propia
# tabla, "All housing units" = "Vacant" + "Total occupied", con tres cifras
# redondeadas a miles (±0.5 cada una). Por construcción.
TOLERANCIA_HVS_SUMA_MILES = 1.5
# Tabla 7a contra FRED (media de los cuatro trimestres): el Censo redondea a
# miles (±0.5) y la media de cuatro trimestres redondeados aporta hasta ±0.5
# más. Por construcción. Es un CONTROL, no un gate, y esa clase se fijó con el
# resultado a la vista: en 2001-2019 la diferencia llega a 3.75 mil en ocho
# años, así que FRED no reproduce los promedios de la Tabla 7a al redondeo.
# No se sabe por qué; el control lo marca y no decide.
TOLERANCIA_HVS_FRED_MILES = 1.0
# FRED trae los trimestres como se publicaron; la Tabla 7a reexpresa 2020 en
# adelante con la Vintage 2025 (diferencias de 5 a 58 mil, vistas en el paso 0).
# El control rige hasta la última vintage cerrada; de 2020 en adelante no se
# compara y la diferencia va a la ficha.
HVS_FRED_CONTROL_HASTA = 2019
# Population Estimates (1 de julio) contra la Tabla 7a (promedio del año):
# conceptos distintos; control. Fijada con el resultado a la vista: -0.07 %.
TOLERANCIA_POPEST_PCT = 0.5
MINIMO_COMPARACIONES_N0 = MINIMO_COMPARACIONES_GATE

# --- Salidas ----------------------------------------------------------------------

ARCHIVO_N0_SERIES = DIR_SERIES / "numerador_series.csv"
ARCHIVO_N0_FICHAS = DIR_SERIES / "serie_N0.csv"
ARCHIVO_N0_DESCARGAS = DIR_SERIES / "numerador_descargas.csv"
FORMATO_N0 = "%.12g"
EPSILON_REVISION_N0 = 0.0005
COLUMNAS_N0_SERIES = ["serie", "anio", "fecha", "valor", "unidad", "estado", "control", "cita", "nota"]
COLUMNAS_N0_FICHAS = [
    "serie",
    "nombre",
    "familia",
    "mide",
    "publicada",
    "estado",
    "unidad",
    "convencion",
    "frecuencia",
    "emisor",
    "fuente",
    "identificador",
    "url",
    "licencia",
    "atribucion",
    "validacion",
    "supuestos",
    "quiebres",
    "primer_anio",
    "ultimo_anio",
    "anios",
]
CONTROL_DENTRO = CONTRASTE_FMI_DENTRO
CONTROL_DISPUTA = VALOR_EN_DISPUTA
CONTROL_SIN_COMPARAR = CONTRASTE_FMI_SIN_COMPARAR


@dataclass(frozen=True)
class SerieN0:
    """Una serie anual de N0 y todo lo que su ficha tiene que decir."""

    clave: str
    nombre: str
    familia: str
    mide: str
    unidad: str
    convencion: str
    emisor: str
    descarga: Descarga | None
    identificador: str
    supuestos: tuple[str, ...]
    frecuencia: str = "anual"
    nota: str = ""


_SUP_BTC = ("A-N0-1", "A-N0-2", "A-N0-13")
_SUP_METALES = ("A-N0-1", "A-N0-3", "A-N0-4", "A-N0-13")
_SUP_COTA = ("A-N0-1", "A-N0-3", "A-N0-5", "A-N0-6", "A-N0-13")
_SUP_ACCIONES = ("A-N0-1", "A-N0-7", "A-N0-9", "A-N0-13")
_SUP_DEUDA = ("A-N0-1", "A-N0-8", "A-N0-9", "A-N0-13")
_SUP_VIVIENDAS = ("A-N0-1", "A-N0-10", "A-N0-11", "A-N0-13")
_EMISOR_COIN_METRICS = "Coin Metrics (lectura de la cadena de Bitcoin)"
_EMISOR_USGS = "U.S. Geological Survey"
_EMISOR_JUNTA_Z1 = "Junta de Gobernadores del Sistema de la Reserva Federal"
_EMISOR_CENSO = "U.S. Census Bureau"
BTC_CONVENCION_FIN_DE_ANIO = "oferta al cierre del 31 de diciembre (00:00 UTC del 1 de enero), lectura de Coin Metrics"
BTC_CONVENCION_ANIO = "suma de los bloques del año calendario (UTC)"


def _serie_btc(clave: str, nombre: str, mide: str, unidad: str, convencion: str, identificador: str, nota: str = "") -> SerieN0:
    return SerieN0(clave, nombre, FAMILIA_BTC, mide, unidad, convencion, _EMISOR_COIN_METRICS, DESCARGA_COIN_METRICS_OFERTA, identificador, _SUP_BTC, nota=nota)


def _serie_metal(metal: str, cota: bool) -> SerieN0:
    descarga = DESCARGA_USGS_DS140_ORO if metal == "oro" else DESCARGA_USGS_DS140_PLATA
    nombre_metal = {"oro": "Oro", "plata": "Plata"}[metal]
    if not cota:
        return SerieN0(
            f"{metal}_produccion_mundial_t",
            f"{nombre_metal}: producción minera mundial anual",
            FAMILIA_METALES,
            MIDE_FLUJO,
            "toneladas métricas de contenido de metal",
            "producción de mina del año calendario; Data Series 140 en todo su rango y Mineral Commodity Summaries después, con el último año estimado",
            _EMISOR_USGS,
            descarga,
            "DS140, columna World production; MCS, World total (rounded)",
            _SUP_METALES,
        )
    advertencia = (
        "cota superior: el denominador excluye lo producido antes de 1900 y supone pérdidas despreciables"
        if metal == "oro"
        else "no es una cota: el consumo industrial no recuperado reduce el stock real y la cifra es solo indicativa"
    )
    return SerieN0(
        f"{metal}_crecimiento_stock_cota_superior_pct",
        f"{nombre_metal}: cota superior de la tasa de crecimiento del stock (producción del año / producción acumulada desde 1900)",
        FAMILIA_METALES,
        MIDE_COTA,
        "% anual",
        "producción del año dividida por la suma de la producción mundial de 1900 al año anterior (cálculo propio)",
        _EMISOR_USGS,
        descarga,
        "cálculo propio sobre la producción mundial",
        _SUP_COTA,
        nota=advertencia,
    )


def _series_acciones() -> tuple[SerieN0, ...]:
    series = []
    for sector, flujo, saldo, rotulo in SECTORES_ACCIONES:
        nombre_sector = {
            "total": "todos los sectores",
            "no_financieras": "sociedades no financieras",
            "financieras": "sectores financieros internos",
            "resto_del_mundo": "resto del mundo",
        }[sector]
        series.append(
            SerieN0(
                f"acciones_eeuu_emision_neta_{sector}_musd",
                f"Acciones de EE.UU.: emisión neta, {nombre_sector}",
                FAMILIA_ACCIONES,
                MIDE_FLUJO,
                "millones de USD",
                "flujo del año calendario a valor de transacción: hasta 1951 el dato anual de la Junta; desde 1952 la media de los cuatro trimestres a tasa anual ajustada",
                _EMISOR_JUNTA_Z1,
                DESCARGA_Z1_POR_TABLA["F51_1_t"],
                f"{flujo}.Q ({rotulo})",
                _SUP_ACCIONES,
                nota="en dólares, no en acciones: la cantidad de acciones no existe en el Z.1",
            )
        )
        series.append(
            SerieN0(
                f"acciones_eeuu_valor_de_mercado_{sector}_musd",
                f"Acciones de EE.UU.: valor de mercado a fin de año, {nombre_sector}",
                FAMILIA_ACCIONES,
                MIDE_STOCK,
                "millones de USD",
                "saldo a fin del cuarto trimestre, a valor de mercado, sin ajuste estacional",
                _EMISOR_JUNTA_Z1,
                DESCARGA_Z1_POR_TABLA["F51_1_s"],
                f"{saldo}.Q",
                _SUP_ACCIONES,
            )
        )
        series.append(
            SerieN0(
                f"acciones_eeuu_emision_neta_{sector}_pct_vm",
                f"Acciones de EE.UU.: emisión neta como porcentaje del valor de mercado del año anterior, {nombre_sector}",
                FAMILIA_ACCIONES,
                MIDE_TASA,
                "% del valor de mercado de fin del año anterior",
                "emisión neta del año dividida por el saldo a valor de mercado del cuarto trimestre del año anterior (cálculo propio); mezcla cantidades y precios y lo declara",
                _EMISOR_JUNTA_Z1,
                DESCARGA_Z1_POR_TABLA["F51_1_t"],
                f"{flujo}.Q / {saldo}.Q",
                _SUP_ACCIONES,
                nota="sin interpretar: un valor negativo es más recompras que emisiones en ese año",
            )
        )
    return tuple(series)


SERIES_N0: tuple[SerieN0, ...] = (
    _serie_btc(
        "btc_emision_calendario_btc",
        "BTC: emisión del año según el calendario del protocolo",
        MIDE_FLUJO,
        "BTC",
        BTC_CONVENCION_ANIO + "; subsidio de cada bloque según Bitcoin Core, por los bloques observados del año",
        "subsidio(altura) × BlkCnt",
        nota="el calendario fija el subsidio por bloque; cuántos bloques caen en un año es un dato observado",
    ),
    _serie_btc(
        "btc_emision_observada_btc",
        "BTC: emisión observada del año",
        MIDE_FLUJO,
        "BTC",
        BTC_CONVENCION_ANIO + "; suma de IssTotNtv",
        "IssTotNtv",
    ),
    _serie_btc(
        "btc_oferta_fin_de_anio_btc",
        "BTC: oferta en circulación a fin de año",
        MIDE_STOCK,
        "BTC",
        BTC_CONVENCION_FIN_DE_ANIO,
        "SplyCur",
    ),
    _serie_btc(
        "btc_oferta_crecimiento_pct",
        "BTC: tasa de crecimiento de la oferta en circulación",
        MIDE_TASA,
        "% anual",
        "oferta a fin de año sobre la oferta a fin del año anterior, menos uno (cálculo propio)",
        "SplyCur",
    ),
    _serie_btc(
        "btc_porcentaje_minado_pct",
        "BTC: porcentaje del máximo de 21 millones ya emitido, a fin de año",
        MIDE_PROPORCION,
        "% de 21000000 BTC",
        BTC_CONVENCION_FIN_DE_ANIO + " dividida por MAX_MONEY (cálculo propio)",
        "SplyCur / 21000000",
    ),
    _serie_btc(
        "btc_oferta_a_la_fecha_btc",
        "BTC: oferta en circulación a la fecha de la descarga",
        MIDE_STOCK,
        "BTC",
        "último día con dato en la descarga, cierre a las 00:00 UTC del día siguiente",
        "SplyCur",
        nota="una sola fila, con la fecha; no es una serie anual",
    ),
    _serie_btc(
        "btc_porcentaje_minado_a_la_fecha_pct",
        "BTC: porcentaje del máximo de 21 millones ya emitido, a la fecha de la descarga",
        MIDE_PROPORCION,
        "% de 21000000 BTC",
        "último día con dato en la descarga, dividido por MAX_MONEY (cálculo propio)",
        "SplyCur / 21000000",
        nota="una sola fila, con la fecha; no es una serie anual",
    ),
    SerieN0(
        "btc_elasticidad_oferta",
        "BTC: elasticidad de la oferta respecto del precio",
        FAMILIA_ELASTICIDAD,
        MIDE_ELASTICIDAD,
        "d ln(oferta) / d ln(precio)",
        "cero por construcción: el subsidio por bloque es función de la altura del bloque y de nada más (Bitcoin Core, GetBlockSubsidy)",
        "Bitcoin Core (código del protocolo)",
        None,
        "GetBlockSubsidy",
        ("A-N0-1", "A-N0-12"),
        frecuencia="sin frecuencia: propiedad del protocolo",
        nota="dato del protocolo, no una estimación; no hay elasticidad que estimar",
    ),
    _serie_metal("oro", cota=False),
    _serie_metal("oro", cota=True),
    _serie_metal("plata", cota=False),
    _serie_metal("plata", cota=True),
    *_series_acciones(),
    SerieN0(
        "deuda_eeuu_titulos_deuda_musd",
        "Deuda de EE.UU.: títulos de deuda en circulación, todos los sectores",
        FAMILIA_DEUDA,
        MIDE_STOCK,
        "millones de USD",
        "saldo a fin del cuarto trimestre, sin ajuste estacional; incluye los títulos emitidos por el resto del mundo en manos de residentes",
        _EMISOR_JUNTA_Z1,
        DESCARGA_Z1_POR_TABLA["F3_s"],
        f"{Z1_TITULOS_DEUDA}.Q (All sectors; total debt securities; liability)",
        _SUP_DEUDA,
    ),
    SerieN0(
        "deuda_eeuu_titulos_deuda_variacion_pct",
        "Deuda de EE.UU.: variación anual de los títulos de deuda en circulación",
        FAMILIA_DEUDA,
        MIDE_TASA,
        "% anual",
        "saldo de fin de año sobre el de fin del año anterior, menos uno (cálculo propio)",
        _EMISOR_JUNTA_Z1,
        DESCARGA_Z1_POR_TABLA["F3_s"],
        f"{Z1_TITULOS_DEUDA}.Q",
        _SUP_DEUDA,
    ),
    SerieN0(
        "deuda_eeuu_no_financiera_musd",
        "Deuda de EE.UU.: deuda de los sectores no financieros internos (títulos y préstamos)",
        FAMILIA_DEUDA,
        MIDE_STOCK,
        "millones de USD",
        "saldo a fin del cuarto trimestre, ajustado por estacionalidad",
        _EMISOR_JUNTA_Z1,
        DESCARGA_Z1_POR_TABLA["D3_s"],
        f"{Z1_DEUDA_NO_FINANCIERA}.Q (Domestic nonfinancial sectors; debt securities and loans; liability)",
        _SUP_DEUDA,
    ),
    SerieN0(
        "deuda_eeuu_no_financiera_variacion_pct",
        "Deuda de EE.UU.: variación anual de la deuda de los sectores no financieros internos",
        FAMILIA_DEUDA,
        MIDE_TASA,
        "% anual",
        "saldo de fin de año sobre el de fin del año anterior, menos uno (cálculo propio)",
        _EMISOR_JUNTA_Z1,
        DESCARGA_Z1_POR_TABLA["D3_s"],
        f"{Z1_DEUDA_NO_FINANCIERA}.Q",
        _SUP_DEUDA,
    ),
    SerieN0(
        "viviendas_eeuu_parque_hvs_miles",
        "Viviendas de EE.UU.: parque total (HVS, Tabla 7)",
        FAMILIA_VIVIENDAS,
        MIDE_STOCK,
        "miles de viviendas",
        "promedio de las estimaciones mensuales del año; cada año con el valor de su base original, y la base revisada del Censo solo como denominador de la tasa del año siguiente (A-N0-10)",
        _EMISOR_CENSO,
        DESCARGA_CENSO_HVS_T7,
        "Tabla 7, fila All housing units",
        _SUP_VIVIENDAS,
    ),
    SerieN0(
        "viviendas_eeuu_parque_hvs_crecimiento_pct",
        "Viviendas de EE.UU.: tasa de crecimiento del parque (HVS, Tabla 7)",
        FAMILIA_VIVIENDAS,
        MIDE_TASA,
        "% anual",
        "parque del año sobre el del año anterior en la misma base, menos uno (cálculo propio)",
        _EMISOR_CENSO,
        DESCARGA_CENSO_HVS_T7,
        "Tabla 7, fila All housing units",
        _SUP_VIVIENDAS,
    ),
    SerieN0(
        "viviendas_eeuu_parque_hvs_7a_miles",
        "Viviendas de EE.UU.: parque total revisado con los controles de vivienda (HVS, Tabla 7a)",
        FAMILIA_VIVIENDAS,
        MIDE_STOCK,
        "miles de viviendas",
        "promedio de las estimaciones mensuales del año, revisado con las vintages 2010, 2020 y 2025 de Population Estimates",
        _EMISOR_CENSO,
        DESCARGA_CENSO_HVS_T7A,
        "Tabla 7a, fila All housing units",
        _SUP_VIVIENDAS,
    ),
    SerieN0(
        "viviendas_eeuu_parque_hvs_7a_crecimiento_pct",
        "Viviendas de EE.UU.: tasa de crecimiento del parque revisado (HVS, Tabla 7a)",
        FAMILIA_VIVIENDAS,
        MIDE_TASA,
        "% anual",
        "parque del año sobre el del año anterior, menos uno (cálculo propio)",
        _EMISOR_CENSO,
        DESCARGA_CENSO_HVS_T7A,
        "Tabla 7a, fila All housing units",
        _SUP_VIVIENDAS,
    ),
    SerieN0(
        "viviendas_eeuu_parque_popest_unidades",
        "Viviendas de EE.UU.: parque total al 1 de julio (Population Estimates)",
        FAMILIA_VIVIENDAS,
        MIDE_STOCK,
        "viviendas",
        "existencias al 1 de julio, estimadas desde la base del Censo de 2020 (vintage 2025)",
        _EMISOR_CENSO,
        DESCARGA_CENSO_POPEST,
        "NST-EST2025-HU, fila United States",
        _SUP_VIVIENDAS,
    ),
    SerieN0(
        "viviendas_eeuu_parque_popest_crecimiento_pct",
        "Viviendas de EE.UU.: tasa de crecimiento del parque al 1 de julio (Population Estimates)",
        FAMILIA_VIVIENDAS,
        MIDE_TASA,
        "% anual",
        "parque al 1 de julio sobre el del 1 de julio anterior, menos uno (cálculo propio)",
        _EMISOR_CENSO,
        DESCARGA_CENSO_POPEST,
        "NST-EST2025-HU, fila United States",
        _SUP_VIVIENDAS,
    ),
)
SERIES_N0_POR_CLAVE = {serie.clave: serie for serie in SERIES_N0}


@dataclass(frozen=True)
class PendienteN0:
    """Algo que el sitio afirma o afirmaría y que no tiene serie: va a la ficha como NO MEDIDO o pendiente."""

    clave: str
    nombre: str
    familia: str
    mide: str
    estado: str
    fuente: str
    supuestos: tuple[str, ...]


_PENDIENTE_RESPUESTA = (
    "pendiente: familia \"respuesta observada de la oferta al precio\"; antes de calcular, un paso 0 corto "
    "de las fuentes de precio y un prerregistro en SUPUESTOS.md con su propio commit (A-N0-12)"
)
PENDIENTES_N0: tuple[PendienteN0, ...] = (
    PendienteN0(
        "oro_stock_sobre_tierra_t",
        "Oro: existencias sobre la superficie",
        FAMILIA_METALES,
        MIDE_STOCK,
        "NO MEDIDO como serie: la única serie de existencias es del World Gold Council, clase (c); su cifra va como estimación de terceros en citas_terceros.csv, fuera de todo cálculo (A-N0-6, A-D0-28)",
        "World Gold Council (c); USGS no publica existencias",
        ("A-N0-6",),
    ),
    PendienteN0(
        "oro_stock_to_flow",
        "Oro: stock-to-flow",
        FAMILIA_METALES,
        MIDE_PROPORCION,
        "NO MEDIDO como serie: sin existencias abiertas no hay cociente; la cota superior del crecimiento del stock es lo más que se puede publicar (A-N0-5, A-N0-6)",
        "cálculo propio imposible sin existencias",
        ("A-N0-5", "A-N0-6"),
    ),
    PendienteN0(
        "plata_stock_t",
        "Plata: existencias",
        FAMILIA_METALES,
        MIDE_STOCK,
        "NO MEDIDO: no se encontró ninguna fuente abierta de existencias de plata (FUENTES.md, N0.5.5)",
        "ninguna",
        ("A-N0-6",),
    ),
    PendienteN0(
        "acciones_global_en_circulacion",
        "Acciones: cantidad en circulación o emisión neta global",
        FAMILIA_ACCIONES,
        MIDE_STOCK,
        "NO MEDIDO: sin fuente abierta (la WFE es de clase (c), FUENTES.md D0.9); lo que hay es EE.UU. (A-N0-7)",
        "WFE (c)",
        ("A-N0-7", "A-N0-13"),
    ),
    PendienteN0(
        "viviendas_global",
        "Viviendas: parque global",
        FAMILIA_VIVIENDAS,
        MIDE_STOCK,
        "NO MEDIDO: UN-Habitat no se leyó y no hay otra fuente abierta leída; lo que hay es EE.UU. (A-N0-10)",
        "UN-Habitat (no leído)",
        ("A-N0-10", "A-N0-13"),
    ),
    PendienteN0(
        "deuda_global_titulos",
        "Deuda: títulos de deuda en circulación, suma de economías",
        FAMILIA_DEUDA,
        MIDE_STOCK,
        "NO MEDIDO: es la suma de 49 economías declarantes al BIS de A-D0-22, pendiente de implementar; nunca \"global\" (A-N0-8)",
        "BIS, Debt securities statistics (a)",
        ("A-N0-8", "A-D0-22"),
    ),
    PendienteN0(
        "deuda_eeuu_elasticidad_oferta",
        "Deuda de EE.UU.: elasticidad de la oferta respecto del precio",
        FAMILIA_ELASTICIDAD,
        MIDE_ELASTICIDAD,
        "NO MEDIDO: la deuda no tiene un precio comparable (decisión del dueño, FUENTES.md N0.10.5, punto 4; A-N0-12)",
        "ninguna",
        ("A-N0-12",),
    ),
    PendienteN0("oro_respuesta_oferta_precio", "Oro: respuesta observada de la oferta al precio", FAMILIA_ELASTICIDAD, MIDE_ELASTICIDAD, _PENDIENTE_RESPUESTA, "USGS DS140 (producción y valor unitario) o Pink Sheet; deflactor por leer", ("A-N0-12",)),
    PendienteN0("plata_respuesta_oferta_precio", "Plata: respuesta observada de la oferta al precio", FAMILIA_ELASTICIDAD, MIDE_ELASTICIDAD, _PENDIENTE_RESPUESTA, "USGS DS140 (producción y valor unitario) o Pink Sheet; deflactor por leer", ("A-N0-12",)),
    PendienteN0("viviendas_eeuu_respuesta_oferta_precio", "Viviendas de EE.UU.: respuesta observada de la oferta al precio", FAMILIA_ELASTICIDAD, MIDE_ELASTICIDAD, _PENDIENTE_RESPUESTA, "Censo (construcción) e índice de precios de la FHFA, por leer", ("A-N0-12",)),
    PendienteN0("acciones_eeuu_respuesta_oferta_precio", "Acciones de EE.UU.: respuesta observada de la oferta al precio", FAMILIA_ELASTICIDAD, MIDE_ELASTICIDAD, _PENDIENTE_RESPUESTA, "Z.1 (emisión neta) y una medida de valuación por definir", ("A-N0-12",)),
)
