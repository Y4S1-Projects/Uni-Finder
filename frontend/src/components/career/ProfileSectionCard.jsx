import React from "react";
import { twMerge } from "tailwind-merge";

export default function ProfileSectionCard({ children, className = "" }) {
  return (
    <div
      className={twMerge(
        "bg-white/70 backdrop-blur-xl shadow-lg rounded-2xl p-6 space-y-6 border border-gray-100",
        className,
      )}
    >
      {children}
    </div>
  );
}
