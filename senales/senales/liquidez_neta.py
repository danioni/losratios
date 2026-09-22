"""S2.x - Liquidez neta de la Fed.

S2.1  Liquidez neta = WALCL - WTREGEN - RRPONTSYD, en miles de millones de USD,
      una observación por miércoles.
S2.2  Variación de S2.1 a 13 semanas, en porcentaje.

Un comando hace todo:

    python -m senales.liquidez_neta

descarga, verifica unidades, alinea al miércoles, calcula, valida contra el
H.4.1, escribe las salidas y actualiza el changelog. Si la validación falla, se
detiene y reporta la diferencia sin escribir ninguna serie: publicar un número
que no reproduce su propia ancla sería peor que no publicar nada.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from senales import bitacora, fuentes_fred, grafico
from senales.configuracion import (
    ARCHIVO_CHANGELOG,
    ARCHIVO_GRAFICO,
    ARCHIVO_SERIE,
    COLUMNAS_REVISABLES,
    COLUMNAS_SERIE,
    DIR_CRUDO,
    DIR_REPORTES,
    DIR_SERIES,
    EPSILON_REVISION,
    FECHA_INICIO,
    MAX_DIAS_ARRASTRE_RRP,
    SERIE_RRP,
    SERIE_TGA,
    SERIE_WALCL,
    UMBRAL_EXPANSION_CONTRACCION,
    VENTANA_VARIACION_SEMANAS,
    CasoValidacion,
    SerieFRED,
    VALIDACION_H41,
)
from senales.fuentes_fred import ErrorDeFuente
from senales.nucleo import asegurar_directorios, escribir_csv_determinista, formatear, leer_csv_serie

CODIGO_ERROR_FUENTE = 1
CODIGO_VALIDACION_FALLIDA = 2


@dataclass(frozen=True)
class ResultadoValidacion:
    """Contraste del cálculo contra el ancla externa del H.4.1."""

    caso: CasoValidacion
    calculado: float | None
    componentes: dict[str, tuple[float | None, float]]

    @property
    def diferencia(self) -> float | None:
        if self.calculado is None:
            return None
        return self.calculado - self.caso.s2_1_esperado

    @property
    def ok(self) -> bool:
        return self.diferencia is not None and abs(self.diferencia) <= self.caso.tolerancia

    def resumen(self) -> str:
        if self.calculado is None:
            return (
                f"FALLA - la fecha ancla {self.caso.fecha} no está en la serie calculada"
            )
        estado = "OK" if self.ok else "FALLA"
        return (
            f"{estado} - {self.caso.fecha}: calculado {formatear(self.calculado, 3)} vs "
            f"esperado {formatear(self.caso.s2_1_esperado, 3)}, "
            f"diferencia {formatear(self.diferencia, 3)}, "
            f"tolerancia +/-{formatear(self.caso.tolerancia, 3)}"
        )

    def detalle_componentes(self) -> list[str]:
        lineas = []
        for nombre, (calculado, esperado) in self.componentes.items():
            delta = None if calculado is None else calculado - esperado
            lineas.append(
                f"  {nombre:<6} calculado {formatear(calculado, 3):>12}  "
                f"H.4.1 {formatear(esperado, 3):>12}  diferencia {formatear(delta, 3):>12}"
            )
        return lineas


def alinear_a_miercoles(
    walcl: pd.Series,
    tga: pd.Series,
    rrp: pd.Series,
    fecha_inicio: date,
    max_dias_arrastre: int = MAX_DIAS_ARRASTRE_RRP,
) -> pd.DataFrame:
    """Arma la grilla semanal de miércoles y engancha las tres series.

    WALCL define la grilla porque es la fecha de balance del H.4.1. TGA se
    empareja por fecha exacta. ON RRP es diario: se toma el valor del miércoles
    y, si ese día no tiene dato, el último disponible anterior dentro de
    max_dias_arrastre, dejando constancia en rrp_fecha_origen.
    """
    inicio = pd.Timestamp(fecha_inicio)
    grilla = pd.DatetimeIndex(walcl.index[walcl.index >= inicio]).sort_values()

    no_miercoles = [f.date() for f in grilla if f.weekday() != 2]
    if no_miercoles:
        raise ErrorDeFuente(
            f"{SERIE_WALCL.id}: {len(no_miercoles)} observaciones no caen en miércoles "
            f"(primeras: {no_miercoles[:3]}). La grilla semanal de la señal asume el "
            "nivel de miércoles del H.4.1; revisar la fuente antes de seguir."
        )

    tolerancia = pd.Timedelta(days=max_dias_arrastre)
    rrp_valor = rrp.reindex(grilla, method="ffill", tolerance=tolerancia)
    origen = pd.Series(rrp.index, index=rrp.index)
    rrp_origen = origen.reindex(grilla, method="ffill", tolerance=tolerancia)

    return pd.DataFrame(
        {
            "fecha": grilla,
            "walcl": walcl.reindex(grilla).to_numpy(),
            "tga": tga.reindex(grilla).to_numpy(),
            "rrp": rrp_valor.to_numpy(),
            "rrp_fecha_origen": pd.DatetimeIndex(rrp_origen.to_numpy()),
        }
    ).reset_index(drop=True)


def calcular_variacion(s2_1: pd.Series, ventana_semanas: int) -> pd.Series:
    """Variación porcentual contra el miércoles de hace ventana_semanas.

    El desplazamiento es por fecha, no por posición: si falta una semana, la
    comparación devuelve vacío en vez de saltar silenciosamente a otra semana.
    """
    if not isinstance(s2_1.index, pd.DatetimeIndex):
        raise TypeError("s2_1 tiene que estar indexada por fecha")
    referencia = s2_1.reindex(s2_1.index - pd.Timedelta(weeks=ventana_semanas))
    referencia.index = s2_1.index
    referencia = referencia.where(referencia != 0.0)
    return (s2_1 / referencia - 1.0) * 100.0


def construir_serie(
    walcl: pd.Series,
    tga: pd.Series,
    rrp: pd.Series,
    fecha_inicio: date = FECHA_INICIO,
    ventana_semanas: int = VENTANA_VARIACION_SEMANAS,
    max_dias_arrastre: int = MAX_DIAS_ARRASTRE_RRP,
) -> pd.DataFrame:
    """Tabla completa de S2.1 y S2.2 a partir de las tres series normalizadas."""
    tabla = alinear_a_miercoles(walcl, tga, rrp, fecha_inicio, max_dias_arrastre)
    tabla["s2_1_liquidez_neta"] = tabla["walcl"] - tabla["tga"] - tabla["rrp"]

    indexada = tabla.set_index("fecha")["s2_1_liquidez_neta"]
    tabla["s2_2_var_13s_pct"] = calcular_variacion(indexada, ventana_semanas).to_numpy()
    return tabla


def detectar_huecos(tabla: pd.DataFrame, max_dias_arrastre: int = MAX_DIAS_ARRASTRE_RRP) -> list[str]:
    """Enumera lo que falta. Un hueco se reporta, no se rellena."""
    huecos: list[str] = []
    if tabla.empty:
        return ["la serie quedó vacía"]

    esperados = pd.date_range(tabla["fecha"].iloc[0], tabla["fecha"].iloc[-1], freq="W-WED")
    ausentes = esperados.difference(pd.DatetimeIndex(tabla["fecha"]))
    for fecha in ausentes:
        huecos.append(f"{fecha.date()} | miércoles sin observación de {SERIE_WALCL.id}")

    for _, fila in tabla.iterrows():
        marca = fila["fecha"].date()
        if pd.isna(fila["tga"]):
            huecos.append(f"{marca} | {SERIE_TGA.id} sin dato para ese miércoles")
        if pd.isna(fila["rrp"]):
            huecos.append(
                f"{marca} | {SERIE_RRP.id} sin dato en los {max_dias_arrastre} días previos"
            )
        elif pd.notna(fila["rrp_fecha_origen"]) and fila["rrp_fecha_origen"] != fila["fecha"]:
            huecos.append(
                f"{marca} | {SERIE_RRP.id} tomado de {fila['rrp_fecha_origen'].date()} "
                "(el miércoles no tenía dato)"
            )
    return huecos


def validar_caso_ancla(tabla: pd.DataFrame, caso: CasoValidacion) -> ResultadoValidacion:
    """Contrasta la fila del ancla contra los números publicados por el H.4.1."""
    objetivo = pd.Timestamp(caso.fecha)
    fila = tabla.loc[tabla["fecha"] == objetivo]

    def valor(columna: str) -> float | None:
        if fila.empty:
            return None
        crudo = fila.iloc[0][columna]
        return None if pd.isna(crudo) else float(crudo)

    return ResultadoValidacion(
        caso=caso,
        calculado=valor("s2_1_liquidez_neta"),
        componentes={
            "WALCL": (valor("walcl"), caso.walcl),
            "TGA": (valor("tga"), caso.tga),
            "ON RRP": (valor("rrp"), caso.rrp),
        },
    )


def _preparar_para_csv(tabla: pd.DataFrame) -> pd.DataFrame:
    salida = tabla.copy()
    salida["fecha"] = pd.to_datetime(salida["fecha"]).dt.strftime("%Y-%m-%d")
    salida["rrp_fecha_origen"] = pd.to_datetime(salida["rrp_fecha_origen"]).dt.strftime("%Y-%m-%d")
    return salida


def _cargar_serie_normalizada(
    serie: SerieFRED,
    fecha_descarga: date,
    dir_crudo: Path,
    reporte: list[str],
) -> tuple[pd.Series, fuentes_fred.VerificacionUnidad]:
    ruta, descargada = fuentes_fred.descargar_csv(serie, dir_crudo, fecha_descarga)
    reporte.append(
        f"{serie.id}: {'descargada' if descargada else 'reutilizada'} {ruta.name}"
    )

    verificacion = fuentes_fred.verificar_unidades(serie, fuentes_fred.unidad_declarada(serie))
    valores = fuentes_fred.leer_csv_crudo(ruta, serie)
    fuentes_fred.verificar_orden_de_magnitud(valores, serie)
    return valores, verificacion


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m senales.liquidez_neta",
        description="Construye y actualiza S2.1 (liquidez neta de la Fed) y S2.2 (su variación a 13 semanas).",
    )
    analizador.add_argument(
        "--fecha-descarga",
        type=date.fromisoformat,
        default=date.today(),
        help="Fecha de la descarga a usar (AAAA-MM-DD). Permite rehacer una corrida "
        "anterior a partir de los archivos ya guardados en data/raw.",
    )
    argumentos = analizador.parse_args(argv)
    fecha_descarga = argumentos.fecha_descarga

    asegurar_directorios(DIR_CRUDO, DIR_SERIES, DIR_REPORTES)
    reporte_descargas: list[str] = []

    try:
        walcl, ver_walcl = _cargar_serie_normalizada(
            SERIE_WALCL, fecha_descarga, DIR_CRUDO, reporte_descargas
        )
        tga, ver_tga = _cargar_serie_normalizada(
            SERIE_TGA, fecha_descarga, DIR_CRUDO, reporte_descargas
        )
        rrp, ver_rrp = _cargar_serie_normalizada(
            SERIE_RRP, fecha_descarga, DIR_CRUDO, reporte_descargas
        )
        tabla = construir_serie(walcl, tga, rrp)
    except ErrorDeFuente as error:
        print(f"ERROR DE FUENTE: {error}", file=sys.stderr)
        return CODIGO_ERROR_FUENTE

    verificaciones = [ver_walcl, ver_tga, ver_rrp]
    lineas_unidad = [
        f"{v.serie_id}: {v.etiqueta} ({v.detalle})" for v in verificaciones
    ]

    print("Descargas")
    for linea in reporte_descargas:
        print(f"  {linea}")
    print("Unidades")
    for linea in lineas_unidad:
        print(f"  {linea}")

    validacion = validar_caso_ancla(tabla, VALIDACION_H41)
    print("Validación")
    print(f"  {validacion.resumen()}")
    for linea in validacion.detalle_componentes():
        print(linea)

    if not validacion.ok:
        print("", file=sys.stderr)
        print(
            "La corrida se detiene: el cálculo no reproduce el ancla del H.4.1 dentro de la "
            "tolerancia. No se escribió ninguna serie, ningún gráfico ni el changelog.",
            file=sys.stderr,
        )
        print(
            "No ajustar la fórmula para que cuadre. Revisar, en este orden: unidades "
            "declaradas por FRED, la convención de la serie de TGA (A-S2-4: WTREGEN es "
            "promedio semanal, WDTGAL es nivel de miércoles) y el perímetro del ON RRP "
            "(A-S2-1).",
            file=sys.stderr,
        )
        contexto = tabla.loc[
            (tabla["fecha"] >= pd.Timestamp(VALIDACION_H41.fecha) - pd.Timedelta(weeks=3))
            & (tabla["fecha"] <= pd.Timestamp(VALIDACION_H41.fecha) + pd.Timedelta(weeks=3))
        ]
        if not contexto.empty:
            print("", file=sys.stderr)
            print("Semanas alrededor del ancla:", file=sys.stderr)
            print(_preparar_para_csv(contexto).to_string(index=False), file=sys.stderr)
        return CODIGO_VALIDACION_FALLIDA

    salida = _preparar_para_csv(tabla)
    previa = leer_csv_serie(ARCHIVO_SERIE)
    revisiones = bitacora.detectar_revisiones(previa, tabla, COLUMNAS_REVISABLES, EPSILON_REVISION)
    agregadas = bitacora.filas_agregadas(previa, tabla)
    huecos = detectar_huecos(tabla)

    escribir_csv_determinista(salida, ARCHIVO_SERIE, COLUMNAS_SERIE)
    grafico.dibujar(
        tabla,
        ARCHIVO_GRAFICO,
        VENTANA_VARIACION_SEMANAS,
        UMBRAL_EXPANSION_CONTRACCION,
        fuente="FRED (WALCL, WTREGEN, RRPONTSYD), release H.4.1 de la Reserva Federal",
    )

    umbral = (
        "NO MEDIDO (A-S2-3)"
        if UMBRAL_EXPANSION_CONTRACCION is None
        else formatear(UMBRAL_EXPANSION_CONTRACCION)
    )
    notas = [f"Serie de TGA en uso: {SERIE_TGA.id} ({SERIE_TGA.descripcion})"]
    if previa is None:
        notas.insert(0, "primera publicación de la serie: no hay corrida anterior con que comparar")

    entrada = bitacora.EntradaChangelog(
        fecha_corrida=fecha_descarga,
        rango_datos=(tabla["fecha"].iloc[0], tabla["fecha"].iloc[-1]),
        observaciones=len(tabla),
        agregadas=agregadas,
        revisiones=revisiones,
        huecos=huecos,
        verificaciones_unidad=lineas_unidad,
        resultado_validacion=validacion.resumen(),
        umbral=umbral,
        notas=notas,
    )
    cambio = bitacora.actualizar_changelog(ARCHIVO_CHANGELOG, entrada)

    print("Salidas")
    print(f"  {ARCHIVO_SERIE} ({len(tabla)} filas)")
    print(f"  {ARCHIVO_GRAFICO}")
    print(f"  {ARCHIVO_CHANGELOG} ({'actualizado' if cambio else 'sin cambios'})")
    print("Resumen")
    print(f"  Rango: {tabla['fecha'].iloc[0].date()} a {tabla['fecha'].iloc[-1].date()}")
    print(f"  Filas agregadas: {len(agregadas)}")
    print(f"  Revisiones históricas: {len(revisiones)}")
    for revision in revisiones[:10]:
        print(f"    {revision}")
    if len(revisiones) > 10:
        print(f"    ... y {len(revisiones) - 10} más (ver el changelog)")
    print(f"  Huecos: {len(huecos)}")
    for hueco in huecos[:10]:
        print(f"    {hueco}")
    if len(huecos) > 10:
        print(f"    ... y {len(huecos) - 10} más (ver el changelog)")
    print(f"  Última S2.1: {formatear(tabla['s2_1_liquidez_neta'].iloc[-1], 3)} miles de millones")
    print(f"  Última S2.2: {formatear(tabla['s2_2_var_13s_pct'].iloc[-1], 3)} %")
    print(f"  Umbral de expansión/contracción: {umbral}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
