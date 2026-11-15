document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("dataset-file");
    const fileName = document.getElementById("file-name");

    if (fileInput && fileName) {

        fileInput.addEventListener("change", function () {

            if (this.files.length > 0) {
                fileName.textContent = "Selected: " + this.files[0].name;
            } else {
                fileName.textContent = "No file selected";
            }

        });

    }

});