const FALLBACK_SEND_ERROR =
    "Не удалось отправить заявку. Позвоните нам по номеру +375 29 123-45-67.";

export async function sendLead(payload) {
    const response = await fetch("/api/lead", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error(FALLBACK_SEND_ERROR);
    }

    if (!response.ok) {
        throw new Error(result.message || FALLBACK_SEND_ERROR);
    }

    return result;
}