/**
 * Recommendations Summary Component
 * Displays summary of the analysis
 */
import React from "react";

export function RecommendationsSummary({ skillsCount, rolesCount }) {
  return (
    <div className="bg-slate-50 p-4 rounded-lg mb-6 border-l-4 border-blue-500">
      <p className="m-0 text-gray-500">
        Analyzed <strong>{skillsCount}</strong> skills across{" "}
        <strong>{rolesCount}</strong> career roles
      </p>
    </div>
  );
}

export function HowItWorks() {
  return (
    <div className="bg-purple-50 p-6 rounded-lg mt-6">
      <h3 className="text-purple-600 font-semibold mb-4">💡 How This Works</h3>
      <p className="text-gray-600 leading-relaxed m-0">
        Our AI uses <strong>Cosine Similarity</strong> to compare your skill
        profile against real job market data. Each role has an
        importance-weighted skill profile built from actual job postings. The
        match score indicates how well your skills align with each role's
        requirements. Higher scores mean better fit!
      </p>
    </div>
  );
}
