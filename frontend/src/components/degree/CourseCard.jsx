import React, { useState } from "react";
import AIExplanationBox from "./AIExplanationBox";
import {
	CheckIcon,
	LockIcon,
	StarIcon,
	UniversityIcon,
	BuildingIcon,
	BriefcaseIcon,
	ClockIcon,
	GraduationIcon,
	BookIcon,
	FlaskIcon,
	ChevronDownIcon,
} from "../ui/DegreeIcons";

// ── Score ring ────────────────────────────────────────────────────────────────
function ScoreRing({ score }) {
	const pct = Math.round(score ?? 0);
	const color =
		pct >= 75 ? "text-emerald-600"
		: pct >= 50 ? "text-blue-600"
		: "text-slate-400";
	return (
		<div
			className={`flex-shrink-0 flex flex-col items-center justify-center w-14 h-14 rounded-full border-4 border-current ${color} bg-white shadow-sm`}>
			<span className='text-base font-extrabold leading-none'>{pct}</span>
			<span className='text-[9px] font-bold leading-none opacity-70'>%</span>
		</div>
	);
}

// ── Main component ────────────────────────────────────────────────────────────
export default function CourseCard({ course, isEligible = true, isAspirationnal = false, olMarks = null }) {
	const [expanded, setExpanded] = useState(false);

	const courseName = course.course_name || course.degree_name || "(Unnamed Degree)";
	const universities = Array.isArray(course.universities) ? course.universities : [];
	const score = course.score ?? course.match_score_percentage ?? null;

	// ── Card theme by status ──────────────────────────────────────────────────
	let accentBar, headerBg, statusBadge;

	if (isAspirationnal) {
		accentBar = "from-amber-400 to-orange-500";
		headerBg = "bg-gradient-to-br from-amber-500 to-orange-600";
		statusBadge = (
			<span className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-lg bg-amber-100 text-amber-800 border border-amber-300'>
				<StarIcon className='w-3.5 h-3.5' /> Ambitious
			</span>
		);
	} else if (isEligible) {
		accentBar = "from-blue-500 via-indigo-500 to-cyan-400";
		headerBg = "bg-gradient-to-br from-blue-500 to-indigo-700";
		statusBadge = (
			<span className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-lg bg-blue-100 text-blue-800 border border-blue-300'>
				<CheckIcon className='w-3.5 h-3.5' /> Eligible
			</span>
		);
	} else {
		accentBar = "from-slate-400 to-slate-500";
		headerBg = "bg-slate-600";
		statusBadge = (
			<span className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-100 text-slate-600 border border-slate-300'>
				<LockIcon className='w-3.5 h-3.5' /> Higher Z-Score Needed
			</span>
		);
	}

	// Z-score gap info for aspirational courses
	const zscoreGap = course.zscore_gap;

	return (
		<div
			onClick={() => setExpanded(!expanded)}
			className={`group relative flex flex-col overflow-hidden border rounded-3xl transition-all duration-300 cursor-pointer bg-white shadow-md
				${
					isEligible ? "border-blue-100 hover:border-blue-300 hover:shadow-xl hover:-translate-y-1"
					: isAspirationnal ? "border-amber-200 hover:border-amber-400 hover:shadow-xl hover:-translate-y-1"
					: "border-slate-200 hover:border-slate-300 hover:shadow-md opacity-85 hover:opacity-100"
				}`}>
			{/* Top accent bar */}
			<div className={`h-1.5 bg-gradient-to-r ${accentBar}`} />

			{/* Card header */}
			<div className={`relative px-6 py-4 ${headerBg}`}>
				<div className='absolute top-0 right-0 w-24 h-24 rounded-full pointer-events-none bg-white/10 blur-2xl' />
				<div className='relative z-10 flex items-start justify-between gap-3'>
					<div className='flex-1 min-w-0'>
						<h3 className='text-lg font-extrabold leading-snug text-white'>{courseName}</h3>
					</div>
					<div className='flex flex-col items-end flex-shrink-0 gap-2'>
						{score !== null && <ScoreRing score={score} />}
					</div>
				</div>
				<div className='relative z-10 -mt-2'>{statusBadge}</div>
			</div>

			{/* Card body */}
			<div className='flex flex-col flex-1 p-5 space-y-4'>
				{/* Z-Score gap — aspirational courses */}
				{isAspirationnal && zscoreGap && (
					<div className='flex items-center gap-3 p-3 border rounded-xl bg-amber-50 border-amber-200'>
						<div className='flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg bg-amber-100 text-amber-700'>
							<StarIcon className='w-4 h-4' />
						</div>
						<div className='text-sm'>
							<p className='font-bold text-amber-800'>
								Your Z-Score: {Number(zscoreGap.student_zscore).toFixed(4)} &nbsp;|&nbsp; Required:{" "}
								{Number(zscoreGap.required_cutoff).toFixed(4)}
							</p>
							<p className='text-amber-600 text-xs mt-0.5'>
								Gap: {(Number(zscoreGap.required_cutoff) - Number(zscoreGap.student_zscore)).toFixed(4)} — keep
								striving!
							</p>
						</div>
					</div>
				)}

				{/* Universities */}
				{universities.length > 0 && (
					<div>
						<p className='flex items-center gap-1.5 mb-2 text-xs font-bold tracking-widest uppercase text-blue-500'>
							<UniversityIcon className='w-3 h-3' /> Offering Universities
						</p>
						<div className='flex flex-wrap gap-1.5'>
							{universities.map((uni, i) => (
								<span
									key={i}
									className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-800 border border-blue-200 hover:bg-blue-100 transition-colors'>
									<UniversityIcon className='w-3 h-3' />
									{uni}
								</span>
							))}
						</div>
					</div>
				)}

				{/* Metadata tags */}
				{(course.faculty_department || course.industry || course.job_role || course.duration) && (
					<div className='flex flex-wrap gap-1.5'>
						{course.faculty_department && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200'>
								<BuildingIcon className='w-3 h-3' />
								{course.faculty_department}
							</span>
						)}
						{course.industry && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-cyan-50 text-cyan-700 border border-cyan-200'>
								<BuildingIcon className='w-3 h-3' />
								{course.industry}
							</span>
						)}
						{course.job_role && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-sky-50 text-sky-700 border border-sky-200'>
								<BriefcaseIcon className='w-3 h-3' />
								{course.job_role}
							</span>
						)}
						{course.duration && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-50 text-slate-600 border border-slate-200'>
								<ClockIcon className='w-3 h-3' />
								{course.duration}
							</span>
						)}
					</div>
				)}

				{/* Expanded details */}
				{expanded && (
					<div className='pt-3 mt-1 space-y-3 duration-200 border-t border-slate-100 animate-in fade-in slide-in-from-top-2'>
						{course.degree_programme && (
							<div>
								<p className='flex items-center gap-1.5 mb-1 text-xs font-bold tracking-widest uppercase text-blue-500 pt-2'>
									<GraduationIcon className='w-3 h-3' /> Programme
								</p>
								<p className='text-sm leading-relaxed text-slate-700'>{course.degree_programme}</p>
							</div>
						)}
						{(course.raw_subject_requirements || course.metadata?.raw_subject_requirements) && (
							<div>
								<p className='flex items-center gap-1.5 mb-1 text-xs font-bold tracking-widest uppercase text-blue-500 pt-2'>
									<BookIcon className='w-3 h-3' /> Subject Requirements
								</p>
								<p className='text-sm leading-relaxed text-slate-700'>
									{course.raw_subject_requirements || course.metadata?.raw_subject_requirements}
								</p>
							</div>
						)}
						{course.medium_of_instruction && (
							<div>
								<p className='pt-2 mb-1 text-xs font-bold tracking-widest text-blue-500 uppercase'>Medium</p>
								<p className='text-sm text-slate-700'>{course.medium_of_instruction}</p>
							</div>
						)}
						{course.practical_test !== undefined && (
							<div>
								<p className='flex items-center gap-1.5 mb-1 text-xs font-bold tracking-widest uppercase text-blue-500 pt-2'>
									<FlaskIcon className='w-3 h-3' /> Practical Test
								</p>
								<p className='text-sm text-slate-700'>{course.practical_test ? "Required" : "Not Required"}</p>
							</div>
						)}
						{course.proposed_intake && (
							<div>
								<p className='pt-2 mb-1 text-xs font-bold tracking-widest text-blue-500 uppercase'>Proposed Intake</p>
								<p className='text-sm font-semibold text-slate-700'>{course.proposed_intake} students</p>
							</div>
						)}
						{course.notes && (
							<div>
								<p className='pt-2 mb-1 text-xs font-bold tracking-widest text-blue-500 uppercase'>Notes</p>
								<p className='text-sm italic leading-relaxed text-slate-600'>{course.notes}</p>
							</div>
						)}
					</div>
				)}

				{/* AI Explanation */}
				{course.explanation && (
					<div className='pt-3 mt-auto mb-4'>
						<AIExplanationBox explanation={course.explanation} olMarks={olMarks} />
					</div>
				)}

				{/* Expand toggle */}
				<button className='flex items-center justify-center w-full gap-2 px-4 py-2 mt-auto text-xs font-bold transition-all rounded-xl text-slate-500 bg-slate-50 hover:bg-slate-100 hover:text-slate-700 group-hover:bg-blue-50 group-hover:text-blue-600'>
					{expanded ? "Show Less" : "Show More Details"}
					<span className={`transition-transform duration-300 ${expanded ? "rotate-180" : ""}`}>
						<ChevronDownIcon className='w-4 h-4' />
					</span>
				</button>
			</div>
		</div>
	);
}
