/**
 * Domain Badge Component
 * Displays the career domain as a styled badge
 */
import React from "react";

const DOMAIN_CLASSES = {
  SOFTWARE_ENGINEERING:
    "bg-indigo-50 text-indigo-700 border border-indigo-200",
  DATA: "bg-indigo-50 text-indigo-700 border border-indigo-200",
  AI_ML:
    "bg-indigo-50 text-indigo-700 border border-indigo-200",
  DEVOPS:
    "bg-indigo-50 text-indigo-700 border border-indigo-200",
  QA: "bg-gray-50 text-gray-700 border border-gray-200",
  MOBILE:
    "bg-indigo-50 text-indigo-700 border border-indigo-200",
  UI_UX:
    "bg-indigo-50 text-indigo-700 border border-indigo-200",
  default:
    "bg-gray-50 text-gray-700 border border-gray-200",
};

export function DomainBadge({ domain, size = "small" }) {
  if (!domain) return null;

  const colorClass = DOMAIN_CLASSES[domain] || DOMAIN_CLASSES.default;
  const sizeClasses =
    size === "large"
      ? "px-3 py-1 text-sm rounded-md"
      : "px-2 py-0.5 text-xs rounded";

  return (
    <span
      className={`${colorClass} ${sizeClasses} font-semibold shadow-sm hover:shadow-md transition-all duration-200`}
    >
      {domain.replace(/_/g, " ")}
    </span>
  );
}
