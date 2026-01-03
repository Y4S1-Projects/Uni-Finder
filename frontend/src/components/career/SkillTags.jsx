/**
 * Skill Tags Component
 * Displays skills as colored tags
 */
import React from "react";

const SKILL_STYLES = {
  matched: {
    background: "#d1fae5",
    color: "#065f46",
    label: "✅ Skills You Have",
    labelColor: "#059669",
  },
  missing: {
    background: "#fef3c7",
    color: "#92400e",
    label: "📚 Skills to Learn",
    labelColor: "#ca8a04",
  },
};

export function SkillTag({ skill, variant = "matched", size = "small" }) {
  const style = SKILL_STYLES[variant];
  const padding = size === "large" ? "6px 12px" : "2px 8px";
  const fontSize = size === "large" ? 13 : 11;

  // Handle both string and object skills
  const skillName = typeof skill === "object" ? skill.name || skill.id : skill;

  return (
    <span
      style={{
        background: style.background,
        padding,
        borderRadius: 12,
        fontSize,
        color: style.color,
      }}
    >
      {skillName}
    </span>
  );
}

export function SkillTagList({
  skills,
  variant = "matched",
  maxDisplay = 5,
  size = "small",
  showLabel = true,
}) {
  const style = SKILL_STYLES[variant];

  if (!skills || skills.length === 0) return null;

  return (
    <div>
      {showLabel && (
        <div
          style={{
            fontSize: 12,
            color: style.labelColor,
            marginBottom: 4,
          }}
        >
          {style.label} ({skills.length})
        </div>
      )}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: size === "large" ? 8 : 4,
        }}
      >
        {skills.slice(0, maxDisplay).map((skill, index) => (
          <SkillTag
            key={typeof skill === "object" ? skill.id : skill || index}
            skill={skill}
            variant={variant}
            size={size}
          />
        ))}
        {skills.length > maxDisplay && (
          <span style={{ fontSize: 11, color: "#666" }}>
            +{skills.length - maxDisplay} more
          </span>
        )}
      </div>
    </div>
  );
}
