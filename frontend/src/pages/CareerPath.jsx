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
    <div style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      {/* Header */}
      <h2>🎯 Career Path Recommender</h2>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
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
    <form onSubmit={onSubmit} style={{ display: "grid", gap: "1rem" }}>
      <label>
        <strong>Your Skills</strong>
        <div style={{ marginTop: 8 }}>
          <SkillSelector selected={selectedSkills} onChange={onSkillsChange} />
        </div>
      </label>

      <div style={{ marginTop: 8 }}>
        <button
          type="submit"
          disabled={loading || selectedSkills.length === 0}
          style={{
            padding: "0.75rem 1.5rem",
            background: selectedSkills.length === 0 ? "#ccc" : "#4a90d9",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: selectedSkills.length === 0 ? "not-allowed" : "pointer",
            fontSize: 16,
          }}
        >
          {loading ? "Analyzing..." : "Find My Best Career Matches"}
        </button>
      </div>
    </form>
  );
}

function ErrorMessage({ message }) {
  return (
    <div
      style={{
        marginTop: "1rem",
        color: "crimson",
        padding: "1rem",
        background: "#fff0f0",
        borderRadius: 6,
      }}
    >
      {message}
    </div>
  );
}

function RecommendationsSection({ recommendations, onViewDetails }) {
  return (
    <div style={{ marginTop: "2rem" }}>
      {/* Summary */}
      <RecommendationsSummary
        skillsCount={recommendations.skills_analyzed.length}
        rolesCount={recommendations.total_roles_compared}
      />

      {/* Title */}
      <h3 style={{ marginBottom: "1rem" }}>🏆 Top Career Recommendations</h3>

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
