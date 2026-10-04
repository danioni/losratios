"""Fase R - Precios mensuales y ratios.

Cinco series —oro, plata, BTC, S&P 500 y Nasdaq Composite— llevadas a una sola
convención, el promedio mensual de cierres diarios (A-R0-1), y los cinco pares
del sitio.

Un comando hace todo:

    python -m senales.ratios

descarga, deja constancia de cada descarga en el manifiesto, lleva cada serie a
meses completos, calcula los pares, contrasta contra una segunda fuente, escribe
las salidas y actualiza el changelog.

No todo lo que se calcula se publica. Las series y los pares que dependen de un
índice cuyo dueño no dio permiso se calculan igual, quedan fuera del repositorio
y se publican como NO MEDIDO (A-R0-14). Si un contraste no cierra, la corrida se
detiene sin escribir ninguna serie.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from senales import bitacora, fuentes_precios
from senales.configuracion import (
    ANCLA_LBMA_ORO,
    ANCLA_LBMA_PLATA,
    ARCHIVO_CHANGELOG,
    ARCHIVO_DESCARGAS,
    ARCHIVO_INTERNO,
    ARCHIVO_PARES,
    ARCHIVO_PRECIOS,
    ARCHIVO_RATIOS,
    ARCHIVO_SERIES_INFO,
    BANDAS_LBMA,
    COLUMNAS_INTERNO,
    COLUMNAS_PARES,
    COLUMNAS_PRECIOS,
    COLUMNAS_RATIOS,
    COLUMNAS_SERIES_INFO,
    CONTRASTES,
    CONTRASTE_BTC,
    CONTRASTE_NASDAQ,
    CONTRASTE_SP500,
    DESCARGA_COIN_METRICS,
    DESCARGA_NASDAQCOM,
    DESCARGA_PINK_SHEET,
    DESCARGA_SHILLER,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    DIR_SERIES,
    DIR_SERIES_PRIVADO,
    EPSILON_REVISION_PRECIOS,
    EPSILON_REVISION_RATIOS,
    ESTADO_DATO,
    ESTADO_ESTIMACION,
    FORMATO_RATIOS,
    NASDAQ_FECHA_BASE,
    NASDAQ_VALOR_BASE,
    NO_MEDIDO_PERMISO,
    ORO_DEFINICION_ANTES,
    ORO_DEFINICION_DESPUES,
    ORO_QUIEBRE_DEFINICION,
    PARES,
    SERIES_PRECIO,
    TOLERANCIA_ANCLA_ORO_PCT,
    TOLERANCIA_ANCLA_PLATA_PCT,
    VENTANA_CONTRASTE_NASDAQ_ANIOS,
    AnclaMensual,
    BandaTrimestral,
    Contraste,
    Par,
    SeriePrecio,
)
from senales.fuentes_fred import ErrorDeFuente
from senales.fuentes_precios import RegistroDescarga
from senales.nucleo import asegurar_directorios, escribir_csv_determinista, formatear

CODIGO_ERROR_FUENTE = 1
CODIGO_VALIDACION_FALLIDA = 2

SERIES_POR_CLAVE: dict[str, SeriePrecio] = {serie.clave: serie for serie in SERIES_PRECIO}


def _mes(valor) -> str:
    return pd.Timestamp(valor).strftime("%Y-%m")


# --- A-R0-1: promedio mensual, solo de meses completos ------------------------


def _hay_habiles_antes(primera: pd.Timestamp) -> bool:
    """¿Hubo días hábiles entre el 1 del mes y la primera observación?"""
    inicio = primera.to_period("M").to_timestamp()
    return len(pd.bdate_range(inicio, primera - pd.Timedelta(days=1))) > 0


def promedio_mensual(diaria: pd.Series, dias_calendario: bool) -> tuple[pd.Series, list[str]]:
    """Promedio de los cierres diarios de cada mes completo.

    Un mes cuenta como completo cuando la serie ya tiene una observación
    posterior a su último día: el mes de la última observación es el mes en
    curso y queda afuera. El primer mes queda afuera si la serie arranca con el
    mes empezado.

    `dias_calendario` distingue un mercado que opera todos los días (A-R0-5) de
    uno que opera los hábiles. En el primero un mes está completo si tiene todos
    sus días; en el segundo no hay calendario contra el que contar.

    Devuelve la serie mensual y la lista de meses descartados, con el motivo.
    """
    periodos = diaria.index.to_period("M")
    promedios = diaria.groupby(periodos).mean()
    cuentas = diaria.groupby(periodos).size()
    primera, ultima = diaria.index[0], diaria.index[-1]

    conservados, descartados = [], []
    for periodo in promedios.index:
        if periodo == ultima.to_period("M"):
            descartados.append(
                f"{periodo}: mes en curso (la última observación es del {ultima.date()})"
            )
        elif dias_calendario and cuentas[periodo] != periodo.days_in_month:
            descartados.append(
                f"{periodo}: tiene {cuentas[periodo]} de {periodo.days_in_month} días"
            )
        elif (
            not dias_calendario
            and periodo == primera.to_period("M")
            and _hay_habiles_antes(primera)
        ):
            descartados.append(
                f"{periodo}: la serie empieza el {primera.date()}, con el mes empezado"
            )
        else:
            conservados.append(periodo)

    mensual = promedios.loc[conservados]
    mensual.index = mensual.index.to_timestamp()
    mensual.index.name = "mes"
    return mensual, descartados


def meses_completos(mensual: pd.Series, actualizada: date | None) -> tuple[pd.Series, list[str]]:
    """Recorta una fuente que ya viene mensual a sus meses completos.

    Un mes está completo si terminó antes de la fecha en que la fuente dice
    haberse actualizado. Si la fuente no declara esa fecha, la última fila se
    descarta: no hay cómo saber si es un mes entero. No se lee la nota de texto
    que la fuente pone al pie, que puede cambiar de redacción (A-R0-11).
    """
    if mensual.empty:
        return mensual, []
    if actualizada is None:
        return mensual.iloc[:-1], [
            f"{_mes(mensual.index[-1])}: última fila de una fuente que no declara "
            "cuándo se actualizó"
        ]
    fin_de_mes = mensual.index + pd.offsets.MonthEnd(0)
    completos = fin_de_mes < pd.Timestamp(actualizada)
    descartados = [
        f"{_mes(mes)}: no había terminado cuando la fuente se actualizó ({actualizada})"
        for mes in mensual.index[~completos]
    ]
    return mensual[completos], descartados


def desde_el_mes(mensual: pd.Series, serie: SeriePrecio) -> tuple[pd.Series, list[str]]:
    """Aplica el primer mes de una serie, si tiene uno (A-R0-10 para BTC)."""
    if serie.desde is None:
        return mensual, []
    corte = pd.Timestamp(serie.desde + "-01")
    antes = mensual[mensual.index < corte]
    if antes.empty:
        return mensual, []
    return mensual[mensual.index >= corte], [
        f"{_mes(antes.index[0])} a {_mes(antes.index[-1])}: {len(antes)} meses anteriores "
        f"a {serie.desde}, que es desde donde la serie se usa"
    ]


def verificar_banda(mensual: pd.Series, serie: SeriePrecio) -> None:
    """Control de orden de magnitud: atrapa una unidad equivocada sin metadatos."""
    if mensual.empty:
        raise ErrorDeFuente(f"{serie.nombre}: no quedó ningún mes completo")
    minimo, maximo = serie.banda_plausible
    fuera = mensual[(mensual < minimo) | (mensual > maximo)]
    if not fuera.empty:
        muestra = ", ".join(f"{_mes(m)}={formatear(v, 4)}" for m, v in fuera.head(3).items())
        raise ErrorDeFuente(
            f"{serie.nombre}: {len(fuera)} meses fuera de la banda plausible "
            f"[{minimo}, {maximo}] {serie.unidad} ({muestra})"
        )


def verificar_base_nasdaq(diaria: pd.Series) -> None:
    """El Nasdaq Composite vale 100 el 5 de febrero de 1971: es su unidad."""
    base = pd.Timestamp(NASDAQ_FECHA_BASE)
    if base not in diaria.index or abs(diaria[base] - NASDAQ_VALOR_BASE) > 1e-9:
        hallado = diaria.get(base, "sin dato")
        raise ErrorDeFuente(
            f"NASDAQCOM: el {NASDAQ_FECHA_BASE} debería valer {NASDAQ_VALOR_BASE} (la base "
            f"del índice) y vale {hallado}. La serie no es la que se configuró."
        )


# --- Pares y regla de publicación (A-R0-14) -----------------------------------


def par_publicable(par: Par) -> bool:
    return SERIES_POR_CLAVE[par.numerador].publicable and SERIES_POR_CLAVE[par.denominador].publicable


def estado_del_par(par: Par) -> str:
    if not par_publicable(par):
        return NO_MEDIDO_PERMISO
    lados = (SERIES_POR_CLAVE[par.numerador], SERIES_POR_CLAVE[par.denominador])
    if any(lado.estado == ESTADO_ESTIMACION for lado in lados):
        return ESTADO_ESTIMACION
    return ESTADO_DATO


def calcular_pares(precios: pd.DataFrame) -> pd.DataFrame:
    """Los cinco ratios, mes a mes. Donde falta un lado, el ratio queda vacío."""
    pares = pd.DataFrame(index=precios.index)
    for par in PARES:
        denominador = precios[par.denominador].where(precios[par.denominador] != 0.0)
        pares[par.clave] = precios[par.numerador] / denominador
    return pares


def tabla_precios(precios: pd.DataFrame) -> pd.DataFrame:
    """Las series que se publican, con lo que hay que decir junto a cada una."""
    publicables = [serie.clave for serie in SERIES_PRECIO if serie.publicable]
    visibles = precios.loc[precios[publicables].notna().any(axis=1), publicables]
    quiebre = pd.Timestamp(ORO_QUIEBRE_DEFINICION + "-01")

    tabla = pd.DataFrame({"mes": [_mes(mes) for mes in visibles.index]})
    tabla["oro_usd_oz"] = visibles["oro"].to_numpy()
    # A-R0-7: el quiebre de definición del oro va declarado fila por fila.
    tabla["oro_definicion"] = [
        "" if pd.isna(valor) else (ORO_DEFINICION_ANTES if mes < quiebre else ORO_DEFINICION_DESPUES)
        for mes, valor in visibles["oro"].items()
    ]
    tabla["plata_usd_oz"] = visibles["plata"].to_numpy()
    # A-R0-8: la plata es una estimación, y se ve.
    tabla["plata_estado"] = [
        "" if pd.isna(valor) else SERIES_POR_CLAVE["plata"].estado for valor in visibles["plata"]
    ]
    tabla["btc_usd"] = visibles["btc"].to_numpy()
    return tabla


def tabla_ratios(pares: pd.DataFrame) -> pd.DataFrame:
    """Los pares publicables, en formato largo. Los demás no tienen filas acá."""
    bloques = []
    for par in PARES:
        if not par_publicable(par):
            continue
        valores = pares[par.clave].dropna()
        bloques.append(
            pd.DataFrame(
                {
                    "mes": [_mes(mes) for mes in valores.index],
                    "par": par.clave,
                    "valor": valores.to_numpy(),
                    "estado": estado_del_par(par),
                }
            )
        )
    if not bloques:
        return pd.DataFrame(columns=COLUMNAS_RATIOS)
    return pd.concat(bloques, ignore_index=True).sort_values(["mes", "par"], kind="stable")


def tabla_pares(pares: pd.DataFrame) -> pd.DataFrame:
    """Los cinco pares, publicados o no, y hasta dónde llega cada uno.

    Es donde un par sin permiso aparece: existe, tiene historia, y su estado
    dice por qué no se muestra.
    """
    filas = []
    for par in PARES:
        valores = pares[par.clave].dropna()
        filas.append(
            {
                "par": par.clave,
                "nombre": par.nombre,
                "publicado": "sí" if par_publicable(par) else "no",
                "estado": estado_del_par(par),
                "primer_mes": "" if valores.empty else _mes(valores.index[0]),
                "ultimo_mes": "" if valores.empty else _mes(valores.index[-1]),
                "meses": len(valores),
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_PARES)


def _validacion_de(serie: SeriePrecio) -> str:
    """Con qué se valida una serie, dicho junto a ella."""
    for contraste in CONTRASTES:
        if contraste.serie == serie.clave:
            return (
                f"contraste mensual contra {contraste.fuente}, "
                f"+/-{formatear(contraste.tolerancia_pct, 2)} % (A-R0-12)"
            )
    ancla = {"oro": ANCLA_LBMA_ORO, "plata": ANCLA_LBMA_PLATA}.get(serie.clave)
    if ancla is not None:
        return (
            f"ancla de {ancla.mes} contra {ancla.fuente}, "
            f"+/-{formatear(ancla.tolerancia_pct, 2)} % (A-R0-16)"
        )
    return (
        "sin gate de nivel: no hay ancla de LBMA transcrita (A-R0-16); solo un "
        "control de banda contra los extremos trimestrales que publica LBMA"
    )


def tabla_series(precios: pd.DataFrame) -> pd.DataFrame:
    """Las cinco series y lo que hay que decir junto a cada una.

    Es donde va la atribución que exigen las licencias, el estado de cada serie
    y con qué se valida. Los valores de las que no se publican no están acá.
    """
    filas = []
    for serie in SERIES_PRECIO:
        valores = precios[serie.clave].dropna()
        filas.append(
            {
                "serie": serie.clave,
                "nombre": serie.nombre,
                "publicada": "sí" if serie.publicable else "no",
                "estado": serie.estado,
                "unidad": serie.unidad,
                "fuente": serie.descarga.descripcion,
                "licencia": serie.descarga.licencia,
                "atribucion": serie.descarga.atribucion,
                "validacion": _validacion_de(serie),
                "supuestos": " ".join(serie.supuestos),
                "primer_mes": "" if valores.empty else _mes(valores.index[0]),
                "ultimo_mes": "" if valores.empty else _mes(valores.index[-1]),
                "meses": len(valores),
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_SERIES_INFO)


def tabla_interna(precios: pd.DataFrame, pares: pd.DataFrame) -> pd.DataFrame:
    """Lo que se calcula y no se publica. Va al directorio ignorado por git."""
    columnas = [serie.clave for serie in SERIES_PRECIO if not serie.publicable]
    columnas += [par.clave for par in PARES if not par_publicable(par)]
    junta = precios.join(pares)[columnas]
    junta = junta.loc[junta.notna().any(axis=1)]
    tabla = pd.DataFrame({"mes": [_mes(mes) for mes in junta.index]})
    for columna in columnas:
        tabla[columna] = junta[columna].to_numpy()
    return tabla


# --- Contrastes (A-R0-12) -----------------------------------------------------


@dataclass(frozen=True)
class ResultadoContraste:
    """Una serie contra su segunda fuente, mes a mes."""

    contraste: Contraste
    meses: int
    mediana_pct: float | None
    maxima_pct: float | None
    peor_mes: str | None
    valor_serie: float | None
    valor_contraste: float | None
    fuera: list[str]

    @property
    def ok(self) -> bool:
        """Sin meses comunes no hay contraste, y sin contraste no hay gate."""
        return self.meses > 0 and not self.fuera

    def resumen(self) -> str:
        nombre = SERIES_POR_CLAVE[self.contraste.serie].nombre
        if self.meses == 0:
            return f"FALLA - {nombre}: ningún mes en común con {self.contraste.fuente}"
        # A-R0-12: de una serie que no se publica no queda escrito ningún nivel,
        # ni el propio ni el de contraste. Solo cuántos meses, la mediana, y la
        # fecha y la diferencia del mes que más se aparta.
        niveles = ""
        if SERIES_POR_CLAVE[self.contraste.serie].publicable:
            niveles = (
                f" ({formatear(self.valor_serie, 4)} contra "
                f"{formatear(self.valor_contraste, 4)})"
            )
        linea = (
            f"{'OK' if self.ok else 'FALLA'} - {nombre} contra {self.contraste.fuente}: "
            f"{self.meses} meses, diferencia mediana {formatear(self.mediana_pct, 3)} %, "
            f"máxima {formatear(self.maxima_pct, 3)} % en {self.peor_mes}{niveles}, "
            f"tolerancia +/-{formatear(self.contraste.tolerancia_pct, 2)} %"
        )
        if self.fuera:
            linea += f"; {len(self.fuera)} meses fuera: {', '.join(self.fuera[:6])}"
            if len(self.fuera) > 6:
                linea += f" y {len(self.fuera) - 6} más"
        return linea


def contrastar(serie: pd.Series, referencia: pd.Series, contraste: Contraste) -> ResultadoContraste:
    """Compara los meses comunes. Cada mes tiene que cerrar, no el promedio."""
    comunes = serie.dropna().index.intersection(referencia.dropna().index)
    if contraste.desde is not None:
        comunes = comunes[comunes >= pd.Timestamp(contraste.desde + "-01")]
    if len(comunes) == 0:
        return ResultadoContraste(contraste, 0, None, None, None, None, None, [])

    diferencia = (serie.loc[comunes] / referencia.loc[comunes] - 1.0) * 100.0
    absoluta = diferencia.abs()
    peor = absoluta.idxmax()
    fuera = [
        f"{_mes(mes)} ({formatear(valor, 3)} %)"
        for mes, valor in diferencia[absoluta > contraste.tolerancia_pct].items()
    ]
    return ResultadoContraste(
        contraste=contraste,
        meses=len(comunes),
        mediana_pct=float(absoluta.median()),
        maxima_pct=float(absoluta.max()),
        peor_mes=_mes(peor),
        valor_serie=float(serie.loc[peor]),
        valor_contraste=float(referencia.loc[peor]),
        fuera=fuera,
    )


def _hace_anios(fecha: date, anios: int) -> date:
    try:
        return fecha.replace(year=fecha.year - anios)
    except ValueError:  # 29 de febrero
        return fecha.replace(year=fecha.year - anios, day=28)


def obtener_referencias(fecha_descarga: date) -> dict[str, pd.Series]:
    """Baja las tres fuentes de contraste y las lleva a la misma convención.

    Nada de lo que se baja acá se guarda. Los dos lados del contraste pasan por
    `promedio_mensual`, para comparar promedios mensuales con promedios mensuales.
    """
    sp500 = fuentes_precios.contraste_fred_diario(CONTRASTE_SP500, "SP500")
    nasdaq = fuentes_precios.contraste_nasdaq(
        CONTRASTE_NASDAQ,
        _hace_anios(fecha_descarga, VENTANA_CONTRASTE_NASDAQ_ANIOS),
        fecha_descarga,
    )
    btc = fuentes_precios.contraste_bitstamp(
        CONTRASTE_BTC, date.fromisoformat(CONTRASTE_BTC.desde + "-01"), fecha_descarga
    )
    return {
        "sp500": promedio_mensual(sp500, dias_calendario=False)[0],
        "nasdaq": promedio_mensual(nasdaq, dias_calendario=False)[0],
        "btc": promedio_mensual(btc, dias_calendario=True)[0],
    }


# --- Oro y plata: ancla y bandas (A-R0-16) ------------------------------------


def verificar_ancla(
    mensual: pd.Series, ancla: AnclaMensual | None, nombre: str, tolerancia_pct: float
) -> tuple[bool, str]:
    """El gate de nivel de un metal, contra un valor transcrito a mano."""
    if ancla is None:
        return True, (
            f"NO MEDIDO (A-R0-16) - {nombre}: no hay ancla de LBMA transcrita; la serie "
            f"se publica sin gate de nivel. Tolerancia ya fijada: +/-{formatear(tolerancia_pct, 2)} %"
        )
    mes = pd.Timestamp(ancla.mes + "-01")
    if mes not in mensual.index or pd.isna(mensual[mes]):
        return False, f"FALLA - {nombre}: el mes del ancla, {ancla.mes}, no está en la serie"
    diferencia = (mensual[mes] / ancla.valor - 1.0) * 100.0
    ok = abs(diferencia) <= ancla.tolerancia_pct
    return ok, (
        f"{'OK' if ok else 'FALLA'} - {nombre} {ancla.mes}: {formatear(mensual[mes], 4)} contra "
        f"{formatear(ancla.valor, 4)} de {ancla.fuente}, diferencia {formatear(diferencia, 3)} %, "
        f"tolerancia +/-{formatear(ancla.tolerancia_pct, 2)} %"
    )


def verificar_bandas(
    precios: pd.DataFrame, bandas: tuple[BandaTrimestral, ...]
) -> tuple[bool, list[str]]:
    """Un promedio mensual no puede caer fuera de los extremos de su trimestre."""
    todo_ok, lineas = True, []
    for banda in bandas:
        nombre = SERIES_POR_CLAVE[banda.serie].nombre
        for etiqueta in banda.meses:
            mes = pd.Timestamp(etiqueta + "-01")
            valor = precios[banda.serie].get(mes)
            if valor is None or pd.isna(valor):
                lineas.append(f"sin dato - {nombre} {etiqueta}: el mes no está en la serie")
                continue
            dentro = banda.minimo <= valor <= banda.maximo
            todo_ok = todo_ok and dentro
            lineas.append(
                f"{'OK' if dentro else 'FALLA'} - {nombre} {etiqueta}: {formatear(valor, 2)} "
                f"{'dentro' if dentro else 'FUERA'} de [{formatear(banda.minimo, 2)}, "
                f"{formatear(banda.maximo, 2)}] ({banda.fuente})"
            )
    return todo_ok, lineas


# --- Changelog ----------------------------------------------------------------


@dataclass
class EntradaRatios:
    """Una corrida de los ratios, tal como queda en el changelog."""

    fecha_corrida: date
    descargas: list[str]
    series: list[str]
    descartados: list[str]
    pares: list[str]
    agregados: list[str]
    revisiones: list[str]
    contrastes: list[str]
    metales: list[str]
    notas: list[str] = field(default_factory=list)

    @property
    def titulo(self) -> str:
        return f"{self.fecha_corrida.isoformat()} · ratios"

    def render(self) -> str:
        lineas = [f"## {self.titulo}", ""]

        def bloque(encabezado: str, items: list[str], vacio: str) -> None:
            if not items:
                lineas.append(f"- {encabezado}: {vacio}")
                return
            lineas.append(f"- {encabezado}:")
            lineas.extend(f"  - {item}" for item in items)

        bloque("Descargas", self.descargas, "ninguna")
        bloque("Series, en meses completos", self.series, "ninguna")
        bloque("Meses descartados", self.descartados, "ninguno")
        bloque("Pares", self.pares, "ninguno")
        if self.agregados:
            sufijo = "" if len(self.agregados) <= 5 else f" (últimos 5 de {len(self.agregados)})"
            lineas.append(
                f"- Meses agregados: {len(self.agregados)} [{', '.join(self.agregados[-5:])}]{sufijo}"
            )
        else:
            lineas.append("- Meses agregados: 0")
        bloque("Revisiones de datos históricos", self.revisiones, "ninguna")
        bloque("Contrastes", self.contrastes, "ninguno")
        bloque("Oro y plata", self.metales, "sin controles")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


def _leer_publicado(ruta: Path) -> pd.DataFrame | None:
    """Una salida de la corrida anterior, con `fecha` para comparar por fecha."""
    if not ruta.exists():
        return None
    tabla = pd.read_csv(ruta)
    tabla["fecha"] = pd.to_datetime(tabla["mes"] + "-01")
    return tabla


def _con_fecha(tabla: pd.DataFrame) -> pd.DataFrame:
    copia = tabla.copy()
    copia["fecha"] = pd.to_datetime(copia["mes"] + "-01")
    return copia


def _ancho(largo: pd.DataFrame | None) -> pd.DataFrame | None:
    """Los ratios en una columna por par, para compararlos fecha por fecha."""
    if largo is None or largo.empty:
        return None
    return largo.pivot(index="fecha", columns="par", values="valor").reset_index()


# --- Corrida ------------------------------------------------------------------


@dataclass
class Fuentes:
    """Lo que entregan las cuatro descargas, antes de recortar a meses completos."""

    registros: list[RegistroDescarga]
    oro: pd.Series
    plata: pd.Series
    pink_sheet_actualizada: date | None
    sp500: pd.Series
    shiller_actualizada: date | None
    nasdaq_diaria: pd.Series
    btc_diaria: pd.Series


def cargar_fuentes(fecha_descarga: date) -> Fuentes:
    manifiesto = fuentes_precios.leer_manifiesto(ARCHIVO_DESCARGAS)
    registros: dict[str, RegistroDescarga] = {}
    try:
        for descarga in (
            DESCARGA_PINK_SHEET,
            DESCARGA_SHILLER,
            DESCARGA_NASDAQCOM,
            DESCARGA_COIN_METRICS,
        ):
            registros[descarga.clave] = fuentes_precios.descargar(
                descarga, fecha_descarga, DIR_CRUDO, DIR_CRUDO_PRIVADO, manifiesto
            )
    finally:
        # El manifiesto registra lo que se bajó, cierre o no la validación.
        if registros:
            fuentes_precios.actualizar_manifiesto(ARCHIVO_DESCARGAS, list(registros.values()))

    pink = fuentes_precios.leer_pink_sheet(registros[DESCARGA_PINK_SHEET.clave].ruta)
    return Fuentes(
        registros=list(registros.values()),
        oro=pink.oro,
        plata=pink.plata,
        # La fecha que la propia planilla declara manda sobre la de la cabecera HTTP.
        pink_sheet_actualizada=pink.actualizada
        or registros[DESCARGA_PINK_SHEET.clave].actualizada,
        sp500=fuentes_precios.leer_shiller(registros[DESCARGA_SHILLER.clave].ruta),
        shiller_actualizada=registros[DESCARGA_SHILLER.clave].actualizada,
        nasdaq_diaria=fuentes_precios.leer_fred_diario(
            registros[DESCARGA_NASDAQCOM.clave].ruta, DESCARGA_NASDAQCOM.clave
        ),
        btc_diaria=fuentes_precios.leer_coin_metrics(registros[DESCARGA_COIN_METRICS.clave].ruta),
    )


def construir_precios(fuentes: Fuentes) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Las cinco series, en meses completos, y lo que se descartó de cada una."""
    verificar_base_nasdaq(fuentes.nasdaq_diaria)
    mensuales = {
        "oro": meses_completos(fuentes.oro, fuentes.pink_sheet_actualizada),
        "plata": meses_completos(fuentes.plata, fuentes.pink_sheet_actualizada),
        "btc": promedio_mensual(fuentes.btc_diaria, dias_calendario=True),
        "sp500": meses_completos(fuentes.sp500, fuentes.shiller_actualizada),
        "nasdaq": promedio_mensual(fuentes.nasdaq_diaria, dias_calendario=False),
    }
    columnas, descartados = {}, {}
    for serie in SERIES_PRECIO:
        mensual, fuera = mensuales[serie.clave]
        mensual, antes = desde_el_mes(mensual, serie)
        verificar_banda(mensual, serie)
        columnas[serie.clave] = mensual
        descartados[serie.clave] = fuera + antes
    precios = pd.DataFrame(columnas).sort_index()
    precios.index.name = "mes"
    return precios, descartados


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.ratios",
        description="Construye y actualiza los precios mensuales y los ratios de la fase R.",
    )
    analizador.add_argument(
        "--fecha-descarga",
        type=date.fromisoformat,
        default=date.today(),
        help="Fecha de la descarga a usar (AAAA-MM-DD). Permite rehacer una corrida "
        "anterior a partir de los crudos ya guardados.",
    )
    fecha_descarga = analizador.parse_args(argv).fecha_descarga

    asegurar_directorios(DIR_CRUDO, DIR_CRUDO_PRIVADO, DIR_SERIES, DIR_SERIES_PRIVADO)

    try:
        fuentes = cargar_fuentes(fecha_descarga)
        precios, descartados = construir_precios(fuentes)
        referencias = obtener_referencias(fecha_descarga)
    except ErrorDeFuente as error:
        print(f"ERROR DE FUENTE: {error}", file=sys.stderr)
        return CODIGO_ERROR_FUENTE

    pares = calcular_pares(precios)

    lineas_descargas = [registro.linea() for registro in fuentes.registros]
    lineas_series = [
        f"{serie.nombre}: {_mes(precios[serie.clave].first_valid_index())} a "
        f"{_mes(precios[serie.clave].last_valid_index())}, "
        f"{precios[serie.clave].notna().sum()} meses, "
        f"{'se publica' if serie.publicable else 'se calcula y no se publica'} "
        f"({serie.descarga.licencia}; {', '.join(serie.supuestos)})"
        for serie in SERIES_PRECIO
    ]
    lineas_descartados = [
        f"{SERIES_POR_CLAVE[clave].nombre} | {motivo}"
        for clave, motivos in descartados.items()
        for motivo in motivos
    ]

    print("Descargas")
    for linea in lineas_descargas:
        print(f"  {linea}")
    print("Series")
    for linea in lineas_series:
        print(f"  {linea}")

    contrastes = [
        contrastar(precios[contraste.serie], referencias[contraste.serie], contraste)
        for contraste in (CONTRASTE_SP500, CONTRASTE_NASDAQ, CONTRASTE_BTC)
    ]
    ancla_oro_ok, linea_ancla_oro = verificar_ancla(
        precios["oro"], ANCLA_LBMA_ORO, "Oro", TOLERANCIA_ANCLA_ORO_PCT
    )
    ancla_plata_ok, linea_ancla_plata = verificar_ancla(
        precios["plata"], ANCLA_LBMA_PLATA, "Plata", TOLERANCIA_ANCLA_PLATA_PCT
    )
    bandas_ok, lineas_bandas = verificar_bandas(precios, BANDAS_LBMA)
    lineas_contrastes = [resultado.resumen() for resultado in contrastes]
    lineas_metales = [linea_ancla_oro, linea_ancla_plata] + lineas_bandas

    print("Contrastes")
    for linea in lineas_contrastes:
        print(f"  {linea}")
    print("Oro y plata")
    for linea in lineas_metales:
        print(f"  {linea}")

    if not (all(r.ok for r in contrastes) and ancla_oro_ok and ancla_plata_ok and bandas_ok):
        print("", file=sys.stderr)
        print(
            "La corrida se detiene: un contraste no cerró dentro de su tolerancia. No se "
            "escribió ninguna serie ni el changelog. El manifiesto de descargas sí quedó "
            "actualizado.",
            file=sys.stderr,
        )
        print(
            "No ajustar la tolerancia para que cuadre (A-R0-12). Revisar, en este orden: "
            "la fuente (¿cambió de archivo, de unidad o de definición?), la convención "
            "(¿los dos lados son promedios mensuales de cierres diarios?) y el mes (¿está "
            "completo en las dos fuentes?).",
            file=sys.stderr,
        )
        return CODIGO_VALIDACION_FALLIDA

    publicada_precios = tabla_precios(precios)
    publicada_ratios = tabla_ratios(pares)
    publicada_pares = tabla_pares(pares)
    interna = tabla_interna(precios, pares)

    previa_precios = _leer_publicado(ARCHIVO_PRECIOS)
    previa_ratios = _leer_publicado(ARCHIVO_RATIOS)
    nueva_precios = _con_fecha(publicada_precios)
    revisiones = bitacora.detectar_revisiones(
        previa_precios, nueva_precios, ["oro_usd_oz", "plata_usd_oz", "btc_usd"], EPSILON_REVISION_PRECIOS
    )
    nueva_ratios = _ancho(_con_fecha(publicada_ratios))
    if nueva_ratios is not None:
        revisiones += bitacora.detectar_revisiones(
            _ancho(previa_ratios),
            nueva_ratios,
            [par.clave for par in PARES if par_publicable(par)],
            EPSILON_REVISION_RATIOS,
        )
    agregados = [_mes(f) for f in bitacora.filas_agregadas(previa_precios, nueva_precios)]

    escribir_csv_determinista(publicada_precios, ARCHIVO_PRECIOS, COLUMNAS_PRECIOS, FORMATO_RATIOS)
    escribir_csv_determinista(publicada_ratios, ARCHIVO_RATIOS, COLUMNAS_RATIOS, FORMATO_RATIOS)
    escribir_csv_determinista(publicada_pares, ARCHIVO_PARES, COLUMNAS_PARES, FORMATO_RATIOS)
    escribir_csv_determinista(
        tabla_series(precios), ARCHIVO_SERIES_INFO, COLUMNAS_SERIES_INFO, FORMATO_RATIOS
    )
    escribir_csv_determinista(interna, ARCHIVO_INTERNO, COLUMNAS_INTERNO, FORMATO_RATIOS)

    lineas_pares = [
        f"{fila.nombre}: {fila.estado}"
        + (f", {fila.primer_mes} a {fila.ultimo_mes}, {fila.meses} meses" if fila.meses else "")
        for fila in publicada_pares.itertuples()
    ]
    notas = [
        "los crudos que no se pueden redistribuir y las series que no se publican están "
        "fuera del repositorio (A-R0-15); de las fuentes de contraste no se guarda nada "
        "(A-R0-12)",
    ]
    if previa_precios is None:
        notas.insert(0, "primera publicación de las series: no hay corrida anterior con que comparar")

    entrada = EntradaRatios(
        fecha_corrida=fecha_descarga,
        descargas=[
            f"{registro.descarga.clave}: {registro.url}, sha256 {registro.sha256}"
            + (f", actualizada el {registro.actualizada}" if registro.actualizada else "")
            for registro in fuentes.registros
        ],
        series=lineas_series,
        descartados=lineas_descartados,
        pares=lineas_pares,
        agregados=agregados,
        revisiones=[str(revision) for revision in revisiones],
        contrastes=lineas_contrastes,
        metales=lineas_metales,
        notas=notas,
    )
    cambio = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Pares")
    for linea in lineas_pares:
        print(f"  {linea}")
    print("Salidas")
    print(f"  {ARCHIVO_PRECIOS} ({len(publicada_precios)} meses)")
    print(f"  {ARCHIVO_RATIOS} ({len(publicada_ratios)} filas)")
    print(f"  {ARCHIVO_PARES}")
    print(f"  {ARCHIVO_SERIES_INFO}")
    print(f"  {ARCHIVO_DESCARGAS}")
    print(f"  {ARCHIVO_INTERNO} (fuera del repositorio)")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio else 'sin cambios'})")
    print("Resumen")
    print(f"  Meses agregados: {len(agregados)}")
    print(f"  Revisiones históricas: {len(revisiones)}")
    for revision in revisiones[:10]:
        print(f"    {revision}")
    if len(revisiones) > 10:
        print(f"    ... y {len(revisiones) - 10} más (ver el changelog)")
    print(f"  Meses descartados: {len(lineas_descartados)}")
    for linea in lineas_descartados:
        print(f"    {linea}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
