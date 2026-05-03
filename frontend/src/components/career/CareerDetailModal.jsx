/**
 * Career Detail Modal Component
 * Phase D: Full-screen modal showing detailed career information, score breakdown,
 * core/supporting/missing skill clusters, ranking explanation, seniority fit,
 * ladder position, and AI explanation.
 */
import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ScoreCard } from "./ScoreDisplay";
import { SkillTagList } from "./SkillTags";
import { NextRoleBadge } from "./NextRoleBadge";
import { DomainBadge } from "./DomainBadge";
import { AIExplanation, AILoadingState } from "./AIExplanation";
import { IoClose } from "react-icons/io5";
import { FaCheckCircle, FaBookOpen, FaCogs, FaChartBar, FaExclamationTriangle, FaInfoCircle } from "react-icons/fa";
import { useCountUp } from "../../hooks/useCountUp";

export function CareerDetailModal({ isOpen, onClose, jobDetail, isLoading, onViewPath, userProfile }) {
	const [isMounted, setIsMounted] = useState(false);

	useEffect(() => {
		if (!isOpen) {
			setIsMounted(false);
			return;
		}
		const id = requestAnimationFrame(() => setIsMounted(true));
		return () => cancelAnimationFrame(id);
	}, [isOpen]);

	if (!isOpen) return null;

	return createPortal(
		<div
			className='fixed inset-0 flex items-center justify-center z-[9999] overflow-auto py-8'
			onClick={onClose}
		>
			<div
				className={`absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-300 ${
					isMounted ? "opacity-100" : "opacity-0"
				}`}
			/>
			<div
				className={`bg-gradient-to-br from-white via-blue-50 to-indigo-50 rounded-3xl max-w-2xl w-full mx-4 p-8 relative shadow-2xl border-2 border-blue-100 max-h-[85vh] overflow-auto transform transition-all duration-300 ease-out ${
					isMounted ? "opacity-100 scale-100" : "opacity-0 scale-95"
				}`}
				onClick={(e) => e.stopPropagation()}
			>
				{/* Close Button */}
				<CloseButton onClick={onClose} />

				{/* Content */}
				{isLoading ?
					<AILoadingState />
				: jobDetail ?
					<CareerDetailContent jobDetail={jobDetail} onViewPath={onViewPath} userProfile={userProfile} />
				:	<ErrorState />}
			</div>
		</div>,
		document.body,
	);
}

