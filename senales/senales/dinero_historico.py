"""Fase D0, tramo histórico: el dinero de EE.UU. antes de 1959, transcrito de la Junta.

Dos series que no se llaman M2 (A-D0-17): efectivo y depósitos en bancos
comerciales en fechas de balance, 1892 a 1946, de la Tabla 9 de *Banking and
Monetary Statistics, 1914-1941* y de su continuación en el volumen 1941-1970;
y la misma suma, mensual y ajustada por estacionalidad, 1947 a 1958, de la
Tabla 1.1 del volumen 1941-1970. Las dos son escaneos: las cifras se
transcribieron dos veces, de forma independiente, y este módulo exige que las
dos lecturas coincidan celda por celda antes de usarlas (A-D0-19). Después
verifica que los subtotales impresos sumen el total impreso, compara contra una
segunda publicación con una tolerancia fijada antes (A-D0-32) y publica lo que
cerró. Lo que no cierra queda NO MEDIDO, con el motivo en la ficha.

La serie sin ajuste estacional de 1947-58 también está transcrita y controlada,
pero no tiene segunda fuente accesible a un programa: se publica como NO MEDIDO
(A-D0-31). Las erratas de la fuente se publican tal como están impresas y se
marcan como valor en disputa (A-D0-33).

Uso, desde senales/:

    python -m senales.dinero_historico
    python -m senales.dinero_historico --fecha-descarga 2026-10-07

Códigos de salida: 0 todo bien · 1 problema con una fuente · 2 la transcripción
o un gate de sumas no cerró (no se escribe nada).
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from senales import bitacora, fuentes_denominador, fuentes_precios
from senales.configuracion import (
    ANCLAS_HSUS_1960,
    ARCHIVO_CHANGELOG,
    ARCHIVO_D0_FICHAS,
    ARCHIVO_DINERO_HISTORICO,
    ARCHIVO_DINERO_HISTORICO_DESCARGAS,
    CITA_BMS_1914_1941,
    CITA_BMS_1941_1970_CONTINUACION,
    CITA_BMS_1941_1970_TABLA_1_1,
    CLAVE_DINERO_1892_1946,
    CLAVE_DINERO_1947_1958,
    CLAVE_DINERO_1947_1958_SIN_AJUSTAR,
    CLAVES_DINERO_HISTORICO,
    COLUMNAS_D0_FICHAS,
    COLUMNAS_DINERO_HISTORICO,
    DESCARGA_BMS_1914_1941,
    DESCARGA_BMS_1941_1970,
    DESCARGA_FRED_NBER_M14144C,
    DESCARGA_HSUS_1960,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    DIR_SERIES,
    DIR_TRANSCRIPCION_JUNTA,
    EPSILON_REVISION_D0,
    ESTADO_DATO,
    ESTADO_FECHA_DE_BALANCE,
    FORMATO_D0,
    FRED_SERIE_NBER_M14144C,
    MINIMO_COMPARACIONES_DINERO_HISTORICO,
    NO_MEDIDO_SIN_AJUSTAR_1947_1958,
    NO_MEDIDO_SIN_VALIDACION,
    SERIE_DINERO_1892_1946,
    SERIE_DINERO_1947_1958,
    SERIE_DINERO_1947_1958_SIN_AJUSTAR,
    SERIES_DINERO_HISTORICO,
    TOLERANCIA_ANCLAS_HSUS,
    TOLERANCIA_NBER_MILES_DE_MILLONES,
    TOLERANCIA_SUMA_MILES_DE_MILLONES,
    TOLERANCIA_SUMA_MILLONES,
    VALOR_EN_DISPUTA,
    SerieD0,
)
from senales.denominador import Validacion
from senales.fuentes_denominador import CopiaFaltante
from senales.fuentes_fred import ErrorDeFuente
from senales.nucleo import asegurar_directorios, escribir_csv_determinista, formatear

CODIGO_ERROR_FUENTE = 1
CODIGO_GATE = 2

# Cada tabla transcrita: los dos archivos independientes y su columna clave.
TABLAS = {
    "tabla_9": ("A_tabla_9.csv", "B_tabla_9.csv", "fecha"),
    "continuacion_tabla_9": ("A_continuacion_tabla_9.csv", "B_continuacion_tabla_9.csv", "fecha"),
    "tabla_1_1_A": ("A_tabla_1_1_A.csv", "B_tabla_1_1_A.csv", "mes"),
    "tabla_1_1_B": ("A_tabla_1_1_B.csv", "B_tabla_1_1_B.csv", "mes"),
}
ARCHIVO_RESOLUCIONES = "resoluciones.csv"

# Identidades impresas de cada tabla: total = suma de componentes, con la
# tolerancia del redondeo de la unidad (A-D0-32).
IDENTIDADES = {
    "tabla_9": (
        ("total_depositos", ("vista_ajustados", "gobierno", "plazo_total"), TOLERANCIA_SUMA_MILLONES),
        ("plazo_total", ("plazo_comerciales", "plazo_cajas", "plazo_postal"), TOLERANCIA_SUMA_MILLONES),
        ("total_depositos_y_efectivo", ("total_depositos", "efectivo"), TOLERANCIA_SUMA_MILLONES),
        ("total_vista_y_efectivo", ("vista_ajustados", "efectivo"), TOLERANCIA_SUMA_MILLONES),
    ),
    "continuacion_tabla_9": (
        ("money_stock_total", ("efectivo", "vista_ajustados"), TOLERANCIA_SUMA_MILLONES),
        ("plazo_total", ("plazo_comerciales", "plazo_cajas", "plazo_postal"), TOLERANCIA_SUMA_MILLONES),
    ),
    "tabla_1_1_A": (("total", ("efectivo", "vista"), TOLERANCIA_SUMA_MILES_DE_MILLONES),),
    "tabla_1_1_B": (("total", ("efectivo", "vista"), TOLERANCIA_SUMA_MILES_DE_MILLONES),),
}
# Las tablas cuyas identidades son un gate: si una falla, la corrida se detiene.
# En la Tabla 1.1 la identidad es un control: una fila que no cuadra se publica
# como está impresa y marcada en disputa (A-D0-33).
TABLAS_CON_GATE_DE_SUMAS = ("tabla_9", "continuacion_tabla_9")

# Las dos filas de 1941 están en la Tabla 9 y en su continuación: tienen que
# ser iguales, columna por columna.
SUPERPOSICION_1941 = {
    "money_stock_total": "total_vista_y_efectivo",
    "efectivo": "efectivo",
    "vista_ajustados": "vista_ajustados",
    "plazo_total": "plazo_total",
    "plazo_comerciales": "plazo_comerciales",
    "plazo_cajas": "plazo_cajas",
    "plazo_postal": "plazo_postal",
    "gobierno": "gobierno",
}
# Qué columna de la continuación corresponde a cada columna de la Tabla 9 que
# usan las anclas del Censo.
CONTINUACION_A_TABLA_9 = {valor: clave for clave, valor in SUPERPOSICION_1941.items()}

NOTAS_TABLA_9 = {
    "plazo_comerciales:5": (
        "nota 5 de la Tabla 9: excluye tres cajas de ahorro mutuas que pasaron a ser miembros del "
        "Sistema de la Reserva en 1941"
    ),
    "plazo_cajas:5": (
        "nota 5 de la Tabla 9: incluye tres cajas de ahorro mutuas que pasaron a ser miembros del "
        "Sistema de la Reserva en 1941"
    ),
}

COMPONENTES_FECHAS_DE_BALANCE = ("efectivo", "vista_ajustados", "plazo_comerciales")
UNIDAD_MILLONES = "millones de USD"
UNIDAD_MILES_DE_MILLONES = "miles de millones de USD"


class ErrorDeTranscripcion(ErrorDeFuente):
    """Las dos lecturas no coinciden, o una identidad impresa no cuadra."""


# --- Lectura y cotejo de las dos transcripciones (A-D0-19) ----------------------


@dataclass
class Transcripcion:
    """Las cuatro tablas, ya cotejadas, con los valores como números."""

    tablas: dict[str, pd.DataFrame]
    celdas_comparadas: int
    resueltas: list[str] = field(default_factory=list)  # qué celdas difirieron y cómo se cerraron


def _leer_csv(ruta: Path) -> list[dict[str, str]]:
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def _numero(texto: str) -> float | None:
    limpio = texto.strip().replace(",", "")
    if limpio == "":
        return None
    return float(limpio)


def _leer_resoluciones(directorio: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    ruta = directorio / ARCHIVO_RESOLUCIONES
    if not ruta.exists():
        return {}
    return {(f["tabla"], f["fecha"], f["columna"]): f for f in _leer_csv(ruta)}


def leer_transcripcion(directorio: Path = DIR_TRANSCRIPCION_JUNTA) -> Transcripcion:
    """Lee las lecturas A y B de cada tabla y exige que coincidan celda por celda.

    Una celda en la que difieren solo se acepta si `resoluciones.csv` trae esa
    celda con los dos valores leídos y el valor resuelto releyendo la imagen.
    Nunca se elige una de las dos lecturas (A-D0-19).
    """
    resoluciones = _leer_resoluciones(directorio)
    tablas: dict[str, pd.DataFrame] = {}
    diferencias: list[str] = []
    resueltas: list[str] = []
    comparadas = 0
    for tabla, (nombre_a, nombre_b, clave) in TABLAS.items():
        filas_a = {f[clave].strip(): f for f in _leer_csv(directorio / nombre_a)}
        filas_b = {f[clave].strip(): f for f in _leer_csv(directorio / nombre_b)}
        if set(filas_a) != set(filas_b):
            solo_a = sorted(set(filas_a) - set(filas_b))
            solo_b = sorted(set(filas_b) - set(filas_a))
            raise ErrorDeTranscripcion(
                f"{tabla}: las dos transcripciones no tienen las mismas filas; solo en A: {solo_a}; solo en B: {solo_b}"
            )
        columnas_a = [c for c in next(iter(filas_a.values())) if c not in (clave, "nota")]
        columnas_b = [c for c in next(iter(filas_b.values())) if c not in (clave, "nota")]
        if columnas_a != columnas_b:
            raise ErrorDeTranscripcion(f"{tabla}: las columnas de A y de B no coinciden: {columnas_a} / {columnas_b}")
        registros = []
        for fecha in sorted(filas_a):
            fila = {clave: fecha}
            notas = []
            for columna in columnas_a:
                va, vb = filas_a[fecha][columna].strip(), filas_b[fecha][columna].strip()
                comparadas += 1
                if va == vb:
                    texto = va
                else:
                    resolucion = resoluciones.get((tabla, fecha, columna))
                    if (
                        resolucion is None
                        or resolucion["valor_A"].strip() != va
                        or resolucion["valor_B"].strip() != vb
                    ):
                        diferencias.append(f"{tabla} {fecha} {columna}: A={va!r} B={vb!r}")
                        continue
                    texto = resolucion["valor_resuelto"].strip()
                    resueltas.append(
                        f"{tabla} {fecha} {columna}: A={va} B={vb} -> {texto} ({resolucion['como_se_resolvio']})"
                    )
                    notas.append(f"lectura con reserva ({columna}): A leyó {va} y B {vb}; se resolvió {texto} releyendo la imagen")
                if "?" in texto:
                    diferencias.append(f"{tabla} {fecha} {columna}: dígito ilegible sin resolver ({texto!r})")
                    continue
                fila[columna] = _numero(texto)
            # Las marcas de nota al pie (p. ej. "plazo_comerciales:5") van a la serie, en el
            # componente que anotan; las observaciones libres de cada lectura quedan en los
            # crudos versionados.
            for filas in (filas_a, filas_b):
                for marca in filas[fecha].get("nota", "").split(";"):
                    marca = marca.strip()
                    if marca in NOTAS_TABLA_9 and marca not in notas:
                        notas.append(marca)
            fila["nota"] = ";".join(notas)
            registros.append(fila)
        tabla_df = pd.DataFrame(registros).set_index(clave)
        tabla_df.index.name = clave
        tablas[tabla] = tabla_df
    if diferencias:
        raise ErrorDeTranscripcion(
            "las dos transcripciones difieren en celdas sin resolución en resoluciones.csv:\n  "
            + "\n  ".join(diferencias)
        )
    return Transcripcion(tablas=tablas, celdas_comparadas=comparadas, resueltas=resueltas)


# --- Gates de sumas y de superposición ----------------------------------------


@dataclass(frozen=True)
class FalloDeSuma:
    tabla: str
    fecha: str
    identidad: str
    impreso: float
    suma: float

    @property
    def diferencia(self) -> float:
        return self.impreso - self.suma

    def __str__(self) -> str:
        return (
            f"{self.tabla} {self.fecha}: {self.identidad}: impreso {formatear(self.impreso, 1)}, "
            f"suma de componentes {formatear(self.suma, 1)} (diferencia {formatear(self.diferencia, 1)})"
        )


def verificar_sumas(transcripcion: Transcripcion) -> dict[str, list[FalloDeSuma]]:
    """Cada total impreso contra la suma de sus componentes impresos."""
    fallos: dict[str, list[FalloDeSuma]] = {tabla: [] for tabla in TABLAS}
    for tabla, identidades in IDENTIDADES.items():
        datos = transcripcion.tablas[tabla]
        for total, componentes, tolerancia in identidades:
            for fecha, fila in datos.iterrows():
                impreso = fila[total]
                if pd.isna(impreso):
                    continue
                # Una celda en blanco es un rubro que no existía (el ahorro postal antes de
                # 1911): suma cero. Un total en blanco no se puede comprobar.
                partes = [0.0 if pd.isna(fila[c]) else float(fila[c]) for c in componentes]
                suma = round(float(sum(partes)), 6)
                if abs(impreso - suma) > tolerancia + 1e-9:
                    fallos[tabla].append(
                        FalloDeSuma(tabla, str(fecha), f"{total} = {' + '.join(componentes)}", float(impreso), suma)
                    )
    return fallos


def verificar_superposicion_1941(transcripcion: Transcripcion) -> list[str]:
    """Las filas de 1941 de la continuación tienen que repetir las de la Tabla 9."""
    tabla_9 = transcripcion.tablas["tabla_9"]
    continuacion = transcripcion.tablas["continuacion_tabla_9"]
    fallas = []
    comunes = tabla_9.index.intersection(continuacion.index)
    if len(comunes) == 0:
        return ["la continuación no comparte ninguna fecha con la Tabla 9"]
    for fecha in comunes:
        for columna_c, columna_9 in SUPERPOSICION_1941.items():
            a, b = continuacion.loc[fecha, columna_c], tabla_9.loc[fecha, columna_9]
            if pd.isna(a) and pd.isna(b):
                continue
            if pd.isna(a) or pd.isna(b) or abs(a - b) > TOLERANCIA_SUMA_MILLONES:
                fallas.append(f"{fecha} {columna_c}: continuación {a} contra Tabla 9 {b}")
    return fallas


# --- Construcción de las series -------------------------------------------------


def _mes_de(fecha: str) -> str:
    return fecha[:7]


def _nota_de(marcas: str, componente: str) -> str:
    """La nota al pie que corresponde a un componente publicado (y al total, que lo incluye)."""
    textos = []
    for marca in marcas.split(";"):
        marca = marca.strip()
        if marca in NOTAS_TABLA_9 and (marca.startswith(f"{componente}:") or componente == "total"):
            if marca.split(":")[0] in COMPONENTES_FECHAS_DE_BALANCE:
                textos.append(NOTAS_TABLA_9[marca])
    return "; ".join(textos)


def _filas(mes, fecha, serie, unidad, estado, control, cita, marcas, componentes: dict[str, float]):
    return [
        {
            "mes": mes,
            "fecha": fecha,
            "serie": serie,
            "componente": componente,
            "valor": valor,
            "unidad": unidad,
            "estado": estado,
            "control": control,
            "cita": cita,
            "nota": _nota_de(marcas, componente),
        }
        for componente, valor in componentes.items()
    ]


def construir_fechas_de_balance(transcripcion: Transcripcion) -> pd.DataFrame:
    """1892-06-30 a 1946-12-31: efectivo + depósitos a la vista ajustados + a plazo en bancos comerciales."""
    filas = []
    serie = CLAVE_DINERO_1892_1946
    tabla_9 = transcripcion.tablas["tabla_9"]
    for fecha, fila in tabla_9.iterrows():
        pagina = "34" if fecha <= "1933-12-31" else "35"
        componentes = {
            "efectivo": int(fila["efectivo"]),
            "vista_ajustados": int(fila["vista_ajustados"]),
            "plazo_comerciales": int(fila["plazo_comerciales"]),
        }
        componentes["total"] = sum(componentes.values())
        filas += _filas(
            _mes_de(fecha), fecha, serie, UNIDAD_MILLONES, ESTADO_FECHA_DE_BALANCE, "",
            CITA_BMS_1914_1941.format(pagina=pagina), fila["nota"], componentes,
        )
    continuacion = transcripcion.tablas["continuacion_tabla_9"]
    for fecha, fila in continuacion.iterrows():
        if fecha in tabla_9.index:
            continue  # 1941: la fuente es la Tabla 9; la continuación solo la confirma
        componentes = {
            "efectivo": int(fila["efectivo"]),
            "vista_ajustados": int(fila["vista_ajustados"]),
            "plazo_comerciales": int(fila["plazo_comerciales"]),
        }
        componentes["total"] = sum(componentes.values())
        filas += _filas(
            _mes_de(fecha), fecha, serie, UNIDAD_MILLONES, ESTADO_FECHA_DE_BALANCE, "",
            CITA_BMS_1941_1970_CONTINUACION, fila["nota"], componentes,
        )
    return pd.DataFrame(filas, columns=COLUMNAS_DINERO_HISTORICO)


def construir_mensual(
    transcripcion: Transcripcion, tabla: str, serie: str, fallos: list[FalloDeSuma]
) -> pd.DataFrame:
    """1947-01 a 1958-12: money stock impreso + depósitos a plazo ajustados, de la Tabla 1.1 A o B."""
    parte = "A" if tabla == "tabla_1_1_A" else "B"
    pagina = "17" if parte == "A" else "20"
    cita = CITA_BMS_1941_1970_TABLA_1_1.format(parte=parte, pagina=pagina)
    en_disputa = {f.fecha: f for f in fallos}
    filas = []
    for mes, fila in transcripcion.tablas[tabla].iterrows():
        componentes = {
            "efectivo": round(float(fila["efectivo"]), 1),
            "vista": round(float(fila["vista"]), 1),
            "money_stock": round(float(fila["total"]), 1),
            "plazo_ajustados": round(float(fila["plazo_ajustados"]), 1),
        }
        componentes["total"] = round(componentes["money_stock"] + componentes["plazo_ajustados"], 1)
        control = ""
        if mes in en_disputa:
            fallo = en_disputa[mes]
            control = (
                f"{VALOR_EN_DISPUTA}: errata de la fuente, efectivo + vista = {formatear(fallo.suma, 1)} no cuadra "
                f"con el money stock impreso {formatear(fallo.impreso, 1)} (A-D0-33)"
            )
        filas += _filas(str(mes), "", serie, UNIDAD_MILES_DE_MILLONES, ESTADO_DATO, control, cita, fila["nota"], componentes)
    return pd.DataFrame(filas, columns=COLUMNAS_DINERO_HISTORICO)


def construir_series(transcripcion: Transcripcion, fallos: dict[str, list[FalloDeSuma]]) -> dict[str, pd.DataFrame]:
    return {
        CLAVE_DINERO_1892_1946: construir_fechas_de_balance(transcripcion),
        CLAVE_DINERO_1947_1958: construir_mensual(
            transcripcion, "tabla_1_1_A", CLAVE_DINERO_1947_1958, fallos["tabla_1_1_A"]
        ),
        CLAVE_DINERO_1947_1958_SIN_AJUSTAR: construir_mensual(
            transcripcion, "tabla_1_1_B", CLAVE_DINERO_1947_1958_SIN_AJUSTAR, fallos["tabla_1_1_B"]
        ),
    }


def total_de(serie: pd.DataFrame) -> pd.Series:
    """La columna total de una serie larga, indexada por mes (o fecha de balance)."""
    totales = serie.loc[serie["componente"] == "total"]
    indice = totales["fecha"].where(totales["fecha"] != "", totales["mes"])
    return pd.Series(totales["valor"].to_numpy(dtype=float), index=indice.to_numpy(), name=serie["serie"].iloc[0])


# --- Validación contra una segunda publicación (A-D0-32) -------------------------


@dataclass
class ValidacionAnclas:
    """El gate de las fechas de balance: cifras leídas a mano de una segunda publicación."""

    serie: str
    fuente: str
    tolerancia: str
    fechas: list[str]
    cifras: int
    fuera: list[str]
    minimo: int = MINIMO_COMPARACIONES_DINERO_HISTORICO

    @property
    def ok(self) -> bool:
        return len(self.fechas) >= self.minimo and not self.fuera

    @property
    def comparados(self) -> int:
        return len(self.fechas)

    def resumen(self) -> str:
        estado = "cerró" if self.ok else "NO cerró"
        texto = (
            f"{self.serie}: gate contra {self.fuente} {estado}: {len(self.fechas)} fechas de balance, "
            f"{self.cifras} cifras, tolerancia {self.tolerancia}"
        )
        if self.fuera:
            texto += f"; fuera de tolerancia: {', '.join(self.fuera[:6])}"
            if len(self.fuera) > 6:
                texto += f" y {len(self.fuera) - 6} más"
        return texto

    def validacion(self) -> str:
        estado = "cerró" if self.ok else "no cerró"
        texto = (
            f"gate contra {self.fuente}, tolerancia {self.tolerancia}: {estado} en {len(self.fechas)} fechas "
            f"de balance ({self.cifras} cifras)"
        )
        if self.fuera:
            texto += f", {len(self.fuera)} fuera"
        return texto


def validar_anclas_hsus(transcripcion: Transcripcion) -> ValidacionAnclas:
    """Las fechas de balance contra las filas de junio del Censo, leídas a mano. Igualdad."""
    tabla_9 = transcripcion.tablas["tabla_9"]
    continuacion = transcripcion.tablas["continuacion_tabla_9"]
    cifras = 0
    fuera: list[str] = []
    fechas: list[str] = []
    for ancla in ANCLAS_HSUS_1960:
        if ancla.fecha in tabla_9.index:
            fila = tabla_9.loc[ancla.fecha]
            columnas = {c: c for c in ancla.valores}
        elif ancla.fecha in continuacion.index:
            fila = continuacion.loc[ancla.fecha]
            columnas = {c: CONTINUACION_A_TABLA_9[c] for c in ancla.valores if c in CONTINUACION_A_TABLA_9}
        else:
            fuera.append(f"{ancla.fecha} (no está en la transcripción)")
            continue
        fechas.append(ancla.fecha)
        for columna, columna_transcrita in columnas.items():
            esperado = float(ancla.valores[columna])
            observado = fila[columna_transcrita]
            cifras += 1
            if pd.isna(observado):
                fuera.append(f"{ancla.fecha} {columna} (sin dato transcrito)")
            elif abs(float(observado) - esperado) > TOLERANCIA_ANCLAS_HSUS:
                fuera.append(f"{ancla.fecha} {columna}: transcrito {float(observado):.0f}, Censo {esperado:.0f}")
    return ValidacionAnclas(
        serie=CLAVE_DINERO_1892_1946,
        fuente=f"{DESCARGA_HSUS_1960.descripcion}, {len(ANCLAS_HSUS_1960)} filas de junio leídas a mano",
        tolerancia=f"igualdad en {UNIDAD_MILLONES}",
        fechas=fechas,
        cifras=cifras,
        fuera=fuera,
    )


def leer_contraste_fred(ruta: Path) -> pd.Series:
    """El CSV de FRED de la serie del NBER: fecha, valor; los huecos vienen como '.'."""
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    if list(tabla.columns) != ["observation_date", FRED_SERIE_NBER_M14144C]:
        raise ErrorDeFuente(f"{ruta.name}: columnas inesperadas {list(tabla.columns)}")
    valores = pd.to_numeric(tabla[FRED_SERIE_NBER_M14144C].replace(".", ""), errors="coerce")
    serie = pd.Series(valores.to_numpy(), index=[fecha[:7] for fecha in tabla["observation_date"]], name="m14144c")
    return serie.dropna()


def validar_nber(serie_mensual: pd.DataFrame, contraste: pd.Series | None, nota_sin_fuente: str = "") -> Validacion:
    """El total mensual ajustado contra m14144c del NBER, mes a mes, con ±0.1."""
    fuente = f"NBER m14144c vía FRED ({FRED_SERIE_NBER_M14144C})"
    tolerancia = f"±{TOLERANCIA_NBER_MILES_DE_MILLONES} {UNIDAD_MILES_DE_MILLONES}"
    if contraste is None:
        return Validacion(
            serie=CLAVE_DINERO_1947_1958, fuente=fuente, tolerancia=tolerancia, comparados=0, fuera=[], maxima=None,
            nota=nota_sin_fuente, minimo=MINIMO_COMPARACIONES_DINERO_HISTORICO,
        )
    totales = total_de(serie_mensual)
    comunes = sorted(set(totales.index) & set(contraste.index))
    fuera = []
    maxima = 0.0
    diferencias = []
    for mes in comunes:
        diferencia = float(totales[mes]) - float(contraste[mes])
        diferencias.append(abs(diferencia))
        maxima = max(maxima, abs(diferencia))
        if abs(diferencia) > TOLERANCIA_NBER_MILES_DE_MILLONES + 1e-9:
            fuera.append(f"{mes} ({formatear(totales[mes], 1)} contra {formatear(contraste[mes], 1)})")
    nota = ""
    if comunes:
        nota = f"diferencia mediana {formatear(pd.Series(diferencias).median(), 2)}"
    return Validacion(
        serie=CLAVE_DINERO_1947_1958,
        fuente=fuente,
        tolerancia=tolerancia,
        comparados=len(comunes),
        fuera=fuera,
        maxima=maxima if comunes else None,
        minimo=MINIMO_COMPARACIONES_DINERO_HISTORICO,
        meses=comunes,
        nota=nota,
    )


# --- Fichas (serie_D0.csv) -----------------------------------------------------


def _ficha(serie: SerieD0, publicada: bool, estado: str, validacion: str, valores: pd.Series, quiebres_extra: str = "") -> dict:
    quiebres = "; ".join(f"{q.mes}: {q.texto}" for q in serie.quiebres)
    if quiebres_extra:
        quiebres = f"{quiebres}; {quiebres_extra}" if quiebres else quiebres_extra
    return {
        "serie": serie.clave,
        "nombre": serie.nombre,
        "familia": serie.familia,
        "publicada": "sí" if publicada else "no",
        "estado": estado,
        "unidad": serie.unidad,
        "convencion": serie.convencion,
        "frecuencia_nativa": serie.frecuencia_nativa,
        "ajuste_estacional": serie.ajuste,
        "emisor": serie.emisor,
        "fuente": serie.descarga.descripcion,
        "identificador": serie.identificador,
        "url": serie.descarga.url,
        "licencia": serie.descarga.licencia,
        "atribucion": serie.descarga.atribucion,
        "validacion": validacion,
        "supuestos": " ".join(serie.supuestos),
        "quiebres": quiebres,
        "primer_mes": "" if valores.empty else str(valores.index[0])[:7],
        "ultimo_mes": "" if valores.empty else str(valores.index[-1])[:7],
        "meses": len(valores),
    }


def _meses(cantidad: int) -> str:
    return "1 mes" if cantidad == 1 else f"{cantidad} meses"


def fichas(
    series: dict[str, pd.DataFrame],
    validaciones: dict[str, Validacion | ValidacionAnclas],
    fallos: dict[str, list[FalloDeSuma]],
) -> list[dict]:
    """Las tres filas de serie_D0.csv del tramo histórico."""
    hsus = validaciones[CLAVE_DINERO_1892_1946]
    nber = validaciones[CLAVE_DINERO_1947_1958]
    disputa_a = len(fallos["tabla_1_1_A"])
    disputa_b = len(fallos["tabla_1_1_B"])
    filas = [
        _ficha(
            SERIE_DINERO_1892_1946,
            hsus.ok,
            ESTADO_FECHA_DE_BALANCE if hsus.ok else NO_MEDIDO_SIN_VALIDACION,
            hsus.validacion() + "; gate de sumas: cada total impreso es la suma exacta de sus componentes",
            total_de(series[CLAVE_DINERO_1892_1946]),
        ),
        _ficha(
            SERIE_DINERO_1947_1958,
            nber.ok,
            ESTADO_DATO if nber.ok else NO_MEDIDO_SIN_VALIDACION,
            nber.validacion()
            + f"; control de sumas (±{TOLERANCIA_SUMA_MILES_DE_MILLONES}): {_meses(disputa_a)} en disputa por errata de la fuente",
            total_de(series[CLAVE_DINERO_1947_1958]),
        ),
        _ficha(
            SERIE_DINERO_1947_1958_SIN_AJUSTAR,
            False,
            NO_MEDIDO_SIN_AJUSTAR_1947_1958,
            f"sin validación externa; control de sumas (±{TOLERANCIA_SUMA_MILES_DE_MILLONES}): {_meses(disputa_b)} en disputa por errata de la fuente",
            total_de(series[CLAVE_DINERO_1947_1958_SIN_AJUSTAR]),
        ),
    ]
    return filas


def actualizar_fichas(ruta: Path, filas: list[dict]) -> None:
    """Reemplaza en serie_D0.csv las filas del tramo histórico, dejando las demás como están.

    denominador.py escribe el archivo completo en cada corrida y conserva estas
    filas (ver denominador.tabla_fichas); aquí se reemplazan en su lugar, y la
    serie sin ajustar se agrega después de la ajustada si todavía no estaba.
    """
    nuevas = {fila["serie"]: fila for fila in filas}
    if ruta.exists():
        previas = pd.read_csv(ruta, dtype=str, keep_default_na=False).to_dict("records")
    else:
        previas = []
    resultado = []
    colocadas: set[str] = set()
    claves_previas = [fila["serie"] for fila in previas]
    for posicion, fila in enumerate(previas):
        clave = fila["serie"]
        if clave not in nuevas:
            resultado.append(fila)
            continue
        resultado.append(nuevas[clave])
        colocadas.add(clave)
        siguiente = claves_previas[posicion + 1] if posicion + 1 < len(claves_previas) else ""
        if clave == CLAVE_DINERO_1947_1958 and siguiente != CLAVE_DINERO_1947_1958_SIN_AJUSTAR:
            resultado.append(nuevas[CLAVE_DINERO_1947_1958_SIN_AJUSTAR])
            colocadas.add(CLAVE_DINERO_1947_1958_SIN_AJUSTAR)
    for clave in CLAVES_DINERO_HISTORICO:
        if clave not in colocadas:
            resultado.append(nuevas[clave])
    tabla = pd.DataFrame(resultado, columns=COLUMNAS_D0_FICHAS)
    escribir_csv_determinista(tabla, ruta, COLUMNAS_D0_FICHAS, FORMATO_D0)


# --- Revisiones y changelog ------------------------------------------------------


def revisiones_de(previa: pd.DataFrame | None, nueva: pd.DataFrame) -> list[str]:
    """Cada valor publicado que cambió respecto de la corrida anterior."""
    if previa is None or previa.empty:
        return []
    clave = ["mes", "fecha", "serie", "componente"]
    anterior = previa.assign(fecha=previa["fecha"].fillna("")).set_index(clave)["valor"].astype(float)
    actual = nueva.set_index(clave)["valor"].astype(float)
    comunes = anterior.index.intersection(actual.index)
    cambios = []
    for indice in comunes:
        if abs(float(anterior[indice]) - float(actual[indice])) > EPSILON_REVISION_D0:
            cambios.append(f"{indice[0]} {indice[2]} {indice[3]}: {anterior[indice]} -> {actual[indice]}")
    for indice in anterior.index.difference(actual.index):
        cambios.append(f"{indice[0]} {indice[2]} {indice[3]}: desaparece ({anterior[indice]})")
    return cambios


@dataclass
class EntradaDineroHistorico:
    fecha_corrida: date
    descargas: list[str]
    transcripcion: list[str]
    series: list[str]
    validaciones: list[str]
    revisiones: list[str]
    notas: list[str] = field(default_factory=list)

    @property
    def titulo(self) -> str:
        return f"{self.fecha_corrida.isoformat()} · dinero histórico"

    def render(self) -> str:
        lineas = [f"## {self.titulo}", ""]

        def bloque(encabezado: str, items: list[str], vacio: str) -> None:
            if not items:
                lineas.append(f"- {encabezado}: {vacio}")
                return
            lineas.append(f"- {encabezado}:")
            lineas.extend(f"  - {item}" for item in items)

        bloque("Fuentes", self.descargas, "ninguna")
        bloque("Transcripción", self.transcripcion, "sin cotejo")
        bloque("Series", self.series, "ninguna")
        bloque("Validación", self.validaciones, "ninguna")
        bloque("Revisiones de datos históricos", self.revisiones, "ninguna")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


# --- Corrida -----------------------------------------------------------------------


def _leer(ruta: Path) -> pd.DataFrame | None:
    if not ruta.exists():
        return None
    return pd.read_csv(ruta, dtype={"mes": str, "fecha": str, "control": str, "nota": str}, keep_default_na=False)


def publicar(series: dict[str, pd.DataFrame], publicadas: set[str]) -> pd.DataFrame:
    partes = [series[clave] for clave in CLAVES_DINERO_HISTORICO if clave in publicadas]
    if not partes:
        return pd.DataFrame(columns=COLUMNAS_DINERO_HISTORICO)
    return pd.concat(partes, ignore_index=True).loc[:, COLUMNAS_DINERO_HISTORICO]


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.dinero_historico",
        description="Publica el dinero de EE.UU. antes de 1959, transcrito de las publicaciones de la Junta.",
    )
    analizador.add_argument(
        "--fecha-descarga",
        type=date.fromisoformat,
        default=date.today(),
        help="Fecha de la descarga de contraste a usar (AAAA-MM-DD). Permite rehacer una corrida anterior.",
    )
    fecha = analizador.parse_args(argv).fecha_descarga
    asegurar_directorios(DIR_CRUDO, DIR_CRUDO_PRIVADO, DIR_SERIES)
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")

    # 1. Las dos lecturas tienen que coincidir, y los totales impresos, sumar.
    try:
        transcripcion = leer_transcripcion(DIR_TRANSCRIPCION_JUNTA)
    except ErrorDeTranscripcion as error:
        print(f"TRANSCRIPCIÓN: {error}", file=sys.stderr)
        return CODIGO_GATE
    fallos = verificar_sumas(transcripcion)
    superposicion = verificar_superposicion_1941(transcripcion)
    detenciones = [str(f) for tabla in TABLAS_CON_GATE_DE_SUMAS for f in fallos[tabla]] + [
        f"superposición de 1941: {s}" for s in superposicion
    ]
    if detenciones:
        print("GATE DE SUMAS: no cerró; no se escribe nada:", file=sys.stderr)
        for linea in detenciones:
            print(f"  {linea}", file=sys.stderr)
        return CODIGO_GATE

    # 2. Las fuentes: los escaneos (copias a mano, solo para el manifiesto) y el contraste.
    manifiesto = fuentes_precios.leer_manifiesto(ARCHIVO_DINERO_HISTORICO_DESCARGAS)
    registros = []
    notas = []
    for descarga in (DESCARGA_BMS_1914_1941, DESCARGA_BMS_1941_1970, DESCARGA_HSUS_1960):
        try:
            registros.append(
                fuentes_denominador.descargar(descarga, fecha, DIR_CRUDO, DIR_CRUDO_PRIVADO, manifiesto)
            )
        except CopiaFaltante:
            notas.append(
                f"sin copia en disco de {descarga.clave}: la transcripción versionada no la necesita; "
                f"para cotejarla con el escaneo, bajar {descarga.url} como "
                f"{descarga.clave}_<AAAA-MM-DD>.{descarga.extension} en data/privado/raw"
            )
    contraste = None
    nota_contraste = ""
    try:
        registro = fuentes_denominador.descargar(
            DESCARGA_FRED_NBER_M14144C, fecha, DIR_CRUDO, DIR_CRUDO_PRIVADO, manifiesto
        )
        registros.append(registro)
        contraste = leer_contraste_fred(registro.ruta)
    except ErrorDeFuente as error:
        nota_contraste = f"no se pudo leer el contraste: {str(error)[:200]}"
        notas.append(nota_contraste)

    # 3. Las series, los gates y las fichas.
    series = construir_series(transcripcion, fallos)
    validaciones = {
        CLAVE_DINERO_1892_1946: validar_anclas_hsus(transcripcion),
        CLAVE_DINERO_1947_1958: validar_nber(series[CLAVE_DINERO_1947_1958], contraste, nota_contraste),
    }
    publicadas = {clave for clave, validacion in validaciones.items() if validacion.ok}
    tabla = publicar(series, publicadas)
    filas_fichas = fichas(series, validaciones, fallos)

    previa = _leer(ARCHIVO_DINERO_HISTORICO)
    revisiones = revisiones_de(previa, tabla)
    escribir_csv_determinista(tabla, ARCHIVO_DINERO_HISTORICO, COLUMNAS_DINERO_HISTORICO, FORMATO_D0)
    actualizar_fichas(ARCHIVO_D0_FICHAS, filas_fichas)
    if registros:
        fuentes_precios.actualizar_manifiesto(ARCHIVO_DINERO_HISTORICO_DESCARGAS, registros)

    lineas_series = []
    for fila in filas_fichas:
        if fila["publicada"] == "sí":
            lineas_series.append(
                f"{fila['nombre']}: se publica, {fila['primer_mes']} a {fila['ultimo_mes']}, "
                f"{fila['meses']} observaciones ({fila['unidad']}; {fila['convencion']}; {fila['supuestos']})"
            )
        else:
            lineas_series.append(f"{fila['nombre']}: no se publica: {fila['estado']}")
    lineas_transcripcion = [
        f"{transcripcion.celdas_comparadas} celdas leídas dos veces; {len(transcripcion.resueltas)} discrepancias, "
        "resueltas releyendo la imagen",
    ] + [f"resuelta: {r}" for r in transcripcion.resueltas]
    lineas_transcripcion += [
        f"gate de sumas: Tabla 9 y continuación, todas las identidades cuadran; superposición de 1941: igual"
    ]
    for tabla_1_1 in ("tabla_1_1_A", "tabla_1_1_B"):
        for fallo in fallos[tabla_1_1]:
            lineas_transcripcion.append(f"control de sumas, en disputa: {fallo}")
    lineas_validacion = [v.resumen() for v in validaciones.values()]
    if previa is None:
        notas.insert(0, "primera publicación de las series: no hay corrida anterior con que comparar")
    entrada = EntradaDineroHistorico(
        fecha_corrida=fecha,
        descargas=[
            f"{r.descarga.clave}: {r.url}, sha256 {r.sha256}"
            + ("" if r.fecha_descarga == fecha else f", copia del {r.fecha_descarga}")
            for r in registros
        ],
        transcripcion=lineas_transcripcion,
        series=lineas_series,
        validaciones=lineas_validacion,
        revisiones=revisiones[:40] + ([f"y {len(revisiones) - 40} más"] if len(revisiones) > 40 else []),
        notas=notas,
    )
    cambio_changelog = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Transcripción")
    for linea in lineas_transcripcion:
        print(f"  {linea}")
    print("Fuentes")
    for registro in registros:
        print(f"  {registro.linea()}")
    for nota in notas:
        print(f"  {nota}")
    print("Series")
    for linea in lineas_series:
        print(f"  {linea}")
    print("Validación")
    for linea in lineas_validacion:
        print(f"  {linea}")
    print("Salidas")
    print(f"  {ARCHIVO_DINERO_HISTORICO} ({len(tabla)} filas)")
    print(f"  {ARCHIVO_D0_FICHAS} ({len(filas_fichas)} fichas reemplazadas)")
    print(f"  {ARCHIVO_DINERO_HISTORICO_DESCARGAS}")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio_changelog else 'sin cambios'})")
    print(f"  Revisiones históricas: {len(revisiones)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
