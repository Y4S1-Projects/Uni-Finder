/**
 * Next Role Badge Component
 * Displays the next career step in a highlighted badge
 */
import React from "react";
import { FaRocket } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

export function NextRoleBadge({
  nextRole,
  nextRoleTitle,
  variant = "compact",
  showLadderButton = true,
}) {
  const navigate = useNavigate();

  if (!nextRole) return null;

  if (variant === "full") {
    return (
      <div className="bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 p-5 rounded-xl border-2 border-purple-200 shadow-md hover:shadow-lg transition-all duration-300">
        <div className="font-semibold text-purple-700 mb-2 flex items-center gap-2">
          <FaRocket className="text-lg" /> Next Career Step
        </div>
        <div className="flex items-center justify-between gap-4">
          <div className="text-xl font-bold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent">
            {nextRoleTitle || nextRole}
          </div>
          {showLadderButton && (
            <button
              onClick={() => navigate("/career-ladder")}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg text-sm font-semibold transition-all duration-300 shadow-md hover:shadow-lg whitespace-nowrap"
            >
              View Career Path
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 px-4 py-2.5 rounded-lg border border-purple-200 shadow-sm hover:shadow-md transition-all duration-200 flex items-center justify-between gap-4">
      <div>
        <span className="text-purple-700 font-semibold flex items-center gap-1.5">
          <FaRocket /> Next Step:
        </span>{" "}
        <span className="text-purple-900 font-medium">
          {nextRoleTitle || nextRole}
        </span>
      </div>
      {showLadderButton && (
        <button
          onClick={() => navigate("/career-ladder")}
          className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg text-xs font-semibold transition-all duration-300 shadow-md hover:shadow-lg whitespace-nowrap hover:scale-105"
        >
          View Path
        </button>
      )}
    </div>
  );
}
