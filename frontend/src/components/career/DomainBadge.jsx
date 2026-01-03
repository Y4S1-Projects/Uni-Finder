/**
 * Domain Badge Component
 * Displays the career domain as a styled badge
 */
import React from "react";

const DOMAIN_COLORS = {
  SOFTWARE_ENGINEERING: { bg: "#e0e7ff", text: "#4338ca" },
  DATA: { bg: "#fef3c7", text: "#92400e" },
  AI_ML: { bg: "#fce7f3", text: "#9d174d" },
  DEVOPS: { bg: "#d1fae5", text: "#065f46" },
  QA: { bg: "#fee2e2", text: "#991b1b" },
  MOBILE: { bg: "#e0f2fe", text: "#0369a1" },
  UI_UX: { bg: "#f3e8ff", text: "#7c3aed" },
  default: { bg: "#f3f4f6", text: "#4b5563" },
};

export function DomainBadge({ domain, size = "small" }) {
  if (!domain) return null;

  const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.default;
  const padding = size === "large" ? "4px 12px" : "2px 8px";
  const fontSize = size === "large" ? 14 : 12;

  return (
    <span
      style={{
        background: colors.bg,
        color: colors.text,
        padding,
        borderRadius: size === "large" ? 6 : 4,
        fontSize,
      }}
    >
      {domain.replace(/_/g, " ")}
    </span>
  );
}
