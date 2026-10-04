"""Fase R - Precios mensuales y ratios.

Cinco series —oro, plata, BTC, S&P 500 y Nasdaq Composite— llevadas a una sola
convención, el promedio mensual de cierres diarios (A-R0-1), y los cinco pares
del sitio.

Un comando hace todo:

    python -m senales.ratios

descarga, deja constancia de cada descarga en el manifiesto, lleva cada serie a
meses completos, calcula los pares, valida cada serie contra una segunda fuente,
escribe las salidas y actualiza el changelog.

No todo lo que se calcula se publica. Una serie se publica si su licencia lo
permite sin interpretarla y si su validación externa cerró (A-R0-14). Lo demás
se calcula igual, queda fuera del repositorio y se publica como NO MEDIDO, con
el motivo. Si el contraste de BTC o de un índice no cierra, la corrida se
detiene sin escribir ninguna serie.

El oro y la plata se comparan además, mes a mes, contra el FMI (A-R0-20). Ese
control no detiene la corrida: el mes que pasa del umbral se publica sin
cambios, marcado como valor en disputa, y queda fuera de las métricas.
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
    ANCLAS_USGS,
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
    CONTRASTE_FMI_DENTRO,
    CONTRASTE_FMI_SIN_COMPARAR,
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
    FMI_COPIA,
    FORMATO_RATIOS,
    MINIMO_ANIOS_GATE,
    NASDAQ_FECHA_BASE,
    NASDAQ_VALOR_BASE,
    NO_MEDIDO_PERMISO,
    NO_MEDIDO_SIN_VALIDACION,
    ORO_DEFINICION_ANTES,
    ORO_DEFINICION_DESPUES,
    ORO_QUIEBRE_DEFINICION,
    PARES,
    PINK_SHEET_CONGELADA,
    SERIES_PRECIO,
    TOLERANCIA_GATE_ORO_PCT,
    TOLERANCIA_GATE_PLATA_PCT,
    UMBRAL_DISPUTA_PCT,
    UMBRAL_ERROR_REDONDEO_PCT,
    VALOR_EN_DISPUTA,
    VENTANA_CONTRASTE_NASDAQ_ANIOS,
    AnclaAnual,
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

# Los metales se validan con el gate anual (A-R0-16); el resto, con un contraste
# mensual (A-R0-12).
TOLERANCIAS_GATE = {"oro": TOLERANCIA_GATE_ORO_PCT, "plata": TOLERANCIA_GATE_PLATA_PCT}


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


def verificar_redondeo(mensual: pd.Series, serie: SeriePrecio) -> None:
    """La precisión de una fuente que redondea se comprueba, no se asume.

    El error por redondeo que se publica junto a cada valor (A-R0-17) sale del
    paso con que la fuente redondea. Si la fuente cambia de precisión, ese error
    deja de ser cierto, y la corrida se detiene en vez de publicar una cota falsa.
    """
    if serie.medio_paso_redondeo is None:
        return
    paso = 2.0 * serie.medio_paso_redondeo
    cociente = mensual / paso
    fuera = mensual[(cociente - cociente.round()).abs() > 1e-6]
    if not fuera.empty:
        muestra = ", ".join(f"{_mes(m)}={v!r}" for m, v in fuera.head(3).items())
        raise ErrorDeFuente(
            f"{serie.nombre}: {len(fuera)} valores no son múltiplos de {paso} ({muestra}). La "
            "fuente cambió la precisión con que publica la serie: el error por redondeo "
            "declarado ya no vale. Releer la fuente y actualizar configuracion.py y "
            "SUPUESTOS.md (A-R0-9, A-R0-17)."
        )


def error_redondeo_pct(mensual: pd.Series, medio_paso: pd.Series) -> pd.Series:
    """Error máximo de cada valor por el redondeo de la fuente, en porcentaje.

    Es medio paso de redondeo sobre el valor. El medio paso va mes por mes,
    porque depende de qué edición de la fuente se usó en cada uno (A-R0-19):
    0.5 para el oro y 0.05 para la plata en la edición vigente, y 0 donde la
    fuente no redondea.
    """
    return medio_paso.reindex(mensual.index).fillna(0.0) / mensual * 100.0


def errores_de_pares(precios: pd.DataFrame, pasos: pd.DataFrame) -> pd.DataFrame:
    """Error máximo de cada ratio por redondeo: la suma de los de sus dos lados.

    Es la cota de primer orden del error relativo de un cociente.
    """
    errores = pd.DataFrame(index=precios.index)
    for par in PARES:
        errores[par.clave] = sum(
            error_redondeo_pct(precios[lado], pasos[lado])
            for lado in (par.numerador, par.denominador)
        )
    return errores


# --- A-R0-19: empalme de las dos ediciones del Pink Sheet ---------------------


@dataclass(frozen=True)
class ResultadoEmpalme:
    """Si redondear la edición congelada reproduce la vigente, mes por mes."""

    serie: str
    meses: int
    empates: list[str]
    fuera: list[str]

    @property
    def ok(self) -> bool:
        return self.meses > 0 and not self.fuera

    def resumen(self) -> str:
        nombre = SERIES_POR_CLAVE[self.serie].nombre
        if self.meses == 0:
            return f"FALLA - {nombre}: las dos ediciones no tienen ningún mes en común"
        linea = (
            f"{'OK' if self.ok else 'FALLA'} - {nombre}: redondear la edición del "
            f"{PINK_SHEET_CONGELADA.fecha_edicion} reproduce la vigente en "
            f"{self.meses - len(self.fuera)} de {self.meses} meses superpuestos"
        )
        if self.empates:
            linea += (
                f"; {len(self.empates)} {'queda' if len(self.empates) == 1 else 'quedan'} "
                "exactamente a medio paso de redondeo: "
                + ", ".join(self.empates)
            )
        if self.fuera:
            linea += f"; NO coinciden {len(self.fuera)}: " + ", ".join(self.fuera[:8])
            if len(self.fuera) > 8:
                linea += f" y {len(self.fuera) - 8} más"
        return linea


def controlar_empalme(
    congelada: pd.Series, vigente: pd.Series, serie: SeriePrecio
) -> ResultadoEmpalme:
    """Redondear la edición congelada tiene que reproducir la vigente.

    Es lo que justifica empalmarlas: son la misma serie, publicada con distinta
    precisión. Un mes coincide si la edición congelada queda a no más de medio
    paso de redondeo de la vigente. Los que quedan exactamente a medio paso —un
    valor terminado en ,5 justo— se aceptan y se listan: ahí las dos formas de
    redondear son válidas. Cualquier otro desvío quiere decir que el Banco
    Mundial revisó ese mes después de congelada la edición, y la corrida se
    detiene.
    """
    medio_paso = serie.medio_paso_redondeo or 0.0
    comunes = congelada.dropna().index.intersection(vigente.dropna().index)
    distancia = (congelada.loc[comunes] - vigente.loc[comunes]).abs()
    holgura = 1e-9
    empates = distancia[(distancia - medio_paso).abs() <= holgura]
    fuera = distancia[distancia > medio_paso + holgura]
    return ResultadoEmpalme(
        serie=serie.clave,
        meses=len(comunes),
        empates=[
            f"{_mes(mes)} ({float(congelada[mes])!r} y {float(vigente[mes])!r})"
            for mes in empates.index
        ],
        fuera=[
            f"{_mes(mes)} ({float(congelada[mes])!r} y {float(vigente[mes])!r})"
            for mes in fuera.index
        ],
    )


def empalmar(congelada: pd.Series, vigente: pd.Series, ultimo_mes: str) -> pd.Series:
    """La edición congelada hasta `ultimo_mes`, y la vigente desde el mes siguiente."""
    corte = pd.Timestamp(ultimo_mes + "-01")
    if congelada.empty or congelada.index[-1] < corte:
        raise ErrorDeFuente(
            f"la edición congelada llega hasta {_mes(congelada.index[-1]) if len(congelada) else 'ningún mes'} "
            f"y el empalme la necesita hasta {ultimo_mes}"
        )
    serie = pd.concat([congelada[congelada.index <= corte], vigente[vigente.index > corte]])
    serie.index.name = "mes"
    return serie


def medio_paso_publicado(valor: float) -> float:
    """Media unidad del último decimal con que un valor está publicado.

    35.27 está publicado al centavo: medio paso 0.005. 36.0 está publicado al
    dólar: medio paso 0.5. No se supone que un valor que termina en cero tenga
    más precisión de la que muestra; es la lectura conservadora.
    """
    if pd.isna(valor):
        return 0.0
    texto = repr(float(valor))
    decimales = 0 if texto.endswith(".0") or "e" in texto else len(texto.split(".")[1])
    return 0.5 * 10.0**-decimales


def medios_pasos(precios: pd.DataFrame, ultimo_mes_congelada: str) -> pd.DataFrame:
    """Medio paso de redondeo de cada valor, según la edición de la que salió.

    La edición vigente del Pink Sheet declara su precisión: el oro al dólar y la
    plata a un decimal. La edición congelada no declara ninguna y trae cada mes
    con los decimales que tenga, de ninguno a once: ahí el medio paso es el del
    último decimal publicado de ese valor. Una fuente que no redondea aporta 0.
    """
    corte = pd.Timestamp(ultimo_mes_congelada + "-01")
    pasos = pd.DataFrame(0.0, index=precios.index, columns=precios.columns)
    congelados = pasos.index <= corte
    for serie in SERIES_PRECIO:
        if serie.medio_paso_redondeo is None:
            continue
        pasos.loc[~congelados, serie.clave] = serie.medio_paso_redondeo
        pasos.loc[congelados, serie.clave] = (
            precios.loc[congelados, serie.clave].map(medio_paso_publicado).to_numpy()
        )
    return pasos


def apto_desde(error: pd.Series) -> str:
    """Primer mes del tramo final en que el ratio es apto para métricas sin
    interrupción. Vacío si el último mes no lo es.
    """
    error = error.dropna()
    no_aptos = error[error > UMBRAL_ERROR_REDONDEO_PCT]
    if error.empty or (not no_aptos.empty and no_aptos.index[-1] == error.index[-1]):
        return ""
    if no_aptos.empty:
        return _mes(error.index[0])
    return _mes(error.index[error.index > no_aptos.index[-1]][0])


def meses_aptos(error: pd.Series, en_disputa: pd.Series | None = None) -> pd.Series:
    """Qué meses de un ratio entran a una métrica (A-R0-17, A-R0-20).

    Los del tramo final sin interrupción, no todos los que cumplen el umbral de
    a uno. Un mes suelto que lo cumple antes de ese tramo queda afuera: lo cumple
    porque el metal estaba caro ese mes, y elegir los meses por el nivel del
    precio sesga cualquier percentil que se calcule con ellos.

    Un mes con un valor en disputa sale, y no corta el tramo: es una exclusión
    puntual y declarada, no un hueco de precisión. Los meses que lo siguen y los
    que lo preceden dentro del tramo siguen siendo aptos.
    """
    desde = apto_desde(error)
    if not desde:
        return pd.Series(False, index=error.index)
    aptos = pd.Series(error.index >= pd.Timestamp(desde + "-01"), index=error.index)
    if en_disputa is not None:
        aptos &= ~en_disputa.reindex(error.index, fill_value=False).astype(bool)
    return aptos


# --- A-R0-20: control mensual del oro y la plata contra el FMI -----------------


@dataclass(frozen=True)
class Disputa:
    """Un mes en que el Pink Sheet y el FMI se apartan más que el umbral."""

    mes: str
    valor: float  # el del Pink Sheet, que es el que se publica, sin cambios
    referencia: float  # el del FMI
    diferencia_pct: float  # medida sobre el valor del FMI

    def detalle(self) -> str:
        return (
            f"Pink Sheet {self.valor!r}, FMI {round(self.referencia, 4)!r}, "
            f"diferencia {formatear(self.diferencia_pct, 3)} %"
        )

    def marca(self) -> str:
        """Lo que acompaña al valor en precios_mensuales.csv."""
        return f"{VALOR_EN_DISPUTA}: {self.detalle()}"


@dataclass(frozen=True)
class ResultadoFMI:
    """Una serie del Pink Sheet contra la del FMI, sobre todos los meses en común."""

    serie: str
    umbral_pct: float
    comparados: tuple[str, ...]
    mediana_pct: float | None
    disputas: tuple[Disputa, ...]

    def resumen(self) -> str:
        nombre = SERIES_POR_CLAVE[self.serie].nombre
        if not self.comparados:
            return f"{nombre}: ningún mes en común con el FMI; no hay control"
        linea = (
            f"{nombre}: {len(self.comparados)} meses comparados, de {self.comparados[0]} a "
            f"{self.comparados[-1]}; diferencia mediana {formatear(self.mediana_pct, 3)} %; "
            f"umbral +/-{formatear(self.umbral_pct, 2)} %; "
        )
        if not self.disputas:
            return linea + "ningún mes en disputa"
        return (
            linea
            + f"{len(self.disputas)} {'mes' if len(self.disputas) == 1 else 'meses'} en disputa: "
            + "; ".join(f"{disputa.mes} ({disputa.detalle()})" for disputa in self.disputas)
        )

    def validacion(self) -> str:
        """El texto que acompaña a la serie en series.csv, con la atribución al FMI."""
        return (
            f"control mensual contra el FMI, +/-{formatear(self.umbral_pct, 2)} % (A-R0-20): "
            f"{len(self.disputas)} de {len(self.comparados)} meses comparados quedan como "
            f"{VALOR_EN_DISPUTA}. {FMI_COPIA.descarga.atribucion}"
        )


def comparar_con_fmi(
    mensual: pd.Series, referencia: pd.Series, serie: str, umbral_pct: float
) -> ResultadoFMI:
    """Compara todos los meses que el Pink Sheet y el FMI tienen en común.

    No es un gate: no cierra ni deja de cerrar, y no detiene la corrida. Dice
    qué meses quedan en disputa. Tampoco decide cuál de las dos fuentes tiene
    razón: el valor publicado sigue siendo el del Pink Sheet.
    """
    comunes = mensual.dropna().index.intersection(referencia.dropna().index)
    if len(comunes) == 0:
        return ResultadoFMI(serie, umbral_pct, (), None, ())
    diferencia = (mensual.loc[comunes] / referencia.loc[comunes] - 1.0) * 100.0
    fuera = diferencia[diferencia.abs() > umbral_pct]
    return ResultadoFMI(
        serie=serie,
        umbral_pct=umbral_pct,
        comparados=tuple(_mes(mes) for mes in comunes),
        mediana_pct=float(diferencia.abs().median()),
        disputas=tuple(
            Disputa(_mes(mes), float(mensual.loc[mes]), float(referencia.loc[mes]), float(valor))
            for mes, valor in fuera.items()
        ),
    )


def meses_en_disputa(comparaciones: dict[str, ResultadoFMI], indice: pd.Index) -> pd.DataFrame:
    """Por serie, qué meses tienen su valor en disputa. Una serie sin control, ninguno."""
    tabla = pd.DataFrame(False, index=indice, columns=[serie.clave for serie in SERIES_PRECIO])
    for clave, resultado in comparaciones.items():
        meses = [pd.Timestamp(disputa.mes + "-01") for disputa in resultado.disputas]
        tabla.loc[tabla.index.isin(meses), clave] = True
    return tabla


def lados_en_disputa(par: Par, disputas: pd.DataFrame | None, indice: pd.Index) -> pd.Series:
    """Qué lados de un par tienen el valor en disputa en cada mes.

    Vacío si ninguno; si no, "oro", "plata" u "oro y plata". Un ratio no es más
    firme que su lado más débil: con un lado en disputa, el mes no es apto.
    """
    if disputas is None:
        return pd.Series("", index=indice, dtype="object")
    propias = disputas.reindex(indice, fill_value=False)
    return pd.Series(
        [
            " y ".join(
                lado for lado in (par.numerador, par.denominador) if bool(propias.at[mes, lado])
            )
            for mes in indice
        ],
        index=indice,
        dtype="object",
    )


def _contraste_fmi(resultado: ResultadoFMI | None, valores: pd.Series) -> list[str]:
    """Lo que el control contra el FMI dice de cada mes publicado de un metal."""
    comparados = set() if resultado is None else set(resultado.comparados)
    marcas = {} if resultado is None else {d.mes: d.marca() for d in resultado.disputas}
    salida = []
    for mes, valor in valores.items():
        etiqueta = _mes(mes)
        if pd.isna(valor):
            salida.append("")
        elif etiqueta in marcas:
            salida.append(marcas[etiqueta])
        elif etiqueta in comparados:
            salida.append(CONTRASTE_FMI_DENTRO)
        else:
            salida.append(CONTRASTE_FMI_SIN_COMPARAR)
    return salida


def verificar_base_nasdaq(diaria: pd.Series) -> None:
    """El Nasdaq Composite vale 100 el 5 de febrero de 1971: es su unidad."""
    base = pd.Timestamp(NASDAQ_FECHA_BASE)
    if base not in diaria.index or abs(diaria[base] - NASDAQ_VALOR_BASE) > 1e-9:
        hallado = diaria.get(base, "sin dato")
        raise ErrorDeFuente(
            f"NASDAQCOM: el {NASDAQ_FECHA_BASE} debería valer {NASDAQ_VALOR_BASE} (la base "
            f"del índice) y vale {hallado}. La serie no es la que se configuró."
        )


# --- Regla de publicación (A-R0-14) -------------------------------------------
#
# Una serie se publica si pasa dos filtros: la licencia y la validación. En todo
# lo que sigue, `validadas` es el conjunto de claves de las series cuya
# validación externa cerró en esta corrida.


def serie_publicada(serie: SeriePrecio, validadas: set[str]) -> bool:
    return serie.publicable and serie.clave in validadas


def estado_de_serie(serie: SeriePrecio, validadas: set[str]) -> str:
    if not serie.publicable:
        return NO_MEDIDO_PERMISO
    if serie.clave not in validadas:
        return NO_MEDIDO_SIN_VALIDACION
    return serie.estado


def par_publicado(par: Par, validadas: set[str]) -> bool:
    return all(
        serie_publicada(SERIES_POR_CLAVE[lado], validadas)
        for lado in (par.numerador, par.denominador)
    )


def estado_del_par(par: Par, validadas: set[str]) -> str:
    """Un par no es más firme que su lado más débil.

    Si a un lado le falta el permiso, el par espera el permiso. Si le falta la
    validación, el par no tiene validación. Si un lado es una estimación, el par
    lo es.
    """
    lados = (SERIES_POR_CLAVE[par.numerador], SERIES_POR_CLAVE[par.denominador])
    if not all(lado.publicable for lado in lados):
        return NO_MEDIDO_PERMISO
    if not all(lado.clave in validadas for lado in lados):
        return NO_MEDIDO_SIN_VALIDACION
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


def _redondear(valores: pd.Series, decimales: int = 4):
    return valores.round(decimales).to_numpy()


def tabla_precios(
    precios: pd.DataFrame,
    pasos: pd.DataFrame,
    validadas: set[str],
    comparaciones: dict[str, ResultadoFMI] | None = None,
) -> pd.DataFrame:
    """Las series que se publican, con lo que hay que decir junto a cada una.

    Las columnas son siempre las mismas. La de una serie que no se publica queda
    vacía: el motivo está en series.csv.
    """
    comparaciones = comparaciones or {}
    claves = ("oro", "plata", "btc")
    visibles = precios.loc[:, list(claves)].copy()
    for clave in claves:
        if not serie_publicada(SERIES_POR_CLAVE[clave], validadas):
            visibles[clave] = float("nan")
    visibles = visibles.loc[visibles.notna().any(axis=1)]
    quiebre = pd.Timestamp(ORO_QUIEBRE_DEFINICION + "-01")

    tabla = pd.DataFrame({"mes": [_mes(mes) for mes in visibles.index]})
    tabla["oro_usd_oz"] = visibles["oro"].to_numpy()
    # A-R0-17: el error máximo por redondeo va junto a cada valor.
    tabla["oro_error_redondeo_pct"] = _redondear(error_redondeo_pct(visibles["oro"], pasos["oro"]))
    # A-R0-7: el quiebre de definición del oro va declarado fila por fila.
    tabla["oro_definicion"] = [
        "" if pd.isna(valor) else (ORO_DEFINICION_ANTES if mes < quiebre else ORO_DEFINICION_DESPUES)
        for mes, valor in visibles["oro"].items()
    ]
    # A-R0-20: un valor en disputa se publica sin cambios, y se dice.
    tabla["oro_contraste_fmi"] = _contraste_fmi(comparaciones.get("oro"), visibles["oro"])
    tabla["plata_usd_oz"] = visibles["plata"].to_numpy()
    tabla["plata_error_redondeo_pct"] = _redondear(
        error_redondeo_pct(visibles["plata"], pasos["plata"])
    )
    # A-R0-8: la plata es una estimación, y se ve.
    tabla["plata_estado"] = [
        "" if pd.isna(valor) else SERIES_POR_CLAVE["plata"].estado for valor in visibles["plata"]
    ]
    tabla["plata_contraste_fmi"] = _contraste_fmi(comparaciones.get("plata"), visibles["plata"])
    # A-R0-19: de qué edición del Pink Sheet salen los metales de cada mes.
    corte = pd.Timestamp(PINK_SHEET_CONGELADA.ultimo_mes + "-01")
    tabla["pink_sheet_edicion"] = [
        ""
        if pd.isna(oro) and pd.isna(plata)
        else (PINK_SHEET_CONGELADA.fecha_edicion.isoformat() if mes <= corte else "vigente")
        for mes, oro, plata in zip(visibles.index, visibles["oro"], visibles["plata"])
    ]
    tabla["btc_usd"] = visibles["btc"].to_numpy()
    return tabla


def tabla_ratios(
    pares: pd.DataFrame,
    errores: pd.DataFrame,
    validadas: set[str],
    disputas: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Los pares que se publican, en formato largo. Los demás no tienen filas acá.

    Cada fila lleva el error máximo del ratio por redondeo, qué lado tiene el
    valor en disputa, si alguno, y si el mes es apto para métricas (A-R0-17,
    A-R0-20). Un mes no apto se publica igual, con su error y su disputa a la
    vista; lo que no puede es entrar a un percentil, a una tendencia ni a la
    evidencia de nada.
    """
    bloques = []
    for par in PARES:
        if not par_publicado(par, validadas):
            continue
        valores = pares[par.clave].dropna()
        error = errores.loc[valores.index, par.clave]
        lados = lados_en_disputa(par, disputas, valores.index)
        bloques.append(
            pd.DataFrame(
                {
                    "mes": [_mes(mes) for mes in valores.index],
                    "par": par.clave,
                    "valor": valores.to_numpy(),
                    "error_redondeo_pct": _redondear(error),
                    "valor_en_disputa": lados.to_numpy(),
                    "apto_metricas": [
                        "sí" if apto else "no" for apto in meses_aptos(error, lados != "")
                    ],
                    "estado": estado_del_par(par, validadas),
                }
            )
        )
    if not bloques:
        return pd.DataFrame(columns=COLUMNAS_RATIOS)
    return pd.concat(bloques, ignore_index=True).sort_values(["mes", "par"], kind="stable")


