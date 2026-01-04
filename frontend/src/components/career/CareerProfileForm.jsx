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
  { id: "software_engineering", name: "Software Engineering" },
  { id: "data", name: "Data Science / Analytics" },
  { id: "ai_ml", name: "AI / Machine Learning" },
  { id: "devops", name: "DevOps / Cloud" },
  { id: "qa", name: "QA / Testing" },
  { id: "ui_ux", name: "UI / UX Design" },
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

  const handleDomainSelect = (selected) => {
    preferredDomain.setValue(selected?.id || "");
  };

  // Get selected option object for dropdowns
  const selectedEducation = EDUCATION_OPTIONS.find(
    (opt) => opt.id === educationLevel.value
  );
  const selectedCareerGoal = CAREER_GOAL_OPTIONS.find(
    (opt) => opt.id === careerGoal.value
  );
  const selectedDomain = DOMAIN_OPTIONS.find(
    (opt) => opt.id === preferredDomain.value
  );

  return (
    <form
      onSubmit={onSubmit}
      className="p-8 bg-white rounded-2xl border-2 border-purple-200 shadow-lg"
    >
      {/* Two-column grid for inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Experience Level - Radio Group */}
        <div>
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaBriefcase className="text-purple-600" />
            <span>Experience Level</span>
            <span className="text-red-500">*</span>
          </div>
          <div className="space-y-2">
            {EXPERIENCE_OPTIONS.map((option) => (
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
        </div>

        {/* Current Status - Button Group */}
        <div>
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaUser className="text-purple-600" />
            <span>Current Status</span>
            <span className="text-red-500">*</span>
          </div>
          <div className="flex gap-3">
            {STATUS_OPTIONS.map((option) => (
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

        {/* Education Level - Dropdown */}
        <div>
          <Dropdown
            label="Highest Education"
            labelClassName="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3"
            isRequired={true}
            placeholder="Select education level"
            options={EDUCATION_OPTIONS}
            defaultOption={selectedEducation}
            displayKey="name"
            idKey="id"
            onSelect={handleEducationSelect}
            onBlur={educationLevel.handleInputBlur}
            error={educationLevel.hasError ? educationLevel.errorMessage : null}
            buttonClassName="bg-white text-gray-700 border-2 border-gray-200 focus:border-purple-400 hover:border-gray-300"
            dropdownClassName="bg-white border-2 border-purple-200"
            optionClassName="text-gray-700 hover:bg-purple-50"
            prefixIcon={<FaGraduationCap className="text-purple-600" />}
          />
        </div>

        {/* Career Goal - Dropdown */}
        <div>
          <Dropdown
            label="Career Goal"
            labelClassName="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3"
            isRequired={true}
            placeholder="What is your goal?"
            options={CAREER_GOAL_OPTIONS}
            defaultOption={selectedCareerGoal}
            displayKey="name"
            idKey="id"
            onSelect={handleCareerGoalSelect}
            onBlur={careerGoal.handleInputBlur}
            error={careerGoal.hasError ? careerGoal.errorMessage : null}
            buttonClassName="bg-white text-gray-700 border-2 border-gray-200 focus:border-purple-400 hover:border-gray-300"
            dropdownClassName="bg-white border-2 border-purple-200"
            optionClassName="text-gray-700 hover:bg-purple-50"
            prefixIcon={<FaRocket className="text-purple-600" />}
          />
        </div>

        {/* Preferred Domain - Dropdown (Optional) */}
        <div>
          <Dropdown
            label={
              <>
                Preferred Domain
                <span className="text-gray-500 text-sm font-normal ml-2">
                  (Optional)
                </span>
              </>
            }
            labelClassName="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3"
            placeholder="No preference"
            options={DOMAIN_OPTIONS}
            defaultOption={selectedDomain}
            displayKey="name"
            idKey="id"
            onSelect={handleDomainSelect}
            onBlur={preferredDomain.handleInputBlur}
            buttonClassName="bg-white text-gray-700 border-2 border-gray-200 focus:border-purple-400 hover:border-gray-300"
            dropdownClassName="bg-white border-2 border-purple-200"
            optionClassName="text-gray-700 hover:bg-purple-50"
            prefixIcon={<FaChartLine className="text-purple-600" />}
          />
        </div>
      </div>

      {/* Skills Selection - Full Width */}
      <div>
        <label>
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-3">
            <FaTrophy className="text-purple-600" />
            <span>Your Skills</span>
            <span className="text-red-500">*</span>
            <span className="text-gray-500 text-sm font-normal ml-2">
              (Select at least 5 skills)
            </span>
          </div>
          <SkillSelector selected={selectedSkills} onChange={onSkillsChange} />
          {selectedSkills.length > 0 && selectedSkills.length < 5 && (
            <p className="text-red-500 text-sm mt-2">
              Please select at least 5 skills (currently selected:{" "}
              {selectedSkills.length})
            </p>
          )}
        </label>
      </div>

      {/* Submit Button */}
      <div className="mt-6">
        <button
          type="submit"
          disabled={loading || !isFormValid}
          className={`w-full px-8 py-4 text-white rounded-xl text-base font-semibold transition-all duration-300 shadow-lg flex items-center justify-center gap-2 ${
            !isFormValid
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
        {!isFormValid && !loading && (
          <p className="text-gray-500 text-sm mt-3 text-center">
            Please fill all required fields and select at least 5 skills
          </p>
        )}
      </div>
    </form>
  );
}
