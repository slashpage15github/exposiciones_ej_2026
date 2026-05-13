(function () {
    const regionSelect = document.getElementById("region-filter");
    const drugSelect = document.getElementById("drug-filter");
    const statusNode = document.getElementById("filter-status");
    const resetButton = document.getElementById("filter-reset");

    function resetOptions(selectNode) {
        while (selectNode.options.length > 1) {
            selectNode.remove(1);
        }
    }

    function fillSelect(selectNode, values, label) {
        resetOptions(selectNode);

        values.forEach((value) => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            selectNode.appendChild(option);
        });

        selectNode.setAttribute("aria-label", label);
    }

    window.createGeoFilters = function createGeoFilters(points, onChange) {
        if (!regionSelect || !drugSelect || !statusNode || !resetButton) {
            return;
        }

        const regions = [...new Set(points.map((point) => point.region))].sort();
        const drugTypes = [...new Set(points.map((point) => point.drugName))].sort();

        fillSelect(regionSelect, regions, "Filtrar por región");
        fillSelect(drugSelect, drugTypes, "Filtrar por tipo de droga");

        function applyFilters() {
            const region = regionSelect.value;
            const drugName = drugSelect.value;
            const filteredPoints = points.filter((point) => {
                const matchesRegion = region === "all" || point.region === region;
                const matchesDrug = drugName === "all" || point.drugName === drugName;
                return matchesRegion && matchesDrug;
            });

            const countryCount = new Set(filteredPoints.map((point) => point.countryCode)).size;

            const regionLabel = region === "all" ? "todas las regiones" : region;
            const drugLabel = drugName === "all" ? "todos los tipos" : drugName;
            statusNode.textContent = `Mostrando ${filteredPoints.length} registro(s) en ${countryCount} marcador(es) de país para ${regionLabel} y ${drugLabel}.`;
            onChange(filteredPoints, { region, drugName });
        }

        regionSelect.addEventListener("change", applyFilters);
        drugSelect.addEventListener("change", applyFilters);
        resetButton.addEventListener("click", () => {
            regionSelect.value = "all";
            drugSelect.value = "all";
            applyFilters();
        });

        applyFilters();
    };

    window.setGeoFilterStatus = function setGeoFilterStatus(message) {
        if (statusNode) {
            statusNode.textContent = message;
        }
    };
})();