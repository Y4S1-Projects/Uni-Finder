import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import CareerProfileForm from "../components/career/CareerProfileForm";
import {
  CareerRecommendationCard,
  CareerDetailModal,
  RecommendationsSummary,
  HowItWorks,
  CareerButton,
  ProfileSectionCard,
  NativeSelectField,
} from "../components/career";
import {
  useCareerRecommendations,
  useCareerDetail,
} from "../hooks/useCareerRecommendations";
import {
  validateExperienceLevel,
  validateCurrentStatus,
  validatePreferredDomain,
  validateEducationLevel,
  validateCareerGoal,
} from "../utils/validationUtils";
import { useInput } from "../hooks/use-input";
import {
  getProfiles,
  createProfile,
  updateProfile,
  deleteProfile,
} from "../api/careerProfileApi";
import { FaChartLine, FaPlus, FaSave, FaTrash } from "react-icons/fa";

const MAX_PROFILES = 3;

const defaultForm = {
  name: "",
  skills: [],
  experience_level: "",
  current_status: "",
  preferred_domain: "",
  education_level: "",
  career_goal: "",
};

function normalizeSkills(skills) {
  return (skills || [])
    .map((skill) => {
      if (!skill) return "";
      if (typeof skill === "string" || typeof skill === "number") {
        return String(skill);
      }
      return String(skill.id || skill.skill_id || skill.skillId || "");
    })
    .filter(Boolean);
}

function mapProfileToFormData(profile) {
  return {
    name: profile?.name || "",
    skills: normalizeSkills(profile?.skills),
    experience_level: profile?.experience_level || "",
    current_status: profile?.current_status || "",
    preferred_domain: profile?.preferred_domain || "",
    education_level: profile?.education_level || "",
    career_goal: profile?.career_goal || "",
  };
}

function buildProfilePayload(formData) {
  const payload = {
    name: (formData.name || "").trim(),
    skills: normalizeSkills(formData.skills),
    experience_level: formData.experience_level || "",
    current_status: formData.current_status || "",
    education_level: formData.education_level || "",
    career_goal: formData.career_goal || "",
  };

  if (formData.preferred_domain) {
    payload.preferred_domain = formData.preferred_domain;
  }

  return payload;
}

