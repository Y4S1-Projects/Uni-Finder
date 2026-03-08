import React from "react";
import { createPortal } from "react-dom";
import { FaTimes, FaCheckCircle, FaExclamationTriangle } from "react-icons/fa";

export default function LevelDetailModal({ level, userSkills = [], onClose }) {
  if (!level) return null;

  const userSkillsLower = new Set(
    (userSkills || []).map((s) =>
      typeof s === "string"
        ? s.toLowerCase()
        : String(s.name || s).toLowerCase(),
    ),
  );

  const requiredSkills = level.required_skills || level.skills_needed || [];
  const matchedSkills = requiredSkills.filter((s) =>
    userSkillsLower.has(s.toLowerCase()),
  );
  const missingSkills = requiredSkills.filter(
    (s) => !userSkillsLower.has(s.toLowerCase()),
  );

  const readiness =
    level.readiness_score != null
      ? Math.round(level.readiness_score * 100)
      : null;

  // Use portal to render modal at document body level, avoiding z-index stacking context issues
  return createPortal(
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-500 text-white">
          <div>
            <h3 className="text-lg font-bold">
              {level.role || level.title || `Level ${level.level}`}
            </h3>
            {level.level != null && (
              <p className="text-purple-200 text-sm">Level {level.level}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 transition-colors"
          >
            <FaTimes className="text-white" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 overflow-y-auto max-h-[60vh] space-y-5">
          {/* Readiness */}
          {readiness != null && (
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">
                Readiness
              </p>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all"
                  style={{ width: `${readiness}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">{readiness}% ready</p>
            </div>
          )}

          {/* Skills you have */}
          {matchedSkills.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-1">
                <FaCheckCircle className="text-green-500" /> Skills You Have (
                {matchedSkills.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {matchedSkills.map((s) => (
                  <span
                    key={s}
                    className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700 border border-green-200"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Skills to develop */}
          {missingSkills.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-amber-700 mb-2 flex items-center gap-1">
                <FaExclamationTriangle className="text-amber-500" /> Skills to
                Develop ({missingSkills.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {missingSkills.map((s) => (
                  <span
                    key={s}
                    className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {level.description && (
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">
                Description
              </p>
              <p className="text-sm text-gray-600">{level.description}</p>
            </div>
          )}

          {/* Experience */}
          {level.typical_experience && (
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">
                Typical Experience
              </p>
              <p className="text-sm text-gray-600">
                {level.typical_experience}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-gray-50 border-t flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
