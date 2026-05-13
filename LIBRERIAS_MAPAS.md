# Librerias de mapas

## MapLibre GL JS
- Motor de render basado en WebGL: dibuja mapas vectoriales en la GPU para alta fluidez.
- Usa estilos JSON (Mapbox Style Spec) para definir capas, colores y simbolos.
- Consume fuentes como vector tiles, GeoJSON y raster, y permite efectos 3D y rotacion.

## Leaflet
- Libreria ligera orientada a 2D: renderiza capas con DOM/SVG/Canvas.
- Modelo simple de mapa y capas: normalmente usa tiles raster y sobrepone vectores.
- Muy facil de integrar y extender via plugins.

## OpenLayers
- Motor mas completo para GIS web: soporta Canvas y WebGL segun la capa.
- Maneja multiples proyecciones y formatos (WMS/WMTS/WFS, vector tiles, GeoJSON).
- Ideal para escenarios avanzados con analisis, edicion y grandes volumnes de datos.
