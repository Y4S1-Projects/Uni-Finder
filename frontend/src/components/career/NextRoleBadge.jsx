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
      <div className="bg-purple-50 p-4 rounded-lg">
        <div className="font-medium text-purple-600 mb-1">
          🚀 Next Career Step
        </div>
        <div className="text-lg text-purple-800">
          {nextRoleTitle || nextRole}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-green-50 px-3 py-2 rounded-md">
      <span className="text-green-600 font-medium">🚀 Next Step:</span>{" "}
      <span className="text-green-800">{nextRoleTitle || nextRole}</span>
    </div>
  );
}
