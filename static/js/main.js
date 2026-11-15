
/* =====================================================
   DATAPULSE — MAIN JAVASCRIPT
   Sidebar | Page Animation | Flash Messages
===================================================== */


document.addEventListener("DOMContentLoaded", function () {


    /* =========================================
       1. SIDEBAR TOGGLE
    ========================================= */

    const sidebar = document.querySelector(".app-sidebar");

    const toggle = document.getElementById("sidebarToggle");


    if (sidebar && toggle) {

        toggle.addEventListener("click", function (event) {

            event.stopPropagation();

            sidebar.classList.toggle("open");

        });


        /* Close sidebar when clicking outside */

        document.addEventListener("click", function (event) {

            if (
                window.innerWidth <= 768 &&
                !sidebar.contains(event.target) &&
                !toggle.contains(event.target)
            ) {

                sidebar.classList.remove("open");

            }

        });


        /* Close sidebar after selecting a menu item */

        sidebar.querySelectorAll(".sidebar-link").forEach(link => {

            link.addEventListener("click", function () {

                if (window.innerWidth <= 768) {

                    sidebar.classList.remove("open");

                }

            });

        });

    }


    /* =========================================
       2. PAGE ENTRANCE ANIMATION
    ========================================= */

    document.body.classList.add("page-loaded");


    /* =========================================
       3. FLASH MESSAGE AUTO HIDE
    ========================================= */

    document.querySelectorAll(".flash-message").forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";

            message.style.transform = "translateY(-5px)";

            message.style.transition =
                "opacity 0.4s ease, transform 0.4s ease";


            setTimeout(function () {

                message.remove();

            }, 400);

        }, 4500);

    });


    /* =========================================
       4. WINDOW RESIZE HANDLING
    ========================================= */

    window.addEventListener("resize", function () {

        if (window.innerWidth > 768 && sidebar) {

            sidebar.classList.remove("open");

        }

    });


    /* =========================================
       5. INITIALIZATION
    ========================================= */

    console.log(
        "DataPulse main application initialized."
    );

});
