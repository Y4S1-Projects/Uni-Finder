import React, { useEffect, useMemo } from "react";
import SkillSelector from "./SkillSelector";
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
  { value: "0", label: "Student / No experience" },
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
  values,
  handleChange,
  selectedSkills,
  onSkillsChange,
  onSubmit,
  loading,
  experienceLevel,
  currentStatus,
  preferredDomain,
  educationLevel,
  careerGoal,
  title,
  subtitle,
  submitLabel,
  loadingLabel,
}) {
  const formTitle = title || "Career Profile Assessment";
  const formSubtitle =
    subtitle ||
    "Complete your profile to get personalized career recommendations";
  const submitText = submitLabel || "Find My Best Career Matches";
  const submitLoadingText = loadingLabel || "Analyzing Your Profile...";
  const formValues = useMemo(
    () =>
      values || {
        skills: selectedSkills || [],
        experience_level: experienceLevel?.value || "",
        current_status: currentStatus?.value || "",
        preferred_domain: preferredDomain?.value || "",
        education_level: educationLevel?.value || "",
        career_goal: careerGoal?.value || "",
      },
    [
      values,
      selectedSkills,
      experienceLevel?.value,
      currentStatus?.value,
      preferredDomain?.value,
      educationLevel?.value,
      careerGoal?.value,
    ],
  );
  const setFieldValue = (name, value) => {
    if (typeof handleChange === "function") {
      handleChange({ target: { name, value } });
      return;
    }

    const fieldMap = {
      experience_level: experienceLevel,
      current_status: currentStatus,
      preferred_domain: preferredDomain,
      education_level: educationLevel,
      career_goal: careerGoal,
    };

    if (name === "skills" && typeof onSkillsChange === "function") {
      onSkillsChange(value);
      return;
    }

    fieldMap[name]?.setValue?.(value);
  };
  const selectedSkillValues = formValues.skills || [];

  useEffect(() => {
    console.log("FORM STATE:", formValues);
  }, [formValues]);

  // Check if all required fields are filled
  const isFormValid =
    formValues.experience_level &&
    formValues.current_status &&
    formValues.education_level &&
    formValues.career_goal &&
    selectedSkillValues.length >= 5;

  const handleCareerGoalSelect = (selected) => {
    setFieldValue("career_goal", selected?.id || "");
  };

  const handleStatusSelect = (selected) => {
    setFieldValue("current_status", selected?.value || "");
  };

  const handleDomainSelect = (selected) => {
    setFieldValue("preferred_domain", selected?.id || "");
  };

  // Get selected option object for dropdowns
  const selectedCareerGoal = CAREER_GOAL_OPTIONS.find(
    (opt) => opt.id === formValues.career_goal,
  );
  const selectedStatus = STATUS_OPTIONS.find(
    (opt) => opt.value === formValues.current_status,
  );
  const selectedDomain = DOMAIN_OPTIONS.find(
    (opt) => opt.id === formValues.preferred_domain,
  );

  return (
    <div className="relative z-10">
      <div className="absolute inset-0 rounded-3xl blur-xl opacity-70 -z-10 bg-gradient-to-br from-indigo-50/60 via-white to-indigo-50/60" />

      <form
        onSubmit={onSubmit}
        className="relative p-6 md:p-10 transition-all duration-500 border shadow-lg bg-white/90 backdrop-blur-xl rounded-2xl border-gray-100 hover:shadow-xl space-y-6"
      >
        <div className="pb-6 border-b border-gray-100 flex flex-wrap items-center gap-4 justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 md:text-3xl">
              {formTitle}
            </h2>
            <p className="mt-2 text-sm text-gray-600 md:text-base">
              {formSubtitle}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:gap-6 md:grid-cols-2">
          <div className="p-6 transition-all duration-300 border rounded-2xl shadow-md hover:shadow-lg bg-white border-gray-200">
            <div className="flex items-center gap-3 mb-4 text-lg font-bold text-gray-900">
              <div className="p-2 rounded-lg shadow-md bg-indigo-600">
                <FaBriefcase className="text-xl text-white" />
              </div>
              <span>Experience Level</span>
              <span className="text-red-500">*</span>
            </div>
            <div className="flex flex-col h-full gap-3">
              {EXPERIENCE_OPTIONS.map((option, index) => (
                <button
                  key={`${option.value}-${index}`}
                  type="button"
                  name="experience_level"
                  value={option.value}
                  onClick={() =>
                    setFieldValue("experience_level", option.value)
                  }
                  onBlur={experienceLevel.handleInputBlur}
                  className={`px-5 py-3 font-semibold transition-all duration-300 border border-transparent shadow-sm rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/40 hover:shadow-md ${
                    formValues.experience_level === option.value
                      ? "bg-indigo-600 text-white shadow-md scale-[1.01]"
                      : "bg-white/90 text-gray-700 border-gray-200 hover:border-indigo-200"
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <p className="flex items-center gap-1 mt-3 text-sm text-red-500 h-4">
              {experienceLevel.hasError ? (
                <>
                  <span className="text-red-500">⚠</span>
                  {experienceLevel.errorMessage}
                </>
              ) : (
                ""
              )}
            </p>
          </div>

          <div className="p-6 transition-all duration-300 border rounded-2xl shadow-md hover:shadow-lg bg-white border-gray-200">
            <div className="flex items-center gap-3 mb-4 text-lg font-bold text-gray-900">
              <div className="p-2 rounded-lg shadow-md bg-indigo-600">
                <FaGraduationCap className="text-xl text-white" />
              </div>
              <span>Highest Education</span>
              <span className="text-red-500">*</span>
            </div>
            <div className="flex flex-col h-full gap-3">
              {EDUCATION_OPTIONS.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  name="education_level"
                  value={option.id}
                  onClick={() => setFieldValue("education_level", option.id)}
                  onBlur={educationLevel.handleInputBlur}
                  className={`px-5 py-3 font-semibold transition-all duration-300 border border-transparent shadow-sm rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/40 hover:shadow-md ${
                    formValues.education_level === option.id
                      ? "bg-indigo-600 text-white shadow-md scale-[1.01]"
                      : "bg-white/90 text-gray-700 border-gray-200 hover:border-indigo-200"
                  }`}
                >
                  {option.name}
                </button>
              ))}
            </div>
            <p className="flex items-center gap-1 mt-3 text-sm text-red-500 h-4">
              {educationLevel.hasError ? (
                <>
                  <span className="text-red-500">⚠</span>
                  {educationLevel.errorMessage}
                </>
              ) : (
                ""
              )}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:gap-6 md:grid-cols-2">
          <div className="p-6 transition-all duration-300 border rounded-2xl shadow-md hover:shadow-lg bg-white border-gray-200 relative z-50">
            <Dropdown
              name="current_status"
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
              buttonClassName="bg-white/90 text-gray-700 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/50"
              dropdownClassName="z-[120] absolute"
              optionClassName="text-gray-700 hover:bg-indigo-50"
              prefixIcon={
                <div className="p-2 rounded-lg shadow-md bg-indigo-600">
                  <FaUser className="text-lg text-white" />
                </div>
              }
            />
          </div>

          <div className="p-6 transition-all duration-300 border rounded-2xl shadow-md hover:shadow-lg bg-white border-gray-200 relative z-50">
            <Dropdown
              name="career_goal"
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
              buttonClassName="bg-white/90 text-gray-700 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/50"
              dropdownClassName="z-[120] absolute"
              optionClassName="text-gray-700 hover:bg-indigo-50"
              prefixIcon={
                <div className="p-2 rounded-lg shadow-md bg-indigo-600">
                  <FaRocket className="text-lg text-white" />
                </div>
              }
            />
          </div>

          <div className="p-6 transition-all duration-300 border md:col-span-2 rounded-2xl shadow-md hover:shadow-lg bg-white border-gray-200 relative z-40">
            <Dropdown
              name="preferred_domain"
              label={
                <div className="flex items-center gap-2">
                  <span>Preferred Domain</span>
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-700">
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
              buttonClassName="bg-white/90 text-gray-700 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/60 transition-all duration-200 ease-in-out"
              dropdownClassName="z-[120] absolute max-h-60 overflow-y-auto"
              optionClassName="text-gray-700 transition-all duration-200 ease-in-out hover:bg-indigo-50"
              prefixIcon={
                <div className="p-2 rounded-lg shadow-md bg-indigo-600">
                  <FaChartLine className="text-lg text-white" />
                </div>
              }
            />

            <p className="mt-3 text-sm leading-relaxed text-gray-600">
              Choose "No Preference" for unbiased AI recommendations based
              purely on your skills. Or select a specific domain if you know
              your career direction.
            </p>

            {!formValues.preferred_domain && (
              <div className="flex items-center gap-3 p-4 mt-4 border border-blue-200 rounded-lg bg-blue-50">
                <div className="flex-shrink-0 p-2 bg-blue-100 rounded-full">
                  <FaChartLine className="text-lg text-blue-600" />
                </div>
                <p className="m-0 text-sm text-blue-800">
                  AI will analyze your skills and recommend the best-fit careers
                  across all domains.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="relative z-30 w-full p-6 md:p-8 transition-all duration-300 border rounded-2xl shadow-md hover:shadow-lg bg-white border-gray-200">
          <div className="block w-full">
            <div className="flex items-center gap-3 mb-4 text-xl font-bold text-gray-800">
              <div className="p-3 rounded-lg shadow-md bg-indigo-600">
                <FaTrophy className="text-2xl text-white" />
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <span>Your Skills</span>
                <span className="text-red-500">*</span>
                <span className="px-3 py-1 text-sm font-semibold rounded-full bg-indigo-100 text-indigo-700">
                  Select at least 5 skills
                </span>
              </div>
            </div>
            <div className="w-full relative z-10">
              <SkillSelector
                selectedSkills={selectedSkillValues}
                onChange={(skills) => setFieldValue("skills", skills)}
              />
            </div>
            {selectedSkillValues.length > 0 &&
              selectedSkillValues.length < 5 && (
                <p className="flex items-center gap-2 p-3 mt-3 text-sm text-red-500 border border-red-200 rounded-lg bg-red-50">
                  <span className="text-lg text-red-500">⚠</span>
                  <span>
                    Please select at least 5 skills (currently selected:{" "}
                    <span className="font-bold">
                      {selectedSkillValues.length}
                    </span>
                    )
                  </span>
                </p>
              )}
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={loading || !isFormValid}
            className={`w-full px-8 py-5 text-white rounded-2xl border border-transparent text-lg font-bold transition-all duration-300 flex items-center justify-center gap-3 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-500/40 ${
              !isFormValid || loading
                ? "bg-gray-400 cursor-not-allowed opacity-70 hover:scale-100"
                : "bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.01] active:scale-[0.99]"
            }`}
          >
            {loading ? (
              <>
                <FaSearch className="text-2xl animate-spin" />
                <span>{submitLoadingText}</span>
              </>
            ) : (
              <>
                <FaTrophy className="text-2xl" />
                <span>{submitText}</span>
              </>
            )}
          </button>
          {!isFormValid && !loading && (
            <p className="p-3 mt-4 text-sm text-center text-gray-600 border border-gray-100 rounded-xl bg-gradient-to-r from-gray-50/80 to-blue-50/50">
              💡 Please fill all required fields and select at least 5 skills to
              continue
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
