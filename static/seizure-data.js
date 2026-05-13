(function () {
    const API_URL = "/api/seizures";
    const COUNTRIES_URL = "/static/vendor/countries.geojson";

    let seizureDataPromise;
    let centroidsPromise;

    function collectBounds(coordinates, bounds) {
        if (!Array.isArray(coordinates)) {
            return bounds;
        }

        if (typeof coordinates[0] === "number" && typeof coordinates[1] === "number") {
            const [lng, lat] = coordinates;
            bounds.minLng = Math.min(bounds.minLng, lng);
            bounds.maxLng = Math.max(bounds.maxLng, lng);
            bounds.minLat = Math.min(bounds.minLat, lat);
            bounds.maxLat = Math.max(bounds.maxLat, lat);
            return bounds;
        }

        coordinates.forEach((entry) => collectBounds(entry, bounds));
        return bounds;
    }

    function buildCentroidIndex(geoJson) {
        return geoJson.features.reduce((index, feature) => {
            const code = feature.properties["ISO3166-1-Alpha-3"];
            if (!code || !feature.geometry) {
                return index;
            }

            const bounds = collectBounds(feature.geometry.coordinates, {
                minLng: Infinity,
                maxLng: -Infinity,
                minLat: Infinity,
                maxLat: -Infinity
            });

            if (!Number.isFinite(bounds.minLng) || !Number.isFinite(bounds.minLat)) {
                return index;
            }

            index[code] = [
                Number(((bounds.minLng + bounds.maxLng) / 2).toFixed(4)),
                Number(((bounds.minLat + bounds.maxLat) / 2).toFixed(4))
            ];

            return index;
        }, {});
    }

    window.loadSeizureData = function loadSeizureData() {
        if (!seizureDataPromise) {
            seizureDataPromise = fetch(API_URL)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Failed to load seizure data: ${response.status}`);
                    }
                    return response.json();
                })
                .then((payload) => payload.records);
        }

        return seizureDataPromise;
    };

    window.loadCountryCentroids = function loadCountryCentroids() {
        if (!centroidsPromise) {
            centroidsPromise = fetch(COUNTRIES_URL)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Failed to load country shapes: ${response.status}`);
                    }
                    return response.json();
                })
                .then(buildCentroidIndex);
        }

        return centroidsPromise;
    };

    window.aggregateSeizureRows = function aggregateSeizureRows(rows, centroids) {
        const countries = new Map();

        rows.forEach((row) => {
            const coords = centroids[row.countryCode];
            if (!coords) {
                return;
            }

            if (!countries.has(row.countryCode)) {
                countries.set(row.countryCode, {
                    countryCode: row.countryCode,
                    country: row.country,
                    region: row.region,
                    subregion: row.subregion,
                    coords,
                    kilograms: 0,
                    drugNames: new Set()
                });
            }

            const entry = countries.get(row.countryCode);
            entry.kilograms += Number(row.kilograms);
            entry.drugNames.add(row.drugName);
        });

        return [...countries.values()]
            .map((entry) => ({
                ...entry,
                kilograms: Number(entry.kilograms.toFixed(2)),
                drugNames: [...entry.drugNames].sort()
            }))
            .sort((left, right) => right.kilograms - left.kilograms);
    };

    window.scaleMarkerRadius = function scaleMarkerRadius(kilograms) {
        const scaled = 6 + Math.log10(Math.max(kilograms, 1)) * 3;
        return Math.max(6, Math.min(18, scaled));
    };
})();