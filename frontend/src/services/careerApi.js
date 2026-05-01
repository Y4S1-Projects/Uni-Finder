/**
 * Career Service API
 * Handles all API calls to the career recommendation service
 */

const CAREER_API = process.env.REACT_APP_CAREER_SERVICE_URL;

if (!CAREER_API) {
  throw new Error("Missing REACT_APP_CAREER_SERVICE_URL in frontend .env");
}

/**
 * Get career recommendations based on user skills and profile
 * @param {string[]} skillIds - Array of skill IDs
 * @param {number} topN - Number of recommendations to return
 * @param {Object} careerContext - User profile context for personalized recommendations
 * @param {string} careerContext.experience_level - e.g., "student", "0-1", "1-3", "3-5", "5+"
 * @param {string} careerContext.current_status - e.g., "student", "graduate", "working"
 * @param {string} careerContext.preferred_domain - e.g., "backend_engineering", "ai_ml"
 * @param {string} careerContext.education_level - e.g., "bachelors", "masters"
 * @param {string} careerContext.career_goal - e.g., "first_job", "get_promoted", "switch_career"
 * @returns {Promise<Object>} Recommendations response with score breakdowns
 */
export async function getCareerRecommendations(
  skillIds,
  topN = 5,
  careerContext = {},
) {
  const response = await fetch(`${CAREER_API}/recommend_careers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_skill_ids: skillIds,
      top_n: topN,
      // Include all profile fields for weighted scoring
      experience_level: careerContext.experience_level || null,
      current_status: careerContext.current_status || null,
      preferred_domain: careerContext.preferred_domain || null,
      education_level: careerContext.education_level || null,
      career_goal: careerContext.career_goal || null,
    }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      body.detail || body.message || "Failed to get recommendations",
    );
  }

  return response.json();
}

/**
 * Get AI-powered explanation for a career recommendation (Phase D)
 * Now passes all structured data — score breakdown, explanations, core/supporting/missing skills,
 * seniority, ladder position, confidence, profile source, and user profile.
 * @param {Object} params - Explanation parameters
 * @returns {Promise<Object>} Explanation response with full Phase D payload
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
  // Phase D structured fields
  scoreBreakdown,
  explanations,
  seniority,
  ladderPosition,
  ladderLength,
  confidenceScore,
  matchedCoreSkills,
  matchedSupportingSkills,
  missingCriticalSkills,
  isBestMatch,
  profileSource,
  // User profile
  experienceLevel,
  currentStatus,
  educationLevel,
  careerGoal,
  preferredDomain,
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
      // Phase D
      score_breakdown: scoreBreakdown || null,
      explanations: explanations || null,
      seniority: seniority ?? null,
      ladder_position: ladderPosition ?? null,
      ladder_length: ladderLength ?? null,
      confidence_score: confidenceScore ?? null,
      matched_core_skills: matchedCoreSkills || null,
      matched_supporting_skills: matchedSupportingSkills || null,
      missing_critical_skills: missingCriticalSkills || null,
      is_best_match: isBestMatch ?? null,
      profile_source: profileSource || null,
      // Profile
      experience_level: experienceLevel || null,
      current_status: currentStatus || null,
      education_level: educationLevel || null,
      career_goal: careerGoal || null,
      preferred_domain: preferredDomain || null,
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
