const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:3000/api/v1";
export async function fetchPowerBiEmbed() {
    const token = localStorage.getItem("accessToken");
    const response = await fetch(`${API_BASE}/analytics/powerbi/embed`, {
        headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : ""
        }
    });
    const data = (await response.json());
    if (!response.ok) {
        throw new Error(data.message ?? `Request failed: ${response.status}`);
    }
    return data;
}
export async function apiGet(path) {
    const token = localStorage.getItem("accessToken");
    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : ""
        }
    });
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
}
export async function login(email, password) {
    let response;
    try {
        response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
    }
    catch {
        throw new Error(`Cannot reach API at ${API_BASE}. Is the backend running (e.g. npm start on port 3000)?`);
    }
    const json = (await response.json().catch(() => ({})));
    if (!response.ok) {
        throw new Error(json.message || "Invalid username or password");
    }
    if (!json.accessToken) {
        throw new Error("Login response missing token");
    }
    localStorage.setItem("accessToken", json.accessToken);
}
export async function apiPost(path, body) {
    const token = localStorage.getItem("accessToken");
    const response = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify(body)
    });
    if (!response.ok) {
        const json = await response.json().catch(() => ({}));
        throw new Error(json.message ?? `Request failed: ${response.status}`);
    }
    return response.json();
}
export async function apiPatch(path, body) {
    const token = localStorage.getItem("accessToken");
    const response = await fetch(`${API_BASE}${path}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify(body)
    });
    if (!response.ok) {
        const json = await response.json().catch(() => ({}));
        throw new Error(json.message ?? `Request failed: ${response.status}`);
    }
    return response.json();
}
