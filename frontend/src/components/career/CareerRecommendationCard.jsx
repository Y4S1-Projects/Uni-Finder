import React from "react";
import { useNavigate } from "react-router-dom";
import { FaStar, FaEye, FaCheckCircle, FaBookOpen, FaRocket } from "react-icons/fa";

export function CareerRecommendationCard({ recommendation, rank, isBestMatch = false, onViewDetails, userSkills }) {
	const navigate = useNavigate();
	const { role_id, role_title, domain, match_score, next_role, next_role_title, skill_gap } = recommendation;

	const viewCareerLadder = () => {
		navigate("/career-ladder", {
			state: {
				userSkills: userSkills,
				selectedDomain: domain,
				recommendations: [recommendation],
			},
		});
	};

	const readinessPercent =
		skill_gap && skill_gap.readiness_score !== undefined ? (skill_gap.readiness_score * 100).toFixed(0) : 0;

	const matchPercent = match_score !== undefined ? (match_score * 100).toFixed(0) : 0;

	return (
		<div
			className={`p-6 mb-6 rounded-2xl relative transition-all duration-300 shadow-sm border ${
				isBestMatch ? "bg-gradient-to-br from-[#f8f9ff] to-[#f3f5ff] border-[#e2e8f0]" : "bg-[#f8fbff] border-[#eaf2ff]" // matching the light blue bg tone
			}`}>
			{/* Best Match Badge */}
			{isBestMatch && (
				<div className='absolute -top-3 right-6 bg-[#b68bf5] text-white px-4 py-1 rounded-full text-[11px] font-bold shadow-sm flex items-center gap-1.5 uppercase tracking-wide'>
					<FaStar className='text-[10px]' /> BEST MATCH
				</div>
			)}

			{/* Header: Title, Domain, Scores */}
			<div className='flex items-start justify-between mb-4'>
				<div>
					<h4 className='text-xl font-bold text-[#4338ca] mb-2 leading-tight'>
						{rank}. {role_title || role_id}
					</h4>
					<div className='inline-flex'>
						<span className='text-[10px] font-bold uppercase tracking-widest text-[#6b21a8] bg-[#f3e8ff] px-2.5 py-1 rounded-md'>
							{domain?.replace(/_/g, " ")}
						</span>
					</div>
				</div>

				<div className='text-right shrink-0'>
					<div className='text-2xl font-bold text-[#4338ca]'>{matchPercent}%</div>
					<div className='text-[11px] text-gray-500 font-semibold uppercase tracking-wider'>Match Score</div>
				</div>
			</div>

			{/* Progress Bar */}
			<div className='w-full bg-[#e2e8f0] rounded-full h-1.5 mb-6 overflow-hidden'>
				<div className='bg-[#3b82f6] h-1.5 rounded-full' style={{ width: `${matchPercent}%` }}></div>
			</div>

			{/* Next Step Box */}
			{next_role && (
				<div className='bg-[#fcfaff] rounded-xl p-4 mb-6 flex justify-between items-center border border-[#f3e8ff]'>
					<div>
						<div className='flex items-center gap-1.5 text-xs text-[#6b21a8] font-bold mb-1'>
							<FaRocket className='text-sm' /> Next Step:
						</div>
						<div className='text-sm text-[#4b5563] ml-5'>{next_role_title || next_role}</div>
					</div>
					<button
						onClick={viewCareerLadder}
						className='text-white text-xs font-bold px-4 py-2 rounded-lg transition-all shadow-sm hover:shadow-md hover:scale-[1.02]'
						style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
						View Path
					</button>
				</div>
			)}

			{/* Stats and Skills Flex */}
			<div className='flex flex-col gap-6 mb-6 md:flex-row'>
				{/* Readiness */}
				<div className='shrink-0 md:w-24'>
					<div className='text-[10px] text-gray-500 font-semibold uppercase tracking-wider mb-1'>Readiness</div>
					<div className='text-xl font-bold text-[#6b21a8]'>{readinessPercent}%</div>
				</div>

				{/* Skills You Have */}
				<div className='flex-1'>
					<div className='flex items-center gap-1.5 mb-2.5'>
						<FaCheckCircle className='text-[#9333ea] text-sm' />
						<span className='text-xs font-bold text-[#7e22ce]'>
							Skills You Have ({skill_gap?.matched_skills?.length || 0})
						</span>
					</div>
					<div className='flex flex-wrap gap-1.5'>
						{skill_gap?.matched_skills?.slice(0, 5).map((s) => (
							<span
								key={s.id || s}
								className='text-[11px] font-medium bg-[#f3e8ff] border border-[#e9d5ff] text-[#7e22ce] px-2.5 py-1 rounded-full whitespace-nowrap'>
								{s.name || s.id || s}
							</span>
						))}
						{skill_gap?.matched_skills?.length > 5 && (
							<span className='text-[11px] font-medium text-[#7e22ce] px-1 py-1 rounded-full whitespace-nowrap'>
								+{skill_gap.matched_skills.length - 5} more
							</span>
						)}
					</div>
				</div>

				{/* Skills to Learn */}
				<div className='flex-1'>
					<div className='flex items-center gap-1.5 mb-2.5'>
						<FaBookOpen className='text-sm text-gray-600' />
						<span className='text-xs font-bold text-gray-800'>
							Skills to Learn ({skill_gap?.missing_skills?.length || 0})
						</span>
					</div>
					<div className='flex flex-wrap gap-1.5'>
						{skill_gap?.missing_skills?.slice(0, 5).map((s) => (
							<span
								key={s.id || s}
								className='text-[11px] font-medium border border-gray-200 text-gray-600 px-2.5 py-1 rounded-full bg-white whitespace-nowrap'>
								{s.name || s.id || s}
							</span>
						))}
						{skill_gap?.missing_skills?.length > 5 && (
							<span className='text-[11px] font-medium text-gray-500 px-1 py-1 rounded-full whitespace-nowrap'>
								+{skill_gap.missing_skills.length - 5} more
							</span>
						)}
					</div>
				</div>
			</div>

			{/* View Details Button */}
			<div>
				<button
					onClick={() => onViewDetails(recommendation)}
					className='text-white text-xs font-bold px-5 py-2.5 rounded-lg transition-all shadow-md hover:shadow-lg hover:scale-[1.02] flex items-center gap-2 inline-flex'
					style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
					<FaEye className='text-sm' /> View Details & AI Explanation
				</button>
			</div>
		</div>
	);
}
