import React from "react";
import { twMerge } from "tailwind-merge";
import { careerBaseButton, careerGradientButton } from "./careerClassNames";

export default function GradientButton({
  children,
  className = "",
  disabled = false,
  type = "button",
  onClick,
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={twMerge(
        "relative overflow-hidden font-semibold",
        careerBaseButton,
        careerGradientButton,
        "hover:-translate-y-0.5 active:translate-y-0 py-2.5",
        disabled ? "opacity-60 cursor-not-allowed hover:translate-y-0" : "",
        className,
      )}
    >
      <span className="relative z-10">{children}</span>
      <span className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-300 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.35),_transparent_60%)]" />
    </button>
  );
}
