---
name: descargando-enaho
description: Descarga del portal de microdatos del INEI los módulos 34 (sumaria) y 02 (miembros del hogar) de la ENAHO en formato STATA, y el GeoJSON de los 25 departamentos del Perú, a la carpeta datos/. Úsala cuando pidan descargar, bajar u obtener la ENAHO, sus microdatos o el mapa de departamentos, o cuando otra skill de la ENAHO no encuentre los archivos en datos/.
argument-hint: [año]
---
# Descargar la ENAHO

1. Corre exactamente: `uv run ${CLAUDE_SKILL_DIR}/scripts/descargar.py --anio $0` (si no hay año, usa 2024).
2. El script baja tres archivos a `datos/` y no vuelve a bajar los que ya existen:
   - `966-Modulo34.zip`: sumaria, una fila por hogar.
   - `966-Modulo02.zip`: miembros, una fila por persona.
   - `peru_departamental_simple.geojson`: límites de los 25 departamentos.
3. Lee lo que imprime. Si un zip no es un zip válido o pesa menos de 1 MB, el portal del INEI falló o está caído:
   detente y pide al usuario bajarlo desde el navegador con el enlace que imprime el script. No intentes otras URL.
4. `966` es el código de la ENAHO 2024. Para otro año, pide al usuario el código del portal
   (https://proyectos.inei.gob.pe/microdatos/) y corre con `--codigo <código>`. No adivines códigos.
5. Comprueba que `datos/` esté en `.gitignore`: los microdatos no se suben al repositorio.
6. Responde con la lista de archivos y su tamaño. No los descomprimas: `limpiando-enaho` lee los zip directamente.
