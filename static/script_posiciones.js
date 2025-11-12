document.addEventListener("DOMContentLoaded", function () {
    fetch("/static/posiciones.json")
        .then(response => response.json())
        .then(data => {
            const areaSelect = document.getElementById("area");
            const positionSelect = document.getElementById("position");

            Object.keys(data).forEach(area => {
                const option = document.createElement("option");
                option.value = area;
                option.textContent = area;
                areaSelect.appendChild(option);
            });

            window.actualizarPosiciones = function () {
                const areaSeleccionada = areaSelect.value;
                positionSelect.innerHTML = '<option value="">' + (positionSelect.getAttribute("data-placeholder") || "Select a position") + '</option>';

                if (data[areaSeleccionada]) {
                    data[areaSeleccionada].forEach(posicion => {
                        const option = document.createElement("option");
                        option.value = posicion;
                        option.textContent = posicion;
                        positionSelect.appendChild(option);
                    });
                }
            };

            areaSelect.addEventListener("change", actualizarPosiciones);
        })
        .catch(error => console.error("Error loading JSON:", error));
});
