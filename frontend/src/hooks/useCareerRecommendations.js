/**
 * Custom hook for career recommendations logic
 */
import { useState, useCallback } from "react";
import {
  getCareerRecommendations,
  getCareerExplanation,
} from "../services/careerApi";

export function useCareerRecommendations() {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = useCallback(async (skillIds, topN = 5) => {
    if (!skillIds || skillIds.length === 0) {
      setError("Please select at least one skill");
      return null;
    }

    setLoading(true);
    setError(null);
    setRecommendations(null);

    try {
      const data = await getCareerRecommendations(skillIds, topN);
      setRecommendations(data);
      return data;
    } catch (err) {
      setError(err.message || String(err));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearRecommendations = useCallback(() => {
    setRecommendations(null);
    setError(null);
  }, []);

  return {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    clearRecommendations,
  };
}

export function useCareerDetail() {
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetail, setJobDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchJobDetail = useCallback(async (recommendation, userSkillIds) => {
    setSelectedJob(recommendation);
    setDetailLoading(true);
    setJobDetail(null);

    // Extract skill IDs (skills may be objects {id, name} or strings)
    const extractSkillIds = (skills) =>
      (skills || []).map((s) => (typeof s === "object" ? s.id : s));

    try {
      const data = await getCareerExplanation({
        roleId: recommendation.role_id,
        roleTitle: recommendation.role_title,
        domain: recommendation.domain,
        matchScore: recommendation.match_score,
        userSkillIds: userSkillIds,
        matchedSkills: extractSkillIds(
          recommendation.skill_gap?.matched_skills
        ),
        missingSkills: extractSkillIds(
          recommendation.skill_gap?.missing_skills
        ),
        readinessScore: recommendation.skill_gap?.readiness_score || 0,
        nextRole: recommendation.next_role,
        nextRoleTitle: recommendation.next_role_title,
      });
      setJobDetail(data);
      return data;
    } catch (err) {
      console.error(err);
      // Fallback to basic detail without AI explanation
      // Skills from recommendation are already {id, name} objects
      const normalizeSkills = (skills) =>
        (skills || []).map((s) =>
          typeof s === "object" ? s : { id: s, name: s }
        );

      const fallbackDetail = {
        ...recommendation,
        matched_skills: normalizeSkills(
          recommendation.skill_gap?.matched_skills
        ),
        missing_skills: normalizeSkills(
          recommendation.skill_gap?.missing_skills
        ),
        readiness_score: recommendation.skill_gap?.readiness_score || 0,
        explanation: null,
      };
      setJobDetail(fallbackDetail);
      return fallbackDetail;
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const closeDetail = useCallback(() => {
    setSelectedJob(null);
    setJobDetail(null);
  }, []);

  return {
    selectedJob,
    jobDetail,
    detailLoading,
    fetchJobDetail,
    closeDetail,
  };
}
