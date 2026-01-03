/**
 * Score Display Component
 * Displays match score or readiness score with visual indicator
 */
import React from "react";

export function getScoreColor(score) {
  if (score >= 0.7) return "text-green-600";
  if (score >= 0.4) return "text-yellow-600";
  return "text-red-600";
}

export function getScoreBgColor(score) {
  if (score >= 0.7) return "bg-green-500";
  if (score >= 0.4) return "bg-yellow-500";
  return "bg-red-500";
}

export function ScoreCircle({ score, label, size = "normal" }) {
  const colorClass = getScoreColor(score);
  const sizeClasses = {
    large: "text-3xl",
    normal: "text-2xl",
    small: "text-xl",
  };
  const labelSizeClasses = {
    large: "text-sm",
    normal: "text-xs",
    small: "text-xs",
  };

  return (
    <div className="text-right">
      <div className={`font-bold ${sizeClasses[size]} ${colorClass}`}>
        {(score * 100).toFixed(0)}%
      </div>
      <div className={`${labelSizeClasses[size]} text-gray-500`}>{label}</div>
    </div>
  );
}

export function ScoreCard({ score, label, variant = "blue" }) {
  const variants = {
    blue: "bg-gradient-to-br from-blue-50 to-blue-100 text-blue-700 border-2 border-blue-200",
    green:
      "bg-gradient-to-br from-green-50 to-green-100 text-green-700 border-2 border-green-200",
    purple:
      "bg-gradient-to-br from-purple-50 to-purple-100 text-purple-700 border-2 border-purple-200",
  };

  return (
    <div
      className={`flex-1 p-5 rounded-xl text-center shadow-md hover:shadow-lg transition-all duration-300 ${
        variants[variant] || variants.blue
      }`}
    >
      <div className="text-4xl font-bold">{(score * 100).toFixed(0)}%</div>
      <div className="text-xs font-semibold text-gray-600 mt-1">{label}</div>
    </div>
  );
}

export function ProgressBar({ score, height = "h-2" }) {
  const bgColorClass = getScoreBgColor(score);

  return (
    <div className={`bg-gray-200 rounded-full ${height} overflow-hidden`}>
      <div
        className={`${height} ${bgColorClass} rounded-full transition-all duration-500`}
        style={{ width: `${score * 100}%` }}
      />
    </div>
  );
}
