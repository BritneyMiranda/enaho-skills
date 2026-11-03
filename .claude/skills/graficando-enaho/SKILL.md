---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza monetaria o extrema de la ENAHO del INEI por área urbana y rural, sexo, grupo de edad, dominio o departamento, ponderados y con formato fijo, y los guarda como PNG en figuras/. Úsala cuando pidan graficar, comparar o visualizar la pobreza del Perú con la ENAHO.
argument-hint: [area|sexo|edad|dominio|departamento] [pobreza|extrema]
---
# Graficar la ENAHO

1. Si no existe `salidas/personas_2024.parquet` o `salidas/hogares_2024.parquet`, usa primero la skill
   `limpiando-enaho`.
2. Traduce el pedido a un corte: urbano/rural → `area`; hombres/mujeres → `sexo`; niños, jóvenes, adultos
   mayores → `edad`; costa/sierra/selva o Lima Metropolitana → `dominio`; regiones → `departamento`.
   Si piden pobreza extrema, usa `--medida extrema`.
3. Corre exactamente: `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por <corte> --medida <medida>`.
   Un corte por gráfico; si piden varios, corre el script una vez por corte.
4. Responde con las cifras que imprime el script (con un decimal) y la ruta del PNG. Mira el PNG antes de
   entregarlo.

## Reglas fijas (ya están en el script; no las cambies por pedido)

- Pondera siempre: área, dominio y departamento con `factor07 × mieperho` (método oficial del INEI);
  sexo y edad con `facpob07`, porque solo existen por persona.
- Barras horizontales que empiezan en cero, ordenadas de menor a mayor (la edad va en su orden natural).
- Un solo color y el valor escrito en cada barra; sin eje X ni cuadrícula.
- El título dice qué y cuándo: «Pobreza monetaria por sexo, 2024 (% de personas)».
- Nota al pie: «Fuente: INEI, ENAHO 2024» y el factor usado.
- PNG a 200 dpi en `figuras/<medida>_<corte>_<año>.png`.

Si piden algo que el script no cubre (otra variable, un cruce de dos variables), escribe un script nuevo en
`scripts/` del proyecto siguiendo estas mismas reglas, y lee antes `.claude/skills/limpiando-enaho/reference.md`.
