"""Mapa coroplético de la pobreza de la ENAHO por departamento, unido por código."""

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

TINTA, TINTA_SUAVE, FONDO = "#1F1F1F", "#6B6B6B", "#FFFFFF"
MEDIDAS = {"pobreza": ("pobre", "Pobreza monetaria"), "extrema": ("pobre_extremo", "Pobreza extrema")}
# Pobreza monetaria 2024 por departamento (referencias/pobreza_departamento_2024.csv de la sesión 16).
REFERENCIA_2024 = {
    "01": 25.7, "02": 22.8, "03": 24.0, "04": 15.8, "05": 32.8, "06": 45.0, "07": 33.9, "08": 18.5, "09": 33.4,
    "10": 39.0, "11": 6.0, "12": 18.5, "13": 30.2, "14": 14.0, "15": 27.1, "16": 43.0, "17": 11.1, "18": 11.0,
    "19": 39.0, "20": 31.9, "21": 39.9, "22": 22.0, "23": 24.0, "24": 26.9, "25": 27.1,
}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--medida", choices=MEDIDAS, default="pobreza")
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--salidas", default="salidas")
    p.add_argument("--geojson", default="datos/peru_departamental_simple.geojson")
    p.add_argument("--mapas", default="mapas")
    a = p.parse_args()

    archivo = Path(a.salidas) / f"hogares_{a.anio}.parquet"
    if not archivo.exists():
        raise SystemExit(f"No existe {archivo}. Usa primero la skill limpiando-enaho.")
    if not Path(a.geojson).exists():
        raise SystemExit(f"No existe {a.geojson}. Usa primero la skill descargando-enaho.")
    indicador, titulo = MEDIDAS[a.medida]

    # Pobreza por departamento con el método oficial del INEI: sumaria ponderada con factor07 × mieperho.
    h = pd.read_parquet(archivo)
    h["_num"] = h[indicador] * h["peso"]
    t = h.groupby("departamento")[["_num", "peso"]].sum()
    tabla = (t["_num"] / t["peso"] * 100).astype(float).round(1).rename("pct").reset_index()

    # Unir por código como texto de dos dígitos, nunca por nombre.
    geo = gpd.read_file(a.geojson)
    geo["FIRST_IDDP"] = geo["FIRST_IDDP"].astype(str).str.zfill(2)
    mapa = geo.merge(tabla, left_on="FIRST_IDDP", right_on="departamento", how="left", validate="1:1")

    sin_dato = mapa.loc[mapa.pct.isna(), "NOMBDEP"].tolist()
    sobran = sorted(set(tabla.departamento) - set(geo.FIRST_IDDP))
    if len(mapa) != 25 or sin_dato or sobran:
        raise SystemExit(f"La unión falló: {len(mapa)} polígonos, sin dato {sin_dato}, códigos sin polígono {sobran}")
    for codigo in ("07", "15"):  # Callao y Lima van separados
        if codigo not in set(mapa.FIRST_IDDP):
            raise SystemExit(f"Falta el departamento {codigo} en el GeoJSON")
    if a.anio == 2024 and a.medida == "pobreza":
        distintos = {c: (v, REFERENCIA_2024[c]) for c, v in zip(tabla.departamento, tabla.pct) if v != REFERENCIA_2024[c]}
        if distintos:
            raise SystemExit(f"No replica la referencia 2024 (calculado, referencia): {distintos}")

    fig, ax = plt.subplots(figsize=(7.5, 9.5), facecolor=FONDO)
    mapa.plot(
        column="pct", ax=ax, cmap="Oranges", vmin=0, vmax=mapa.pct.max(),
        edgecolor="white", linewidth=0.6, legend=True,
        legend_kwds={"label": f"{titulo} (% de personas)", "shrink": 0.5},
    )
    ax.set_axis_off()
    ax.set_title(f"{titulo} por departamento, {a.anio}", color=TINTA, fontsize=14)
    fig.text(0.02, 0.02, f"Fuente: INEI, ENAHO {a.anio} (sumaria), ponderado con factor07 × mieperho",
             color=TINTA_SUAVE, fontsize=8)

    carpeta = Path(a.mapas)
    carpeta.mkdir(exist_ok=True)
    nombre = "pobreza_departamento.png" if a.medida == "pobreza" else f"{a.medida}_departamento.png"
    fig.savefig(carpeta / nombre, dpi=200, bbox_inches="tight", facecolor=FONDO)
    tabla.merge(geo[["FIRST_IDDP", "NOMBDEP"]], left_on="departamento", right_on="FIRST_IDDP")[
        ["departamento", "NOMBDEP", "pct"]
    ].to_csv(carpeta / nombre.replace(".png", ".csv"), index=False)

    print(mapa.sort_values("pct", ascending=False)[["FIRST_IDDP", "NOMBDEP", "pct"]].to_string(index=False))
    comprobado = " Los 25 coinciden con la referencia 2024." if a.anio == 2024 and a.medida == "pobreza" else ""
    print(f"\n25 departamentos con dato.{comprobado} guardado {carpeta / nombre}")


if __name__ == "__main__":
    main()
