import React from "react";
import { twMerge } from "tailwind-merge";
import { FaUserCheck, FaTrash, FaEdit } from "react-icons/fa";
import { DomainBadge } from "./DomainBadge";
import {
  careerBaseButton,
  careerGradientButton,
  careerNeutralButton,
  careerDangerOutlineButton,
} from "./careerClassNames";

function normalizeDomain(domain) {
  if (!domain) return "";
  return String(domain).toUpperCase();
}

function formatStatus(status) {
  if (!status) return "";
  return status.replace(/_/g, " ");
}

export default function ProfileCard({
  profile,
  isActive,
  onSelect,
  onEdit,
  onDelete,
  disabled,
}) {
  const domainValue = normalizeDomain(profile?.preferred_domain);

  return (
    <div
      className={`p-4 rounded-2xl border transition-all duration-300 shadow-sm hover:shadow-md ${
        isActive
          ? "border-indigo-400 bg-white"
          : "border-gray-200 bg-white"
      } ${disabled ? "opacity-60" : ""}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="text-lg font-semibold text-gray-900">
            {profile?.name || "Untitled Profile"}
          </h4>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {domainValue ? (
              <DomainBadge domain={domainValue} size="small" />
            ) : (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                No domain preference
              </span>
            )}
            {profile?.current_status && (
              <span className="text-xs text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                {formatStatus(profile.current_status)}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {profile?.skills?.length || 0} skills selected
          </p>
        </div>
        {isActive && (
          <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-100 px-2 py-1 rounded-full">
            Active
          </span>
        )}
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        <button
          type="button"
          onClick={() => onSelect(profile)}
          disabled={disabled}
          className={twMerge(
            careerBaseButton,
            "flex items-center justify-center gap-2 text-xs font-semibold py-2 rounded-xl px-2",
            isActive
              ? careerGradientButton
              : "bg-white text-indigo-700 border border-gray-200 hover:bg-indigo-50 hover:border-indigo-200",
          )}
        >
          <FaUserCheck className="text-xs" />
          {isActive ? "Selected" : "Select"}
        </button>
        <button
          type="button"
          onClick={() => onEdit(profile)}
          disabled={disabled}
          className={twMerge(
            careerBaseButton,
            careerNeutralButton,
            "flex items-center justify-center gap-2 text-xs font-semibold py-2 rounded-xl px-2 border-blue-200/80 text-blue-700 hover:bg-blue-50 hover:text-blue-800",
          )}
        >
          <FaEdit className="text-xs" /> Edit
        </button>
        <button
          type="button"
          onClick={() => onDelete(profile)}
          disabled={disabled}
          className={twMerge(
            careerBaseButton,
            careerDangerOutlineButton,
            "flex items-center justify-center gap-2 text-xs font-semibold py-2 rounded-xl px-2",
          )}
        >
          <FaTrash className="text-xs" /> Delete
        </button>
      </div>
    </div>
  );
}
