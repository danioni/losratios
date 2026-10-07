"""Fase D0 - El Denominador: dinero, balances de bancos centrales y tipos de cambio.

Un comando hace todo:

    python -m senales.denominador [--fecha-descarga AAAA-MM-DD]

baja (o reutiliza) los crudos del día, deja constancia de cada descarga en el
manifiesto, lleva cada serie a su convención mensual, valida cada una contra una
segunda fuente, calcula el agregado en USD, escribe las salidas y actualiza el
changelog.

Qué se publica y qué no sigue la regla de la fase R (A-R0-14): una serie se
publica si su licencia lo permite y si su gate cerró. Lo demás se calcula igual
y aparece en serie_D0.csv como NO MEDIDO, con el motivo. Las series del BCE
llegan por copia bajada a mano (A-D0-29): si falta la copia o su hash no
coincide con el manifiesto, la serie queda NO MEDIDO en esa corrida y la
corrida sigue.

Ningún valor se interpola ni se arrastra. Un hueco es un hueco.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from senales import bitacora, fuentes_denominador, fuentes_precios
from senales.configuracion import (
    ANCLAS_BALANCE_PBOC,
    ANCLAS_CHINA,
    ARCHIVO_CHANGELOG,
    ARCHIVO_D0_AGREGADO,
    ARCHIVO_D0_BALANCES,
    ARCHIVO_D0_CAMBIO,
    ARCHIVO_D0_DESCARGAS,
    ARCHIVO_D0_DINERO,
    ARCHIVO_D0_FICHAS,
    BDE_CODIGO_M2_AJUSTADA,
    BDE_CODIGO_M2_SIN_AJUSTAR,
    BOJ_CODIGO_BALANCE,
    BOJ_CODIGO_M2,
    CLAVE_DINERO_1947_1958,
    CLAVE_DINERO_1947_1958_SIN_AJUSTAR,
    CLAVES_DINERO_HISTORICO,
    COLUMNAS_D0_AGREGADO,
    COLUMNAS_D0_BALANCES,
    COLUMNAS_D0_CAMBIO,
    COLUMNAS_D0_DINERO,
    COLUMNAS_D0_FICHAS,
    CONTRASTE_BDE_AJUSTADA,
    CONTRASTE_BDE_SIN_AJUSTAR,
    CONTRASTE_BIS_CAMBIO_CN,
    CONTRASTE_BIS_CAMBIO_JP,
    CONTRASTE_BIS_CAMBIO_XM,
    CONTRASTE_ESTAT,
    CONTRASTE_FRED_WALCL,
    CONTRASTE_H6_HTML,
    DESCARGA_BCE_BALANCE,
    DESCARGA_BCE_M2_AJUSTADA,
    DESCARGA_BCE_M2_SIN_AJUSTAR,
    DESCARGA_BIS_ACTIVOS_CN,
    DESCARGA_BIS_ACTIVOS_JP,
    DESCARGA_BIS_ACTIVOS_US,
    DESCARGA_BIS_ACTIVOS_XM,
    DESCARGA_BOJ_BALANCE,
    DESCARGA_BOJ_M2,
    DESCARGA_H6,
    DESCARGA_H10,
    DESCARGA_H41,
    DESCARGA_OCDE_CHINA,
    DIR_CRUDO,
    DIR_CRUDO_PRIVADO,
    DIR_SERIES,
    ECONOMIAS_AGREGADO,
    EPSILON_REVISION_D0,
    ESTADO_DATO,
    ESTADO_ESTIMACION,
    ESTAT_INDICADOR_M2,
    FAMILIA_BALANCE,
    FAMILIA_CAMBIO,
    FAMILIA_DINERO,
    FORMATO_D0,
    JUNTA_MULTIPLICADOR_H6,
    JUNTA_MULTIPLICADOR_H10,
    JUNTA_MULTIPLICADOR_H41,
    JUNTA_SERIE_BALANCE,
    JUNTA_SERIES_H6,
    JUNTA_SERIES_H10,
    MESES_GATE_BDE,
    MINIMO_ANCLAS,
    MINIMO_COMPARACIONES_GATE,
    NO_MEDIDO_ACCESO_VEDADO,
    NO_MEDIDO_SIN_VALIDACION,
    NOMBRE_AGREGADO,
    OCDE_AREA_CHINA,
    OCDE_MEDIDA_DINERO_AMPLIO,
    SERIES_D0,
    SERIES_PENDIENTES,
    TOLERANCIA_BDE,
    TOLERANCIA_BIS_BOJ,
    TOLERANCIA_BIS_EUROSISTEMA,
    TOLERANCIA_BIS_FED,
    TOLERANCIA_CAMBIO_PCT,
    TOLERANCIA_ESTAT,
    TOLERANCIA_FRED_WALCL,
    TOLERANCIA_H6_HTML,
    AnclaMensual,
    Descarga,
    SerieD0,
)
from senales.fuentes_denominador import (
    AccesoVedado,
    CopiaFaltante,
    exigir_multiplicador,
    interpretar_bde,
    interpretar_estat,
    interpretar_tabla_h6,
    leer_csv_bce,
    leer_csv_bis_activos,
    leer_csv_bis_cambio,
    leer_csv_boj,
    leer_csv_ocde,
    leer_json,
    leer_xml_junta,
)
from senales.fuentes_fred import ErrorDeFuente
from senales.fuentes_precios import RegistroDescarga
from senales.nucleo import asegurar_directorios, escribir_csv_determinista, formatear

CODIGO_ERROR_FUENTE = 1

SERIES_POR_CLAVE: dict[str, SerieD0] = {serie.clave: serie for serie in SERIES_D0}

# Las descargas que alimentan series, y las que solo se leen para comparar.
DESCARGAS_FUENTE = (
    DESCARGA_H6,
    DESCARGA_H10,
    DESCARGA_H41,
    DESCARGA_BCE_M2_AJUSTADA,
    DESCARGA_BCE_M2_SIN_AJUSTAR,
    DESCARGA_BCE_BALANCE,
    DESCARGA_BOJ_M2,
    DESCARGA_BOJ_BALANCE,
    DESCARGA_OCDE_CHINA,
    DESCARGA_BIS_ACTIVOS_CN,
)
DESCARGAS_CONTRASTE = (
    CONTRASTE_H6_HTML,
    CONTRASTE_FRED_WALCL,
    DESCARGA_BIS_ACTIVOS_US,
    CONTRASTE_BDE_AJUSTADA,
    CONTRASTE_BDE_SIN_AJUSTAR,
    DESCARGA_BIS_ACTIVOS_XM,
    CONTRASTE_ESTAT,
    DESCARGA_BIS_ACTIVOS_JP,
    CONTRASTE_BIS_CAMBIO_XM,
    CONTRASTE_BIS_CAMBIO_JP,
    CONTRASTE_BIS_CAMBIO_CN,
)
# De qué descarga de fuente depende cada serie.
FUENTE_DE = {
    "m2_eeuu": DESCARGA_H6,
    "m2_eeuu_sin_ajustar": DESCARGA_H6,
    "m2_eurozona": DESCARGA_BCE_M2_AJUSTADA,
    "m2_eurozona_sin_ajustar": DESCARGA_BCE_M2_SIN_AJUSTAR,
    "m2_japon": DESCARGA_BOJ_M2,
    "dinero_amplio_china": DESCARGA_OCDE_CHINA,
    "balance_fed": DESCARGA_H41,
    "balance_eurosistema": DESCARGA_BCE_BALANCE,
    "balance_boj": DESCARGA_BOJ_BALANCE,
    "balance_pboc": DESCARGA_BIS_ACTIVOS_CN,
    "usd_por_eur": DESCARGA_H10,
    "jpy_por_usd": DESCARGA_H10,
    "cny_por_usd": DESCARGA_H10,
}


def _mes(valor) -> str:
    return pd.Timestamp(valor).strftime("%Y-%m")


def _a_mes(serie: pd.Series) -> pd.Series:
    """Reindexa una serie mensual al primer día de cada mes."""
    mensual = serie.copy()
    mensual.index = pd.DatetimeIndex(
        [pd.Timestamp(year=f.year, month=f.month, day=1) for f in mensual.index], name="mes"
    )
    return mensual[~mensual.index.duplicated(keep="last")].sort_index()


# --- Crudos -------------------------------------------------------------------


@dataclass
class Crudos:
    """Lo que entregaron las descargas, y lo que no se pudo tener."""

    registros: list[RegistroDescarga] = field(default_factory=list)
    rutas: dict[str, Path] = field(default_factory=dict)  # clave de la descarga -> crudo
    faltantes: dict[str, str] = field(default_factory=dict)  # clave -> motivo


def cargar_crudos(fecha_descarga: date, sesion=None) -> Crudos:
    """Baja o reutiliza cada crudo. Una fuente de contraste que falla no detiene nada.

    Una fuente de serie que falla por red o por formato detiene la corrida, como
    en la fase R. Las dos excepciones son el robots.txt que veda el pedido y la
    copia a mano que falta o no coincide: esas dejan la serie NO MEDIDO.
    """
    manifiesto = fuentes_precios.leer_manifiesto(ARCHIVO_D0_DESCARGAS)
    crudos = Crudos()
    for descarga in DESCARGAS_FUENTE + DESCARGAS_CONTRASTE:
        try:
            registro = fuentes_denominador.descargar(
                descarga, fecha_descarga, DIR_CRUDO, DIR_CRUDO_PRIVADO, manifiesto, sesion
            )
        except (AccesoVedado, CopiaFaltante) as error:
            crudos.faltantes[descarga.clave] = str(error)
            continue
        except ErrorDeFuente as error:
            if descarga in DESCARGAS_CONTRASTE or descarga.manual:
                crudos.faltantes[descarga.clave] = str(error)
                continue
            raise
        crudos.registros.append(registro)
        crudos.rutas[descarga.clave] = registro.ruta
    return crudos


# --- Series -------------------------------------------------------------------


@dataclass
class SerieConstruida:
    """Una serie ya en su convención mensual, con lo que hace falta para publicarla."""

    valores: pd.Series  # indexada por mes (primer día)
    fecha_origen: pd.Series | None = None  # A-D0-14: de qué semana sale cada mes
    rotulo: str | None = None  # el rótulo que la fuente le pone (China)
    semanal: pd.Series | None = None  # balances: los datos semanales
    fin_de_mes: pd.DataFrame | None = None  # tipos de cambio: último día del mes


def ultimo_del_mes(semanal: pd.Series, paso_dias: int = 7) -> tuple[pd.Series, pd.Series]:
    """El último dato semanal fechado dentro de cada mes, con su fecha (A-D0-14).

    El mes está completo cuando el dato que seguiría al último (siete días
    después) ya cae en otro mes. Así el mes en curso queda afuera hasta que
    llegue su última semana.
    """
    valores, origenes, meses = [], [], []
    for periodo, grupo in semanal.groupby(semanal.index.to_period("M")):
        ultima = grupo.index[-1]
        if (ultima + pd.Timedelta(days=paso_dias)).to_period("M") == periodo:
            continue
        meses.append(periodo.to_timestamp())
        valores.append(float(grupo.iloc[-1]))
        origenes.append(ultima)
    indice = pd.DatetimeIndex(meses, name="mes")
    return (
        pd.Series(valores, index=indice, dtype=float),
        pd.Series(origenes, index=indice, dtype="datetime64[ns]"),
    )


def fin_de_mes(diaria: pd.Series) -> pd.DataFrame:
    """El último dato diario de cada mes completo, con su fecha.

    Un mes está completo si la serie diaria ya tiene un dato de un mes
    posterior: el último dato de un mes en curso no es el de fin de mes.
    """
    ultimo_periodo = diaria.index[-1].to_period("M")
    filas = []
    for periodo, grupo in diaria.groupby(diaria.index.to_period("M")):
        if periodo == ultimo_periodo:
            continue
        filas.append((periodo.to_timestamp(), float(grupo.iloc[-1]), grupo.index[-1]))
    tabla = pd.DataFrame(filas, columns=["mes", "fin_de_mes", "fecha_fin_de_mes"]).set_index("mes")
    tabla.index.name = "mes"
    return tabla


def _desde(serie: SerieD0, valores: pd.Series) -> pd.Series:
    if serie.desde is None:
        return valores
    return valores[valores.index >= pd.Timestamp(serie.desde + "-01")]


def verificar_banda(serie: SerieD0, valores: pd.Series) -> None:
    """Control de orden de magnitud: atrapa una unidad equivocada sin metadatos."""
    if valores.empty:
        raise ErrorDeFuente(f"{serie.nombre}: la serie quedó vacía")
    minimo, maximo = serie.banda_plausible
    fuera = valores[(valores < minimo) | (valores > maximo)]
    if not fuera.empty:
        muestra = ", ".join(f"{_mes(m)}={formatear(v, 4)}" for m, v in fuera.head(3).items())
        raise ErrorDeFuente(
            f"{serie.nombre}: {len(fuera)} valores fuera de la banda plausible "
            f"[{minimo}, {maximo}] {serie.unidad} ({muestra})"
        )


def construir_series(crudos: Crudos) -> tuple[dict[str, SerieConstruida], dict[str, str]]:
    """Cada serie en su convención mensual. Devuelve también los motivos de las que faltan."""
    series: dict[str, SerieConstruida] = {}
    motivos: dict[str, str] = {}
    rutas = crudos.rutas

    # Junta: H.6, H.4.1 y H.10.
    if DESCARGA_H6.clave in rutas:
        xml = leer_xml_junta(rutas[DESCARGA_H6.clave], set(JUNTA_SERIES_H6.values()))
        for clave, nombre in JUNTA_SERIES_H6.items():
            exigir_multiplicador(xml[nombre], nombre, JUNTA_MULTIPLICADOR_H6)
            series[clave] = SerieConstruida(_a_mes(xml[nombre].valores))
    if DESCARGA_H41.clave in rutas:
        xml = leer_xml_junta(rutas[DESCARGA_H41.clave], {JUNTA_SERIE_BALANCE})
        exigir_multiplicador(xml[JUNTA_SERIE_BALANCE], JUNTA_SERIE_BALANCE, JUNTA_MULTIPLICADOR_H41)
        semanal = xml[JUNTA_SERIE_BALANCE].valores
        mensual, origen = ultimo_del_mes(semanal)
        series["balance_fed"] = SerieConstruida(mensual, fecha_origen=origen, semanal=semanal)
    if DESCARGA_H10.clave in rutas:
        nombres = {nombre for par in JUNTA_SERIES_H10.values() for nombre in par}
        xml = leer_xml_junta(rutas[DESCARGA_H10.clave], nombres)
        for clave, (mensual, diaria) in JUNTA_SERIES_H10.items():
            exigir_multiplicador(xml[mensual], mensual, JUNTA_MULTIPLICADOR_H10)
            exigir_multiplicador(xml[diaria], diaria, JUNTA_MULTIPLICADOR_H10)
            series[clave] = SerieConstruida(
                _a_mes(xml[mensual].valores), fin_de_mes=fin_de_mes(xml[diaria].valores)
            )

    # BCE: copias a mano.
    for clave, descarga in (
        ("m2_eurozona", DESCARGA_BCE_M2_AJUSTADA),
        ("m2_eurozona_sin_ajustar", DESCARGA_BCE_M2_SIN_AJUSTAR),
    ):
        if descarga.clave in rutas:
            valores = leer_csv_bce(rutas[descarga.clave], SERIES_POR_CLAVE[clave].identificador)
            series[clave] = SerieConstruida(_a_mes(valores))
    if DESCARGA_BCE_BALANCE.clave in rutas:
        semanal = leer_csv_bce(
            rutas[DESCARGA_BCE_BALANCE.clave], SERIES_POR_CLAVE["balance_eurosistema"].identificador
        )
        mensual, origen = ultimo_del_mes(semanal)
        series["balance_eurosistema"] = SerieConstruida(mensual, fecha_origen=origen, semanal=semanal)

    # Banco de Japón.
    if DESCARGA_BOJ_M2.clave in rutas:
        series["m2_japon"] = SerieConstruida(leer_csv_boj(rutas[DESCARGA_BOJ_M2.clave], BOJ_CODIGO_M2))
    if DESCARGA_BOJ_BALANCE.clave in rutas:
        series["balance_boj"] = SerieConstruida(
            leer_csv_boj(rutas[DESCARGA_BOJ_BALANCE.clave], BOJ_CODIGO_BALANCE)
        )

    # China: la OCDE para el dinero amplio, el BIS para el balance.
    if DESCARGA_OCDE_CHINA.clave in rutas:
        ocde = leer_csv_ocde(rutas[DESCARGA_OCDE_CHINA.clave], OCDE_AREA_CHINA, OCDE_MEDIDA_DINERO_AMPLIO)
        series["dinero_amplio_china"] = SerieConstruida(ocde.valores, rotulo=ocde.rotulo)
    if DESCARGA_BIS_ACTIVOS_CN.clave in rutas:
        series["balance_pboc"] = SerieConstruida(
            leer_csv_bis_activos(rutas[DESCARGA_BIS_ACTIVOS_CN.clave], "CN")
        )

    for serie in SERIES_D0:
        if serie.clave in series:
            construida = series[serie.clave]
            construida.valores = _desde(serie, construida.valores)
            if construida.fecha_origen is not None:
                construida.fecha_origen = construida.fecha_origen.reindex(construida.valores.index)
            verificar_banda(serie, construida.valores)
        else:
            motivos[serie.clave] = crudos.faltantes.get(
                FUENTE_DE[serie.clave].clave, f"{serie.nombre}: sin crudo"
            )
    return series, motivos


# --- Validación (A-D0-25) ------------------------------------------------------


@dataclass
class Validacion:
    """El resultado del gate de una serie: contra qué, cuántos meses y si cerró."""

    serie: str
    fuente: str
    tolerancia: str
    comparados: int
    fuera: list[str]  # meses fuera de tolerancia
    maxima: float | None  # diferencia máxima observada, en la unidad de la comparación
    en_disputa: list[str] = field(default_factory=list)  # control: marca, no decide
    nota: str = ""
    minimo: int = MINIMO_COMPARACIONES_GATE  # cuántas comparaciones hacen falta para decidir
    clase: str = "gate"  # "gate" decide la publicación; "control" marca meses en disputa
    meses: list[str] = field(default_factory=list)  # qué meses se compararon

    @property
    def ok(self) -> bool:
        return self.comparados >= self.minimo and not self.fuera

    def como_control(self) -> "Validacion":
        """Un control no decide: lo que quedó fuera de tolerancia pasa a disputa."""
        self.en_disputa = sorted(set(self.en_disputa) | set(self.fuera))
        self.fuera = []
        self.clase = "control"
        return self

    def resumen(self) -> str:
        if self.comparados == 0:
            detalle = f" ({self.nota})" if self.nota else ""
            return f"{self.serie}: sin comparar contra {self.fuente}{detalle}"
        estado = "cerró" if self.ok else "NO cerró"
        texto = (
            f"{self.serie}: {self.clase} contra {self.fuente} {estado}: {self.comparados} meses, "
            f"tolerancia {self.tolerancia}, diferencia máxima {formatear(self.maxima, 4)}"
        )
        if self.fuera:
            texto += f"; fuera de tolerancia: {', '.join(self.fuera[:6])}"
            if len(self.fuera) > 6:
                texto += f" y {len(self.fuera) - 6} más"
        if self.en_disputa:
            texto += f"; en disputa (control): {len(self.en_disputa)} meses"
        if self.nota:
            texto += f"; {self.nota}"
        return texto

    def validacion(self) -> str:
        """Lo que va en la ficha."""
        if self.comparados == 0:
            return f"sin validación externa: no se pudo comparar contra {self.fuente}"
        estado = "cerró" if self.ok else "no cerró"
        texto = (
            f"{self.clase} contra {self.fuente}, tolerancia {self.tolerancia}: {estado} en "
            f"{self.comparados} meses"
        )
        if self.fuera:
            texto += f", {len(self.fuera)} fuera"
        if self.en_disputa:
            texto += f"; {len(self.en_disputa)} meses en disputa"
        if self.nota:
            texto += f"; {self.nota}"
        return texto


def comparar(
    serie: str,
    valores: pd.Series,
    referencia: pd.Series,
    tolerancia: float,
    fuente: str,
    unidad: str,
    ultimos: int | None = None,
    relativa: bool = False,
) -> Validacion:
    """Compara mes a mes dos series y dice si el gate cierra.

    `relativa` compara en porcentaje. `ultimos` limita la comparación a los
    últimos N meses comunes.
    """
    comunes = valores.dropna().index.intersection(referencia.dropna().index)
    if ultimos is not None:
        comunes = comunes[-ultimos:]
    if len(comunes) == 0:
        return Validacion(serie, fuente, f"±{tolerancia:g} {unidad}", 0, [], None)
    propios, ajenos = valores.loc[comunes], referencia.loc[comunes]
    diferencia = (propios - ajenos).abs()
    if relativa:
        diferencia = diferencia / ajenos.abs() * 100.0
    excedidos = diferencia[diferencia > tolerancia].index
    return Validacion(
        serie,
        fuente,
        f"±{tolerancia:g} {unidad}",
        len(comunes),
        [_mes(m) for m in excedidos],
        float(diferencia.max()),
        meses=[_mes(m) for m in comunes],
    )


def comparar_anclas(serie: str, valores: pd.Series, anclas: tuple[AnclaMensual, ...]) -> Validacion:
    """Gate contra valores leídos a mano de una segunda fuente (como A-R0-16)."""
    propias = [ancla for ancla in anclas if ancla.serie == serie]
    if len(propias) < MINIMO_ANCLAS:
        return Validacion(
            serie,
            "lecturas a mano de una segunda fuente",
            "medio paso del redondeo de la fuente",
            0,
            [],
            None,
            nota=f"hay {len(propias)} anclas y hacen falta {MINIMO_ANCLAS}",
        )
    fuera, maxima, comparados = [], 0.0, 0
    for ancla in propias:
        mes = pd.Timestamp(ancla.mes + "-01")
        if mes not in valores.index or pd.isna(valores.loc[mes]):
            fuera.append(f"{ancla.mes} (sin dato en la serie)")
            continue
        comparados += 1
        diferencia = abs(float(valores.loc[mes]) - ancla.valor)
        maxima = max(maxima, diferencia)
        if diferencia > ancla.tolerancia:
            fuera.append(ancla.mes)
    fuente = f"{propias[0].fuente} (leída el {propias[0].fecha_lectura})"
    resultado = Validacion(
        serie, fuente, f"±{propias[0].tolerancia:g} por ancla", comparados, fuera, maxima,
        minimo=MINIMO_ANCLAS,
    )
    if comparados < MINIMO_ANCLAS:
        resultado.nota = f"solo {comparados} anclas con dato en la serie"
        resultado.comparados = 0
    return resultado


def _fin_de_semana_bis(mes: pd.Timestamp) -> pd.Timestamp:
    """El viernes de la semana que contiene el último día hábil del mes (regla del BIS)."""
    ultimo = mes + pd.offsets.MonthEnd(0)
    while ultimo.weekday() >= 5:
        ultimo -= pd.Timedelta(days=1)
    return ultimo + pd.Timedelta(days=4 - ultimo.weekday())


def _referencia(crudos: Crudos, descarga: Descarga, lector):
    """Lee una fuente de contraste. Si no se puede leer, el gate queda sin comparar."""
    ruta = crudos.rutas.get(descarga.clave)
    if ruta is None:
        return None
    try:
        return lector(ruta)
    except ErrorDeFuente as error:
        crudos.faltantes[descarga.clave] = f"no se pudo leer: {error}"
        return None


def _sin_fuente(crudos: Crudos, clave: str, descarga: Descarga, tolerancia: str) -> Validacion:
    motivo = crudos.faltantes.get(descarga.clave, "sin crudo")
    return Validacion(clave, descarga.descripcion, tolerancia, 0, [], None, nota=motivo[:120])


def validar(series: dict[str, SerieConstruida], crudos: Crudos) -> dict[str, Validacion]:
    """Un gate por serie. Las tolerancias están declaradas en configuracion.py."""
    resultados: dict[str, Validacion] = {}

    # M2 de EE.UU. contra la Tabla 1 en HTML.
    tabla = _referencia(
        crudos, CONTRASTE_H6_HTML, lambda ruta: interpretar_tabla_h6(ruta.read_text(encoding="utf-8"))
    )
    for clave, columna in (("m2_eeuu", "ajustada"), ("m2_eeuu_sin_ajustar", "sin_ajustar")):
        if clave not in series:
            continue
        if tabla is None:
            resultados[clave] = _sin_fuente(crudos, clave, CONTRASTE_H6_HTML, f"±{TOLERANCIA_H6_HTML:g}")
            continue
        resultados[clave] = comparar(
            clave,
            series[clave].valores,
            _a_mes(tabla[columna]),
            TOLERANCIA_H6_HTML,
            "la Tabla 1 del H.6 en HTML",
            "miles de millones de USD",
        )

    # Balance de la Fed: gate contra el BIS (último miércoles del mes) y control contra FRED.
    if "balance_fed" in series:
        bis = _referencia(crudos, DESCARGA_BIS_ACTIVOS_US, lambda ruta: leer_csv_bis_activos(ruta, "US"))
        if bis is None:
            resultados["balance_fed"] = _sin_fuente(
                crudos, "balance_fed", DESCARGA_BIS_ACTIVOS_US, f"±{TOLERANCIA_BIS_FED:g}"
            )
        else:
            resultados["balance_fed"] = comparar(
                "balance_fed",
                series["balance_fed"].valores,
                bis * 1000.0,
                TOLERANCIA_BIS_FED,
                "BIS WS_CBTA (EE.UU.)",
                "millones de USD",
            )
        fred = _referencia(
            crudos,
            CONTRASTE_FRED_WALCL,
            lambda ruta: fuentes_precios.interpretar_fred_diario(ruta.read_text(encoding="utf-8"), "WALCL"),
        )
        semanal = series["balance_fed"].semanal
        if fred is not None and semanal is not None:
            control = comparar(
                "balance_fed", semanal, fred, TOLERANCIA_FRED_WALCL, "FRED WALCL", "millones de USD"
            )
            # Las semanas distintas se traducen a los meses que salen de esas semanas.
            semanas_distintas = {
                f for f in semanal.index if _mes(f) in set(control.fuera)
            } if control.fuera else set()
            resultados["balance_fed"].en_disputa = [
                _mes(mes)
                for mes, origen in series["balance_fed"].fecha_origen.items()
                if pd.notna(origen) and pd.Timestamp(origen) in semanas_distintas
            ]
            resultados["balance_fed"].nota = (
                f"control contra FRED WALCL: {control.comparados} semanas, "
                + ("todas iguales" if not control.fuera else f"{len(control.fuera)} distintas")
            )

    # M2 de la Eurozona contra el Banco de España, últimos meses.
    for clave, descarga, codigo in (
        ("m2_eurozona", CONTRASTE_BDE_AJUSTADA, BDE_CODIGO_M2_AJUSTADA),
        ("m2_eurozona_sin_ajustar", CONTRASTE_BDE_SIN_AJUSTAR, BDE_CODIGO_M2_SIN_AJUSTAR),
    ):
        if clave not in series:
            continue
        bde = _referencia(
            crudos, descarga, lambda ruta, c=codigo: interpretar_bde(ruta.read_text(encoding="latin-1"), c)
        )
        if bde is None:
            resultados[clave] = _sin_fuente(crudos, clave, descarga, f"±{TOLERANCIA_BDE:g}")
            continue
        resultados[clave] = comparar(
            clave,
            series[clave].valores,
            bde,
            TOLERANCIA_BDE,
            "el Banco de España (cuadros 1.12 y 1.10)",
            "millones de EUR",
            ultimos=MESES_GATE_BDE,
        )

    # Balance del Eurosistema contra el BIS, con la regla de semana del BIS.
    if "balance_eurosistema" in series:
        bis = _referencia(crudos, DESCARGA_BIS_ACTIVOS_XM, lambda ruta: leer_csv_bis_activos(ruta, "XM"))
        semanal = series["balance_eurosistema"].semanal
        if bis is None or semanal is None:
            resultados["balance_eurosistema"] = _sin_fuente(
                crudos, "balance_eurosistema", DESCARGA_BIS_ACTIVOS_XM, f"±{TOLERANCIA_BIS_EUROSISTEMA:g}"
            )
        else:
            propios = pd.Series(
                {mes: semanal.get(_fin_de_semana_bis(mes), float("nan")) for mes in bis.index},
                dtype=float,
            )
            resultados["balance_eurosistema"] = comparar(
                "balance_eurosistema",
                propios,
                bis * 1000.0,
                TOLERANCIA_BIS_EUROSISTEMA,
                "BIS WS_CBTA (zona del euro), viernes de la última semana hábil",
                "millones de EUR",
            )

    # Japón: M2 contra e-Stat; balance contra el BIS.
    if "m2_japon" in series:
        estat = _referencia(
            crudos, CONTRASTE_ESTAT, lambda ruta: interpretar_estat(leer_json(ruta), ESTAT_INDICADOR_M2)
        )
        if estat is None:
            resultados["m2_japon"] = _sin_fuente(crudos, "m2_japon", CONTRASTE_ESTAT, f"±{TOLERANCIA_ESTAT:g}")
        else:
            resultados["m2_japon"] = comparar(
                "m2_japon",
                series["m2_japon"].valores,
                estat,
                TOLERANCIA_ESTAT,
                "e-Stat Statistics Dashboard",
                "100 millones de JPY",
            )
    if "balance_boj" in series:
        bis = _referencia(crudos, DESCARGA_BIS_ACTIVOS_JP, lambda ruta: leer_csv_bis_activos(ruta, "JP"))
        if bis is None:
            resultados["balance_boj"] = _sin_fuente(
                crudos, "balance_boj", DESCARGA_BIS_ACTIVOS_JP, f"±{TOLERANCIA_BIS_BOJ:g}"
            )
        else:
            resultados["balance_boj"] = comparar(
                "balance_boj",
                series["balance_boj"].valores,
                bis * 10.0,
                TOLERANCIA_BIS_BOJ,
                "BIS WS_CBTA (Japón)",
                "100 millones de JPY",
            )

    # China: anclas leídas a mano.
    if "dinero_amplio_china" in series:
        resultados["dinero_amplio_china"] = comparar_anclas(
            "dinero_amplio_china", series["dinero_amplio_china"].valores, ANCLAS_CHINA
        )
    if "balance_pboc" in series:
        resultados["balance_pboc"] = comparar_anclas(
            "balance_pboc", series["balance_pboc"].valores, ANCLAS_BALANCE_PBOC
        )

    # Tipos de cambio contra el BIS: promedio mensual, en porcentaje. Es un
    # control, como quedó en FUENTES.md D0.11: dos fijaciones a horas distintas
    # no son el mismo dato, y un mes fuera del umbral se publica marcado en
    # disputa (A-D0-25).
    for clave, descarga, moneda, invertir in (
        ("usd_por_eur", CONTRASTE_BIS_CAMBIO_XM, "EUR", True),
        ("jpy_por_usd", CONTRASTE_BIS_CAMBIO_JP, "JPY", False),
        ("cny_por_usd", CONTRASTE_BIS_CAMBIO_CN, "CNY", False),
    ):
        if clave not in series:
            continue
        bis = _referencia(crudos, descarga, lambda ruta, m=moneda: leer_csv_bis_cambio(ruta, m, "A"))
        if bis is None:
            resultados[clave] = _sin_fuente(crudos, clave, descarga, f"±{TOLERANCIA_CAMBIO_PCT:g} %")
            continue
        referencia = (1.0 / bis) if invertir else bis
        resultados[clave] = comparar(
            clave,
            series[clave].valores,
            referencia,
            TOLERANCIA_CAMBIO_PCT,
            "BIS WS_XRU, promedio mensual",
            "%",
            relativa=True,
        ).como_control()
    return resultados


# --- Publicación ----------------------------------------------------------------


def estado_de_serie(serie: SerieD0, motivos: dict[str, str], validaciones: dict[str, Validacion]) -> str:
    if serie.clave in motivos:
        motivo = motivos[serie.clave]
        if "robots.txt" in motivo:
            return NO_MEDIDO_ACCESO_VEDADO
        return "NO MEDIDO: " + motivo.split(":", 1)[-1].strip()[:160]
    validacion = validaciones.get(serie.clave)
    if validacion is None or not validacion.ok:
        return NO_MEDIDO_SIN_VALIDACION
    return serie.estado


def serie_publicada(serie: SerieD0, motivos: dict[str, str], validaciones: dict[str, Validacion]) -> bool:
    validacion = validaciones.get(serie.clave)
    return serie.publicable and serie.clave not in motivos and validacion is not None and validacion.ok


def _estado_fila(serie: SerieD0, mes: pd.Timestamp) -> str:
    if serie.estimacion_hasta is not None and mes <= pd.Timestamp(serie.estimacion_hasta + "-01"):
        return ESTADO_ESTIMACION
    return serie.estado


def _quiebre_fila(serie: SerieD0, mes: pd.Timestamp) -> str:
    return "; ".join(quiebre.texto for quiebre in serie.quiebres if quiebre.mes == _mes(mes))


def tabla_dinero(series: dict[str, SerieConstruida], publicadas: set[str]) -> pd.DataFrame:
    filas = []
    for serie in SERIES_D0:
        if serie.familia != FAMILIA_DINERO or serie.clave not in publicadas:
            continue
        for mes, valor in series[serie.clave].valores.dropna().items():
            filas.append(
                {
                    "mes": _mes(mes),
                    "serie": serie.clave,
                    "valor": valor,
                    "estado": _estado_fila(serie, mes),
                    "quiebre": _quiebre_fila(serie, mes),
                }
            )
    return pd.DataFrame(filas, columns=COLUMNAS_D0_DINERO)


def tabla_balances(series: dict[str, SerieConstruida], publicadas: set[str]) -> pd.DataFrame:
    filas = []
    for serie in SERIES_D0:
        if serie.familia != FAMILIA_BALANCE or serie.clave not in publicadas:
            continue
        construida = series[serie.clave]
        for mes, valor in construida.valores.dropna().items():
            origen = ""
            if construida.fecha_origen is not None and pd.notna(construida.fecha_origen.get(mes)):
                origen = pd.Timestamp(construida.fecha_origen[mes]).strftime("%Y-%m-%d")
            filas.append(
                {
                    "mes": _mes(mes),
                    "serie": serie.clave,
                    "valor": valor,
                    "fecha_origen": origen,
                    "estado": _estado_fila(serie, mes),
                    "quiebre": _quiebre_fila(serie, mes),
                }
            )
    return pd.DataFrame(filas, columns=COLUMNAS_D0_BALANCES)


def tabla_cambio(
    series: dict[str, SerieConstruida], publicadas: set[str], validaciones: dict[str, Validacion]
) -> pd.DataFrame:
    filas = []
    for serie in SERIES_D0:
        if serie.familia != FAMILIA_CAMBIO or serie.clave not in publicadas:
            continue
        construida = series[serie.clave]
        disputa = set(validaciones[serie.clave].en_disputa)
        comparados = set(validaciones[serie.clave].meses)
        fines = construida.fin_de_mes
        if fines is None:
            fines = pd.DataFrame(columns=["fin_de_mes", "fecha_fin_de_mes"])
        meses = construida.valores.dropna().index.union(fines.index)
        for mes in meses:
            promedio = construida.valores.get(mes, float("nan"))
            fin = fines["fin_de_mes"].get(mes, float("nan"))
            fecha = fines["fecha_fin_de_mes"].get(mes)
            if _mes(mes) in disputa:
                contraste = "valor en disputa"
            elif _mes(mes) in comparados:
                contraste = "dentro del umbral"
            else:
                contraste = "sin comparar"
            filas.append(
                {
                    "mes": _mes(mes),
                    "par": serie.clave,
                    "promedio_mensual": promedio,
                    "fin_de_mes": fin,
                    "fecha_fin_de_mes": ""
                    if fecha is None or pd.isna(fecha)
                    else pd.Timestamp(fecha).strftime("%Y-%m-%d"),
                    "contraste": contraste,
                }
            )
    return pd.DataFrame(filas, columns=COLUMNAS_D0_CAMBIO)


def _publicado(serie: pd.Series) -> pd.Series:
    """Los valores tal como quedan en el CSV (FORMATO_D0): una derivada sale de lo publicado."""
    patron = FORMATO_D0.replace("%", "")
    return serie.map(lambda valor: valor if pd.isna(valor) else float(format(valor, patron)))


def _en_usd(nombre: str, dinero: str, valores: pd.Series, tipo: SerieConstruida | None, tasa_fija=None):
    """Una serie de dinero en miles de millones de USD, con su convención de tipo de cambio."""
    if tipo is None:
        return valores  # ya está en miles de millones de USD, promedio mensual
    if dinero == "m2_eurozona_sin_ajustar":
        # Saldo de fin de mes en millones de EUR, por USD/EUR del último día del mes.
        tasa = _publicado(tipo.fin_de_mes["fin_de_mes"]) if tasa_fija is None else tasa_fija
        return valores * (tasa.reindex(valores.index) if tasa_fija is None else tasa) / 1000.0
    # Promedio de saldos en 100 millones de JPY, por el promedio mensual de JPY por USD.
    tasa = _publicado(tipo.valores) if tasa_fija is None else tasa_fija
    return valores / (tasa.reindex(valores.index) if tasa_fija is None else tasa) / 10.0


def agregado(series: dict[str, SerieConstruida], publicadas: set[str]) -> tuple[pd.DataFrame, list[str]]:
    """El agregado en USD (A-D0-10, A-D0-11): meses comunes a las tres economías.

    Cada serie entra con el tipo de cambio de su convención: promedio del mes
    para los promedios (EE.UU., Japón), último día del mes para los saldos de
    fin de mes (Eurozona). La columna a tipo de cambio constante usa el del
    primer mes común. Todo en miles de millones de USD.
    """
    notas: list[str] = []
    faltan = sorted(
        {dinero for _, dinero, _ in ECONOMIAS_AGREGADO if dinero not in publicadas}
        | {cambio for _, _, cambio in ECONOMIAS_AGREGADO if cambio is not None and cambio not in publicadas}
    )
    if faltan:
        notas.append(f"el agregado no se calcula: faltan {', '.join(faltan)}")
        return pd.DataFrame(columns=COLUMNAS_D0_AGREGADO), notas

    en_usd = {
        nombre: _en_usd(
            nombre, dinero, _publicado(series[dinero].valores.dropna()), None if cambio is None else series[cambio]
        )
        for nombre, dinero, cambio in ECONOMIAS_AGREGADO
    }
    tabla = pd.DataFrame(en_usd).dropna()
    if tabla.empty:
        notas.append("el agregado no se calcula: no hay meses comunes")
        return pd.DataFrame(columns=COLUMNAS_D0_AGREGADO), notas
    primero = tabla.index[0]
    constante = {}
    for nombre, dinero, cambio in ECONOMIAS_AGREGADO:
        valores = _publicado(series[dinero].valores.reindex(tabla.index))
        if cambio is None:
            constante[nombre] = valores
            continue
        tipo = series[cambio]
        fija = float(
            _publicado(tipo.fin_de_mes["fin_de_mes"]).loc[primero]
            if dinero == "m2_eurozona_sin_ajustar"
            else _publicado(tipo.valores).loc[primero]
        )
        constante[nombre] = _en_usd(nombre, dinero, valores, tipo, tasa_fija=fija)
    constante = pd.DataFrame(constante)
    salida = pd.DataFrame(
        {
            "mes": [_mes(mes) for mes in tabla.index],
            "m2_eeuu_usd": tabla["eeuu"].to_numpy(),
            "m2_eurozona_usd": tabla["eurozona"].to_numpy(),
            "m2_japon_usd": tabla["japon"].to_numpy(),
            "agregado_usd": tabla.sum(axis=1).to_numpy(),
            "agregado_usd_tc_constante": constante.sum(axis=1).to_numpy(),
            "estado": ESTADO_DATO,
        }
    )
    notas.append(
        f"{NOMBRE_AGREGADO}: {salida['mes'].iloc[0]} a {salida['mes'].iloc[-1]}, {len(salida)} meses; "
        f"tipo de cambio constante del {_mes(primero)} (A-D0-11)"
    )
    return salida, notas


def series_desde_publicadas(dinero: pd.DataFrame, cambio: pd.DataFrame) -> dict[str, SerieConstruida]:
    """Reconstruye las series que usa el agregado a partir de los CSV publicados.

    Es lo que permite comprobar, sin red y sin crudos, que denominador_agregado.csv
    sale de denominador_dinero.csv y denominador_tipos_de_cambio.csv.
    """
    series: dict[str, SerieConstruida] = {}
    for clave, grupo in dinero.groupby("serie"):
        indice = pd.DatetimeIndex(pd.to_datetime(grupo["mes"] + "-01"), name="mes")
        series[clave] = SerieConstruida(pd.Series(grupo["valor"].to_numpy(dtype=float), index=indice))
    for clave, grupo in cambio.groupby("par"):
        indice = pd.DatetimeIndex(pd.to_datetime(grupo["mes"] + "-01"), name="mes")
        promedio = pd.Series(grupo["promedio_mensual"].to_numpy(dtype=float), index=indice).dropna()
        fines = pd.DataFrame(
            {
                "fin_de_mes": grupo["fin_de_mes"].to_numpy(dtype=float),
                "fecha_fin_de_mes": pd.to_datetime(grupo["fecha_fin_de_mes"], errors="coerce").to_numpy(),
            },
            index=indice,
        ).dropna(subset=["fin_de_mes"])
        fines.index.name = "mes"
        series[clave] = SerieConstruida(promedio, fin_de_mes=fines)
    return series


def tabla_fichas(
    series: dict[str, SerieConstruida],
    motivos: dict[str, str],
    validaciones: dict[str, Validacion],
    fichas_previas: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Una fila por serie. Las del tramo histórico las escribe dinero_historico.py y aquí se conservan."""
    previas = {}
    if fichas_previas is not None and not fichas_previas.empty:
        previas = {
            fila["serie"]: fila
            for fila in fichas_previas.fillna("").astype(str).to_dict("records")
            if fila["serie"] in CLAVES_DINERO_HISTORICO
        }
    filas = []
    for serie in SERIES_D0:
        construida = series.get(serie.clave)
        valores = construida.valores.dropna() if construida is not None else pd.Series(dtype=float)
        validacion = validaciones.get(serie.clave)
        nombre = serie.nombre
        if construida is not None and construida.rotulo:
            nombre = nombre.format(rotulo=construida.rotulo)
        filas.append(
            {
                "serie": serie.clave,
                "nombre": nombre,
                "familia": serie.familia,
                "publicada": "sí" if serie_publicada(serie, motivos, validaciones) else "no",
                "estado": estado_de_serie(serie, motivos, validaciones),
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
                "validacion": validacion.validacion() if validacion is not None else "sin validación externa",
                "supuestos": " ".join(serie.supuestos),
                "quiebres": "; ".join(f"{q.mes}: {q.texto}" for q in serie.quiebres),
                "primer_mes": "" if valores.empty else _mes(valores.index[0]),
                "ultimo_mes": "" if valores.empty else _mes(valores.index[-1]),
                "meses": len(valores),
            }
        )
    for pendiente in SERIES_PENDIENTES:
        if pendiente.clave in previas:
            # dinero_historico.py ya publicó (o dejó NO MEDIDO con su motivo) esta serie.
            filas.append(previas.pop(pendiente.clave))
            if pendiente.clave == CLAVE_DINERO_1947_1958 and CLAVE_DINERO_1947_1958_SIN_AJUSTAR in previas:
                filas.append(previas.pop(CLAVE_DINERO_1947_1958_SIN_AJUSTAR))
            continue
        filas.append(
            {columna: "" for columna in COLUMNAS_D0_FICHAS}
            | {
                "serie": pendiente.clave,
                "nombre": pendiente.nombre,
                "familia": pendiente.familia,
                "publicada": "no",
                "estado": pendiente.estado,
                "fuente": pendiente.fuente,
                "supuestos": " ".join(pendiente.supuestos),
                "meses": 0,
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_D0_FICHAS)


# --- Revisiones -----------------------------------------------------------------


def _ancha(tabla: pd.DataFrame | None, clave: str, valor: str) -> pd.DataFrame | None:
    """Una tabla larga (mes, serie, valor) a ancha, con la columna fecha que pide la bitácora."""
    if tabla is None or tabla.empty:
        return None
    ancha = tabla.pivot(index="mes", columns=clave, values=valor)
    ancha.columns = [str(columna) for columna in ancha.columns]
    ancha.insert(0, "fecha", pd.to_datetime(ancha.index + "-01"))
    return ancha.reset_index(drop=True)


def _leer_fichas(ruta: Path) -> pd.DataFrame | None:
    """La ficha anterior, con todo como texto: un vacío es un vacío y 144 meses no son 144.0."""
    if not ruta.exists():
        return None
    return pd.read_csv(ruta, dtype=str, keep_default_na=False)


def _leer(ruta: Path) -> pd.DataFrame | None:
    return pd.read_csv(ruta, dtype={"mes": str}) if ruta.exists() else None


def revisiones_de(
    previa: pd.DataFrame | None, nueva: pd.DataFrame, clave: str, valor: str
) -> list[bitacora.Revision]:
    ancha_previa, ancha_nueva = _ancha(previa, clave, valor), _ancha(nueva, clave, valor)
    if ancha_previa is None or ancha_nueva is None:
        return []
    columnas = [c for c in ancha_nueva.columns if c != "fecha" and c in ancha_previa.columns]
    return bitacora.detectar_revisiones(ancha_previa, ancha_nueva, columnas, EPSILON_REVISION_D0)


# --- Changelog ------------------------------------------------------------------


@dataclass
class EntradaDenominador:
    fecha_corrida: date
    descargas: list[str]
    series: list[str]
    validaciones: list[str]
    agregado: list[str]
    revisiones: list[str]
    notas: list[str] = field(default_factory=list)

    @property
    def titulo(self) -> str:
        return f"{self.fecha_corrida.isoformat()} · denominador"

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
        bloque("Agregado", self.agregado, "sin agregado")
        bloque("Revisiones de datos históricos", self.revisiones, "ninguna")
        for nota in self.notas:
            lineas.append(f"- Nota: {nota}")
        lineas.append("")
        return "\n".join(lineas)


LIMITE_REVISIONES_LISTADAS = 40


def resumir_revisiones(revisiones: list[bitacora.Revision]) -> list[str]:
    if len(revisiones) <= LIMITE_REVISIONES_LISTADAS:
        return [str(revision) for revision in revisiones]
    por_columna: dict[str, list[bitacora.Revision]] = {}
    for revision in revisiones:
        por_columna.setdefault(revision.columna, []).append(revision)
    lineas = [f"{len(revisiones)} revisiones: la fuente reescribió la historia; se resumen por serie"]
    for columna, propias in sorted(por_columna.items()):
        lineas.append(
            f"{columna}: {len(propias)} meses, de {propias[0].fecha.date()} a {propias[-1].fecha.date()}"
        )
    return lineas


# --- main -----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.denominador",
        description="Construye y actualiza las series de la fase D0 (El Denominador).",
    )
    analizador.add_argument(
        "--fecha-descarga",
        type=date.fromisoformat,
        default=date.today(),
        help="Fecha de la descarga a usar (AAAA-MM-DD). Permite rehacer una corrida "
        "anterior a partir de los crudos ya guardados.",
    )
    fecha_descarga = analizador.parse_args(argv).fecha_descarga
    asegurar_directorios(DIR_CRUDO, DIR_CRUDO_PRIVADO, DIR_SERIES)
    # La consola de Windows no siempre puede con los nombres de las fuentes en
    # otros alfabetos. Los archivos se escriben en UTF-8; la consola, como pueda.
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")

    try:
        crudos = cargar_crudos(fecha_descarga)
        series, motivos = construir_series(crudos)
    except ErrorDeFuente as error:
        print(f"ERROR DE FUENTE: {error}", file=sys.stderr)
        return CODIGO_ERROR_FUENTE
    fuentes_precios.actualizar_manifiesto(ARCHIVO_D0_DESCARGAS, crudos.registros)

    validaciones = validar(series, crudos)
    publicadas = {s.clave for s in SERIES_D0 if serie_publicada(s, motivos, validaciones)}

    dinero = tabla_dinero(series, publicadas)
    balances = tabla_balances(series, publicadas)
    cambio = tabla_cambio(series, publicadas, validaciones)
    agregada, notas_agregado = agregado(series, publicadas)
    fichas = tabla_fichas(series, motivos, validaciones, _leer_fichas(ARCHIVO_D0_FICHAS))

    previa_dinero = _leer(ARCHIVO_D0_DINERO)
    revisiones = revisiones_de(previa_dinero, dinero, "serie", "valor")
    revisiones += revisiones_de(_leer(ARCHIVO_D0_BALANCES), balances, "serie", "valor")
    revisiones += revisiones_de(_leer(ARCHIVO_D0_CAMBIO), cambio, "par", "promedio_mensual")
    previa_agregado = _leer(ARCHIVO_D0_AGREGADO)
    if previa_agregado is not None and not previa_agregado.empty and not agregada.empty:
        revisiones += bitacora.detectar_revisiones(
            previa_agregado.assign(fecha=pd.to_datetime(previa_agregado["mes"] + "-01")),
            agregada.assign(fecha=pd.to_datetime(agregada["mes"] + "-01")),
            ["agregado_usd", "agregado_usd_tc_constante"],
            EPSILON_REVISION_D0,
        )

    escribir_csv_determinista(dinero, ARCHIVO_D0_DINERO, COLUMNAS_D0_DINERO, FORMATO_D0)
    escribir_csv_determinista(balances, ARCHIVO_D0_BALANCES, COLUMNAS_D0_BALANCES, FORMATO_D0)
    escribir_csv_determinista(cambio, ARCHIVO_D0_CAMBIO, COLUMNAS_D0_CAMBIO, FORMATO_D0)
    escribir_csv_determinista(agregada, ARCHIVO_D0_AGREGADO, COLUMNAS_D0_AGREGADO, FORMATO_D0)
    escribir_csv_determinista(fichas, ARCHIVO_D0_FICHAS, COLUMNAS_D0_FICHAS, FORMATO_D0)

    lineas_series = []
    for fila in fichas.itertuples():
        if fila.publicada == "sí":
            lineas_series.append(
                f"{fila.nombre}: se publica, {fila.primer_mes} a {fila.ultimo_mes}, {fila.meses} meses "
                f"({fila.unidad}; {fila.convencion}; {fila.supuestos})"
            )
        else:
            lineas_series.append(f"{fila.nombre}: no se publica: {fila.estado}")
    lineas_validacion = [validacion.resumen() for validacion in validaciones.values()]
    notas = [
        "las series del BCE entran por copia bajada a mano (A-D0-29); los ZIP de la Junta y "
        "las fuentes de contraste quedan fuera del repositorio, con su hash en el manifiesto (A-D0-27)",
    ]
    if previa_dinero is None:
        notas.insert(0, "primera publicación de las series: no hay corrida anterior con que comparar")
    for clave, motivo in crudos.faltantes.items():
        notas.append(f"sin crudo de {clave}: {motivo[:200]}")

    entrada = EntradaDenominador(
        fecha_corrida=fecha_descarga,
        descargas=[
            f"{r.descarga.clave}: {r.url}, sha256 {r.sha256}"
            + (f", actualizada el {r.actualizada}" if r.actualizada else "")
            + ("" if r.fecha_descarga == fecha_descarga else f", copia del {r.fecha_descarga}")
            for r in crudos.registros
        ],
        series=lineas_series,
        validaciones=lineas_validacion,
        agregado=notas_agregado,
        revisiones=resumir_revisiones(revisiones),
        notas=notas,
    )
    cambio_changelog = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

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
    print("Agregado")
    for linea in notas_agregado:
        print(f"  {linea}")
    print("Salidas")
    for ruta, tabla in (
        (ARCHIVO_D0_DINERO, dinero),
        (ARCHIVO_D0_BALANCES, balances),
        (ARCHIVO_D0_CAMBIO, cambio),
        (ARCHIVO_D0_AGREGADO, agregada),
        (ARCHIVO_D0_FICHAS, fichas),
    ):
        print(f"  {ruta} ({len(tabla)} filas)")
    print(f"  {ARCHIVO_D0_DESCARGAS}")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio_changelog else 'sin cambios'})")
    print("Resumen")
    print(f"  Series publicadas: {len(publicadas)} de {len(SERIES_D0)}")
    print(f"  Revisiones históricas: {len(revisiones)}")
    for revision in revisiones[:10]:
        print(f"    {revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
