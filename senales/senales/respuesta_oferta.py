"""Fase N1: la respuesta observada de la oferta al precio.

Para cada par (activo, ventana) del prerregistro (SUPUESTOS.md, A-N1-1 a
A-N1-12) estima cómo covaría la variación anual de la cantidad ofrecida con la
variación anual del precio real del mismo año y de los cinco anteriores:

    y_t = α + Σ_{k=0}^{5} β_k · Δlog p_{t−k} + ε_t

con y_t = Δlog del flujo (oro, plata, viviendas de EE.UU.) o el nivel de la tasa
de emisión neta (acciones de EE.UU.), mínimos cuadrados ordinarios, errores de
Newey-West con rezago máximo 4 e intervalos del 95 % por coeficiente y para la
suma (A-N1-8). Es una asociación observada, no una elasticidad causal: precio y
cantidad se determinan juntos (A-N1-1). Nada se cambia después de ver un
resultado (A-N1-9).

Qué entra y de dónde (A-N1-2 a A-N1-6): la producción del USGS y la tasa de
emisión neta del Z.1 salen de numerador_series.csv (fase N0); el Pink Sheet
mensual, de precios_mensuales.csv (fase R); el valor unitario de la DS140, de
los xlsx versionados por N0; las viviendas terminadas del Censo, el índice de la
FHFA, el CPI-U por FRED y la tabla B.103 del Z.1 se bajan aquí, con el
robots.txt leído antes y su SHA-256 en el manifiesto (A-N1-11).

Uso, desde senales/:

    python -m senales.respuesta_oferta                           # baja, valida, estima y escribe las salidas
    python -m senales.respuesta_oferta --fecha-descarga 2026-10-14   # rehace una corrida con los crudos de ese día

Códigos de salida: 0 todo bien · 1 el gate de construcción de la B.103 no cerró
(la corrida se detiene, A-N1-5) · 2 alguna fuente no se pudo bajar o leer y sus
pares quedaron NO MEDIDO (las salidas se escriben igual).
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path
from statistics import NormalDist

import pandas as pd

from senales import bitacora, fuentes_denominador, fuentes_precios, fuentes_respuesta_oferta as fr
from senales.configuracion import (
    ARCHIVO_CHANGELOG,
    ARCHIVO_N0_DESCARGAS,
    ARCHIVO_N0_SERIES,
    ARCHIVO_N1_COEFICIENTES,
    ARCHIVO_N1_DESCARGAS,
    ARCHIVO_N1_FICHAS,
    ARCHIVO_N1_INSUMOS,
    ARCHIVO_N1_RESUMEN,
    ARCHIVO_PRECIOS,
    BLS_CPI_EXTENSIONES,
    COLUMNAS_N1_COEFICIENTES,
    COLUMNAS_N1_FICHAS,
    COLUMNAS_N1_INSUMOS,
    COLUMNAS_N1_RESUMEN,
    CONTRASTE_FRED_FHFA,
    CONTRASTE_Z1_HTML_B103,
    CONTROL_DENTRO,
    CONTROL_DISPUTA,
    CONTROL_SIN_COMPARAR,
    DESCARGA_BLS_CPI_COPIA,
    DESCARGA_CENSO_TERMINADAS,
    DESCARGA_FHFA_HPI_AT,
    DESCARGA_FRED_CPI,
    DESCARGA_USGS_DS140_ORO,
    DESCARGA_USGS_DS140_PLATA,
    DESCARGA_Z1_B103,
    DESCARGA_Z1_ZIP,
    DESCARGAS_N1_CONTRASTE,
    DESCARGAS_N1_FUENTE,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    DIR_REPORTES,
    DIR_SERIES,
    EPSILON_REVISION_N1,
    ESTADO_DATO,
    ESTADO_ESTIMACION,
    ESTADO_EVIDENCIA_INSUFICIENTE,
    ESTADO_NO_MEDIDO,
    FAMILIA_RESPUESTA,
    FHFA_AREA_EEUU,
    FILAS_FIJAS_N1,
    FORMATO_N1,
    FORMATO_N1_COEFICIENTES,
    FRED_ID_CPI,
    FRED_ID_FHFA,
    INSUMOS_N1,
    MIDE_RESPUESTA,
    MINIMO_COMPARACIONES_N1,
    N1_DECIMALES,
    N1_N_MINIMO,
    N1_NEWEY_WEST_L,
    N1_NIVEL,
    N1_REZAGO_MAXIMO,
    NO_MEDIDO_SIN_VALIDACION,
    PARES_N1,
    PRECIO_DS140,
    PRECIO_FHFA,
    PRECIO_PINK_SHEET,
    PRECIO_VALUACION,
    PREFIJO_GRAFICO_N1,
    ROTULO_FIJO_N1,
    ROTULO_NO_RESPONDE,
    ROTULO_RESPONDE,
    ROTULO_RESPUESTA_NEGATIVA,
    SERIE_TASA_ACCIONES,
    SERIE_TERMINADAS,
    TOLERANCIA_B103_IDENTIDAD_PP,
    TOLERANCIA_CPI_ANUAL,
    TOLERANCIA_CPI_MENSUAL,
    TOLERANCIA_DS140_PINK_SHEET_PCT,
    TOLERANCIA_FHFA_FRED,
    Z1_B103_SERIES,
    Z1_PUBLICACION,
    ParN1,
    SerieN1,
)
from senales.fuentes_denominador import AccesoVedado, CopiaFaltante
from senales.fuentes_fred import ErrorDeFuente
from senales.fuentes_numerador import leer_tabla_z1
from senales.fuentes_precios import RegistroDescarga
from senales.nucleo import asegurar_directorios, escribir_csv_determinista, formatear
from senales.numerador import ValidacionN0

CODIGO_GATE_DE_CONSTRUCCION = 1
CODIGO_FUENTE_FALTANTE = 2
NO_MEDIDO_SIN_CRUDO = "NO MEDIDO: sin crudo de la fuente en esta corrida"
NO_MEDIDO_SIN_INSUMO = "NO MEDIDO: sin la serie publicada que hace de insumo"
NO_MEDIDO_SIN_DEFLACTOR = "NO MEDIDO: sin validación del deflactor"
METALES = ("oro", "plata")
REZAGOS = tuple(range(N1_REZAGO_MAXIMO + 1))
Z = NormalDist().inv_cdf(N1_NIVEL)
SIN_DESVIO = "no"


class GateDeConstruccion(RuntimeError):
    """El gate de construcción de la B.103 no cerró: la lectura del CSV está mal y la corrida se detiene (A-N1-5)."""


# --- Crudos (A-N1-11) --------------------------------------------------------------------


@dataclass
class Crudos:
    registros: list[RegistroDescarga] = field(default_factory=list)
    rutas: dict[str, Path] = field(default_factory=dict)
    faltantes: dict[str, str] = field(default_factory=dict)


def _buscar_copia_bls(fecha_descarga: date, dir_privado: Path):
    """La copia a mano del BLS más reciente, con cualquiera de las extensiones admitidas."""
    candidatas = []
    for extension in BLS_CPI_EXTENSIONES:
        descarga = replace(DESCARGA_BLS_CPI_COPIA, extension=extension)
        try:
            fecha = fuentes_denominador.fecha_de_copia_manual(descarga, fecha_descarga, DIR_CRUDO, dir_privado)
        except CopiaFaltante:
            continue
        candidatas.append((fecha, descarga))
    if not candidatas:
        raise CopiaFaltante(
            f"{DESCARGA_BLS_CPI_COPIA.clave}: no hay una copia del BLS bajada a mano en data/privado/raw con fecha hasta "
            f"{fecha_descarga}. Abrir {DESCARGA_BLS_CPI_COPIA.url} en un navegador, guardar la tabla como "
            f"{DESCARGA_BLS_CPI_COPIA.clave}_<AAAA-MM-DD>.<{'|'.join(BLS_CPI_EXTENSIONES)}> ahí, y volver a correr "
            "(A-N1-6). Sin ella, el CPI y los tres pares deflactados quedan NO MEDIDO."
        )
    fecha, descarga = max(candidatas, key=lambda par: par[0])
    return fecha, descarga


def cargar_crudos(
    fecha_descarga: date,
    sesion=None,
    dir_crudo: Path | None = None,
    dir_privado: Path | None = None,
    manifiesto_en: Path | None = None,
    manifiesto_n0_en: Path | None = None,
) -> Crudos:
    """Baja o reutiliza cada crudo. Una fuente que falla deja sus pares NO MEDIDO; no detiene la corrida.

    Cada crudo que ya está en disco se verifica contra el hash del manifiesto
    antes de usarse (fuentes_precios.descargar): si no coincide, no se usa y la
    fuente queda como faltante con la razón. Los xlsx de la Data Series 140
    entran por el manifiesto de N0, que es quien los versionó (A-N0-14).
    """
    dir_crudo = dir_crudo or DIR_CRUDO
    dir_privado = dir_privado or DIR_CRUDO_PRIVADO
    manifiesto = fuentes_precios.leer_manifiesto(manifiesto_en or ARCHIVO_N1_DESCARGAS)
    manifiesto_n0 = fuentes_precios.leer_manifiesto(manifiesto_n0_en or ARCHIVO_N0_DESCARGAS)
    crudos = Crudos()

    def bajar(descarga, contra=None, fecha=None) -> RegistroDescarga | None:
        try:
            registro = fuentes_denominador.descargar(
                descarga, fecha or fecha_descarga, dir_crudo, dir_privado, manifiesto if contra is None else contra, sesion
            )
        except (AccesoVedado, CopiaFaltante, ErrorDeFuente) as error:
            crudos.faltantes[descarga.clave] = str(error)
            return None
        crudos.registros.append(registro)
        crudos.rutas[descarga.clave] = registro.ruta
        return registro

    for descarga in DESCARGAS_N1_FUENTE:
        bajar(descarga)
    for descarga in (DESCARGA_USGS_DS140_ORO, DESCARGA_USGS_DS140_PLATA):
        bajar(descarga, contra=manifiesto_n0)

    destino_b103 = fuentes_precios.ruta_cruda(DESCARGA_Z1_B103, fecha_descarga, dir_crudo, dir_privado)
    if not destino_b103.exists():
        registro_zip = bajar(DESCARGA_Z1_ZIP)
        if registro_zip is not None:
            try:
                miembro, contenido = fr.extraer_b103_del_zip(registro_zip.ruta)
            except ErrorDeFuente as error:
                crudos.faltantes[DESCARGA_Z1_B103.clave] = str(error)
            else:
                destino_b103.parent.mkdir(parents=True, exist_ok=True)
                temporal = destino_b103.with_suffix(destino_b103.suffix + ".tmp")
                temporal.write_bytes(contenido)
                temporal.replace(destino_b103)
                crudos.faltantes.pop(DESCARGA_Z1_B103.clave, None)
    if destino_b103.exists():
        bajar(DESCARGA_Z1_B103)
    else:
        crudos.faltantes.setdefault(DESCARGA_Z1_B103.clave, crudos.faltantes.get(DESCARGA_Z1_ZIP.clave, "sin el paquete ZIP del Z.1"))

    try:
        fecha_bls, descarga_bls = _buscar_copia_bls(fecha_descarga, dir_privado)
    except CopiaFaltante as error:
        crudos.faltantes[DESCARGA_BLS_CPI_COPIA.clave] = str(error)
    else:
        bajar(descarga_bls, fecha=fecha_bls)

    for descarga in DESCARGAS_N1_CONTRASTE:
        bajar(descarga)
    return crudos


# --- Promedios anuales y lecturas de lo publicado (A-N1-2) ----------------------------------


def promedio_anual(serie: pd.Series, periodos_por_anio: int) -> pd.Series:
    """El promedio simple de los períodos de un año, solo si están todos (A-N1-2)."""
    por_anio: dict[int, list[float]] = {}
    for etiqueta, valor in serie.items():
        if pd.isna(valor):
            continue
        anio = int(etiqueta.year) if isinstance(etiqueta, pd.Timestamp) else int(str(etiqueta)[:4])
        por_anio.setdefault(anio, []).append(float(valor))
    resultado = {anio: sum(valores) / periodos_por_anio for anio, valores in por_anio.items() if len(valores) == periodos_por_anio}
    salida = pd.Series(resultado, dtype=float).sort_index()
    salida.index.name = "anio"
    return salida


@dataclass(frozen=True)
class PrecioPinkSheet:
    anual: pd.Series  # año -> promedio de los doce meses
    meses_en_disputa: dict[int, list[str]]  # año -> meses "valor en disputa" (A-R0-20)
    edicion: str


def leer_pink_sheet_anual(tabla: pd.DataFrame, metal: str) -> PrecioPinkSheet:
    """El promedio anual de la serie mensual publicada por la fase R y los años con un mes en disputa."""
    columna, contraste = f"{metal}_usd_oz", f"{metal}_contraste_fmi"
    for necesaria in ("mes", columna, contraste):
        if necesaria not in tabla.columns:
            raise ErrorDeFuente(f"precios_mensuales.csv: falta la columna {necesaria}")
    meses = pd.to_datetime(tabla["mes"].astype(str) + "-01")
    valores = pd.to_numeric(tabla[columna], errors="coerce")
    serie = pd.Series(valores.to_numpy(), index=pd.DatetimeIndex(meses)).dropna()
    disputa: dict[int, list[str]] = {}
    for mes, marca in zip(meses, tabla[contraste].astype(str)):
        if marca.startswith(CONTROL_DISPUTA):
            disputa.setdefault(int(mes.year), []).append(mes.strftime("%Y-%m"))
    ediciones = sorted(set(tabla.get("pink_sheet_edicion", pd.Series(dtype=str)).astype(str)))
    return PrecioPinkSheet(promedio_anual(serie, 12), disputa, ", ".join(e for e in ediciones if e))


@dataclass(frozen=True)
class SeriePublicadaN0:
    valores: pd.Series  # año -> valor
    estado: dict[int, str]
    control: dict[int, str]
    cita: dict[int, str]
    unidad: str


def leer_serie_n0(tabla: pd.DataFrame, clave: str) -> SeriePublicadaN0:
    propias = tabla.loc[tabla["serie"] == clave]
    if propias.empty:
        raise ErrorDeFuente(f"numerador_series.csv: la serie {clave} no está publicada")
    anios = propias["anio"].astype(int)
    valores = pd.Series(pd.to_numeric(propias["valor"]).to_numpy(), index=anios.to_numpy(), dtype=float).sort_index()
    valores.index.name = "anio"
    return SeriePublicadaN0(
        valores,
        dict(zip(anios, propias["estado"].astype(str))),
        dict(zip(anios, propias["control"].astype(str))),
        dict(zip(anios, propias["cita"].astype(str))),
        str(propias["unidad"].iloc[0]),
    )


# --- Construcción -------------------------------------------------------------------------


@dataclass
class Construido:
    produccion: dict[str, SeriePublicadaN0] = field(default_factory=dict)
    tasa_acciones: SeriePublicadaN0 | None = None
    pink_sheet: dict[str, PrecioPinkSheet] = field(default_factory=dict)
    ds140: dict[str, fr.ValorUnitarioDS140] = field(default_factory=dict)
    cpi_mensual: pd.Series | None = None
    cpi_decimales: int = 0
    bls: fr.CopiaBLS | None = None
    fhfa_trimestral: pd.Series | None = None
    fhfa_decimales: int = 0
    fred_fhfa: pd.Series | None = None
    terminadas: fr.Terminadas | None = None
    b103: pd.DataFrame | None = None
    html_b103: dict | None = None
    motivos: dict[str, str] = field(default_factory=dict)  # clave de descarga o insumo -> por qué falta


def construir(
    rutas: dict[str, Path],
    faltantes: dict[str, str] | None = None,
    archivo_precios: Path | None = None,
    archivo_n0: Path | None = None,
) -> Construido:
    """Lee cada crudo presente y los insumos publicados. Lo que falta deja su motivo."""
    construido = Construido(motivos=dict(faltantes or {}))

    def ruta(clave: str) -> Path | None:
        return rutas.get(clave)

    def leer(clave: str, lector):
        try:
            return lector()
        except ErrorDeFuente as error:
            construido.motivos[clave] = str(error)
            return None

    archivo_precios = archivo_precios or ARCHIVO_PRECIOS
    archivo_n0 = archivo_n0 or ARCHIVO_N0_SERIES
    if archivo_n0.exists():
        tabla_n0 = pd.read_csv(archivo_n0, dtype={"fecha": str}, keep_default_na=False)
        for metal in METALES:
            serie = leer(f"{metal}_produccion", lambda: leer_serie_n0(tabla_n0, f"{metal}_produccion_mundial_t"))
            if serie is not None:
                construido.produccion[metal] = serie
        construido.tasa_acciones = leer("tasa_acciones", lambda: leer_serie_n0(tabla_n0, SERIE_TASA_ACCIONES))
    else:
        for clave in ("oro_produccion", "plata_produccion", "tasa_acciones"):
            construido.motivos[clave] = f"no existe {archivo_n0.name}"
    if archivo_precios.exists():
        tabla_precios = pd.read_csv(archivo_precios, dtype=str, keep_default_na=False)
        for metal in METALES:
            precio = leer(f"{metal}_pink_sheet", lambda: leer_pink_sheet_anual(tabla_precios, metal))
            if precio is not None:
                construido.pink_sheet[metal] = precio
    else:
        for metal in METALES:
            construido.motivos[f"{metal}_pink_sheet"] = f"no existe {archivo_precios.name}"

    for metal, descarga in (("oro", DESCARGA_USGS_DS140_ORO), ("plata", DESCARGA_USGS_DS140_PLATA)):
        if (r := ruta(descarga.clave)) is not None:
            valor = leer(descarga.clave, lambda: fr.leer_valor_unitario_ds140(r, metal))
            if valor is not None:
                construido.ds140[metal] = valor
    if (r := ruta(DESCARGA_FRED_CPI.clave)) is not None:
        texto = r.read_text(encoding="utf-8")
        construido.cpi_mensual = leer(DESCARGA_FRED_CPI.clave, lambda: fr.interpretar_fred(texto, FRED_ID_CPI))
        construido.cpi_decimales = fr.decimales_fred(texto, FRED_ID_CPI)
    if (r := ruta(DESCARGA_BLS_CPI_COPIA.clave)) is not None:
        construido.bls = leer(DESCARGA_BLS_CPI_COPIA.clave, lambda: fr.leer_bls(r))
    if (r := ruta(DESCARGA_FHFA_HPI_AT.clave)) is not None:
        texto = r.read_text(encoding="utf-8", errors="replace")
        construido.fhfa_trimestral = leer(DESCARGA_FHFA_HPI_AT.clave, lambda: fr.interpretar_fhfa(texto, FHFA_AREA_EEUU))
        construido.fhfa_decimales = fr.decimales_fhfa(texto, FHFA_AREA_EEUU)
    if (r := ruta(CONTRASTE_FRED_FHFA.clave)) is not None:
        construido.fred_fhfa = leer(CONTRASTE_FRED_FHFA.clave, lambda: fr.leer_fred(r, FRED_ID_FHFA))
    if (r := ruta(DESCARGA_CENSO_TERMINADAS.clave)) is not None:
        construido.terminadas = leer(DESCARGA_CENSO_TERMINADAS.clave, lambda: fr.leer_terminadas(r))
    if (r := ruta(DESCARGA_Z1_B103.clave)) is not None:
        construido.b103 = leer(DESCARGA_Z1_B103.clave, lambda: leer_tabla_z1(r, Z1_B103_SERIES))
    if (r := ruta(CONTRASTE_Z1_HTML_B103.clave)) is not None:
        construido.html_b103 = leer(CONTRASTE_Z1_HTML_B103.clave, lambda: fr.leer_html_z1_con_decimales(r))
    return construido


# --- Gates y controles (A-N1-3 a A-N1-6) ------------------------------------------------------


def validar_cpi_bls(cpi: pd.Series, bls: fr.CopiaBLS) -> tuple[ValidacionN0, ValidacionN0]:
    """A-N1-6: el CPI de FRED contra la copia a mano del BLS, mes a mes (±0.0005) y año a año (±0.001)."""
    fuera, maxima, comparados, periodos = [], 0.0, 0, []
    for mes, valor in bls.mensual.items():
        propio = cpi.get(mes)
        if propio is None or pd.isna(propio):
            continue
        diferencia = abs(float(propio) - float(valor))
        comparados += 1
        maxima = max(maxima, diferencia)
        periodos.append(mes.strftime("%Y-%m"))
        if diferencia > TOLERANCIA_CPI_MENSUAL + 1e-9:
            fuera.append(f"{mes.strftime('%Y-%m')}: FRED {propio:.3f}, BLS {valor:.3f}")
    mensual = ValidacionN0(
        "cpi_u_eeuu", f"la copia a mano del BLS ({bls.serie_id or 'serie no declarada en el archivo'}), mes a mes",
        f"±{TOLERANCIA_CPI_MENSUAL:g}", comparados, fuera, maxima, anios=sorted(set(p[:4] for p in periodos)),
    )
    if bls.anual is None:
        anual = ValidacionN0("cpi_u_eeuu_promedio_anual", "el promedio anual publicado por el BLS", f"±{TOLERANCIA_CPI_ANUAL:g}", 0, [], None, nota="la copia no trae la fila de promedio anual")
        return mensual, anual
    propio_anual = promedio_anual(cpi, 12)
    fuera, maxima, comparados, anios = [], 0.0, 0, []
    for anio, valor in bls.anual.items():
        propio = propio_anual.get(int(anio))
        if propio is None or pd.isna(propio):
            continue
        diferencia = abs(round(float(propio), 3) - float(valor))
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(str(int(anio)))
        if diferencia > TOLERANCIA_CPI_ANUAL + 1e-9:
            fuera.append(f"{int(anio)}: promedio propio {propio:.3f}, BLS {valor:.3f}")
    anual = ValidacionN0("cpi_u_eeuu_promedio_anual", "el promedio anual publicado por el BLS", f"±{TOLERANCIA_CPI_ANUAL:g}", comparados, fuera, maxima, anios=anios)
    return mensual, anual


def validar_fhfa_fred(fhfa: pd.Series, fred: pd.Series, decimales: int) -> ValidacionN0:
    """A-N1-4: gate de transporte, el CSV de la FHFA contra la copia de FRED, trimestre a trimestre."""
    tolerancia = 0.5 * 10 ** (-decimales) if decimales else TOLERANCIA_FHFA_FRED
    tolerancia = max(tolerancia, TOLERANCIA_FHFA_FRED) if decimales >= 2 else tolerancia
    fuera, maxima, comparados, periodos = [], 0.0, 0, []
    for fecha, valor in fred.items():
        periodo = f"{fecha.year}:Q{(fecha.month - 1) // 3 + 1}"
        propio = fhfa.get(periodo)
        if propio is None or pd.isna(propio):
            continue
        diferencia = abs(float(propio) - float(valor))
        comparados += 1
        maxima = max(maxima, diferencia)
        periodos.append(periodo)
        if diferencia > tolerancia + 1e-9:
            fuera.append(f"{periodo}: FHFA {propio:g}, FRED {valor:g}")
    return ValidacionN0(
        "viviendas_eeuu_precio_fhfa_at", f"FRED {FRED_ID_FHFA} (copia de la misma serie; gate de transporte)",
        f"±{tolerancia:g}", comparados, fuera, maxima, anios=sorted(set(p[:4] for p in periodos)),
    )


def tolerancia_terminadas(terminadas: fr.Terminadas) -> float:
    """A-N1-4: doce veces medio paso de la hoja mensual más medio paso de la hoja anual, por construcción."""
    return 12 * 0.5 * 10 ** (-terminadas.decimales_mensual) + 0.5 * 10 ** (-terminadas.decimales_anual)


def validar_terminadas(terminadas: fr.Terminadas) -> ValidacionN0:
    """A-N1-4: gate de transporte, la suma de los doce meses sin ajustar contra la hoja anual."""
    tolerancia = tolerancia_terminadas(terminadas)
    suma = promedio_anual(terminadas.mensual, 12) * 12
    fuera, maxima, comparados, anios = [], 0.0, 0, []
    for anio, valor in terminadas.anual.items():
        if int(anio) not in suma.index:
            continue
        diferencia = abs(float(suma[int(anio)]) - float(valor))
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(str(int(anio)))
        if diferencia > tolerancia + 1e-9:
            fuera.append(f"{int(anio)}: hoja anual {valor:g}, suma de los meses {suma[int(anio)]:.3f}")
    return ValidacionN0(
        SERIE_TERMINADAS, f"la suma de la hoja mensual sin ajustar ({terminadas.hoja_mensual}) contra la hoja anual ({terminadas.hoja_anual}), mismo archivo",
        f"±{tolerancia:g} mil (por construcción)", comparados, fuera, maxima, anios=anios,
    )


def validar_b103_identidad(b103: pd.DataFrame) -> ValidacionN0:
    """A-N1-5: gate de construcción. (LM103164105 + LM103192105) / FL102090005 × 100 reproduce FL103164106."""
    fuera, maxima, comparados, periodos = [], 0.0, 0, []
    for periodo, fila in b103.iterrows():
        acciones, fdi, patrimonio, razon = (fila[m] for m in Z1_B103_SERIES)
        if any(pd.isna(v) for v in (acciones, fdi, patrimonio, razon)) or patrimonio == 0:
            continue
        propia = (float(acciones) + float(fdi)) / float(patrimonio) * 100.0
        diferencia = abs(propia - float(razon))
        comparados += 1
        maxima = max(maxima, diferencia)
        periodos.append(periodo)
        if diferencia > TOLERANCIA_B103_IDENTIDAD_PP + 1e-9:
            fuera.append(f"{periodo}: propia {propia:.3f}, FL103164106 {razon:g}")
    return ValidacionN0(
        "acciones_eeuu_valuacion_junta_fl103164106_pct",
        "la identidad (LM103164105 + LM103192105) / FL102090005 × 100 = FL103164106 (gate de construcción del pipeline)",
        f"±{TOLERANCIA_B103_IDENTIDAD_PP:g} puntos porcentuales", comparados, fuera, maxima, anios=periodos,
    )


def validar_b103_html(b103: pd.DataFrame, html: dict[str, dict[str, tuple[float | None, int]]]) -> ValidacionN0:
    """A-N1-5 (como A-N0-9): gate de transporte, el CSV contra la tabla B.103 en HTML, medio paso de lo que publica el HTML."""
    fuera, maxima, comparados, periodos = [], 0.0, 0, []
    tolerancias = set()
    for mnemonico in Z1_B103_SERIES:
        del_html = html.get(mnemonico)
        if not del_html:
            fuera.append(f"{mnemonico}: no está en el HTML")
            continue
        es_porcentaje = mnemonico == "FL103164106"
        for periodo, (valor_html, decimales) in del_html.items():
            if valor_html is None:
                continue
            if ":Q" in periodo:
                propio = b103[mnemonico].get(periodo)
            else:
                propio = b103[mnemonico].get(f"{periodo}:Q4")  # las columnas anuales de un balance son el cuarto trimestre
            if propio is None or pd.isna(propio):
                fuera.append(f"{mnemonico} {periodo}: sin dato en el CSV")
                continue
            propio = float(propio) if es_porcentaje else float(propio) / 1000.0
            tolerancia = 0.5 * 10 ** (-decimales)
            tolerancias.add(tolerancia)
            diferencia = abs(propio - valor_html)
            comparados += 1
            maxima = max(maxima, diferencia)
            periodos.append(periodo)
            if diferencia > tolerancia + 1e-9:
                fuera.append(f"{mnemonico} {periodo}: CSV {propio:.3f}, HTML {valor_html:g}")
    return ValidacionN0(
        "z1_b103", "la tabla B.103 del Z.1 en HTML (mismo emisor; gate de transporte)",
        "medio paso de la última cifra del HTML (" + ", ".join(f"±{t:g}" for t in sorted(tolerancias)) + ")" if tolerancias else "medio paso de la última cifra del HTML",
        comparados, fuera, maxima, anios=sorted(set(periodos)),
    )


def validar_ds140_pink_sheet(metal: str, ds140: fr.ValorUnitarioDS140, pink: PrecioPinkSheet) -> ValidacionN0:
    """A-N1-3: control, el valor unitario de la DS140 en USD/oz contra el promedio anual del Pink Sheet, ±5 %."""
    fuera, dentro, maxima, comparados, anios = [], [], 0.0, 0, []
    for anio, valor in ds140.usd_por_oz.items():
        referencia = pink.anual.get(int(anio))
        if referencia is None or pd.isna(referencia) or referencia == 0:
            continue
        diferencia = abs(float(valor) - float(referencia)) / float(referencia) * 100.0
        comparados += 1
        maxima = max(maxima, diferencia)
        anios.append(str(int(anio)))
        if diferencia > TOLERANCIA_DS140_PINK_SHEET_PCT:
            fuera.append(f"{int(anio)}: DS140 {valor:.2f} USD/oz, Pink Sheet {referencia:.2f} ({diferencia:.1f} %)")
        else:
            dentro.append(str(int(anio)))
    resultado = ValidacionN0(
        f"{metal}_precio_ds140_valor_unitario_usd_oz", "el promedio anual del Pink Sheet (otra cotización del mismo metal)",
        f"±{TOLERANCIA_DS140_PINK_SHEET_PCT:g} %", comparados, fuera, maxima, anios=anios,
    ).como_control()
    resultado.dentro = dentro
    return resultado


def validar(construido: Construido) -> dict[str, ValidacionN0]:
    validaciones: dict[str, ValidacionN0] = {}
    if construido.cpi_mensual is not None and construido.bls is not None:
        validaciones["cpi_bls_mensual"], validaciones["cpi_bls_anual"] = validar_cpi_bls(construido.cpi_mensual, construido.bls)
    if construido.fhfa_trimestral is not None and construido.fred_fhfa is not None:
        validaciones["fhfa_fred"] = validar_fhfa_fred(construido.fhfa_trimestral, construido.fred_fhfa, construido.fhfa_decimales)
    if construido.terminadas is not None:
        validaciones["terminadas_sumas"] = validar_terminadas(construido.terminadas)
    if construido.b103 is not None:
        validaciones["b103_identidad"] = validar_b103_identidad(construido.b103)
        if construido.html_b103 is not None:
            validaciones["b103_html"] = validar_b103_html(construido.b103, construido.html_b103)
    for metal in METALES:
        if metal in construido.ds140 and metal in construido.pink_sheet:
            validaciones[f"ds140_pink_sheet_{metal}"] = validar_ds140_pink_sheet(metal, construido.ds140[metal], construido.pink_sheet[metal])
    return validaciones


def exigir_gate_de_construccion(validaciones: dict[str, ValidacionN0]) -> None:
    """A-N1-5: si la identidad de la B.103 no cierra en un solo trimestre, la corrida se detiene."""
    gate = validaciones.get("b103_identidad")
    if gate is not None and not gate.ok:
        raise GateDeConstruccion(
            "la lectura del CSV de la B.103 está mal: " + gate.resumen() + ". No se publica nada en esta corrida (A-N1-5)."
        )


# --- Estado de cada insumo y de cada par -----------------------------------------------------


def _gate_ok(validaciones: dict[str, ValidacionN0], clave: str) -> bool:
    validacion = validaciones.get(clave)
    return validacion is not None and validacion.ok


def estado_cpi(construido: Construido, validaciones: dict[str, ValidacionN0]) -> tuple[bool, str]:
    if construido.cpi_mensual is None:
        return False, f"{NO_MEDIDO_SIN_CRUDO}: {construido.motivos.get(DESCARGA_FRED_CPI.clave, 'sin el CSV de FRED')[:200]}"
    if construido.bls is None:
        return False, f"{NO_MEDIDO_SIN_DEFLACTOR}: {construido.motivos.get(DESCARGA_BLS_CPI_COPIA.clave, 'sin la copia a mano del BLS')[:300]}"
    if not _gate_ok(validaciones, "cpi_bls_mensual"):
        return False, f"{NO_MEDIDO_SIN_DEFLACTOR}: el gate mensual contra el BLS no cerró"
    anual = validaciones.get("cpi_bls_anual")
    if anual is not None and anual.comparados and not anual.ok:
        return False, f"{NO_MEDIDO_SIN_DEFLACTOR}: el gate anual contra el BLS no cerró"
    return True, ESTADO_DATO


def estado_insumo(clave: str, construido: Construido, validaciones: dict[str, ValidacionN0]) -> tuple[bool, str]:
    """(se usa, estado) de cada insumo de A-N1-11."""
    motivo = construido.motivos.get
    if clave == SERIE_TERMINADAS:
        if construido.terminadas is None:
            return False, f"{NO_MEDIDO_SIN_CRUDO}: {motivo(DESCARGA_CENSO_TERMINADAS.clave, '')[:200]}"
        return (True, ESTADO_DATO) if _gate_ok(validaciones, "terminadas_sumas") else (False, NO_MEDIDO_SIN_VALIDACION)
    if clave == "viviendas_eeuu_precio_fhfa_at_promedio_anual":
        if construido.fhfa_trimestral is None:
            return False, f"{NO_MEDIDO_SIN_CRUDO}: {motivo(DESCARGA_FHFA_HPI_AT.clave, '')[:200]}"
        return (True, ESTADO_DATO) if _gate_ok(validaciones, "fhfa_fred") else (False, NO_MEDIDO_SIN_VALIDACION)
    if clave == "cpi_u_eeuu_promedio_anual":
        return estado_cpi(construido, validaciones)
    if clave.endswith("_precio_pink_sheet_promedio_anual_usd_oz"):
        metal = clave.split("_")[0]
        return (True, ESTADO_DATO) if metal in construido.pink_sheet else (False, f"{NO_MEDIDO_SIN_INSUMO}: {motivo(f'{metal}_pink_sheet', '')[:200]}")
    if clave.endswith("_precio_ds140_valor_unitario_usd_oz"):
        metal = clave.split("_")[0]
        descarga = DESCARGA_USGS_DS140_ORO if metal == "oro" else DESCARGA_USGS_DS140_PLATA
        return (True, ESTADO_DATO) if metal in construido.ds140 else (False, f"{NO_MEDIDO_SIN_CRUDO}: {motivo(descarga.clave, '')[:200]}")
    if clave == "acciones_eeuu_valuacion_no_financieras_pct":
        if construido.b103 is None:
            return False, f"{NO_MEDIDO_SIN_CRUDO}: {motivo(DESCARGA_Z1_B103.clave, '')[:200]}"
        if not _gate_ok(validaciones, "b103_identidad"):
            return False, "NO MEDIDO: el gate de construcción de la B.103 no cerró"
        return (True, ESTADO_DATO) if _gate_ok(validaciones, "b103_html") else (False, NO_MEDIDO_SIN_VALIDACION)
    if clave == "acciones_eeuu_valuacion_junta_fl103164106_pct":
        if construido.b103 is None:
            return False, f"{NO_MEDIDO_SIN_CRUDO}: {motivo(DESCARGA_Z1_B103.clave, '')[:200]}"
        return (False, "gate de construcción: cerró" if _gate_ok(validaciones, "b103_identidad") else "gate de construcción: NO cerró")
    raise KeyError(clave)


def estado_cantidad(par: ParN1, construido: Construido) -> tuple[bool, str]:
    if par.activo_clave in METALES:
        if par.activo_clave in construido.produccion:
            return True, ESTADO_DATO
        return False, f"{NO_MEDIDO_SIN_INSUMO}: {construido.motivos.get(f'{par.activo_clave}_produccion', '')[:200]}"
    if par.activo_clave == "acciones":
        if construido.tasa_acciones is not None:
            return True, ESTADO_DATO
        return False, f"{NO_MEDIDO_SIN_INSUMO}: {construido.motivos.get('tasa_acciones', '')[:200]}"
    return (True, ESTADO_DATO) if construido.terminadas is not None else (False, f"{NO_MEDIDO_SIN_CRUDO}: {construido.motivos.get(DESCARGA_CENSO_TERMINADAS.clave, '')[:200]}")


def motivo_no_medido(par: ParN1, construido: Construido, validaciones: dict[str, ValidacionN0]) -> str | None:
    """Por qué un par no se calcula, o None si todos sus insumos están y sus gates cerraron."""
    usable, estado = estado_cantidad(par, construido)
    if not usable:
        return estado
    if par.activo_clave == "viviendas":
        usable, estado = estado_insumo(SERIE_TERMINADAS, construido, validaciones)
        if not usable:
            return estado
    claves_precio = {
        PRECIO_PINK_SHEET: f"{par.activo_clave}_precio_pink_sheet_promedio_anual_usd_oz",
        PRECIO_DS140: f"{par.activo_clave}_precio_ds140_valor_unitario_usd_oz",
        PRECIO_FHFA: "viviendas_eeuu_precio_fhfa_at_promedio_anual",
        PRECIO_VALUACION: "acciones_eeuu_valuacion_no_financieras_pct",
    }
    usable, estado = estado_insumo(claves_precio[par.precio], construido, validaciones)
    if not usable:
        return estado
    if par.deflactar:
        usable, estado = estado_cpi(construido, validaciones)
        if not usable:
            return estado
    return None


# --- Insumos por par y año (A-N1-2, A-N1-8) -----------------------------------------------------


@dataclass(frozen=True)
class NivelesPar:
    cantidad: pd.Series  # año -> cantidad (o tasa, en fracción, en las acciones)
    precio: pd.Series  # año -> precio nominal (o la valuación)
    cpi: pd.Series | None  # año -> CPI promedio anual, si se deflacta
    unidad_cantidad: str
    unidad_precio: str
    estado_cantidad: dict[int, str]
    control_cantidad: dict[int, str]  # año -> marca del control de N0 ("valor en disputa", ...)
    control_precio: dict[int, str]  # año -> marca de control del precio
    motivo_control_precio: dict[int, str]
    cita_cantidad: dict[int, str]
    cita_precio: str


def niveles_de(par: ParN1, construido: Construido, validaciones: dict[str, ValidacionN0]) -> NivelesPar:
    """Las series anuales en niveles de un par, con las marcas de los controles que las afectan."""
    control_precio: dict[int, str] = {}
    motivo_precio: dict[int, str] = {}
    if par.activo_clave in METALES:
        propia = construido.produccion[par.activo_clave]
        cantidad, unidad_cantidad = propia.valores, "toneladas"
        estado_cantidad, control_cantidad, cita_cantidad = propia.estado, propia.control, propia.cita
        if par.precio == PRECIO_PINK_SHEET:
            pink = construido.pink_sheet[par.activo_clave]
            precio, unidad_precio = pink.anual, "USD por onza troy"
            for anio, meses in pink.meses_en_disputa.items():
                control_precio[anio] = CONTROL_DISPUTA
                motivo_precio[anio] = f"mes en disputa con el FMI (A-R0-20): {', '.join(meses)}"
            cita_precio = f"Pink Sheet (fase R, precios_mensuales.csv, ediciones {pink.edicion}), promedio de los doce meses (cálculo propio)"
        else:
            ds140 = construido.ds140[par.activo_clave]
            precio, unidad_precio = ds140.usd_por_oz, "USD por onza troy"
            control = validaciones.get(f"ds140_pink_sheet_{par.activo_clave}")
            if control is not None:
                for anio in control.anios:
                    control_precio[int(anio)] = CONTROL_DISPUTA if anio in control.en_disputa else CONTROL_DENTRO
                for anio in control.en_disputa:
                    motivo_precio[int(anio)] = f"DS140 contra Pink Sheet fuera de ±{TOLERANCIA_DS140_PINK_SHEET_PCT:g} % (A-N1-3)"
            cita_precio = f"USGS Data Series 140 ({ds140.modificado}), columna {ds140.encabezado} dividida por 32150.7 oz/t (cálculo propio)"
    elif par.activo_clave == "viviendas":
        terminadas = construido.terminadas
        cantidad, unidad_cantidad = terminadas.anual, "miles de viviendas"
        estado_cantidad = {int(a): ESTADO_DATO for a in cantidad.index}
        control_cantidad = {}
        cita_cantidad = {int(a): f"Censo, New Residential Construction, viviendas terminadas, hoja {terminadas.hoja_anual}" + (f" ({terminadas.fuente})" if terminadas.fuente else "") for a in cantidad.index}
        precio, unidad_precio = promedio_anual(construido.fhfa_trimestral, 4), "índice, 1980 Q1 = 100"
        cita_precio = "FHFA, índice all-transactions, EE.UU., promedio de los cuatro trimestres (cálculo propio)"
    else:
        propia = construido.tasa_acciones
        cantidad, unidad_cantidad = propia.valores / 100.0, "fracción del valor de mercado de fin del año anterior"
        estado_cantidad, control_cantidad, cita_cantidad = propia.estado, propia.control, propia.cita
        b103 = construido.b103
        razon = (b103["LM103164105"] / b103["FL102090005"] * 100.0).dropna()
        precio, unidad_precio = promedio_anual(razon, 4), "% del patrimonio neto"
        cita_precio = f"{Z1_PUBLICACION}, B.103: LM103164105.Q / FL102090005.Q × 100, promedio de los cuatro trimestres (cálculo propio); sin inversión extranjera directa y sin deflactar (A-N1-5)"
    cpi = promedio_anual(construido.cpi_mensual, 12) if par.deflactar else None
    return NivelesPar(cantidad, precio, cpi, unidad_cantidad, unidad_precio, estado_cantidad, control_cantidad, control_precio, motivo_precio, cita_cantidad, cita_precio)


def _log(valor: float | None) -> float | None:
    return math.log(valor) if valor is not None and not pd.isna(valor) and valor > 0 else None


def insumos_de(par: ParN1, niveles: NivelesPar) -> pd.DataFrame:
    """Una fila por año, del año anterior al inicio al fin: niveles, variaciones y marcas.

    La ventana acota las variables en diferencias: Δlog p_s existe para s en
    [inicio, fin] si hay nivel en s y en s−1 y ninguno de los dos está marcado en
    disputa; y_t, para t en [inicio, fin], con la misma regla sobre la cantidad
    (A-N1-8). Lo marcado por un control no entra a ninguna métrica (CLAUDE.md).
    """
    filas = []
    for anio in range(par.inicio - 1, par.fin + 1):
        cantidad = niveles.cantidad.get(anio)
        cantidad = None if cantidad is None or pd.isna(cantidad) else float(cantidad)
        precio = niveles.precio.get(anio)
        precio = None if precio is None or pd.isna(precio) else float(precio)
        cpi = None
        if niveles.cpi is not None:
            cpi = niveles.cpi.get(anio)
            cpi = None if cpi is None or pd.isna(cpi) else float(cpi)
        real = (precio / cpi) if (par.deflactar and precio is not None and cpi is not None) else (precio if not par.deflactar else None)
        marcas, motivos = [], []
        if niveles.control_cantidad.get(anio, "").startswith(CONTROL_DISPUTA):
            marcas.append(f"cantidad: {niveles.control_cantidad[anio]}")
            motivos.append("la cantidad del año está en disputa (control de N0, A-N0-4)")
        if niveles.control_precio.get(anio):
            marcas.append(f"precio: {niveles.control_precio[anio]}")
            if niveles.control_precio[anio] == CONTROL_DISPUTA:
                motivos.append(niveles.motivo_control_precio.get(anio, "el precio del año está en disputa"))
        filas.append(
            {
                "activo": par.activo, "ventana": par.ventana, "anio": anio,
                "cantidad": cantidad, "unidad_cantidad": niveles.unidad_cantidad,
                "estado_cantidad": niveles.estado_cantidad.get(anio, "") if cantidad is not None else "",
                "precio_nominal": precio, "unidad_precio": niveles.unidad_precio,
                "cpi": cpi if par.deflactar else None, "precio_real": real,
                "y": None, "dlog_precio_real": None,
                "control": "; ".join(marcas), "excluido": "", "motivo_exclusion": "; ".join(motivos),
                "cita_cantidad": niveles.cita_cantidad.get(anio, "") if cantidad is not None else "",
                "cita_precio": niveles.cita_precio if precio is not None else "",
            }
        )
    tabla = pd.DataFrame(filas, columns=COLUMNAS_N1_INSUMOS)
    por_anio = {int(f["anio"]): f for f in filas}
    cantidad_disputada = {a for a, f in por_anio.items() if niveles.control_cantidad.get(a, "").startswith(CONTROL_DISPUTA)}
    precio_disputado = {a for a, f in por_anio.items() if niveles.control_precio.get(a) == CONTROL_DISPUTA}
    con_cantidad = [a for a, f in por_anio.items() if f["cantidad"] is not None]
    con_precio = [a for a, f in por_anio.items() if f["precio_real"] is not None]

    def hueco(anio: int, presentes: list[int]) -> bool:
        # Un nivel que falta entre el primero y el último que existen es un hueco, no un arranque.
        return bool(presentes) and min(presentes) < anio < max(presentes)

    y_col, dlog_col, excl_col, motivo_col = [], [], [], []
    for fila in filas:
        anio = int(fila["anio"])
        previo = por_anio.get(anio - 1)
        y = dlog = None
        excluido, motivo = [], [fila["motivo_exclusion"]] if fila["motivo_exclusion"] else []
        if anio >= par.inicio:
            cantidad_ok = fila["cantidad"] is not None and anio not in cantidad_disputada
            previa_ok = previo is not None and previo["cantidad"] is not None and (anio - 1) not in cantidad_disputada
            if par.activo_clave == "acciones":
                if cantidad_ok:
                    y = fila["cantidad"]
            elif cantidad_ok and previa_ok:
                y = _log(fila["cantidad"]) - _log(previo["cantidad"])
            if y is None:
                excluido.append("y")
                if (anio - 1) in cantidad_disputada:
                    motivo.append(f"usa la cantidad de {anio - 1}, en disputa")
                elif fila["cantidad"] is None and hueco(anio, con_cantidad):
                    motivo.append(f"hueco: sin cantidad en {anio}")
                elif par.activo_clave != "acciones" and fila["cantidad"] is not None and (previo is None or previo["cantidad"] is None) and hueco(anio - 1, con_cantidad):
                    motivo.append(f"hueco: sin cantidad en {anio - 1}")
            precio_ok = fila["precio_real"] is not None and anio not in precio_disputado
            previo_ok = previo is not None and previo["precio_real"] is not None and (anio - 1) not in precio_disputado
            if precio_ok and previo_ok:
                dlog = _log(fila["precio_real"]) - _log(previo["precio_real"])
            else:
                excluido.append("Δlog p")
                if (anio - 1) in precio_disputado:
                    motivo.append(f"usa el precio de {anio - 1}, en disputa")
                elif fila["precio_real"] is None and hueco(anio, con_precio):
                    motivo.append(f"hueco: sin precio real en {anio}")
                elif fila["precio_real"] is not None and (previo is None or previo["precio_real"] is None) and hueco(anio - 1, con_precio):
                    motivo.append(f"hueco: sin precio real en {anio - 1}")
        y_col.append(y)
        dlog_col.append(dlog)
        excl_col.append(", ".join(excluido))
        motivo_col.append("; ".join(m for m in motivo if m))
    tabla["y"] = y_col
    tabla["dlog_precio_real"] = dlog_col
    tabla["excluido"] = excl_col
    tabla["motivo_exclusion"] = motivo_col
    return tabla


# --- La regresión (A-N1-8) -------------------------------------------------------------------


def _resolver(matriz: list[list[float]], vector: list[float]) -> list[float]:
    """Gauss con pivoteo parcial, en aritmética pura de Python: los bytes no dependen de la biblioteca."""
    n = len(vector)
    a = [fila[:] + [vector[i]] for i, fila in enumerate(matriz)]
    for columna in range(n):
        pivote = max(range(columna, n), key=lambda i: abs(a[i][columna]))
        if abs(a[pivote][columna]) < 1e-300:
            raise ValueError("la matriz de la regresión es singular")
        a[columna], a[pivote] = a[pivote], a[columna]
        for i in range(n):
            if i == columna:
                continue
            factor = a[i][columna] / a[columna][columna]
            if factor != 0.0:
                for j in range(columna, n + 1):
                    a[i][j] -= factor * a[columna][j]
    return [a[i][n] / a[i][i] for i in range(n)]


def _inversa(matriz: list[list[float]]) -> list[list[float]]:
    n = len(matriz)
    columnas = [_resolver(matriz, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[columnas[j][i] for j in range(n)] for i in range(n)]


def _producto(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


@dataclass(frozen=True)
class Estimacion:
    beta: list[float]  # [α, β_0, ..., β_5]
    covarianza: list[list[float]]  # Newey-West
    n: int
    anios: list[int]

    @property
    def errores(self) -> list[float]:
        return [math.sqrt(max(self.covarianza[i][i], 0.0)) for i in range(len(self.beta))]

    @property
    def suma(self) -> float:
        return sum(self.beta[1:])

    @property
    def error_suma(self) -> float:
        p = len(self.beta)
        return math.sqrt(max(sum(self.covarianza[i][j] for i in range(1, p) for j in range(1, p)), 0.0))


def minimos_cuadrados_newey_west(y: list[float], X: list[list[float]], L: int = N1_NEWEY_WEST_L) -> tuple[list[float], list[list[float]]]:
    """MCO y la covarianza de Newey-West (núcleo de Bartlett, rezago máximo L, sin corrección de muestra pequeña).

    Los rezagos del núcleo se cuentan sobre las observaciones consecutivas de la
    muestra (A-N1-8). Todo en aritmética pura de Python, en un orden fijo, para
    que dos máquinas den los mismos bytes.
    """
    n, p = len(y), len(X[0])
    XtX = [[sum(X[t][i] * X[t][j] for t in range(n)) for j in range(p)] for i in range(p)]
    Xty = [sum(X[t][i] * y[t] for t in range(n)) for i in range(p)]
    beta = _resolver(XtX, Xty)
    residuos = [y[t] - sum(X[t][i] * beta[i] for i in range(p)) for t in range(n)]
    xe = [[X[t][i] * residuos[t] for i in range(p)] for t in range(n)]
    S = [[sum(xe[t][i] * xe[t][j] for t in range(n)) for j in range(p)] for i in range(p)]
    for j in range(1, L + 1):
        peso = 1.0 - j / (L + 1.0)
        gamma = [[sum(xe[t][a] * xe[t - j][b] for t in range(j, n)) for b in range(p)] for a in range(p)]
        for a in range(p):
            for b in range(p):
                S[a][b] += peso * (gamma[a][b] + gamma[b][a])
    inversa = _inversa(XtX)
    V = _producto(_producto(inversa, S), inversa)
    return beta, V


def muestra_de(insumos: pd.DataFrame, inicio: int) -> tuple[list[int], list[float], list[list[float]]]:
    """Los años t con y_t y Δlog p_{t−k} para los seis k, y sus filas (constante y seis rezagos)."""
    y_por_anio = {int(a): v for a, v in zip(insumos["anio"], insumos["y"]) if v is not None and not pd.isna(v)}
    dlog = {int(a): v for a, v in zip(insumos["anio"], insumos["dlog_precio_real"]) if v is not None and not pd.isna(v)}
    anios, y, X = [], [], []
    for anio in sorted(y_por_anio):
        if anio < inicio + N1_REZAGO_MAXIMO:
            continue
        rezagos = [dlog.get(anio - k) for k in REZAGOS]
        if any(r is None for r in rezagos):
            continue
        anios.append(anio)
        y.append(float(y_por_anio[anio]))
        X.append([1.0] + [float(r) for r in rezagos])
    return anios, y, X


def estimar(insumos: pd.DataFrame, inicio: int) -> Estimacion | None:
    anios, y, X = muestra_de(insumos, inicio)
    if len(anios) < N1_N_MINIMO:
        return Estimacion([], [], len(anios), anios) if anios else Estimacion([], [], 0, [])
    beta, V = minimos_cuadrados_newey_west(y, X)
    return Estimacion(beta, V, len(anios), anios)


def rotulo_de(suma: float, error: float) -> str:
    """A-N1-10: por el intervalo del 95 % de la suma, y nada más."""
    inferior, superior = suma - Z * error, suma + Z * error
    if inferior > 0:
        return ROTULO_RESPONDE
    if superior < 0:
        return ROTULO_RESPUESTA_NEGATIVA
    return ROTULO_NO_RESPONDE


def especificacion_de(par: ParN1) -> str:
    dependiente = "tasa_t (nivel de la emisión neta / valor de mercado previo, en fracción)" if par.activo_clave == "acciones" else "Δlog(cantidad_t)"
    precio = "Δlog(valuación_{t−k}), sin deflactar" if not par.deflactar else "Δlog(precio real_{t−k}) con precio real = nominal / CPI del mismo año"
    return (
        f"{dependiente} sobre {precio}, k = 0..{N1_REZAGO_MAXIMO}, en una sola regresión con constante; mínimos cuadrados ordinarios; "
        f"errores de Newey-West (Bartlett, L = {N1_NEWEY_WEST_L}, sin corrección de muestra pequeña); intervalos del 95 % con cuantil normal; n mínimo {N1_N_MINIMO}"
    )


# --- Resultados por par ------------------------------------------------------------------------


@dataclass
class ResultadoPar:
    par: ParN1
    estado: str  # estimación, evidencia insuficiente o NO MEDIDO: ...
    motivo: str
    insumos: pd.DataFrame | None
    estimacion: Estimacion | None

    @property
    def rotulo(self) -> str:
        if self.estimacion is None or not self.estimacion.beta:
            return ""
        return rotulo_de(self.estimacion.suma, self.estimacion.error_suma)

    @property
    def anios_excluidos(self) -> str:
        if self.insumos is None:
            return ""
        anios = sorted(int(a) for a, m in zip(self.insumos["anio"], self.insumos["motivo_exclusion"]) if m and int(a) >= self.par.inicio)
        return ", ".join(str(a) for a in anios)


def resultados(construido: Construido, validaciones: dict[str, ValidacionN0]) -> list[ResultadoPar]:
    salida = []
    for par in PARES_N1:
        motivo = motivo_no_medido(par, construido, validaciones)
        if motivo is not None:
            salida.append(ResultadoPar(par, ESTADO_NO_MEDIDO, motivo, None, None))
            continue
        insumos = insumos_de(par, niveles_de(par, construido, validaciones))
        try:
            estimacion = estimar(insumos, par.inicio)
        except ValueError as error:
            salida.append(ResultadoPar(par, ESTADO_NO_MEDIDO, f"NO MEDIDO: la regresión no tiene solución ({error})", insumos, None))
            continue
        if estimacion is None or not estimacion.beta:
            n = estimacion.n if estimacion is not None else 0
            salida.append(ResultadoPar(par, ESTADO_EVIDENCIA_INSUFICIENTE, f"{n} observaciones utilizables y hacen falta {N1_N_MINIMO} (A-N1-8)", insumos, estimacion))
            continue
        salida.append(ResultadoPar(par, ESTADO_ESTIMACION, "", insumos, estimacion))
    return salida


# --- Tablas de salida (A-N1-11) ------------------------------------------------------------------


def _redondear(valor: float) -> float:
    return round(valor, N1_DECIMALES)


def tabla_coeficientes(resultados_: list[ResultadoPar], fecha_corrida: date) -> pd.DataFrame:
    filas = []
    for resultado in resultados_:
        estimacion = resultado.estimacion
        if resultado.estado != ESTADO_ESTIMACION or estimacion is None:
            continue
        errores = estimacion.errores
        for k in REZAGOS:
            beta, error = estimacion.beta[k + 1], errores[k + 1]
            filas.append(
                {
                    "activo": resultado.par.activo, "ventana": resultado.par.ventana, "rezago": k,
                    "coeficiente": _redondear(beta), "error_estandar": _redondear(error),
                    "intervalo_inferior": _redondear(beta - Z * error), "intervalo_superior": _redondear(beta + Z * error),
                    "n": estimacion.n, "fecha_corrida": fecha_corrida.isoformat(), "rotulo_fijo": ROTULO_FIJO_N1,
                    "desvio_del_prerregistro": SIN_DESVIO, "supuestos": " ".join(resultado.par.supuestos),
                }
            )
    return pd.DataFrame(filas, columns=COLUMNAS_N1_COEFICIENTES)


def tabla_resumen(resultados_: list[ResultadoPar], fecha_corrida: date) -> pd.DataFrame:
    filas = []
    for resultado in resultados_:
        par, estimacion = resultado.par, resultado.estimacion
        fila = {columna: "" for columna in COLUMNAS_N1_RESUMEN} | {
            "activo": par.activo, "ventana": par.ventana, "especificacion": especificacion_de(par),
            "estado": resultado.estado, "motivo": resultado.motivo, "rotulo": resultado.rotulo, "rotulo_fijo": ROTULO_FIJO_N1,
            "desvio_del_prerregistro": SIN_DESVIO, "supuestos": " ".join(par.supuestos), "fecha_corrida": fecha_corrida.isoformat(),
            "anios_excluidos": resultado.anios_excluidos,
        }
        if estimacion is not None:
            fila["n"] = estimacion.n
            if estimacion.anios:
                fila["primer_anio"], fila["ultimo_anio"] = estimacion.anios[0], estimacion.anios[-1]
            if estimacion.beta:
                suma, error = estimacion.suma, estimacion.error_suma
                fila |= {"suma": _redondear(suma), "error_estandar": _redondear(error), "intervalo_inferior": _redondear(suma - Z * error), "intervalo_superior": _redondear(suma + Z * error)}
        filas.append(fila)
    for fija in FILAS_FIJAS_N1:
        filas.append(
            {columna: "" for columna in COLUMNAS_N1_RESUMEN} | {
                "activo": fija.activo, "ventana": fija.ventana, "especificacion": "ninguna: no se estima", "rotulo": fija.rotulo,
                "estado": fija.estado, "motivo": fija.motivo, "rotulo_fijo": ROTULO_FIJO_N1, "desvio_del_prerregistro": SIN_DESVIO,
                "supuestos": " ".join(fija.supuestos), "fecha_corrida": fecha_corrida.isoformat(),
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_N1_RESUMEN)


def tabla_insumos(resultados_: list[ResultadoPar]) -> pd.DataFrame:
    tablas = [r.insumos for r in resultados_ if r.insumos is not None]
    if not tablas:
        return pd.DataFrame(columns=COLUMNAS_N1_INSUMOS)
    return pd.concat(tablas, ignore_index=True).loc[:, COLUMNAS_N1_INSUMOS]


def _validacion_de_insumo(clave: str, validaciones: dict[str, ValidacionN0]) -> str:
    claves = {
        SERIE_TERMINADAS: ["terminadas_sumas"],
        "viviendas_eeuu_precio_fhfa_at_promedio_anual": ["fhfa_fred"],
        "cpi_u_eeuu_promedio_anual": ["cpi_bls_mensual", "cpi_bls_anual"],
        "oro_precio_ds140_valor_unitario_usd_oz": ["ds140_pink_sheet_oro"],
        "plata_precio_ds140_valor_unitario_usd_oz": ["ds140_pink_sheet_plata"],
        "acciones_eeuu_valuacion_no_financieras_pct": ["b103_identidad", "b103_html"],
        "acciones_eeuu_valuacion_junta_fl103164106_pct": ["b103_identidad", "b103_html"],
    }.get(clave, [])
    textos = [validaciones[c].validacion() for c in claves if c in validaciones]
    if clave.endswith("_precio_pink_sheet_promedio_anual_usd_oz"):
        textos.append("el nivel anual lo validó el gate de la fase R contra el USGS en 2021–2024 (A-R0-16); el control mensual del FMI marca los meses en disputa (A-R0-20)")
    return "; ".join(textos) if textos else "sin validación externa"


def tabla_fichas(construido: Construido, validaciones: dict[str, ValidacionN0], resultados_: list[ResultadoPar], insumos: pd.DataFrame, fecha_corrida: date) -> pd.DataFrame:
    filas = []
    for serie in INSUMOS_N1:
        usable, estado = estado_insumo(serie.clave, construido, validaciones)
        anios_insumo = _anios_del_insumo(serie.clave, construido)
        filas.append(
            {
                "serie": serie.clave, "nombre": serie.nombre, "familia": serie.familia, "mide": serie.mide,
                "publicada": "sí" if usable else "no", "estado": estado, "unidad": serie.unidad, "convencion": serie.convencion,
                "frecuencia": serie.frecuencia, "emisor": serie.emisor,
                "fuente": serie.descarga.descripcion if serie.descarga else "fase R, precios_mensuales.csv (Pink Sheet del Banco Mundial, A-R0-19)",
                "identificador": serie.identificador,
                "url": serie.descarga.url if serie.descarga else "data/series/precios_mensuales.csv",
                "licencia": serie.descarga.licencia if serie.descarga else "CC BY 4.0 (Banco Mundial, Pink Sheet; A-R0-14)",
                "atribucion": serie.descarga.atribucion if serie.descarga else "The World Bank: Commodity Price Data (The Pink Sheet). Los promedios anuales son cálculo propio.",
                "validacion": _validacion_de_insumo(serie.clave, validaciones),
                "supuestos": " ".join(serie.supuestos), "quiebres": serie.nota + (f"; corrida del {fecha_corrida}" if serie.nota else f"corrida del {fecha_corrida}") + "; " + ROTULO_FIJO_N1,
                "primer_anio": anios_insumo[0] if anios_insumo else "", "ultimo_anio": anios_insumo[1] if anios_insumo else "", "anios": anios_insumo[2] if anios_insumo else 0,
            }
        )
    for resultado in resultados_:
        par, estimacion = resultado.par, resultado.estimacion
        filas.append(
            {
                "serie": f"respuesta_oferta_{par.clave}", "nombre": f"{par.activo}: respuesta observada de la oferta al precio, ventana {par.ventana}",
                "familia": FAMILIA_RESPUESTA, "mide": MIDE_RESPUESTA,
                "publicada": "sí" if resultado.estado == ESTADO_ESTIMACION else "no", "estado": _estado_de_resultado(resultado),
                "unidad": "coeficientes de Δlog(cantidad) sobre Δlog(precio real)" if par.activo_clave != "acciones" else "variación de la tasa de emisión neta (fracción) por unidad de Δlog de la valuación",
                "convencion": especificacion_de(par), "frecuencia": "anual", "emisor": "cálculo propio",
                "fuente": f"cantidad: {par.cantidad_nombre}; precio: {par.precio_nombre}", "identificador": par.cantidad_serie,
                "url": "", "licencia": "cálculo propio sobre fuentes citadas en las fichas de los insumos", "atribucion": "",
                "validacion": "los gates y controles de los insumos (fichas de arriba); el método no tiene validación externa: es un prerregistro",
                "supuestos": " ".join(par.supuestos),
                "quiebres": f"ventana {par.inicio}–{par.fin}, que acota las variables en diferencias; años excluidos: {resultado.anios_excluidos or 'ninguno'}; corrida del {fecha_corrida}; " + ROTULO_FIJO_N1,
                "primer_anio": estimacion.anios[0] if estimacion is not None and estimacion.anios else "",
                "ultimo_anio": estimacion.anios[-1] if estimacion is not None and estimacion.anios else "",
                "anios": estimacion.n if estimacion is not None else 0,
            }
        )
    for fija in FILAS_FIJAS_N1:
        filas.append(
            {columna: "" for columna in COLUMNAS_N1_FICHAS} | {
                "serie": f"respuesta_oferta_{fija.clave}", "nombre": f"{fija.activo}: respuesta observada de la oferta al precio",
                "familia": FAMILIA_RESPUESTA, "mide": MIDE_RESPUESTA, "publicada": "no", "estado": fija.estado if fija.estado == ESTADO_DATO else fija.motivo,
                "convencion": fija.motivo if fija.estado == ESTADO_DATO else "", "fuente": "Bitcoin Core (código del protocolo)" if fija.clave == "btc" else "ninguna",
                "supuestos": " ".join(fija.supuestos), "quiebres": ROTULO_FIJO_N1, "anios": 0,
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_N1_FICHAS)


def _estado_de_resultado(resultado: ResultadoPar) -> str:
    if resultado.estado == ESTADO_NO_MEDIDO:
        return resultado.motivo  # ya empieza con "NO MEDIDO: ..."
    if resultado.estado == ESTADO_EVIDENCIA_INSUFICIENTE:
        return f"{resultado.estado}: {resultado.motivo}"
    return resultado.estado


def _anios_del_insumo(clave: str, construido: Construido) -> tuple[int, int, int] | None:
    serie = None
    if clave == SERIE_TERMINADAS and construido.terminadas is not None:
        serie = construido.terminadas.anual
    elif clave == "viviendas_eeuu_precio_fhfa_at_promedio_anual" and construido.fhfa_trimestral is not None:
        serie = promedio_anual(construido.fhfa_trimestral, 4)
    elif clave == "cpi_u_eeuu_promedio_anual" and construido.cpi_mensual is not None:
        serie = promedio_anual(construido.cpi_mensual, 12)
    elif clave.endswith("_precio_pink_sheet_promedio_anual_usd_oz") and clave.split("_")[0] in construido.pink_sheet:
        serie = construido.pink_sheet[clave.split("_")[0]].anual
    elif clave.endswith("_precio_ds140_valor_unitario_usd_oz") and clave.split("_")[0] in construido.ds140:
        serie = construido.ds140[clave.split("_")[0]].usd_por_oz
    elif clave.startswith("acciones_eeuu_valuacion") and construido.b103 is not None:
        if clave.endswith("junta_fl103164106_pct"):
            serie = construido.b103["FL103164106"].dropna()
            return int(str(serie.index[0])[:4]), int(str(serie.index[-1])[:4]), len(serie)
        serie = promedio_anual((construido.b103["LM103164105"] / construido.b103["FL102090005"] * 100.0).dropna(), 4)
    if serie is None or serie.empty:
        return None
    return int(serie.index.min()), int(serie.index.max()), len(serie)


# --- Revisiones y changelog (A-N1-12) ------------------------------------------------------------


def revisiones_de(previa_coef: pd.DataFrame | None, nueva_coef: pd.DataFrame, previo_resumen: pd.DataFrame | None, nuevo_resumen: pd.DataFrame) -> list[str]:
    revisiones = []
    if previa_coef is not None and not previa_coef.empty:
        anterior = {(f.activo, f.ventana, int(f.rezago)): float(f.coeficiente) for f in previa_coef.itertuples()}
        for fila in nueva_coef.itertuples():
            clave = (fila.activo, fila.ventana, int(fila.rezago))
            if clave in anterior and abs(anterior[clave] - float(fila.coeficiente)) > EPSILON_REVISION_N1:
                revisiones.append(f"{fila.activo}, {fila.ventana}, rezago {fila.rezago}: coeficiente {formatear(anterior[clave], 6)} -> {formatear(float(fila.coeficiente), 6)}")
        for clave in sorted(set(anterior) - {(f.activo, f.ventana, int(f.rezago)) for f in nueva_coef.itertuples()}):
            revisiones.append(f"{clave[0]}, {clave[1]}, rezago {clave[2]}: el coeficiente deja de publicarse")
    if previo_resumen is not None and not previo_resumen.empty:
        anterior = {(f.activo, f.ventana): (str(f.rotulo), str(f.estado), str(f.suma), str(f.n)) for f in previo_resumen.itertuples()}
        for fila in nuevo_resumen.itertuples():
            clave = (fila.activo, fila.ventana)
            if clave not in anterior:
                continue
            rotulo, estado, suma, n = anterior[clave]
            if rotulo != str(fila.rotulo) or estado != str(fila.estado):
                revisiones.append(f"{fila.activo}, {fila.ventana}: rótulo/estado {rotulo!r}/{estado!r} -> {str(fila.rotulo)!r}/{str(fila.estado)!r}")
            elif suma and str(fila.suma) and abs(float(suma) - float(fila.suma)) > EPSILON_REVISION_N1:
                revisiones.append(f"{fila.activo}, {fila.ventana}: suma {suma} -> {fila.suma} (n {n} -> {fila.n})")
    return revisiones


@dataclass
class EntradaRespuestaOferta:
    fecha_corrida: date
    descargas: list[str]
    insumos: list[str]
    validaciones: list[str]
    resultados: list[str]
    revisiones: list[str]
    notas: list[str] = field(default_factory=list)

    @property
    def titulo(self) -> str:
        return f"{self.fecha_corrida.isoformat()} · respuesta_oferta"

    def render(self) -> str:
        lineas = [f"## {self.titulo}", ""]

        def bloque(encabezado: str, items: list[str], vacio: str) -> None:
            if not items:
                lineas.append(f"- {encabezado}: {vacio}")
                return
            lineas.append(f"- {encabezado}:")
            lineas.extend(f"  - {item}" for item in items)

        bloque("Descargas", self.descargas, "ninguna")
        bloque("Insumos", self.insumos, "ninguno")
        bloque("Validación", self.validaciones, "ninguna")
        bloque("Resultados (activo → ventana → rótulo → n; sin interpretar)", self.resultados, "ninguno")
        bloque("Revisiones respecto de la corrida anterior", self.revisiones, "ninguna")
        lineas.append(f"- Rótulo fijo: {ROTULO_FIJO_N1}")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


# --- Gráficos ----------------------------------------------------------------------------------


def graficar(resultados_: list[ResultadoPar], dir_reportes: Path) -> list[Path]:
    """Un PNG por par estimado: los seis coeficientes con su intervalo y la suma. Sin interpretar."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from senales.grafico import ESTILO, GRILLA, TINTA, TINTA_SUAVE

    rutas = []
    for resultado in resultados_:
        estimacion = resultado.estimacion
        if resultado.estado != ESTADO_ESTIMACION or estimacion is None:
            continue
        errores = estimacion.errores
        betas = estimacion.beta[1:]
        with plt.rc_context(ESTILO):
            figura, eje = plt.subplots(figsize=(7.5, 4.2))
            eje.axhline(0.0, color=TINTA_SUAVE, linewidth=0.8)
            eje.errorbar(list(REZAGOS), betas, yerr=[Z * e for e in errores[1:]], fmt="o", color=TINTA, ecolor=TINTA, elinewidth=1.2, capsize=3, markersize=5)
            eje.errorbar([N1_REZAGO_MAXIMO + 1.5], [estimacion.suma], yerr=[Z * estimacion.error_suma], fmt="s", color=TINTA, ecolor=TINTA, elinewidth=1.2, capsize=3, markersize=6)
            eje.set_xticks(list(REZAGOS) + [N1_REZAGO_MAXIMO + 1.5])
            eje.set_xticklabels([f"k = {k}" for k in REZAGOS] + ["suma"])
            eje.set_ylabel("coeficiente (intervalo del 95 %)")
            eje.yaxis.grid(True, color=GRILLA, linewidth=0.7)
            eje.set_axisbelow(True)
            eje.set_title(f"{resultado.par.activo} · {resultado.par.ventana} · rótulo: {resultado.rotulo}", loc="left", fontsize=11, pad=10)
            pie = (
                f"{ROTULO_FIJO_N1}. n = {estimacion.n} ({estimacion.anios[0]}–{estimacion.anios[-1]}); "
                f"MCO, Newey-West L = {N1_NEWEY_WEST_L}; prerregistro A-N1-1 a A-N1-12."
            )
            eje.annotate(pie, xy=(0.0, -0.2), xycoords="axes fraction", fontsize=7.5, color=TINTA_SUAVE, va="top", ha="left", wrap=True)
            destino = dir_reportes / f"{PREFIJO_GRAFICO_N1}{resultado.par.clave}.png"
            destino.parent.mkdir(parents=True, exist_ok=True)
            figura.savefig(destino, dpi=160, bbox_inches="tight")
            plt.close(figura)
        rutas.append(destino)
    return rutas


