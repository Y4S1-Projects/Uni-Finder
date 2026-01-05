import React from "react";
import { twMerge } from "tailwind-merge";

// Common form styles used across components
export const formStyles = {
  label:
    "text-gray-800 font-semibold text-sm sm:text-base md:text-lg text-left mb-2 sm:mb-2.5",
  helpText:
    "text-gray-500 text-[8px] sm:text-[.6875rem] font-normal leading-0 mb-1 sm:mb-2",
  errorText:
    "block text-red-500 text-[8px] sm:text-[10px] font-normal leading-normal",
  errorContainer: "h-[14px] sm:h-5 mt-0 text-left mb-1",
  requiredStar: "text-red-500",
  input:
    "w-full h-9 sm:h-10 md:h-11 rounded-md font-normal text-[10px] sm:text-base text-gray-700 bg-white placeholder:text-gray-400 placeholder:text-opacity-80 focus:outline-none px-3 sm:px-4 py-2 sm:py-3 border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all duration-200",
  dropDown:
    "w-full flex items-center justify-between px-3 sm:px-4 py-2 sm:py-3 bg-white text-gray-700 font-normal text-sm sm:text-base rounded-md placeholder-gray-400 placeholder-opacity-80 border-2 border-gray-200 focus:border-purple-400 transition-all duration-200",
  dropDownOptions:
    "w-full flex items-center justify-between px-3 sm:px-4 py-2 sm:py-3 bg-white text-gray-700 font-normal text-sm sm:text-base placeholder-gray-400 placeholder-opacity-80 my-[1px]",
};

/**
 * FormLabel - Reusable label component
 */
export const FormLabel = ({
  htmlFor,
  label,
  isRequired,
  className,
  helpText,
  prefixIcon,
}) => {
  if (!label) return null;

  return (
    <label
      htmlFor={htmlFor}
      className={twMerge(
        formStyles.label,
        helpText ? "mb-0 sm:mb-0" : "mb-2 sm:mb-2.5",
        className
      )}
    >
      {prefixIcon && <span className="inline-flex mr-2">{prefixIcon}</span>}
      {label} {isRequired && <span className={formStyles.requiredStar}>*</span>}
    </label>
  );
};

/**
 * FormHelperText - Reusable helper text component
 */
export const FormHelperText = ({
  helpText = "",
  error = "",
  className = "",
  errorClassName = "",
}) => {
  return (
    <div className={twMerge(formStyles.errorContainer, className)}>
      {helpText && !error && (
        <span className={formStyles.helpText}>{helpText}</span>
      )}
      {error && (
        <span className={twMerge(formStyles.errorText, errorClassName)}>
          {error}
        </span>
      )}
    </div>
  );
};
