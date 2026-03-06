import React, { useState } from "react";
import {
	FaUniversity,
	FaCheckCircle,
	FaLock,
	FaAward,
	FaBriefcase,
	FaClock,
	FaBuilding,
	FaChevronDown,
	FaStar,
	FaBook,
	FaFlask,
	FaGraduationCap,
} from "react-icons/fa";
import MatchRing from "./MatchRing";
import AIExplanationBox from "./AIExplanationBox";

export default function CourseCard({ course, isEligible = true, isAspirationnal = false }) {
	const [expanded, setExpanded] = useState(false);

	const score = course.interest_match_score ?? course.match_score_percentage ?? course.score ?? 0;
	const courseName = course.course_name || course.degree_name || "(Unnamed Degree)";
	const universities = Array.isArray(course.universities) ? course.universities : [];

	// Determine Card Styling & Badges based on status
	let cardStyle = "bg-white border-slate-200 hover:border-blue-400 shadow-md";
	let badgeStyle = "bg-blue-50 border-blue-200 text-blue-800 text-blue-600";
	let accentColor = "from-blue-400 to-blue-500";
	let statusBadge = null;

	if (isAspirationnal) {
		cardStyle = "bg-gradient-to-br from-amber-50 to-orange-50 border-amber-300 hover:border-amber-400 shadow-md";
		badgeStyle = "bg-amber-100 border-amber-300 text-amber-900 text-amber-700";
		accentColor = "from-amber-400 to-orange-500";
		statusBadge = (
			<div
				className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${badgeStyle} text-xs font-bold tracking-wide uppercase shadow-sm`}>
				<FaAward className='text-lg' />
				Dream Path Match
			</div>
		);
	} else if (isEligible) {
		cardStyle = "bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-300 hover:border-emerald-400 shadow-md";
		badgeStyle = "bg-emerald-100 border-emerald-300 text-emerald-900 text-emerald-700";
		accentColor = "from-emerald-400 to-teal-500";
		statusBadge = (
			<div
				className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${badgeStyle} text-xs font-bold tracking-wide uppercase shadow-sm`}>
				<FaCheckCircle className='text-lg' />
				Eligible
			</div>
		);
	} else {
		cardStyle =
			"bg-gradient-to-br from-slate-50 to-gray-50 border-slate-300 hover:border-slate-400 shadow-sm opacity-85 hover:opacity-95";
		badgeStyle = "bg-slate-200 border-slate-300 text-slate-700 text-slate-600";
		accentColor = "from-slate-400 to-slate-500";
		statusBadge = (
			<div
				className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${badgeStyle} text-xs font-bold tracking-wide uppercase shadow-sm`}>
				<FaLock className='text-lg' />
				Requires Higher Z-Score
			</div>
		);
	}

	return (
		<div
			onClick={() => setExpanded(!expanded)}
			className={`relative p-0 rounded-2xl border transition-all duration-300 flex flex-col h-full overflow-hidden cursor-pointer ${
				expanded ? "hover:shadow-2xl" : "hover:-translate-y-1 hover:shadow-2xl"
			} ${cardStyle}`}>
			{/* Top Accent Bar */}
			<div className={`h-1 bg-gradient-to-r ${accentColor}`}></div>

			<div className='p-6 flex flex-col h-full'>
				{/* Header: Status Badge & Match Score */}
				<div className='flex items-start justify-between gap-4 mb-3'>
					<div className='flex-1'>{statusBadge}</div>
					<div className='flex-shrink-0'>
						<div className='relative'>
							<MatchRing score={score} />
							{score >= 80 && <FaStar className='absolute -top-1 -right-1 text-yellow-400 text-xs drop-shadow-lg' />}
						</div>
					</div>
				</div>

				{/* Score Summary */}
				<div className='mb-3 pb-3 border-b border-slate-100'>
					<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1'>Match Score</p>
					<p className='text-2xl font-bold text-slate-900'>{Math.round(score)}%</p>
				</div>

				{/* Title */}
				<h3 className='mb-3 text-xl font-extrabold leading-tight tracking-tight md:text-2xl text-slate-900 hover:text-blue-600 transition-colors'>
					{courseName}
				</h3>

				{/* Universities */}
				{universities.length > 0 && (
					<div className='mb-3 pb-3 border-b border-slate-100'>
						<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-2'>
							<FaUniversity className='inline mr-1.5' />
							Available at
						</p>
						<div className='flex flex-wrap gap-2'>
							{universities.map((uni, idx) => (
								<span
									key={idx}
									className='inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-full bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 transition-colors'>
									{uni}
								</span>
							))}
						</div>
					</div>
				)}

				{/* Metadata Tags */}
				{(course.industry || course.job_role || course.duration || course.faculty_department) && (
					<div className='mb-3 pb-3 border-b border-slate-100'>
						<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-2'>Details</p>
						<div className='flex flex-wrap gap-2'>
							{course.faculty_department && (
								<span className='inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors'>
									<FaBuilding className='text-indigo-500' />
									{course.faculty_department}
								</span>
							)}
							{course.industry && (
								<span className='inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 transition-colors'>
									<FaBuilding className='text-purple-500' />
									{course.industry}
								</span>
							)}
							{course.job_role && (
								<span className='inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg bg-cyan-50 text-cyan-700 border border-cyan-200 hover:bg-cyan-100 transition-colors'>
									<FaBriefcase className='text-cyan-500' />
									{course.job_role}
								</span>
							)}
							{course.duration && (
								<span className='inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg bg-orange-50 text-orange-700 border border-orange-200 hover:bg-orange-100 transition-colors'>
									<FaClock className='text-orange-500' />
									{course.duration}
								</span>
							)}
						</div>
					</div>
				)}

				{/* Expanded Content */}
				{expanded && (
					<div className='mb-3 pb-3 border-b border-slate-100 space-y-3 animate-in fade-in slide-in-from-top-2 duration-300'>
						{/* Degree Programme */}
						{course.degree_programme && (
							<div>
								<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-2'>
									<FaGraduationCap /> Programme
								</p>
								<p className='text-sm text-slate-700 leading-relaxed'>{course.degree_programme}</p>
							</div>
						)}

						{/* Subject Requirements */}
						{(course.raw_subject_requirements || course.metadata?.raw_subject_requirements) && (
							<div>
								<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-2'>
									<FaBook /> Subject Requirements
								</p>
								<p className='text-sm text-slate-700 leading-relaxed'>
									{course.raw_subject_requirements || course.metadata?.raw_subject_requirements}
								</p>
							</div>
						)}

						{/* Medium of Instruction */}
						{course.medium_of_instruction && (
							<div>
								<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1'>Medium</p>
								<p className='text-sm text-slate-700'>{course.medium_of_instruction}</p>
							</div>
						)}

						{/* Practical Test */}
						{course.practical_test !== undefined && (
							<div>
								<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-2'>
									<FaFlask /> Practical Test
								</p>
								<p className='text-sm text-slate-700'>
									{course.practical_test ? "Yes - Required" : "No - Not Required"}
								</p>
							</div>
						)}

						{/* Proposed Intake */}
						{course.proposed_intake && (
							<div>
								<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1'>Proposed Intake</p>
								<p className='text-sm text-slate-700 font-semibold'>{course.proposed_intake} students</p>
							</div>
						)}

						{/* Notes */}
						{course.notes && (
							<div>
								<p className='text-xs font-bold uppercase tracking-wider text-slate-500 mb-1'>Additional Notes</p>
								<p className='text-sm text-slate-700 leading-relaxed italic'>{course.notes}</p>
							</div>
						)}
					</div>
				)}

				{/* Explanation Box */}
				{course.explanation && (
					<div className='mt-auto pt-3'>
						<AIExplanationBox explanation={course.explanation} />
					</div>
				)}

				{/* Expand/Collapse Indicator */}
				<div className='mt-3 pt-3 border-t border-slate-100 flex items-center justify-center'>
					<button className='flex items-center justify-center gap-2 py-2 px-4 text-sm font-bold text-slate-600 bg-slate-50 hover:bg-slate-100 rounded-lg transition-all hover:gap-3 w-full'>
						{expanded ? "Show Less" : "Show More Details"}
						<FaChevronDown className={`text-xs transition-transform duration-300 ${expanded ? "rotate-180" : ""}`} />
					</button>
				</div>
			</div>
		</div>
	);
}
