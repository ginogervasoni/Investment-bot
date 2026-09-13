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

## Paso 5 — Actualización y control de calidad

`.github/workflows/update-market-data.yml` ejecuta el conector el primer día de cada mes a las 08:17 en `America/Argentina/Cordoba` y también permite una ejecución manual. El proceso:

1. conserva el archivo anterior para comparar períodos;
2. ejecuta `scripts/extract_tulugar_market.py`;
3. valida el resultado con `scripts/validate_market_data.py`;
4. comprueba que no retrocedan las fechas ni cambien las zonas autorizadas;
5. crea un commit únicamente si el contenido real cambió.

La validación exige que venta más alquiler coincidan con el total de avisos, que los precios sean positivos, que la atribución y los enlaces sean válidos y que las cuatro coincidencias territoriales permanezcan separadas de las seis zonas sin asignación. El sitio intenta leer la versión vigente de GitHub y conserva `data/market-santa-fe.json` como respaldo operativo.

## Paso 6 — Crédito e ingresos

`affordability-santa-fe.json` agrega dos fuentes oficiales que permiten medir accesibilidad sin alterar el puntaje de inversión:

- microdatos de hogares de la EPH del INDEC para el aglomerado Gran Santa Fe (`AGLOMERADO=10`);
- préstamos hipotecarios UVA, valor de la UVA y tipo de cambio minorista vendedor publicados por el BCRA.

Para el primer trimestre de 2026, la mediana ponderada del ingreso total familiar positivo fue de $1.400.000 mensuales. El cálculo utiliza `ITF` y `PONDIH` para 608 hogares relevados, representativos de 349.646 hogares mediante el ponderador. Se informa como una estimación propia sobre microdatos oficiales y no como un cuadro publicado directamente por INDEC.

En agosto de 2026, los hipotecarios UVA otorgados registraron una tasa nominal anual promedio de UVA + 6,91%, un plazo promedio de 8.499 días (23,3 años) y $362.624,8 millones otorgados a escala nacional. El valor UVA incorporado es $2.114,62 al 11 de septiembre y el tipo de cambio minorista vendedor B 9791 es $1.533,53 por USD al 9 de septiembre de 2026.

El simulador combina estas referencias con el precio de oferta de departamentos de TuLugar. Muestra precio estimado, anticipo, meses de ingreso mediano necesarios para ese anticipo y relación precio/ingreso anual. No estima cuota, aprobación crediticia, impuestos, gastos ni precio final de escritura. Los períodos no son concurrentes, de modo que el resultado es orientativo y permanece fuera de los colores y rankings del mapa.

La extracción se reproduce con:

```bash
python scripts/extract_affordability.py
```

El script detecta y descarga los cinco trimestres EPH más recientes, procesa la planilla mensual de préstamos UVA y consulta las variables 4 y 31 de la API v4 del BCRA para obtener dólar minorista vendedor y UVA.

## Paso 7 — Automatización de fuentes oficiales

El flujo `.github/workflows/update-market-data.yml` actualiza mensualmente los cuatro bloques de información: mercado, construcción, ingresos y finanzas. Sus controles principales son:

1. cada conector se ejecuta y valida de manera independiente;
2. IPEC descubre las planillas más recientes desde las páginas oficiales y conserva enlaces conocidos como respaldo;
3. INDEC detecta automáticamente el último trimestre EPH disponible;
4. BCRA se consulta mediante su API oficial v4 y su planilla mensual de hipotecarios UVA;
5. ninguna serie puede retroceder de período ni publicar valores fuera de rango;
6. un conector fallido restaura su último archivo válido;
7. `pipeline-status.json` informa el resultado de cada fuente y la fecha del último control;
8. el flujo termina con alerta cuando alguna fuente queda degradada, incluso después de proteger los datos vigentes.

El frontend intenta leer el estado publicado en GitHub y utiliza la copia incluida en la versión del sitio como respaldo. La actualización mensual se ejecuta el día 1 a las 08:17 de Argentina y también puede iniciarse manualmente desde GitHub Actions.

## Paso 8 — Mercado Libre Inmuebles

`scripts/extract_mercadolibre_market.py` consulta exclusivamente `https://api.mercadolibre.com`. El alcance inicial son departamentos publicados en venta en Santa Fe Capital. El proceso:

1. resuelve la ciudad mediante `classified_locations`;
2. pagina la búsqueda del sitio argentino `MLA` hasta el límite admitido;
3. consulta el detalle de los avisos por lotes;
4. conserva solamente departamentos en venta ubicados en la ciudad;
5. normaliza ARS a USD con la referencia BCRA ya incorporada;
6. calcula medianas y muestras para ciudad y barrios con alias verificados;
7. publica solo estadísticas agregadas en `mercadolibre-santa-fe.json`.

No se escriben IDs de avisos, vendedores, direcciones, coordenadas, títulos, descripciones ni enlaces individuales. `scripts/validate_mercadolibre_market.py` comprueba el esquema, los rangos de precios, la muestra, el límite de resultados y la ausencia de campos individuales.

La activación requiere crear y autorizar una aplicación en [Mercado Libre Developers](https://developers.mercadolibre.com.ar/) y guardar el token como secreto `MELI_ACCESS_TOKEN` del repositorio. Mientras el secreto no exista, el flujo mensual conserva el archivo con `pending_authorization`, no falla los demás conectores y el sitio informa que no hay datos de Mercado Libre. Los tokens nunca deben añadirse al repositorio ni enviarse por chat.
