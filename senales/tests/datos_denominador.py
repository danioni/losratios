"""Fuentes fabricadas para probar la fase D0 sin red.

Cada función devuelve el texto o los bytes con la forma que entrega la fuente
real, con números pequeños y coherentes entre fuente y contraste, para que los
gates cierren salvo que un test los haga fallar a propósito.
"""

from __future__ import annotations

import io
import json
import zipfile

import pandas as pd

MESES = pd.period_range("2025-01", "2026-08", freq="M")  # 20 meses


def meses_ts() -> pd.DatetimeIndex:
    return pd.DatetimeIndex([p.to_timestamp() for p in MESES])


# --- Junta: ZIP de XML -----------------------------------------------------------


def xml_junta(series: dict[str, tuple[dict, list[tuple[str, float | None]]]]) -> bytes:
    """Un XML con la forma mínima que lee leer_xml_junta: Series > Obs."""
    partes = ['<?xml version="1.0"?><root>']
    for nombre, (atributos, observaciones) in series.items():
        extra = " ".join(f'{k}="{v}"' for k, v in atributos.items())
        partes.append(f'<Series SERIES_NAME="{nombre}" {extra}>')
        partes.append(f"<Annotations><Annotation><AnnotationText>{nombre} de prueba</AnnotationText></Annotation></Annotations>")
        for fecha, valor in observaciones:
            if valor is None:
                partes.append(f'<Obs TIME_PERIOD="{fecha}" OBS_VALUE="ND" OBS_STATUS="ND"/>')
            else:
                partes.append(f'<Obs TIME_PERIOD="{fecha}" OBS_VALUE="{valor}" OBS_STATUS="A"/>')
        partes.append("</Series>")
    partes.append("</root>")
    return "".join(partes).encode("utf-8")


def zip_junta(nombre_xml: str, series) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archivo:
        archivo.writestr(nombre_xml, xml_junta(series))
    return buffer.getvalue()


def m2_eeuu() -> pd.Series:
    return pd.Series([21000.0 + 50.0 * i for i in range(len(MESES))], index=meses_ts())


