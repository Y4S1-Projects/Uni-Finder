/**
 * Skill Tags Component
 * Displays skills as colored tags
 */
import React from "react";

const SKILL_STYLES = {
  matched: {
    tagClass: "bg-green-100 text-green-800",
    label: "✅ Skills You Have",
    labelClass: "text-green-600",
  },
  missing: {
    tagClass: "bg-amber-100 text-amber-800",
    label: "📚 Skills to Learn",
    labelClass: "text-yellow-600",
  },
};

export function SkillTag({ skill, variant = "matched", size = "small" }) {
  const style = SKILL_STYLES[variant];
  const sizeClasses =
    size === "large" ? "px-3 py-1.5 text-sm" : "px-2 py-0.5 text-xs";

  // Handle both string and object skills
  const skillName = typeof skill === "object" ? skill.name || skill.id : skill;

  return (
    <span className={`${style.tagClass} ${sizeClasses} rounded-full`}>
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
        <div className={`text-xs ${style.labelClass} mb-1`}>
          {style.label} ({skills.length})
        </div>
      )}
      <div className={`flex flex-wrap ${size === "large" ? "gap-2" : "gap-1"}`}>
        {skills.slice(0, maxDisplay).map((skill, index) => (
          <SkillTag
            key={typeof skill === "object" ? skill.id : skill || index}
            skill={skill}
            variant={variant}
            size={size}
          />
        ))}
        {skills.length > maxDisplay && (
          <span className="text-xs text-gray-500">
            +{skills.length - maxDisplay} more
          </span>
        )}
      </div>
    </div>
  );
}
