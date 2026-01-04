/**
 * Career Path Page
 * Main page for career recommendations using modular components
 */
import React from "react";
import SkillSelector from "../components/career/SkillSelector";
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
import { FaChartLine, FaSearch, FaTrophy } from "react-icons/fa";

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
      <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent flex items-center gap-2">
        <FaChartLine /> Career Path Recommender
      </h2>
      <p className="text-gray-700 mb-8 text-lg">
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
    <form
      onSubmit={onSubmit}
      className="grid gap-6 p-6 bg-white rounded-2xl border-2 border-purple-200 shadow-lg"
    >
      <label>
        <strong className="block mb-3 text-gray-800 text-lg">
          Your Skills
        </strong>
        <SkillSelector selected={selectedSkills} onChange={onSkillsChange} />
      </label>

      <div className="mt-2">
        <button
          type="submit"
          disabled={loading || selectedSkills.length === 0}
          className={`px-8 py-4 text-white rounded-xl text-base font-semibold transition-all duration-300 shadow-lg ${
            selectedSkills.length === 0
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-2xl hover:scale-105 cursor-pointer"
          }`}
        >
          {loading ? (
            <>
              <FaSearch className="animate-spin" /> Analyzing...
            </>
          ) : (
            <>
              <FaTrophy /> Find My Best Career Matches
            </>
          )}
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
      <h3 className="text-xl font-semibold mb-4 bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent flex items-center gap-2">
        <FaTrophy /> Top Career Recommendations
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
