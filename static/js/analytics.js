/* =====================================================
   DATAPULSE — ANALYTICS JAVASCRIPT
   Missing Value Indicators
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // =========================================
    // 01. MISSING VALUE PROGRESS BARS
    // =========================================

    const progressBars = document.querySelectorAll(
        ".missing-progress-fill"
    );

    progressBars.forEach(function (bar) {

        const missing = Number(
            bar.dataset.missing
        );

        const total = Number(
            bar.dataset.total
        );

        let percentage = 0;

        if (total > 0 && Number.isFinite(missing)) {
            percentage = (missing / total) * 100;
        }

        percentage = Math.min(
            100,
            Math.max(0, percentage)
        );

        bar.style.width = percentage + "%";

        // Highlight columns with missing values
        if (missing > 0) {
            bar.classList.add("has-missing-data");
        }

    });


    // =========================================
    // 02. CONSOLE STATUS
    // =========================================

    console.info(
        "DataPulse Analytics initialized successfully."
    );

});