import React from "react";
import { twMerge } from "tailwind-merge";

export default function NativeSelectField({
  className = "",
  disabled,
  children,
  ...rest
}) {
  return (
    <div className="relative w-full">
      <select
        disabled={disabled}
        className={twMerge(
          "appearance-none w-full pr-10 pl-4 py-2.5 rounded-xl border border-gray-200 bg-white/90 text-gray-800 text-sm font-medium",
          "focus:outline-none focus:ring-2 focus:ring-purple-500/30 focus:border-purple-200/80 transition-all duration-200",
          "disabled:opacity-60 disabled:cursor-not-allowed",
          className,
        )}
        {...rest}
      >
        {children}
      </select>
      <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm leading-none select-none">
        ▼
      </div>
    </div>
  );
}
