/**
 * Recommendations Summary Component
 * Displays summary of the analysis
 */
import React from "react";

export function RecommendationsSummary({ skillsCount, rolesCount }) {
  return (
    <div
      style={{
        background: "#f8fafc",
        padding: "1rem",
        borderRadius: 8,
        marginBottom: "1.5rem",
        borderLeft: "4px solid #4a90d9",
      }}
    >
      <p style={{ margin: 0, color: "#666" }}>
        Analyzed <strong>{skillsCount}</strong> skills across{" "}
        <strong>{rolesCount}</strong> career roles
      </p>
    </div>
  );
}

export function HowItWorks() {
  return (
    <div
      style={{
        background: "#faf5ff",
        padding: "1.5rem",
        borderRadius: 8,
        marginTop: "1.5rem",
      }}
    >
      <h3 style={{ margin: "0 0 1rem 0", color: "#7c3aed" }}>
        💡 How This Works
      </h3>
      <p style={{ color: "#666", lineHeight: 1.6, margin: 0 }}>
        Our AI uses <strong>Cosine Similarity</strong> to compare your skill
        profile against real job market data. Each role has an
        importance-weighted skill profile built from actual job postings. The
        match score indicates how well your skills align with each role's
        requirements. Higher scores mean better fit!
      </p>
    </div>
  );
}
