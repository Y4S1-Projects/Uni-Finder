const API_PATH = "/api/career-profiles";

function getApiBaseUrl() {
  const configuredOrigin =
    process.env.REACT_APP_API_BASE_URL || process.env.REACT_APP_BACKEND_URL;
  const runtimeOrigin =
    typeof window !== "undefined" && window.location?.origin
      ? window.location.origin
      : "";
  const origin = (configuredOrigin || runtimeOrigin).replace(/\/+$/, "");

  if (origin.endsWith(API_PATH)) return origin;
  if (origin.endsWith("/api")) return `${origin}/career-profiles`;
  return `${origin}${API_PATH}`;
}

const API_BASE_URL = getApiBaseUrl();

async function request(path = "", options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    const message =
      data?.message || data?.error || response.statusText || "Request failed";
    const error = new Error(message);
    error.status = response.status;
    error.payload = data;
    throw error;
  }

  return data?.data ?? data;
}

export function getProfiles() {
  return request("");
}

export function getProfileById(profileId) {
  return request(`/${profileId}`);
}

export function createProfile(payload) {
  return request("", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProfile(profileId, payload) {
  return request(`/${profileId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteProfile(profileId) {
  return request(`/${profileId}`, {
    method: "DELETE",
  });
}
