import React, { useState } from "react";
import AIExplanationBox from "./AIExplanationBox";

// ── Inline SVG icons ──────────────────────────────────────────────────────────
const CheckIcon = () => (
	<svg className='w-3.5 h-3.5' fill='none' stroke='currentColor' strokeWidth='2.5' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
	</svg>
);
const LockIcon = () => (
	<svg className='w-3.5 h-3.5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z'
		/>
	</svg>
);
const StarIcon = () => (
	<svg className='w-3.5 h-3.5' fill='currentColor' viewBox='0 0 24 24'>
		<path d='M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.499Z' />
	</svg>
);
const UniversityIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0 0 12 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75Z'
		/>
	</svg>
);
const BuildingIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21'
		/>
	</svg>
);
const BriefcaseIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0M12 12.75h.008v.008H12v-.008Z'
		/>
	</svg>
);
const ClockIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z' />
	</svg>
);
const GraduationIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5'
		/>
	</svg>
);
const BookIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25'
		/>
	</svg>
);
const FlaskIcon = () => (
	<svg className='w-3 h-3' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15M14.25 3.104c.251.023.501.05.75.082M19.8 15a2.25 2.25 0 0 1 .45 1.319c0 1.305-1.044 2.381-2.36 2.381H6.11c-1.316 0-2.36-1.076-2.36-2.381 0-.483.153-.93.45-1.319'
		/>
	</svg>
);
const ChevronDown = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2.5' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='m19.5 8.25-7.5 7.5-7.5-7.5' />
	</svg>
);

// ── Score ring helper ─────────────────────────────────────────────────────────
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

	// ── Card theme by status ─────────────────────────────────────────────────
	let accentBar, headerBg, statusBadge;

	if (isAspirationnal) {
		accentBar = "from-amber-400 to-orange-500";
		headerBg = "bg-amber-600";
		statusBadge = (
			<span className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-lg bg-amber-100 text-amber-800 border border-amber-300'>
				<StarIcon /> Dream Match
			</span>
		);
	} else if (isEligible) {
		accentBar = "from-blue-500 via-indigo-500 to-cyan-400";
		headerBg = "bg-gradient-to-br from-blue-500 to-indigo-700";
		statusBadge = (
			<span className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-lg bg-blue-100 text-blue-800 border border-blue-300'>
				<CheckIcon /> Eligible
			</span>
		);
	} else {
		accentBar = "from-slate-400 to-slate-500";
		headerBg = "bg-slate-600";
		statusBadge = (
			<span className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-100 text-slate-600 border border-slate-300'>
				<LockIcon /> Higher Z-Score Needed
			</span>
		);
	}

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
				{/* Corner blob */}
				<div className='absolute top-0 right-0 w-24 h-24 rounded-full pointer-events-none bg-white/10 blur-2xl' />

				<div className='relative z-10 flex items-start justify-between gap-3'>
					<div className='flex-1 min-w-0'>
						<h3 className='text-lg font-extrabold leading-snug text-white'>{courseName}</h3>
					</div>
					<div className='flex flex-col items-end flex-shrink-0 gap-2'>
						{score !== null && <ScoreRing score={score} />}
					</div>
				</div>

				{/* Status badge */}
				<div className='relative z-10 -mt-2'>{statusBadge}</div>
			</div>

			{/* Card body */}
			<div className='flex flex-col flex-1 p-5 space-y-4'>
				{/* Universities */}
				{universities.length > 0 && (
					<div>
						<p className='flex items-center gap-1.5 mb-2 text-xs font-bold tracking-widest uppercase text-blue-500'>
							<UniversityIcon /> Offering Universities
						</p>
						<div className='flex flex-wrap gap-1.5'>
							{universities.map((uni, i) => (
								<span
									key={i}
									className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-800 border border-blue-200 hover:bg-blue-100 transition-colors'>
									<UniversityIcon />
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
								<BuildingIcon />
								{course.faculty_department}
							</span>
						)}
						{course.industry && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-cyan-50 text-cyan-700 border border-cyan-200'>
								<BuildingIcon />
								{course.industry}
							</span>
						)}
						{course.job_role && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-sky-50 text-sky-700 border border-sky-200'>
								<BriefcaseIcon />
								{course.job_role}
							</span>
						)}
						{course.duration && (
							<span className='inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-50 text-slate-600 border border-slate-200'>
								<ClockIcon />
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
									<GraduationIcon /> Programme
								</p>
								<p className='text-sm leading-relaxed text-slate-700'>{course.degree_programme}</p>
							</div>
						)}
						{(course.raw_subject_requirements || course.metadata?.raw_subject_requirements) && (
							<div>
								<p className='flex items-center gap-1.5 mb-1 text-xs font-bold tracking-widest uppercase text-blue-500 pt-2'>
									<BookIcon /> Subject Requirements
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
									<FlaskIcon /> Practical Test
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
						<ChevronDown />
					</span>
				</button>
			</div>
		</div>
	);
}
