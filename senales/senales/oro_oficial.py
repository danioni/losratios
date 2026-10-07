"""Fase R, contexto histórico: el precio oficial del oro en EE.UU., 1900-03 a 1959-12.

Una serie fijada por ley, no observada en un mercado (A-R0-21). Sale de dos
normas leídas en fuentes primarias de dominio público (FUENTES.md, 4.8): el
dólar de 25,8 granos de oro de 9/10 de fino de la ley del 14 de marzo de 1900 y
el de 15 5/21 granos de la proclamación del 31 de enero de 1934. El precio por
onza troy se deriva con fracciones exactas y se publica a cuatro decimales
(A-R0-23); el mes en que cambia la norma lleva el precio anterior, como lo hace
la Junta (A-R0-22). Cada fila dice que es un precio oficial y no de mercado,
qué norma rige, si había convertibilidad (A-R0-26) y que no sirve para
métricas. Antes de 1900 queda NO MEDIDO (A-R0-24); en 1960 empieza el Pink
Sheet y no se empalma.

El gate (A-R0-25) compara el precio derivado con cifras publicadas por otras
instituciones (Tesoro, Casa de Moneda, Junta, FMI), leídas a mano, con ±0.005
USD, y exige que el primer mes a 35 sea 1934-02.

Uso, desde senales/:

    python -m senales.oro_oficial

No descarga nada: todo sale de configuracion.py. Códigos de salida: 0 todo
bien · 2 el gate no cerró (no se escribe nada).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from senales import bitacora
from senales.configuracion import (
    ANCLAS_ORO_OFICIAL,
    ARCHIVO_CHANGELOG,
    ARCHIVO_ORO_OFICIAL,
    ARCHIVO_SERIES_INFO,
    CLAVE_ORO_OFICIAL,
    COLUMNAS_ORO_OFICIAL,
    COLUMNAS_SERIES_INFO,
    CONVENCION_MES_DE_CAMBIO,
    CONVERTIBILIDAD_ORO_OFICIAL,
    DECIMALES_ORO_OFICIAL,
    DIR_SERIES,
    ESTADO_DATO,
    ETIQUETA_ORO_OFICIAL,
    FORMATO_RATIOS,
    MESES_PRECIO_ADMINISTRADO,
    MINIMO_ANCLAS_ORO_OFICIAL,
    NO_MEDIDO_ORO_ANTES_DE_1900,
    NO_MEDIDO_SIN_VALIDACION,
    NOTA_PRECIO_ADMINISTRADO,
    PRIMER_MES_A_35,
    QUIEBRE_ORO_OFICIAL,
    TOLERANCIA_ORO_OFICIAL,
    TRAMOS_ORO_OFICIAL,
    TramoOroOficial,
)
from senales.nucleo import asegurar_directorios, escribir_csv_determinista

CODIGO_GATE = 2
SUPUESTOS_ORO_OFICIAL = ("A-R0-21", "A-R0-22", "A-R0-23", "A-R0-24", "A-R0-25", "A-R0-26")
NOMBRE_ORO_OFICIAL = "Oro: precio oficial en EE.UU. (fijado por ley), 1900-03 a 1959-12"
UNIDAD_ORO_OFICIAL = "USD por onza troy de oro fino"


# --- Construcción -------------------------------------------------------------------


def meses_entre(desde: str, hasta: str) -> list[str]:
    return [str(periodo) for periodo in pd.period_range(desde, hasta, freq="M")]


def precio_publicado(tramo: TramoOroOficial) -> float:
    """El precio derivado de la fracción legal, redondeado a los decimales que se publican."""
    return round(float(tramo.precio), DECIMALES_ORO_OFICIAL)


def _convertibilidad(mes: str) -> str:
    for desde, hasta, texto in CONVERTIBILIDAD_ORO_OFICIAL:
        if desde <= mes <= hasta:
            return texto
    return ""


def _nota(mes: str) -> str:
    desde, hasta = MESES_PRECIO_ADMINISTRADO
    return NOTA_PRECIO_ADMINISTRADO if desde <= mes <= hasta else ""


def verificar_tramos(tramos: tuple[TramoOroOficial, ...] = TRAMOS_ORO_OFICIAL) -> None:
    """Los tramos se siguen sin hueco ni superposición, mes a mes."""
    for anterior, siguiente in zip(tramos, tramos[1:]):
        esperado = str(pd.Period(anterior.hasta, freq="M") + 1)
        if siguiente.desde != esperado:
            raise ValueError(
                f"los tramos del precio oficial no se siguen: {anterior.hasta} y después {siguiente.desde}"
            )


def construir_serie(tramos: tuple[TramoOroOficial, ...] = TRAMOS_ORO_OFICIAL) -> pd.DataFrame:
    """Una fila por mes, con el precio del tramo vigente y todo lo que hay que decir junto a él."""
    verificar_tramos(tramos)
    filas = []
    for tramo in tramos:
        precio = precio_publicado(tramo)
        for mes in meses_entre(tramo.desde, tramo.hasta):
            filas.append(
                {
                    "mes": mes,
                    "oro_oficial_usd_oz": precio,
                    "etiqueta": ETIQUETA_ORO_OFICIAL,
                    "norma": tramo.norma,
                    "vigente_desde": tramo.vigente_desde,
                    "convertibilidad": _convertibilidad(mes),
                    "estado": ESTADO_DATO,
                    "apto_metricas": "no",
                    "cita": tramo.cita,
                    "nota": _nota(mes),
                }
            )
    return pd.DataFrame(filas, columns=COLUMNAS_ORO_OFICIAL)


# --- Gate (A-R0-25) -------------------------------------------------------------------


@dataclass
class ValidacionOroOficial:
    anclas: int
    fuera: list[str] = field(default_factory=list)
    maxima: float = 0.0
    mes_de_cambio_ok: bool = True
    minimo: int = MINIMO_ANCLAS_ORO_OFICIAL

    @property
    def ok(self) -> bool:
        return self.anclas >= self.minimo and not self.fuera and self.mes_de_cambio_ok

    def resumen(self) -> str:
        estado = "cerró" if self.ok else "NO cerró"
        texto = (
            f"{CLAVE_ORO_OFICIAL}: gate de nivel y fecha contra cifras publicadas por el Tesoro, la Casa de Moneda, "
            f"la Junta y el FMI {estado}: {self.anclas} cifras, tolerancia ±{TOLERANCIA_ORO_OFICIAL} USD, "
            f"diferencia máxima {self.maxima:.4f}; primer mes a 35: {'1934-02' if self.mes_de_cambio_ok else 'otro'}"
        )
        if self.fuera:
            texto += f"; fuera de tolerancia: {', '.join(self.fuera)}"
        return texto

    def validacion(self) -> str:
        estado = "cerró" if self.ok else "no cerró"
        texto = (
            f"gate de nivel y fecha contra el Tesoro, la Casa de Moneda, la Junta y el FMI, tolerancia "
            f"±{TOLERANCIA_ORO_OFICIAL} USD y primer mes a 35 en {PRIMER_MES_A_35}: {estado} en {self.anclas} cifras"
        )
        if self.fuera:
            texto += f", {len(self.fuera)} fuera"
        return texto


def validar(serie: pd.DataFrame, anclas=ANCLAS_ORO_OFICIAL) -> ValidacionOroOficial:
    precios = serie.set_index("mes")["oro_oficial_usd_oz"]
    resultado = ValidacionOroOficial(anclas=0)
    for ancla in anclas:
        if ancla.mes not in precios.index:
            resultado.fuera.append(f"{ancla.mes} (fuera de la serie)")
            continue
        resultado.anclas += 1
        diferencia = abs(float(precios[ancla.mes]) - ancla.valor)
        resultado.maxima = max(resultado.maxima, diferencia)
        if diferencia > TOLERANCIA_ORO_OFICIAL + 1e-12:
            resultado.fuera.append(f"{ancla.mes}: serie {precios[ancla.mes]:.4f}, fuente {ancla.valor}")
    a_35 = precios[precios.round(2) == 35.0]
    resultado.mes_de_cambio_ok = (not a_35.empty) and a_35.index[0] == PRIMER_MES_A_35
    return resultado


# --- Ficha (series.csv de la fase R) ------------------------------------------------


def ficha(serie: pd.DataFrame, validacion: ValidacionOroOficial) -> dict:
    publicada = validacion.ok
    return {
        "serie": CLAVE_ORO_OFICIAL,
        "nombre": NOMBRE_ORO_OFICIAL,
        "publicada": "sí" if publicada else "no",
        "estado": ESTADO_DATO if publicada else NO_MEDIDO_SIN_VALIDACION,
        "unidad": UNIDAD_ORO_OFICIAL,
        "fuente": (
            "Leyes y proclamaciones de EE.UU. leídas en publicaciones oficiales (Tesoro, Casa de Moneda, Junta), "
            "en FRASER; precio derivado de la fracción legal, no descargado. "
            + ETIQUETA_ORO_OFICIAL
            + "; "
            + CONVENCION_MES_DE_CAMBIO
            + "; "
            + NOTA_PRECIO_ADMINISTRADO
            + "; "
            + NO_MEDIDO_ORO_ANTES_DE_1900
            + "; "
            + QUIEBRE_ORO_OFICIAL
        ),
        "licencia": "Dominio público (textos legales y publicaciones de agencias federales de EE.UU., inferencia; FUENTES.md 4.8)",
        "atribucion": (
            "Statutes at Large y proclamaciones de EE.UU., vía Annual Report of the Secretary of the Treasury (1900, 1934), "
            "Annual Report of the Director of the Mint (1935) y Federal Reserve Bulletin (1934, 1947); copias digitales de "
            "FRASER, Federal Reserve Bank of St. Louis. Fuera de apto_metricas."
        ),
        "validacion": validacion.validacion(),
        "supuestos": " ".join(SUPUESTOS_ORO_OFICIAL),
        "primer_mes": serie["mes"].iloc[0] if not serie.empty else "",
        "ultimo_mes": serie["mes"].iloc[-1] if not serie.empty else "",
        "meses": len(serie),
    }


def actualizar_ficha(ruta, fila: dict) -> None:
    """Reemplaza (o agrega después del oro) la fila del precio oficial en series.csv.

    ratios.py escribe el archivo completo en cada corrida y conserva esta fila
    (ver ratios.tabla_series).
    """
    previas = pd.read_csv(ruta, dtype=str, keep_default_na=False).to_dict("records") if ruta.exists() else []
    resultado = [f for f in previas if f["serie"] != CLAVE_ORO_OFICIAL]
    posicion = next((i + 1 for i, f in enumerate(resultado) if f["serie"] == "oro"), len(resultado))
    resultado.insert(posicion, fila)
    escribir_csv_determinista(pd.DataFrame(resultado, columns=COLUMNAS_SERIES_INFO), ruta, COLUMNAS_SERIES_INFO, FORMATO_RATIOS)


# --- Changelog y corrida ---------------------------------------------------------------


@dataclass
class EntradaOroOficial:
    fecha_corrida: date
    tramos: list[str]
    serie: list[str]
    validacion: list[str]
    revisiones: list[str]
    notas: list[str] = field(default_factory=list)

    @property
    def titulo(self) -> str:
        return f"{self.fecha_corrida.isoformat()} · oro oficial"

    def render(self) -> str:
        lineas = [f"## {self.titulo}", ""]

        def bloque(encabezado: str, items: list[str], vacio: str) -> None:
            if not items:
                lineas.append(f"- {encabezado}: {vacio}")
                return
            lineas.append(f"- {encabezado}:")
            lineas.extend(f"  - {item}" for item in items)

        bloque("Tramos", self.tramos, "ninguno")
        bloque("Serie", self.serie, "ninguna")
        bloque("Validación", self.validacion, "ninguna")
        bloque("Revisiones de datos históricos", self.revisiones, "ninguna")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


def revisiones_de(previa: pd.DataFrame | None, nueva: pd.DataFrame) -> list[str]:
    if previa is None or previa.empty:
        return []
    anterior = previa.set_index("mes")["oro_oficial_usd_oz"].astype(float)
    actual = nueva.set_index("mes")["oro_oficial_usd_oz"].astype(float)
    cambios = [
        f"{mes}: {anterior[mes]} -> {actual[mes]}"
        for mes in anterior.index.intersection(actual.index)
        if abs(anterior[mes] - actual[mes]) > 1e-9
    ]
    cambios += [f"{mes}: desaparece" for mes in anterior.index.difference(actual.index)]
    return cambios


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.oro_oficial",
        description="Publica el precio oficial del oro en EE.UU., 1900-03 a 1959-12, derivado de la ley.",
    )
    analizador.add_argument("--fecha-corrida", type=date.fromisoformat, default=date.today())
    fecha = analizador.parse_args(argv).fecha_corrida
    asegurar_directorios(DIR_SERIES)
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")

    serie = construir_serie()
    validacion = validar(serie)
    if not validacion.ok:
        print(f"GATE: {validacion.resumen()}", file=sys.stderr)
        print("No se escribe nada.", file=sys.stderr)
        return CODIGO_GATE

    previa = pd.read_csv(ARCHIVO_ORO_OFICIAL, dtype={"mes": str}) if ARCHIVO_ORO_OFICIAL.exists() else None
    revisiones = revisiones_de(previa, serie)
    escribir_csv_determinista(serie, ARCHIVO_ORO_OFICIAL, COLUMNAS_ORO_OFICIAL, FORMATO_RATIOS)
    fila = ficha(serie, validacion)
    actualizar_ficha(ARCHIVO_SERIES_INFO, fila)

    lineas_tramos = [
        f"{t.desde} a {t.hasta}: {precio_publicado(t):.4f} USD por onza troy = {480} ÷ ({t.granos} × {t.fino}) "
        f"= {t.precio}; {t.norma}; vigente desde {t.vigente_desde}"
        for t in TRAMOS_ORO_OFICIAL
    ]
    lineas_serie = [
        f"{NOMBRE_ORO_OFICIAL}: se publica, {fila['primer_mes']} a {fila['ultimo_mes']}, {fila['meses']} meses "
        f"({UNIDAD_ORO_OFICIAL}; {ETIQUETA_ORO_OFICIAL}; fuera de apto_metricas; {fila['supuestos']})",
        CONVENCION_MES_DE_CAMBIO,
        NO_MEDIDO_ORO_ANTES_DE_1900,
        QUIEBRE_ORO_OFICIAL,
    ]
    notas = [] if previa is not None else ["primera publicación de la serie: no hay corrida anterior con que comparar"]
    entrada = EntradaOroOficial(
        fecha_corrida=fecha,
        tramos=lineas_tramos,
        serie=lineas_serie,
        validacion=[validacion.resumen()],
        revisiones=revisiones,
        notas=notas,
    )
    cambio = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Tramos")
    for linea in lineas_tramos:
        print(f"  {linea}")
    print("Serie")
    for linea in lineas_serie:
        print(f"  {linea}")
    print("Validación")
    print(f"  {validacion.resumen()}")
    print("Salidas")
    print(f"  {ARCHIVO_ORO_OFICIAL} ({len(serie)} filas)")
    print(f"  {ARCHIVO_SERIES_INFO} (ficha {CLAVE_ORO_OFICIAL})")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio else 'sin cambios'})")
    print(f"  Revisiones históricas: {len(revisiones)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
