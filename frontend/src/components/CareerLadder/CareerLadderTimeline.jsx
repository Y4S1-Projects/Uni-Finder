import React, { useState } from "react";
import { FaCheckCircle, FaLock, FaArrowUp, FaStar, FaTrophy } from "react-icons/fa";
import { CareerDetailModal } from "../career/CareerDetailModal";
import { useCareerDetail } from "../../hooks/useCareerRecommendations";

export default function CareerLadderTimeline({ progressionData, userSkills, userProfile }) {
	const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } = useCareerDetail();

	const { eligible_levels } = progressionData;

	const allLevels = eligible_levels || [];

	if (allLevels.length === 0) {
		return (
			<div className='flex flex-col items-center justify-center p-12 text-center bg-white border border-gray-100 shadow-sm rounded-2xl'>
				<FaLock className='mb-4 text-4xl text-gray-300' />
				<h3 className='mb-2 text-xl font-bold text-gray-800'>Path Locked</h3>
				<p className='max-w-md text-gray-500'>
					No eligible career levels found. Build more skills to unlock career paths!
				</p>
			</div>
		);
	}

	const handleLevelClick = (level) => {
		const recommendationObj = {
			...level,
			role_id: level.role_id,
			role_title: level.role_title || level.role || "Unknown Role",
			domain: level.domain || progressionData.domain,
			readiness_score: level.readiness_score ?? 0,
			match_score: level.match_score ?? level.readiness_score ?? 0,
			confidence_score: level.confidence_score ?? 1.0,
			skill_gap: {
				matched_skills: level.matched_skills ?? [],
				missing_skills: level.missing_skills ?? [],
				readiness_score: level.readiness_score ?? 0,
			},
			description: level.description ?? level.explanation ?? "",
			experience_range: level.experience_range ?? "",
		};
		fetchJobDetail(recommendationObj, userSkills);
	};

	return (
		<div className='relative'>
			{/* Timeline Container */}
			<div className='relative'>
				{/* Vertical Line */}
				<div className='absolute top-0 bottom-0 w-1 left-8 bg-gray-200 rounded-full'></div>

				{/* Level Cards */}
				<div className='space-y-12'>
					{allLevels.map((level, index) => {
						const isAchievable = level.readiness_score >= 0.4;
						const isCurrent = level.is_current;
						const isLocked = level.readiness_score < 0.2 && !isCurrent;

						return (
							<LevelCard
								key={level.level}
								level={level}
								index={index}
								isCurrent={isCurrent}
								isAchievable={isAchievable}
								isLocked={isLocked}
								onClick={() => handleLevelClick(level)}
							/>
						);
					})}
				</div>
			</div>

			<CareerDetailModal
				isOpen={!!selectedJob}
				onClose={closeDetail}
				jobDetail={jobDetail}
				isLoading={detailLoading}
				userProfile={userProfile}
			/>
		</div>
	);
}

