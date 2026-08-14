const API_BASE = "http://localhost:8000";

export async function api(path) {
    const url = path.startsWith("http") ? path : API_BASE + path;

    const res = await fetch(url, {
        headers: { "Accept": "application/json" },
    });

    const text = await res.text();
    let data = null;
    if (text) {
        try {
            data = JSON.parse(text);
        } catch (e) {
            data = { detail: text };
        }
    }

    if (!res.ok) {
        const msg = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status} error`;
        throw new Error(msg);
    }
    return data;
}