# --- main ----------------------------------------------------------------------------------------


def _leer(ruta: Path) -> pd.DataFrame | None:
    return pd.read_csv(ruta, dtype=str, keep_default_na=False) if ruta.exists() else None


def correr(fecha_descarga: date, sesion=None, con_graficos: bool = True) -> int:
    asegurar_directorios(DIR_CRUDO, DIR_CRUDO_PRIVADO, DIR_SERIES)
    crudos = cargar_crudos(fecha_descarga, sesion)
    construido = construir(crudos.rutas, crudos.faltantes)
    validaciones = validar(construido)
    try:
        exigir_gate_de_construccion(validaciones)
    except GateDeConstruccion as error:
        print(f"GATE DE CONSTRUCCIÓN: {error}", file=sys.stderr)
        return CODIGO_GATE_DE_CONSTRUCCION
    fuentes_precios.actualizar_manifiesto(ARCHIVO_N1_DESCARGAS, crudos.registros)

    resultados_ = resultados(construido, validaciones)
    coeficientes = tabla_coeficientes(resultados_, fecha_descarga)
    resumen = tabla_resumen(resultados_, fecha_descarga)
    insumos = tabla_insumos(resultados_)
    fichas = tabla_fichas(construido, validaciones, resultados_, insumos, fecha_descarga)

    revisiones = revisiones_de(_leer(ARCHIVO_N1_COEFICIENTES), coeficientes, _leer(ARCHIVO_N1_RESUMEN), resumen)
    primera = not ARCHIVO_N1_RESUMEN.exists()
    escribir_csv_determinista(coeficientes, ARCHIVO_N1_COEFICIENTES, COLUMNAS_N1_COEFICIENTES, FORMATO_N1_COEFICIENTES)
    escribir_csv_determinista(resumen, ARCHIVO_N1_RESUMEN, COLUMNAS_N1_RESUMEN, FORMATO_N1_COEFICIENTES)
    escribir_csv_determinista(insumos, ARCHIVO_N1_INSUMOS, COLUMNAS_N1_INSUMOS, FORMATO_N1)
    escribir_csv_determinista(fichas, ARCHIVO_N1_FICHAS, COLUMNAS_N1_FICHAS, FORMATO_N1)
    graficos = graficar(resultados_, DIR_REPORTES) if con_graficos else []

    lineas_insumos = []
    for fila in fichas.itertuples():
        if fila.familia == FAMILIA_RESPUESTA and fila.mide == MIDE_RESPUESTA:
            continue
        lineas_insumos.append(f"{fila.nombre}: {'se usa' if fila.publicada == 'sí' else 'no se usa'}: {fila.estado}" + (f"; {fila.primer_anio} a {fila.ultimo_anio}, {fila.anios} valores" if fila.anios else ""))
    lineas_resultados = []
    for fila in resumen.itertuples():
        lineas_resultados.append(
            f"{fila.activo} → {fila.ventana} → {fila.rotulo or fila.estado} → n = {fila.n or '—'}"
            + (f" (suma {fila.suma}, intervalo [{fila.intervalo_inferior}, {fila.intervalo_superior}])" if fila.suma else "")
            + (f"; años excluidos: {fila.anios_excluidos}" if fila.anios_excluidos else "")
            + (f"; {fila.motivo}" if fila.motivo and fila.estado != ESTADO_ESTIMACION else "")
        )
    notas = [
        "prerregistro A-N1-1 a A-N1-12, fijado antes de descargar o cruzar un precio; ningún parámetro se eligió con los datos (A-N1-9)",
        "las series de cantidad salen de numerador_series.csv (fase N0) y el Pink Sheet mensual de precios_mensuales.csv (fase R); los crudos nuevos y sus hashes están en respuesta_oferta_descargas.csv (A-N1-11)",
    ]
    if primera:
        notas.insert(0, "primera publicación de la familia: no hay corrida anterior con que comparar")
    for clave, motivo in crudos.faltantes.items():
        notas.append(f"sin crudo de {clave}: {motivo[:240]}")
    entrada = EntradaRespuestaOferta(
        fecha_corrida=fecha_descarga,
        descargas=[
            f"{r.descarga.clave}: {r.url}, sha256 {r.sha256}" + (f", actualizada el {r.actualizada}" if r.actualizada else "") + ("" if r.fecha_descarga == fecha_descarga else f", copia del {r.fecha_descarga}")
            for r in crudos.registros
        ],
        insumos=lineas_insumos,
        validaciones=[v.resumen() for v in validaciones.values()],
        resultados=lineas_resultados,
        revisiones=revisiones[:40] + ([f"y {len(revisiones) - 40} más"] if len(revisiones) > 40 else []),
        notas=notas,
    )
    cambio = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Descargas")
    for registro in crudos.registros:
        print(f"  {registro.linea()}")
    for clave, motivo in crudos.faltantes.items():
        print(f"  {clave}: SIN CRUDO: {motivo[:200]}")
    print("Validación")
    for validacion in validaciones.values():
        print(f"  {validacion.resumen()}")
    print("Resultados (activo → ventana → rótulo → n)")
    for linea in lineas_resultados:
        print(f"  {linea}")
    print("Salidas")
    for ruta, tabla in ((ARCHIVO_N1_COEFICIENTES, coeficientes), (ARCHIVO_N1_RESUMEN, resumen), (ARCHIVO_N1_INSUMOS, insumos), (ARCHIVO_N1_FICHAS, fichas)):
        print(f"  {ruta} ({len(tabla)} filas)")
    print(f"  {ARCHIVO_N1_DESCARGAS}")
    for grafico in graficos:
        print(f"  {grafico}")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio else 'sin cambios'})")
    print(f"Rótulo fijo: {ROTULO_FIJO_N1}")
    return CODIGO_FUENTE_FALTANTE if crudos.faltantes else 0


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.respuesta_oferta",
        description="Estima la familia 'respuesta observada de la oferta al precio' según el prerregistro A-N1-*.",
    )
    analizador.add_argument(
        "--fecha-descarga",
        type=date.fromisoformat,
        default=date.today(),
        help="Fecha de la descarga a usar (AAAA-MM-DD). Permite rehacer una corrida anterior a partir de los crudos ya guardados.",
    )
    analizador.add_argument("--sin-graficos", action="store_true", help="No escribe los PNG de reportes/.")
    argumentos = analizador.parse_args(argv)
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")
    return correr(argumentos.fecha_descarga, con_graficos=not argumentos.sin_graficos)


if __name__ == "__main__":
    raise SystemExit(main())
