"""Gráfico de barras de la pobreza de la ENAHO por área, sexo, edad, dominio o departamento."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

COLOR = "#C2410C"
TINTA, TINTA_SUAVE = "#1F1F1F", "#6B6B6B"
DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
DOMINIOS = {
    1: "Costa norte", 2: "Costa centro", 3: "Costa sur", 4: "Sierra norte",
    5: "Sierra centro", 6: "Sierra sur", 7: "Selva", 8: "Lima Metropolitana",
}
# Qué base y qué columna usa cada corte. Área, dominio y departamento siguen el método oficial del INEI
# (sumaria con factor07 × mieperho); sexo y edad solo existen por persona (facpob07).
CORTES = {
    "area": ("hogares", "area", "área de residencia", None),
    "dominio": ("hogares", "dominio", "dominio geográfico", DOMINIOS),
    "departamento": ("hogares", "departamento", "departamento", DEPARTAMENTOS),
    "sexo": ("personas", "sexo", "sexo", None),
    "edad": ("personas", "grupo_edad", "grupo de edad", None),
}
MEDIDAS = {"pobreza": ("pobre", "Pobreza monetaria"), "extrema": ("pobre_extremo", "Pobreza extrema")}
ORDEN_NATURAL = {"edad"}  # los grupos de edad se leen en su orden, no por valor


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--por", choices=CORTES, required=True)
    p.add_argument("--medida", choices=MEDIDAS, default="pobreza")
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--salidas", default="salidas")
    p.add_argument("--figuras", default="figuras")
    a = p.parse_args()

    base, columna, nombre_corte, etiquetas = CORTES[a.por]
    archivo = Path(a.salidas) / f"{base}_{a.anio}.parquet"
    if not archivo.exists():
        raise SystemExit(f"No existe {archivo}. Usa primero la skill limpiando-enaho.")
    df = pd.read_parquet(archivo)
    peso = "peso" if base == "hogares" else "facpob07"
    indicador, titulo_medida = MEDIDAS[a.medida]

    df["_num"] = df[indicador] * df[peso]
    tabla = df.groupby(columna, observed=True)[["_num", peso]].sum()
    serie = (tabla["_num"] / tabla[peso] * 100).astype(float).round(1).rename("pct")
    if etiquetas:
        serie.index = serie.index.map(etiquetas)
    serie = serie.sort_index() if a.por in ORDEN_NATURAL else serie.sort_values()
    if a.por in ORDEN_NATURAL:
        serie = serie.iloc[::-1]  # barras horizontales: el primer grupo arriba

    alto = max(2.6, 0.32 * len(serie) + 1.4)
    fig, ax = plt.subplots(figsize=(8, alto))
    barras = ax.barh(serie.index.astype(str), serie.values, color=COLOR, height=0.68)
    ax.bar_label(barras, labels=[f"{v:.1f} %" for v in serie.values], padding=4, color=TINTA, fontsize=9)

    ax.set_xlim(0, serie.max() * 1.15)
    ax.margins(y=0.02)
    ax.xaxis.set_visible(False)
    for lado in ("top", "right", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color(TINTA_SUAVE)
    ax.tick_params(axis="y", length=0, colors=TINTA, labelsize=9)
    ax.set_title(f"{titulo_medida} por {nombre_corte}, {a.anio} (% de personas)",
                 loc="left", color=TINTA, fontsize=12, pad=12)
    metodo = "factor07 × mieperho" if base == "hogares" else "facpob07"
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {a.anio}. Ponderado con {metodo}.",
             color=TINTA_SUAVE, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    figuras = Path(a.figuras)
    figuras.mkdir(exist_ok=True)
    salida = figuras / f"{a.medida}_{a.por}_{a.anio}.png"
    fig.savefig(salida, dpi=200)
    print(serie.iloc[::-1].to_string())
    print(f"\nguardado {salida}")


if __name__ == "__main__":
    main()
