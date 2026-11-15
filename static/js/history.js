document.addEventListener("DOMContentLoaded", function () {

    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this dataset history entry?"
            );

            if (!confirmed) {
                event.preventDefault();
                return;
            }

            const button = form.querySelector("[data-delete]");

            if (button) {
                button.innerHTML =
                    '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...';

                button.disabled = true;
            }

        });

    });

});