def zip_h6() -> bytes:
    ajustada = m2_eeuu()
    atributos = {"UNIT_MULT": "1e+09", "CURRENCY": "USD", "FREQ": "129"}
    return zip_junta(
        "H6_data.xml",
        {
            "M2.M": (atributos, [((m + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"), v) for m, v in ajustada.items()]),
            "M2_N.M": (atributos, [((m + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"), v + 10.0) for m, v in ajustada.items()]),
        },
    )


def miercoles() -> pd.DatetimeIndex:
    return pd.date_range("2025-01-01", "2026-09-30", freq="W-WED")


def balance_fed_semanal() -> pd.Series:
    fechas = miercoles()
    return pd.Series([6_700_000.0 + 1000.0 * i for i in range(len(fechas))], index=fechas)


def zip_h41() -> bytes:
    semanal = balance_fed_semanal()
    atributos = {"UNIT_MULT": "1000000", "CURRENCY": "USD", "FREQ": "19"}
    return zip_junta(
        "H41_data.xml",
        {"RESPPMA_N.WW": (atributos, [(f.strftime("%Y-%m-%d"), v) for f, v in semanal.items()])},
    )


def dias_habiles() -> pd.DatetimeIndex:
    return pd.bdate_range("2025-01-02", "2026-09-25")


def cambio_diario(base: float, pendiente: float) -> pd.Series:
    fechas = dias_habiles()
    return pd.Series([base + pendiente * i for i in range(len(fechas))], index=fechas)


def cambio_mensual_promedio(diaria: pd.Series) -> pd.Series:
    """El promedio mensual que publica la Junta (G.5), incluido el mes en curso."""
    return diaria.groupby(diaria.index.to_period("M")).mean()


def zip_h10() -> bytes:
    atributos = {"UNIT_MULT": "1", "FREQ": "9"}
    series = {}
    for diaria, mensual, base, pendiente in (
        ("RXI$US_N.B.EU", "RXI$US_N.M.EU", 1.10, 0.0001),
        ("RXI_N.B.JA", "RXI_N.M.JA", 150.0, 0.01),
        ("RXI_N.B.CH", "RXI_N.M.CH", 7.0, 0.0005),
    ):
        d = cambio_diario(base, pendiente)
        m = cambio_mensual_promedio(d)
        series[diaria] = (atributos, [(f.strftime("%Y-%m-%d"), round(v, 4)) for f, v in d.items()])
        series[mensual] = (
            {"UNIT_MULT": "1", "FREQ": "129"},
            [((p.to_timestamp() + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"), round(v, 4)) for p, v in m.items()],
        )
    return zip_junta("H10_data.xml", series)


def html_h6() -> str:
    """La Tabla 1 del H.6 con la estructura real: encabezados con id y celdas con headers."""
    ajustada = m2_eeuu()
    filas = []
    for i, (mes, valor) in enumerate(ajustada.items(), start=1):
        rotulo = mes.strftime("%b. %Y").replace("May.", "May").replace("Jun.", "June").replace("Jul.", "July").replace("Sep.", "Sept.")
        filas.append(
            f'<tr><th id="t1tg1r{i}" headers="t1tg1a1">{rotulo}</th>'
            f'<td class="data" headers="t1tg1a2 t1tg1b1 t1tg1r{i}">1.0</td>'
            f'<td class="data" headers="t1tg1a2 t1tg1b2 t1tg1r{i}">{valor:,.1f}</td>'
            f'<td class="data" headers="t1tg1a3 t1tg1b4 t1tg1r{i}">1.0</td>'
            f'<td class="data" headers="t1tg1a3 t1tg1b5 t1tg1r{i}">{valor + 10.0:,.1f}</td></tr>'
        )
    return (
        '<html><body><table title="Table 1" id="t1tg1"><thead><tr>'
        '<th rowspan="3" id="t1tg1a1" class="colhead">Date</th>'
        '<th colspan="2" id="t1tg1a2" class="colhead">Seasonally adjusted</th>'
        '<th colspan="8" id="t1tg1a3" class="colhead">Not seasonally adjusted</th></tr><tr>'
        '<th id="t1tg1b1" class="colhead" headers="t1tg1a2">M1 <sup>1</sup></th>'
        '<th id="t1tg1b2" class="colhead" headers="t1tg1a2">M2 <a href="#f"><sup>2</sup></a></th>'
        '<th id="t1tg1b4" class="colhead" headers="t1tg1a3">M1 <sup>1</sup></th>'
        '<th id="t1tg1b5" class="colhead" headers="t1tg1a3">M2 <sup>2</sup></th>'
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table></body></html>"
    )


def csv_fred_walcl() -> str:
    semanal = balance_fed_semanal()
    return "observation_date,WALCL\n" + "".join(f"{f.date()},{int(v)}\n" for f, v in semanal.items())


# --- BCE -----------------------------------------------------------------------


def csv_bce(clave: str, observaciones: list[tuple[str, float]], unidad: str = "EUR", mult: str = "6") -> str:
    lineas = ["KEY,FREQ,TIME_PERIOD,OBS_VALUE,OBS_STATUS,UNIT,UNIT_MULT,TITLE_COMPL"]
    for periodo, valor in observaciones:
        lineas.append(f"{clave},M,{periodo},{valor},A,{unidad},{mult},Serie de prueba")
    return "\n".join(lineas) + "\n"


def m2_eurozona() -> pd.Series:
    return pd.Series([16_000_000.0 + 20_000.0 * i for i in range(len(MESES))], index=meses_ts())


def csv_bce_m2(clave: str, desplazamiento: float = 0.0) -> str:
    return csv_bce(clave, [(m.strftime("%Y-%m"), v + desplazamiento) for m, v in m2_eurozona().items()])


def viernes() -> pd.DatetimeIndex:
    return pd.date_range("2025-01-03", "2026-09-25", freq="W-FRI")


def balance_eurosistema_semanal() -> pd.Series:
    fechas = viernes()
    return pd.Series([6_300_000.0 - 1000.0 * i for i in range(len(fechas))], index=fechas)


def csv_bce_balance(clave: str) -> str:
    semanal = balance_eurosistema_semanal()
    observaciones = []
    for fecha, valor in semanal.items():
        anio, semana, _ = fecha.isocalendar()
        observaciones.append((f"{anio}-W{semana:02d}", valor))
    return csv_bce(clave, observaciones)


# --- Banco de Japón --------------------------------------------------------------


def m2_japon() -> pd.Series:
    return pd.Series([12_900_000.0 + 5000.0 * i for i in range(len(MESES))], index=meses_ts())


def balance_boj() -> pd.Series:
    return pd.Series([6_400_000.0 + 2000.0 * i for i in range(len(MESES))], index=meses_ts())


def csv_boj(codigo: str, serie: pd.Series, nombre: str = "Serie de prueba", estado: str = "200") -> str:
    lineas = [
        f"STATUS,{estado}",
        "MESSAGEID,M181000I",
        "SERIES_CODE,NAME_OF_TIME_SERIES,UNIT,FREQUENCY,CATEGORY,LAST_UPDATE,SURVEY_DATES,VALUES",
    ]
    for mes, valor in serie.items():
        lineas.append(f"{codigo},{nombre},100 million yen,MONTHLY,Prueba,20260909,{mes.strftime('%Y%m')},{valor:.0f}")
    return "\n".join(lineas) + "\n"


def json_estat(serie: pd.Series, indicador: str) -> str:
    objetos = [
        {"VALUE": {"@indicator": indicador, "@time": mes.strftime("%Y%m") + "00", "$": f"{valor:.0f}"}}
        for mes, valor in serie.items()
    ]
    return json.dumps({"GET_STATS": {"STATISTICAL_DATA": {"DATA_INF": {"DATA_OBJ": objetos}}}})


# --- OCDE y BIS ------------------------------------------------------------------


def dinero_china() -> pd.Series:
    return pd.Series([330_000_000.0 + 1_000_000.0 * i for i in range(len(MESES))], index=meses_ts())


def csv_ocde(serie: pd.Series, area: str = "CHN", medida: str = "MABM", rotulo: str = "M3") -> str:
    lineas = [
        "STRUCTURE,REF_AREA,Reference area,FREQ,MEASURE,Measure,UNIT_MEASURE,ADJUSTMENT,Adjustment,TIME_PERIOD,OBS_VALUE,UNIT_MULT"
    ]
    for mes, valor in serie.items():
        lineas.append(
            f"DATAFLOW,{area},China,M,{medida},{rotulo},XDC,N,Neither seasonally adjusted nor calendar adjusted,"
            f"{mes.strftime('%Y-%m')},{valor:.0f},6"
        )
    return "\n".join(lineas) + "\n"


def csv_bis_activos(area: str, mensual: pd.Series) -> str:
    """WS_CBTA en miles de millones de moneda local, con las columnas que lee el pipeline."""
    lineas = ["FREQ,REF_AREA,UNIT_MEASURE,TRANSFORMATION,UNIT_MULT,TIME_PERIOD,OBS_VALUE"]
    for mes, valor in mensual.items():
        lineas.append(f"M,{area},XDC,N,9,{mes.strftime('%Y-%m')},{valor}")
    return "\n".join(lineas) + "\n"


def csv_bis_cambio(moneda: str, promedio: pd.Series) -> str:
    lineas = ["FREQ,REF_AREA,CURRENCY,COLLECTION,UNIT_MULT,TIME_PERIOD,OBS_VALUE"]
    for mes, valor in promedio.items():
        lineas.append(f"M,XX,{moneda},A,0,{mes.strftime('%Y-%m')},{valor}")
    return "\n".join(lineas) + "\n"


# --- Banco de España -------------------------------------------------------------

MESES_BDE = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def csv_bde(codigo: str, serie: pd.Series) -> str:
    lineas = [
        f'"CÓDIGO DE LA SERIE",X_OTRA,{codigo}',
        '"DESCRIPCIÓN DE LA SERIE","Otra","Agregados monetarios de la UEM. M2. Saldos"',
    ]
    for mes, valor in serie.items():
        lineas.append(f'"{MESES_BDE[mes.month - 1]} {mes.year}",1,{valor:.0f}')
    return "\n".join(lineas) + "\n"
