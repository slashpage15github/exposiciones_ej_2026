const leafletMapNode = document.getElementById("leaflet-map");

if (leafletMapNode) {
	const BASEMAPS = {
		osm: {
			label: "OpenStreetMap",
			url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
			options: {
				maxZoom: 19,
				attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
			}
		},
		carto: {
			label: "Carto Positron",
			url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
			options: {
				maxZoom: 20,
				subdomains: "abcd",
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
			}
		},
		opentopo: {
			label: "OpenTopoMap",
			url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
			options: {
				maxZoom: 17,
				subdomains: "abc",
				attribution:
					'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
			}
		},
		hot: {
			label: "HOT OpenStreetMap",
			url: "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
			options: {
				maxZoom: 19,
				subdomains: "abc",
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/">OpenStreetMap France</a>'
			}
		}
	};

	const map = L.map("leaflet-map", {
		center: [20, 0],
		zoom: 2,
		minZoom: 2
	});

	const leafletBaseLayers = Object.entries(BASEMAPS).reduce((accumulator, [id, definition]) => {
		accumulator[definition.label] = L.tileLayer(definition.url, definition.options);
		return accumulator;
	}, {});

	leafletBaseLayers[BASEMAPS.osm.label].addTo(map);

	const basemapControl = document.createElement("div");
	basemapControl.className = "basemap-control";
	basemapControl.innerHTML = `
		<label for="leaflet-basemap" class="basemap-control__label">Mapa base</label>
		<select id="leaflet-basemap" class="basemap-control__select" aria-label="Seleccionar mapa base">
			${Object.entries(BASEMAPS)
				.map(([id, definition]) => `<option value="${id}">${definition.label}</option>`)
				.join("")}
		</select>
	`;
	leafletMapNode.parentElement?.appendChild(basemapControl);

	const basemapSelect = basemapControl.querySelector("#leaflet-basemap");
	basemapSelect?.addEventListener("change", (event) => {
		const selectedId = event.target.value;
		const selectedBasemap = BASEMAPS[selectedId] || BASEMAPS.osm;
		Object.values(leafletBaseLayers).forEach((layer) => {
			if (map.hasLayer(layer)) {
				map.removeLayer(layer);
			}
		});
		leafletBaseLayers[selectedBasemap.label].addTo(map);
	});

	const markerLayer = L.layerGroup().addTo(map);

	function renderMarkers(rows, centroids) {
		const points = window.aggregateSeizureRows(rows, centroids);
		markerLayer.clearLayers();

		points.forEach((point) => {
			L.circleMarker([point.coords[1], point.coords[0]], {
				radius: window.scaleMarkerRadius(point.kilograms),
				color: "#102542",
				weight: 2,
				fillColor: "#d95d39",
				fillOpacity: 0.78
			})
				.addTo(markerLayer)
				.bindPopup(
					`<strong>${point.country}</strong><br>${point.region} / ${point.subregion}<br>Total incautado: ${point.kilograms} kg<br>Tipos de droga: ${point.drugNames.slice(0, 3).join(", ")}${point.drugNames.length > 3 ? "..." : ""}`
				);
		});

		if (points.length > 0) {
			const bounds = L.latLngBounds(points.map((point) => [point.coords[1], point.coords[0]]));
			map.fitBounds(bounds, { padding: [40, 40] });
		} else {
			map.setView([20, 0], 2);
		}
	}

	(async () => {
		try {
			const [rows, centroids] = await Promise.all([window.loadSeizureData(), window.loadCountryCentroids()]);
			window.createGeoFilters(rows, (filteredRows) => renderMarkers(filteredRows, centroids));
		} catch (error) {
			console.error(error);
			window.setGeoFilterStatus("No se pudieron cargar los datos reales de incautaciones.");
		}
	})();
}
