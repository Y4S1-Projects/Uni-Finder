import React from "react";
import SkillSelector from "./SkillSelector";
import Input from "../Form/Input";
import Dropdown from "../Form/Dropdown";
import {
  FaChartLine,
  FaSearch,
  FaTrophy,
  FaUser,
  FaGraduationCap,
  FaBriefcase,
  FaRocket,
} from "react-icons/fa";

const EXPERIENCE_OPTIONS = [
  { value: "student", label: "Student / No experience" },
  { value: "0-1", label: "0–1 years" },
  { value: "1-3", label: "1–3 years" },
  { value: "3-5", label: "3–5 years" },
  { value: "5+", label: "5+ years" },
];

const STATUS_OPTIONS = [
  { value: "student", label: "Student" },
  { value: "graduate", label: "Graduate" },
  { value: "working", label: "Working Professional" },
];

const EDUCATION_OPTIONS = [
  { id: "al", name: "A/L" },
  { id: "diploma", name: "Diploma" },
  { id: "hnd", name: "HND" },
  { id: "bachelors", name: "Bachelor's Degree" },
  { id: "masters", name: "Master's Degree" },
];

const CAREER_GOAL_OPTIONS = [
  { id: "first_job", name: "Get first job" },
  { id: "switch_career", name: "Switch career" },
  { id: "get_promoted", name: "Get promoted" },
];

const DOMAIN_OPTIONS = [
  { id: "", name: "No Preference - Let AI Decide (Recommended)" },
  { id: "software_engineering", name: "Software Engineering" },
  { id: "frontend_engineering", name: "Frontend Engineering" },
  { id: "backend_engineering", name: "Backend Engineering" },
  { id: "fullstack_engineering", name: "Full-Stack Engineering" },
  { id: "data_engineering", name: "Data Engineering" },
  { id: "data_science", name: "Data Science" },
  { id: "ai_ml", name: "AI / Machine Learning" },
  { id: "devops", name: "DevOps / SRE" },
  { id: "cloud_engineering", name: "Cloud Engineering" },
  { id: "security", name: "Security / Cybersecurity" },
  { id: "qa", name: "QA / Testing" },
  { id: "mobile_engineering", name: "Mobile Development" },
  { id: "ui_ux", name: "UI/UX Design" },
  { id: "product_management", name: "Product Management" },
  { id: "business_analysis", name: "Business Analysis" },
  { id: "project_management", name: "Project Management" },
  { id: "technical_writing", name: "Technical Writing" },
  { id: "blockchain_web3", name: "Blockchain / Web3" },
  { id: "game_development", name: "Game Development" },
  { id: "embedded_systems", name: "Embedded Systems" },
];

