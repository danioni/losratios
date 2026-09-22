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
    """Ancla externa contra la que se contrasta el cálculo antes de publicar."""

    fecha: date
    walcl: float
    tga: float
    rrp: float
    s2_1_esperado: float
    tolerancia: float
    fuente: str


SERIE_WALCL = SerieFRED(
    id="WALCL",
    descripcion="Activos totales de la Fed (menos eliminaciones de consolidacion), nivel de miércoles",
    unidad="millones",
    unidad_fred="Millions of U.S. Dollars",
    frecuencia="semanal_miercoles",
    banda_plausible=(500.0, 20_000.0),
)

# A-S2-4: WTREGEN es un promedio semanal, no el nivel del miércoles que publica
# el H.4.1. Se usa por convención (así lo pide el marco), y el gate de validación
# es el que decide si la mezcla de convenciones cabe en la tolerancia de +/-5.
SERIE_TGA_PROMEDIO_SEMANAL = SerieFRED(
    id="WTREGEN",
    descripcion="Cuenta general del Tesoro (TGA), promedio semanal a miércoles",
    unidad="miles_de_millones",
    unidad_fred="Billions of U.S. Dollars",
    frecuencia="semanal_miercoles",
    banda_plausible=(0.0, 2_000.0),
)

# Alternativa documentada en SUPUESTOS.md (A-S2-4): el TGA como nivel de miércoles,
# que es la convención del H.4.1. Para usarla, apuntar SERIE_TGA acá.
SERIE_TGA_NIVEL_MIERCOLES = SerieFRED(
    id="WDTGAL",
    descripcion="Cuenta general del Tesoro (TGA), nivel de miércoles",
    unidad="millones",
    unidad_fred="Millions of U.S. Dollars",
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

# Serie de TGA efectivamente en uso. Cambiarla es un cambio de supuesto (A-S2-4).
SERIE_TGA = SERIE_TGA_PROMEDIO_SEMANAL

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

VALIDACION_H41 = CasoValidacion(
    fecha=date(2026, 9, 16),
    walcl=6747.0,
    tga=877.0,
    rrp=4.0,
    s2_1_esperado=5866.0,
    tolerancia=5.0,
    fuente="H.4.1 de la semana del 16 de septiembre de 2026, en miles de millones de USD",
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
