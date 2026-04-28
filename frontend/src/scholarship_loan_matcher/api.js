const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const MATCHER_SERVICE_URL_RAW =
	process.env.REACT_APP_SCHOLARSHIP_MATCHER_URL || process.env.REACT_APP_SCHOLARSHIP_SERVICE_URL || null;
const MATCHER_SERVICE_URL = MATCHER_SERVICE_URL_RAW ? MATCHER_SERVICE_URL_RAW.replace(/\/+$/, "") : null;

if (!BACKEND_URL) {
	throw new Error("Missing REACT_APP_BACKEND_URL in frontend .env");
}

// If a dedicated matcher service URL is configured, call it directly.
// Otherwise, fall back to the Node backend route for compatibility.
const MATCH_BASE = (MATCHER_SERVICE_URL || `${BACKEND_URL}/api/scholarships`).replace(/\/+$/, "");
const API_BASE = BACKEND_URL;

// Dataset update & stats: when REACT_APP_SCHOLARSHIP_MATCHER_URL is set, these
// call the scholarship service directly so admin can run update/stats without Node.
// Matcher service must expose: POST /matcher/update-datasets, GET /matcher/update-datasets/stats
// with the same JSON shape as the Node backend (success, updated_at, summary; success, scholarships, loans, last_updated).
const DATASET_API_BASE = MATCHER_SERVICE_URL || API_BASE;
const DATASET_UPDATE_PATH = MATCHER_SERVICE_URL ? "/matcher/update-datasets" : "/api/update-datasets";
const DATASET_STATS_PATH = MATCHER_SERVICE_URL ? "/matcher/update-datasets/stats" : "/api/update-datasets/stats";

export async function requestMatches(profile, options = {}) {
	const { topN = 5, matchType } = options;

	const response = await fetch(`${MATCH_BASE}/match`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			profile: {
				...profile,
				match_type: matchType,
			},
			top_n: topN,
			match_type: matchType,
		}),
	});

	if (!response.ok) {
		const errorBody = await response.json().catch(() => ({}));
		const message = errorBody?.detail || errorBody?.message || "Failed to fetch recommendations.";
		throw new Error(message);
	}

	const payload = await response.json();
	const matches = payload.matches || [];

	if (!matchType) {
		return matches;
	}

	return matches.filter((item) => {
		if (!item?.record_type) {
			return false;
		}
		return item.record_type.toLowerCase() === matchType.toLowerCase();
	});
}

export async function triggerDatasetUpdate() {
	const response = await fetch(`${DATASET_API_BASE}${DATASET_UPDATE_PATH}`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
	});

	if (!response.ok) {
		let message = "Failed to update datasets.";
		const contentType = response.headers.get("content-type") || "";
		if (contentType.includes("application/json")) {
			const errorBody = await response.json().catch(() => ({}));
			message =
				errorBody?.detail ||
				errorBody?.error ||
				errorBody?.message ||
				message;
		} else {
			const errorText = await response.text().catch(() => "");
			if (errorText) message = errorText;
		}
		throw new Error(message);
	}

	return await response.json();
}

export async function getDatasetStats() {
	const response = await fetch(`${DATASET_API_BASE}${DATASET_STATS_PATH}`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
		},
	});

	if (!response.ok) {
		let message = "Failed to fetch dataset stats.";
		const contentType = response.headers.get("content-type") || "";
		if (contentType.includes("application/json")) {
			const errorBody = await response.json().catch(() => ({}));
			message =
				errorBody?.detail ||
				errorBody?.error ||
				errorBody?.message ||
				message;
		} else {
			const errorText = await response.text().catch(() => "");
			if (errorText) message = errorText;
		}
		throw new Error(message);
	}

	return await response.json();
}
