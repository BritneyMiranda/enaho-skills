"""Descarga los módulos 34 y 02 de la ENAHO (STATA) y el GeoJSON departamental a datos/."""

import argparse
import urllib.request
import zipfile
from pathlib import Path

# Código del portal de microdatos del INEI por año, verificado con el nombre de la sumaria dentro de cada zip.
CODIGOS = {
    2015: 498, 2016: 546, 2017: 603, 2018: 634, 2019: 687,
    2020: 737, 2021: 759, 2022: 784, 2023: 906, 2024: 966,
}
URL_INEI = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo}-Modulo{modulo}.zip"
URL_GEOJSON = (
    "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
    "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson"
)
MODULOS = ["34", "02"]


def bajar(url: str, destino: Path) -> None:
    if destino.exists() and destino.stat().st_size > 0:
        print(f"ya existe   {destino} ({destino.stat().st_size / 1e6:.1f} MB)")
        return
    print(f"bajando     {url}")
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    temporal = destino.with_suffix(destino.suffix + ".part")
    with urllib.request.urlopen(pedido, timeout=300) as r, open(temporal, "wb") as f:
        while bloque := r.read(1 << 20):
            f.write(bloque)
    temporal.replace(destino)
    print(f"guardado    {destino} ({destino.stat().st_size / 1e6:.1f} MB)")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--codigo", type=int, help="código del portal del INEI si el año no está en CODIGOS")
    p.add_argument("--datos", default="datos")
    a = p.parse_args()

    codigo = a.codigo or CODIGOS.get(a.anio)
    if codigo is None:
        raise SystemExit(f"No conozco el código del INEI para {a.anio}. Corre de nuevo con --codigo.")

    datos = Path(a.datos)
    datos.mkdir(exist_ok=True)

    for modulo in MODULOS:
        url = URL_INEI.format(codigo=codigo, modulo=modulo)
        zip_ = datos / f"{codigo}-Modulo{modulo}.zip"
        try:
            bajar(url, zip_)
        except OSError as e:
            raise SystemExit(f"Falló la descarga ({e}). Bájalo en el navegador: {url}")
        if zip_.stat().st_size < 1e6 or not zipfile.is_zipfile(zip_):
            zip_.unlink()
            raise SystemExit(f"{zip_.name} no es un zip válido. Bájalo en el navegador: {url}")
        dtas = [n for n in zipfile.ZipFile(zip_).namelist() if n.lower().endswith(".dta")]
        print(f"            contiene {', '.join(Path(n).name for n in dtas)}")

    bajar(URL_GEOJSON, datos / "peru_departamental_simple.geojson")
    print("listo")


if __name__ == "__main__":
    main()
