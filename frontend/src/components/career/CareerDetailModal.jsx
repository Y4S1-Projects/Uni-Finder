/**
 * Career Detail Modal Component
 * Phase D: Full-screen modal showing detailed career information, score breakdown,
 * core/supporting/missing skill clusters, ranking explanation, seniority fit,
 * ladder position, and AI explanation.
 */
import React from "react";
import { createPortal } from "react-dom";
import { ScoreCard } from "./ScoreDisplay";
import { SkillTagList } from "./SkillTags";
import { NextRoleBadge } from "./NextRoleBadge";
import { DomainBadge } from "./DomainBadge";
import { AIExplanation, AILoadingState } from "./AIExplanation";
import { IoClose } from "react-icons/io5";
import {
  FaCheckCircle,
  FaBookOpen,
  FaCogs,
  FaChartBar,
  FaExclamationTriangle,
  FaInfoCircle,
  FaLayerGroup,
} from "react-icons/fa";

export function CareerDetailModal({
  isOpen,
  onClose,
  jobDetail,
  isLoading,
  onViewPath,
  userProfile,
}) {
  if (!isOpen) return null;

  // Use portal to render modal at document body level, avoiding z-index stacking context issues
  return createPortal(
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9999] overflow-auto py-8 animate-fade-in"
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
          <CareerDetailContent
            jobDetail={jobDetail}
            onViewPath={onViewPath}
            userProfile={userProfile}
          />
        ) : (
          <ErrorState />
        )}
      </div>
    </div>,
    document.body,
  );
}

function CloseButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="absolute top-4 right-4 bg-white hover:bg-gradient-to-br hover:from-purple-50 hover:to-blue-50 rounded-full w-16 h-16 flex items-center justify-center transition-all duration-300 hover:scale-125 shadow-lg hover:shadow-2xl border-2 border-purple-200 hover:border-purple-600 z-50 group"
      aria-label="Close modal"
    >
      <IoClose className="text-4xl text-purple-600 group-hover:text-purple-800 group-hover:rotate-90 transition-all duration-300" />
    </button>
  );
}

