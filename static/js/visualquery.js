/* =========================================================
   DATAPULSE — VISUALQUERY
   Query Suggestions | Loading | Copy Answer
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const questionInput = document.getElementById("question");
    const queryForm = document.getElementById("vq-form");
    const submitButton = document.getElementById("vq-submit");
    const copyButton = document.getElementById("vq-copy");

    /* =====================================================
       01. SUGGESTED QUESTIONS
    ===================================================== */

    const suggestionButtons = document.querySelectorAll(
        ".vq-suggestion[data-question]"
    );

    suggestionButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const question = this.dataset.question;

            if (!questionInput || !question) return;

            questionInput.value = question;

            questionInput.focus();

            questionInput.dispatchEvent(
                new Event("input", { bubbles: true })
            );

        });

    });


    /* =====================================================
       02. QUERY LOADING STATE
    ===================================================== */

    if (queryForm && submitButton) {

        queryForm.addEventListener("submit", function () {

            if (!questionInput) return;

            const question = questionInput.value.trim();

            if (!question) {

                questionInput.focus();

                return;

            }

            submitButton.disabled = true;

            submitButton.innerHTML = `
                <i class="fas fa-spinner fa-spin"></i>
                <span>Analyzing...</span>
            `;

        });

    }


    /* =====================================================
       03. COPY ANSWER
    ===================================================== */

    if (copyButton) {

        copyButton.addEventListener("click", async function () {

            const answerElement = document.querySelector(".vq-answer");

            const detailsElement = document.querySelector(
                ".vq-answer-details"
            );

            if (!answerElement) return;

            const answer = answerElement.innerText.trim();

            const details = detailsElement
                ? detailsElement.innerText.trim()
                : "";

            const textToCopy = details
                ? answer + "\n" + details
                : answer;

            const originalHTML = copyButton.innerHTML;

            try {

                await navigator.clipboard.writeText(textToCopy);

                copyButton.innerHTML = `
                    <i class="fas fa-check"></i>
                    Copied!
                `;

                copyButton.classList.add("copied");

                setTimeout(function () {

                    copyButton.innerHTML = originalHTML;

                    copyButton.classList.remove("copied");

                }, 2000);

            } catch (error) {

                const temporaryInput = document.createElement("textarea");

                temporaryInput.value = textToCopy;

                temporaryInput.style.position = "fixed";
                temporaryInput.style.opacity = "0";

                document.body.appendChild(temporaryInput);

                temporaryInput.select();

                const successful = document.execCommand("copy");

                temporaryInput.remove();

                if (successful) {

                    copyButton.innerHTML = `
                        <i class="fas fa-check"></i>
                        Copied!
                    `;

                    setTimeout(function () {
                        copyButton.innerHTML = originalHTML;
                    }, 2000);

                } else {

                    alert("Unable to copy answer.");

                }

            }

        });

    }


    /* =====================================================
       04. RESULT SCROLL
    ===================================================== */

    const resultElement = document.querySelector(".vq-result");

    if (resultElement) {

        resultElement.setAttribute("tabindex", "-1");

        resultElement.focus({
            preventScroll: true
        });

    }

});