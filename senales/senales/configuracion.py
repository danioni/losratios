"""Configuración central del marco de señales.

Todo parámetro que afecte un número publicado vive en este archivo, no en el
código de cálculo. Cambiar un valor de aquí obliga a registrar el cambio en
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
MINIMO_ANCLAS = 2

# --- Agregado (A-D0-10, A-D0-11, A-D0-12) ------------------------------------

# Las economías que entran al agregado en USD: nombre, serie de dinero y tipo
# de cambio. A-D0-9: China queda fuera mientras no se demuestre que su
# definición es comparable.
ECONOMIAS_AGREGADO = (
    ("eeuu", "m2_eeuu_sin_ajustar", None),
    ("eurozona", "m2_eurozona_sin_ajustar", "usd_por_eur"),
    ("japon", "m2_japon", "jpy_por_usd"),
)
NOMBRE_AGREGADO = "M2 de tres economías (EE.UU., Eurozona y Japón), en USD"

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
    "agregado_usd",
    "agregado_usd_tc_constante",
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
