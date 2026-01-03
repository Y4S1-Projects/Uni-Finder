/**
 * Score Display Component
 * Displays match score or readiness score with visual indicator
 */
import React from "react";

export function getScoreColor(score) {
  if (score >= 0.7) return "#16a34a"; // green
  if (score >= 0.4) return "#ca8a04"; // yellow
  return "#dc2626"; // red
}

export function ScoreCircle({ score, label, size = "normal" }) {
  const color = getScoreColor(score);
  const fontSize = size === "large" ? 32 : size === "small" ? 20 : 28;
  const labelSize = size === "large" ? 14 : 12;

  return (
    <div style={{ textAlign: "right" }}>
      <div
        style={{
          fontSize,
          fontWeight: "bold",
          color,
        }}
      >
        {(score * 100).toFixed(0)}%
      </div>
      <div style={{ fontSize: labelSize, color: "#666" }}>{label}</div>
    </div>
  );
}

export function ScoreCard({
  score,
  label,
  bgColor = "#f0f7ff",
  textColor = "#2563eb",
}) {
  return (
    <div
      style={{
        flex: 1,
        background: bgColor,
        padding: "1rem",
        borderRadius: 8,
        textAlign: "center",
      }}
    >
      <div
        style={{
          fontSize: 32,
          fontWeight: "bold",
          color: textColor,
        }}
      >
        {(score * 100).toFixed(0)}%
      </div>
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
    </div>
  );
}

export function ProgressBar({ score, height = 8 }) {
  const color = getScoreColor(score);

  return (
    <div
      style={{
        background: "#e5e7eb",
        borderRadius: height,
        height,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${score * 100}%`,
          height: "100%",
          background: color,
          borderRadius: height,
          transition: "width 0.5s ease",
        }}
      />
    </div>
  );
}
