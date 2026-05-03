/**
 * Next Role Badge Component
 * Displays the next career step in a highlighted badge
 */
import React from "react";
import { FaRocket } from "react-icons/fa";

export function NextRoleBadge({
  nextRole,
  nextRoleTitle,
  variant = "compact",
  showLadderButton = true,
  onViewPath,
}) {
  if (!nextRole) return null;

  if (variant === "full") {
    return (
      <div className="bg-gradient-to-br from-indigo-50 via-white to-blue-50 p-5 rounded-xl border-2 border-indigo-100 shadow-md hover:shadow-lg transition-all duration-300">
        <div className="font-semibold text-indigo-700 mb-2 flex items-center gap-2">
          <FaRocket className="text-lg" /> Next Career Step
        </div>
        <div className="flex items-center justify-between gap-4">
          <div className="text-xl font-bold text-indigo-900 tracking-tight">
            {nextRoleTitle || nextRole}
          </div>
          {showLadderButton && onViewPath && (
            <button
              onClick={onViewPath}
              className="px-4 py-2 text-white rounded-lg text-sm font-semibold transition-all duration-200 shadow-md hover:shadow-lg whitespace-nowrap bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-indigo-500/30 border border-transparent"
            >
              View Career Path
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white px-4 py-2.5 rounded-lg border border-indigo-100 shadow-sm hover:shadow-md transition-all duration-200 flex items-center justify-between gap-4">
      <div>
        <span className="text-indigo-700 font-semibold flex items-center gap-1.5">
          <FaRocket /> Next Step:
        </span>{" "}
        <span className="text-indigo-900 font-medium">
          {nextRoleTitle || nextRole}
        </span>
      </div>
      {showLadderButton && onViewPath && (
        <button
          onClick={onViewPath}
          className="px-3 py-1.5 text-white rounded-lg text-xs font-semibold transition-all duration-200 shadow-md hover:shadow-lg whitespace-nowrap bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.05] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-indigo-500/30 border border-transparent"
        >
          View Path
        </button>
      )}
    </div>
  );
}
