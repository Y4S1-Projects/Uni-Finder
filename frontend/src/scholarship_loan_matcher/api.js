const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

if (!BACKEND_URL) {
	throw new Error("Missing REACT_APP_BACKEND_URL in frontend .env");
}

const BASE_URL = `${BACKEND_URL}/api/scholarships`;
const API_BASE = BACKEND_URL;

export async function requestMatches(profile, options = {}) {
	const { topN = 5, matchType } = options;

	const response = await fetch(`${BASE_URL}/match?topN=${topN}`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			...profile,
			match_type: matchType,
		}),
	});

	if (!response.ok) {
		const errorBody = await response.json().catch(() => ({}));
		const message = errorBody?.message || "Failed to fetch recommendations.";
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
	const response = await fetch(`${API_BASE}/api/update-datasets`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
	});

	if (!response.ok) {
		const errorBody = await response.json().catch(() => ({}));
		const message = errorBody?.error || errorBody?.message || "Failed to update datasets.";
		throw new Error(message);
	}

	return await response.json();
}

export async function getDatasetStats() {
	const response = await fetch(`${API_BASE}/api/update-datasets/stats`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
		},
	});

	if (!response.ok) {
		const errorBody = await response.json().catch(() => ({}));
		const message = errorBody?.error || errorBody?.message || "Failed to fetch dataset stats.";
		throw new Error(message);
	}

	return await response.json();
}
