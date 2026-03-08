/**
 * Career Service API
 * Handles all API calls to the career recommendation service
 */

const CAREER_API = process.env.REACT_APP_CAREER_SERVICE_URL;

if (!CAREER_API) {
	throw new Error("Missing REACT_APP_CAREER_SERVICE_URL in frontend .env");
}

/**
 * Get career recommendations based on user skills
 * @param {string[]} skillIds - Array of skill IDs
 * @param {number} topN - Number of recommendations to return
 * @returns {Promise<Object>} Recommendations response
 */
export async function getCareerRecommendations(skillIds, topN = 5) {
	const response = await fetch(`${CAREER_API}/recommend_careers`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			user_skill_ids: skillIds,
			top_n: topN,
		}),
	});

	if (!response.ok) {
		const body = await response.json().catch(() => ({}));
		throw new Error(body.detail || body.message || "Failed to get recommendations");
	}

	return response.json();
}

/**
 * Get AI-powered explanation for a career recommendation
 * @param {Object} params - Explanation parameters
 * @returns {Promise<Object>} Explanation response
 */
export async function getCareerExplanation({
	roleId,
	roleTitle,
	domain,
	matchScore,
	userSkillIds,
	matchedSkills,
	missingSkills,
	readinessScore,
	nextRole,
	nextRoleTitle,
}) {
	const response = await fetch(`${CAREER_API}/explain_career`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			role_id: roleId,
			role_title: roleTitle,
			domain: domain,
			match_score: matchScore,
			user_skill_ids: userSkillIds,
			matched_skills: matchedSkills,
			missing_skills: missingSkills,
			readiness_score: readinessScore,
			next_role: nextRole,
			next_role_title: nextRoleTitle,
		}),
	});

	if (!response.ok) {
		throw new Error("Failed to get explanation");
	}

	return response.json();
}

/**
 * Predict user's role based on skills
 * @param {string[]} skillIds - Array of skill IDs
 * @returns {Promise<Object>} Prediction response
 */
export async function predictRole(skillIds) {
	const response = await fetch(`${CAREER_API}/predict_role`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			user_skill_ids: skillIds,
		}),
	});

	if (!response.ok) {
		const body = await response.json().catch(() => ({}));
		throw new Error(body.detail || body.message || "Failed to predict role");
	}

	return response.json();
}

/**
 * Check career service health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
	const response = await fetch(`${CAREER_API}/health`);
	return response.json();
}
