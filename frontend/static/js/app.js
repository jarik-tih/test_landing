import { validatePhone, getDigits } from "./validators.js";
import { buildLeadPayload } from "./analytics.js";
import { sendLead } from "./api.js";

const DUPLICATE_WINDOW_MS = 10 * 60 * 1000;

const DUPLICATE_MESSAGE =
    "Мы уже получили заявку с этого номера. Скоро вам позвоним.";

const FALLBACK_NETWORK_ERROR =
    "Нет соединения. Позвоните нам: +375 29 123-45-67.";

const form = document.querySelector("#lead-form");

if (form) {
    initializeLeadForm(form);
}

function initializeLeadForm(form) {
    const phone = form.elements.namedItem("phone");
    const statusBox = form.querySelector(".form-status");
    const submitButton = form.querySelector('button[type="submit"]');
    const submitLabel = form.querySelector(".button-label");

    let sending = false;
    let conversionSource = "direct_form";

    function setStatus(message, type = "") {
        statusBox.textContent = message;
        statusBox.className = `form-status ${type}`;
    }

    function isDuplicateSubmission(digits) {
        const key = `kvarta:${digits.slice(-9)}`;
        const lastSent = Number(sessionStorage.getItem(key) || 0);

        return Date.now() - lastSent < DUPLICATE_WINDOW_MS;
    }

    function rememberSubmission(digits) {
        const key = `kvarta:${digits.slice(-9)}`;

        sessionStorage.setItem(key, String(Date.now()));
    }

    function startSending() {
        sending = true;
        submitButton.disabled = true;
        submitLabel.textContent = "Отправляем…";
        setStatus("");
    }

    function stopSending() {
        sending = false;
        submitButton.disabled = false;
        submitLabel.textContent = "Отправить заявку";
    }

    phone.addEventListener("input", () => {
        phone.setCustomValidity("");
        phone.classList.remove("invalid");
    });

    document.addEventListener("click", (event) => {
        const link = event.target.closest("[data-lead-source]");

        if (!link) {
            return;
        }

        conversionSource = link.dataset.leadSource;
    });

    document.querySelectorAll("[data-interest]").forEach((link) => {
        link.addEventListener("click", () => {
            form.elements.namedItem("interest").value =
                link.dataset.interest;
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (sending) {
            return;
        }

        const formData = new FormData(form);
        const phoneValue = formData.get("phone");

        if (!validatePhone(phoneValue)) {
            phone.setCustomValidity(
                "Введите белорусский номер, например +375 29 123-45-67."
            );
            phone.reportValidity();
            phone.classList.add("invalid");
            return;
        }

        const digits = getDigits(phoneValue);

        if (isDuplicateSubmission(digits)) {
            setStatus(DUPLICATE_MESSAGE, "error");
            return;
        }

        const payload = buildLeadPayload(
            formData,
            conversionSource
        );

        startSending();

        try {
            const result = await sendLead(payload);

            rememberSubmission(digits);
            form.reset();

            setStatus(
                result.message || "Заявка успешно отправлена!",
                "success"
            );
        } catch (error) {
            setStatus(
                error.message || FALLBACK_NETWORK_ERROR,
                "error"
            );
        } finally {
            stopSending();
        }
    });
}