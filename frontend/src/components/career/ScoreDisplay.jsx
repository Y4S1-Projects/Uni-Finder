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
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600",
  };

  return (
    <div
      className={`flex-1 p-4 rounded-lg text-center ${
        variants[variant]?.split(" ")[0] || "bg-blue-50"
      }`}
    >
      <div
        className={`text-3xl font-bold ${
          variants[variant]?.split(" ")[1] || "text-blue-600"
        }`}
      >
        {(score * 100).toFixed(0)}%
      </div>
      <div className="text-xs text-gray-500">{label}</div>
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
