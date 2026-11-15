/* =====================================================
   DATAPULSE — REPORTS & EXPORT STUDIO
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const exportButtons = document.querySelectorAll(
        "[data-export]"
    );

    exportButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const format = button.dataset.export;

            const text = button.querySelector("span");
            const icon = button.querySelector("i");

            if (!text || !icon) return;

            const originalText = text.textContent;
            const originalIcon = icon.className;

            text.textContent = "Preparing download...";
            icon.className = "fa-solid fa-spinner fa-spin";

            button.style.pointerEvents = "none";
            button.style.opacity = "0.75";

            /*
             * Restore the button after the download
             * request has had time to start.
             */

            setTimeout(function () {

                text.textContent = originalText;
                icon.className = originalIcon;

                button.style.pointerEvents = "";
                button.style.opacity = "";

            }, 2500);

            console.log(
                "DataPulse export requested:",
                format.toUpperCase()
            );

        });

    });

});