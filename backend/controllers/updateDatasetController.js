// Proxy controller for dataset update operations
export const triggerUpdate = async (req, res, next) => {
	try {
		const scholarshipServiceUrl = process.env.SCHOLARSHIP_SERVICE_URL || "http://unifinder-scholarship-service:5005";
		
		const response = await fetch(`${scholarshipServiceUrl}/api/update-datasets`, {
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
				error: `Dataset update service error: ${errorText}`,
			});
		}

		const data = await response.json();
		return res.status(200).json(data);
	} catch (error) {
		next(error);
	}
};

export const getStats = async (req, res, next) => {
	try {
		const scholarshipServiceUrl = process.env.SCHOLARSHIP_SERVICE_URL || "http://unifinder-scholarship-service:5005";
		
		const response = await fetch(`${scholarshipServiceUrl}/api/update-datasets/stats`, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
		});

		if (!response.ok) {
			const errorText = await response.text();
			return res.status(response.status).json({
				success: false,
				error: `Dataset stats service error: ${errorText}`,
			});
		}

		const data = await response.json();
		return res.status(200).json(data);
	} catch (error) {
		next(error);
	}
};
