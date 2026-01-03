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
      style={{
        background: isBestMatch
          ? "linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%)"
          : "#fff",
        border: isBestMatch ? "2px solid #4a90d9" : "1px solid #e5e7eb",
        padding: "1.5rem",
        borderRadius: 12,
        marginBottom: "1rem",
        position: "relative",
      }}
    >
      {/* Best Match Badge */}
      {isBestMatch && (
        <span
          style={{
            position: "absolute",
            top: -10,
            right: 16,
            background: "#4a90d9",
            color: "white",
            padding: "4px 12px",
            borderRadius: 12,
            fontSize: 12,
            fontWeight: "bold",
          }}
        >
          BEST MATCH
        </span>
      )}

      {/* Header: Title, Domain, Score */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "1rem",
        }}
      >
        <div>
          <h4
            style={{
              margin: "0 0 4px 0",
              fontSize: 20,
              color: "#1e40af",
            }}
          >
            {rank}. {role_title || role_id}
          </h4>
          <DomainBadge domain={domain} />
        </div>
        <ScoreCircle score={match_score} label="Match Score" />
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: "1rem" }}>
        <ProgressBar score={match_score} />
      </div>

      {/* Next Career Step */}
      {next_role && (
        <div style={{ marginBottom: "1rem" }}>
          <NextRoleBadge nextRole={next_role} nextRoleTitle={next_role_title} />
        </div>
      )}

      {/* Skill Gap Display */}
      {skill_gap && (
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          {/* Readiness */}
          <div style={{ flex: "1 1 120px" }}>
            <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
              Readiness
            </div>
            <div style={{ fontWeight: "bold", color: "#1e40af" }}>
              {(skill_gap.readiness_score * 100).toFixed(0)}%
            </div>
          </div>

          {/* Matched Skills */}
          <div style={{ flex: "2 1 200px" }}>
            <SkillTagList
              skills={skill_gap.matched_skills}
              variant="matched"
              maxDisplay={5}
            />
          </div>

          {/* Missing Skills */}
          <div style={{ flex: "2 1 200px" }}>
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
        style={{
          marginTop: "1rem",
          padding: "0.5rem 1rem",
          background: "#7c3aed",
          color: "white",
          border: "none",
          borderRadius: 6,
          cursor: "pointer",
          fontSize: 14,
          fontWeight: 500,
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        🔍 View Details & AI Explanation
      </button>
    </div>
  );
}
