---
name: mapeando-enaho
description: Hace un mapa coroplético del Perú con la pobreza monetaria o extrema de la ENAHO del INEI por departamento (región), uniendo por código de ubigeo con los límites de los 25 departamentos, y lo guarda como PNG en mapas/. Úsala cuando pidan un mapa, mapear o ver en el territorio la pobreza por departamento o región.
argument-hint: [pobreza|extrema] [año]
---
# Mapear la ENAHO

1. Si no existe `salidas/hogares_<año>.parquet` (2024 si no piden otro), usa primero la skill `limpiando-enaho`.
   Si no existe `datos/peru_departamental_simple.geojson`, usa primero la skill `descargando-enaho`.
2. Corre exactamente: `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --medida <medida> --anio <año>`
   (por defecto `pobreza` y 2024).
3. Si el script se detiene porque la unión falló o no replica la referencia 2024, no lo «arregles» uniendo por
   nombre ni dibujando por otro camino: revisa que los códigos sean texto de dos dígitos y que la base esté
   validada.
4. Mira el PNG antes de entregarlo. Responde con la ruta del mapa, el departamento con mayor y menor pobreza
   y sus cifras (2024: Cajamarca 45.0 %, Ica 6.0 %). La tabla queda en `mapas/<medida>_departamento.csv`.

## Reglas fijas (ya están en el script; no las cambies por pedido)

- Une por código: `ubigeo[:2]` de la ENAHO con `FIRST_IDDP` del GeoJSON, ambos como texto.
- Nunca por nombre: «APURIMAC» del GeoJSON no es «Apurímac».
- Exige 25 departamentos y ninguno sin dato; si no, se detiene.
- En 2024 comprueba los 25 departamentos contra la referencia de la clase, a un decimal.
- Lima (15) y Callao (07) van separados.
- Pondera con `factor07 × mieperho` sobre la sumaria, el método oficial del INEI.
- Un solo tono de claro a oscuro (`Oranges`) que empieza en 0; nunca arcoíris.
- Leyenda con la unidad: % de personas. Título con qué y cuándo. Fuente al pie.
- PNG a 200 dpi en `mapas/`.
