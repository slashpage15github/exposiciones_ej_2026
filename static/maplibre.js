const mapLibreMapNode = document.getElementById("maplibre-map");

if (mapLibreMapNode) {
    const BASEMAPS = {
        osm: {
            label: "OpenStreetMap",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        },
        carto: {
            label: "Carto Positron",
            tiles: ["https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", "https://d.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"],
            maxZoom: 20,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        },
        opentopo: {
            label: "OpenTopoMap",
            tiles: ["https://a.tile.opentopomap.org/{z}/{x}/{y}.png", "https://b.tile.opentopomap.org/{z}/{x}/{y}.png", "https://c.tile.opentopomap.org/{z}/{x}/{y}.png"],
            maxZoom: 17,
            attribution:
                'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
        },
        hot: {
            label: "HOT OpenStreetMap",
            tiles: ["https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", "https://b.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", "https://c.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"],
            maxZoom: 19,
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/">OpenStreetMap France</a>'
        }
    };

    function createRasterStyle(basemapId) {
        const basemap = BASEMAPS[basemapId] || BASEMAPS.osm;
        return {
            version: 8,
            sources: {
                basemap: {
                    type: "raster",
                    tiles: basemap.tiles,
                    tileSize: 256,
                    maxzoom: basemap.maxZoom,
                    attribution: basemap.attribution
                }
            },
            layers: [
                {
                    id: "basemap-layer",
                    type: "raster",
                    source: "basemap"
                }
            ]
        };
    }

    const map = new maplibregl.Map({
        container: "maplibre-map",
        style: createRasterStyle("osm"),
        center: [10, 20],
        zoom: 1.6
    });

    const markers = [];

    map.addControl(new maplibregl.NavigationControl(), "top-right");

    const basemapControl = document.createElement("div");
    basemapControl.className = "basemap-control";
    basemapControl.innerHTML = `
        <label for="maplibre-basemap" class="basemap-control__label">Mapa base</label>
        <select id="maplibre-basemap" class="basemap-control__select" aria-label="Seleccionar mapa base">
            ${Object.entries(BASEMAPS)
                .map(([id, definition]) => `<option value="${id}">${definition.label}</option>`)
                .join("")}
        </select>
    `;
    mapLibreMapNode.parentElement?.appendChild(basemapControl);

    const basemapSelect = basemapControl.querySelector("#maplibre-basemap");
    basemapSelect?.addEventListener("change", (event) => {
        const selectedId = event.target.value;
        map.setStyle(createRasterStyle(selectedId));
        map.once("error", () => {
            map.setStyle(createRasterStyle("osm"));
            if (basemapSelect) {
                basemapSelect.value = "osm";
            }
        });
    });

    function createMarkerElement(kilograms) {
        const radius = window.scaleMarkerRadius(kilograms);
        const markerElement = document.createElement("div");
        markerElement.className = "map-marker-bubble";
        markerElement.style.width = `${radius * 2}px`;
        markerElement.style.height = `${radius * 2}px`;
        return markerElement;
    }

    function renderMarkers(rows, centroids) {
        const points = window.aggregateSeizureRows(rows, centroids);
        markers.forEach((marker) => marker.remove());
        markers.length = 0;

        points.forEach((point) => {
            const marker = new maplibregl.Marker({ element: createMarkerElement(point.kilograms) })
                .setLngLat(point.coords)
                .setPopup(
                    new maplibregl.Popup({ offset: 25 }).setHTML(
						`<strong>${point.country}</strong><br>${point.region} / ${point.subregion}<br>Total incautado: ${point.kilograms} kg<br>Tipos de droga: ${point.drugNames.slice(0, 3).join(", ")}${point.drugNames.length > 3 ? "..." : ""}`
                    )
                )
                .addTo(map);

            markers.push(marker);
        });

        if (points.length > 0) {
            const bounds = new maplibregl.LngLatBounds();
            points.forEach((point) => bounds.extend(point.coords));
            map.fitBounds(bounds, { padding: 60, maxZoom: 4 });
        } else {
            map.easeTo({ center: [10, 20], zoom: 1.6 });
        }
    }

    map.on("load", () => {
        (async () => {
            try {
                const [rows, centroids] = await Promise.all([window.loadSeizureData(), window.loadCountryCentroids()]);
                window.createGeoFilters(rows, (filteredRows) => renderMarkers(filteredRows, centroids));
            } catch (error) {
                console.error(error);
                window.setGeoFilterStatus("No se pudieron cargar los datos reales de incautaciones.");
            }
        })();
    });
}