function LevelCard({ level, index, isCurrent, isAchievable, isLocked, onClick }) {
	const getCardStyle = () => {
		if (isCurrent) {
			return "bg-indigo-50 border-indigo-500 shadow-md ring-4 ring-indigo-500/5 scale-105 z-10";
		} else if (isLocked) {
			return "bg-gray-50 border-gray-200 opacity-60 grayscale shadow-sm";
		} else {
			return "bg-white border-gray-200 shadow-sm hover:shadow-md";
		}
	};

	const getIcon = () => {
		if (isCurrent) return <FaStar className='text-2xl text-yellow-500' />;
		if (isAchievable) return <FaArrowUp className='text-2xl text-indigo-600' />;
		if (isLocked) return <FaLock className='text-2xl text-gray-400' />;
		return <FaTrophy className='text-2xl text-indigo-500' />;
	};

	const textColor = isCurrent ? "text-indigo-900" : "text-gray-900";

	return (
		<div className='relative flex items-start gap-8 ml-4'>
			{/* Timeline Node */}
			<div className='relative z-10 flex-shrink-0'>
				<div
					className={`flex items-center justify-center w-16 h-16 transition-all duration-300 rounded-full border-2 ${
						isCurrent ? "bg-white border-indigo-400 shadow-lg" : "bg-white border-gray-100 shadow-md"
					}`}>
					{getIcon()}
				</div>

				{isCurrent && (
					<div className='absolute -top-2 -right-2'>
						<span className='flex w-6 h-6'>
							<span className='absolute inline-flex w-full h-full bg-yellow-400 rounded-full opacity-75 animate-ping'></span>
							<span className='relative inline-flex items-center justify-center w-6 h-6 bg-yellow-500 rounded-full'>
								<FaCheckCircle className='text-sm text-white' />
							</span>
						</span>
					</div>
				)}
			</div>

			{/* Card Content */}
			<div
				className={`flex-1 p-6 rounded-2xl transition-all duration-300 cursor-pointer border ${getCardStyle()} ${
					isLocked ? "cursor-not-allowed" : "hover:-translate-y-1"
				}`}
				onClick={!isLocked ? onClick : undefined}>
				{/* Header */}
				<div className='flex items-start justify-between mb-4'>
					<div>
						<div className='flex items-center gap-3 mb-2'>
							<span
								className={`text-[10px] font-bold px-2 py-1 rounded-full border ${
									isCurrent ? "bg-indigo-100 text-indigo-700 border-indigo-200" : "bg-gray-100 text-gray-600 border-gray-200"
								}`}>
								TIER {level.level}
							</span>
							{isCurrent && (
								<span className='px-3 py-1 text-[10px] font-black text-yellow-700 bg-yellow-100 border border-yellow-200 rounded-full tracking-wider uppercase'>
									YOU ARE HERE
								</span>
							)}
						</div>
						<h3 className={`text-2xl font-bold ${textColor} mb-1 tracking-tight`}>{level.role_title}</h3>
						<p className={`text-sm ${isCurrent ? "text-indigo-700/80" : "text-gray-600"}`}>{level.experience_range}</p>
					</div>

					<div className='text-right'>
						<div
							className={`mb-1 text-3xl font-extrabold ${isAchievable ? "text-indigo-600" : "text-gray-400"}`}>
							{level.readiness_score >= 1 ? 100 : Math.floor(level.readiness_score * 100)}%
						</div>
						<p className='text-xs text-gray-600'>Ready</p>
					</div>
				</div>

				{/* Progress Bar */}
				<div className='mb-4'>
					<div className='w-full h-2 overflow-hidden bg-gray-200 rounded-full'>
						<div
							className={`h-full transition-all duration-700 rounded-full ${
								isAchievable ? "bg-indigo-600 shadow-[0_0_8px_rgba(79,70,229,0.4)]" : "bg-gray-300"
							}`}
							style={{ width: `${level.readiness_score * 100}%` }}
						/>
					</div>
				</div>

				{/* Skills Summary */}
				<div className='grid grid-cols-2 gap-4 mt-4 text-sm'>
					<div className={isCurrent ? "text-indigo-900/90" : "text-gray-600"}>
						<span className='font-semibold'>Skills Matched:</span>
						<span className='ml-2 font-bold text-emerald-600'>{level.matched_skills?.length || 0}</span>
					</div>
					<div className={isCurrent ? "text-indigo-900/90" : "text-gray-600"}>
						<span className='font-semibold'>Skills Needed:</span>
						<span className='ml-2 font-bold text-rose-500'>{level.missing_skills?.length || 0}</span>
					</div>
				</div>

				{/* Time Estimate */}
				{level.estimated_time && (
					<div className='pt-4 mt-4 border-t border-gray-200/50'>
						<p className={`text-sm ${isCurrent ? "text-indigo-700/80" : "text-gray-500"}`}>
							<span className='font-semibold'>Estimated Time:</span>
							<span className='ml-2 font-medium'>{level.estimated_time}</span>
						</p>
					</div>
				)}

				{/* CTA */}
				{!isLocked && (
					<button className='w-full px-4 py-2.5 mt-6 font-bold text-indigo-700 transition-all duration-300 rounded-xl border border-indigo-100 bg-indigo-50/50 hover:bg-indigo-100 active:scale-[0.98]'>
						View Details & Learning Path →
					</button>
				)}
			</div>
		</div>
	);
}
