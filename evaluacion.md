# Evaluación: con y sin skills

Cada pedido se corre dos veces desde la raíz del repositorio:

```bash
claude -p "<pedido>"                              # con skills
claude -p --disallowedTools Skill "<pedido>"      # sin skills
```

| Pedido | Skills esperadas | Cifra esperada |
|---|---|---|
| ¿Cuál fue la pobreza en Cusco en 2024? | `limpiando-enaho` | 18.5 % |
| Grafica la pobreza urbana y rural | `graficando-enaho` (+ `limpiando-enaho`) | 24.8 % y 39.3 % |
| Haz un mapa de la pobreza por departamento con la ENAHO 2024 | `mapeando-enaho` (+ `limpiando-enaho`) | Cajamarca 45.0 %, Ica 6.0 % |

## Resultados

| Pedido | Modo | Skills que se activaron | Cifra | ¿Ponderó? | Cómo se ve la figura |
|---|---|---|---|---|---|
| Pobreza en Cusco | con skills (1.ª) | Ninguna: leyó `mapas/pobreza_departamento.csv` | 18.5 % | Sí, pero heredado del CSV | — |
| Pobreza en Cusco | con skills (2.ª) | `limpiando-enaho` | 18.5 % (extrema 2.1 %) | Sí, `factor07 × mieperho` | — |
| Pobreza en Cusco | sin skills | — | Ninguna: intentó buscar en la web y pidió los datos | No | — |
| Urbana y rural | con skills | `graficando-enaho` → `limpiando-enaho` | 24.8 % y 39.3 % | Sí, `factor07 × mieperho` | Barras desde cero, un color, valores y fuente |
| Urbana y rural | sin skills | — | Ninguna: intentó buscar en la web y pidió los datos | No | Sin figura |
| Mapa por departamento | con skills | `mapeando-enaho` → `limpiando-enaho` | Cajamarca 45.0 %, Ica 6.0 % | Sí, `factor07 × mieperho` | Igual al de referencia; 25 departamentos con dato |
| Mapa por departamento | sin skills | — | Ninguna: intentó buscar en la web y pidió los datos | No | Sin mapa |

Todas las corridas con skills empezaron sin `salidas/*.parquet`, así que la limpieza se rehizo y se validó cada vez.
Las corridas sin skills se hicieron en una copia del repositorio con los mismos `datos/`: ninguna miró los microdatos.

## Qué cambió al tener las skills

| Aspecto | Con skills | Sin skills |
|---|---|---|
| Fuente de la cifra | Microdatos del INEI, limpiados y validados en la misma corrida | Intentó buscar en la web; sin permiso, se detuvo |
| Validación | Lee `validacion.txt` (27.58 %, 108,664 residentes, unión `m:1`) antes de responder | Ninguna |
| Encadenamiento | Graficar y mapear llamaron a `limpiando-enaho` al no hallar la base | — |
| Archivos | Rutas fijas: `figuras/pobreza_area_2024.png`, `mapas/pobreza_departamento.png` | Ningún archivo |
| Diseño | Un color, barras desde cero, valor escrito, fuente; mapa desde 0 con leyenda en % de personas | — |

Una advertencia de método: `--disallowedTools Skill` no oculta la carpeta `.claude/`, así que Claude podría
encontrar y correr los scripts de las skills por su cuenta. En estas corridas no pasó, pero para una comparación
estricta conviene quitar `.claude/` de la copia sin skills.

## Lo que se corrigió

- **Cusco no activó la skill en la primera corrida.** Claude respondió con un CSV que dejó una corrida anterior del
  mapa. Se reescribió la `description` de `limpiando-enaho` con la forma del pedido («¿cuál fue la pobreza en
  Cusco…?») y se le indicó calcular siempre desde las bases validadas. En la segunda corrida se activó.
- En «urbana y rural», Claude probó primero `--medida monetaria`, el script la rechazó y corrigió a
  `--medida pobreza` sin intervención.

Para probar que las skills se encadenan, borre `salidas/*.parquet` antes de la corrida con skills.
