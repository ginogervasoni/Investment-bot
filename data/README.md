# Datos de Nodo Santa Fe

## Paso 1 — Base territorial

La aplicación consume en tiempo real la capa `scit_vecinales` del servicio WMS oficial de la Infraestructura de Datos Espaciales de Santa Fe. La capa es producida por el Servicio de Catastro e Información Territorial.

- Servicio: `https://aswe.santafe.gov.ar/idesf/wms`
- Estándar: OGC WMS 1.1.1
- Capa: `scit_vecinales`
- Sistemas compatibles: EPSG:4326 y EPSG:3857
- Fecha de verificación: 2026-09-12

## Paso 2 — Censo 2022

`censo-2022-santa-fe-radios.geojson` contiene 568 radios censales asociados al gobierno local Santa Fe (`820147`). Los conteos provienen de la base REDATAM del Censo 2022 del INDEC y se convierten a un GeoJSON compacto mediante `scripts/extract_censo_2022.py`.

- Población en viviendas particulares: 405.264
- Viviendas particulares: 164.604
- Viviendas con personas presentes: 147.723
- Hogares: 149.903
- Hogares inquilinos: 35.149 (23,4%)
- Fecha censal: 18 de mayo de 2022
- Fecha de extracción: 12 de septiembre de 2026

Las geometrías de radio provienen de la cartografía censal distribuida por CONICET; la conversión pública a Parquet es mantenida por `ciut-redatam` y Source Cooperative. El catálogo documenta estos intermediarios para conservar la trazabilidad.

El Censo no se actualiza mensualmente. En futuras etapas, la actualización mensual corresponderá a permisos, construcción, actividad, crédito, precios y alquileres. Los puntajes, precios y rentabilidades actuales permanecen simulados.
