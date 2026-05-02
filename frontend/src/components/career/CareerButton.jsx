import React from "react";
import { twMerge } from "tailwind-merge";
import {
  careerBaseButton,
  careerGradientButton,
  careerSecondaryDestructiveButton,
  careerNeutralButton,
  careerDangerOutlineButton,
} from "./careerClassNames";

const VARIANT_CLASS = {
  primary: careerGradientButton,
  secondary: careerSecondaryDestructiveButton,
  muted: careerNeutralButton,
  danger: careerDangerOutlineButton,
};

export default function CareerButton({
  variant = "primary",
  className = "",
  children,
  type = "button",
  ...rest
}) {
  return (
    <button
      type={type}
      className={twMerge(
        careerBaseButton,
        VARIANT_CLASS[variant] || careerGradientButton,
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
