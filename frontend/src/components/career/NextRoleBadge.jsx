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
      <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-purple-100 p-5 rounded-xl border-2 border-purple-200 shadow-md hover:shadow-lg transition-all duration-300">
        <div className="font-semibold text-purple-700 mb-2 flex items-center gap-2">
          🚀 Next Career Step
        </div>
        <div className="text-xl font-bold bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-transparent">
          {nextRoleTitle || nextRole}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-green-50 to-emerald-50 px-4 py-2.5 rounded-lg border border-green-200 shadow-sm hover:shadow-md transition-all duration-200">
      <span className="text-green-700 font-semibold">🚀 Next Step:</span>{" "}
      <span className="text-green-800 font-medium">
        {nextRoleTitle || nextRole}
      </span>
    </div>
  );
}
