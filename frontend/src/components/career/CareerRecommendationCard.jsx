/**
 * Career Recommendation Card Component
 * Displays a single career recommendation with all details
 */
import React from "react";
import { ScoreCircle, ProgressBar } from "./ScoreDisplay";
import { SkillTagList } from "./SkillTags";
import { NextRoleBadge } from "./NextRoleBadge";
import { DomainBadge } from "./DomainBadge";
import { FaStar, FaEye } from "react-icons/fa";

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

  return (
    <div
      className={`p-6 rounded-2xl mb-5 relative transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] ${
        isBestMatch
          ? "bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 border-2 border-purple-300 shadow-xl"
          : "bg-white border-2 border-gray-200 hover:border-purple-300"
      }`}
    >
      {/* Best Match Badge */}
      {isBestMatch && (
        <span className="absolute -top-3 right-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-lg animate-pulse flex items-center gap-1.5">
          <FaStar /> BEST MATCH
        </span>
      )}

      {/* Header: Title, Domain, Score */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-xl font-semibold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent mb-1">
            {rank}. {role_title || role_id}
          </h4>
          <DomainBadge domain={domain} />
        </div>
        <ScoreCircle score={match_score} label="Match Score" />
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <ProgressBar score={match_score} />
      </div>

      {/* Next Career Step */}
      {next_role && (
        <div className="mb-4">
          <NextRoleBadge nextRole={next_role} nextRoleTitle={next_role_title} />
        </div>
      )}

      {/* Skill Gap Display */}
      {skill_gap && (
        <div className="flex gap-4 flex-wrap">
          {/* Readiness */}
          <div className="flex-1 min-w-[120px]">
            <div className="text-xs text-gray-600 mb-1">Readiness</div>
            <div className="font-bold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent">
              {(skill_gap.readiness_score * 100).toFixed(0)}%
            </div>
          </div>

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
        className="mt-5 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-xl text-sm font-semibold flex items-center gap-2 transition-all duration-300 shadow-md hover:shadow-xl hover:scale-105"
      >
        <FaEye /> View Details & AI Explanation
      </button>
    </div>
  );
}
