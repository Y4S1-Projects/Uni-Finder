/**
 * Career Detail Modal Component
 * Full-screen modal showing detailed career information and AI explanation
 */
import React from "react";
import { ScoreCard } from "./ScoreDisplay";
import { SkillTagList } from "./SkillTags";
import { NextRoleBadge } from "./NextRoleBadge";
import { DomainBadge } from "./DomainBadge";
import { AIExplanation, AILoadingState } from "./AIExplanation";

export function CareerDetailModal({ isOpen, onClose, jobDetail, isLoading }) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[1050] overflow-auto py-8 animate-fade-in"
      onClick={onClose}
      style={{
        animation: "fadeIn 0.2s ease-out",
      }}
    >
      <div
        className="bg-gradient-to-br from-white via-blue-50 to-indigo-50 rounded-3xl max-w-2xl w-full mx-4 p-8 relative shadow-2xl border-2 border-blue-100 max-h-[85vh] overflow-auto transform transition-all duration-300"
        onClick={(e) => e.stopPropagation()}
        style={{
          animation: "slideUp 0.3s ease-out",
        }}
      >
        {/* Close Button */}
        <CloseButton onClick={onClose} />

        {/* Content */}
        {isLoading ? (
          <AILoadingState />
        ) : jobDetail ? (
          <CareerDetailContent jobDetail={jobDetail} />
        ) : (
          <ErrorState />
        )}
      </div>
    </div>
  );
}

function CloseButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="absolute top-4 right-4 bg-gradient-to-br from-gray-100 to-gray-200 hover:from-red-100 hover:to-red-200 rounded-full w-10 h-10 flex items-center justify-center text-xl transition-all duration-300 hover:scale-110 hover:rotate-90 shadow-md hover:shadow-lg z-10"
    >
      ✕
    </button>
  );
}

function CareerDetailContent({ jobDetail }) {
  return (
    <>
      {/* Header */}
      <div className="mb-6 animate-slide-in-left">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-700 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-3">
          {jobDetail.role_title || jobDetail.role_id}
        </h2>
        <DomainBadge domain={jobDetail.domain} size="large" />
      </div>

      {/* Scores */}
      <div
        className="flex gap-4 mb-6 animate-scale-in"
        style={{ animationDelay: "0.1s" }}
      >
        <ScoreCard
          score={jobDetail.match_score}
          label="Match Score"
          variant="blue"
        />
        <ScoreCard
          score={jobDetail.readiness_score}
          label="Readiness"
          variant="green"
        />
      </div>

      {/* Next Career Step */}
      {jobDetail.next_role && (
        <div className="mb-6">
          <NextRoleBadge
            nextRole={jobDetail.next_role}
            nextRoleTitle={jobDetail.next_role_title}
            variant="full"
          />
        </div>
      )}

      {/* Skills You Have */}
      {jobDetail.matched_skills?.length > 0 && (
        <div
          className="mb-6 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          <h3 className="text-base font-semibold text-green-700 mb-3 flex items-center gap-2">
            <span className="text-lg">✅</span> Skills You Already Have (
            {jobDetail.matched_skills.length})
          </h3>
          <SkillTagList
            skills={jobDetail.matched_skills}
            variant="matched"
            maxDisplay={100}
            size="large"
            showLabel={false}
          />
        </div>
      )}

      {/* Skills to Develop */}
      {jobDetail.missing_skills?.length > 0 && (
        <div
          className="mb-6 animate-fade-in-up"
          style={{ animationDelay: "0.3s" }}
        >
          <h3 className="text-base font-semibold text-amber-700 mb-3 flex items-center gap-2">
            <span className="text-lg">📚</span> Skills to Develop (
            {jobDetail.missing_skills.length})
          </h3>
          <SkillTagList
            skills={jobDetail.missing_skills}
            variant="missing"
            maxDisplay={100}
            size="large"
            showLabel={false}
          />
        </div>
      )}

      {/* AI Explanation */}
      <AIExplanation explanation={jobDetail.explanation} />
    </>
  );
}

function ErrorState() {
  return (
    <div className="text-center py-8 text-gray-500">
      Failed to load details. Please try again.
    </div>
  );
}
