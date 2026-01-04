import React, { useState } from "react";
import { twMerge } from "tailwind-merge";
import { FormLabel, FormHelperText, formStyles } from "./FormUtils";

const Input = ({
  // Basic Props
  id,
  name,
  label,
  placeholder,
  type = "text",
  value,
  defaultValue,
  onChange,
  onBlur,
  onFocus,
  onClick,

  // Validation Props
  isRequired = false,
  error,
  pattern,
  min,
  max,
  minLength,
  maxLength,
  step,

  // Style Props
  className = "",
  labelStyle = "",
  inputStyle = "",
  outerContainerStyle = "",
  helpTextStyle = "",
  errorTextStyle = "",

  // Icon Props
  icon,
  prefixIcon,
  searchIcon = false,

  // Helper Props
  helpText,
  disabled = false,
  readOnly = false,
  autoComplete,
  autoFocus = false,

  // Special Flags
  allowFillColor = false,
  isFilterSearch = false,

  // Textarea Props
  rows = 4,
  cols,
  resize = "none",

  // Input HTML attributes
  list,
  accept,
  multiple,

  // Rest of props
  ...rest
}) => {
  const [isFocused, setIsFocused] = useState(false);

  // Determine border classes based on state
  const getBorderClasses = () => {
    if (isFocused) return "border border-light-blue-2";
    return "border-0";
  };

  // Event handlers with callback support
  const handleFocus = (e) => {
    setIsFocused(true);
    if (onFocus) onFocus(e);
  };

  const handleBlur = (e) => {
    setIsFocused(false);
    if (onBlur) onBlur(e);
  };

  const handleClick = (e) => {
    if (onClick) onClick(e);
  };

  // Base classes for both input and textarea
  const baseClasses = twMerge(formStyles.input, getBorderClasses(), inputStyle);

  // Handle textarea rendering
  if (type === "textarea") {
    return (
      <div className={twMerge("flex flex-col w-full", outerContainerStyle)}>
        <FormLabel
          htmlFor={id}
          label={label}
          isRequired={isRequired}
          className={labelStyle}
          helpText={helpText}
        />

        {helpText && (
          <div className="flex items-center justify-between max-h-[15px] sm:max-h-5 mb-1 sm:mb-2">
            <span className={twMerge(formStyles.helpText, helpTextStyle)}>
              {helpText}
            </span>
          </div>
        )}

        <textarea
          id={id}
          name={name}
          placeholder={placeholder}
          value={value}
          defaultValue={defaultValue}
          onChange={onChange}
          disabled={disabled}
          readOnly={readOnly}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onClick={handleClick}
          autoFocus={autoFocus}
          rows={rows}
          cols={cols}
          maxLength={maxLength}
          minLength={minLength}
          autoComplete={autoComplete}
          style={{ resize }}
          className={twMerge(
            baseClasses,
            searchIcon ? "pl-8 sm:pl-10" : "",
            prefixIcon ? "pl-10 sm:pl-12" : "",
            className
          )}
          {...rest}
        />

        <FormHelperText
          error={!isFilterSearch ? error : null}
          errorClassName={errorTextStyle}
        />
      </div>
    );
  }

  // Handle regular inputs
  return (
    <div
      className={twMerge(
        "flex flex-col justify-center w-full",
        outerContainerStyle
      )}
    >
      <FormLabel
        htmlFor={id}
        label={label}
        isRequired={isRequired}
        className={labelStyle}
        helpText={helpText}
      />

      {helpText && (
        <div className="flex items-center justify-between max-h-[15px] sm:max-h-5 mb-1 sm:mb-2">
          <span className={twMerge(formStyles.helpText, helpTextStyle)}>
            {helpText}
          </span>
        </div>
      )}

      <div className="relative">
        {searchIcon && (
          <div className="absolute inset-y-0 left-2 sm:left-3 flex items-center pointer-events-none">
            <svg
              className="w-4 h-4 sm:w-5 sm:h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
        )}

        {prefixIcon && (
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 sm:pl-4 pointer-events-none">
            {prefixIcon}
          </div>
        )}

        <input
          id={id}
          type={type}
          name={name}
          placeholder={placeholder}
          value={value}
          defaultValue={defaultValue}
          onChange={onChange}
          disabled={disabled}
          readOnly={readOnly}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onClick={handleClick}
          autoFocus={autoFocus}
          autoComplete={autoComplete}
          maxLength={maxLength}
          minLength={minLength}
          min={min}
          max={max}
          step={step}
          pattern={pattern}
          list={list}
          accept={accept}
          multiple={multiple}
          className={twMerge(
            baseClasses,
            searchIcon ? "pl-8 sm:pl-10" : "",
            prefixIcon ? "pl-10 sm:pl-14 md:pl-16" : "",
            className
          )}
          {...rest}
        />

        {icon && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:pr-3">
            {icon}
          </div>
        )}
      </div>

      <FormHelperText
        error={!isFilterSearch ? error : null}
        errorClassName={errorTextStyle}
      />
    </div>
  );
};

export default Input;
