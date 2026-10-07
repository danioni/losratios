"""Fase N0: El Numerador. La oferta de los activos, su tasa de crecimiento y su elasticidad.

Las series anuales que alimentan elnumerador.com, construidas con la disciplina
de las fases R y D0 (FUENTES.md, sección N0; SUPUESTOS.md, A-N0-1 en adelante):

- BTC: la emisión del año según el calendario del protocolo (dato) por los
  bloques observados, la oferta en circulación y su tasa de crecimiento, el
  porcentaje minado; gate contra la oferta observada de Coin Metrics (A-N0-2).
- Oro y plata: producción minera mundial del USGS (A-N0-3), control de
  consistencia contra el BGS (A-N0-4) y la cota superior de la tasa de
  crecimiento del stock (A-N0-5).
- Acciones de EE.UU.: emisión neta por sector y total, en millones de USD y
  como porcentaje del valor de mercado (Z.1, A-N0-7).
- Deuda de EE.UU.: títulos de deuda y deuda no financiera, con su variación
  (Z.1, A-N0-8). Gate de transporte del Z.1: el CSV contra el HTML (A-N0-9).
- Viviendas de EE.UU.: el parque del HVS (Tablas 7 y 7a) y de Population
  Estimates, con su tasa (A-N0-10, A-N0-11).

Cada serie dice qué mide: un flujo, un stock, una tasa de crecimiento, una
cota o una elasticidad (A-N0-1). La elasticidad de BTC es cero por construcción;
las demás esperan su prerregistro (A-N0-12).

Uso, desde senales/:

    python -m senales.numerador                     # baja, valida, escribe las salidas y el changelog
    python -m senales.numerador --fecha-descarga 2026-10-07   # rehace una corrida con los crudos de ese día

Códigos de salida: 0 todo bien · 1 una fuente de serie falló.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from senales import bitacora, fuentes_denominador, fuentes_numerador as fn, fuentes_precios
from senales.configuracion import (
    ARCHIVO_CHANGELOG,
    ARCHIVO_N0_DESCARGAS,
    ARCHIVO_N0_FICHAS,
    ARCHIVO_N0_SERIES,
    BGS_LEIDO,
    BGS_PUBLICACION,
    BGS_RECONOCIMIENTO,
    BGS_SHA256,
    BGS_URL,
    BTC_CITA_PROTOCOLO,
    BTC_FECHA_CITA_PROTOCOLO,
    BTC_INTERVALO_HALVING,
    BTC_MAXIMO,
    BTC_SATOSHIS_POR_BTC,
    BTC_SUBSIDIO_INICIAL_SAT,
    COLUMNAS_N0_FICHAS,
    COLUMNAS_N0_SERIES,
    CONTRASTE_FRED_HVS,
    CONTRASTES_Z1_HTML,
    CONTROL_DENTRO,
    CONTROL_DISPUTA,
    CONTROL_SIN_COMPARAR,
    DESCARGA_CENSO_HVS_T7,
    DESCARGA_CENSO_HVS_T7A,
    DESCARGA_CENSO_POPEST,
    DESCARGA_COIN_METRICS_OFERTA,
    DESCARGA_USGS_DS140_ORO,
    DESCARGA_USGS_DS140_PLATA,
    DESCARGA_Z1_POR_TABLA,
    DESCARGA_Z1_ZIP,
    DESCARGAS_N0_CONTRASTE,
    DESCARGAS_N0_FUENTE,
    DESCARGAS_Z1_TABLAS,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    DIR_SERIES,
    EPSILON_REVISION_N0,
    ESTADO_DATO,
    ESTADO_ESTIMACION,
    FORMATO_N0,
    FRED_ID_HVS,
    HVS_FRED_CONTROL_HASTA,
    LECTURAS_BGS,
    LECTURAS_MCS,
    METALES_ANIO_BASE,
    MINIMO_COMPARACIONES_N0,
    NO_MEDIDO_SIN_VALIDACION,
    PENDIENTES_N0,
    SECTORES_ACCIONES,
    SERIES_N0,
    TOLERANCIA_BGS_PCT,
    TOLERANCIA_BTC_CALENDARIO_PCT,
    TOLERANCIA_HVS_FRED_MILES,
    TOLERANCIA_HVS_SUMA_MILES,
    TOLERANCIA_POPEST_PCT,
    TOLERANCIA_Z1_HTML_MILES_DE_MILLONES,
    Z1_DEUDA_NO_FINANCIERA,
    Z1_PUBLICACION,
    Z1_TABLAS,
    Z1_TITULOS_DEUDA,
    Z1_ULTIMO_ANIO_ANUAL,
    LecturaBGS,
    LecturaMCS,
    SerieN0,
)
from senales.fuentes_denominador import AccesoVedado, CopiaFaltante
from senales.fuentes_fred import ErrorDeFuente
from senales.fuentes_precios import RegistroDescarga
from senales.nucleo import asegurar_directorios, escribir_csv_determinista, formatear

CODIGO_ERROR_FUENTE = 1
SAT = BTC_SATOSHIS_POR_BTC
NO_MEDIDO_SIN_CRUDO = "NO MEDIDO: sin crudo de la fuente en esta corrida"

# Qué serie del Z.1 lleva cada mnemónico, por tabla.
SERIES_POR_TABLA_Z1 = {
    "F51_1_t": tuple(flujo for _, flujo, _, _ in SECTORES_ACCIONES),
    "F51_1_s": tuple(saldo for _, _, saldo, _ in SECTORES_ACCIONES),
    "F3_s": (Z1_TITULOS_DEUDA,),
    "F3_t": ("FA894122005",),
    "D3_s": (Z1_DEUDA_NO_FINANCIERA,),
}
TABLAS_DE_FLUJO_Z1 = {"F51_1_t", "F3_t"}


# --- Crudos --------------------------------------------------------------------


@dataclass
class Crudos:
    registros: list[RegistroDescarga] = field(default_factory=list)
    rutas: dict[str, Path] = field(default_factory=dict)
    faltantes: dict[str, str] = field(default_factory=dict)


def cargar_crudos(fecha_descarga: date, sesion=None, dir_crudo: Path | None = None, dir_privado: Path | None = None, manifiesto_en: Path | None = None) -> Crudos:
    """Baja o reutiliza cada crudo. Una fuente de contraste que falla no detiene nada.

    Las tablas del Z.1 entran por el paquete ZIP: si el CSV de una tabla ya
    está en data/raw con su fecha, se reutiliza y no se pide nada; si falta, se
    baja el ZIP (que queda fuera del repositorio) y se extrae el miembro con sus
    bytes exactos (A-N0-14).
    """
    dir_crudo = dir_crudo or DIR_CRUDO
    dir_privado = dir_privado or DIR_CRUDO_PRIVADO
    manifiesto = fuentes_precios.leer_manifiesto(manifiesto_en or ARCHIVO_N0_DESCARGAS)
    crudos = Crudos()

    def bajar(descarga, obligatoria: bool) -> RegistroDescarga | None:
        try:
            registro = fuentes_denominador.descargar(descarga, fecha_descarga, dir_crudo, dir_privado, manifiesto, sesion)
        except (AccesoVedado, CopiaFaltante) as error:
            crudos.faltantes[descarga.clave] = str(error)
            return None
        except ErrorDeFuente as error:
            if obligatoria and not descarga.manual:
                raise
            crudos.faltantes[descarga.clave] = str(error)
            return None
        crudos.registros.append(registro)
        crudos.rutas[descarga.clave] = registro.ruta
        return registro

    for descarga in DESCARGAS_N0_FUENTE:
        bajar(descarga, obligatoria=True)

    faltan = [
        d for d in DESCARGAS_Z1_TABLAS
        if not fuentes_precios.ruta_cruda(d, fecha_descarga, dir_crudo, dir_privado).exists()
    ]
    if faltan:
        registro_zip = bajar(DESCARGA_Z1_ZIP, obligatoria=True)
        if registro_zip is not None:
            miembros = fn.extraer_tablas_z1(registro_zip.ruta, tuple(d.clave.removeprefix("z1_") for d in faltan))
            for descarga in faltan:
                destino = fuentes_precios.ruta_cruda(descarga, fecha_descarga, dir_crudo, dir_privado)
                contenido = miembros[descarga.clave.removeprefix("z1_")]
                destino.parent.mkdir(parents=True, exist_ok=True)
                temporal = destino.with_suffix(destino.suffix + ".tmp")
                temporal.write_bytes(contenido)
                temporal.replace(destino)
    for descarga in DESCARGAS_Z1_TABLAS:
        if fuentes_precios.ruta_cruda(descarga, fecha_descarga, dir_crudo, dir_privado).exists():
            bajar(descarga, obligatoria=True)
        else:
            crudos.faltantes.setdefault(descarga.clave, crudos.faltantes.get(DESCARGA_Z1_ZIP.clave, "sin el paquete ZIP del Z.1"))

    for descarga in DESCARGAS_N0_CONTRASTE:
        bajar(descarga, obligatoria=False)
    return crudos


# --- BTC (A-N0-2) ----------------------------------------------------------------


def subsidio_sat(altura: int) -> int:
    """GetBlockSubsidy de Bitcoin Core, en satoshis: 50 BTC que se parten en dos cada 210000 bloques."""
    halvings = altura // BTC_INTERVALO_HALVING
    if halvings >= 64:
        return 0
    return BTC_SUBSIDIO_INICIAL_SAT >> halvings


def suma_subsidios_sat(desde: int, hasta: int) -> int:
    """La suma de los subsidios de los bloques `desde` a `hasta`, inclusive, por tramos de halving."""
    total, altura = 0, desde
    while altura <= hasta:
        fin = min((altura // BTC_INTERVALO_HALVING + 1) * BTC_INTERVALO_HALVING - 1, hasta)
        total += (fin - altura + 1) * subsidio_sat(altura)
        altura = fin + 1
    return total


@dataclass
class ConstruccionBTC:
    anual: pd.DataFrame  # índice año; bloques, altura_fin, calendario, observada, oferta_fin, calendario_acumulado
    fecha_ultima: pd.Timestamp
    oferta_ultima: float
    altura_ultima: int


def construir_btc(diaria: pd.DataFrame) -> ConstruccionBTC:
    """Suma por año calendario lo que el protocolo permite y lo que Coin Metrics observó.

    `BlkCnt` acumulado es la altura del último bloque del día: no cuenta al
    génesis, cuyos 50 BTC no están en el conjunto de salidas no gastadas
    (FUENTES.md, N0.3.2). El calendario del año suma el subsidio de cada bloque
    minado ese año; el calendario acumulado suma los bloques 1 a N. Solo se
    publican los años completos (A-N0-13).
    """
    acumulado = diaria["bloques"].cumsum()
    previo = acumulado.shift(1, fill_value=0)
    calendario_dia = [
        suma_subsidios_sat(int(p) + 1, int(a)) / SAT if a > p else 0.0 for p, a in zip(previo, acumulado)
    ]
    tabla = diaria.assign(altura_fin=acumulado, calendario=calendario_dia)
    ultima = tabla.index[-1]
    anios = tabla.index.year
    completos = [a for a in sorted(set(anios)) if a < ultima.year or (ultima.month == 12 and ultima.day == 31)]
    filas = []
    for anio in completos:
        del_anio = tabla[anios == anio]
        fin = del_anio.iloc[-1]
        filas.append(
            {
                "anio": anio,
                "bloques": int(del_anio["bloques"].sum()),
                "altura_fin": int(fin["altura_fin"]),
                "calendario": float(del_anio["calendario"].sum()),
                "observada": float(del_anio["emision"].sum()),
                "oferta_fin": float(fin["oferta"]),
                "calendario_acumulado": suma_subsidios_sat(1, int(fin["altura_fin"])) / SAT,
            }
        )
    anual = pd.DataFrame(filas, columns=["anio", "bloques", "altura_fin", "calendario", "observada", "oferta_fin", "calendario_acumulado"]).set_index("anio")
    return ConstruccionBTC(anual, ultima, float(tabla["oferta"].iloc[-1]), int(acumulado.iloc[-1]))


# --- Validación ------------------------------------------------------------------------


@dataclass
class ValidacionN0:
    """El resultado de un gate o un control de N0: contra qué, cuántos años y si cerró."""

    serie: str
    fuente: str
    tolerancia: str
    comparados: int
    fuera: list[str]
    maxima: float | None
    en_disputa: list[str] = field(default_factory=list)
    dentro: list[str] = field(default_factory=list)
    nota: str = ""
    minimo: int = MINIMO_COMPARACIONES_N0
    clase: str = "gate"
    anios: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.comparados >= self.minimo and not self.fuera

    def como_control(self) -> "ValidacionN0":
        self.en_disputa = sorted(set(self.en_disputa) | {f.split(":")[0] for f in self.fuera})
        self.fuera = []
        self.clase = "control"
        return self

    def resumen(self) -> str:
        if self.comparados == 0:
            detalle = f" ({self.nota})" if self.nota else ""
            return f"{self.serie}: sin comparar contra {self.fuente}{detalle}"
        estado = "cerró" if self.ok else "NO cerró"
        texto = (
            f"{self.serie}: {self.clase} contra {self.fuente} {estado}: {self.comparados} comparaciones, "
            f"tolerancia {self.tolerancia}, diferencia máxima {formatear(self.maxima, 4)}"
        )
        if self.fuera:
            texto += f"; fuera de tolerancia: {', '.join(self.fuera[:6])}"
            if len(self.fuera) > 6:
                texto += f" y {len(self.fuera) - 6} más"
        if self.en_disputa:
            texto += f"; en disputa (control): {', '.join(self.en_disputa)}"
        if self.nota:
            texto += f"; {self.nota}"
        return texto

    def validacion(self) -> str:
        if self.comparados == 0:
            detalle = f" ({self.nota})" if self.nota else ""
            return f"sin comparar contra {self.fuente}{detalle}"
        estado = "cerró" if self.ok else "no cerró"
        texto = f"{self.clase} contra {self.fuente}, tolerancia {self.tolerancia}: {estado} en {self.comparados} comparaciones"
        if self.fuera:
            texto += f", {len(self.fuera)} fuera"
        if self.en_disputa:
            texto += f"; en disputa: {', '.join(self.en_disputa)}"
        if self.nota:
            texto += f"; {self.nota}"
        return texto


def validar_btc(construccion: ConstruccionBTC) -> ValidacionN0:
    """A-N0-2: la oferta observada nunca supera el calendario y queda a menos de 0.001 % de él."""
    fuera, maxima = [], 0.0
    for anio, fila in construccion.anual.iterrows():
        if fila["observada"] > fila["calendario"] + 1e-6:
            fuera.append(f"{anio}: la emisión observada {fila['observada']:.3f} supera el calendario {fila['calendario']:.3f}")
        if fila["oferta_fin"] > fila["calendario_acumulado"] + 1e-6:
            fuera.append(f"{anio}: la oferta {fila['oferta_fin']:.3f} supera el calendario acumulado {fila['calendario_acumulado']:.3f}")
        diferencia = (fila["calendario_acumulado"] - fila["oferta_fin"]) / fila["calendario_acumulado"] * 100.0
        maxima = max(maxima, abs(diferencia))
        if diferencia > TOLERANCIA_BTC_CALENDARIO_PCT:
            fuera.append(f"{anio}: la oferta queda {diferencia:.5f} % por debajo del calendario")
    return ValidacionN0(
        "btc",
        "el calendario del protocolo (Bitcoin Core) a la misma altura de bloque",
        f"oferta ≤ calendario y diferencia ≤ {TOLERANCIA_BTC_CALENDARIO_PCT:g} %",
        len(construccion.anual),
        fuera,
        maxima,
        anios=[str(a) for a in construccion.anual.index],
    )


# --- Oro y plata (A-N0-3, A-N0-4, A-N0-5) ----------------------------------------------


@dataclass
class SerieMetal:
    produccion: pd.Series  # año -> toneladas
    estado: dict[int, str]
    cita: dict[int, str]
    notas: dict[int, str]
    revisiones: list[str]


def construir_metal(ds140: fn.DS140, metal: str, lecturas: tuple[LecturaMCS, ...] = LECTURAS_MCS) -> SerieMetal:
    """La Data Series 140 en todo su rango y los Mineral Commodity Summaries después.

    De cada año posterior a la DS140 se toma la edición más reciente que lo
    publica como final; si solo hay estimaciones, la más reciente, marcada como
    estimación. Toda cifra que otra edición publicó distinta queda declarada
    como revisión, sin corregir nada (A-N0-3).
    """
    produccion = ds140.produccion.copy()
    estado = {int(anio): ESTADO_DATO for anio in produccion.index}
    cita = {int(anio): f"USGS Data Series 140 ({ds140.modificado})" for anio in produccion.index}
    notas: dict[int, str] = {}
    revisiones: list[str] = []
    ultimo_ds140 = int(produccion.index.max())
    por_anio: dict[int, list[LecturaMCS]] = {}
    for lectura in lecturas:
        if lectura.metal == metal:
            por_anio.setdefault(lectura.anio, []).append(lectura)

    def rotulo(lectura: LecturaMCS) -> str:
        return f"MCS {lectura.edicion}: {lectura.valor_t:g}{' (estimado)' if lectura.estimado else ''}"

    for anio in sorted(por_anio):
        lista = sorted(por_anio[anio], key=lambda l: l.edicion)
        if anio <= ultimo_ds140:
            distintas = [l for l in lista if abs(l.valor_t - float(produccion[anio])) > 1e-9]
            if distintas:
                texto = f"{anio}: se publica la DS140 ({produccion[anio]:g}); " + "; ".join(rotulo(l) for l in distintas)
                revisiones.append(texto)
                notas[anio] = "revisión declarada: " + "; ".join(rotulo(l) for l in distintas) + " (A-N0-3)"
            continue
        finales = [l for l in lista if not l.estimado]
        elegida = max(finales or lista, key=lambda l: l.edicion)
        produccion[anio] = elegida.valor_t
        estado[anio] = ESTADO_DATO if finales else ESTADO_ESTIMACION
        cita[anio] = f"USGS Mineral Commodity Summaries {elegida.edicion}" + (", estimado" if elegida.estimado else "")
        otras = [l for l in lista if l is not elegida and abs(l.valor_t - elegida.valor_t) > 1e-9]
        if otras:
            revisiones.append(f"{anio}: se publica {rotulo(elegida)}; " + "; ".join(rotulo(l) for l in otras))
            notas[anio] = "revisión declarada: " + "; ".join(rotulo(l) for l in otras) + " (A-N0-3)"
    produccion = produccion.sort_index()
    produccion.index = produccion.index.astype(int)
    produccion.index.name = "anio"
    return SerieMetal(produccion, estado, cita, notas, revisiones)


def cota_superior(produccion: pd.Series, anio_base: int = METALES_ANIO_BASE) -> pd.Series:
    """A-N0-5: producción del año sobre la producción acumulada desde el año base hasta el anterior, en %."""
    desde_base = produccion.loc[anio_base:]
    acumulado_previo = desde_base.cumsum().shift(1)
    return (desde_base / acumulado_previo * 100.0).dropna()


def validar_bgs(metal: str, produccion: pd.Series, lecturas: tuple[LecturaBGS, ...] = LECTURAS_BGS) -> ValidacionN0:
    """A-N0-4: control de consistencia contra el total mundial del BGS; marca, no decide."""
    fuera, dentro, maxima, comparados, anios = [], [], 0.0, 0, []
    for lectura in lecturas:
        if lectura.metal != metal or lectura.anio not in produccion.index:
            continue
        usgs = float(produccion[lectura.anio])
        diferencia = abs(usgs - lectura.valor_kg / 1000.0) / usgs * 100.0
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(str(lectura.anio))
        if diferencia > TOLERANCIA_BGS_PCT:
            fuera.append(f"{lectura.anio}: USGS {usgs:g} t, BGS {lectura.valor_kg / 1000.0:g} t ({diferencia:.1f} %)")
        else:
            dentro.append(str(lectura.anio))
    resultado = ValidacionN0(
        f"{metal}_produccion_mundial_t",
        "el total mundial del BGS (World Mineral Production 2020-24)",
        f"±{TOLERANCIA_BGS_PCT:g} %",
        comparados,
        fuera,
        maxima,
        anios=anios,
    ).como_control()
    resultado.dentro = dentro
    if comparados and comparados < MINIMO_COMPARACIONES_N0:
        resultado.nota = f"solo {comparados} años comparables y hacen falta {MINIMO_COMPARACIONES_N0}"
    return resultado


# --- Z.1: acciones y deuda (A-N0-7, A-N0-8, A-N0-9) ----------------------------------------


def flujos_anuales_z1(tabla: pd.DataFrame, mnemonico: str) -> pd.Series:
    """Hasta 1951 el dato anual de la Junta (fechado :Q4); desde 1952 la media de los cuatro trimestres."""
    columna = tabla[mnemonico].dropna()
    por_anio: dict[int, dict[int, float]] = {}
    for periodo, valor in columna.items():
        por_anio.setdefault(int(periodo[:4]), {})[int(periodo[-1])] = float(valor)
    resultado = {}
    for anio, trimestres in sorted(por_anio.items()):
        if anio <= Z1_ULTIMO_ANIO_ANUAL and set(trimestres) == {4}:
            resultado[anio] = trimestres[4]
        elif len(trimestres) == 4:
            resultado[anio] = sum(trimestres.values()) / 4.0
    serie = pd.Series(resultado, dtype=float)
    serie.index.name = "anio"
    return serie


def saldos_fin_de_anio_z1(tabla: pd.DataFrame, mnemonico: str) -> pd.Series:
    columna = tabla[mnemonico].dropna()
    serie = pd.Series({int(p[:4]): float(v) for p, v in columna.items() if p.endswith(":Q4")}, dtype=float)
    serie.index.name = "anio"
    return serie


def validar_z1_html(tabla: str, csv_tabla: pd.DataFrame, html: dict[str, dict[str, float | None]], mnemonicos: tuple[str, ...]) -> ValidacionN0:
    """A-N0-9: gate de transporte, el CSV del paquete contra la tabla en HTML del mismo emisor."""
    es_flujo = tabla in TABLAS_DE_FLUJO_Z1
    comparados, fuera, maxima, periodos = 0, [], 0.0, []
    for mnemonico in mnemonicos:
        del_html = html.get(mnemonico)
        if not del_html:
            fuera.append(f"{mnemonico}: no está en el HTML")
            continue
        anuales = (flujos_anuales_z1 if es_flujo else saldos_fin_de_anio_z1)(csv_tabla, mnemonico)
        for periodo, valor_html in del_html.items():
            if valor_html is None:
                continue
            if ":Q" in periodo:
                propio = csv_tabla[mnemonico].get(periodo)
            else:
                propio = anuales.get(int(periodo))
            if propio is None or pd.isna(propio):
                fuera.append(f"{mnemonico} {periodo}: sin dato en el CSV")
                continue
            diferencia = abs(float(propio) / 1000.0 - valor_html)
            comparados += 1
            maxima = max(maxima, diferencia)
            periodos.append(periodo)
            if diferencia > TOLERANCIA_Z1_HTML_MILES_DE_MILLONES + 1e-9:
                fuera.append(f"{mnemonico} {periodo}: CSV {float(propio) / 1000.0:.3f}, HTML {valor_html:g}")
    return ValidacionN0(
        f"z1_{tabla}",
        f"la tabla {tabla.replace('_', '.')} del Z.1 en HTML (mismo emisor)",
        f"±{TOLERANCIA_Z1_HTML_MILES_DE_MILLONES:g} miles de millones de USD",
        comparados,
        fuera,
        maxima,
        anios=sorted(set(periodos)),
    )


# --- Viviendas (A-N0-10, A-N0-11) --------------------------------------------------------


def crecimiento(serie: pd.Series, bases_revisadas: dict[int, float] | None = None) -> pd.Series:
    """Valor del año sobre el del año anterior, menos uno, en %. Con la base revisada donde la haya."""
    bases_revisadas = bases_revisadas or {}
    valores = serie.sort_index()
    resultado = {}
    for anio, valor in valores.items():
        previo = int(anio) - 1
        if previo not in valores.index:
            continue
        base = bases_revisadas.get(previo, float(valores[previo]))
        resultado[int(anio)] = (float(valor) / base - 1.0) * 100.0
    salida = pd.Series(resultado, dtype=float)
    salida.index.name = "anio"
    return salida


def validar_hvs_sumas(clave: str, tabla: fn.TablaHVS) -> ValidacionN0:
    """A-N0-11: gate de transporte, 'All housing units' = 'Vacant' + 'Total occupied' en cada columna."""
    fuera, maxima, comparados, anios = [], 0.0, 0, []
    for columna in tabla.columnas:
        if columna.total is None or columna.vacantes is None or columna.ocupadas is None:
            continue
        etiqueta = f"{columna.anio}{'r' if columna.revisada else ''}"
        diferencia = abs(columna.total - (columna.vacantes + columna.ocupadas))
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(etiqueta)
        if diferencia > TOLERANCIA_HVS_SUMA_MILES + 1e-9:
            fuera.append(f"{etiqueta}: {columna.total:g} contra {columna.vacantes:g} + {columna.ocupadas:g}")
    return ValidacionN0(
        clave,
        "la identidad de la propia tabla, total = vacantes + ocupadas (gate de transporte)",
        f"±{TOLERANCIA_HVS_SUMA_MILES:g} mil",
        comparados,
        fuera,
        maxima,
        anios=anios,
    )


def validar_hvs_fred(clave: str, tabla: fn.TablaHVS, fred: pd.Series) -> ValidacionN0:
    """A-N0-11: control, la Tabla 7a contra la media de los cuatro trimestres de FRED, hasta la última vintage cerrada."""
    fuera, maxima, comparados, anios, sin = [], 0.0, 0, [], []
    for anio, valor in tabla.total.items():
        trimestres = fred[fred.index.year == anio]
        if anio > HVS_FRED_CONTROL_HASTA:
            if len(trimestres) == 4:
                sin.append(f"{anio}: {trimestres.mean() - valor:+.2f}")
            continue
        if len(trimestres) != 4:
            continue
        diferencia = abs(float(trimestres.mean()) - valor)
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(str(anio))
        if diferencia > TOLERANCIA_HVS_FRED_MILES + 1e-9:
            fuera.append(f"{anio}: Tabla 7a {valor:g}, FRED {trimestres.mean():.2f}")
    resultado = ValidacionN0(
        clave,
        f"FRED {FRED_ID_HVS}, media de los cuatro trimestres, hasta {HVS_FRED_CONTROL_HASTA}",
        f"±{TOLERANCIA_HVS_FRED_MILES:g} mil",
        comparados,
        fuera,
        maxima,
        anios=anios,
    ).como_control()
    if sin:
        resultado.nota = (
            f"de {HVS_FRED_CONTROL_HASTA + 1} en adelante no se compara porque FRED no recoge la Vintage 2025; "
            "diferencia FRED menos Tabla 7a, en miles: " + ", ".join(sin)
        )
    return resultado


def validar_popest(clave: str, tabla: fn.TablaHVS, popest: fn.Popest) -> ValidacionN0:
    """A-N0-11: control, el parque al 1 de julio contra el promedio del año de la Tabla 7a, en %."""
    fuera, dentro, maxima, comparados, anios = [], [], 0.0, 0, []
    total = tabla.total
    for anio, unidades in popest.serie.items():
        if int(anio) not in total:
            continue
        diferencia = abs(float(unidades) / 1000.0 - total[int(anio)]) / total[int(anio)] * 100.0
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(str(int(anio)))
        if diferencia > TOLERANCIA_POPEST_PCT:
            fuera.append(f"{int(anio)}: Tabla 7a {total[int(anio)]:g} mil, Population Estimates {unidades / 1000.0:.3f} mil ({diferencia:.2f} %)")
        else:
            dentro.append(str(int(anio)))
    resultado = ValidacionN0(
        clave,
        "Population Estimates (parque al 1 de julio)",
        f"±{TOLERANCIA_POPEST_PCT:g} %",
        comparados,
        fuera,
        maxima,
        anios=anios,
    ).como_control()
    resultado.dentro = dentro
    return resultado


# --- Construcción -----------------------------------------------------------------------


@dataclass
class Construido:
    btc: ConstruccionBTC | None = None
    metales: dict[str, SerieMetal] = field(default_factory=dict)
    z1: dict[str, pd.DataFrame] = field(default_factory=dict)
    html_z1: dict[str, dict] = field(default_factory=dict)
    hvs7: fn.TablaHVS | None = None
    hvs7a: fn.TablaHVS | None = None
    popest: fn.Popest | None = None
    fred: pd.Series | None = None
    fecha_coin_metrics: date | None = None
    motivos: dict[str, str] = field(default_factory=dict)  # clave de descarga -> por qué falta


def construir(rutas: dict[str, Path], faltantes: dict[str, str] | None = None) -> Construido:
    """Lee cada crudo presente. Un crudo de fuente que falta deja sus series NO MEDIDO."""
    construido = Construido(motivos=dict(faltantes or {}))

    def ruta(clave: str) -> Path | None:
        return rutas.get(clave)

    if (r := ruta(DESCARGA_COIN_METRICS_OFERTA.clave)) is not None:
        construido.btc = construir_btc(fn.leer_coin_metrics_oferta(r))
        construido.fecha_coin_metrics = date.fromisoformat(r.stem[-10:])
    for metal, descarga in (("oro", DESCARGA_USGS_DS140_ORO), ("plata", DESCARGA_USGS_DS140_PLATA)):
        if (r := ruta(descarga.clave)) is not None:
            construido.metales[metal] = construir_metal(fn.leer_ds140(r, metal), metal)
    for tabla in Z1_TABLAS:
        if (r := ruta(DESCARGA_Z1_POR_TABLA[tabla].clave)) is not None:
            construido.z1[tabla] = fn.leer_tabla_z1(r, SERIES_POR_TABLA_Z1[tabla])
    for tabla, contraste in CONTRASTES_Z1_HTML.items():
        if (r := ruta(contraste.clave)) is not None:
            try:
                construido.html_z1[tabla] = fn.leer_html_z1(r)
            except ErrorDeFuente as error:
                construido.motivos[contraste.clave] = str(error)
    if (r := ruta(DESCARGA_CENSO_HVS_T7.clave)) is not None:
        construido.hvs7 = fn.leer_hvs(r)
    if (r := ruta(DESCARGA_CENSO_HVS_T7A.clave)) is not None:
        construido.hvs7a = fn.leer_hvs(r)
    if (r := ruta(DESCARGA_CENSO_POPEST.clave)) is not None:
        construido.popest = fn.leer_popest(r)
    if (r := ruta(CONTRASTE_FRED_HVS.clave)) is not None:
        try:
            construido.fred = fn.leer_fred_trimestral(r, FRED_ID_HVS)
        except ErrorDeFuente as error:
            construido.motivos[CONTRASTE_FRED_HVS.clave] = str(error)
    return construido


def validar(construido: Construido) -> dict[str, ValidacionN0]:
    """Todos los gates y controles, con las tolerancias de configuracion.py."""
    validaciones: dict[str, ValidacionN0] = {}
    if construido.btc is not None:
        validaciones["btc"] = validar_btc(construido.btc)
    for metal, serie in construido.metales.items():
        validaciones[f"bgs_{metal}"] = validar_bgs(metal, serie.produccion)
    for tabla, csv_tabla in construido.z1.items():
        if tabla not in CONTRASTES_Z1_HTML:
            continue
        html = construido.html_z1.get(tabla)
        if html is None:
            validaciones[f"z1_{tabla}"] = ValidacionN0(
                f"z1_{tabla}",
                f"la tabla {tabla.replace('_', '.')} del Z.1 en HTML",
                f"±{TOLERANCIA_Z1_HTML_MILES_DE_MILLONES:g} miles de millones de USD",
                0,
                [],
                None,
                nota="sin el HTML en esta corrida",
            )
        else:
            validaciones[f"z1_{tabla}"] = validar_z1_html(tabla, csv_tabla, html, SERIES_POR_TABLA_Z1[tabla])
    if construido.hvs7 is not None:
        validaciones["hvs7_sumas"] = validar_hvs_sumas("viviendas_eeuu_parque_hvs_miles", construido.hvs7)
    if construido.hvs7a is not None:
        validaciones["hvs7a_sumas"] = validar_hvs_sumas("viviendas_eeuu_parque_hvs_7a_miles", construido.hvs7a)
        if construido.fred is not None:
            validaciones["hvs7a_fred"] = validar_hvs_fred("viviendas_eeuu_parque_hvs_7a_miles", construido.hvs7a, construido.fred)
        else:
            validaciones["hvs7a_fred"] = ValidacionN0(
                "viviendas_eeuu_parque_hvs_7a_miles", f"FRED {FRED_ID_HVS}", f"±{TOLERANCIA_HVS_FRED_MILES:g} mil", 0, [], None,
                nota="sin el CSV de FRED en esta corrida", clase="control",
            )
        if construido.popest is not None:
            validaciones["popest"] = validar_popest("viviendas_eeuu_parque_popest_unidades", construido.hvs7a, construido.popest)
    return validaciones


# Qué validación decide la publicación de cada serie (None: solo controles o dato del protocolo).
def gates_de(clave: str) -> tuple[str, ...]:
    if clave == "btc_elasticidad_oferta":
        return ()
    if clave.startswith("btc_"):
        return ("btc",)
    if clave.startswith("acciones_eeuu_emision_neta") and clave.endswith("_musd"):
        return ("z1_F51_1_t",)
    if clave.startswith("acciones_eeuu_valor_de_mercado"):
        return ("z1_F51_1_s",)
    if clave.startswith("acciones_eeuu_emision_neta") and clave.endswith("_pct_vm"):
        return ("z1_F51_1_t", "z1_F51_1_s")
    if clave.startswith("deuda_eeuu_titulos_deuda"):
        return ("z1_F3_s",)
    if clave.startswith("deuda_eeuu_no_financiera"):
        return ("z1_D3_s",)
    if clave.startswith("viviendas_eeuu_parque_hvs_7a"):
        return ("hvs7a_sumas",)
    if clave.startswith("viviendas_eeuu_parque_hvs"):
        return ("hvs7_sumas",)
    return ()


def crudo_de(clave: str) -> tuple[str, ...]:
    """De qué descargas depende cada serie."""
    if clave == "btc_elasticidad_oferta":
        return ()
    if clave.startswith("btc_"):
        return (DESCARGA_COIN_METRICS_OFERTA.clave,)
    if clave.startswith("oro_"):
        return (DESCARGA_USGS_DS140_ORO.clave,)
    if clave.startswith("plata_"):
        return (DESCARGA_USGS_DS140_PLATA.clave,)
    if clave.startswith("acciones_eeuu_emision_neta") and clave.endswith("_musd"):
        return (DESCARGA_Z1_POR_TABLA["F51_1_t"].clave,)
    if clave.startswith("acciones_eeuu_valor_de_mercado"):
        return (DESCARGA_Z1_POR_TABLA["F51_1_s"].clave,)
    if clave.startswith("acciones_eeuu"):
        return (DESCARGA_Z1_POR_TABLA["F51_1_t"].clave, DESCARGA_Z1_POR_TABLA["F51_1_s"].clave)
    if clave.startswith("deuda_eeuu_titulos"):
        return (DESCARGA_Z1_POR_TABLA["F3_s"].clave,)
    if clave.startswith("deuda_eeuu_no_financiera"):
        return (DESCARGA_Z1_POR_TABLA["D3_s"].clave,)
    if clave.startswith("viviendas_eeuu_parque_hvs_7a"):
        return (DESCARGA_CENSO_HVS_T7A.clave,)
    if clave.startswith("viviendas_eeuu_parque_hvs"):
        return (DESCARGA_CENSO_HVS_T7.clave,)
    if clave.startswith("viviendas_eeuu_parque_popest"):
        return (DESCARGA_CENSO_POPEST.clave,)
    return ()


def estado_de_serie(serie: SerieN0, construido: Construido, validaciones: dict[str, ValidacionN0]) -> tuple[bool, str]:
    """(se publica, estado de la ficha)."""
    for clave in crudo_de(serie.clave):
        if clave in construido.motivos:
            return False, f"{NO_MEDIDO_SIN_CRUDO}: {construido.motivos[clave][:160]}"
    for gate in gates_de(serie.clave):
        validacion = validaciones.get(gate)
        if validacion is None or not validacion.ok:
            return False, NO_MEDIDO_SIN_VALIDACION
    return True, ESTADO_DATO


# --- Tablas de salida -------------------------------------------------------------------


def _fila(serie: str, anio, fecha: str, valor: float, unidad: str, estado: str, control: str = "", cita: str = "", nota: str = "") -> dict:
    return {
        "serie": serie,
        "anio": int(anio),
        "fecha": fecha,
        "valor": float(valor),
        "unidad": unidad,
        "estado": estado,
        "control": control,
        "cita": cita,
        "nota": nota,
    }


def _unidad(clave: str) -> str:
    return next(s.unidad for s in SERIES_N0 if s.clave == clave)


def filas_btc(construccion: ConstruccionBTC, fecha_descarga: date | None) -> list[dict]:
    cita = f"Coin Metrics community, descarga del {fecha_descarga}" if fecha_descarga else "Coin Metrics community"
    filas = []
    anual = construccion.anual
    for anio, fila in anual.iterrows():
        fin = f"{anio}-12-31"
        filas.append(_fila("btc_emision_calendario_btc", anio, "", fila["calendario"], "BTC", ESTADO_DATO, cita=f"calendario del protocolo (Bitcoin Core, GetBlockSubsidy; A-N0-2) por los {fila['bloques']} bloques del año según {cita}", nota=f"bloques {int(fila['altura_fin']) - int(fila['bloques']) + 1} a {int(fila['altura_fin'])}"))
        filas.append(_fila("btc_emision_observada_btc", anio, "", fila["observada"], "BTC", ESTADO_DATO, cita=cita))
        filas.append(_fila("btc_oferta_fin_de_anio_btc", anio, fin, fila["oferta_fin"], "BTC", ESTADO_DATO, cita=cita, nota=f"calendario acumulado hasta el bloque {int(fila['altura_fin'])}: {fila['calendario_acumulado']:.3f}"))
        filas.append(_fila("btc_porcentaje_minado_pct", anio, fin, fila["oferta_fin"] / BTC_MAXIMO * 100.0, _unidad("btc_porcentaje_minado_pct"), ESTADO_DATO, cita=f"{cita}; MAX_MONEY de Bitcoin Core"))
        previo = int(anio) - 1
        if previo in anual.index:
            filas.append(_fila("btc_oferta_crecimiento_pct", anio, fin, (fila["oferta_fin"] / anual.loc[previo, "oferta_fin"] - 1.0) * 100.0, "% anual", ESTADO_DATO, cita=f"{cita} (cálculo propio)"))
    fecha_ultima = construccion.fecha_ultima.strftime("%Y-%m-%d")
    filas.append(_fila("btc_oferta_a_la_fecha_btc", construccion.fecha_ultima.year, fecha_ultima, construccion.oferta_ultima, "BTC", ESTADO_DATO, cita=cita, nota=f"último día con dato; altura {construccion.altura_ultima}"))
    filas.append(_fila("btc_porcentaje_minado_a_la_fecha_pct", construccion.fecha_ultima.year, fecha_ultima, construccion.oferta_ultima / BTC_MAXIMO * 100.0, _unidad("btc_porcentaje_minado_a_la_fecha_pct"), ESTADO_DATO, cita=f"{cita}; MAX_MONEY de Bitcoin Core", nota="último día con dato"))
    return filas


def fila_elasticidad_btc() -> dict:
    return _fila(
        "btc_elasticidad_oferta",
        int(BTC_FECHA_CITA_PROTOCOLO[:4]),
        BTC_FECHA_CITA_PROTOCOLO,
        0.0,
        _unidad("btc_elasticidad_oferta"),
        ESTADO_DATO,
        cita=BTC_CITA_PROTOCOLO,
        nota="cero por construcción: el subsidio por bloque es función de la altura y de nada más (A-N0-12)",
    )


def filas_metal(metal: str, serie: SerieMetal, control: ValidacionN0 | None) -> list[dict]:
    disputa = set(control.en_disputa) if control is not None else set()
    dentro = set(control.dentro) if control is not None else set()
    cota = cota_superior(serie.produccion)
    clave_cota = f"{metal}_crecimiento_stock_cota_superior_pct"
    advertencia = next(s.nota for s in SERIES_N0 if s.clave == clave_cota)
    filas = []
    for anio, valor in serie.produccion.items():
        marca = CONTROL_DISPUTA if str(anio) in disputa else CONTROL_DENTRO if str(anio) in dentro else ""
        filas.append(_fila(f"{metal}_produccion_mundial_t", anio, "", valor, "toneladas", serie.estado[int(anio)], marca, serie.cita[int(anio)], serie.notas.get(int(anio), "")))
        if int(anio) in cota.index:
            filas.append(_fila(clave_cota, anio, "", float(cota[int(anio)]), "% anual", ESTADO_ESTIMACION, marca, f"cálculo propio sobre la producción mundial del USGS desde {METALES_ANIO_BASE}", advertencia + " (A-N0-5)"))
    return filas


def filas_acciones(z1: dict[str, pd.DataFrame], publicadas: set[str]) -> list[dict]:
    filas = []
    flujos_tabla, saldos_tabla = z1.get("F51_1_t"), z1.get("F51_1_s")
    for sector, flujo, saldo, rotulo in SECTORES_ACCIONES:
        flujos = flujos_anuales_z1(flujos_tabla, flujo) if flujos_tabla is not None else None
        saldos = saldos_fin_de_anio_z1(saldos_tabla, saldo) if saldos_tabla is not None else None
        clave_flujo = f"acciones_eeuu_emision_neta_{sector}_musd"
        clave_saldo = f"acciones_eeuu_valor_de_mercado_{sector}_musd"
        clave_pct = f"acciones_eeuu_emision_neta_{sector}_pct_vm"
        if flujos is not None and clave_flujo in publicadas:
            for anio, valor in flujos.items():
                nota = "dato anual de la Junta" if anio <= Z1_ULTIMO_ANIO_ANUAL else "media de los cuatro trimestres a tasa anual ajustada"
                filas.append(_fila(clave_flujo, anio, "", valor, "millones de USD", ESTADO_DATO, cita=f"{Z1_PUBLICACION}, F51.1.t, {flujo}.Q", nota=nota))
        if saldos is not None and clave_saldo in publicadas:
            for anio, valor in saldos.items():
                filas.append(_fila(clave_saldo, anio, f"{anio}-12-31", valor, "millones de USD", ESTADO_DATO, cita=f"{Z1_PUBLICACION}, F51.1.s, {saldo}.Q"))
        if flujos is not None and saldos is not None and clave_pct in publicadas:
            for anio, valor in flujos.items():
                previo = int(anio) - 1
                if previo in saldos.index and saldos[previo] != 0:
                    filas.append(_fila(clave_pct, anio, "", valor / float(saldos[previo]) * 100.0, "% del valor de mercado previo", ESTADO_DATO, cita=f"{Z1_PUBLICACION}, {flujo}.Q sobre {saldo}.Q de {previo}:Q4 (cálculo propio)"))
    return filas


def filas_deuda(z1: dict[str, pd.DataFrame], publicadas: set[str]) -> list[dict]:
    filas = []
    for tabla, mnemonico, clave in (("F3_s", Z1_TITULOS_DEUDA, "deuda_eeuu_titulos_deuda"), ("D3_s", Z1_DEUDA_NO_FINANCIERA, "deuda_eeuu_no_financiera")):
        if tabla not in z1:
            continue
        saldos = saldos_fin_de_anio_z1(z1[tabla], mnemonico)
        if f"{clave}_musd" in publicadas:
            for anio, valor in saldos.items():
                filas.append(_fila(f"{clave}_musd", anio, f"{anio}-12-31", valor, "millones de USD", ESTADO_DATO, cita=f"{Z1_PUBLICACION}, {tabla.replace('_', '.')}, {mnemonico}.Q"))
        if f"{clave}_variacion_pct" in publicadas:
            for anio, valor in crecimiento(saldos).items():
                filas.append(_fila(f"{clave}_variacion_pct", anio, f"{anio}-12-31", valor, "% anual", ESTADO_DATO, cita=f"{Z1_PUBLICACION}, {mnemonico}.Q (cálculo propio)"))
    return filas


def filas_viviendas(construido: Construido, validaciones: dict[str, ValidacionN0], publicadas: set[str]) -> list[dict]:
    filas = []
    if construido.hvs7 is not None:
        tabla = construido.hvs7
        total, revisados, notas = tabla.total, tabla.revisados, tabla.notas_por_anio
        serie = pd.Series(total, dtype=float)
        cita = f"Censo, HVS Tabla 7 ({tabla.fuente.removeprefix('Source: ')})"
        if "viviendas_eeuu_parque_hvs_miles" in publicadas:
            for anio, valor in serie.items():
                nota = ""
                if notas.get(int(anio)) == "*":
                    nota = "promedio de 11 meses: el HVS no relevó octubre de 2025 (cierre del gobierno federal)"
                elif notas.get(int(anio)):
                    nota = f"nota {notas[int(anio)]} de la fuente"
                if int(anio) in revisados:
                    nota = (nota + "; " if nota else "") + f"la fuente trae además {revisados[int(anio)]:g} en la base revisada, que es el denominador de la tasa de {int(anio) + 1} (A-N0-10)"
                filas.append(_fila("viviendas_eeuu_parque_hvs_miles", anio, "", valor, "miles de viviendas", ESTADO_DATO, cita=cita, nota=nota))
        if "viviendas_eeuu_parque_hvs_crecimiento_pct" in publicadas:
            for anio, valor in crecimiento(serie, revisados).items():
                nota = f"sobre la base revisada de {anio - 1}: {revisados[anio - 1]:g}" if (anio - 1) in revisados else ""
                filas.append(_fila("viviendas_eeuu_parque_hvs_crecimiento_pct", anio, "", valor, "% anual", ESTADO_DATO, cita=f"{cita} (cálculo propio)", nota=nota))
    if construido.hvs7a is not None:
        tabla = construido.hvs7a
        serie = pd.Series(tabla.total, dtype=float)
        control = validaciones.get("popest")
        disputa = set(control.en_disputa) if control is not None else set()
        dentro = set(control.dentro) if control is not None else set()
        cita = f"Censo, HVS Tabla 7a ({tabla.fuente.removeprefix('Source: ')})"
        if "viviendas_eeuu_parque_hvs_7a_miles" in publicadas:
            for anio, valor in serie.items():
                nota = "promedio de 11 meses: el HVS no relevó octubre de 2025" if tabla.notas_por_anio.get(int(anio), "").startswith("*") else ""
                marca = CONTROL_DISPUTA if str(int(anio)) in disputa else CONTROL_DENTRO if str(int(anio)) in dentro else ""
                filas.append(_fila("viviendas_eeuu_parque_hvs_7a_miles", anio, "", valor, "miles de viviendas", ESTADO_DATO, marca, cita, nota))
        if "viviendas_eeuu_parque_hvs_7a_crecimiento_pct" in publicadas:
            for anio, valor in crecimiento(serie).items():
                filas.append(_fila("viviendas_eeuu_parque_hvs_7a_crecimiento_pct", anio, "", valor, "% anual", ESTADO_DATO, cita=f"{cita} (cálculo propio)"))
    if construido.popest is not None:
        popest = construido.popest
        control = validaciones.get("popest")
        disputa = set(control.en_disputa) if control is not None else set()
        dentro = set(control.dentro) if control is not None else set()
        cita = f"Censo, Population Estimates NST-EST2025-HU ({popest.publicado})"
        if "viviendas_eeuu_parque_popest_unidades" in publicadas:
            for anio, valor in popest.serie.items():
                marca = CONTROL_DISPUTA if str(int(anio)) in disputa else CONTROL_DENTRO if str(int(anio)) in dentro else ""
                filas.append(_fila("viviendas_eeuu_parque_popest_unidades", anio, f"{int(anio)}-07-01", valor, "viviendas", ESTADO_DATO, marca, cita, f"base del 1 de abril de 2020: {popest.base:g}" if int(anio) == popest.serie.index.min() else ""))
        if "viviendas_eeuu_parque_popest_crecimiento_pct" in publicadas:
            for anio, valor in crecimiento(popest.serie).items():
                filas.append(_fila("viviendas_eeuu_parque_popest_crecimiento_pct", anio, f"{anio}-07-01", valor, "% anual", ESTADO_DATO, cita=f"{cita} (cálculo propio)"))
    return filas


def tabla_series(construido: Construido, validaciones: dict[str, ValidacionN0], publicadas: set[str]) -> pd.DataFrame:
    """Una fila por serie y año, solo de las series publicadas."""
    filas: list[dict] = []
    if construido.btc is not None:
        filas += [f for f in filas_btc(construido.btc, construido.fecha_coin_metrics) if f["serie"] in publicadas]
    if "btc_elasticidad_oferta" in publicadas:
        filas.append(fila_elasticidad_btc())
    for metal, serie in construido.metales.items():
        filas += [f for f in filas_metal(metal, serie, validaciones.get(f"bgs_{metal}")) if f["serie"] in publicadas]
    filas += filas_acciones(construido.z1, publicadas)
    filas += filas_deuda(construido.z1, publicadas)
    filas += filas_viviendas(construido, validaciones, publicadas)
    tabla = pd.DataFrame(filas, columns=COLUMNAS_N0_SERIES)
    return tabla.sort_values(["serie", "anio", "fecha"], kind="stable").reset_index(drop=True)


def _quiebres(serie: SerieN0, construido: Construido, validaciones: dict[str, ValidacionN0]) -> str:
    partes = []
    if serie.clave.startswith(("oro_", "plata_")):
        metal = serie.clave.split("_")[0]
        propia = construido.metales.get(metal)
        if propia is not None:
            partes += propia.revisiones
            partes.append("el BGS incluye estimaciones de minería artesanal que el USGS no declara (A-N0-4)")
    if serie.clave.startswith("viviendas_eeuu_parque_hvs_7a"):
        partes.append("2000-2009 en la base de la Vintage 2010, 2010-2019 en la de 2020 y 2020 en adelante en la de 2025 (nota de la Tabla 7a)")
        if (fred := validaciones.get("hvs7a_fred")) is not None and fred.nota:
            partes.append(fred.nota)
    elif serie.clave.startswith("viviendas_eeuu_parque_hvs") and construido.hvs7 is not None:
        revisados = construido.hvs7.revisados
        if revisados:
            partes.append("años con base revisada por el Censo: " + ", ".join(f"{a} ({v:g})" for a, v in sorted(revisados.items())))
        if construido.hvs7a is not None:
            comunes = sorted(set(construido.hvs7.total) & set(construido.hvs7a.total))[-3:]
            partes.append("difiere de la Tabla 7a por la base: " + ", ".join(f"{a}: {construido.hvs7.total[a]:g} contra {construido.hvs7a.total[a]:g}" for a in comunes))
    if serie.clave.startswith("acciones_eeuu_emision_neta") and serie.clave.endswith("_musd"):
        partes.append(f"hasta {Z1_ULTIMO_ANIO_ANUAL} la Junta publica un dato anual; desde {Z1_ULTIMO_ANIO_ANUAL + 1}, trimestral")
    if serie.clave == "deuda_eeuu_titulos_deuda_musd":
        partes.append("incluye los títulos emitidos por el resto del mundo en manos de residentes; el BIS queda 6.65 % por debajo en 2025-Q4 por contar solo emisores residentes (FUENTES.md, N0.7.2)")
    return "; ".join(partes)


def _validacion_de(serie: SerieN0, validaciones: dict[str, ValidacionN0]) -> str:
    claves = list(gates_de(serie.clave))
    if serie.clave.startswith("oro_"):
        claves.append("bgs_oro")
    if serie.clave.startswith("plata_"):
        claves.append("bgs_plata")
    if serie.clave.startswith("viviendas_eeuu_parque_hvs_7a"):
        claves += ["hvs7a_fred", "popest"]
    if serie.clave.startswith("viviendas_eeuu_parque_popest"):
        claves.append("popest")
    if serie.clave == "btc_elasticidad_oferta":
        return "no aplica: es una propiedad del código del protocolo, citada con su commit (A-N0-12)"
    textos = [validaciones[c].validacion() for c in claves if c in validaciones]
    if serie.clave.startswith("viviendas_eeuu_parque_hvs") and not serie.clave.startswith("viviendas_eeuu_parque_hvs_7a"):
        textos.append("comparación declarada contra la Tabla 7a: dos bases distintas por decisión del Censo")
    return "; ".join(textos) if textos else "sin validación externa"


def tabla_fichas(construido: Construido, validaciones: dict[str, ValidacionN0], series: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for serie in SERIES_N0:
        publicada, estado = estado_de_serie(serie, construido, validaciones)
        propias = series.loc[series["serie"] == serie.clave]
        estados = set(propias["estado"]) if not propias.empty else set()
        if publicada and ESTADO_ESTIMACION in estados:
            estado = ESTADO_ESTIMACION if estados == {ESTADO_ESTIMACION} else f"{ESTADO_DATO}; estimación en {', '.join(str(a) for a in propias.loc[propias['estado'] == ESTADO_ESTIMACION, 'anio'])}"
        filas.append(
            {
                "serie": serie.clave,
                "nombre": serie.nombre,
                "familia": serie.familia,
                "mide": serie.mide,
                "publicada": "sí" if publicada else "no",
                "estado": estado,
                "unidad": serie.unidad,
                "convencion": serie.convencion,
                "frecuencia": serie.frecuencia,
                "emisor": serie.emisor,
                "fuente": serie.descarga.descripcion if serie.descarga else "Bitcoin Core (código del protocolo)",
                "identificador": serie.identificador,
                "url": serie.descarga.url if serie.descarga else "https://github.com/bitcoin/bitcoin/blob/9dfde64cc3262329051fd05fffe40eecc786a99f/src/validation.cpp",
                "licencia": serie.descarga.licencia if serie.descarga else "MIT",
                "atribucion": serie.descarga.atribucion if serie.descarga else BTC_CITA_PROTOCOLO,
                "validacion": _validacion_de(serie, validaciones),
                "supuestos": " ".join(serie.supuestos),
                "quiebres": _quiebres(serie, construido, validaciones) + (f"; {serie.nota}" if serie.nota else ""),
                "primer_anio": "" if propias.empty else int(propias["anio"].min()),
                "ultimo_anio": "" if propias.empty else int(propias["anio"].max()),
                "anios": len(propias),
            }
        )
    for pendiente in PENDIENTES_N0:
        filas.append(
            {columna: "" for columna in COLUMNAS_N0_FICHAS}
            | {
                "serie": pendiente.clave,
                "nombre": pendiente.nombre,
                "familia": pendiente.familia,
                "mide": pendiente.mide,
                "publicada": "no",
                "estado": pendiente.estado,
                "fuente": pendiente.fuente,
                "supuestos": " ".join(pendiente.supuestos),
                "anios": 0,
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_N0_FICHAS)


# --- Revisiones y changelog ---------------------------------------------------------------


def _leer(ruta: Path) -> pd.DataFrame | None:
    return pd.read_csv(ruta, dtype={"fecha": str}, keep_default_na=False) if ruta.exists() else None


def _ancha(tabla: pd.DataFrame | None) -> pd.DataFrame | None:
    if tabla is None or tabla.empty:
        return None
    ancha = tabla.pivot_table(index="anio", columns="serie", values="valor", aggfunc="first")
    ancha.columns = [str(c) for c in ancha.columns]
    ancha.insert(0, "fecha", pd.to_datetime(ancha.index.astype(int).astype(str) + "-01-01"))
    return ancha.reset_index(drop=True)


def revisiones_de(previa: pd.DataFrame | None, nueva: pd.DataFrame) -> list[bitacora.Revision]:
    ancha_previa, ancha_nueva = _ancha(previa), _ancha(nueva)
    if ancha_previa is None or ancha_nueva is None:
        return []
    columnas = [c for c in ancha_nueva.columns if c != "fecha" and c in ancha_previa.columns]
    return bitacora.detectar_revisiones(ancha_previa, ancha_nueva, columnas, EPSILON_REVISION_N0)


@dataclass
class EntradaNumerador:
    fecha_corrida: date
    descargas: list[str]
    series: list[str]
    validaciones: list[str]
    revisiones: list[str]
    notas: list[str] = field(default_factory=list)

    @property
    def titulo(self) -> str:
        return f"{self.fecha_corrida.isoformat()} · numerador"

    def render(self) -> str:
        lineas = [f"## {self.titulo}", ""]

        def bloque(encabezado: str, items: list[str], vacio: str) -> None:
            if not items:
                lineas.append(f"- {encabezado}: {vacio}")
                return
            lineas.append(f"- {encabezado}:")
            lineas.extend(f"  - {item}" for item in items)

        bloque("Descargas", self.descargas, "ninguna")
        bloque("Series", self.series, "ninguna")
        bloque("Validación", self.validaciones, "ninguna")
        bloque("Revisiones de datos históricos", self.revisiones, "ninguna")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


# --- main --------------------------------------------------------------------------------


def correr(fecha_descarga: date, sesion=None) -> int:
    asegurar_directorios(DIR_CRUDO, DIR_CRUDO_PRIVADO, DIR_SERIES)
    try:
        crudos = cargar_crudos(fecha_descarga, sesion)
        construido = construir(crudos.rutas, crudos.faltantes)
    except ErrorDeFuente as error:
        print(f"ERROR DE FUENTE: {error}", file=sys.stderr)
        return CODIGO_ERROR_FUENTE
    fuentes_precios.actualizar_manifiesto(ARCHIVO_N0_DESCARGAS, crudos.registros)

    validaciones = validar(construido)
    publicadas = {s.clave for s in SERIES_N0 if estado_de_serie(s, construido, validaciones)[0]}
    series = tabla_series(construido, validaciones, publicadas)
    fichas = tabla_fichas(construido, validaciones, series)

    previa = _leer(ARCHIVO_N0_SERIES)
    revisiones = revisiones_de(previa, series)
    escribir_csv_determinista(series, ARCHIVO_N0_SERIES, COLUMNAS_N0_SERIES, FORMATO_N0)
    escribir_csv_determinista(fichas, ARCHIVO_N0_FICHAS, COLUMNAS_N0_FICHAS, FORMATO_N0)

    lineas_series = []
    for fila in fichas.itertuples():
        if fila.publicada == "sí":
            lineas_series.append(
                f"{fila.nombre}: se publica, {fila.primer_anio} a {fila.ultimo_anio}, {fila.anios} filas "
                f"({fila.mide}; {fila.unidad}; {fila.convencion}; {fila.supuestos})"
            )
        else:
            lineas_series.append(f"{fila.nombre}: no se publica: {fila.estado}")
    lineas_validacion = [v.resumen() for v in validaciones.values()]
    notas = [
        "las tablas del Z.1 se extraen del paquete ZIP con sus bytes exactos; el ZIP, el HTML del Z.1 y el CSV de FRED "
        "quedan fuera del repositorio, con su hash en el manifiesto (A-N0-14)",
        f"las cifras del BGS son lecturas a mano de {BGS_PUBLICACION} ({BGS_URL}, SHA-256 {BGS_SHA256}, leído el {BGS_LEIDO}); "
        f"\"{BGS_RECONOCIMIENTO}\"",
    ]
    if previa is None:
        notas.insert(0, "primera publicación de las series: no hay corrida anterior con que comparar")
    for clave, motivo in crudos.faltantes.items():
        notas.append(f"sin crudo de {clave}: {motivo[:200]}")
    entrada = EntradaNumerador(
        fecha_corrida=fecha_descarga,
        descargas=[
            f"{r.descarga.clave}: {r.url}, sha256 {r.sha256}"
            + (f", actualizada el {r.actualizada}" if r.actualizada else "")
            + ("" if r.fecha_descarga == fecha_descarga else f", copia del {r.fecha_descarga}")
            for r in crudos.registros
        ],
        series=lineas_series,
        validaciones=lineas_validacion,
        revisiones=[str(r) for r in revisiones[:40]] + ([f"y {len(revisiones) - 40} más"] if len(revisiones) > 40 else []),
        notas=notas,
    )
    cambio = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Descargas")
    for registro in crudos.registros:
        print(f"  {registro.linea()}")
    for clave, motivo in crudos.faltantes.items():
        print(f"  {clave}: SIN CRUDO: {motivo[:160]}")
    print("Series")
    for linea in lineas_series:
        print(f"  {linea}")
    print("Validación")
    for linea in lineas_validacion:
        print(f"  {linea}")
    print("Salidas")
    print(f"  {ARCHIVO_N0_SERIES} ({len(series)} filas)")
    print(f"  {ARCHIVO_N0_FICHAS} ({len(fichas)} filas)")
    print(f"  {ARCHIVO_N0_DESCARGAS}")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio else 'sin cambios'})")
    print("Resumen")
    print(f"  Series publicadas: {len(publicadas)} de {len(SERIES_N0)}")
    print(f"  Revisiones históricas: {len(revisiones)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.numerador",
        description="Construye y actualiza las series anuales de la fase N0 (El Numerador).",
    )
    analizador.add_argument(
        "--fecha-descarga",
        type=date.fromisoformat,
        default=date.today(),
        help="Fecha de la descarga a usar (AAAA-MM-DD). Permite rehacer una corrida anterior a partir de los crudos ya guardados.",
    )
    fecha_descarga = analizador.parse_args(argv).fecha_descarga
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")
    return correr(fecha_descarga)


if __name__ == "__main__":
    raise SystemExit(main())
