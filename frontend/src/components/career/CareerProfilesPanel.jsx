import React from "react";
import { FaPlus, FaUserCircle } from "react-icons/fa";
import ProfileCard from "./ProfileCard";
import GradientButton from "./GradientButton";

export default function CareerProfilesPanel({
  profiles,
  activeProfileId,
  onSelect,
  onEdit,
  onDelete,
  onCreate,
  loading,
}) {
  const hasProfiles = profiles && profiles.length > 0;
  const isAtLimit = profiles.length >= 3;

  return (
    <aside className="relative p-6 rounded-2xl border border-gray-100 bg-white/70 shadow-lg backdrop-blur-xl">
      <div className="absolute inset-0 rounded-2xl -z-10 bg-gradient-to-br from-indigo-100/50 to-blue-100/30" />

      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-lg font-bold text-gray-800">Your Profiles</h3>
          <p className="text-xs text-gray-600">
            Save up to 3 career identities
          </p>
        </div>
        <span className="text-xs font-semibold text-purple-600 bg-purple-100 px-3 py-1 rounded-full">
          {profiles.length}/3
        </span>
      </div>

      <GradientButton
        onClick={onCreate}
        disabled={isAtLimit}
        className="w-full mb-4"
      >
        <span className="flex items-center justify-center gap-2">
          <FaPlus /> Create Profile
        </span>
      </GradientButton>

      {loading && (
        <div className="space-y-3 animate-pulse">
          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-24 rounded-2xl bg-gradient-to-r from-purple-100 to-blue-100"
            />
          ))}
        </div>
      )}

      {!loading && !hasProfiles && (
        <div className="text-center py-8 px-4 rounded-2xl border border-dashed border-purple-200 bg-white/70">
          <FaUserCircle className="text-3xl text-purple-300 mx-auto mb-3" />
          <p className="text-sm font-semibold text-gray-700">
            No profiles created yet
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Create your first career profile to get started.
          </p>
        </div>
      )}

      {!loading && hasProfiles && (
        <div className="space-y-4">
          {profiles.map((profile) => (
            <ProfileCard
              key={profile.profileId}
              profile={profile}
              isActive={activeProfileId === profile.profileId}
              onSelect={onSelect}
              onEdit={onEdit}
              onDelete={onDelete}
              disabled={loading}
            />
          ))}
        </div>
      )}

      {isAtLimit && (
        <p className="mt-4 text-xs text-purple-700 bg-purple-50 border border-purple-100 rounded-lg p-3">
          You have reached the maximum of 3 profiles. Delete one to create a new
          profile.
        </p>
      )}
    </aside>
  );
}
