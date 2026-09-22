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
