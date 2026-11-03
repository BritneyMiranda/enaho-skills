"""Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO y arma una base de personas.

Pipeline fijo: leer, normalizar, filtrar residentes, unir, construir, validar, guardar.
"""

import argparse
import zipfile
from pathlib import Path

import pandas as pd

CODIGOS = {2024: 966}
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
# Cifras oficiales del INEI para comparar. Solo se valida contra ellas el año que esté aquí.
OFICIAL = {2024: {"pobreza": 27.6, "extrema": 5.5, "hogares": 33_691, "residentes": 108_664}}
TOLERANCIA = 0.1

COLS_SUMARIA = LLAVES_HOGAR + ["ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07"]
COLS_PERSONAS = LLAVES_PERSONA + ["anio", "p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]


def leer_dta(zip_: Path, nombre: str) -> pd.DataFrame:
    """Lee un .dta dentro del zip sin convertir etiquetas y con las llaves como texto."""
    with zipfile.ZipFile(zip_) as zf:
        ruta = [n for n in zf.namelist() if Path(n).name.lower() == nombre]
        if not ruta:
            raise SystemExit(f"{zip_} no contiene {nombre}")
        with zf.open(ruta[0]) as f:
            df = pd.read_stata(f, convert_categoricals=False)
    df.columns = [normalizar(c) for c in df.columns]
    for c in LLAVES_PERSONA + ["ubigeo"]:
        if c in df:
            df[c] = df[c].astype(str).str.strip()
    return df


def normalizar(columna: str) -> str:
    c = columna.strip().lower()
    # El año llega como «aÑo» o con la eñe rota.
    if len(c) == 3 and c[0] == "a" and c[2] == "o" and not c.isascii():
        return "anio"
    return c


def ponderado(x: pd.Series, w: pd.Series) -> float:
    return float((x * w).sum() / w.sum() * 100)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--codigo", type=int)
    p.add_argument("--datos", default="datos")
    p.add_argument("--salidas", default="salidas")
    a = p.parse_args()

    codigo = a.codigo or CODIGOS.get(a.anio)
    if codigo is None:
        raise SystemExit(f"No conozco el código del INEI para {a.anio}. Corre de nuevo con --codigo.")
    datos, salidas = Path(a.datos), Path(a.salidas)
    zips = {m: datos / f"{codigo}-Modulo{m}.zip" for m in ("34", "02")}
    faltan = [str(z) for z in zips.values() if not z.exists()]
    if faltan:
        raise SystemExit(f"Faltan {', '.join(faltan)}. Usa primero la skill descargando-enaho.")

    # 1-2. Leer y normalizar
    sumaria = leer_dta(zips["34"], f"sumaria-{a.anio}.dta")[COLS_SUMARIA]
    miembros = leer_dta(zips["02"], f"enaho01-{a.anio}-200.dta")[COLS_PERSONAS]

    # 3. Filtrar residentes habituales (definición del INEI)
    residente = ((miembros.p204 == 1) & (miembros.p205 == 2)) | ((miembros.p204 == 2) & (miembros.p206 == 1))
    personas = miembros[residente].copy()

    # 4. Unir personas con su hogar
    base = personas.merge(sumaria, on=LLAVES_HOGAR, how="left", validate="m:1", indicator=True)

    # 5. Construir
    base["departamento"] = base.ubigeo.str[:2]
    base["urbano"] = base.estrato <= 5
    base["area"] = base.urbano.map({True: "Urbana", False: "Rural"})
    base["pobre"] = base.pobreza <= 2
    base["pobre_extremo"] = base.pobreza == 1
    base["sexo"] = base.p207.map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base.p208a
    base["grupo_edad"] = pd.cut(
        base.edad, [-1, 13, 17, 29, 44, 59, 200],
        labels=["0-13", "14-17", "18-29", "30-44", "45-59", "60 y más"],
    ).astype(str)

    # 6. Validar
    pob_hogar = ponderado(sumaria.pobreza <= 2, sumaria.factor07 * sumaria.mieperho)
    ext_hogar = ponderado(sumaria.pobreza == 1, sumaria.factor07 * sumaria.mieperho)
    pob_pers = ponderado(base.pobre, base.facpob07)
    chequeos = [
        ("llaves de hogar únicas en la sumaria", not sumaria.duplicated(LLAVES_HOGAR).any()),
        ("llaves de persona únicas en miembros", not miembros.duplicated(LLAVES_PERSONA).any()),
        ("la unión no perdió ni duplicó filas", len(base) == len(personas)),
        ("toda persona encontró su hogar", (base._merge == "both").all()),
        ("25 departamentos", base.departamento.nunique() == 25),
        ("ninguna persona sin pobreza ni factor", base[["pobreza", "facpob07"]].notna().all().all()),
    ]
    oficial = OFICIAL.get(a.anio)
    if oficial:
        chequeos += [
            (f"hogares = {oficial['hogares']:,}", len(sumaria) == oficial["hogares"]),
            (f"residentes habituales = {oficial['residentes']:,}", len(personas) == oficial["residentes"]),
            (f"pobreza (sumaria) a {TOLERANCIA} pts de {oficial['pobreza']} %", abs(pob_hogar - oficial["pobreza"]) < TOLERANCIA),
            (f"pobreza (personas) a {TOLERANCIA} pts de {oficial['pobreza']} %", abs(pob_pers - oficial["pobreza"]) < TOLERANCIA),
            (f"pobreza extrema a {TOLERANCIA} pts de {oficial['extrema']} %", abs(ext_hogar - oficial["extrema"]) < TOLERANCIA),
        ]

    lineas = [
        f"ENAHO {a.anio} (código INEI {codigo})",
        f"hogares en la sumaria:          {len(sumaria):,}",
        f"filas del módulo 02:            {len(miembros):,}",
        f"residentes habituales:          {len(personas):,}",
        f"pobreza, sumaria factor07×mieperho: {pob_hogar:.2f} %",
        f"pobreza, personas facpob07:     {pob_pers:.2f} %",
        f"pobreza extrema (sumaria):      {ext_hogar:.2f} %",
        f"población expandida:            {base.facpob07.sum() / 1e6:.2f} millones",
        "" if oficial else f"AVISO: no hay cifras oficiales cargadas para {a.anio}; compara a mano con el INEI.",
        "",
    ] + [f"[{'OK' if ok else 'FALLA'}] {texto}" for texto, ok in chequeos]
    todo_ok = all(ok for _, ok in chequeos)
    lineas += ["", "RESULTADO: VALIDADA" if todo_ok else "RESULTADO: NO VALIDADA, no uses esta base"]

    # 7. Guardar
    salidas.mkdir(exist_ok=True)
    (salidas / "validacion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    if not todo_ok:
        raise SystemExit(1)
    columnas = LLAVES_PERSONA + [
        "anio", "ubigeo", "departamento", "dominio", "estrato", "urbano", "area",
        "p203", "sexo", "edad", "grupo_edad", "pobreza", "pobre", "pobre_extremo",
        "mieperho", "factor07", "facpob07",
    ]
    base[columnas].to_parquet(salidas / f"personas_{a.anio}.parquet", index=False)

    # Base de hogares: el método oficial del INEI para pobreza por área o departamento.
    hogares = sumaria.assign(
        anio=a.anio,
        departamento=sumaria.ubigeo.str[:2],
        urbano=sumaria.estrato <= 5,
        area=(sumaria.estrato <= 5).map({True: "Urbana", False: "Rural"}),
        pobre=sumaria.pobreza <= 2,
        pobre_extremo=sumaria.pobreza == 1,
        peso=sumaria.factor07 * sumaria.mieperho,
    )
    hogares.to_parquet(salidas / f"hogares_{a.anio}.parquet", index=False)
    print(f"\nguardado {salidas / f'personas_{a.anio}.parquet'}")
    print(f"guardado {salidas / f'hogares_{a.anio}.parquet'}")


if __name__ == "__main__":
    main()
