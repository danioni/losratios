"""Gráfico de dos paneles para la señal de liquidez neta.

Estética deliberadamente sobria: fondo blanco, una sola tipografía, dos tonos
apagados y ningún adorno. El gráfico tiene que poder mostrarse en una reunión
sin que el color cuente una historia que los datos no cuentan.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

TINTA = "#2f3e4d"
TINTA_SUAVE = "#7a8899"
POSITIVO = "#4d6b82"
NEGATIVO = "#8f5d55"
GRILLA = "#dcdfe4"

ESTILO = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": TINTA_SUAVE,
    "axes.labelcolor": TINTA,
    "text.color": TINTA,
    "xtick.color": TINTA_SUAVE,
    "ytick.color": TINTA_SUAVE,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
}


def dibujar(
    tabla: pd.DataFrame,
    destino: Path,
    ventana_semanas: int,
    umbral: float | None,
    fuente: str,
) -> Path:
    """Escribe el PNG de dos paneles y devuelve la ruta."""
    datos = tabla.dropna(subset=["s2_1_liquidez_neta"])
    if datos.empty:
        raise ValueError("no hay datos de S2.1 para graficar")

    fechas = pd.to_datetime(datos["fecha"])
    variacion = datos["s2_2_var_13s_pct"]

    with plt.rc_context(ESTILO):
        figura, (arriba, abajo) = plt.subplots(
            2,
            1,
            figsize=(10, 6.5),
            sharex=True,
            gridspec_kw={"height_ratios": [2, 1], "hspace": 0.18},
        )

        arriba.plot(fechas, datos["s2_1_liquidez_neta"], color=TINTA, linewidth=1.3)
        arriba.set_ylabel("Miles de millones de USD")
        arriba.set_title(
            "S2.1  Liquidez neta de la Fed  ·  WALCL − WTREGEN − RRPONTSYD",
            loc="left",
            fontsize=11,
            pad=10,
        )
        arriba.yaxis.grid(True, color=GRILLA, linewidth=0.7)
        arriba.set_axisbelow(True)

        colores = [NEGATIVO if v < 0 else POSITIVO for v in variacion.fillna(0.0)]
        abajo.bar(fechas, variacion.fillna(0.0), width=5.0, color=colores, linewidth=0)
        abajo.axhline(0.0, color=TINTA, linewidth=0.8)
        abajo.set_ylabel("%")
        abajo.set_title(
            f"S2.2  Variación de S2.1 a {ventana_semanas} semanas",
            loc="left",
            fontsize=11,
            pad=8,
        )
        abajo.yaxis.grid(True, color=GRILLA, linewidth=0.7)
        abajo.set_axisbelow(True)

        localizador = mdates.AutoDateLocator(minticks=4, maxticks=9)
        abajo.xaxis.set_major_locator(localizador)
        abajo.xaxis.set_major_formatter(mdates.ConciseDateFormatter(localizador))

        texto_umbral = (
            "Umbral de expansión/contracción: NO MEDIDO (A-S2-3)"
            if umbral is None
            else f"Umbral de expansión/contracción: {umbral:.2f} %"
        )
        pie = (
            f"Fuente: {fuente}. Observación semanal de miércoles. "
            f"Último dato: {fechas.iloc[-1].date()}.\n"
            f"{texto_umbral}. La serie describe el contexto de liquidez; no es una predicción."
        )
        abajo.annotate(
            pie,
            xy=(0.0, -0.26),
            xycoords="axes fraction",
            fontsize=7.5,
            color=TINTA_SUAVE,
            va="top",
            ha="left",
        )

        destino.parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(destino, dpi=160, bbox_inches="tight")
        plt.close(figura)

    return destino
