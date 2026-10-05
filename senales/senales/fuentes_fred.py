"""Descarga y normalización de series de FRED.

Dos reglas que este módulo no negocia:

1. Las descargas crudas se guardan con la fecha de descarga en el nombre y
   nunca se sobrescriben. Correr dos veces el mismo día reutiliza el archivo.
2. La unidad de una serie no se asume. Se declara en configuracion.py y se
   contrasta contra los metadatos publicados por FRED. Si no se puede alcanzar
   los metadatos, la corrida sigue pero lo reporta como NO VERIFICADO, y el
   control de orden de magnitud y el caso de validación quedan como red.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from senales.configuracion import URL_CSV, URL_METADATOS, SerieFRED
from senales.nucleo import normalizar_texto

TIEMPO_LIMITE = 60

# Cuántas líneas del .txt de FRED se miran buscando la declaración de unidad.
# El encabezado real ronda las diez líneas; el margen es para que un campo nuevo
# no rompa la lectura.
LINEAS_ENCABEZADO_METADATOS = 40

# Texto de FRED -> clave de unidad interna.
EQUIVALENCIAS_UNIDAD = {
    "millions of u.s. dollars": "millones",
    "millions of us dollars": "millones",
    "millions of dollars": "millones",
    "billions of u.s. dollars": "miles_de_millones",
    "billions of us dollars": "miles_de_millones",
    "billions of dollars": "miles_de_millones",
}


class ErrorDeFuente(RuntimeError):
    """La fuente no entregó lo que se esperaba: red, formato o unidades."""


@dataclass(frozen=True)
class VerificacionUnidad:
    serie_id: str
    unidad_configurada: str
    unidad_declarada: str | None
    verificada: bool
    detalle: str

    @property
    def etiqueta(self) -> str:
        return "VERIFICADA" if self.verificada else "NO VERIFICADA"


def ruta_cruda(serie: SerieFRED, dir_crudo: Path, fecha_descarga: date) -> Path:
    return dir_crudo / f"{serie.id}_{fecha_descarga.isoformat()}.csv"


def descargar_csv(
    serie: SerieFRED,
    dir_crudo: Path,
    fecha_descarga: date,
    sesion: requests.Session | None = None,
) -> tuple[Path, bool]:
    """Baja el CSV crudo de una serie. Devuelve (ruta, se_descargo_ahora).

    Si ya existe la descarga de hoy la reutiliza: el archivo crudo es un
    registro de lo que la fuente dijo ese día y no se pisa.
    """
    destino = ruta_cruda(serie, dir_crudo, fecha_descarga)
    if destino.exists():
        return destino, False

    dir_crudo.mkdir(parents=True, exist_ok=True)
    url = URL_CSV.format(id=serie.id)
    cliente = sesion or requests
    try:
        respuesta = cliente.get(url, timeout=TIEMPO_LIMITE)
        respuesta.raise_for_status()
    except requests.RequestException as error:
        raise ErrorDeFuente(f"no se pudo descargar {serie.id} desde {url}: {error}") from error

    texto = respuesta.text
    if not texto.strip() or "," not in texto.splitlines()[0]:
        raise ErrorDeFuente(f"{serie.id}: la respuesta de FRED no parece un CSV")

    temporal = destino.with_suffix(".csv.tmp")
    temporal.write_text(texto, encoding="utf-8")
    temporal.replace(destino)
    return destino, True


def leer_csv_crudo(ruta: Path, serie: SerieFRED) -> pd.Series:
    """Lee un CSV crudo de FRED y lo devuelve en miles de millones de USD.

    FRED marca los datos faltantes con un punto. Esos quedan afuera: un hueco es
    un hueco y se reporta más adelante, no se rellena aquí.
    """
    tabla = pd.read_csv(ruta)
    if tabla.shape[1] < 2:
        raise ErrorDeFuente(f"{serie.id}: el CSV tiene menos de dos columnas")

    columna_fecha, columna_valor = tabla.columns[0], tabla.columns[1]
    if normalizar_texto(columna_fecha) not in {"date", "observation_date"}:
        raise ErrorDeFuente(
            f"{serie.id}: la primera columna es '{columna_fecha}', se esperaba la fecha"
        )
    if normalizar_texto(columna_valor) != normalizar_texto(serie.id):
        raise ErrorDeFuente(
            f"{serie.id}: la segunda columna es '{columna_valor}', se esperaba '{serie.id}'"
        )

    fechas = pd.to_datetime(tabla[columna_fecha], errors="coerce")
    valores = pd.to_numeric(tabla[columna_valor], errors="coerce")
    indice = pd.DatetimeIndex(fechas)
    indice.name = "fecha"  # el nombre del encabezado de FRED cambió con el tiempo
    resultado = pd.Series(valores.to_numpy(), index=indice, name=serie.id)
    resultado = resultado[resultado.index.notna()].dropna().sort_index()
    resultado = resultado[~resultado.index.duplicated(keep="last")]
    return resultado * serie.factor


def unidad_declarada(
    serie: SerieFRED, sesion: requests.Session | None = None
) -> tuple[str | None, str]:
    """Lee la unidad que FRED declara para la serie. Devuelve (unidad, motivo).

    `unidad` es None si no se pudo leer. `motivo` dice siempre por qué, y eso no
    es un lujo: la versión anterior devolvía None para cualquier causa —red
    cortada, 404, redirección a HTML, encabezado con otro formato— y el operador
    veía "NO VERIFICADA" sin manera de saber cuál de todas era. En la primera
    corrida real del pipeline las tres series salieron NO VERIFICADAS y no hubo
    forma de distinguir el caso desde la salida. Ver A-S2-9.

    Sigue siendo mejor esfuerzo: si no se puede leer, la corrida continúa y
    quedan como red la banda de orden de magnitud y el gate del H.4.1.
    """
    url = URL_METADATOS.format(id=serie.id)
    cliente = sesion or requests
    try:
        respuesta = cliente.get(url, timeout=TIEMPO_LIMITE)
    except requests.RequestException as error:
        return None, f"{url} no respondió ({type(error).__name__}: {error})"

    if respuesta.status_code != 200:
        return None, f"{url} respondió HTTP {respuesta.status_code}"

    lineas = respuesta.text.splitlines()
    for linea in lineas[:LINEAS_ENCABEZADO_METADATOS]:
        if normalizar_texto(linea).startswith("units:"):
            return linea.split(":", 1)[1].strip(), f"leída de {url}"

    tipo = respuesta.headers.get("Content-Type", "sin Content-Type")
    primera = next((l.strip() for l in lineas if l.strip()), "(respuesta vacía)")
    return None, (
        f"{url} respondió HTTP 200 ({tipo}) pero no hay línea 'Units:' en las "
        f"primeras {LINEAS_ENCABEZADO_METADATOS} líneas; la primera línea con "
        f"contenido es {primera[:80]!r}"
    )


def verificar_unidades(
    serie: SerieFRED, declarada: str | None, motivo: str = ""
) -> VerificacionUnidad:
    """Contrasta la unidad configurada contra la que declara FRED.

    `motivo` es lo que devolvió `unidad_declarada`. Se arrastra hasta el detalle
    para que el changelog quede con la causa concreta y no con un "no se pudo".
    """
    if declarada is None:
        causa = f"; causa: {motivo}" if motivo else ""
        return VerificacionUnidad(
            serie_id=serie.id,
            unidad_configurada=serie.unidad,
            unidad_declarada=None,
            verificada=False,
            detalle=(
                "no se pudo leer los metadatos de FRED; se usa la unidad configurada "
                f"({serie.unidad}) y quedan como control la banda de orden de magnitud "
                f"y el caso de validación{causa}"
            ),
        )

    clave = EQUIVALENCIAS_UNIDAD.get(normalizar_texto(declarada))
    if clave is None:
        return VerificacionUnidad(
            serie_id=serie.id,
            unidad_configurada=serie.unidad,
            unidad_declarada=declarada,
            verificada=False,
            detalle=f"FRED declara '{declarada}', una unidad que este script no sabe normalizar",
        )
    if clave != serie.unidad:
        raise ErrorDeFuente(
            f"{serie.id}: FRED declara '{declarada}' ({clave}) pero la configuración dice "
            f"'{serie.unidad}'. Corregir configuracion.py y registrarlo en SUPUESTOS.md; "
            "no ajustar el cálculo para compensar."
        )
    return VerificacionUnidad(
        serie_id=serie.id,
        unidad_configurada=serie.unidad,
        unidad_declarada=declarada,
        verificada=True,
        detalle=f"FRED declara '{declarada}', coincide con la configuración",
    )


def verificar_orden_de_magnitud(valores: pd.Series, serie: SerieFRED) -> None:
    """Control de cordura: atrapa un error de unidad de 1000x aunque no haya red."""
    if valores.empty:
        raise ErrorDeFuente(f"{serie.id}: la serie quedó vacía después de limpiar")
    minimo, maximo = serie.banda_plausible
    fuera = valores[(valores < minimo) | (valores > maximo)]
    if not fuera.empty:
        muestra = ", ".join(
            f"{fecha.date()}={valor:.3f}" for fecha, valor in fuera.head(3).items()
        )
        raise ErrorDeFuente(
            f"{serie.id}: {len(fuera)} valores fuera de la banda plausible "
            f"[{minimo}, {maximo}] miles de millones ({muestra}). "
            "Suele indicar que la unidad declarada cambió en la fuente."
        )
