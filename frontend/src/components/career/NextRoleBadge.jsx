/**
 * Next Role Badge Component
 * Displays the next career step in a highlighted badge
 */
import React from "react";

export function NextRoleBadge({
  nextRole,
  nextRoleTitle,
  variant = "compact",
}) {
  if (!nextRole) return null;

  if (variant === "full") {
    return (
      <div
        style={{
          background: "#faf5ff",
          padding: "1rem",
          borderRadius: 8,
        }}
      >
        <div
          style={{
            fontWeight: 500,
            color: "#7c3aed",
            marginBottom: 4,
          }}
        >
          🚀 Next Career Step
        </div>
        <div style={{ fontSize: 18, color: "#5b21b6" }}>
          {nextRoleTitle || nextRole}
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        background: "#f0fdf4",
        padding: "0.75rem",
        borderRadius: 6,
      }}
    >
      <span style={{ color: "#16a34a", fontWeight: 500 }}>🚀 Next Step:</span>{" "}
      <span style={{ color: "#166534" }}>{nextRoleTitle || nextRole}</span>
    </div>
  );
}
