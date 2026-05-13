# Funcionamiento Total de las Demos de Georeferenciacion

## 1. Vision general del proyecto

La aplicacion expone 3 demos de mapas:

- Leaflet: /examples/leaflet-world
- OpenLayers: /examples/openlayers-world
- MapLibre: /examples/maplibre-world

Todas comparten:

- El mismo backend Flask.
- El mismo endpoint de datos agregados: /api/seizures.
- El mismo archivo de centroides por pais: /static/vendor/countries.geojson.
- El mismo sistema de filtros (region y tipo de droga).
- El mismo criterio para escalar el tamano de marcadores por cantidad en kilogramos.

## 2. Backend Flask (fuente de datos comun)

Archivo principal: app.py

### 2.1 Rutas

- /: pagina de inicio con tarjetas de demos.
- /examples/<slug>: renderiza la plantilla de cada libreria.
- /api/seizures: devuelve JSON con registros agregados.

### 2.2 Consulta SQL y agregacion

La funcion load_seizure_records:

- Lee db/drug_seizures.db.
- Agrupa por region, subregion, pais, droga y codigo pais (msCode).
- Normaliza valores de Kilograms (incluyendo valores vacios y comas).
- Filtra registros sin codigo pais y con total mayor a 0.
- Devuelve objetos con:
  - region
  - subregion
  - country
  - drugName
  - countryCode
  - kilograms

### 2.3 Cache

Se usa lru_cache(maxsize=1) para evitar recalcular la consulta en cada request del endpoint.

## 3. Capa de datos compartida en frontend

Archivo: static/seizure-data.js

### 3.1 Carga de datos

- loadSeizureData():
  - Hace fetch a /api/seizures.
  - Cachea la promesa para reutilizar resultados.

- loadCountryCentroids():
  - Hace fetch a /static/vendor/countries.geojson.
  - Construye indice de centroides por ISO3166-1-Alpha-3.
  - Cachea la promesa.

### 3.2 Calculo de centroides

- Recorre las coordenadas de cada geometria.
- Calcula bounds min/max lng/lat.
- Deriva centro aproximado por pais.

### 3.3 Agregacion para mapa

aggregateSeizureRows(rows, centroids):

- Une cada registro de incautacion con el centroide del pais.
- Agrupa por countryCode.
- Suma kilograms por pais.
- Junta tipos de droga en un conjunto unico.
- Devuelve lista ordenada de mayor a menor kilograms.

### 3.4 Escala de burbuja

scaleMarkerRadius(kilograms):

- Formula: 6 + log10(max(kilograms, 1)) * 3.
- Limite inferior: 6.
- Limite superior: 18.

## 4. Filtros compartidos

Archivo: static/filter-controls.js

### 4.1 Controles

Usa elementos de _map_filters.html:

- region-filter
- drug-filter
- filter-reset
- filter-status

### 4.2 Flujo

createGeoFilters(points, onChange):

- Construye opciones de region y tipo de droga desde los datos.
- Aplica filtros al cambiar cualquier select.
- Ejecuta callback onChange(filteredPoints) para que cada libreria repinte el mapa.
- Actualiza texto de estado con cantidad de registros y paises visibles.

## 5. Demo Leaflet

Archivo principal: static/leaflet.js

### 5.1 Inicializacion

- Crea mapa con centro [20, 0], zoom 2, minZoom 2.
- Crea grupo markerLayer para los marcadores.

### 5.2 Mapas base disponibles

- OpenStreetMap
- Carto Positron
- OpenTopoMap
- HOT OpenStreetMap

Hay un selector visual (basemap-control) que cambia la capa base activa.

### 5.3 Render de datos

renderMarkers(rows, centroids):

- Convierte datos filtrados a puntos agregados por pais.
- Limpia marcadores previos.
- Dibuja circleMarker por pais.
- Popup por marcador con:
  - pais
  - region/subregion
  - total incautado
  - tipos de droga (hasta 3 + ...)
- Ajusta encuadre con fitBounds si hay puntos.
- Si no hay puntos, vuelve a vista global.

### 5.4 Arranque

- Carga en paralelo datos de incautaciones y centroides.
- Monta filtros compartidos.
- El callback de filtros repinta marcadores.

## 6. Demo OpenLayers

Archivo principal: static/openlayers.js

### 6.1 Inicializacion

