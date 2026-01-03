/**
 * Career Path Page
 * Main page for career recommendations using modular components
 */
import React from "react";
import SkillSelector from "../components/SkillSelector";
import {
  CareerRecommendationCard,
  CareerDetailModal,
  RecommendationsSummary,
  HowItWorks,
} from "../components/career";
import {
  useCareerRecommendations,
  useCareerDetail,
} from "../hooks/useCareerRecommendations";

export default function CareerPath() {
  const [selectedSkills, setSelectedSkills] = React.useState([]);

  // Custom hooks for business logic
  const { recommendations, loading, error, fetchRecommendations } =
    useCareerRecommendations();

  const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } =
    useCareerDetail();

  const handlePredict = async (e) => {
    e.preventDefault();
    await fetchRecommendations(selectedSkills, 5);
  };

  const handleViewJob = (recommendation) => {
    fetchJobDetail(recommendation, selectedSkills);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <h2 className="text-2xl font-bold mb-2">🎯 Career Path Recommender</h2>
      <p className="text-gray-500 mb-6">
        Select your skills below and we'll recommend the best matching career
        roles using AI-powered cosine similarity analysis.
      </p>

      {/* Skill Selection Form */}
      <SkillSelectionForm
        selectedSkills={selectedSkills}
        onSkillsChange={setSelectedSkills}
        onSubmit={handlePredict}
        loading={loading}
      />

      {/* Error Display */}
      {error && <ErrorMessage message={error} />}

      {/* Recommendations List */}
      {recommendations && (
        <RecommendationsSection
          recommendations={recommendations}
          onViewDetails={handleViewJob}
        />
      )}

      {/* Detail Modal */}
      <CareerDetailModal
        isOpen={!!selectedJob}
        onClose={closeDetail}
        jobDetail={jobDetail}
        isLoading={detailLoading}
      />
    </div>
  );
}

// =============================================================================
// Sub-components (could be extracted to separate files if needed)
// =============================================================================

function SkillSelectionForm({
  selectedSkills,
  onSkillsChange,
  onSubmit,
  loading,
}) {
  return (
    <form onSubmit={onSubmit} className="grid gap-4">
      <label>
        <strong className="block mb-2">Your Skills</strong>
        <SkillSelector selected={selectedSkills} onChange={onSkillsChange} />
      </label>

      <div className="mt-2">
        <button
          type="submit"
          disabled={loading || selectedSkills.length === 0}
          className={`px-6 py-3 text-white rounded-md text-base font-medium transition-colors ${
            selectedSkills.length === 0
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600 cursor-pointer"
          }`}
        >
          {loading ? "Analyzing..." : "Find My Best Career Matches"}
        </button>
      </div>
    </form>
  );
}

function ErrorMessage({ message }) {
  return (
    <div className="mt-4 text-red-600 p-4 bg-red-50 rounded-md">{message}</div>
  );
}

function RecommendationsSection({ recommendations, onViewDetails }) {
  return (
    <div className="mt-8">
      {/* Summary */}
      <RecommendationsSummary
        skillsCount={recommendations.skills_analyzed.length}
        rolesCount={recommendations.total_roles_compared}
      />

      {/* Title */}
      <h3 className="text-xl font-semibold mb-4">
        🏆 Top Career Recommendations
      </h3>

      {/* Recommendation Cards */}
      {recommendations.recommendations.map((rec, index) => (
        <CareerRecommendationCard
          key={rec.role_id}
          recommendation={rec}
          rank={index + 1}
          isBestMatch={index === 0}
          onViewDetails={onViewDetails}
        />
      ))}

      {/* How It Works */}
      <HowItWorks />
    </div>
  );
}
