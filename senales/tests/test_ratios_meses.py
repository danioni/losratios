"""A-R0-1: promedio mensual de cierres diarios, y solo de meses completos."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from senales.configuracion import SERIE_BTC, SERIE_ORO
from senales.fuentes_fred import ErrorDeFuente
from senales.ratios import desde_el_mes, meses_completos, promedio_mensual, verificar_banda
from tests.datos_ratios import diaria_calendario, diaria_habil


def test_el_valor_del_mes_es_el_promedio_y_no_el_cierre():
    diaria = diaria_habil("2026-08-03", "2026-09-10", base=100.0, pendiente=1.0)
    mensual, _ = promedio_mensual(diaria, dias_calendario=False)
    agosto = diaria.loc["2026-08"]
    assert mensual[pd.Timestamp("2026-08-01")] == pytest.approx(agosto.mean())
    assert mensual[pd.Timestamp("2026-08-01")] != pytest.approx(agosto.iloc[-1])


def test_el_mes_en_curso_no_entra():
    diaria = diaria_habil("2026-08-03", "2026-09-10", base=100.0)
    mensual, descartados = promedio_mensual(diaria, dias_calendario=False)
    assert list(mensual.index) == [pd.Timestamp("2026-08-01")]
    assert any("2026-09" in d and "mes en curso" in d for d in descartados)


def test_un_mes_cuya_ultima_observacion_es_su_ultimo_dia_sigue_en_curso():
    """Hasta que la serie no tiene un dato posterior, no se sabe que el mes cerró."""
    diaria = diaria_habil("2026-08-03", "2026-09-30", base=100.0)
    mensual, _ = promedio_mensual(diaria, dias_calendario=False)
    assert pd.Timestamp("2026-09-01") not in mensual.index


def test_el_primer_mes_queda_afuera_si_la_serie_arranca_empezado():
    """El Nasdaq Composite arranca el 5 de febrero de 1971."""
    diaria = diaria_habil("1971-02-05", "1971-04-06", base=100.0)
    mensual, descartados = promedio_mensual(diaria, dias_calendario=False)
    assert list(mensual.index) == [pd.Timestamp("1971-03-01")]
    assert any("1971-02" in d and "empezado" in d for d in descartados)


def test_el_primer_mes_entra_si_antes_solo_hubo_fin_de_semana():
    """El 1 y el 2 de octubre de 2016 fueron sábado y domingo."""
    diaria = diaria_habil("2016-10-03", "2016-11-03", base=2000.0)
    mensual, descartados = promedio_mensual(diaria, dias_calendario=False)
    assert pd.Timestamp("2016-10-01") in mensual.index
    assert not any("2016-10" in d for d in descartados)


def test_btc_promedia_todos_los_dias_calendario():
    """A-R0-5: el mes de BTC tiene 28 a 31 observaciones, fines de semana incluidos."""
    diaria = diaria_calendario("2026-08-01", "2026-09-02", base=60000.0)
    mensual, _ = promedio_mensual(diaria, dias_calendario=True)
    assert mensual[pd.Timestamp("2026-08-01")] == pytest.approx(diaria.loc["2026-08"].mean())
    assert len(diaria.loc["2026-08"]) == 31


def test_un_mes_de_btc_al_que_le_falta_un_dia_no_se_publica():
    diaria = diaria_calendario("2026-07-01", "2026-09-02", base=60000.0)
    diaria = diaria.drop(pd.Timestamp("2026-08-15"))
    mensual, descartados = promedio_mensual(diaria, dias_calendario=True)
    assert pd.Timestamp("2026-08-01") not in mensual.index
    assert pd.Timestamp("2026-07-01") in mensual.index
    assert any("2026-08" in d and "30 de 31" in d for d in descartados)


def test_el_primer_mes_parcial_de_btc_queda_afuera():
    """Coin Metrics arranca el 18 de julio de 2010."""
    diaria = diaria_calendario("2010-07-18", "2010-09-02", base=0.05, pendiente=0.001)
    mensual, descartados = promedio_mensual(diaria, dias_calendario=True)
    assert list(mensual.index) == [pd.Timestamp("2010-08-01")]
    assert any("2010-07" in d and "14 de 31" in d for d in descartados)


def _mensual(meses: list[str]) -> pd.Series:
    indice = pd.DatetimeIndex([pd.Timestamp(m + "-01") for m in meses], name="mes")
    return pd.Series(range(1, len(meses) + 1), index=indice, dtype="float64")


def test_una_fuente_mensual_se_recorta_a_la_fecha_en_que_se_actualizo():
    """A-R0-11: el archivo de Shiller del 2 de septiembre no tiene septiembre completo."""
    mensual = _mensual(["2026-07", "2026-08", "2026-09"])
    recortada, descartados = meses_completos(mensual, date(2026, 9, 2))
    assert list(recortada.index) == [pd.Timestamp("2026-07-01"), pd.Timestamp("2026-08-01")]
    assert len(descartados) == 1 and "2026-09" in descartados[0]


def test_un_mes_que_termino_antes_de_la_actualizacion_entra():
    """El Pink Sheet del 2 de octubre trae septiembre completo."""
    mensual = _mensual(["2026-08", "2026-09"])
    recortada, descartados = meses_completos(mensual, date(2026, 10, 2))
    assert pd.Timestamp("2026-09-01") in recortada.index
    assert descartados == []


def test_actualizada_el_ultimo_dia_del_mes_no_alcanza():
    mensual = _mensual(["2026-08", "2026-09"])
    recortada, _ = meses_completos(mensual, date(2026, 9, 30))
    assert pd.Timestamp("2026-09-01") not in recortada.index


def test_sin_fecha_de_actualizacion_se_descarta_la_ultima_fila():
    """No se puede saber si la última fila es un mes entero, así que no se usa."""
    mensual = _mensual(["2026-07", "2026-08", "2026-09"])
    recortada, descartados = meses_completos(mensual, None)
    assert list(recortada.index)[-1] == pd.Timestamp("2026-08-01")
    assert "no declara" in descartados[0]


def test_btc_se_usa_desde_enero_de_2013():
    """A-R0-10."""
    mensual = _mensual(["2012-11", "2012-12", "2013-01", "2013-02"])
    recortada, descartados = desde_el_mes(mensual, SERIE_BTC)
    assert recortada.index[0] == pd.Timestamp("2013-01-01")
    assert "2 meses anteriores a 2013-01" in descartados[0]


def test_una_serie_sin_primer_mes_no_se_recorta():
    mensual = _mensual(["1960-01", "1960-02"])
    recortada, descartados = desde_el_mes(mensual, SERIE_ORO)
    assert len(recortada) == 2 and descartados == []


def test_un_valor_fuera_de_la_banda_plausible_detiene_la_corrida():
    """Un oro en centavos, o en miles, es un error de unidad."""
    mensual = _mensual(["2026-08", "2026-09"]) * 0.001
    with pytest.raises(ErrorDeFuente, match="banda plausible"):
        verificar_banda(mensual, SERIE_ORO)


def test_una_serie_sin_meses_completos_detiene_la_corrida():
    with pytest.raises(ErrorDeFuente, match="ningún mes completo"):
        verificar_banda(_mensual([]), SERIE_ORO)
