/**
 * Recommendations Summary Component
 * Displays summary of the analysis
 */
import React from "react";
import { FaLightbulb } from "react-icons/fa";

export function RecommendationsSummary({ skillsCount, rolesCount }) {
  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg mb-6 border-l-4 border-purple-500">
      <p className="m-0 text-gray-700">
        Analyzed <strong className="text-purple-700">{skillsCount}</strong>{" "}
        skills across <strong className="text-purple-700">{rolesCount}</strong>{" "}
        career roles
      </p>
    </div>
  );
}

export function HowItWorks() {
  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-6 rounded-lg mt-6 border border-purple-200">
      <h3 className="text-purple-700 font-semibold mb-4 flex items-center gap-2">
        <FaLightbulb /> How This Works
      </h3>
      <p className="text-gray-700 leading-relaxed m-0">
        Our AI uses{" "}
        <strong className="text-purple-700">Cosine Similarity</strong> to
        compare your skill profile against real job market data. Each role has
        an importance-weighted skill profile built from actual job postings. The
        match score indicates how well your skills align with each role's
        requirements. Higher scores mean better fit!
      </p>
    </div>
  );
}
