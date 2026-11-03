# enaho-skills

Cuatro skills de Claude Code para trabajar la ENAHO 2024 del INEI siempre de la misma forma: descargarla,
limpiarla y validarla contra la pobreza oficial, graficarla y mapearla por departamento.

| Skill | Entra | Sale |
|---|---|---|
| `descargando-enaho` | El año (2024 = código 966 del INEI) | `datos/966-Modulo34.zip`, `datos/966-Modulo02.zip`, `datos/peru_departamental_simple.geojson` |
| `limpiando-enaho` | Los zip de los módulos 34 y 02 | `salidas/personas_2024.parquet`, `salidas/hogares_2024.parquet`, `salidas/validacion.txt` |
| `graficando-enaho` | La base limpia y un corte: área, sexo, edad, dominio o departamento | `figuras/*.png` |
| `mapeando-enaho` | La base limpia y el GeoJSON | `mapas/pobreza_departamento.png` y `.csv` |

Las skills se encadenan: si falta la base limpia, graficar y mapear llaman primero a `limpiando-enaho`, y si
faltan los zip, esta llama a `descargando-enaho`. Un solo pedido («haz un mapa de la pobreza») puede activar las
tres.

## Instalar

```bash
git clone <este repositorio> && cd enaho-skills
uv sync
```

Requiere [uv](https://docs.astral.sh/uv/) y Claude Code. Las skills están en `.claude/skills/` y se cargan solas al
abrir Claude Code en esta carpeta (compruébelo con `/skills`).

## Bajar los datos

Con Claude Code: «descarga la ENAHO 2024», o a mano:

```bash
uv run .claude/skills/descargando-enaho/scripts/descargar.py --anio 2024
```

Si el portal del INEI falla, bájelos en el navegador y póngalos en `datos/`:

- Módulo 34, sumaria: https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip
- Módulo 02, miembros: https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip
- Departamentos: https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson

`datos/` está en `.gitignore`: los microdatos no se suben.

## Correr todo

```bash
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por sexo
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por edad
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por departamento
uv run .claude/skills/mapeando-enaho/scripts/mapear.py
```

O, dentro de Claude Code: «¿cuál fue la pobreza en Cusco en 2024?», «grafica la pobreza urbana y rural»,
«haz un mapa de la pobreza por departamento».

## Validación

`salidas/validacion.txt` confirma que la base replica las cifras oficiales del INEI para 2024:

| Cifra | Oficial | Esta base |
|---|---|---|
| Pobreza monetaria | 27.6 % | 27.58 % (sumaria, `factor07 × mieperho`) · 27.53 % (personas, `facpob07`) |
| Pobreza extrema | 5.5 % | 5.50 % |
| Hogares | 33,691 | 33,691 |
| Residentes habituales | 108,664 | 108,664 |
| Urbana / rural | 24.8 % / 39.3 % | 24.8 % / 39.3 % |
| Cajamarca / Cusco / Ica | 45.0 % / 18.5 % / 6.0 % | 45.0 % / 18.5 % / 6.0 % |

### Una decisión de método

Las cifras por área y departamento se calculan sobre la sumaria ponderada con `factor07 × mieperho`, que es el
método oficial del INEI y reproduce exactamente sus cifras publicadas. Con la base de personas y `facpob07` los
departamentos difieren hasta 0.5 puntos (Huánuco 39.5 en vez de 39.0, Ica 5.9 en vez de 6.0). Sexo y edad solo
existen por persona, así que esos cortes usan `facpob07`. Por eso `limpiando-enaho` guarda dos bases.

## Evaluación

Los tres pedidos de prueba, con y sin skills, se anotan en [evaluacion.md](evaluacion.md).

## Estructura

```text
.claude/skills/
  descargando-enaho/  SKILL.md, scripts/descargar.py
  limpiando-enaho/    SKILL.md, reference.md, scripts/limpiar.py
  graficando-enaho/   SKILL.md, scripts/graficar.py
  mapeando-enaho/     SKILL.md, scripts/mapear.py
salidas/validacion.txt
figuras/  mapas/
evaluacion.md  README.md  pyproject.toml
```

Basado en la [sesión 16](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/16-skills-enaho) del curso
Data Science con Python de d2cml.
