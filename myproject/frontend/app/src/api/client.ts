const TOKEN_KEY = "auth-token";

export async function api<T>(url: string, options?: RequestInit): Promise<T> {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers = new Headers(options?.headers);
    headers.set("Accept", "application/json");
    if (token) headers.set("Authorization", `Token ${token}`);
    if (options?.body && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const res = await fetch(url, {...options, headers});
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