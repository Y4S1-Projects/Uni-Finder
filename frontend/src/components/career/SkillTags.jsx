/**
 * Skill Tags Component
 * Displays skills as colored tags
 */
import React from "react";
import { FaCheckCircle, FaBookOpen } from "react-icons/fa";

const SKILL_STYLES = {
  matched: {
    tagClass:
      "bg-gradient-to-r from-purple-100 to-blue-100 text-purple-900 border border-purple-300 shadow-sm hover:shadow-md transition-all duration-200",
    label: "Skills You Have",
    labelClass: "text-purple-700 font-semibold flex items-center gap-1.5",
    icon: FaCheckCircle,
  },
  missing: {
    tagClass:
      "bg-gray-100 text-gray-700 border border-gray-300 shadow-sm hover:shadow-md transition-all duration-200",
    label: "Skills to Learn",
    labelClass: "text-gray-700 font-semibold flex items-center gap-1.5",
    icon: FaBookOpen,
  },
};

export function SkillTag({ skill, variant = "matched", size = "small" }) {
  const style = SKILL_STYLES[variant];
  const sizeClasses =
    size === "large"
      ? "px-3 py-1 text-xs font-medium"
      : "px-2 py-0.5 text-[10px] font-medium";

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
          <style.icon /> {style.label} ({skills.length})
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
