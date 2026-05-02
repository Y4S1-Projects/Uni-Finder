import React from "react";
import { twMerge } from "tailwind-merge";
import {
  careerBaseButton,
  careerGradientButton,
  careerSecondaryButton,
  careerMutedButton,
  careerDangerOutlineButton,
} from "./careerClassNames";

const VARIANT_CLASS = {
  primary: careerGradientButton,
  secondary: careerSecondaryButton,
  muted: careerMutedButton,
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
