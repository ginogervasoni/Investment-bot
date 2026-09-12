# Nodo Santa Fe

MVP de inteligencia territorial para explorar oportunidades inmobiliarias en Santa Fe Capital.

## Qué incluye

- Mapa interactivo basado en OpenStreetMap con límites vecinales oficiales de SCIT/IDESF.
- Cinco capas: potencial, rentabilidad, valorización, desarrollo y riesgo.
- Perfiles de inversión con ponderaciones diferentes.
- Filtro por puntaje mínimo.
- Ficha detallada y evolución de cada zona.
- Ranking dinámico y comparador de hasta tres zonas.
- Metodología y clasificación transparente de los datos.
- Diseño responsive para desktop, tablet y móvil.

## Estado de los datos

La base territorial ya utiliza la capa oficial `scit_vecinales` publicada por SCIT mediante el servicio WMS de IDESF. Los valores económicos continúan **simulados para demostración**. Antes de utilizar el producto para decisiones reales deben incorporarse los indicadores de IPEC, INDEC, BCRA y registros autorizados del mercado.

## Ejecución local

No requiere instalación. Servir la carpeta mediante cualquier servidor HTTP estático, por ejemplo:

```bash
python3 -m http.server 8080
```

Luego abrir `http://localhost:8080`.

## Próxima etapa

1. Incorporar Censo 2022 por radio censal.
2. Crear procesos de importación y validación para CSV/XLSX.
3. Conectar indicadores oficiales y registrar fecha, metodología y cobertura.
4. Agregar una base geográfica y panel administrativo.
5. Validar el modelo con operaciones históricas antes de publicar recomendaciones.
