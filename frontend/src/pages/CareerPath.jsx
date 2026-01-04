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
import { useInput } from "../hooks/use-input";
import {
  validateExperienceLevel,
  validateCurrentStatus,
  validatePreferredDomain,
  validateEducationLevel,
  validateCareerGoal,
} from "../utils/validationUtils";
import {
  FaChartLine,
  FaSearch,
  FaTrophy,
  FaUser,
  FaGraduationCap,
  FaBriefcase,
  FaRocket,
} from "react-icons/fa";

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

function CareerProfileForm({
  selectedSkills,
  onSkillsChange,
  onSubmit,
  loading,
  experienceLevel,
  currentStatus,
  preferredDomain,
  educationLevel,
  careerGoal,
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="grid gap-6 p-8 bg-white rounded-2xl border-2 border-purple-200 shadow-lg"
    >
      {/* Tier 1: Experience Level */}
      <div>
        <label className="block mb-3">
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaBriefcase className="text-purple-600" />
            <span>Experience Level</span>
            <span className="text-red-500">*</span>
          </div>
          <div className="space-y-2">
            {[
              { value: "student", label: "Student / No experience" },
              { value: "0-1", label: "0–1 years" },
              { value: "1-3", label: "1–3 years" },
              { value: "3-5", label: "3–5 years" },
              { value: "5+", label: "5+ years" },
            ].map((option) => (
              <label
                key={option.value}
                className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-purple-50 transition-colors"
              >
                <input
                  type="radio"
                  name="experience"
                  value={option.value}
                  checked={experienceLevel.value === option.value}
                  onChange={(e) => experienceLevel.setValue(e.target.value)}
                  onBlur={experienceLevel.handleInputBlur}
                  className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
          {experienceLevel.hasError && (
            <p className="text-red-500 text-sm mt-2">
              {experienceLevel.errorMessage}
            </p>
          )}
        </label>
      </div>

      {/* Tier 1: Current Status */}
      <div>
        <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
          <FaUser className="text-purple-600" />
          <span>Current Status</span>
          <span className="text-red-500">*</span>
        </div>
        <div className="flex gap-3">
          {[
            { value: "student", label: "Student" },
            { value: "graduate", label: "Graduate" },
            { value: "working", label: "Working Professional" },
          ].map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => currentStatus.setValue(option.value)}
              onBlur={currentStatus.handleInputBlur}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-300 ${
                currentStatus.value === option.value
                  ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
        {currentStatus.hasError && (
          <p className="text-red-500 text-sm mt-2">
            {currentStatus.errorMessage}
          </p>
        )}
      </div>

      {/* Tier 2: Education Level */}
      <div>
        <label className="block">
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaGraduationCap className="text-purple-600" />
            <span>Highest Education</span>
            <span className="text-red-500">*</span>
          </div>
          <select
            value={educationLevel.value}
            onChange={educationLevel.handleInputChange}
            onBlur={educationLevel.handleInputBlur}
            className="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all duration-200 outline-none text-gray-700"
          >
            <option value="">Select education level</option>
            <option value="al">A/L</option>
            <option value="diploma">Diploma</option>
            <option value="hnd">HND</option>
            <option value="bachelors">Bachelor's Degree</option>
            <option value="masters">Master's Degree</option>
          </select>
          {educationLevel.hasError && (
            <p className="text-red-500 text-sm mt-2">
              {educationLevel.errorMessage}
            </p>
          )}
        </label>
      </div>

      {/* Tier 2: Career Goal */}
      <div>
        <label className="block">
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaRocket className="text-purple-600" />
            <span>Career Goal</span>
            <span className="text-red-500">*</span>
          </div>
          <select
            value={careerGoal.value}
            onChange={careerGoal.handleInputChange}
            onBlur={careerGoal.handleInputBlur}
            className="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all duration-200 outline-none text-gray-700"
          >
            <option value="">What is your goal?</option>
            <option value="first_job">Get first job</option>
            <option value="switch_career">Switch career</option>
            <option value="get_promoted">Get promoted</option>
          </select>
          {careerGoal.hasError && (
            <p className="text-red-500 text-sm mt-2">
              {careerGoal.errorMessage}
            </p>
          )}
        </label>
      </div>

      {/* Tier 1: Preferred Domain (Optional) */}
      <div>
        <label className="block">
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaChartLine className="text-purple-600" />
            <span>Preferred Domain</span>
            <span className="text-gray-500 text-sm font-normal ml-2">
              (Optional)
            </span>
          </div>
          <select
            value={preferredDomain.value}
            onChange={preferredDomain.handleInputChange}
            onBlur={preferredDomain.handleInputBlur}
            className="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all duration-200 outline-none text-gray-700"
          >
            <option value="">No preference</option>
            <option value="software_engineering">Software Engineering</option>
            <option value="data">Data Science / Analytics</option>
            <option value="ai_ml">AI / Machine Learning</option>
            <option value="devops">DevOps / Cloud</option>
            <option value="qa">QA / Testing</option>
            <option value="ui_ux">UI / UX Design</option>
          </select>
        </label>
      </div>

      {/* Skills Selection */}
      <div>
        <label>
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaTrophy className="text-purple-600" />
            <span>Your Skills</span>
          </div>
          <SkillSelector selected={selectedSkills} onChange={onSkillsChange} />
        </label>
      </div>

      {/* Submit Button */}
      <div className="mt-2">
        <button
          type="submit"
          disabled={loading || selectedSkills.length === 0}
          className={`w-full px-8 py-4 text-white rounded-xl text-base font-semibold transition-all duration-300 shadow-lg flex items-center justify-center gap-2 ${
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
