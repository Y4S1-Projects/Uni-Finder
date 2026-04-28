// Proxy controller for scholarship service
export const matchScholarships = async (req, res, next) => {
	try {
		const scholarshipServiceUrl = (
			process.env.SCHOLARSHIP_SERVICE_URL || "http://localhost:5005"
		).replace(/\/+$/, "");
		const topN = Number(req.query.topN) || 5;
		const matchType = req.body?.match_type || req.query?.matchType || null;

		// Scholarship service expects request envelope: { profile, top_n, match_type }
		const response = await fetch(`${scholarshipServiceUrl}/match`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				profile: req.body || {},
				top_n: topN,
				match_type: matchType,
			}),
		});

		if (!response.ok) {
			const errorText = await response.text();
			return res.status(response.status).json({
				success: false,
				message: `Scholarship service error: ${errorText}`,
			});
		}

		const data = await response.json();
		return res.status(200).json(data);
	} catch (error) {
		next(error);
	}
};
