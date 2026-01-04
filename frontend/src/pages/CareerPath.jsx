/**
 * Career Path Page
 * Main page for career recommendations using modular components
 */
import React from "react";
import CareerProfileForm from "../components/career/CareerProfileForm";
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
import { useInput } from "../hooks/use-input";
import {
  validateExperienceLevel,
  validateCurrentStatus,
  validatePreferredDomain,
  validateEducationLevel,
  validateCareerGoal,
} from "../utils/validationUtils";
import { FaChartLine, FaTrophy } from "react-icons/fa";

export default function CareerPath() {
  const [selectedSkills, setSelectedSkills] = React.useState([]);

  // Form inputs using useInput hook
  const experienceLevel = useInput("", validateExperienceLevel);
  const currentStatus = useInput("", validateCurrentStatus);
  const preferredDomain = useInput("", validatePreferredDomain);
  const educationLevel = useInput("", validateEducationLevel);
  const careerGoal = useInput("", validateCareerGoal);

  // Custom hooks for business logic
  const { recommendations, loading, error, fetchRecommendations } =
    useCareerRecommendations();

  const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } =
    useCareerDetail();

  const handlePredict = async (e) => {
    e.preventDefault();

    // Validate all required fields
    experienceLevel.handleInputBlur();
    currentStatus.handleInputBlur();
    educationLevel.handleInputBlur();
    careerGoal.handleInputBlur();

    // Check for errors
    if (
      experienceLevel.hasError ||
      currentStatus.hasError ||
      educationLevel.hasError ||
      careerGoal.hasError
    ) {
      return;
    }

    // Prepare career context data
    const careerContext = {
      experience_level: experienceLevel.value,
      current_status: currentStatus.value,
      preferred_domain: preferredDomain.value || null,
      education_level: educationLevel.value,
      career_goal: careerGoal.value,
    };

    await fetchRecommendations(selectedSkills, 5, careerContext);
  };

  const handleViewJob = (recommendation) => {
    fetchJobDetail(recommendation, selectedSkills);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent flex items-center gap-2">
        <FaChartLine /> Career Path Recommender
      </h2>
      <p className="text-gray-700 mb-8 text-lg">
        Tell us about yourself and select your skills to get personalized
        AI-powered career recommendations.
      </p>

      {/* Career Profile Form */}
      <CareerProfileForm
        selectedSkills={selectedSkills}
        onSkillsChange={setSelectedSkills}
        onSubmit={handlePredict}
        loading={loading}
        experienceLevel={experienceLevel}
        currentStatus={currentStatus}
        preferredDomain={preferredDomain}
        educationLevel={educationLevel}
        careerGoal={careerGoal}
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
// Sub-components
// =============================================================================

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
