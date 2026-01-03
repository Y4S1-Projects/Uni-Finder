/**
 * Career Recommendation Card Component
 * Displays a single career recommendation with all details
 */
import React from "react";
import { ScoreCircle, ProgressBar } from "./ScoreDisplay";
import { SkillTagList } from "./SkillTags";
import { NextRoleBadge } from "./NextRoleBadge";
import { DomainBadge } from "./DomainBadge";

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
          ? "bg-gradient-to-br from-blue-50 via-indigo-50 to-blue-100 border-2 border-blue-300 shadow-xl"
          : "bg-gradient-to-br from-blue-50/60 via-sky-50/70 to-indigo-50/50 border-2 border-blue-200/60 hover:border-blue-300"
      }`}
    >
      {/* Best Match Badge */}
      {isBestMatch && (
        <span className="absolute -top-3 right-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-lg animate-pulse">
          ⭐ BEST MATCH
        </span>
      )}

      {/* Header: Title, Domain, Score */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-xl font-semibold text-blue-800 mb-1">
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
            <div className="text-xs text-gray-500 mb-1">Readiness</div>
            <div className="font-bold text-blue-800">
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
        className="mt-5 px-6 py-3 bg-gradient-to-r from-indigo-400 to-blue-400 hover:from-indigo-500 hover:to-blue-500 text-white rounded-xl text-sm font-semibold flex items-center gap-2 transition-all duration-300 shadow-md hover:shadow-xl hover:scale-105"
      >
        🔍 View Details & AI Explanation
      </button>
    </div>
  );
}
