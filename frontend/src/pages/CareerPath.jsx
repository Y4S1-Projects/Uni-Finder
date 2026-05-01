/**
 * Career Path Page
 * Main page for career recommendations using modular components
 */
import React from "react";
import { useNavigate } from "react-router-dom";
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
import { FaChartLine, FaTrophy, FaUndo } from "react-icons/fa";

export default function CareerPath() {
  const navigate = useNavigate();

  // Restore state from sessionStorage on mount
  const [selectedSkills, setSelectedSkills] = React.useState(() => {
    const saved = sessionStorage.getItem("careerPath_skills");
    return saved ? JSON.parse(saved) : [];
  });

  // Form inputs using useInput hook with restored values
  const experienceLevel = useInput(
    sessionStorage.getItem("careerPath_experienceLevel") || "",
    validateExperienceLevel,
  );
  const currentStatus = useInput(
    sessionStorage.getItem("careerPath_currentStatus") || "",
    validateCurrentStatus,
  );
  const preferredDomain = useInput(
    sessionStorage.getItem("careerPath_preferredDomain") || "",
    validatePreferredDomain,
  );
  const educationLevel = useInput(
    sessionStorage.getItem("careerPath_educationLevel") || "",
    validateEducationLevel,
  );
  const careerGoal = useInput(
    sessionStorage.getItem("careerPath_careerGoal") || "",
    validateCareerGoal,
  );

  // Custom hooks for business logic
  const {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    setRecommendations,
  } = useCareerRecommendations();

  const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } =
    useCareerDetail();

  // Restore recommendations on mount
  React.useEffect(() => {
    const savedRecommendations = sessionStorage.getItem(
      "careerPath_recommendations",
    );
    if (savedRecommendations) {
      setRecommendations(JSON.parse(savedRecommendations));
    }
  }, [setRecommendations]);

  // Save selectedSkills to sessionStorage whenever it changes
  React.useEffect(() => {
    sessionStorage.setItem("careerPath_skills", JSON.stringify(selectedSkills));
  }, [selectedSkills]);

  // Save form values to sessionStorage whenever they change
  React.useEffect(() => {
    sessionStorage.setItem("careerPath_experienceLevel", experienceLevel.value);
  }, [experienceLevel.value]);

  React.useEffect(() => {
    sessionStorage.setItem("careerPath_currentStatus", currentStatus.value);
  }, [currentStatus.value]);

  React.useEffect(() => {
    sessionStorage.setItem("careerPath_preferredDomain", preferredDomain.value);
  }, [preferredDomain.value]);

  React.useEffect(() => {
    sessionStorage.setItem("careerPath_educationLevel", educationLevel.value);
  }, [educationLevel.value]);

  React.useEffect(() => {
    sessionStorage.setItem("careerPath_careerGoal", careerGoal.value);
  }, [careerGoal.value]);

  // Save recommendations to sessionStorage whenever they change
  React.useEffect(() => {
    if (recommendations) {
      sessionStorage.setItem(
        "careerPath_recommendations",
        JSON.stringify(recommendations),
      );
    }
  }, [recommendations]);

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
    fetchJobDetail(recommendation, selectedSkills, {
      experienceLevel: experienceLevel.value,
      currentStatus: currentStatus.value,
      educationLevel: educationLevel.value,
      careerGoal: careerGoal.value,
      preferredDomain: preferredDomain.value,
    });
  };

  const handleViewCareerLadder = () => {
    if (!jobDetail) return;
    navigate("/career-ladder", {
      state: {
        userSkills: selectedSkills,
        selectedDomain: jobDetail.domain,
        recommendations: [jobDetail],
        userProfile: {
          experienceLevel: experienceLevel.value,
          currentStatus: currentStatus.value,
          educationLevel: educationLevel.value,
          careerGoal: careerGoal.value,
        },
      },
    });
  };

  // Optional: Add a function to clear saved state
  const handleClearState = () => {
    sessionStorage.removeItem("careerPath_skills");
    sessionStorage.removeItem("careerPath_experienceLevel");
    sessionStorage.removeItem("careerPath_currentStatus");
    sessionStorage.removeItem("careerPath_preferredDomain");
    sessionStorage.removeItem("careerPath_educationLevel");
    sessionStorage.removeItem("careerPath_careerGoal");
    sessionStorage.removeItem("careerPath_recommendations");
    window.location.reload();
  };

  return (
    <div className="p-8 max-w-5xl mx-auto mt-24">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent flex items-center gap-2">
          <FaChartLine /> Career Path Recommender
        </h2>

        {/* Reset Button */}
        <button
          onClick={handleClearState}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-all duration-300 shadow-md hover:shadow-lg"
          title="Reset all inputs and recommendations"
        >
          <FaUndo />
          <span className="font-semibold">Reset</span>
        </button>
      </div>
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
          userSkills={selectedSkills}
          onViewDetails={handleViewJob}
        />
      )}

      {/* Detail Modal */}
      <CareerDetailModal
        isOpen={!!selectedJob}
        onClose={closeDetail}
        jobDetail={jobDetail}
        isLoading={detailLoading}
        onViewPath={handleViewCareerLadder}
        userProfile={{
          experienceLevel: experienceLevel.value,
          currentStatus: currentStatus.value,
          educationLevel: educationLevel.value,
          careerGoal: careerGoal.value,
        }}
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

function RecommendationsSection({
  recommendations,
  userSkills,
  onViewDetails,
}) {
  return (
    <div className="mt-8">
      {/* Summary */}
      <RecommendationsSummary
        skillsCount={recommendations.skills_analyzed.length}
        rolesCount={recommendations.total_roles_compared}
        domainFilterApplied={recommendations.domain_filter_applied}
        preferredDomain={recommendations.preferred_domain}
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
          isBestMatch={rec.is_best_match || false}
          onViewDetails={onViewDetails}
          userSkills={userSkills}
        />
      ))}

      {/* How It Works */}
      <HowItWorks />
    </div>
  );
}
