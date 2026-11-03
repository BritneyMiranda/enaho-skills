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
| Pobreza en Cusco | con skills | | | | — |
| Pobreza en Cusco | sin skills | — | | | — |
| Urbana y rural | con skills | | | | |
| Urbana y rural | sin skills | — | | | |
| Mapa por departamento | con skills | `mapeando-enaho` → `limpiando-enaho` (sin base limpia previa) | Cajamarca 45.0 %, Ica 6.0 % | Sí, `factor07 × mieperho` | Igual al de referencia; 25 departamentos con dato |
| Mapa por departamento | sin skills | — | | | |

Para probar que las skills se encadenan, borre `salidas/*.parquet` antes de la corrida con skills.
