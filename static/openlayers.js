const openLayersMapNode = document.getElementById("openlayers-map");
const popupContainer = document.getElementById("openlayers-popup");
const popupContent = document.getElementById("openlayers-popup-content");
const popupCloser = document.getElementById("openlayers-popup-closer");

if (openLayersMapNode && window.ol) {
    if (openLayersMapNode.clientHeight === 0) {
        openLayersMapNode.style.minHeight = "560px";
    }

    const diagnostics = {
        tileStart: 0,
        tileEnd: 0,
        tileError: 0,
        postRender: 0,
        renderComplete: 0
    };

    const diagnosticsPanel = document.createElement("div");
    diagnosticsPanel.className = "map-debug-panel";
    diagnosticsPanel.setAttribute("aria-live", "polite");
    openLayersMapNode.parentElement?.appendChild(diagnosticsPanel);

    function getCanvasDiagnostics() {
        const canvases = Array.from(openLayersMapNode.querySelectorAll("canvas"));
        if (canvases.length === 0) {
            return "Canvas: ninguno";
        }

        const details = canvases
            .slice(0, 3)
            .map((canvas, index) => {
                const rect = canvas.getBoundingClientRect();
                const style = window.getComputedStyle(canvas);
                let alphaSample = "n/a";
                let rgbSample = "n/a";
                let spread = "n/a";

                try {
                    const ctx = canvas.getContext("2d", { willReadFrequently: true });
                    if (ctx && canvas.width > 0 && canvas.height > 0) {
                        const x = Math.max(0, Math.floor(canvas.width / 2));
                        const y = Math.max(0, Math.floor(canvas.height / 2));
                        const pixel = ctx.getImageData(x, y, 1, 1).data;
                        alphaSample = String(pixel[3]);
                        rgbSample = `${pixel[0]},${pixel[1]},${pixel[2]}`;

                        const p1 = ctx.getImageData(Math.floor(canvas.width * 0.2), Math.floor(canvas.height * 0.2), 1, 1).data;
                        const p2 = ctx.getImageData(Math.floor(canvas.width * 0.8), Math.floor(canvas.height * 0.8), 1, 1).data;
                        const p3 = ctx.getImageData(Math.floor(canvas.width * 0.2), Math.floor(canvas.height * 0.8), 1, 1).data;
                        const delta =
                            Math.abs(p1[0] - p2[0]) +
                            Math.abs(p1[1] - p2[1]) +
                            Math.abs(p1[2] - p2[2]) +
                            Math.abs(p1[0] - p3[0]) +
                            Math.abs(p1[1] - p3[1]) +
                            Math.abs(p1[2] - p3[2]);
                        spread = String(delta);
                    }
                } catch (error) {
                    alphaSample = "blocked";
                }

                return `#${index + 1} ${Math.round(rect.width)}x${Math.round(rect.height)} css(op:${style.opacity}, vis:${style.visibility}, disp:${style.display}) rgb:${rgbSample} alpha:${alphaSample} spread:${spread}`;
            })
            .join(" | ");

        return `Canvas: ${canvases.length} -> ${details}`;
    }

    function updateDiagnostics(extraMessage = "") {
        const mapSize = typeof map?.getSize === "function" ? map.getSize() : null;
        const nodeWidth = openLayersMapNode.clientWidth;
        const nodeHeight = openLayersMapNode.clientHeight;
        const canvasInfo = getCanvasDiagnostics();
        diagnosticsPanel.innerHTML = `
            <strong>Diagnostico OpenLayers</strong><br>
            Contenedor: ${nodeWidth}x${nodeHeight}px<br>
            Tamano mapa: ${Array.isArray(mapSize) ? `${mapSize[0]}x${mapSize[1]}px` : "sin inicializar"}<br>
            Tiles: start ${diagnostics.tileStart} / end ${diagnostics.tileEnd} / error ${diagnostics.tileError}<br>
            Render: postrender ${diagnostics.postRender} / complete ${diagnostics.renderComplete}
            <br>${canvasInfo}
            ${extraMessage ? `<br>${extraMessage}` : ""}
        `;
    }

    const BASEMAPS = {
        countries: {
            label: "Paises (local)",
            createLayer: () =>
                new ol.layer.Vector({
                    source: new ol.source.Vector({
                        url: "/static/vendor/countries.geojson",
                        format: new ol.format.GeoJSON({
                            dataProjection: "EPSG:4326",
                            featureProjection: "EPSG:3857"
                        })
                    }),
                    style: new ol.style.Style({
                        fill: new ol.style.Fill({ color: "rgba(146, 176, 201, 0.35)" }),
                        stroke: new ol.style.Stroke({ color: "#102542", width: 1.1 })
                    })
                })
        },
        osm: {
            label: "OpenStreetMap",
            createSource: () =>
                new ol.source.XYZ({
                    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    maxZoom: 19,
                    attributions: ['&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors']
                })
        },
        carto: {
            label: "Carto Positron",
            createSource: () =>
                new ol.source.XYZ({
                    url: "https://{a-c}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                    maxZoom: 20,
                    attributions: [
                        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    ]
                })
        },
        opentopo: {
            label: "OpenTopoMap",
            createSource: () =>
                new ol.source.XYZ({
                    url: "https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png",
                    maxZoom: 17,
                    attributions: [
                        'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
                    ]
                })
        },
        hot: {
            label: "HOT OpenStreetMap",
            createSource: () =>
                new ol.source.XYZ({
                    url: "https://{a-c}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
                    maxZoom: 19,
                    attributions: [
                        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/">OpenStreetMap France</a>'
                    ]
                })
        }
    };

    const basemapLayers = Object.entries(BASEMAPS).reduce((accumulator, [id, definition]) => {
        if (typeof definition.createLayer === "function") {
            const layer = definition.createLayer();
            layer.setVisible(id === "countries");
            accumulator[id] = layer;
            return accumulator;
        }

        accumulator[id] = new ol.layer.Tile({
            source: definition.createSource(),
            visible: id === "countries"
        });
        return accumulator;
    }, {});

    const vectorLayer = new ol.layer.Vector({
        source: new ol.source.Vector()
    });

    const overlay = new ol.Overlay({
        element: popupContainer,
        autoPan: {
            animation: {
                duration: 250
            }
        }
    });

    const map = new ol.Map({
        target: openLayersMapNode,
        layers: [...Object.values(basemapLayers), vectorLayer],
        overlays: [overlay],
        view: new ol.View({
            center: ol.proj.fromLonLat([0, 15]),
            zoom: 2
        })
    });

    let hasLoadedAnyTile = false;
    Object.values(basemapLayers).forEach((layer) => {
        if (!(layer instanceof ol.layer.Tile)) {
            return;
        }

        const source = layer.getSource();
        source.on("tileloadstart", () => {
            diagnostics.tileStart += 1;
            updateDiagnostics();
        });
        source.on("tileloadend", () => {
            hasLoadedAnyTile = true;
            diagnostics.tileEnd += 1;
            updateDiagnostics();
        });
        source.on("tileloaderror", (errorEvent) => {
            diagnostics.tileError += 1;
            updateDiagnostics("Fallo de descarga de tiles");
            console.warn("OpenLayers tile load error:", errorEvent);
        });
    });

    requestAnimationFrame(() => map.updateSize());
    window.addEventListener("resize", () => map.updateSize());
    map.once("postrender", () => map.updateSize());
    map.on("postrender", () => {
        diagnostics.postRender += 1;
        if (diagnostics.postRender <= 20) {
            updateDiagnostics();
        }
    });
    map.once("rendercomplete", () => {
        hasLoadedAnyTile = true;
        diagnostics.renderComplete += 1;
        updateDiagnostics("Render completo detectado");
    });
    map.on("rendercomplete", () => {
        diagnostics.renderComplete += 1;
        if (diagnostics.renderComplete <= 20) {
            updateDiagnostics();
        }
    });

    setTimeout(() => {
        if (!hasLoadedAnyTile) {
            console.warn("OpenLayers no completó render inicial, forzando renderSync/updateSize.");
            map.updateSize();
            map.renderSync();
            updateDiagnostics("Se forzo updateSize/renderSync");
        }
    }, 2500);

    setTimeout(() => {
        if (diagnostics.tileStart === 0) {
            updateDiagnostics("No hubo solicitudes de tiles: revisar red/bloqueo del navegador");
        } else if (diagnostics.tileEnd === 0 && diagnostics.tileError > 0) {
            updateDiagnostics("Se pidieron tiles pero todos fallaron: revisar proveedor o firewall");
        }
    }, 4500);

    setTimeout(() => {
        const canvas = openLayersMapNode.querySelector("canvas");
        if (!canvas) {
            return;
        }

        try {
            const ctx = canvas.getContext("2d", { willReadFrequently: true });
            if (!ctx || canvas.width < 4 || canvas.height < 4) {
                return;
            }

            const p1 = ctx.getImageData(Math.floor(canvas.width * 0.25), Math.floor(canvas.height * 0.25), 1, 1).data;
            const p2 = ctx.getImageData(Math.floor(canvas.width * 0.75), Math.floor(canvas.height * 0.75), 1, 1).data;
            const p3 = ctx.getImageData(Math.floor(canvas.width * 0.25), Math.floor(canvas.height * 0.75), 1, 1).data;
            const spread =
                Math.abs(p1[0] - p2[0]) +
                Math.abs(p1[1] - p2[1]) +
                Math.abs(p1[2] - p2[2]) +
                Math.abs(p1[0] - p3[0]) +
                Math.abs(p1[1] - p3[1]) +
                Math.abs(p1[2] - p3[2]);

            if (spread < 20 && basemapSelect) {
                basemapSelect.value = "hot";
                Object.entries(basemapLayers).forEach(([id, layer]) => {
                    layer.setVisible(id === "hot");
                });
                map.renderSync();
                updateDiagnostics("Fallback automatico: se activo HOT para aumentar contraste visual");
            }
        } catch (error) {
            updateDiagnostics("No se pudo analizar el canvas para fallback");
        }
    }, 5500);

    if (window.ResizeObserver) {
        const resizeObserver = new ResizeObserver(() => map.updateSize());
        resizeObserver.observe(openLayersMapNode);
    }

    if (popupCloser) {
        popupCloser.onclick = function () {
            overlay.setPosition(undefined);
            popupContainer.hidden = true;
            popupCloser.blur();
            return false;
        };
    }

    const basemapControl = document.createElement("div");
    basemapControl.className = "basemap-control";
    basemapControl.innerHTML = `
        <label for="openlayers-basemap" class="basemap-control__label">Mapa base</label>
        <select id="openlayers-basemap" class="basemap-control__select" aria-label="Seleccionar mapa base">
            ${Object.entries(BASEMAPS)
                .map(([id, definition]) => `<option value="${id}">${definition.label}</option>`)
                .join("")}
        </select>
    `;
    openLayersMapNode.parentElement?.appendChild(basemapControl);

    const basemapSelect = basemapControl.querySelector("#openlayers-basemap");
    if (basemapSelect) {
        basemapSelect.value = "countries";
    }

    basemapSelect?.addEventListener("change", (event) => {
        const selectedId = event.target.value;
        Object.entries(basemapLayers).forEach(([id, layer]) => {
            layer.setVisible(id === selectedId);
        });
        updateDiagnostics(`Mapa base activo: ${BASEMAPS[selectedId]?.label || "OpenStreetMap"}`);
    });

    updateDiagnostics("Inicializando mapa...");

    function createFeature(point) {
        const feature = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.fromLonLat(point.coords)),
            name: point.country
        });

        feature.setStyle(
            new ol.style.Style({
                image: new ol.style.Circle({
                    radius: window.scaleMarkerRadius(point.kilograms),
                    fill: new ol.style.Fill({ color: "#ff6b6b" }),
                    stroke: new ol.style.Stroke({ color: "#102542", width: 2 })
                })
            })
        );

        feature.setProperties({
            country: point.country,
            region: point.region,
            subregion: point.subregion,
            kilograms: point.kilograms,
            drugNames: point.drugNames
        });

        return feature;
    }

    function renderFeatures(rows, centroids) {
        const points = window.aggregateSeizureRows(rows, centroids);
        const source = vectorLayer.getSource();
        source.clear();
        source.addFeatures(points.map(createFeature));
        overlay.setPosition(undefined);
        popupContainer.hidden = true;

        if (points.length > 0) {
            map.getView().fit(source.getExtent(), {
                padding: [50, 50, 50, 50],
                maxZoom: 4,
                duration: 250
            });
            map.updateSize();
        } else {
            map.getView().setCenter(ol.proj.fromLonLat([0, 15]));
            map.getView().setZoom(2);
        }
    }

    map.on("singleclick", (event) => {
        const feature = map.forEachFeatureAtPixel(event.pixel, (candidate) => candidate);
        if (!feature) {
            overlay.setPosition(undefined);
            popupContainer.hidden = true;
            return;
        }

        popupContent.innerHTML = `
            <strong>${feature.get("country")}</strong>
            <p>${feature.get("region")} / ${feature.get("subregion")}</p>
            <p>Total incautado: ${feature.get("kilograms")} kg</p>
            <p>Tipos de droga: ${feature.get("drugNames").slice(0, 3).join(", ")}${feature.get("drugNames").length > 3 ? "..." : ""}</p>
        `;
        popupContainer.hidden = false;
        overlay.setPosition(event.coordinate);
    });

    map.on("pointermove", (event) => {
        if (event.dragging) {
            return;
        }

        const hit = map.hasFeatureAtPixel(event.pixel);
        openLayersMapNode.style.cursor = hit ? "pointer" : "";
    });

    (async () => {
        try {
            const [rows, centroids] = await Promise.all([window.loadSeizureData(), window.loadCountryCentroids()]);
            window.createGeoFilters(rows, (filteredRows) => renderFeatures(filteredRows, centroids));
        } catch (error) {
            console.error(error);
            window.setGeoFilterStatus("No se pudieron cargar los datos reales de incautaciones.");
        }
    })();
} else if (openLayersMapNode) {
    console.error("OpenLayers no se cargó correctamente.");
    window.setGeoFilterStatus("OpenLayers no se pudo cargar en el navegador.");
}