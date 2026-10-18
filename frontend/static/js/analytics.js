export function collectUtmParams() {
    const params = new URLSearchParams(window.location.search);

    const keys = [
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
    ];

    return Object.fromEntries(
        keys.map((key) => [key, params.get(key) || ""])
    );
}

export function buildLeadPayload(formData, conversionSource) {
    return {
        ...Object.fromEntries(formData.entries()),
        source: conversionSource,
        ...collectUtmParams(),
        landing: window.location.href,
        referrer: document.referrer || "",
    };
}