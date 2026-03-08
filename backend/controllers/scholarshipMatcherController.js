// Proxy controller for scholarship service
export const matchScholarships = async (req, res, next) => {
	try {
		const scholarshipServiceUrl = process.env.SCHOLARSHIP_SERVICE_URL || "http://unifinder-scholarship-service:5005";
		const topN = req.query.topN || 5;
		
		// Forward the request to the scholarship service
		const response = await fetch(`${scholarshipServiceUrl}/api/scholarships/match?topN=${topN}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(req.body),
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
