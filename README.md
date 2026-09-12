# Nodo Santa Fe

MVP de inteligencia territorial para explorar oportunidades inmobiliarias en Santa Fe Capital.

## Qué incluye

- Mapa interactivo basado en OpenStreetMap con límites vecinales oficiales de SCIT/IDESF.
- 568 radios censales del gobierno local Santa Fe con indicadores del Censo 2022.
- Panel de construcción con costo del m² de Gran Santa Fe y permisos de Santa Fe Capital publicados por IPEC.
- Capa de precios de oferta y panel de mercado con datos autorizados de TuLugar para la ciudad y cuatro zonas compatibles.
- Capas coropléticas de población y porcentaje de hogares inquilinos.
- Cinco capas: potencial, rentabilidad, valorización, desarrollo y riesgo.
- Perfiles de inversión con ponderaciones diferentes.
- Filtro por puntaje mínimo.
- Ficha detallada y evolución de cada zona.
- Ranking dinámico y comparador de hasta tres zonas.
- Metodología y clasificación transparente de los datos.
- Diseño responsive para desktop, tablet y móvil.

## Estado de los datos

La base territorial utiliza la capa oficial `scit_vecinales` publicada por SCIT mediante IDESF. El Paso 2 incorpora datos estadísticos del Censo 2022 del INDEC por radio censal: 405.264 personas en viviendas particulares, 164.604 viviendas, 149.903 hogares y 35.149 hogares inquilinos dentro del gobierno local Santa Fe.

La extracción selecciona el código de gobierno local `820147`. El Paso 3 incorpora las series mensuales del IPEC hasta julio de 2026: costo de construcción para Gran Santa Fe y superficie autorizada para el municipio Santa Fe. Estas cifras se muestran como contexto de ciudad o aglomerado y no se distribuyen artificialmente entre vecinales.

El Paso 4 agrega datos abiertos de mercado de TuLugar. La fotografía de ciudad del 12 de septiembre de 2026 contiene 6.081 avisos activos y la serie barrial cerrada corresponde a agosto de 2026. Se vincularon únicamente Candioti Norte, Centro, Candioti Sur —como variante ortográfica de Candioti Sud— y Barranquitas. Los datos representan precios publicados, no precios de cierre.

La capa de precio de oferta y el panel de mercado son reales. Los valores históricos de rentabilidad, valorización, desarrollo, riesgo y el puntaje compuesto continúan **simulados para demostración** y no fueron modificados con esta incorporación.

## Ejecución local

No requiere instalación. Servir la carpeta mediante cualquier servidor HTTP estático, por ejemplo:

```bash
python3 -m http.server 8080
```

Luego abrir `http://localhost:8080`.

## Próxima etapa

1. Automatizar mensualmente la ejecución y validación de los cuatro conectores existentes.
2. Ampliar la cobertura territorial con equivalencias verificadas entre barrios y vecinales.
3. Obtener permisos georreferenciados para construir indicadores por vecinal.
4. Acumular historia suficiente y recalibrar el puntaje con indicadores reales y pruebas retrospectivas.
5. Agregar un panel administrativo y alertas de calidad.
