document.addEventListener("DOMContentLoaded", function () {

    const chartType = document.getElementById("chart_type");
    const xColumn = document.getElementById("x_column");
    const yColumn = document.getElementById("y_column");
    const yField = document.getElementById("yField");
    const chartHint = document.getElementById("chartHint");
    const visualForm = document.getElementById("visualForm");
    const generateButton = document.getElementById("generateButton");

    if (!chartType || !xColumn || !yColumn) return;

    const hints = {
        bar: "Bar charts compare numerical values across categories.",
        line: "Line charts show trends and changes across ordered values.",
        scatter: "Scatter plots explore relationships between two numerical columns.",
        histogram: "Histograms show the frequency distribution of numerical values."
    };

    function updateChartFields() {

        const type = chartType.value;

        const isHistogram = type === "histogram";
        const isScatter = type === "scatter";

        yField.style.display = isHistogram ? "none" : "block";
        yColumn.required = !isHistogram;

        Array.from(xColumn.options).forEach(function (option) {

            if (!option.value) return;

            const isNumeric = option.dataset.numeric === "true";

            option.disabled = (isHistogram || isScatter) && !isNumeric;

        });

        const selectedOption = xColumn.options[xColumn.selectedIndex];

        if (
            selectedOption &&
            selectedOption.disabled
        ) {
            xColumn.value = "";
        }

        if (chartHint) {
            chartHint.querySelector("span").textContent = hints[type];
        }
    }

    chartType.addEventListener("change", updateChartFields);

    visualForm.addEventListener("submit", function (event) {

        if (!xColumn.value) {
            event.preventDefault();
            alert("Please select an X-axis column.");
            return;
        }

        if (
            chartType.value !== "histogram" &&
            !yColumn.value
        ) {
            event.preventDefault();
            alert("Please select a Y-axis numerical column.");
            return;
        }

        if (generateButton) {
            generateButton.disabled = true;
            generateButton.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Generating Chart...';
        }

    });

    updateChartFields();

});