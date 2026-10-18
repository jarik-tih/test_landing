export const PHONE_PATTERN =
    /^(?:\+375|80)\s*\(?\d{2}\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}$/;

export const PHONE_ERROR_MESSAGE =
    "Введите белорусский номер, например +375 29 123-45-67.";

export function normalizePhone(value) {
    return String(value).trim();
}

export function getDigits(value) {
    return String(value).replace(/\D/g, "");
}

export function validatePhone(value) {
    return PHONE_PATTERN.test(normalizePhone(value));
}