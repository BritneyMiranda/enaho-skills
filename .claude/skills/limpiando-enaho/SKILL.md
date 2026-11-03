---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI, valida contra la pobreza oficial y arma bases de personas y hogares con pobreza y factor de expansión. Úsala siempre que pregunten una cifra de pobreza del Perú (¿cuál fue la pobreza en Cusco, Puno, Lima, en el país, en 2024?), o pidan limpiar, unir o analizar la ENAHO, aunque ya exista una tabla en mapas/ o figuras/.
argument-hint: [año]
---
# Limpiar la ENAHO

1. Corre exactamente: `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio $0` (si no hay año, usa 2024;
   hay datos de 2015 a 2024). Si dice que faltan los zip, usa primero la skill `descargando-enaho` con ese año.
   No reescribas el pipeline ni lo cambies para que pase la validación.
2. Lee `salidas/validacion.txt`. Si dice `NO VALIDADA` o la pobreza difiere del INEI en más de 0.1 puntos,
   detente y muestra al usuario qué chequeo falló. Cada año se valida contra su pobreza oficial; 2024 además
   contra hogares, residentes y pobreza extrema.
3. Las cifras de referencia de abajo y de `reference.md` son de 2024.
4. Bases que deja el script:
   - `salidas/personas_$0.parquet`: una fila por residente habitual. Pondera con `facpob07`.
     Úsala para sexo, edad o parentesco.
   - `salidas/hogares_$0.parquet`: una fila por hogar. Pondera con `peso` (= `factor07 × mieperho`).
     Es el método oficial del INEI: úsala para la pobreza nacional, por área o por departamento.
5. Toda cifra va ponderada. Nunca promedies el código `pobreza`: pobre es `pobreza <= 2`.
6. Antes de usar una variable que no está en la base, lee [reference.md](reference.md).

## Para responder una cifra

Calcúlala siempre desde las bases validadas, no desde CSV o figuras que ya existan en el proyecto: pueden ser de
otra corrida o de otra medida.

```python
import pandas as pd
h = pd.read_parquet("salidas/hogares_2024.parquet")
cusco = h[h.departamento == "08"]
print(round((cusco.pobre * cusco.peso).sum() / cusco.peso.sum() * 100, 1))  # 18.5
```

Departamentos por código de dos dígitos (`ubigeo[:2]`), nunca por nombre. La tabla de códigos está en
[reference.md](reference.md).
