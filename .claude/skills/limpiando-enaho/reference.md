# Referencia de la ENAHO 2024

## Archivos

| Módulo | Archivo en el zip | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|---|
| 34 · Sumaria | `sumaria-2024.dta` | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` |
| 02 · Miembros | `enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` |

El zip 34 también trae `sumaria-2024-12g.dta` (gasto en 12 grupos): no es la sumaria que se usa. El zip 02 trae
tablas de ocupaciones (`enaho_tabla_ciuo_88.dta`, `enaho_tabla_cno_2015.dta`) que tampoco se usan. Cada zip trae
el diccionario en PDF.

## Variables de las bases limpias

| Variable | Base | Qué es |
|---|---|---|
| `conglome`, `vivienda`, `hogar`, `codperso` | ambas | Llaves, texto con ceros a la izquierda |
| `ubigeo` | ambas | Departamento, provincia y distrito, texto de 6 dígitos |
| `departamento` | ambas | `ubigeo[:2]`, texto de 2 dígitos |
| `dominio` | ambas | 1–3 costa, 4–6 sierra, 7 selva, 8 Lima Metropolitana |
| `estrato` | ambas | 1–5 urbano, 6–8 rural |
| `urbano`, `area` | ambas | `estrato <= 5`; «Urbana» / «Rural» |
| `pobreza` | ambas | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
| `pobre`, `pobre_extremo` | ambas | `pobreza <= 2`, `pobreza == 1` |
| `mieperho` | ambas | Miembros del hogar (sin trabajadores del hogar ni pensionistas) |
| `factor07` | ambas | Factor de expansión del hogar |
| `peso` | hogares | `factor07 × mieperho`, para pobreza de personas desde la sumaria |
| `facpob07` | personas | Factor de expansión de la persona |
| `p203` | personas | Parentesco: 1 jefe, 2 cónyuge, 3 hijo, … |
| `sexo` | personas | De `p207`: 1 Hombre, 2 Mujer |
| `edad`, `grupo_edad` | personas | `p208a` en años; 0-13, 14-17, 18-29, 30-44, 45-59, 60 y más |

Residente habitual (filtro del INEI, ya aplicado): `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)`.
Es decir, miembros que no estuvieron ausentes 30 días o más, y no miembros presentes 30 días o más.

## Cifras oficiales 2024

| Cifra | Valor |
|---|---|
| Pobreza monetaria | 27.6 % (sumaria: 27.58 %; personas con `facpob07`: 27.53 %) |
| Pobreza extrema | 5.5 % |
| Urbana / rural | 24.8 % / 39.3 % |
| Lima Metropolitana (`dominio == 8`) | 28.2 % |
| Residentes habituales | 108,664 |

## Departamentos (`departamento`)

| Código | Departamento | Código | Departamento | Código | Departamento |
|---|---|---|---|---|---|
| 01 | Amazonas | 10 | Huánuco | 19 | Pasco |
| 02 | Áncash | 11 | Ica | 20 | Piura |
| 03 | Apurímac | 12 | Junín | 21 | Puno |
| 04 | Arequipa | 13 | La Libertad | 22 | San Martín |
| 05 | Ayacucho | 14 | Lambayeque | 23 | Tacna |
| 06 | Cajamarca | 15 | Lima | 24 | Tumbes |
| 07 | Callao | 16 | Loreto | 25 | Ucayali |
| 08 | Cusco | 17 | Madre de Dios | | |
| 09 | Huancavelica | 18 | Moquegua | | |

Lima (15) incluye Lima Metropolitana y Lima Provincias. Callao (07) va aparte.

## Seis trampas

1. Ceros a la izquierda: `conglome` «015009», `ubigeo` «010101». Como número pierden el cero y la unión falla.
2. La columna del año llega como «aÑo» o con la eñe rota: el script la renombra `anio`.
3. No todos son residentes: 117,721 filas en el módulo 02, 108,664 residentes habituales.
4. Sin `validate="m:1"` un hogar repetido multiplica personas sin avisar.
5. Sin factor de expansión, 33,691 hogares no dicen nada de 34 millones de personas.
6. `pobreza` es un código: pobre es `pobreza <= 2`, nunca un promedio.
