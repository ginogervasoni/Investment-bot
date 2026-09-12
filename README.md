# Nodo Santa Fe

MVP de inteligencia territorial para explorar oportunidades inmobiliarias en Santa Fe Capital.

## Qué incluye

- Mapa interactivo basado en OpenStreetMap con límites vecinales oficiales de SCIT/IDESF.
- 568 radios censales del gobierno local Santa Fe con indicadores del Censo 2022.
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

La extracción selecciona el código de gobierno local `820147`. Los valores económicos de precio, renta, valorización, desarrollo y puntaje continúan **simulados para demostración**.

## Ejecución local

No requiere instalación. Servir la carpeta mediante cualquier servidor HTTP estático, por ejemplo:

```bash
python3 -m http.server 8080
```

Luego abrir `http://localhost:8080`.

## Próxima etapa

1. Crear procesos mensuales de importación y validación para CSV/XLSX.
2. Conectar permisos de edificación, actividad y costo de construcción de IPEC/Municipalidad.
3. Incorporar precios y alquileres desde una fuente de mercado autorizada.
4. Recalibrar el puntaje con indicadores reales y pruebas históricas.
5. Agregar un panel administrativo y alertas de calidad.
