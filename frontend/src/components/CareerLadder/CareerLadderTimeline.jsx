import React, { useState } from "react";
import { FaCheckCircle, FaLock, FaArrowUp, FaStar, FaTrophy } from "react-icons/fa";
import LevelDetailModal from "./LevelDetailModal";

export default function CareerLadderTimeline({ progressionData, userSkills }) {
	const [selectedLevel, setSelectedLevel] = useState(null);
	const [showModal, setShowModal] = useState(false);

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
		setSelectedLevel(level);
		setShowModal(true);
	};

	return (
		<div className='relative'>
			{/* Timeline Container */}
			<div className='relative'>
				{/* Vertical Line */}
				<div className='absolute top-0 bottom-0 w-1 left-8 bg-gradient-to-b from-purple-600 via-blue-500 to-gray-300'></div>

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

			{/* Detail Modal */}
			{showModal && selectedLevel && (
				<LevelDetailModal level={selectedLevel} userSkills={userSkills} onClose={() => setShowModal(false)} />
			)}
		</div>
	);
}

function LevelCard({ level, index, isCurrent, isAchievable, isLocked, onClick }) {
	const getCardStyle = () => {
		if (isCurrent) {
			return {
				background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
				border: "3px solid #5a67d8",
				transform: "scale(1.05)",
			};
		} else if (isLocked) {
			return {
				background: "linear-gradient(135deg, rgba(156, 163, 175, 0.1) 0%, rgba(209, 213, 219, 0.1) 100%)",
				border: "2px solid rgba(156, 163, 175, 0.3)",
				opacity: 0.6,
			};
		} else {
			// Achievable & fallback cards
			return {
				background: "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)",
				borderColor: "rgba(102, 126, 234, 0.3)",
				borderWidth: "2px",
				borderStyle: "solid",
			};
		}
	};

	const getIcon = () => {
		if (isCurrent) return <FaStar className='text-2xl text-yellow-400' />;
		if (isAchievable) return <FaArrowUp className='text-2xl text-blue-500' />;
		if (isLocked) return <FaLock className='text-2xl text-gray-400' />;
		return <FaTrophy className='text-2xl text-purple-500' />;
	};

	const textColor = isCurrent ? "text-white" : "text-gray-800";

	return (
		<div className='relative flex items-start gap-8 ml-4'>
			{/* Timeline Node */}
			<div className='relative z-10 flex-shrink-0'>
				<div
					className='flex items-center justify-center w-16 h-16 transition-transform rounded-full shadow-lg hover:scale-110'
					style={getCardStyle()}>
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
				className={`flex-1 p-6 rounded-2xl shadow-xl transition-all duration-300 cursor-pointer hover:shadow-2xl hover:scale-[1.02] ${isLocked ? "cursor-not-allowed" : ""}`}
				style={getCardStyle()}
				onClick={!isLocked ? onClick : undefined}>
				{/* Header */}
				<div className='flex items-start justify-between mb-4'>
					<div>
						<div className='flex items-center gap-3 mb-2'>
							<span
								className={`text-xs font-semibold px-2 py-1 rounded-full ${isCurrent ? "bg-white/20 text-white" : "bg-purple-100 text-purple-700"}`}>
								TIER {level.level}
							</span>
							{isCurrent && (
								<span className='px-3 py-1 text-sm font-bold text-gray-900 bg-yellow-400 rounded-full animate-pulse'>
									YOU ARE HERE
								</span>
							)}
						</div>
						<h3 className={`text-2xl font-bold ${textColor} mb-1`}>{level.role_title}</h3>
						<p className={`text-sm ${isCurrent ? "text-white/80" : "text-gray-600"}`}>{level.experience_range}</p>
					</div>

					<div className='text-right'>
						<div
							className='mb-1 text-3xl font-bold'
							style={{
								background:
									isAchievable ?
										"linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)"
									:	"linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)",
								WebkitBackgroundClip: "text",
								WebkitTextFillColor: "transparent",
							}}>
							{level.readiness_score >= 1 ? 100 : Math.floor(level.readiness_score * 100)}%
						</div>
						<p className='text-xs text-gray-600'>Ready</p>
					</div>
				</div>

				{/* Progress Bar */}
				<div className='mb-4'>
					<div className='w-full h-2 overflow-hidden bg-gray-200 rounded-full'>
						<div
							className='h-full transition-all duration-500 rounded-full'
							style={{
								width: `${level.readiness_score * 100}%`,
								background:
									isAchievable ?
										"linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)"
									:	"linear-gradient(90deg, #9ca3af 0%, #6b7280 100%)",
							}}
						/>
					</div>
				</div>

				{/* Skills Summary */}
				<div className='grid grid-cols-2 gap-4 mt-4 text-sm'>
					<div className={isCurrent ? "text-white/90" : "text-gray-700"}>
						<span className='font-semibold'>Skills Matched:</span>
						<span className='ml-2 font-bold text-green-500'>{level.matched_skills?.length || 0}</span>
					</div>
					<div className={isCurrent ? "text-white/90" : "text-gray-700"}>
						<span className='font-semibold'>Skills Needed:</span>
						<span className='ml-2 font-bold text-red-500'>{level.missing_skills?.length || 0}</span>
					</div>
				</div>

				{/* Time Estimate */}
				{level.estimated_time && (
					<div className='pt-4 mt-4 border-t border-gray-200/50'>
						<p className={`text-sm ${isCurrent ? "text-white/80" : "text-gray-600"}`}>
							<span className='font-semibold'>Estimated Time:</span>
							<span className='ml-2'>{level.estimated_time}</span>
						</p>
					</div>
				)}

				{/* CTA */}
				{!isLocked && (
					<button className='w-full px-4 py-2 mt-6 font-semibold text-purple-700 transition-all duration-300 rounded-lg shadow-sm bg-white/90 hover:shadow-md hover:bg-white'>
						View Details & Learning Path →
					</button>
				)}
			</div>
		</div>
	);
}
