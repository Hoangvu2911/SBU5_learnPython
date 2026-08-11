(function () {
    function getCookie(name) {
        const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return m ? decodeURIComponent(m[2]) : "";
    }

    function formatError(data) {
        if (!data) return "Request failed";
        if (typeof data.detail === "string") return data.detail;
        if (data.__all__ !== undefined) {
            const v = data.__all__;
            if (Array.isArray(v)) return v.join(", ");
            if (typeof v === "string") return v;
        }
        return Object.entries(data)
            .map(([k, v]) => k + ": " + (Array.isArray(v) ? v.join(", ") : v))
            .join("; ");
    }

    async function api(path, options = {}) {
        const opts = { credentials: "same-origin", ...options };
        const headers = { Accept: "application/json", ...(options.headers || {}) };
        if (opts.body && typeof opts.body === "object" && !(opts.body instanceof FormData)) {
            headers["Content-Type"] = "application/json";
            opts.body = JSON.stringify(opts.body);
        }
        const method = (opts.method || "GET").toUpperCase();
        if (method !== "GET" && method !== "HEAD") {
            headers["X-CSRFToken"] = getCookie("csrftoken");
        }
        opts.headers = headers;

        const url = path.startsWith("/") ? path : "/api" + path;
        const res = await fetch(url, opts);

        if (res.status === 401) {
            window.location.href = "/accounts/login/";
            throw new Error("Unauthorized");
        }
        
        const text = await res.text();
        let data = null;
        if (text) {
            try { data = JSON.parse(text); } catch (e) { data = {detail: text}; }
        }
        if (!res.ok) {
            const err = new Error(formatError(data));
            err.status = res.status;
            err.data = data;
            throw err;
        }
        return data;
    }
    window.cinemaApi = api;
})();