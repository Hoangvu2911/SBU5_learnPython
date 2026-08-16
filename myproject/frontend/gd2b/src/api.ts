const API_BASE = "http://localhost:8000";

export async function api<T>(path: string, options?: RequestInit,): Promise<T> {
    const url = path.startsWith("http") ? path : API_BASE + path;

    const res = await fetch(url, {
        ...options,
        headers: { "Accept": "application/json", ...options?.headers },
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
    return data as T;
}