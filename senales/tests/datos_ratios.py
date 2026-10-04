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

from senales.configuracion import AnclaAnual

# Tres años completos y planos, para que el gate anual tenga contra qué cerrar,
# y un 2026 con el segundo trimestre dentro de las bandas de LBMA que están en
# configuracion.py.
ORO_ANUAL = {2023: 4100.0, 2024: 4200.0, 2025: 4300.0}
PLATA_ANUAL = {2023: 60.0, 2024: 62.0, 2025: 64.0}
_ORO_2026 = {"2026-01": 4750.0, "2026-02": 4780.0, "2026-03": 4800.0, "2026-04": 4700.0,
             "2026-05": 4600.0, "2026-06": 4200.0, "2026-07": 4100.0, "2026-08": 4400.0,
             "2026-09": 4300.0}
_PLATA_2026 = {"2026-01": 80.0, "2026-02": 79.0, "2026-03": 78.0, "2026-04": 76.0,
               "2026-05": 78.0, "2026-06": 67.0, "2026-07": 59.0, "2026-08": 65.0,
               "2026-09": 64.5}
ORO = {f"{a}-{m:02d}": v for a, v in ORO_ANUAL.items() for m in range(1, 13)} | _ORO_2026
PLATA = {f"{a}-{m:02d}": v for a, v in PLATA_ANUAL.items() for m in range(1, 13)} | _PLATA_2026


def anclas_de_prueba(factor_oro: float = 1.0, factor_plata: float = 1.0) -> tuple[AnclaAnual, ...]:
    """Anclas anuales que coinciden con los datos de prueba, o que se apartan un factor."""
    from datetime import date

    def ancla(serie: str, anio: int, valor: float) -> AnclaAnual:
        return AnclaAnual(serie, anio, valor, "ancla de prueba", "https://ejemplo.invalid/", date(2026, 10, 4))

    return tuple(ancla("oro", a, v * factor_oro) for a, v in ORO_ANUAL.items()) + tuple(
        ancla("plata", a, v * factor_plata) for a, v in PLATA_ANUAL.items()
    )


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


def escribir_pink_sheet(ruta: Path, descripcion_oro: str = PINK_SHEET_DESCRIPCION_ORO, **opciones) -> Path:
    import openpyxl

    libro = openpyxl.Workbook()
    precios = libro.active
    precios.title = "Monthly Prices"
    for fila in filas_pink_sheet(**opciones):
        precios.append(list(fila))
    descripcion = libro.create_sheet("Description")
    for fila in filas_descripcion(oro=descripcion_oro):
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


# --- A-R0-19: la edición congelada, sin redondear ------------------------------
#
# Mismos meses que los dos primeros años de la edición vigente de prueba, con los
# decimales que la vigente redondea: 4100.27 se publica hoy como 4100, y 60.0137
# como 60.0. Junio de 2024 queda exactamente a medio paso (4200.5 contra 4200).
ORO_CONGELADA = {f"2023-{m:02d}": 4100.27 for m in range(1, 13)} | {
    f"2024-{m:02d}": (4200.5 if m == 6 else 4199.84) for m in range(1, 13)
}
PLATA_CONGELADA = {f"2023-{m:02d}": 60.0137 for m in range(1, 13)} | {
    f"2024-{m:02d}": 61.972 for m in range(1, 13)
}
ARCHIVO_CONGELADA = "pink_sheet_edicion_2025-01-03.xlsx"


def escribir_edicion_congelada(directorio: Path, oro: dict | None = None, plata: dict | None = None):
    """Escribe la edición congelada de prueba y devuelve su declaración, con su hash."""
    import dataclasses
    import hashlib

    from senales.configuracion import PINK_SHEET_CONGELADA

    ruta = escribir_pink_sheet(
        directorio / ARCHIVO_CONGELADA,
        descripcion_oro=PINK_SHEET_CONGELADA.descripcion_oro,
        oro=ORO_CONGELADA if oro is None else oro,
        plata=PLATA_CONGELADA if plata is None else plata,
        actualizado="Updated on January 03, 2025",
    )
    return dataclasses.replace(
        PINK_SHEET_CONGELADA,
        archivo=ARCHIVO_CONGELADA,
        sha256=hashlib.sha256(ruta.read_bytes()).hexdigest(),
    )
