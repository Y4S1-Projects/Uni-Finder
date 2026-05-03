import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, useInView } from "framer-motion";
import { useCountUp } from "../../hooks/useCountUp";
import {
  FaStar,
  FaEye,
  FaCheckCircle,
  FaBookOpen,
  FaRocket,
} from "react-icons/fa";

const MotionDiv = motion?.div || "div";
const MotionSpan = motion?.span || "span";

export function CareerRecommendationCard({
  recommendation,
  rank,
  isBestMatch = false,
  onViewDetails,
  userSkills,
}) {
  const navigate = useNavigate();
  const {
    role_id,
    role_title,
    domain,
    match_score,
    next_role,
    next_role_title,
    skill_gap,
  } = recommendation;

  const viewCareerLadder = () => {
    navigate("/career-ladder", {
      state: {
        userSkills: userSkills,
        selectedDomain: domain,
        recommendations: [recommendation],
      },
    });
  };

  // Use weighted readiness from scoring engine (top-level), fall back to legacy skill_gap
  const readinessPercent =
    recommendation.readiness_score !== undefined
      ? parseInt((recommendation.readiness_score * 100).toFixed(0), 10)
      : skill_gap && skill_gap.readiness_score !== undefined
        ? parseInt((skill_gap.readiness_score * 100).toFixed(0), 10)
        : 0;

  const matchPercent =
    match_score !== undefined ? parseInt((match_score * 100).toFixed(0), 10) : 0;

  const cardRef = useRef(null);
  const isInView = useInView(cardRef, { once: true, amount: 0.2 });

  const { value: animatedMatch } = useCountUp(matchPercent, 1000, isInView);
  const { value: animatedReadiness } = useCountUp(readinessPercent, 1000, isInView);

  const staggerContainer = {
    whileInView: {
      transition: { staggerChildren: 0.05 }
    }
  };

  const staggerChild = {
    initial: { opacity: 0, y: 10 },
    whileInView: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] } }
  };

  return (
    <MotionDiv
      ref={cardRef}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      className={`p-6 mb-6 rounded-2xl relative transition-all duration-[250ms] ease-[cubic-bezier(0.4,0,0.2,1)] hover:-translate-y-[3px] hover:shadow-lg hover:scale-[1.01] shadow-md border ${
        isBestMatch
          ? "bg-white border-indigo-200 ring-2 ring-indigo-50"
          : "bg-white border-gray-200" 
      }`}
    >
      <style>
        {`
          @keyframes softPulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.9; }
          }
          .animate-softPulse {
            animation: softPulse 2s ease-in-out infinite;
          }
        `}
      </style>
      {/* Best Match Badge */}
      {isBestMatch && (
        <div className="absolute -top-3 right-6 bg-indigo-600 text-white px-4 py-1 rounded-full text-[11px] font-bold shadow-sm flex items-center gap-1.5 uppercase tracking-wide animate-softPulse">
          <FaStar className="text-[10px]" /> BEST MATCH
        </div>
      )}

      {/* Header: Title, Domain, Scores */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-xl font-bold text-gray-900 mb-2 leading-tight">
            {rank}. {role_title || role_id}
          </h4>
          <div className="inline-flex">
            <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md">
              {domain?.replace(/_/g, " ")}
            </span>
          </div>
        </div>

        <div className="text-right shrink-0">
          <div className="text-2xl font-bold text-indigo-600">
            {animatedMatch}%
          </div>
          <div className="text-[11px] text-gray-500 font-semibold uppercase tracking-wider">
            Match Score
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full mb-6 bg-gray-200 rounded-full h-1.5 overflow-hidden">
        <MotionDiv
          className="h-full bg-indigo-600 rounded-full"
          initial={{ width: 0 }}
          whileInView={{ width: `${matchPercent}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>

      {/* Next Step Box */}
      {next_role && (
        <div className="bg-gray-50 rounded-xl p-4 mb-6 flex justify-between items-center border border-gray-100">
          <div>
            <div className="flex items-center gap-1.5 text-xs text-indigo-700 font-bold mb-1">
              <FaRocket className="text-sm" /> Next Step:
            </div>
            <div className="text-sm text-[#4b5563] ml-5">
              {next_role_title || next_role}
            </div>
          </div>
          <button
            onClick={viewCareerLadder}
            className="text-white text-xs font-bold px-4 py-2 rounded-xl border border-transparent transition-all duration-200 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
          >
            View Path
          </button>
        </div>
      )}

      {/* Stats and Skills Flex */}
      <div className="flex flex-col md:flex-row gap-6 mb-6">
        {/* Readiness */}
        <div className="shrink-0 md:w-24">
          <div className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider mb-1">
            Readiness
          </div>
          <div className="text-xl font-bold text-indigo-600">
            {animatedReadiness}%
          </div>
        </div>

        {/* Skills You Have */}
        <div className="flex-1">
          <div className="flex items-center gap-1.5 mb-2.5">
            <FaCheckCircle className="text-indigo-600 text-sm" />
            <span className="text-xs font-bold text-indigo-700">
              Skills You Have ({skill_gap?.matched_skills?.length || 0})
            </span>
          </div>
          <MotionDiv 
            className="flex flex-wrap gap-1.5"
            variants={staggerContainer}
            initial="initial"
            whileInView="whileInView"
            viewport={{ once: true }}
          >
            {skill_gap?.matched_skills?.slice(0, 5).map((s) => (
              <MotionSpan
                variants={staggerChild}
                key={s.id || s}
                className="text-[11px] font-medium bg-indigo-50 border border-indigo-100 text-indigo-700 px-2.5 py-1 rounded-full whitespace-nowrap"
              >
                {s.name || s.id || s}
              </MotionSpan>
            ))}
            {skill_gap?.matched_skills?.length > 5 && (
              <MotionSpan variants={staggerChild} className="text-[11px] font-medium text-indigo-700 px-1 py-1 rounded-full whitespace-nowrap self-center">
                +{skill_gap.matched_skills.length - 5} more
              </MotionSpan>
            )}
          </MotionDiv>
        </div>

        {/* Skills to Learn */}
        <div className="flex-1">
          <div className="flex items-center gap-1.5 mb-2.5">
            <FaBookOpen className="text-gray-600 text-sm" />
            <span className="text-xs font-bold text-gray-800">
              Skills to Learn ({skill_gap?.missing_skills?.length || 0})
            </span>
          </div>
          <MotionDiv 
            className="flex flex-wrap gap-1.5"
            variants={staggerContainer}
            initial="initial"
            whileInView="whileInView"
            viewport={{ once: true }}
          >
            {skill_gap?.missing_skills?.slice(0, 5).map((s) => (
              <MotionSpan
                variants={staggerChild}
                key={s.id || s}
                className="text-[11px] font-medium border border-gray-200 text-gray-600 px-2.5 py-1 rounded-full bg-white whitespace-nowrap"
              >
                {s.name || s.id || s}
              </MotionSpan>
            ))}
            {skill_gap?.missing_skills?.length > 5 && (
              <MotionSpan variants={staggerChild} className="text-[11px] font-medium text-gray-500 px-1 py-1 rounded-full whitespace-nowrap self-center">
                +{skill_gap.missing_skills.length - 5} more
              </MotionSpan>
            )}
          </MotionDiv>
        </div>
      </div>

      {/* View Details Button */}
      <div>
        <button
          onClick={() => onViewDetails(recommendation)}
          className="text-white text-xs font-bold px-5 py-2.5 rounded-xl border border-transparent transition-all duration-200 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] flex items-center gap-2 inline-flex bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
        >
          <FaEye className="text-sm" /> View Details & AI Explanation
        </button>
      </div>
    </MotionDiv>
  );
}
