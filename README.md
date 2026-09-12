# Nodo Santa Fe

MVP de inteligencia territorial para explorar oportunidades inmobiliarias en Santa Fe Capital.

## Qué incluye

- Mapa interactivo basado en OpenStreetMap.
- Cinco capas: potencial, rentabilidad, valorización, desarrollo y riesgo.
- Perfiles de inversión con ponderaciones diferentes.
- Filtro por puntaje mínimo.
- Ficha detallada y evolución de cada zona.
- Ranking dinámico y comparador de hasta tres zonas.
- Metodología y clasificación transparente de los datos.
- Diseño responsive para desktop, tablet y móvil.

## Estado de los datos

Los valores actuales son **simulados para demostración**. Los puntos representan áreas aproximadas de análisis y no límites oficiales de barrios. Antes de utilizar el producto para decisiones reales deben incorporarse geometrías verificadas y conectores para IPEC, INDEC, Municipalidad de Santa Fe, SCIT, BCRA y registros autorizados del mercado.

## Ejecución local

No requiere instalación. Servir la carpeta mediante cualquier servidor HTTP estático, por ejemplo:

```bash
python3 -m http.server 8080
```

Luego abrir `http://localhost:8080`.

## Próxima etapa

1. Incorporar GeoJSON oficial de barrios y radios censales.
2. Crear procesos de importación y validación para CSV/XLSX.
3. Conectar fuentes oficiales y registrar fecha, metodología y cobertura.
4. Agregar una base PostgreSQL/PostGIS y panel administrativo.
5. Validar el modelo con operaciones históricas antes de publicar recomendaciones.