- Crea mapa con view en EPSG:3857, centro [0, 15], zoom 2.
- Crea capa vectorial para burbujas de incautacion.
- Crea overlay popup para detalle al hacer clic.

### 6.2 Mapas base disponibles

- Paises (local): capa vectorial desde countries.geojson.
- OpenStreetMap
- Carto Positron
- OpenTopoMap
- HOT OpenStreetMap

El selector de mapa base alterna visibilidad entre capas.

### 6.3 Estado actual de visualizacion

- La opcion por defecto es Paises (local) para garantizar una base visible.
- Tambien se mantienen opciones raster externas para comparacion.

### 6.4 Diagnostico en pantalla

Actualmente incluye panel de diagnostico con:

- Tamano de contenedor y mapa.
- Conteo de tileloadstart/end/error.
- Conteo de postrender/rendercomplete.
- Estado de canvas (rgb, alpha, spread) para depuracion visual.

Ademas incluye fallback de contraste (si detecta canvas casi plano, intenta activar HOT).

### 6.5 Render de datos

renderFeatures(rows, centroids):

- Agrega feature por pais (ol.geom.Point con proyeccion desde lon/lat).
- Aplica estilo circular (radio proporcional a kilograms).
- Ajusta vista al extent de features cuando hay datos.
- Restablece vista global cuando no hay resultados.

Interaccion:

- singleclick: muestra popup con detalle del pais.
- pointermove: cambia cursor cuando hay feature bajo el puntero.

### 6.6 Carga de assets OpenLayers

Template: templates/openlayers_world.html

- CSS OpenLayers desde CDN jsDelivr.
- JS OpenLayers desde CDN jsDelivr.

## 7. Demo MapLibre

Archivo principal: static/maplibre.js

### 7.1 Inicializacion

- Crea mapa WebGL con estilo raster inicial OSM.
- Centro [10, 20], zoom 1.6.
- Agrega NavigationControl.

### 7.2 Mapas base disponibles

- OpenStreetMap
- Carto Positron
- OpenTopoMap
- HOT OpenStreetMap

La funcion createRasterStyle(basemapId) genera estilo MapLibre (version 8) con source raster dinamico.

### 7.3 Cambio de estilo

- Selector basemap-control cambia estilo con map.setStyle(...).
- Si ocurre error de estilo, hay fallback a OSM.

### 7.4 Render de datos

renderMarkers(rows, centroids):

- Limpia markers existentes.
- Crea Marker HTML con tamano proporcional.
- Asigna popup con resumen de pais/incautaciones.
- Ajusta vista con fitBounds si hay puntos.
- Si no hay puntos, vuelve a vista global con easeTo.

### 7.5 Arranque

- Espera evento load del mapa.
- Luego carga datos y centroides.
- Monta filtros compartidos.
- Re-renderiza en cada cambio de filtro.

## 8. Flujo completo de ejecucion (de extremo a extremo)

1. Usuario entra a una ruta /examples/<demo>.
2. Flask renderiza template de la libreria.
3. Se cargan scripts compartidos (datos + filtros) y script propio de la libreria.
4. El script del mapa inicializa:
   - mapa base
   - control de mapa base
   - capa de marcadores/entidades
5. Se ejecuta Promise.all:
   - /api/seizures
   - /static/vendor/countries.geojson
6. Se crea indice de centroides y agregacion por pais.
7. Se montan filtros de region y droga.
8. Cada cambio de filtro dispara repintado de marcadores.
9. El usuario puede cambiar mapa base sin perder estado de filtros.

## 9. Diferencias clave entre demos

- Leaflet:
  - Enfoque simple y rapido para markers.
  - Manejo muy directo de tile layers.

- OpenLayers:
  - Mayor control SIG y pipeline de capas.
  - Incluye popup nativo con overlay.
  - Incluye mapa base local vectorial y panel de diagnostico activo.

- MapLibre:
  - Render WebGL y estilos tipo Mapbox Style.
  - Cambio de mapa base via setStyle.

## 10. Observaciones operativas

- Todas las demos trabajan sin API key usando proveedores abiertos.
- Las atribuciones de cada proveedor estan incluidas en configuracion de capas.
- En OpenLayers, el diagnostico actual fue agregado para investigar el problema de mapa invisible y puede retirarse luego de estabilizar la visualizacion.
