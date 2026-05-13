# Implementacion de librerias de mapas (JS)

## Vision general
Este proyecto tiene tres implementaciones de mapa, una por libreria:

- Leaflet (static/leaflet.js)
- MapLibre GL JS (static/maplibre.js)
- OpenLayers (static/openlayers.js)

Las tres comparten la misma fuente de datos y el mismo flujo de filtros usando dos utilitarios comunes:

- static/seizure-data.js: carga datos y agrega incautaciones por pais.
- static/filter-controls.js: construye filtros de region y tipo de droga.

## Flujo de datos compartido
1. `loadSeizureData()` hace fetch de `/api/seizures` y expone `records`.
2. `loadCountryCentroids()` descarga `/static/vendor/countries.geojson` y calcula centroides por codigo ISO alfa-3 (centro del bbox).
3. `aggregateSeizureRows(rows, centroids)` agrupa por pais, suma kg y acumula tipos de droga.
4. `scaleMarkerRadius(kilograms)` calcula un radio logaritmico para los marcadores.
5. `createGeoFilters(rows, onChange)` arma los selectores y dispara `onChange` con los registros filtrados.

Cada libreria toma los registros filtrados y los transforma en marcadores/feature segun su API.

## Leaflet (static/leaflet.js)
- Crea el mapa con `L.map`, con centro `[20, 0]`, zoom 2 y `minZoom` 2.
- Define `BASEMAPS` con URLs de tiles y crea las capas via `L.tileLayer`.
- Agrega un control HTML (`select`) para cambiar de mapa base.
- Usa `L.layerGroup` para los marcadores.
- `renderMarkers()` crea `L.circleMarker` con estilo y popup, y luego ajusta el `fitBounds`.
- Carga datos en un `Promise.all` y conecta los filtros con `renderMarkers()`.

## MapLibre GL JS (static/maplibre.js)
- Construye un estilo raster dinamico con `createRasterStyle()`.
- Inicia `maplibregl.Map` con `style`, centro `[10, 20]` y zoom 1.6.
- Agrega `NavigationControl` y el mismo selector de mapa base.
- Cambia el estilo con `map.setStyle()`, con fallback a OSM si hay error.
- Crea marcadores DOM (`div`) cuyo tamano depende de `scaleMarkerRadius()`.
- `renderMarkers()` agrega `Marker` con `Popup` y ajusta `fitBounds`.
- La carga de datos ocurre en `map.on("load")`.

## OpenLayers (static/openlayers.js)
- Verifica que exista `window.ol` y asegura altura minima del contenedor.
- Crea un panel de diagnostico para medir carga de tiles y render.
- Define `BASEMAPS` que incluye un vector local de paises (`countries.geojson`) y varias capas XYZ.
- Crea capas base y una capa vectorial para marcadores.
- Usa `ol.Overlay` para el popup HTML (`#openlayers-popup`).
- Ajusta el tamano del mapa con `updateSize()` en eventos de render y resize.
- Implementa un fallback que activa HOT si el canvas queda sin contraste.
- `renderFeatures()` crea `ol.Feature` por pais con estilo circular y `fit` sobre el extent.
- Maneja clicks para abrir el popup y `pointermove` para cursor.

## Filtros y estado (static/filter-controls.js)
- Llena selectores de region y tipo de droga a partir de los datos cargados.
- Aplica filtros locales y actualiza un mensaje de estado.
- Exponen `createGeoFilters()` y `setGeoFilterStatus()` para las paginas de mapas.

## Datos auxiliares
- static/geo-demo-data.js define `window.geoDemoPoints` como dataset de ejemplo. No se usa en los mapas actuales.

## Puntos clave para extender
- Agregar un nuevo mapa base: editar `BASEMAPS` en cada libreria.
- Cambiar el calculo de radio: ajustar `scaleMarkerRadius()`.
- Ajustar agrupacion por pais: modificar `aggregateSeizureRows()`.
- Cambiar filtros: editar `createGeoFilters()` y los selectores en el HTML.
