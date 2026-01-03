/**
 * AI Explanation Component
 * Displays the AI-generated career explanation with markdown formatting
 */
import React from "react";

function formatExplanation(text) {
  if (!text) return "";

  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/^- /gm, "• ")
    .replace(/^(\d+)\. /gm, "<strong>$1.</strong> ")
    .replace(/\n/g, "<br/>");
}

export function AIExplanation({ explanation }) {
  if (!explanation) return null;

  return (
    <div
      style={{
        background: "linear-gradient(135deg, #fdf4ff 0%, #f5f3ff 100%)",
        padding: "1.5rem",
        borderRadius: 12,
        border: "1px solid #e9d5ff",
      }}
    >
      <h3
        style={{
          margin: "0 0 1rem 0",
          color: "#7c3aed",
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        🤖 AI Career Analysis
      </h3>
      <div
        style={{
          color: "#4c1d95",
          lineHeight: 1.7,
          whiteSpace: "pre-wrap",
        }}
        dangerouslySetInnerHTML={{
          __html: formatExplanation(explanation),
        }}
      />
    </div>
  );
}

export function AILoadingState() {
  return (
    <div style={{ textAlign: "center", padding: "3rem" }}>
      <div style={{ fontSize: 48, marginBottom: "1rem" }}>🤖</div>
      <div style={{ color: "#666" }}>AI is analyzing this career path...</div>
    </div>
  );
}