export default function CareerPath() {
  const navigate = useNavigate();
  const hasLoadedProfile = useRef(false);

  const [profiles, setProfiles] = useState([]);
  const [activeProfile, setActiveProfile] = useState(null);
  const { values: formData, handleChange, setValues } = useInput(defaultForm);
  const setValuesRef = useRef(setValues);
  const [initialized, setInitialized] = useState(false);
  const [loadingProfiles, setLoadingProfiles] = useState(false);
  const [profileError, setProfileError] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);
  const [nameTouched, setNameTouched] = useState(false);
  const [touched, setTouched] = useState(createUntouchedFields);

  const {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    setRecommendations,
  } = useCareerRecommendations();
  const setRecommendationsRef = useRef(setRecommendations);

  const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } =
    useCareerDetail();

  useEffect(() => {
    setValuesRef.current = setValues;
    setRecommendationsRef.current = setRecommendations;
  }, [setValues, setRecommendations]);

  useEffect(() => {
    setLoadingProfiles(true);
    setProfileError(null);
    getProfiles()
      .then((data) => {
        const list = Array.isArray(data) ? data : [];
        setProfiles(list);
        if (list.length > 0) {
          hasLoadedProfile.current = false;
          setActiveProfile(list[0]);
        }
      })
      .catch((err) => {
        setProfileError(err.message || "Failed to load profiles");
      })
      .finally(() => {
        setLoadingProfiles(false);
        setInitialized(true);
      });
  }, []);

  useEffect(() => {
    if (activeProfile && !hasLoadedProfile.current) {
      setValuesRef.current(mapProfileToFormData(activeProfile));
      setRecommendationsRef.current(null);
      setNameTouched(false);
      setTouched(createUntouchedFields());
      hasLoadedProfile.current = true;
      return;
    }

    if (!activeProfile && initialized && !hasLoadedProfile.current) {
      setValuesRef.current(defaultForm);
      setRecommendationsRef.current(null);
      setNameTouched(false);
      setTouched(createUntouchedFields());
      hasLoadedProfile.current = true;
    }
  }, [activeProfile, initialized]);

  useEffect(() => {
    console.log("FORM STATE:", formData);
  }, [formData]);

  useEffect(() => {
    if (!actionMessage) return undefined;
    const id = window.setTimeout(() => setActionMessage(null), 4500);
    return () => window.clearTimeout(id);
  }, [actionMessage]);

  const experienceLevel = buildField(
    formData,
    setValues,
    touched,
    setTouched,
    "experience_level",
    validateExperienceLevel,
  );
  const currentStatus = buildField(
    formData,
    setValues,
    touched,
    setTouched,
    "current_status",
    validateCurrentStatus,
  );
  const preferredDomain = buildField(
    formData,
    setValues,
    touched,
    setTouched,
    "preferred_domain",
    validatePreferredDomain,
  );
  const educationLevel = buildField(
    formData,
    setValues,
    touched,
    setTouched,
    "education_level",
    validateEducationLevel,
  );
  const careerGoal = buildField(
    formData,
    setValues,
    touched,
    setTouched,
    "career_goal",
    validateCareerGoal,
  );

  const handlePredict = async (event) => {
    event.preventDefault();
    markRequiredTouched(setTouched, setNameTouched);

    console.log("Submitting:", formData);

    if (
      validateExperienceLevel(formData.experience_level) ||
      validateCurrentStatus(formData.current_status) ||
      validateEducationLevel(formData.education_level) ||
      validateCareerGoal(formData.career_goal) ||
      (formData.skills || []).length < 5
    ) {
      return;
    }

    const careerContext = {
      experience_level: formData.experience_level,
      current_status: formData.current_status,
      preferred_domain: formData.preferred_domain || null,
      education_level: formData.education_level,
      career_goal: formData.career_goal,
    };

    await fetchRecommendations(formData.skills, 5, careerContext);
  };

  const handleSelectProfile = (profileId) => {
    const nextProfile = profiles.find((item) => item.profileId === profileId);
    if (!nextProfile) return;
    hasLoadedProfile.current = false;
    setActiveProfile(nextProfile);
  };

  const handleCreateProfile = async () => {
    markRequiredTouched(setTouched, setNameTouched);
    setActionMessage(null);

    console.log("Submitting:", formData);

    if (!formData.name.trim()) {
      setActionMessage({ type: "error", text: "Profile name is required." });
      return;
    }

    if (
      validateExperienceLevel(formData.experience_level) ||
      validateCurrentStatus(formData.current_status) ||
      validateEducationLevel(formData.education_level) ||
      validateCareerGoal(formData.career_goal) ||
      (formData.skills || []).length < 5
    ) {
      setActionMessage({
        type: "error",
        text: "Please complete required fields before saving.",
      });
      return;
    }

    if (profiles.length >= MAX_PROFILES) {
      setActionMessage({
        type: "error",
        text: "Maximum 3 profiles allowed per user.",
      });
      return;
    }

    try {
      const created = await createProfile(buildProfilePayload(formData));
      const nextProfiles = [created, ...profiles];
      setProfiles(nextProfiles);
      hasLoadedProfile.current = false;
      setActiveProfile(created);
      setActionMessage({ type: "success", text: "Profile created successfully." });
    } catch (err) {
      setActionMessage({
        type: "error",
        text: err.message || "Failed to create profile.",
      });
    }
  };

  const handleSaveProfile = async () => {
    if (!activeProfile) {
      setActionMessage({ type: "error", text: "Select a profile to save." });
      return;
    }

    markRequiredTouched(setTouched, setNameTouched);
    setActionMessage(null);

    console.log("Submitting:", formData);

    if (!formData.name.trim()) {
      setActionMessage({ type: "error", text: "Profile name is required." });
      return;
    }

    if (
      validateExperienceLevel(formData.experience_level) ||
      validateCurrentStatus(formData.current_status) ||
      validateEducationLevel(formData.education_level) ||
      validateCareerGoal(formData.career_goal) ||
      (formData.skills || []).length < 5
    ) {
      setActionMessage({
        type: "error",
        text: "Please complete required fields before saving.",
      });
      return;
    }

    try {
      const updated = await updateProfile(
        activeProfile.profileId,
        buildProfilePayload(formData),
      );
      const nextProfiles = profiles.map((item) =>
        item.profileId === updated.profileId ? updated : item,
      );
      setProfiles(nextProfiles);
      hasLoadedProfile.current = false;
      setActiveProfile(updated);
      setActionMessage({ type: "success", text: "Profile saved successfully." });
    } catch (err) {
      setActionMessage({
        type: "error",
        text: err.message || "Failed to update profile.",
      });
    }
  };

  const handleDeleteClick = () => {
    if (!activeProfile) return;
    handleDeleteConfirm();
  };

  const handleDeleteConfirm = async () => {
    if (!activeProfile) return;

    try {
      await deleteProfile(activeProfile.profileId);
      const nextProfiles = profiles.filter(
        (item) => item.profileId !== activeProfile.profileId,
      );
      setProfiles(nextProfiles);
      setActiveProfile(nextProfiles[0] || null);
      hasLoadedProfile.current = false;
      setActionMessage({
        type: "success",
        text: "Profile deleted successfully.",
      });
    } catch (err) {
      setActionMessage({
        type: "error",
        text: err.message || "Failed to delete profile.",
      });
    }
  };

  const handleViewJob = (recommendation) => {
    fetchJobDetail(recommendation, formData.skills, {
      experienceLevel: formData.experience_level,
      currentStatus: formData.current_status,
      educationLevel: formData.education_level,
      careerGoal: formData.career_goal,
      preferredDomain: formData.preferred_domain,
    });
  };

  const handleViewCareerLadder = () => {
    if (!jobDetail) return;
    navigate("/career-ladder", {
      state: {
        userSkills: formData.skills,
        selectedDomain: jobDetail.domain,
        recommendations: [jobDetail],
        userProfile: {
          experienceLevel: formData.experience_level,
          currentStatus: formData.current_status,
          educationLevel: formData.education_level,
          careerGoal: formData.career_goal,
        },
      },
    });
  };

  if (!initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-600">
        Loading profiles...
      </div>
    );
  }

  const isProfileSelected = Boolean(activeProfile);
  const isProfileFormComplete =
    formData.name.trim() &&
    !validateExperienceLevel(formData.experience_level) &&
    !validateCurrentStatus(formData.current_status) &&
    !validateEducationLevel(formData.education_level) &&
    !validateCareerGoal(formData.career_goal) &&
    (formData.skills || []).length >= 5;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f8f7ff] via-white to-[#edf2ff]">
      <div className="max-w-6xl mx-auto px-6 py-10 mt-20">
        <div className="flex flex-col gap-6">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent flex items-center gap-2">
              <FaChartLine /> Career Path Recommender
            </h2>
            <p className="text-gray-700 mt-2 text-lg">
              Save reusable profiles and get personalized AI-powered
              recommendations.
            </p>
          </div>

          <ProfileSectionCard>
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-100 p-4 rounded-xl text-sm text-gray-700">
              <p className="font-medium text-purple-700 mb-1">How this works</p>
              <ul className="list-disc list-inside space-y-1">
                <li>
                  A profile stores your skills and preferences so you can switch
                  setups without retyping.
                </li>
                <li>Create up to three profiles (e.g. student vs. job seeker).</li>
                <li>
                  After you save, use the form below and run recommendations to
                  see ranked roles and next steps.
                </li>
              </ul>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <h2 className="text-lg font-semibold text-gray-800">
                  Career Profile
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  Create and manage your personalized career setups
                </p>
              </div>
              <span className="text-xs font-semibold text-purple-600 bg-purple-100 px-3 py-1 rounded-full shrink-0 self-start sm:self-auto">
                {profiles.length}/{MAX_PROFILES} profiles
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex flex-col w-full">
                <label className="text-sm font-semibold text-gray-700 mb-2">
                  Active Profile
                </label>
                <NativeSelectField
                  value={activeProfile?.profileId || ""}
                  onChange={(event) =>
                    handleSelectProfile(event.target.value)
                  }
                  disabled={loadingProfiles}
                >
                  <option value="" disabled>
                    {profiles.length
                      ? "Select a profile"
                      : "No profiles created yet"}
                  </option>
                  {profiles.map((profile) => (
                    <option key={profile.profileId} value={profile.profileId}>
                      {profile.name}
                    </option>
                  ))}
                </NativeSelectField>
                <div className="mt-1 min-h-[1.25rem]">
                  {profileError ? (
                    <p className="text-xs text-red-500">{profileError}</p>
                  ) : null}
                </div>
              </div>

              <div className="flex flex-col w-full">
                <label className="text-sm font-semibold text-gray-700 mb-2">
                  Profile Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  onBlur={() => setNameTouched(true)}
                  placeholder="e.g., Backend Builder"
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white/90 text-gray-800 text-sm font-medium transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500/30 focus:border-purple-200/80"
                />
                <p className="text-red-500 text-sm min-h-[1.25rem] mt-1">
                  {nameTouched && !formData.name.trim()
                    ? "Profile name is required."
                    : ""}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 justify-end pt-1 border-t border-gray-100/80">
              <CareerButton
                variant="primary"
                type="button"
                onClick={handleCreateProfile}
                disabled={
                  !isProfileFormComplete || profiles.length >= MAX_PROFILES
                }
                className="inline-flex items-center justify-center gap-2 font-semibold"
              >
                <FaPlus /> Create Profile
              </CareerButton>
              <CareerButton
                variant="muted"
                type="button"
                onClick={handleSaveProfile}
                disabled={!isProfileSelected}
                className="inline-flex items-center justify-center gap-2 font-semibold"
              >
                <FaSave /> Save
              </CareerButton>
              <CareerButton
                variant="danger"
                type="button"
                onClick={handleDeleteClick}
                disabled={!isProfileSelected}
                className="inline-flex items-center justify-center gap-2 font-semibold"
              >
                <FaTrash /> Delete
              </CareerButton>
            </div>
          </ProfileSectionCard>

          <CareerProfileForm
            values={formData}
            handleChange={handleChange}
            onSubmit={handlePredict}
            loading={loading}
            experienceLevel={experienceLevel}
            currentStatus={currentStatus}
            preferredDomain={preferredDomain}
            educationLevel={educationLevel}
            careerGoal={careerGoal}
          />

          {error && <ErrorMessage message={error} />}

          {recommendations && (
            <div className="mt-6 relative z-0">
              <RecommendationsSection
                recommendations={recommendations}
                userSkills={formData.skills}
                onViewDetails={handleViewJob}
              />
            </div>
          )}
        </div>
      </div>



      <CareerDetailModal
        isOpen={!!selectedJob}
        onClose={closeDetail}
        jobDetail={jobDetail}
        isLoading={detailLoading}
        onViewPath={handleViewCareerLadder}
        userProfile={{
          experienceLevel: formData.experience_level,
          currentStatus: formData.current_status,
          educationLevel: formData.education_level,
          careerGoal: formData.career_goal,
        }}
      />
    </div>
  );
}

function buildField(formData, setValues, touched, setTouched, key, validator) {
  const value = formData[key];
  return {
    value,
    setValue: (nextValue) =>
      setValues((prev) => ({ ...prev, [key]: nextValue })),
    handleInputBlur: () => setTouched((prev) => ({ ...prev, [key]: true })),
    hasError: touched[key] && validator(value) !== "",
    errorMessage: validator(value),
  };
}

function markRequiredTouched(setTouched, setNameTouched) {
  setNameTouched(true);
  setTouched((prev) => ({
    ...prev,
    experience_level: true,
    current_status: true,
    education_level: true,
    career_goal: true,
  }));
}

function createUntouchedFields() {
  return {
    experience_level: false,
    current_status: false,
    education_level: false,
    career_goal: false,
  };
}

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
    <div>
      <RecommendationsSummary
        skillsCount={recommendations.skills_analyzed.length}
        rolesCount={recommendations.total_roles_compared}
        domainFilterApplied={recommendations.domain_filter_applied}
        preferredDomain={recommendations.preferred_domain}
      />

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

      <HowItWorks />
    </div>
  );
}
