/**
 * Career Recommendation Card Component
 * Displays a single career recommendation with all details including
 * readiness score, match score, domain, skill gap, and career progression.
 */
import React from "react";
import { ScoreCircle, ProgressBar } from "./ScoreDisplay";
import { SkillTagList } from "./SkillTags";
import { NextRoleBadge } from "./NextRoleBadge";
import { DomainBadge } from "./DomainBadge";
import {
  FaStar,
  FaEye,
  FaCheckCircle,
  FaExclamationTriangle,
} from "react-icons/fa";

export function CareerRecommendationCard({
  recommendation,
  rank,
  isBestMatch = false,
  onViewDetails,
}) {
  const {
    role_id,
    role_title,
    domain,
    match_score,
    next_role,
    next_role_title,
    skill_gap,
  } = recommendation;

  const readinessPercent = skill_gap
    ? (skill_gap.readiness_score * 100).toFixed(0)
    : null;

  // Color for readiness badge
  const readinessColor =
    readinessPercent >= 70
      ? "from-green-500 to-emerald-500"
      : readinessPercent >= 40
        ? "from-yellow-500 to-orange-400"
        : "from-red-500 to-pink-500";

  return (
    <div
      className={`p-6 rounded-2xl mb-5 relative transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] ${
        isBestMatch
          ? "bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 border-2 border-purple-300 shadow-xl"
          : "bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/60 border-2 border-gray-200 hover:border-purple-300"
      }`}
    >
      {/* Best Match Badge */}
      {isBestMatch && (
        <span className="absolute -top-3 right-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-lg animate-pulse flex items-center gap-1.5">
          <FaStar /> BEST MATCH
        </span>
      )}

      {/* Header: Title, Domain, Scores */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-xl font-semibold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent mb-1">
            {rank}. {role_title || role_id}
          </h4>
          <DomainBadge domain={domain} />
        </div>
        <div className="flex items-center gap-3">
          {/* Readiness Badge */}
          {readinessPercent !== null && (
            <div className="flex flex-col items-center">
              <div
                className={`text-lg font-bold text-white bg-gradient-to-r ${readinessColor} rounded-lg px-3 py-1 shadow-md`}
              >
                {readinessPercent}%
              </div>
              <span className="text-[10px] text-gray-500 mt-0.5">
                Readiness
              </span>
            </div>
          )}
          <ScoreCircle score={match_score} label="Match Score" />
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <ProgressBar score={match_score} />
      </div>

      {/* Quick Stats Row */}
      {skill_gap && (
        <div className="flex gap-3 mb-4 text-xs">
          <span className="flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded-full">
            <FaCheckCircle className="text-green-500" />
            {skill_gap.matched_skills?.length || 0} skills matched
          </span>
          <span className="flex items-center gap-1 bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
            <FaExclamationTriangle className="text-orange-500" />
            {skill_gap.missing_skills?.length || 0} skills to learn
          </span>
        </div>
      )}

      {/* Next Career Step */}
      {next_role && (
        <div className="mb-4">
          <NextRoleBadge nextRole={next_role} nextRoleTitle={next_role_title} />
        </div>
      )}

      {/* Skill Gap Display */}
      {skill_gap && (
        <div className="flex gap-4 flex-wrap">
          {/* Matched Skills */}
          <div className="flex-[2] min-w-[200px]">
            <SkillTagList
              skills={skill_gap.matched_skills}
              variant="matched"
              maxDisplay={5}
            />
          </div>

          {/* Missing Skills */}
          <div className="flex-[2] min-w-[200px]">
            <SkillTagList
              skills={skill_gap.missing_skills}
              variant="missing"
              maxDisplay={5}
            />
          </div>
        </div>
      )}

      {/* View Details Button */}
      <button
        onClick={() => onViewDetails(recommendation)}
        className="mt-5 px-6 py-3 text-white rounded-xl text-sm font-semibold flex items-center gap-2 transition-all duration-300 shadow-md hover:shadow-xl hover:scale-105"
        style={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background =
            "linear-gradient(135deg, #5568d3 0%, #65408b 100%)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background =
            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
        }}
      >
        <FaEye /> View Details & AI Explanation
      </button>
    </div>
  );
}
