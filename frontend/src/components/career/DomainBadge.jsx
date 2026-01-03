/**
 * Domain Badge Component
 * Displays the career domain as a styled badge
 */
import React from "react";

const DOMAIN_CLASSES = {
  SOFTWARE_ENGINEERING: "bg-indigo-100 text-indigo-700",
  DATA: "bg-amber-100 text-amber-800",
  AI_ML: "bg-pink-100 text-pink-700",
  DEVOPS: "bg-green-100 text-green-800",
  QA: "bg-red-100 text-red-700",
  MOBILE: "bg-sky-100 text-sky-700",
  UI_UX: "bg-purple-100 text-purple-700",
  default: "bg-gray-100 text-gray-600",
};

export function DomainBadge({ domain, size = "small" }) {
  if (!domain) return null;

  const colorClass = DOMAIN_CLASSES[domain] || DOMAIN_CLASSES.default;
  const sizeClasses =
    size === "large"
      ? "px-3 py-1 text-sm rounded-md"
      : "px-2 py-0.5 text-xs rounded";

  return (
    <span className={`${colorClass} ${sizeClasses} font-medium`}>
      {domain.replace(/_/g, " ")}
    </span>
  );
}
