"""Datos de prueba de la fase R. Todo sintético: ningún test toca la red.

Las fuentes de los índices y de BTC no son abiertas, así que en el repositorio
no hay un recorte real de ninguna. Lo que se reproduce acá es la *forma* de
cada archivo —hojas, encabezados, marcas de dato faltante— con números
inventados que no salen de ninguna fuente.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from senales.configuracion import PINK_SHEET_DESCRIPCION_ORO, PINK_SHEET_DESCRIPCION_PLATA

# Valores del segundo trimestre de 2026 dentro de las bandas de LBMA que están
# en configuracion.py, para que el control de bandas cierre con datos de prueba.
ORO = {"2026-03": 4800.0, "2026-04": 4700.0, "2026-05": 4600.0, "2026-06": 4200.0,
       "2026-07": 4100.0, "2026-08": 4400.0, "2026-09": 4300.0}
PLATA = {"2026-03": 78.0, "2026-04": 76.0, "2026-05": 78.0, "2026-06": 67.0,
         "2026-07": 59.0, "2026-08": 65.0, "2026-09": 64.5}


def filas_pink_sheet(
    oro: dict[str, float] | None = None,
    plata: dict[str, float] | None = None,
    actualizado: str = "Updated on October 02, 2026",
    unidad_plata: str = "($/troy oz)",
) -> list[tuple]:
    """Las filas de la hoja 'Monthly Prices', con la forma del archivo real."""
    oro = ORO if oro is None else oro
    plata = PLATA if plata is None else plata
    filas: list[tuple] = [
        ("World Bank Commodity Price Data (The Pink Sheet)", None, None, None),
        ("monthly prices in nominal US dollars, 1960 to present", None, None, None),
        ("(monthly series are available only in nominal US dollars)", None, None, None),
        (actualizado, None, None, None),
        (None, "Crude oil, average", "Gold", "Silver"),
        (None, "($/bbl)", "($/troy oz)", unidad_plata),
    ]
    for mes in sorted(set(oro) | set(plata)):
        etiqueta = mes.replace("-", "M")
        filas.append((etiqueta, 70.0, oro.get(mes, "…"), plata.get(mes, "…")))
    return filas


def filas_descripcion(
    oro: str = PINK_SHEET_DESCRIPCION_ORO, plata: str = PINK_SHEET_DESCRIPCION_PLATA
) -> list[tuple]:
    return [
        ("World Bank Commodity Price Data (The Pink Sheet)", None, None),
        ("Series Description", None, "Sources"),
        ("   *", oro, "Bloomberg; World Bank."),
        # El archivo real trae dos espacios después de "Harman.".
        ("   *", plata.replace("Harman. Grade", "Harman.  Grade"), "London Bullion Market; World Bank."),
    ]


def escribir_pink_sheet(ruta: Path, **opciones) -> Path:
    import openpyxl

    libro = openpyxl.Workbook()
    precios = libro.active
    precios.title = "Monthly Prices"
    for fila in filas_pink_sheet(**opciones):
        precios.append(list(fila))
    descripcion = libro.create_sheet("Description")
    for fila in filas_descripcion():
        descripcion.append(list(fila))
    libro.save(ruta)
    return ruta


def filas_shiller(valores: dict[str, float], nota_al_pie: bool = True) -> list[tuple]:
    """Las filas de la hoja 'Data' de ie_data.xls: fecha como año.mes en un float."""
    filas: list[tuple] = [
        ("",) * 4,
        ("Stock Market Data Used in \"Irrational Exuberance\"", "", "", ""),
        ("", "S&P", "", ""),
        ("", "Comp.", "Dividend", "Earnings"),
        ("Date", "P", "D", "E"),
    ]
    for mes, valor in sorted(valores.items()):
        anio, numero = mes.split("-")
        filas.append((float(f"{anio}.{numero}"), valor, 1.0, 2.0))
    if nota_al_pie:
        filas.append(("", "Sept price is Sept 1st close", "", ""))
    return filas


def csv_fred(id_serie: str, diaria: pd.Series, vacios: tuple[str, ...] = ()) -> str:
    lineas = [f"observation_date,{id_serie}"]
    for fecha, valor in diaria.items():
        lineas.append(f"{fecha.date()},{valor:.3f}")
    lineas.extend(f"{fecha}," for fecha in vacios)
    return "\n".join(lineas) + "\n"


def documento_coin_metrics(diaria: pd.Series) -> dict:
    return {
        "data": [
            {"asset": "btc", "time": f"{fecha.date()}T00:00:00.000000000Z", "PriceUSD": repr(float(valor))}
            for fecha, valor in diaria.items()
        ]
    }


def diaria_habil(inicio: str, fin: str, base: float, pendiente: float = 0.5) -> pd.Series:
    """Cierres de días hábiles, con una pendiente para que el mes no sea plano."""
    fechas = pd.bdate_range(inicio, fin)
    return pd.Series([base + pendiente * i for i in range(len(fechas))], index=fechas)


def diaria_calendario(inicio: str, fin: str, base: float, pendiente: float = 10.0) -> pd.Series:
    fechas = pd.date_range(inicio, fin)
    return pd.Series([base + pendiente * i for i in range(len(fechas))], index=fechas)
