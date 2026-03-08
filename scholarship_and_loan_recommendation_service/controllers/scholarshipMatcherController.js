export const matchScholarships = async (req, res) => {
	try {
		const profile = req.body || {};
		const topN = Number(req.query.topN) || 5;
		const matchType = profile.match_type || req.query.matchType || null;

		if (!Object.keys(profile).length) {
			return res.status(400).json({ message: "Student profile payload is required." });
		}

		const baseUrl = process.env.SCHOLARSHIP_MATCHER_SERVICE_URL || "http://127.0.0.1:5005";
		const url = new URL("/match", baseUrl);
		url.searchParams.set("top_n", String(topN));
		if (matchType) {
			url.searchParams.set("match_type", String(matchType));
		}

		const response = await fetch(url.toString(), {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ profile }),
		});

		if (!response.ok) {
			let detail = "Matcher service request failed.";
			try {
				const errorBody = await response.json();
				detail = errorBody?.detail || errorBody?.message || detail;
			} catch (_) {
				// ignore JSON parse error
			}
			throw new Error(detail);
		}

		const payload = await response.json();
		const matches = Array.isArray(payload.matches) ? payload.matches : [];

		return res.json({ matches, count: matches.length });
	} catch (error) {
		console.error("Scholarship matcher error:", error);
		return res.status(500).json({
			message: "Unable to fetch scholarship matches at this time.",
			error: error.message,
		});
	}
};
