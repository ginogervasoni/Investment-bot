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

El Censo no se actualiza mensualmente.

## Paso 3 — Construcción y permisos

`construction-series.json` resume los últimos 13 meses disponibles de dos planillas oficiales del IPEC:

- costo total y por capítulos del metro cuadrado para el aglomerado Gran Santa Fe;
- superficie autorizada por permisos de edificación para el municipio Santa Fe.

El corte incorporado es julio de 2026 y los últimos meses son provisorios. La actualización se reproduce con `scripts/extract_ipec_construction.py`, que descarga las planillas, valida las filas de Santa Fe y recalcula variaciones acumuladas.

La escala territorial es ciudad o aglomerado. IPEC no publica estas cifras por vecinal, de modo que la aplicación las muestra como contexto y no modifica con ellas los colores ni puntajes zonales. En esta etapa, los indicadores zonales existentes todavía permanecían simulados.

## Paso 4 — Mercado inmobiliario autorizado

`market-santa-fe.json` contiene métricas agregadas obtenidas de los CSV abiertos de TuLugar. La fuente permite reutilización comercial con atribución; por eso la interfaz identifica a TuLugar y este repositorio no redistribuye los archivos completos como un catálogo alternativo.

La fotografía de Santa Fe del 12 de septiembre de 2026 registra 6.081 avisos activos: 5.307 de venta y 774 de alquiler. La serie mensual barrial incorporada corresponde a agosto de 2026. Solo se enlazan coincidencias verificables:

- Candioti Norte;
- Centro;
- Candioti Sur, documentado como variante ortográfica de Candioti Sud;
- Barranquitas.

Las otras seis zonas de demostración quedan explícitamente sin dato; no se estiman ni se completan artificialmente. `scripts/extract_tulugar_market.py` descarga la fotografía de ciudad y las series mensuales de esos barrios, valida sus campos y genera únicamente el resumen agregado que utiliza la aplicación.

Los importes son precios de oferta publicados, no precios de cierre de operaciones. Como la serie argentina comienza en 2026, esta etapa no calcula valorización anual ni altera todavía el puntaje compuesto, la rentabilidad o el riesgo simulados.
