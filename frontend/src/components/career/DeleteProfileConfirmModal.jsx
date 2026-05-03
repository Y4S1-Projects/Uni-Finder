import React from "react";
import { twMerge } from "tailwind-merge";
import { careerBaseButton, careerNeutralButton, careerDangerOutlineButton } from "./careerClassNames";

export default function DeleteProfileConfirmModal({
  isOpen,
  profileName,
  onCancel,
  onConfirm,
}) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 animate-fadeIn">
      <button
        type="button"
        className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-200 motion-safe:animate-fadeIn"
        onClick={onCancel}
        aria-label="Dismiss"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-profile-title"
        className="relative z-[1] bg-white rounded-2xl p-6 shadow-xl w-full max-w-[320px] space-y-4 border border-gray-100 animate-modal-enter"
      >
        <h3 id="delete-profile-title" className="text-lg font-semibold text-gray-800">
          Delete Profile?
        </h3>
        <p className="text-sm text-gray-500">
          {profileName
            ? `This will remove "${profileName}". This action cannot be undone.`
            : "This action cannot be undone."}
        </p>
        <div className="flex justify-end gap-3 pt-1">
          <button
            type="button"
            onClick={onCancel}
            className={twMerge(
              careerBaseButton,
              careerNeutralButton,
              "px-4 py-2 text-sm font-semibold",
            )}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={twMerge(
              careerBaseButton,
              careerDangerOutlineButton,
              "px-4 py-2 text-sm font-semibold",
            )}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