def tabla_pares(
    pares: pd.DataFrame,
    errores: pd.DataFrame,
    validadas: set[str],
    disputas: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Los cinco pares, publicados o no, y hasta dónde llega cada uno.

    Es donde un par que no se muestra aparece: existe, tiene historia, y su
    estado dice qué le falta.
    """
    filas = []
    for par in PARES:
        valores = pares[par.clave].dropna()
        error = errores.loc[valores.index, par.clave]
        lados = lados_en_disputa(par, disputas, valores.index)
        filas.append(
            {
                "par": par.clave,
                "nombre": par.nombre,
                "publicado": "sí" if par_publicado(par, validadas) else "no",
                "estado": estado_del_par(par, validadas),
                "primer_mes": "" if valores.empty else _mes(valores.index[0]),
                "ultimo_mes": "" if valores.empty else _mes(valores.index[-1]),
                "meses": len(valores),
                # A-R0-17: desde qué mes el par es apto para métricas sin interrupción.
                "apto_desde": apto_desde(error),
                # A-R0-20: un mes en disputa no es apto, y no corta el tramo.
                "meses_aptos": int(meses_aptos(error, lados != "").sum()),
                "meses_en_disputa": int((lados != "").sum()),
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_PARES)


def tabla_series(
    precios: pd.DataFrame, validadas: set[str], validaciones: dict[str, str]
) -> pd.DataFrame:
    """Las cinco series y lo que hay que decir junto a cada una.

    Es donde va la atribución que exigen las licencias, el estado de cada serie
    y con qué se validó. Los valores de las que no se publican no están acá.
    """
    filas = []
    for serie in SERIES_PRECIO:
        valores = precios[serie.clave].dropna()
        filas.append(
            {
                "serie": serie.clave,
                "nombre": serie.nombre,
                "publicada": "sí" if serie_publicada(serie, validadas) else "no",
                "estado": estado_de_serie(serie, validadas),
                "unidad": serie.unidad,
                "fuente": serie.descarga.descripcion,
                "licencia": serie.descarga.licencia,
                "atribucion": serie.descarga.atribucion,
                "validacion": validaciones[serie.clave],
                "supuestos": " ".join(serie.supuestos),
                "primer_mes": "" if valores.empty else _mes(valores.index[0]),
                "ultimo_mes": "" if valores.empty else _mes(valores.index[-1]),
                "meses": len(valores),
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_SERIES_INFO)


def tabla_interna(precios: pd.DataFrame, pares: pd.DataFrame) -> pd.DataFrame:
    """Todo lo que se calcula, se publique o no. Va al directorio ignorado por git."""
    junta = precios.join(pares)
    tabla = pd.DataFrame({"mes": [_mes(mes) for mes in junta.index]})
    for columna in COLUMNAS_INTERNO[1:]:
        tabla[columna] = junta[columna].to_numpy()
    return tabla


# --- Contrastes mensuales (A-R0-12) -------------------------------------------


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


# --- Oro y plata: gate anual y bandas (A-R0-16) -------------------------------


@dataclass(frozen=True)
class ResultadoGateAnual:
    """El promedio de doce meses de un metal contra el precio anual del USGS."""

    serie: str
    tolerancia_pct: float
    anios: int
    cerrados: int
    lineas: list[str]

    @property
    def ok(self) -> bool:
        """Cierra si hay años suficientes y cerraron todos, no la mayoría."""
        return self.anios >= MINIMO_ANIOS_GATE and self.cerrados == self.anios

    def resumen(self) -> str:
        nombre = SERIES_POR_CLAVE[self.serie].nombre
        if self.anios < MINIMO_ANIOS_GATE:
            return (
                f"FALLA - {nombre}: el gate anual tiene {self.anios} años y necesita "
                f"al menos {MINIMO_ANIOS_GATE}"
            )
        return (
            f"{'OK' if self.ok else 'FALLA'} - {nombre}: gate anual contra el USGS, "
            f"{self.cerrados} de {self.anios} años dentro de "
            f"+/-{formatear(self.tolerancia_pct, 2)} %"
        )

    def validacion(self) -> str:
        """El texto que acompaña a la serie en series.csv."""
        return (
            f"gate anual contra el precio promedio del USGS (Mineral Commodity "
            f"Summaries), +/-{formatear(self.tolerancia_pct, 2)} % (A-R0-16): "
            + (
                f"cerró en {self.cerrados} de {self.anios} años"
                if self.ok
                else f"NO cerró ({self.cerrados} de {self.anios} años)"
            )
        )


def gate_anual(
    mensual: pd.Series, anclas: tuple[AnclaAnual, ...], serie: str, tolerancia_pct: float
) -> ResultadoGateAnual:
    """Promedio de los doce meses de cada año contra el valor anual transcrito.

    Un año al que le falta un mes no se promedia: cuenta como no cerrado.
    """
    nombre = SERIES_POR_CLAVE[serie].nombre
    propias = [ancla for ancla in anclas if ancla.serie == serie]
    cerrados, lineas = 0, []
    for ancla in sorted(propias, key=lambda a: a.anio):
        del_anio = mensual[mensual.index.year == ancla.anio].dropna()
        if len(del_anio) != 12:
            lineas.append(
                f"FALLA - {nombre} {ancla.anio}: la serie tiene {len(del_anio)} de 12 meses"
            )
            continue
        promedio = float(del_anio.mean())
        diferencia = (promedio / ancla.valor - 1.0) * 100.0
        dentro = abs(diferencia) <= tolerancia_pct
        cerrados += dentro
        lineas.append(
            f"{'OK' if dentro else 'FALLA'} - {nombre} {ancla.anio}: promedio de los 12 meses "
            f"{formatear(promedio, 4)} contra {formatear(ancla.valor, 2)} del USGS, "
            f"diferencia {formatear(diferencia, 3)} %, "
            f"tolerancia +/-{formatear(tolerancia_pct, 2)} %"
        )
    return ResultadoGateAnual(serie, tolerancia_pct, len(propias), cerrados, lineas)


def verificar_bandas(
    precios: pd.DataFrame, bandas: tuple[BandaTrimestral, ...]
) -> tuple[dict[str, bool], list[str]]:
    """Un promedio mensual no puede caer fuera de los extremos de su trimestre.

    Devuelve, por serie, si todas sus bandas con dato cerraron, y el detalle.
    """
    resultado, lineas = {}, []
    for banda in bandas:
        nombre = SERIES_POR_CLAVE[banda.serie].nombre
        resultado.setdefault(banda.serie, True)
        for etiqueta in banda.meses:
            mes = pd.Timestamp(etiqueta + "-01")
            valor = precios[banda.serie].get(mes)
            if valor is None or pd.isna(valor):
                lineas.append(f"sin dato - {nombre} {etiqueta}: el mes no está en la serie")
                continue
            dentro = banda.minimo <= valor <= banda.maximo
            resultado[banda.serie] = resultado[banda.serie] and dentro
            lineas.append(
                f"{'OK' if dentro else 'FALLA'} - {nombre} {etiqueta}: {formatear(valor, 2)} "
                f"{'dentro' if dentro else 'FUERA'} de [{formatear(banda.minimo, 2)}, "
                f"{formatear(banda.maximo, 2)}] ({banda.fuente})"
            )
    return resultado, lineas


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
    empalme: list[str] = field(default_factory=list)
    fmi: list[str] = field(default_factory=list)
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
        bloque("Empalme del Pink Sheet", self.empalme, "sin control")
        bloque("Pink Sheet contra FMI", self.fmi, "sin control")
        bloque("Contrastes", self.contrastes, "ninguno")
        bloque("Oro y plata", self.metales, "sin controles")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


# Hasta cuántas revisiones se listan una por una. Más que eso no es la fuente
# corrigiendo un dato: es un cambio de método, y se resume por columna.
LIMITE_REVISIONES_LISTADAS = 40


def resumir_revisiones(revisiones: list[bitacora.Revision]) -> list[str]:
    """Las revisiones, una por línea, o resumidas por columna si son demasiadas.

    Una fuente que corrige un dato viejo deja una línea por dato. Un cambio de
    método —otra edición de la fuente, otra regla de empalme— cambia cientos de
    meses a la vez, y listarlos uno por uno entierra lo que importa: cuántos
    cambiaron y cuánto cambió el que más.
    """
    if len(revisiones) <= LIMITE_REVISIONES_LISTADAS:
        return [str(revision) for revision in revisiones]

    def relativa(revision: bitacora.Revision) -> float:
        if pd.isna(revision.anterior) or pd.isna(revision.nuevo) or revision.anterior == 0:
            return float("inf")
        return abs(revision.diferencia / revision.anterior) * 100.0

    lineas = []
    for columna in dict.fromkeys(revision.columna for revision in revisiones):
        propias = [revision for revision in revisiones if revision.columna == columna]
        mayor = max(propias, key=relativa)
        lineas.append(
            f"{columna}: {len(propias)} meses cambiaron respecto de la corrida anterior; "
            f"el mayor cambio es de {formatear(relativa(mayor), 3)} % en "
            f"{_mes(mayor.fecha)} ({formatear(mayor.anterior, 4)} -> {formatear(mayor.nuevo, 4)})"
        )
    lineas.append(
        f"son {len(revisiones)} cambios, más de {LIMITE_REVISIONES_LISTADAS}: es un cambio "
        "de método y no una revisión de la fuente, y por eso va resumido por columna"
    )
    return lineas


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


def _tiene_valores(tabla: pd.DataFrame | None, columna: str) -> bool:
    return tabla is not None and columna in tabla.columns and bool(tabla[columna].notna().any())


def _columnas_comparables(
    previa: pd.DataFrame | None,
    nueva: pd.DataFrame | None,
    columnas: list[str],
    hay_corrida_previa: bool,
) -> tuple[list[str], list[str]]:
    """Separa las columnas que se pueden comparar fila por fila de las que cambiaron
    de estado: una serie que empieza o deja de publicarse no es una revisión de
    cada uno de sus meses, es un solo hecho, y se anota como tal.
    """
    if not hay_corrida_previa:
        return columnas, []
    comparables, cambios = [], []
    for columna in columnas:
        antes, ahora = _tiene_valores(previa, columna), _tiene_valores(nueva, columna)
        if antes == ahora:
            comparables.append(columna)
        else:
            cambios.append(
                f"{columna}: {'dejó de publicarse' if antes else 'empezó a publicarse'} "
                "en esta corrida"
            )
    return comparables, cambios


def _ancho(largo: pd.DataFrame | None) -> pd.DataFrame | None:
    """Los ratios en una columna por par, para compararlos fecha por fecha."""
    if largo is None or largo.empty:
        return None
    return largo.pivot(index="fecha", columns="par", values="valor").reset_index()


# --- Corrida ------------------------------------------------------------------


@dataclass
class Fuentes:
    """Lo que entregan las descargas, antes de recortar a meses completos."""

    registros: list[RegistroDescarga]
    oro: pd.Series  # edición vigente del Pink Sheet, redondeada
    plata: pd.Series
    oro_congelada: pd.Series  # edición de enero de 2025, sin redondear (A-R0-19)
    plata_congelada: pd.Series
    fmi_oro: pd.Series  # referencia del control mensual (A-R0-20)
    fmi_plata: pd.Series
    pink_sheet_actualizada: date | None
    sp500: pd.Series
    shiller_actualizada: date | None
    nasdaq_diaria: pd.Series
    btc_diaria: pd.Series


def cargar_fuentes(fecha_descarga: date) -> Fuentes:
    manifiesto = fuentes_precios.leer_manifiesto(ARCHIVO_DESCARGAS)
    registros: dict[str, RegistroDescarga] = {}
    try:
        # La edición congelada no se baja: es la copia versionada (A-R0-19).
        registros[PINK_SHEET_CONGELADA.descarga.clave] = fuentes_precios.cargar_edicion_congelada(
            PINK_SHEET_CONGELADA, DIR_CRUDO
        )
        # La copia del FMI tampoco se baja, ni siquiera si falta (A-R0-20).
        registros[FMI_COPIA.descarga.clave] = fuentes_precios.cargar_copia_manual(
            FMI_COPIA, DIR_CRUDO
        )
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
    congelada = fuentes_precios.leer_pink_sheet(
        registros[PINK_SHEET_CONGELADA.descarga.clave].ruta,
        PINK_SHEET_CONGELADA.descripcion_oro,
        PINK_SHEET_CONGELADA.descripcion_plata,
    )
    if congelada.actualizada != PINK_SHEET_CONGELADA.fecha_edicion:
        raise ErrorDeFuente(
            f"{PINK_SHEET_CONGELADA.archivo} dice haberse actualizado el "
            f"{congelada.actualizada} y la edición congelada es la del "
            f"{PINK_SHEET_CONGELADA.fecha_edicion}"
        )
    fmi = fuentes_precios.leer_fmi(registros[FMI_COPIA.descarga.clave].ruta)
    return Fuentes(
        registros=list(registros.values()),
        oro=pink.oro,
        plata=pink.plata,
        oro_congelada=congelada.oro,
        plata_congelada=congelada.plata,
        fmi_oro=fmi.oro,
        fmi_plata=fmi.plata,
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


def construir_precios(
    fuentes: Fuentes,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]], list[ResultadoEmpalme]]:
    """Las cinco series en meses completos, el medio paso de redondeo de cada valor,
    lo que se descartó de cada serie y el control del empalme del Pink Sheet.
    """
    verificar_base_nasdaq(fuentes.nasdaq_diaria)
    ultimo = PINK_SHEET_CONGELADA.ultimo_mes
    vigentes = {"oro": fuentes.oro, "plata": fuentes.plata}
    congeladas = {"oro": fuentes.oro_congelada, "plata": fuentes.plata_congelada}
    controles, metales = [], {}
    for metal in ("oro", "plata"):
        serie = SERIES_POR_CLAVE[metal]
        # La precisión declarada es la de la edición vigente, entera.
        verificar_redondeo(vigentes[metal], serie)
        controles.append(controlar_empalme(congeladas[metal], vigentes[metal], serie))
        completos, fuera = meses_completos(vigentes[metal], fuentes.pink_sheet_actualizada)
        metales[metal] = (empalmar(congeladas[metal], completos, ultimo), fuera)
    mensuales = {
        "oro": metales["oro"],
        "plata": metales["plata"],
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
    return precios, medios_pasos(precios, ultimo), descartados, controles


def _validacion_de_contraste(contraste: Contraste) -> str:
    return (
        f"contraste mensual contra {contraste.fuente}, "
        f"+/-{formatear(contraste.tolerancia_pct, 2)} % (A-R0-12): cerró"
    )


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
        precios, pasos, descartados, controles = construir_precios(fuentes)
        referencias = obtener_referencias(fecha_descarga)
    except ErrorDeFuente as error:
        print(f"ERROR DE FUENTE: {error}", file=sys.stderr)
        return CODIGO_ERROR_FUENTE

    lineas_empalme = [control.resumen() for control in controles]
    if not all(control.ok for control in controles):
        print("Empalme del Pink Sheet", file=sys.stderr)
        for linea in lineas_empalme:
            print(f"  {linea}", file=sys.stderr)
        print(
            "La corrida se detiene: redondear la edición congelada del Pink Sheet no "
            "reproduce la vigente. No se escribió ninguna serie ni el changelog. El Banco "
            "Mundial revisó meses anteriores a 2025, y el empalme ya no une dos versiones "
            "de la misma serie (A-R0-19). No se corrige a mano: hay que releer la fuente y "
            "decidir de nuevo de dónde sale ese tramo.",
            file=sys.stderr,
        )
        return CODIGO_VALIDACION_FALLIDA

    pares = calcular_pares(precios)
    errores = errores_de_pares(precios, pasos)

    # A-R0-20: el oro y la plata contra el FMI, sobre todo el historial en común.
    # No detiene la corrida: marca los meses en disputa.
    referencias_fmi = {"oro": fuentes.fmi_oro, "plata": fuentes.fmi_plata}
    comparaciones = {
        metal: comparar_con_fmi(
            precios[metal], referencias_fmi[metal], metal, UMBRAL_DISPUTA_PCT[metal]
        )
        for metal in ("oro", "plata")
    }
    disputas = meses_en_disputa(comparaciones, precios.index)
    lineas_fmi = [comparaciones[metal].resumen() for metal in ("oro", "plata")]

    # --- Validación -----------------------------------------------------------
    contrastes = [
        contrastar(precios[contraste.serie], referencias[contraste.serie], contraste)
        for contraste in CONTRASTES
    ]
    gates = {
        metal: gate_anual(precios[metal], ANCLAS_USGS, metal, TOLERANCIAS_GATE[metal])
        for metal in ("oro", "plata")
    }
    bandas_ok, lineas_bandas = verificar_bandas(precios, BANDAS_LBMA)

    lineas_descargas = [registro.linea() for registro in fuentes.registros]
    lineas_contrastes = [resultado.resumen() for resultado in contrastes]
    lineas_metales = []
    for metal in ("oro", "plata"):
        lineas_metales.append(gates[metal].resumen())
        lineas_metales.extend(gates[metal].lineas)
    lineas_metales.extend(lineas_bandas)

    print("Descargas")
    for linea in lineas_descargas:
        print(f"  {linea}")
    print("Empalme del Pink Sheet")
    for linea in lineas_empalme:
        print(f"  {linea}")
    print("Pink Sheet contra FMI")
    for linea in lineas_fmi:
        print(f"  {linea}")
    print("Contrastes")
    for linea in lineas_contrastes:
        print(f"  {linea}")
    print("Oro y plata")
    for linea in lineas_metales:
        print(f"  {linea}")

    if not all(resultado.ok for resultado in contrastes):
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

    # Los contrastes cerraron, o la corrida ya se habría detenido. Un metal queda
    # validado si cerró su gate anual y ninguna de sus bandas falló.
    validadas = {contraste.serie for contraste in CONTRASTES}
    validadas |= {
        metal for metal in ("oro", "plata") if gates[metal].ok and bandas_ok.get(metal, True)
    }
    validaciones = {c.serie: _validacion_de_contraste(c) for c in CONTRASTES}
    validaciones.update(
        {
            metal: f"{gates[metal].validacion()}; {comparaciones[metal].validacion()}"
            for metal in ("oro", "plata")
        }
    )

    sin_validar = [m for m in ("oro", "plata") if m not in validadas]
    if sin_validar:
        nombres = " y ".join(SERIES_POR_CLAVE[m].nombre.lower() for m in sin_validar)
        print("", file=sys.stderr)
        print(
            f"El gate de {nombres} no cerró. La corrida sigue, pero esas series y los pares "
            f"que las llevan se publican como \"{NO_MEDIDO_SIN_VALIDACION}\" (A-R0-14). "
            "No ensanchar la tolerancia para que cierre (A-R0-16).",
            file=sys.stderr,
        )

    # --- Salidas --------------------------------------------------------------
    lineas_series = [
        f"{serie.nombre}: {_mes(precios[serie.clave].first_valid_index())} a "
        f"{_mes(precios[serie.clave].last_valid_index())}, "
        f"{precios[serie.clave].notna().sum()} meses, "
        + (
            "se publica"
            if serie_publicada(serie, validadas)
            else f"se calcula y no se publica: {estado_de_serie(serie, validadas)}"
        )
        + f" ({serie.descarga.licencia}; {', '.join(serie.supuestos)})"
        for serie in SERIES_PRECIO
    ]
    lineas_descartados = [
        f"{SERIES_POR_CLAVE[clave].nombre} | {motivo}"
        for clave, motivos in descartados.items()
        for motivo in motivos
    ]

    publicada_precios = tabla_precios(precios, pasos, validadas, comparaciones)
    publicada_ratios = tabla_ratios(pares, errores, validadas, disputas)
    publicada_pares = tabla_pares(pares, errores, validadas, disputas)
    interna = tabla_interna(precios, pares)

    previa_precios = _leer_publicado(ARCHIVO_PRECIOS)
    previa_ratios = _leer_publicado(ARCHIVO_RATIOS)
    nueva_precios = _con_fecha(publicada_precios)
    hay_corrida_previa = previa_precios is not None
    comparables, cambios_de_estado = _columnas_comparables(
        previa_precios, nueva_precios, ["oro_usd_oz", "plata_usd_oz", "btc_usd"], hay_corrida_previa
    )
    revisiones = bitacora.detectar_revisiones(
        previa_precios, nueva_precios, comparables, EPSILON_REVISION_PRECIOS
    )
    ancha_previa, ancha_nueva = _ancho(previa_ratios), _ancho(_con_fecha(publicada_ratios))
    comparables, cambios = _columnas_comparables(
        ancha_previa, ancha_nueva, [par.clave for par in PARES], hay_corrida_previa
    )
    cambios_de_estado += cambios
    if ancha_nueva is not None:
        revisiones += bitacora.detectar_revisiones(
            ancha_previa, ancha_nueva, comparables, EPSILON_REVISION_RATIOS
        )
    agregados = [_mes(f) for f in bitacora.filas_agregadas(previa_precios, nueva_precios)]

    escribir_csv_determinista(publicada_precios, ARCHIVO_PRECIOS, COLUMNAS_PRECIOS, FORMATO_RATIOS)
    escribir_csv_determinista(publicada_ratios, ARCHIVO_RATIOS, COLUMNAS_RATIOS, FORMATO_RATIOS)
    escribir_csv_determinista(publicada_pares, ARCHIVO_PARES, COLUMNAS_PARES, FORMATO_RATIOS)
    escribir_csv_determinista(
        tabla_series(precios, validadas, validaciones),
        ARCHIVO_SERIES_INFO,
        COLUMNAS_SERIES_INFO,
        FORMATO_RATIOS,
    )
    escribir_csv_determinista(interna, ARCHIVO_INTERNO, COLUMNAS_INTERNO, FORMATO_RATIOS)

    lineas_pares = [
        f"{fila.nombre}: {fila.estado}"
        + (f", {fila.primer_mes} a {fila.ultimo_mes}, {fila.meses} meses" if fila.meses else "")
        + (
            f"; apto para métricas desde {fila.apto_desde or 'ningún mes'} "
            f"({fila.meses_aptos} meses: el tramo final con error de redondeo <= "
            f"{formatear(UMBRAL_ERROR_REDONDEO_PCT, 1)} %, A-R0-17, menos "
            f"{fila.meses_en_disputa} con un valor en disputa, A-R0-20)"
            if fila.publicado == "sí"
            else ""
        )
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
        revisiones=cambios_de_estado + resumir_revisiones(revisiones),
        contrastes=lineas_contrastes,
        metales=lineas_metales,
        empalme=lineas_empalme,
        fmi=lineas_fmi,
        notas=notas,
    )
    cambio = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Series")
    for linea in lineas_series:
        print(f"  {linea}")
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
