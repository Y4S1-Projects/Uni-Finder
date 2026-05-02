import React from "react";
import CareerProfileForm from "./CareerProfileForm";
import { useInput } from "../../hooks/use-input";
import {
  validateExperienceLevel,
  validateCurrentStatus,
  validatePreferredDomain,
  validateEducationLevel,
  validateCareerGoal,
} from "../../utils/validationUtils";
import { FaTimes, FaUserAstronaut } from "react-icons/fa";

const EMPTY_PROFILE = {
  name: "",
  skills: [],
  experience_level: "",
  current_status: "",
  education_level: "",
  career_goal: "",
  preferred_domain: "",
};

function normalizeSkills(skills) {
  return (skills || [])
    .map((skill) => {
      if (!skill) return "";
      if (typeof skill === "string" || typeof skill === "number")
        return String(skill);
      return String(skill.id || skill.skill_id || skill.skillId || "");
    })
    .filter(Boolean);
}

function mapExperienceFromProfile(value) {
  if (value === "0") return "student";
  return value || "";
}

export default function ProfileModal({
  isOpen,
  mode = "create",
  initialProfile,
  onClose,
  onSubmit,
  loading = false,
}) {
  const baseProfile = initialProfile || EMPTY_PROFILE;
  const [name, setName] = React.useState(baseProfile.name || "");
  const [nameTouched, setNameTouched] = React.useState(false);
  const [selectedSkills, setSelectedSkills] = React.useState(
    normalizeSkills(baseProfile.skills),
  );

  const experienceLevel = useInput(
    mapExperienceFromProfile(baseProfile.experience_level),
    validateExperienceLevel,
  );
  const currentStatus = useInput(
    baseProfile.current_status || "",
    validateCurrentStatus,
  );
  const preferredDomain = useInput(
    baseProfile.preferred_domain || "",
    validatePreferredDomain,
  );
  const educationLevel = useInput(
    baseProfile.education_level || "",
    validateEducationLevel,
  );
  const careerGoal = useInput(
    baseProfile.career_goal || "",
    validateCareerGoal,
  );

  React.useEffect(() => {
    if (!isOpen) return;
    const profile = initialProfile || EMPTY_PROFILE;
    setName(profile.name || "");
    setNameTouched(false);
    setSelectedSkills(normalizeSkills(profile.skills));
    experienceLevel.setValue(
      mapExperienceFromProfile(profile.experience_level),
    );
    currentStatus.setValue(profile.current_status || "");
    preferredDomain.setValue(profile.preferred_domain || "");
    educationLevel.setValue(profile.education_level || "");
    careerGoal.setValue(profile.career_goal || "");
  }, [isOpen, initialProfile]);

  if (!isOpen) return null;

  const isEdit = mode === "edit";
  const nameError =
    nameTouched && !name.trim() ? "Profile name is required" : "";

  const handleSubmit = (event) => {
    event.preventDefault();
    setNameTouched(true);

    experienceLevel.handleInputBlur();
    currentStatus.handleInputBlur();
    educationLevel.handleInputBlur();
    careerGoal.handleInputBlur();

    if (!name.trim()) return;
    if (
      experienceLevel.hasError ||
      currentStatus.hasError ||
      educationLevel.hasError ||
      careerGoal.hasError ||
      selectedSkills.length < 5
    ) {
      return;
    }

    onSubmit({
      name: name.trim(),
      skills: selectedSkills,
      experience_level: experienceLevel.value,
      current_status: currentStatus.value,
      preferred_domain: preferredDomain.value,
      education_level: educationLevel.value,
      career_goal: careerGoal.value,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4 py-8">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="relative p-6 md:p-8 bg-white rounded-3xl shadow-2xl border border-purple-100">
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/90 border border-gray-100 shadow-sm hover:shadow-md transition focus:outline-none focus:ring-2 focus:ring-purple-500/40"
            aria-label="Close"
          >
            <FaTimes />
          </button>

          <div className="mb-6">
            <div className="flex items-center gap-3">
              <span className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 text-white shadow-md">
                <FaUserAstronaut />
              </span>
              <div>
                <h3 className="text-2xl font-bold text-gray-800">
                  {isEdit ? "Edit Career Profile" : "Create New Career Profile"}
                </h3>
                <p className="text-gray-600">
                  {isEdit
                    ? "Update this profile and keep your recommendations aligned."
                    : "Save a new identity to reuse your best recommendations."}
                </p>
              </div>
            </div>

            <div className="mt-6">
              <label className="text-sm font-semibold text-gray-700">
                Profile Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(event) => {
                  setName(event.target.value);
                  if (!nameTouched) setNameTouched(true);
                }}
                onBlur={() => setNameTouched(true)}
                placeholder="e.g., Frontend Explorer"
                className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-700 bg-white/90 focus:outline-none focus:ring-2 focus:ring-purple-500/40 focus:border-purple-200/80 transition"
              />
              {nameError && (
                <p className="mt-2 text-sm text-red-500">{nameError}</p>
              )}
            </div>
          </div>

          <CareerProfileForm
            selectedSkills={selectedSkills}
            onSkillsChange={setSelectedSkills}
            onSubmit={handleSubmit}
            loading={loading}
            experienceLevel={experienceLevel}
            currentStatus={currentStatus}
            preferredDomain={preferredDomain}
            educationLevel={educationLevel}
            careerGoal={careerGoal}
            title="Profile Details"
            subtitle="Use the same career profile form to craft a reusable identity."
            submitLabel={isEdit ? "Save Profile Changes" : "Create Profile"}
            loadingLabel={isEdit ? "Saving Profile..." : "Creating Profile..."}
          />
        </div>
      </div>
    </div>
  );
}
