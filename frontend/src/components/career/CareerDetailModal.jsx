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
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: "1rem",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "white",
          borderRadius: 16,
          maxWidth: 700,
          width: "100%",
          maxHeight: "90vh",
          overflow: "auto",
          padding: "2rem",
          position: "relative",
        }}
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
      style={{
        position: "absolute",
        top: 16,
        right: 16,
        background: "#f3f4f6",
        border: "none",
        borderRadius: "50%",
        width: 32,
        height: 32,
        cursor: "pointer",
        fontSize: 18,
      }}
    >
      ✕
    </button>
  );
}

function CareerDetailContent({ jobDetail }) {
  return (
    <>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ margin: "0 0 8px 0", color: "#1e40af" }}>
          {jobDetail.role_title || jobDetail.role_id}
        </h2>
        <DomainBadge domain={jobDetail.domain} size="large" />
      </div>

      {/* Scores */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <ScoreCard
          score={jobDetail.match_score}
          label="Match Score"
          bgColor="#f0f7ff"
          textColor="#2563eb"
        />
        <ScoreCard
          score={jobDetail.readiness_score}
          label="Readiness"
          bgColor="#f0fdf4"
          textColor="#16a34a"
        />
      </div>

      {/* Next Career Step */}
      {jobDetail.next_role && (
        <div style={{ marginBottom: "1.5rem" }}>
          <NextRoleBadge
            nextRole={jobDetail.next_role}
            nextRoleTitle={jobDetail.next_role_title}
            variant="full"
          />
        </div>
      )}

      {/* Skills You Have */}
      {jobDetail.matched_skills?.length > 0 && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h3
            style={{ margin: "0 0 0.75rem 0", color: "#059669", fontSize: 16 }}
          >
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
        <div style={{ marginBottom: "1.5rem" }}>
          <h3
            style={{ margin: "0 0 0.75rem 0", color: "#ca8a04", fontSize: 16 }}
          >
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
    <div style={{ textAlign: "center", padding: "2rem", color: "#666" }}>
      Failed to load details. Please try again.
    </div>
  );
}
