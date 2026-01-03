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
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-auto p-8 relative"
        onClick={(e) => e.stopPropagation()}
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
      className="absolute top-4 right-4 bg-gray-100 hover:bg-gray-200 rounded-full w-8 h-8 flex items-center justify-center text-lg transition-colors"
    >
      ✕
    </button>
  );
}

function CareerDetailContent({ jobDetail }) {
  return (
    <>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-800 mb-2">
          {jobDetail.role_title || jobDetail.role_id}
        </h2>
        <DomainBadge domain={jobDetail.domain} size="large" />
      </div>

      {/* Scores */}
      <div className="flex gap-4 mb-6">
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
        <div className="mb-6">
          <h3 className="text-base font-semibold text-green-600 mb-3">
            ✅ Skills You Already Have ({jobDetail.matched_skills.length})
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
        <div className="mb-6">
          <h3 className="text-base font-semibold text-yellow-600 mb-3">
            📚 Skills to Develop ({jobDetail.missing_skills.length})
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