function CareerDetailContent({ jobDetail, onViewPath, userProfile }) {
  const sb = jobDetail.score_breakdown || {};
  const expl = jobDetail.explanations || {};
  const coreSkills = jobDetail.matched_core_skills || [];
  const supportSkills = jobDetail.matched_supporting_skills || [];
  const missingCritical = jobDetail.missing_critical_skills || [];

  return (
    <>
      {/* Header */}
      <div className="mb-6 animate-slide-in-left">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-700 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-3">
          {jobDetail.role_title || jobDetail.role_id}
        </h2>

        <div className="flex flex-wrap items-center gap-3">
          <DomainBadge domain={jobDetail.domain} size="large" />

          {/* Best match badge */}
          {jobDetail.is_best_match && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-yellow-100 text-yellow-800 font-semibold border border-yellow-300 shadow-sm">
              ★ Best Match
            </span>
          )}

          {/* Seniority badge */}
          {jobDetail.seniority != null && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700 font-medium border border-indigo-200 shadow-sm">
              Seniority: {jobDetail.seniority}
            </span>
          )}

          {/* Ladder position badge */}
          {jobDetail.ladder_position != null &&
            jobDetail.ladder_length != null && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-purple-100 text-purple-700 font-medium border border-purple-200 shadow-sm">
                Ladder: {jobDetail.ladder_position}/{jobDetail.ladder_length}
              </span>
            )}

          {/* Profile source */}
          {jobDetail.profile_source === "synthetic" && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-orange-100 text-orange-700 font-medium border border-orange-200 shadow-sm">
              Synthetic Profile
            </span>
          )}

          {userProfile && (
            <div className="flex flex-wrap gap-2 items-center ml-2 border-l-2 border-slate-200 pl-4">
              {userProfile.experienceLevel && (
                <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium whitespace-nowrap border border-slate-200 shadow-sm">
                  <span className="opacity-75">Exp:</span>{" "}
                  {userProfile.experienceLevel}
                </span>
              )}
              {userProfile.educationLevel && (
                <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium whitespace-nowrap border border-slate-200 shadow-sm">
                  <span className="opacity-75">Edu:</span>{" "}
                  {userProfile.educationLevel}
                </span>
              )}
              {userProfile.currentStatus && (
                <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium whitespace-nowrap border border-slate-200 shadow-sm">
                  <span className="opacity-75">Status:</span>{" "}
                  {userProfile.currentStatus}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Primary Scores */}
      <div
        className="flex gap-4 mb-6 animate-scale-in"
        style={{ animationDelay: "0.1s" }}
      >
        <ScoreCard
          score={jobDetail.readiness_score}
          label="Readiness"
          variant="green"
        />
        <ScoreCard
          score={jobDetail.match_score}
          label="Match Score"
          variant="blue"
        />
        {jobDetail.confidence_score != null && (
          <ScoreCard
            score={jobDetail.confidence_score}
            label="Confidence"
            variant="purple"
          />
        )}
      </div>

      {/* Score Breakdown Grid */}
      {Object.keys(sb).length > 0 && (
        <div
          className="mb-6 animate-fade-in-up"
          style={{ animationDelay: "0.15s" }}
        >
          <h3 className="text-base font-semibold text-indigo-700 mb-3 flex items-center gap-2">
            <FaChartBar className="text-lg" /> Score Breakdown
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <ScoreBreakdownItem
              label="Core Coverage"
              value={sb.core_skill_coverage_score}
            />
            <ScoreBreakdownItem
              label="Skill Match"
              value={sb.skill_match_score}
            />
            <ScoreBreakdownItem
              label="Domain Fit"
              value={sb.domain_preference_score}
            />
            <ScoreBreakdownItem
              label="Experience Fit"
              value={sb.experience_fit_score}
            />
            <ScoreBreakdownItem
              label="Seniority Fit"
              value={sb.seniority_fit_score}
            />
            <ScoreBreakdownItem
              label="Confidence"
              value={sb.confidence_score}
            />
          </div>
        </div>
      )}

      {/* Why Ranked Here / Why Best Match */}
      {(expl.why_ranked_here || expl.why_best_match) && (
        <div
          className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl animate-fade-in-up"
          style={{ animationDelay: "0.18s" }}
        >
          <h3 className="text-sm font-semibold text-blue-700 mb-2 flex items-center gap-2">
            <FaInfoCircle /> Ranking Explanation
          </h3>
          {expl.why_ranked_here && (
            <p className="text-sm text-blue-900 mb-1">{expl.why_ranked_here}</p>
          )}
          {expl.why_best_match && (
            <p className="text-sm text-blue-800">{expl.why_best_match}</p>
          )}
          {expl.domain_impact && (
            <p className="text-xs text-blue-600 mt-1">{expl.domain_impact}</p>
          )}
          {expl.seniority_fit && (
            <p className="text-xs text-blue-600 mt-1">{expl.seniority_fit}</p>
          )}
        </div>
      )}

      {/* What Lowers Readiness */}
      {expl.why_not_more_ready && (
        <div
          className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          <h3 className="text-sm font-semibold text-amber-700 mb-2 flex items-center gap-2">
            <FaExclamationTriangle /> What Lowers Readiness
          </h3>
          <p className="text-sm text-amber-900">{expl.why_not_more_ready}</p>
        </div>
      )}

      {/* Next Career Step */}
      {jobDetail.next_role && (
        <div className="mb-6">
          <NextRoleBadge
            nextRole={jobDetail.next_role}
            nextRoleTitle={jobDetail.next_role_title}
            variant="full"
            onViewPath={onViewPath}
          />
        </div>
      )}

      {/* Matched Core Skills */}
      {coreSkills.length > 0 && (
        <div
          className="mb-4 animate-fade-in-up"
          style={{ animationDelay: "0.25s" }}
        >
          <h3 className="text-base font-semibold text-green-700 mb-3 flex items-center gap-2">
            <FaCheckCircle className="text-lg" /> Core Skills Matched (
            {coreSkills.length})
          </h3>
          <SkillTagList
            skills={coreSkills}
            variant="matched"
            maxDisplay={100}
            size="large"
            showLabel={false}
          />
        </div>
      )}

      {/* Matched Supporting Skills */}
      {supportSkills.length > 0 && (
        <div
          className="mb-4 animate-fade-in-up"
          style={{ animationDelay: "0.28s" }}
        >
          <h3 className="text-base font-semibold text-teal-600 mb-3 flex items-center gap-2">
            <FaCogs className="text-lg" /> Supporting Skills (
            {supportSkills.length})
          </h3>
          <SkillTagList
            skills={supportSkills}
            variant="matched"
            maxDisplay={50}
            size="large"
            showLabel={false}
          />
        </div>
      )}

      {/* Missing Critical Skills */}
      {missingCritical.length > 0 && (
        <div
          className="mb-6 animate-fade-in-up"
          style={{ animationDelay: "0.3s" }}
        >
          <h3 className="text-base font-semibold text-red-600 mb-3 flex items-center gap-2">
            <FaExclamationTriangle className="text-lg" /> Missing Critical
            Skills ({missingCritical.length})
          </h3>
          <SkillTagList
            skills={missingCritical}
            variant="missing"
            maxDisplay={100}
            size="large"
            showLabel={false}
          />
        </div>
      )}

      {/* Fallback: flat matched/missing if Phase D clusters are empty */}
      {coreSkills.length === 0 &&
        supportSkills.length === 0 &&
        jobDetail.matched_skills?.length > 0 && (
          <div
            className="mb-6 animate-fade-in-up"
            style={{ animationDelay: "0.25s" }}
          >
            <h3 className="text-base font-semibold text-purple-700 mb-3 flex items-center gap-2">
              <FaCheckCircle className="text-lg" /> Skills You Already Have (
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

      {missingCritical.length === 0 && jobDetail.missing_skills?.length > 0 && (
        <div
          className="mb-6 animate-fade-in-up"
          style={{ animationDelay: "0.3s" }}
        >
          <h3 className="text-base font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FaBookOpen className="text-lg" /> Skills to Develop (
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

function ScoreBreakdownItem({ label, value }) {
  if (value == null) return null;
  const pct = Math.round(value * 100);
  const color =
    pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-yellow-500" : "bg-red-400";
  return (
    <div className="bg-white rounded-lg p-2 border border-slate-200 shadow-sm">
      <div className="text-xs text-slate-500 mb-1 truncate">{label}</div>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${color} transition-all`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-slate-700 w-8 text-right">
          {pct}%
        </span>
      </div>
    </div>
  );
}