export default function CareerProfileForm({
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
  // Check if all required fields are filled
  const isFormValid =
    experienceLevel.value &&
    currentStatus.value &&
    educationLevel.value &&
    careerGoal.value &&
    selectedSkills.length >= 5;

  // Convert dropdown selection to string value
  const handleEducationSelect = (selected) => {
    educationLevel.setValue(selected?.id || "");
  };

  const handleCareerGoalSelect = (selected) => {
    careerGoal.setValue(selected?.id || "");
  };

  const handleStatusSelect = (selected) => {
    currentStatus.setValue(selected?.value || "");
  };

  const handleDomainSelect = (selected) => {
    preferredDomain.setValue(selected?.id || "");
  };

  // Get selected option object for dropdowns
  const selectedEducation = EDUCATION_OPTIONS.find(
    (opt) => opt.id === educationLevel.value,
  );
  const selectedCareerGoal = CAREER_GOAL_OPTIONS.find(
    (opt) => opt.id === careerGoal.value,
  );
  const selectedStatus = STATUS_OPTIONS.find(
    (opt) => opt.value === currentStatus.value,
  );
  const selectedDomain = DOMAIN_OPTIONS.find(
    (opt) => opt.id === preferredDomain.value,
  );

  return (
    <div className="relative">
      {/* Gradient Background Container */}
      <div
        className="absolute inset-0 rounded-3xl blur-xl opacity-70 -z-10"
        style={{
          background:
            "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)",
        }}
      />

      <form
        onSubmit={onSubmit}
        className="relative p-8 md:p-10 bg-white/95 backdrop-blur-sm rounded-3xl border border-purple-200/50 shadow-2xl hover:shadow-purple-300/50 transition-all duration-500"
      >
        {/* Form Header with Gradient */}
        <div
          className="mb-8 pb-6 border-b-2"
          style={{
            borderImage: "linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1",
          }}
        >
          <h2
            className="text-2xl md:text-3xl font-bold bg-clip-text text-transparent"
            style={{
              backgroundImage:
                "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            }}
          >
            Career Profile Assessment
          </h2>
          <p className="text-gray-600 mt-2 text-sm md:text-base">
            Complete your profile to get personalized career recommendations
          </p>
        </div>

        {/* Profile Basics Row: Experience Level & Highest Education */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Experience Level - Button Group */}
          <div
            className="p-6 rounded-2xl border transition-all duration-300 hover:shadow-lg"
            style={{
              background:
                "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
              borderColor: "rgba(102, 126, 234, 0.3)",
            }}
          >
            <div className="flex items-center gap-3 text-gray-800 text-lg font-bold mb-4">
              <div
                className="p-2 rounded-lg shadow-md"
                style={{
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                }}
              >
                <FaBriefcase className="text-white text-xl" />
              </div>
              <span>Experience Level</span>
              <span className="text-red-500">*</span>
            </div>
            <div className="flex flex-col gap-3 h-full">
              {EXPERIENCE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => experienceLevel.setValue(option.value)}
                  onBlur={experienceLevel.handleInputBlur}
                  className="py-3 px-5 rounded-xl font-semibold transition-all duration-300 border-2 shadow-sm focus:outline-none hover:shadow-md"
                  style={
                    experienceLevel.value === option.value
                      ? {
                          background:
                            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          color: "white",
                          borderColor: "transparent",
                          transform: "scale(1.02)",
                          boxShadow: "0 10px 15px -3px rgba(102, 126, 234, 0.3)"
                        }
                      : {
                          background: "white",
                          color: "#374151",
                          borderColor: "#e5e7eb",
                        }
                  }
                >
                  {option.label}
                </button>
              ))}
            </div>
            {experienceLevel.hasError && (
              <p className="text-red-500 text-sm mt-3 flex items-center gap-1">
                <span className="text-red-500">⚠</span>
                {experienceLevel.errorMessage}
              </p>
            )}
          </div>

          {/* Highest Education - Button Group */}
          <div
            className="p-6 rounded-2xl border transition-all duration-300 hover:shadow-lg"
            style={{
              background:
                "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
              borderColor: "rgba(102, 126, 234, 0.3)",
            }}
          >
            <div className="flex items-center gap-3 text-gray-800 text-lg font-bold mb-4">
              <div
                className="p-2 rounded-lg shadow-md"
                style={{
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                }}
              >
                <FaGraduationCap className="text-white text-xl" />
              </div>
              <span>Highest Education</span>
              <span className="text-red-500">*</span>
            </div>
            <div className="flex flex-col gap-3 h-full">
              {EDUCATION_OPTIONS.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => educationLevel.setValue(option.id)}
                  onBlur={educationLevel.handleInputBlur}
                  className="py-3 px-5 rounded-xl font-semibold transition-all duration-300 border-2 shadow-sm focus:outline-none hover:shadow-md"
                  style={
                    educationLevel.value === option.id
                      ? {
                          background:
                            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          color: "white",
                          borderColor: "transparent",
                          transform: "scale(1.02)",
                          boxShadow: "0 10px 15px -3px rgba(102, 126, 234, 0.3)"
                        }
                      : {
                          background: "white",
                          color: "#374151",
                          borderColor: "#e5e7eb",
                        }
                  }
                >
                  {option.name}
                </button>
              ))}
            </div>
            {educationLevel.hasError && (
              <p className="text-red-500 text-sm mt-3 flex items-center gap-1">
                <span className="text-red-500">⚠</span>
                {educationLevel.errorMessage}
              </p>
            )}
          </div>
        </div>

        {/* Status & Goals Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Current Status - Dropdown */}
          <div
            className="p-6 rounded-2xl border transition-all duration-300 hover:shadow-lg"
            style={{
              background:
                "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
              borderColor: "rgba(102, 126, 234, 0.3)",
            }}
          >
            <Dropdown
              label="Current Status"
              labelClassName="flex items-center gap-3 text-gray-800 text-lg font-bold mb-4"
              isRequired={true}
              placeholder="Select current status"
              options={STATUS_OPTIONS}
              defaultOption={selectedStatus}
              displayKey="label"
              idKey="value"
              onSelect={handleStatusSelect}
              onBlur={currentStatus.handleInputBlur}
              error={currentStatus.hasError ? currentStatus.errorMessage : null}
              buttonClassName="bg-white text-gray-700 border-2 border-gray-200 hover:border-purple-400 hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 focus:border-purple-500 focus:shadow-lg transition-all duration-300"
              dropdownClassName="bg-white border-2 border-purple-200 shadow-2xl"
              optionClassName="text-gray-700 hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50"
              prefixIcon={
                <div
                  className="p-2 rounded-lg shadow-md"
                  style={{
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  }}
                >
                  <FaUser className="text-white text-lg" />
                </div>
              }
            />
          </div>





          {/* Career Goal - Dropdown */}
          <div
            className="p-6 rounded-2xl border transition-all duration-300 hover:shadow-lg"
            style={{
              background:
                "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
              borderColor: "rgba(102, 126, 234, 0.3)",
            }}
          >
            <Dropdown
              label="Career Goal"
              labelClassName="flex items-center gap-3 text-gray-800 text-lg font-bold mb-4"
              isRequired={true}
              placeholder="What is your goal?"
              options={CAREER_GOAL_OPTIONS}
              defaultOption={selectedCareerGoal}
              displayKey="name"
              idKey="id"
              onSelect={handleCareerGoalSelect}
              onBlur={careerGoal.handleInputBlur}
              error={careerGoal.hasError ? careerGoal.errorMessage : null}
              buttonClassName="bg-white text-gray-700 border-2 border-gray-200 hover:border-purple-400 hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 focus:border-purple-500 focus:shadow-lg transition-all duration-300"
              dropdownClassName="bg-white border-2 border-purple-200 shadow-2xl"
              optionClassName="text-gray-700 hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50"
              prefixIcon={
                <div
                  className="p-2 rounded-lg shadow-md"
                  style={{
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  }}
                >
                  <FaRocket className="text-white text-lg" />
                </div>
              }
            />
          </div>

          {/* Preferred Domain - Dropdown (Optional) */}
          <div
            className="md:col-span-2 p-6 rounded-2xl border transition-all duration-300 hover:shadow-lg"
            style={{
              background:
                "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
              borderColor: "rgba(102, 126, 234, 0.3)",
            }}
          >
            <Dropdown
              label={
                <div className="flex items-center gap-2">
                  <span>Preferred Domain</span>
                  <span
                    className="px-2 py-1 text-xs font-semibold rounded-full"
                    style={{
                      background:
                        "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                      color: "#667eea",
                    }}
                  >
                    Optional
                  </span>
                </div>
              }
              labelClassName="flex items-center gap-3 text-gray-800 text-lg font-bold mb-4"
              placeholder="No Preference - Let AI Decide"
              options={DOMAIN_OPTIONS}
              defaultOption={selectedDomain}
              displayKey="name"
              idKey="id"
              onSelect={handleDomainSelect}
              onBlur={preferredDomain.handleInputBlur}
              buttonClassName="bg-white text-gray-700 border-2 border-gray-200 hover:border-blue-400 hover:bg-gradient-to-r hover:from-blue-50 hover:to-cyan-50 focus:border-blue-500 focus:shadow-lg transition-all duration-300"
              dropdownClassName="bg-white border-2 border-blue-200 shadow-2xl max-h-60 overflow-y-auto"
              optionClassName="text-gray-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-cyan-50"
              prefixIcon={
                <div
                  className="p-2 rounded-lg shadow-md"
                  style={{
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  }}
                >
                  <FaChartLine className="text-white text-lg" />
                </div>
              }
            />

            {/* Help text and info banner */}
            <p className="text-sm text-gray-600 mt-3 leading-relaxed">
              Choose "No Preference" for unbiased AI recommendations based
              purely on your skills. Or select a specific domain if you know
              your career direction.
            </p>

            {/* Info banner when No Preference is selected */}
            {!preferredDomain.value && (
              <div
                className="flex items-center gap-3 p-4 rounded-lg mt-4 border"
                style={{
                  background:
                    "linear-gradient(135deg, rgba(239, 246, 255, 0.9) 0%, rgba(224, 242, 254, 0.9) 100%)",
                  borderColor: "#bfdbfe",
                }}
              >
                <div className="flex-shrink-0 bg-blue-100 p-2 rounded-full">
                  <FaChartLine className="text-blue-600 text-lg" />
                </div>
                <p className="m-0 text-blue-800 text-sm">
                  AI will analyze your skills and recommend the best-fit careers
                  across all domains.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Skills Selection - Full Width */}
        <div
          className="w-full p-8 rounded-2xl border transition-all duration-300 hover:shadow-lg mb-8"
          style={{
            background:
              "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
            borderColor: "rgba(102, 126, 234, 0.3)",
          }}
        >
          <div className="w-full block">
            <div className="flex items-center gap-3 text-gray-800 text-xl font-bold mb-4">
              <div
                className="p-3 rounded-lg shadow-md"
                style={{
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                }}
              >
                <FaTrophy className="text-white text-2xl" />
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <span>Your Skills</span>
                <span className="text-red-500">*</span>
                <span
                  className="px-3 py-1 text-sm font-semibold rounded-full"
                  style={{
                    background:
                      "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                    color: "#667eea",
                  }}
                >
                  Select at least 5 skills
                </span>
              </div>
            </div>
            <div className="w-full">
              <SkillSelector
                selected={selectedSkills}
                onChange={onSkillsChange}
              />
            </div>
            {selectedSkills.length > 0 && selectedSkills.length < 5 && (
              <p className="text-red-500 text-sm mt-3 flex items-center gap-2 bg-red-50 p-3 rounded-lg border border-red-200">
                <span className="text-red-500 text-lg">⚠</span>
                <span>
                  Please select at least 5 skills (currently selected:{" "}
                  <span className="font-bold">{selectedSkills.length}</span>)
                </span>
              </p>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="mt-2">
          <button
            type="submit"
            disabled={loading || !isFormValid}
            className="w-full px-8 py-5 text-white rounded-2xl text-lg font-bold transition-all duration-500 flex items-center justify-center gap-3 shadow-xl hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
            style={
              !isFormValid
                ? {
                    background: "#9ca3af",
                    cursor: "not-allowed",
                    opacity: 0.7,
                  }
                : {
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    boxShadow: "0 10px 40px rgba(102, 126, 234, 0.3)",
                  }
            }
          >
            {loading ? (
              <>
                <FaSearch className="animate-spin text-2xl" />
                <span>Analyzing Your Profile...</span>
              </>
            ) : (
              <>
                <FaTrophy className="text-2xl" />
                <span>Find My Best Career Matches</span>
              </>
            )}
          </button>
          {!isFormValid && !loading && (
            <p className="text-gray-600 text-sm mt-4 text-center bg-gradient-to-r from-gray-50 to-blue-50 p-3 rounded-lg border border-gray-200">
              💡 Please fill all required fields and select at least 5 skills to
              continue
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
