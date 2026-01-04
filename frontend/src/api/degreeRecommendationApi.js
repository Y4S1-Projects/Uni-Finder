import axios from "axios";

const DEGREE_SERVICE_URL = process.env.REACT_APP_DEGREE_SERVICE_URL;

if (!DEGREE_SERVICE_URL) {
	throw new Error("Missing REACT_APP_DEGREE_SERVICE_URL in frontend .env");
}

/**
 * @typedef {Object} StudentProfile
 * @property {string} stream
 * @property {string[]} subjects
 * @property {number} zscore
 * @property {string} interests
 */

/**
 * @typedef {Object} DegreeRecommendationRequest
 * @property {StudentProfile} student
 * @property {string} district
 * @property {number=} max_results
 */

/**
 * Calls Degree Recommendation Service directly.
 * Service route: POST /recommend
 *
 * @param {DegreeRecommendationRequest} payload
 */
export async function fetchDegreeRecommendations(payload) {
	const response = await axios.post(`${DEGREE_SERVICE_URL}/recommend`, payload);
	return response.data;
}
