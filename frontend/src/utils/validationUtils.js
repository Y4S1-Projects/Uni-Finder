/**
 * Validation Utilities for Career Path Form
 */

export const CAREER_FIELD_TYPES = {
  EXPERIENCE_LEVEL: "experience_level",
  CURRENT_STATUS: "current_status",
  PREFERRED_DOMAIN: "preferred_domain",
  EDUCATION_LEVEL: "education_level",
  CAREER_GOAL: "career_goal",
  REQUIRED_FIELD: "required_field",
};

export const errorMessages = {
  REQUIRED_FIELD: "This field is required",
  INVALID_OPTION: "Please select a valid option",
  EXPERIENCE_REQUIRED: "Please select your experience level",
  STATUS_REQUIRED: "Please select your current status",
  EDUCATION_REQUIRED: "Please select your education level",
  GOAL_REQUIRED: "Please select your career goal",
};

// Validate experience level
export const validateExperienceLevel = (value) => {
  const validOptions = ["student", "0-1", "1-3", "3-5", "5+"];
  if (!value) return errorMessages.EXPERIENCE_REQUIRED;
  if (!validOptions.includes(value)) return errorMessages.INVALID_OPTION;
  return "";
};

// Validate current status
export const validateCurrentStatus = (value) => {
  const validOptions = ["student", "graduate", "working"];
  if (!value) return errorMessages.STATUS_REQUIRED;
  if (!validOptions.includes(value)) return errorMessages.INVALID_OPTION;
  return "";
};

// Validate preferred domain (optional)
export const validatePreferredDomain = (value) => {
  if (!value) return ""; // Optional field - empty is valid
  const validOptions = [
    "software_engineering",
    "frontend_engineering",
    "backend_engineering",
    "fullstack_engineering",
    "data_engineering",
    "data_science",
    "data",
    "ai_ml",
    "devops",
    "cloud_engineering",
    "security",
    "qa",
    "mobile_engineering",
    "ui_ux",
    "product_management",
    "business_analysis",
    "project_management",
    "technical_writing",
    "blockchain_web3",
    "game_development",
    "embedded_systems",
  ];
  if (!validOptions.includes(value)) return errorMessages.INVALID_OPTION;
  return "";
};

// Validate education level
export const validateEducationLevel = (value) => {
  const validOptions = ["al", "diploma", "hnd", "bachelors", "masters"];
  if (!value) return errorMessages.EDUCATION_REQUIRED;
  if (!validOptions.includes(value)) return errorMessages.INVALID_OPTION;
  return "";
};

// Validate career goal
export const validateCareerGoal = (value) => {
  const validOptions = ["first_job", "switch_career", "get_promoted"];
  if (!value) return errorMessages.GOAL_REQUIRED;
  if (!validOptions.includes(value)) return errorMessages.INVALID_OPTION;
  return "";
};

// Generic field validator
export const validateField = (fieldType, value) => {
  switch (fieldType) {
    case CAREER_FIELD_TYPES.EXPERIENCE_LEVEL:
      return validateExperienceLevel(value);
    case CAREER_FIELD_TYPES.CURRENT_STATUS:
      return validateCurrentStatus(value);
    case CAREER_FIELD_TYPES.PREFERRED_DOMAIN:
      return validatePreferredDomain(value);
    case CAREER_FIELD_TYPES.EDUCATION_LEVEL:
      return validateEducationLevel(value);
    case CAREER_FIELD_TYPES.CAREER_GOAL:
      return validateCareerGoal(value);
    case CAREER_FIELD_TYPES.REQUIRED_FIELD:
      return !value ? errorMessages.REQUIRED_FIELD : "";
    default:
      return "";
  }
};
