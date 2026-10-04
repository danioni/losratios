"""Lectura de cada fuente, descarga con caché y manifiesto. Sin red."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from senales import fuentes_precios
from senales.configuracion import (
    COLUMNAS_DESCARGAS,
    DESCARGA_COIN_METRICS,
    DESCARGA_NASDAQCOM,
    DESCARGA_PINK_SHEET,
    DESCARGA_SHILLER,
    DESCARGAS,
)
from senales.fuentes_fred import ErrorDeFuente
from tests.datos_ratios import (
    csv_fred,
    diaria_calendario,
    diaria_habil,
    documento_coin_metrics,
    escribir_pink_sheet,
    filas_descripcion,
    filas_pink_sheet,
    filas_shiller,
)

HOY = date(2026, 10, 4)


# --- Pink Sheet --------------------------------------------------------------


def test_el_pink_sheet_se_lee_de_un_xlsx_con_su_forma_real(tmp_path):
    pink = fuentes_precios.leer_pink_sheet(escribir_pink_sheet(tmp_path / "pink.xlsx"))
    assert pink.oro[pd.Timestamp("2026-08-01")] == 4400.0
    assert pink.plata[pd.Timestamp("2026-09-01")] == 64.5
    assert pink.actualizada == date(2026, 10, 2)


def test_el_pink_sheet_no_inventa_los_meses_marcados_como_faltantes():
    """El archivo marca lo que no tiene con '…'. Un hueco es un hueco."""
    filas = filas_pink_sheet(oro={"2026-08": 4400.0, "2026-09": 4300.0}, plata={"2026-09": 64.5})
    pink = fuentes_precios.interpretar_pink_sheet(filas, filas_descripcion())
    assert list(pink.plata.index) == [pd.Timestamp("2026-09-01")]
    assert len(pink.oro) == 2


def test_una_unidad_distinta_en_el_pink_sheet_detiene_la_corrida():
    filas = filas_pink_sheet(unidad_plata="($/kg)")
    with pytest.raises(ErrorDeFuente, match="unidad de 'Silver'"):
        fuentes_precios.interpretar_pink_sheet(filas, filas_descripcion())


def test_si_cambia_la_descripcion_del_oro_la_corrida_se_detiene():
    """A-R0-7: ya cambió una vez, en junio de 2025. La próxima no pasa en silencio."""
    otra = "Gold, average of weekly rates, from January 2027; previously spot"
    with pytest.raises(ErrorDeFuente, match="descripción del oro"):
        fuentes_precios.interpretar_pink_sheet(filas_pink_sheet(), filas_descripcion(oro=otra))


def test_si_cambia_la_descripcion_de_la_plata_la_corrida_se_detiene():
    """A-R0-8: si el Banco Mundial aclara la convención, hay que releerla."""
    otra = "Silver (UK), 99.9% refined, LBMA Silver Price, average of daily rates"
    with pytest.raises(ErrorDeFuente, match="descripción de la plata"):
        fuentes_precios.interpretar_pink_sheet(filas_pink_sheet(), filas_descripcion(plata=otra))


def test_sin_la_fecha_de_actualizacion_el_pink_sheet_la_deja_vacia():
    filas = filas_pink_sheet(actualizado="(sin fecha)")
    assert fuentes_precios.interpretar_pink_sheet(filas, filas_descripcion()).actualizada is None


# --- Shiller -----------------------------------------------------------------


def test_shiller_lee_la_fecha_como_anio_punto_mes():
    serie = fuentes_precios.interpretar_shiller(
        filas_shiller({"1871-01": 5.0, "1871-10": 5.5, "2026-08": 7000.0})
    )
    # 1871.1 es octubre, no enero: los dos primeros decimales son el mes.
    assert serie[pd.Timestamp("1871-10-01")] == 5.5
    assert serie[pd.Timestamp("1871-01-01")] == 5.0
    assert len(serie) == 3


def test_shiller_ignora_la_nota_al_pie_y_las_filas_sin_precio():
    filas = filas_shiller({"2026-07": 7400.0, "2026-08": 7700.0})
    filas.insert(-1, (2026.09, "", "", ""))
    serie = fuentes_precios.interpretar_shiller(filas)
    assert list(serie.index) == [pd.Timestamp("2026-07-01"), pd.Timestamp("2026-08-01")]


def test_shiller_sin_el_encabezado_esperado_detiene_la_corrida():
    with pytest.raises(ErrorDeFuente, match="encabezado"):
        fuentes_precios.interpretar_shiller([("Fecha", "Precio"), (2026.08, 7700.0)])


# --- FRED diario, Coin Metrics y contrastes ----------------------------------


def test_fred_diario_deja_afuera_los_dias_sin_dato():
    diaria = diaria_habil("2026-09-01", "2026-09-04", base=100.0)
    texto = csv_fred("NASDAQCOM", diaria, vacios=("2026-09-07",)) + "2026-09-08,.\n"
    serie = fuentes_precios.interpretar_fred_diario(texto, "NASDAQCOM")
    assert len(serie) == 4
    assert pd.Timestamp("2026-09-07") not in serie.index


def test_fred_diario_rechaza_un_csv_de_otra_serie():
    texto = csv_fred("SP500", diaria_habil("2026-09-01", "2026-09-04", base=100.0))
    with pytest.raises(ErrorDeFuente, match="NASDAQCOM"):
        fuentes_precios.interpretar_fred_diario(texto, "NASDAQCOM")


def test_coin_metrics_fecha_cada_fila_por_su_dia():
    diaria = diaria_calendario("2026-09-29", "2026-10-01", base=80000.0)
    serie = fuentes_precios.interpretar_coin_metrics(documento_coin_metrics(diaria))
    assert list(serie.index) == list(diaria.index)
    assert serie.iloc[0] == 80000.0


def test_coin_metrics_paginado_no_se_trunca_en_silencio():
    documento = documento_coin_metrics(diaria_calendario("2026-09-29", "2026-10-01", base=1.0))
    documento["next_page_url"] = "https://community-api.coinmetrics.io/v4/...&next_page_token=x"
    with pytest.raises(ErrorDeFuente, match="paginación"):
        fuentes_precios.interpretar_coin_metrics(documento)


def test_la_api_de_nasdaq_se_lee_con_su_formato_de_fecha_y_de_miles():
    documento = {"data": {"tradesTable": {"rows": [
        {"date": "10/02/2026", "close": "12,345.67"},
        {"date": "10/01/2026", "close": "12,300.00"},
    ]}}}
    serie = fuentes_precios.interpretar_nasdaq_api(documento)
    assert serie[pd.Timestamp("2026-10-02")] == 12345.67
    assert serie.index.is_monotonic_increasing


def test_la_api_de_nasdaq_sin_filas_es_un_error_de_fuente():
    with pytest.raises(ErrorDeFuente, match="tradesTable"):
        fuentes_precios.interpretar_nasdaq_api({"data": None, "status": {"rCode": 400}})


def test_bitstamp_fecha_cada_vela_por_el_dia_utc_que_abre():
    velas = [{"timestamp": "1790726400", "close": "83556.14"}]  # 2026-09-30 00:00 UTC
    serie = fuentes_precios.interpretar_bitstamp(velas)
    assert serie[pd.Timestamp("2026-09-30")] == 83556.14


# --- Descarga, caché y manifiesto --------------------------------------------


class RespuestaFalsa:
    def __init__(self, contenido: bytes, cabeceras: dict | None = None):
        self.content = contenido
        self.text = contenido.decode("utf-8", errors="replace")
        self.headers = cabeceras or {}

    def raise_for_status(self) -> None:
        return None


class SesionFalsa:
    """Devuelve una respuesta por URL y anota lo que se le pidió."""

    def __init__(self, respuestas: dict[str, RespuestaFalsa]):
        self.respuestas = respuestas
        self.pedidos: list[str] = []

    def get(self, url, **_):
        self.pedidos.append(url)
        return self.respuestas[url]


@pytest.fixture(autouse=True)
def sin_pausas(monkeypatch):
    monkeypatch.setattr(fuentes_precios, "PAUSA_ENTRE_PEDIDOS", 0.0)


def _vacio() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNAS_DESCARGAS)


def test_el_crudo_entra_al_repositorio_solo_si_la_licencia_permite_redistribuirlo(tmp_path):
    """A-R0-15: CC BY y CC BY-NC sí; sin licencia declarada o con reserva, no."""
    abierto, privado = tmp_path / "raw", tmp_path / "privado"
    lugares = {d.clave: fuentes_precios.ruta_cruda(d, HOY, abierto, privado).parent for d in DESCARGAS}
    assert lugares[DESCARGA_PINK_SHEET.clave] == abierto
    assert lugares[DESCARGA_SHILLER.clave] == privado
    assert lugares[DESCARGA_NASDAQCOM.clave] == privado
    assert lugares[DESCARGA_COIN_METRICS.clave] == abierto


def test_una_descarga_registra_url_bytes_hash_y_fecha_de_la_fuente(tmp_path):
    contenido = b"observation_date,NASDAQCOM\n1971-02-05,100.000\n"
    sesion = SesionFalsa({
        DESCARGA_NASDAQCOM.url: RespuestaFalsa(
            contenido, {"Last-Modified": "Sat, 03 Oct 2026 03:38:00 GMT"}
        )
    })
    registro = fuentes_precios.descargar(
        DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", tmp_path / "privado", _vacio(), sesion
    )
    assert registro.descargada_ahora
    assert registro.ruta.read_bytes() == contenido
    assert registro.sha256 == hashlib.sha256(contenido).hexdigest()
    assert registro.bytes == len(contenido)
    assert registro.actualizada == date(2026, 10, 3)
    assert registro.fila()["crudo_en_repo"] == "no"


def test_la_url_del_archivo_se_lee_de_la_pagina_de_la_fuente(tmp_path):
    """La URL del Pink Sheet cambia con cada publicación: no se asume estable."""
    archivo = "https://thedocs.worldbank.org/en/doc/abc-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
    pagina = f'<a href="{archivo}">Monthly prices</a>'.encode()
    sesion = SesionFalsa({
        DESCARGA_PINK_SHEET.url: RespuestaFalsa(pagina),
        archivo: RespuestaFalsa(b"PK\x03\x04 contenido"),
    })
    registro = fuentes_precios.descargar(
        DESCARGA_PINK_SHEET, HOY, tmp_path / "raw", tmp_path / "privado", _vacio(), sesion
    )
    assert registro.url == archivo
    assert sesion.pedidos == [DESCARGA_PINK_SHEET.url, archivo]
    assert registro.ruta.parent == tmp_path / "raw"


def test_un_enlace_sin_protocolo_se_completa():
    html = '<a href="//img1.wsimg.com/blobby/go/x/downloads/y/ie_data.xls?ver=1">Download</a>'
    assert fuentes_precios.extraer_enlace(html, DESCARGA_SHILLER) == (
        "https://img1.wsimg.com/blobby/go/x/downloads/y/ie_data.xls?ver=1"
    )


def test_si_la_pagina_ya_no_enlaza_el_archivo_la_corrida_se_detiene():
    with pytest.raises(ErrorDeFuente, match="cambió de lugar"):
        fuentes_precios.extraer_enlace("<html>sin enlaces</html>", DESCARGA_SHILLER)


def test_una_pagina_de_error_con_http_200_no_pasa_por_planilla(tmp_path):
    archivo = "https://img1.wsimg.com/x/ie_data.xls"
    sesion = SesionFalsa({
        DESCARGA_SHILLER.url: RespuestaFalsa(f'<a href="{archivo}">x</a>'.encode()),
        archivo: RespuestaFalsa(b"<!DOCTYPE html><html>Access denied</html>"),
    })
    with pytest.raises(ErrorDeFuente, match="no devolvió un archivo .xls"):
        fuentes_precios.descargar(
            DESCARGA_SHILLER, HOY, tmp_path / "raw", tmp_path / "privado", _vacio(), sesion
        )
    assert not list((tmp_path / "privado").glob("*"))


def test_el_crudo_del_dia_se_reutiliza_sin_salir_a_la_red(tmp_path):
    privado = tmp_path / "privado"
    privado.mkdir()
    ruta = privado / f"NASDAQCOM_{HOY}.csv"
    ruta.write_bytes(b"observation_date,NASDAQCOM\n1971-02-05,100.000\n")
    sesion = SesionFalsa({})
    registro = fuentes_precios.descargar(
        DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", privado, _vacio(), sesion
    )
    assert not registro.descargada_ahora
    assert sesion.pedidos == []


def _manifiesto_con(registro: fuentes_precios.RegistroDescarga, **cambios) -> pd.DataFrame:
    fila = {**registro.fila(), **cambios}
    return pd.DataFrame([fila], columns=COLUMNAS_DESCARGAS).astype(str)


def test_al_reutilizar_un_crudo_se_recupera_la_fecha_que_declaro_la_fuente(tmp_path):
    """El Last-Modified de Shiller decide qué meses están completos (A-R0-11).

    En una segunda corrida no hay cabecera HTTP: la fecha sale del manifiesto.
    """
    privado = tmp_path / "privado"
    privado.mkdir()
    ruta = privado / f"shiller_ie_data_{HOY}.xls"
    ruta.write_bytes(b"\xd0\xcf\x11\xe0 planilla")
    primera = fuentes_precios.descargar(
        DESCARGA_SHILLER, HOY, tmp_path / "raw", privado, _vacio(), SesionFalsa({})
    )
    manifiesto = _manifiesto_con(primera, actualizada="2026-09-02", url="https://ejemplo/ie_data.xls")
    segunda = fuentes_precios.descargar(
        DESCARGA_SHILLER, HOY, tmp_path / "raw", privado, manifiesto, SesionFalsa({})
    )
    assert segunda.actualizada == date(2026, 9, 2)
    assert segunda.url == "https://ejemplo/ie_data.xls"


def test_un_crudo_que_no_coincide_con_el_hash_publicado_no_se_usa(tmp_path):
    privado = tmp_path / "privado"
    privado.mkdir()
    ruta = privado / f"NASDAQCOM_{HOY}.csv"
    ruta.write_bytes(b"observation_date,NASDAQCOM\n1971-02-05,100.000\n")
    registro = fuentes_precios.descargar(
        DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", privado, _vacio(), SesionFalsa({})
    )
    ruta.write_bytes(b"observation_date,NASDAQCOM\n1971-02-05,999.000\n")
    with pytest.raises(ErrorDeFuente, match="El crudo cambió"):
        fuentes_precios.descargar(
            DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", privado, _manifiesto_con(registro), SesionFalsa({})
        )


def test_un_crudo_no_abierto_que_falta_dice_de_donde_bajarlo_y_con_que_hash(tmp_path):
    """A-R0-15: el repositorio trae el manifiesto, no el archivo."""
    privado = tmp_path / "privado"
    privado.mkdir()
    ruta = privado / f"NASDAQCOM_{HOY}.csv"
    ruta.write_bytes(b"observation_date,NASDAQCOM\n1971-02-05,100.000\n")
    registro = fuentes_precios.descargar(
        DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", privado, _vacio(), SesionFalsa({})
    )
    ruta.unlink()
    sesion = SesionFalsa({})
    with pytest.raises(ErrorDeFuente, match=registro.sha256):
        fuentes_precios.descargar(
            DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", privado, _manifiesto_con(registro), sesion
        )
    assert sesion.pedidos == [], "no se reemplaza un crudo publicado por una descarga nueva"


def test_el_manifiesto_tiene_una_fila_por_fecha_y_fuente(tmp_path):
    privado = tmp_path / "privado"
    privado.mkdir()
    (privado / f"NASDAQCOM_{HOY}.csv").write_bytes(b"observation_date,NASDAQCOM\n1971-02-05,100.000\n")
    registro = fuentes_precios.descargar(
        DESCARGA_NASDAQCOM, HOY, tmp_path / "raw", privado, _vacio(), SesionFalsa({})
    )
    ruta = tmp_path / "series" / "descargas_ratios.csv"
    assert fuentes_precios.actualizar_manifiesto(ruta, [registro]) is True
    assert fuentes_precios.actualizar_manifiesto(ruta, [registro]) is False
    tabla = fuentes_precios.leer_manifiesto(ruta)
    assert list(tabla.columns) == COLUMNAS_DESCARGAS
    assert len(tabla) == 1
    assert tabla.iloc[0]["sha256"] == registro.sha256
    assert "\r" not in ruta.read_bytes().decode("utf-8")


def test_el_manifiesto_conserva_las_descargas_de_otros_dias(tmp_path):
    privado = tmp_path / "privado"
    privado.mkdir()
    ruta = tmp_path / "descargas_ratios.csv"
    for dia in (date(2026, 10, 4), date(2026, 11, 3)):
        (privado / f"NASDAQCOM_{dia}.csv").write_bytes(f"observation_date,NASDAQCOM\n{dia},1.0\n".encode())
        registro = fuentes_precios.descargar(
            DESCARGA_NASDAQCOM, dia, tmp_path / "raw", privado, _vacio(), SesionFalsa({})
        )
        fuentes_precios.actualizar_manifiesto(ruta, [registro])
    tabla = fuentes_precios.leer_manifiesto(ruta)
    assert list(tabla["fecha_descarga"]) == ["2026-10-04", "2026-11-03"]
