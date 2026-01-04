/**
 * Domain Badge Component
 * Displays the career domain as a styled badge
 */
import React from "react";

const DOMAIN_CLASSES = {
  SOFTWARE_ENGINEERING:
    "bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 border border-purple-300",
  DATA: "bg-gradient-to-r from-indigo-100 to-blue-100 text-indigo-700 border border-indigo-300",
  AI_ML:
    "bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 border border-purple-300",
  DEVOPS:
    "bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border border-blue-300",
  QA: "bg-gradient-to-r from-slate-100 to-gray-100 text-slate-700 border border-slate-300",
  MOBILE:
    "bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 border border-indigo-300",
  UI_UX:
    "bg-gradient-to-r from-purple-100 to-violet-100 text-purple-700 border border-purple-300",
  default:
    "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-600 border border-gray-300",
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
