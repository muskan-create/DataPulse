/* =========================================================
   DATAPULSE — COMPARISON PAGE INTERACTIONS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const dataset1 = document.getElementById("dataset1");
    const dataset2 = document.getElementById("dataset2");

    const fileName1 = document.getElementById("file-name-1");
    const fileName2 = document.getElementById("file-name-2");

    const form = document.getElementById("comparison-form");
    const button = document.getElementById("compare-button");


    // Display selected file names
    function showFileName(input, output) {

        if (!input || !output) return;

        input.addEventListener("change", function () {

            if (input.files.length > 0) {

                output.textContent = input.files[0].name;

            } else {

                output.textContent = "No file selected";

            }

        });

    }

    showFileName(dataset1, fileName1);
    showFileName(dataset2, fileName2);


    // Form validation and loading state
    if (form) {

        form.addEventListener("submit", function (event) {

            if (
                !dataset1.files.length ||
                !dataset2.files.length
            ) {

                event.preventDefault();

                alert("Please select both datasets.");

                return;
            }

            button.disabled = true;

            button.innerHTML = `
                <span>Comparing Datasets...</span>
                <span>⏳</span>
            `;

        });

    }

});