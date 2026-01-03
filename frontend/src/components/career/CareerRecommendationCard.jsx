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
      className={`p-6 rounded-xl mb-4 relative ${
        isBestMatch
          ? "bg-gradient-to-br from-blue-50 to-sky-50 border-2 border-blue-400"
          : "bg-white border border-gray-200"
      }`}
    >
      {/* Best Match Badge */}
      {isBestMatch && (
        <span className="absolute -top-2.5 right-4 bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold">
          BEST MATCH
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
        className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md text-sm font-medium flex items-center gap-1.5 transition-colors"
      >
        🔍 View Details & AI Explanation
      </button>
    </div>
  );
}