function CloseButton({ onClick }) {
	return (
		<button
			type='button'
			onClick={onClick}
			className='absolute z-50 flex items-center justify-center w-12 h-12 transition-all duration-200 bg-white/95 rounded-full shadow-md top-4 right-4 hover:scale-110 hover:shadow-lg group border-none outline-none ring-0 focus:outline-none focus:ring-2 focus:ring-purple-500/30'
			style={{ boxShadow: "0 8px 24px rgba(99, 102, 241, 0.16)" }}
			aria-label='Close modal'>
			<IoClose className='text-3xl text-purple-600 transition-all duration-200 group-hover:text-purple-800 group-hover:rotate-90' />
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
			<div className='mb-6 animate-slide-in-left'>
				<h2 className='mb-3 text-3xl font-bold text-transparent bg-gradient-to-r from-blue-700 via-indigo-600 to-purple-600 bg-clip-text'>
					{jobDetail.role_title || jobDetail.role_id}
				</h2>

				<div className='flex flex-wrap items-center gap-3'>
					<DomainBadge domain={jobDetail.domain} size='large' />

					{/* Best match badge */}
					{jobDetail.is_best_match && (
						<span className='text-xs px-2.5 py-1 rounded-full bg-yellow-100 text-yellow-800 font-semibold border border-yellow-300 shadow-sm'>
							★ Best Match
						</span>
					)}

					{/* Seniority badge */}
					{jobDetail.seniority != null && (
						<span className='text-xs px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700 font-medium border border-indigo-200 shadow-sm'>
							Seniority: {jobDetail.seniority}
						</span>
					)}

					{/* Ladder position badge */}
					{jobDetail.ladder_position != null && jobDetail.ladder_length != null && (
						<span className='text-xs px-2.5 py-1 rounded-full bg-purple-100 text-purple-700 font-medium border border-purple-200 shadow-sm'>
							Ladder: {jobDetail.ladder_position}/{jobDetail.ladder_length}
						</span>
					)}

					{/* Profile source */}
					{jobDetail.profile_source === "synthetic" && (
						<span className='text-xs px-2.5 py-1 rounded-full bg-orange-100 text-orange-700 font-medium border border-orange-200 shadow-sm'>
							Synthetic Profile
						</span>
					)}

					{userProfile && (
						<div className='flex flex-wrap items-center gap-2 pl-4 ml-2 border-l-2 border-slate-200'>
							{userProfile.experienceLevel && (
								<span className='text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium whitespace-nowrap border border-slate-200 shadow-sm'>
									<span className='opacity-75'>Exp:</span> {userProfile.experienceLevel}
								</span>
							)}
							{userProfile.educationLevel && (
								<span className='text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium whitespace-nowrap border border-slate-200 shadow-sm'>
									<span className='opacity-75'>Edu:</span> {userProfile.educationLevel}
								</span>
							)}
							{userProfile.currentStatus && (
								<span className='text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium whitespace-nowrap border border-slate-200 shadow-sm'>
									<span className='opacity-75'>Status:</span> {userProfile.currentStatus}
								</span>
							)}
						</div>
					)}
				</div>
			</div>

			<AnimatedSection className='flex gap-4 mb-6' delay={100}>
				<ScoreCard score={jobDetail.readiness_score} label='Readiness' variant='green' />
				<ScoreCard score={jobDetail.match_score} label='Match Score' variant='blue' />
				{jobDetail.confidence_score != null && (
					<ScoreCard score={jobDetail.confidence_score} label='Confidence' variant='purple' />
				)}
			</AnimatedSection>

			{/* Score Breakdown Grid */}
			{Object.keys(sb).length > 0 && (
				<AnimatedSection className='mb-6' delay={150}>
					<h3 className='flex items-center gap-2 mb-3 text-base font-semibold text-indigo-700'>
						<FaChartBar className='text-lg' /> Score Breakdown
					</h3>
					<div className='grid grid-cols-2 gap-2 sm:grid-cols-3'>
						<ScoreBreakdownItem label='Core Coverage' value={sb.core_skill_coverage_score} />
						<ScoreBreakdownItem label='Skill Match' value={sb.skill_match_score} />
						<ScoreBreakdownItem label='Domain Fit' value={sb.domain_preference_score} />
						<ScoreBreakdownItem label='Experience Fit' value={sb.experience_fit_score} />
						<ScoreBreakdownItem label='Seniority Fit' value={sb.seniority_fit_score} />
						<ScoreBreakdownItem label='Confidence' value={sb.confidence_score} />
					</div>
				</AnimatedSection>
			)}

			{/* Why Ranked Here / Why Best Match */}
			{(expl.why_ranked_here || expl.why_best_match) && (
				<AnimatedSection className='p-4 mb-6 border border-blue-200 bg-blue-50 rounded-xl' delay={180}>
					<h3 className='flex items-center gap-2 mb-2 text-sm font-semibold text-blue-700'>
						<FaInfoCircle /> Ranking Explanation
					</h3>
					{expl.why_ranked_here && <p className='mb-1 text-sm text-blue-900'>{expl.why_ranked_here}</p>}
					{expl.why_best_match && <p className='text-sm text-blue-800'>{expl.why_best_match}</p>}
					{expl.domain_impact && <p className='mt-1 text-xs text-blue-600'>{expl.domain_impact}</p>}
					{expl.seniority_fit && <p className='mt-1 text-xs text-blue-600'>{expl.seniority_fit}</p>}
				</AnimatedSection>
			)}

			{/* What Lowers Readiness */}
			{expl.why_not_more_ready && (
				<AnimatedSection className='p-4 mb-6 border bg-amber-50 border-amber-200 rounded-xl' delay={200}>
					<h3 className='flex items-center gap-2 mb-2 text-sm font-semibold text-amber-700'>
						<FaExclamationTriangle /> What Lowers Readiness
					</h3>
					<p className='text-sm text-amber-900'>{expl.why_not_more_ready}</p>
				</AnimatedSection>
			)}

			{/* Next Career Step */}
			{jobDetail.next_role && (
				<div className='mb-6'>
					<NextRoleBadge
						nextRole={jobDetail.next_role}
						nextRoleTitle={jobDetail.next_role_title}
						variant='full'
						onViewPath={onViewPath}
					/>
				</div>
			)}

			{/* Matched Core Skills */}
			{coreSkills.length > 0 && (
				<AnimatedSection className='mb-4' delay={250}>
					<h3 className='flex items-center gap-2 mb-3 text-base font-semibold text-green-700'>
						<FaCheckCircle className='text-lg' /> Core Skills Matched ({coreSkills.length})
					</h3>
					<SkillTagList skills={coreSkills} variant='matched' maxDisplay={100} size='large' showLabel={false} />
				</AnimatedSection>
			)}

			{/* Matched Supporting Skills */}
			{supportSkills.length > 0 && (
				<AnimatedSection className='mb-4' delay={280}>
					<h3 className='flex items-center gap-2 mb-3 text-base font-semibold text-teal-600'>
						<FaCogs className='text-lg' /> Supporting Skills ({supportSkills.length})
					</h3>
					<SkillTagList skills={supportSkills} variant='matched' maxDisplay={50} size='large' showLabel={false} />
				</AnimatedSection>
			)}

			{/* Missing Critical Skills */}
			{missingCritical.length > 0 && (
				<AnimatedSection className='mb-6' delay={300}>
					<h3 className='flex items-center gap-2 mb-3 text-base font-semibold text-red-600'>
						<FaExclamationTriangle className='text-lg' /> Missing Critical Skills ({missingCritical.length})
					</h3>
					<SkillTagList skills={missingCritical} variant='missing' maxDisplay={100} size='large' showLabel={false} />
				</AnimatedSection>
			)}

			{/* Fallback: flat matched/missing if Phase D clusters are empty */}
			{coreSkills.length === 0 && supportSkills.length === 0 && jobDetail.matched_skills?.length > 0 && (
				<AnimatedSection className='mb-6' delay={250}>
					<h3 className='flex items-center gap-2 mb-3 text-base font-semibold text-purple-700'>
						<FaCheckCircle className='text-lg' /> Skills You Already Have ({jobDetail.matched_skills.length})
					</h3>
					<SkillTagList
						skills={jobDetail.matched_skills}
						variant='matched'
						maxDisplay={100}
						size='large'
						showLabel={false}
					/>
				</AnimatedSection>
			)}

			{missingCritical.length === 0 && jobDetail.missing_skills?.length > 0 && (
				<AnimatedSection className='mb-6' delay={300}>
					<h3 className='flex items-center gap-2 mb-3 text-base font-semibold text-gray-700'>
						<FaBookOpen className='text-lg' /> Skills to Develop ({jobDetail.missing_skills.length})
					</h3>
					<SkillTagList
						skills={jobDetail.missing_skills}
						variant='missing'
						maxDisplay={100}
						size='large'
						showLabel={false}
					/>
				</AnimatedSection>
			)}

			{/* AI Explanation */}
			<AIExplanation explanation={jobDetail.explanation} />
		</>
	);
}

function ErrorState() {
	return <div className='py-8 text-center text-gray-500'>Failed to load details. Please try again.</div>;
}

function ScoreBreakdownItem({ label, value }) {
	const [isVisible, setIsVisible] = useState(false);
	const itemRef = useRef(null);
	const safeValue = value == null ? 0 : value;
	const pct = Math.round(safeValue * 100);
	const { value: animatedPct } = useCountUp(pct, 1000, isVisible);
	const color =
		pct >= 70 ? "bg-green-500"
		: pct >= 40 ? "bg-yellow-500"
		: "bg-red-400";

	useEffect(() => {
		if (!itemRef.current) return undefined;
		const observer = new IntersectionObserver(
			([entry]) => {
				if (!entry.isIntersecting) return;
				setIsVisible(true);
				observer.disconnect();
			},
			{ threshold: 0.2 },
		);
		observer.observe(itemRef.current);
		return () => observer.disconnect();
	}, []);

	if (value == null) return null;

	return (
		<div ref={itemRef} className='p-2 bg-white border rounded-lg shadow-sm border-slate-200'>
			<div className='mb-1 text-xs truncate text-slate-500'>{label}</div>
			<div className='flex items-center gap-2'>
				<div className='flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden'>
					<div className={`h-full rounded-full ${color} transition-all duration-700 ease-out`} style={{ width: `${animatedPct}%` }} />
				</div>
				<span className='w-8 text-xs font-semibold text-right text-slate-700'>{animatedPct}%</span>
			</div>
		</div>
	);
}

function AnimatedSection({ children, className = "", delay = 0 }) {
	const [isVisible, setIsVisible] = useState(false);
	const sectionRef = useRef(null);

	useEffect(() => {
		if (!sectionRef.current) return undefined;
		const observer = new IntersectionObserver(
			([entry]) => {
				if (!entry.isIntersecting) return;
				setIsVisible(true);
				observer.disconnect();
			},
			{ threshold: 0.2 },
		);
		observer.observe(sectionRef.current);
		return () => observer.disconnect();
	}, []);

	return (
		<div
			ref={sectionRef}
			className={`${className} transition-all duration-500 ease-out ${
				isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-7"
			}`}
			style={{ transitionDelay: `${delay}ms` }}
		>
			{children}
		</div>
	);
}
