import React from "react";
import { UserIcon, RefreshIcon } from "../../ui/DegreeIcons";

/**
 * ALResultsSummary — shown at top of Step 3 results.
 * Displays the user's inputs as a clean summary card.
 */
export default function ALResultsSummary({ formData }) {
	const { stream, subjects, district, zscore, interests } = formData;

	return (
		<div className='p-6 bg-white border-2 border-blue-100 shadow-lg rounded-3xl'>
			<div className='flex items-center justify-between'>
				<div className='flex flex-row items-center gap-2 mb-2'>
					<div className='flex items-center justify-center w-8 h-8 text-blue-600 bg-blue-100 rounded-lg aspect-square shrink-0'>
						<UserIcon className='w-4 h-4' />
					</div>
					<div className='flex flex-col '>
						<p className='pt-3 text-base font-bold tracking-widest text-blue-600 uppercase'>Your Profile Summary</p>
					</div>
				</div>

				<div>
					<button
						onClick={() => (window.location.href = "/")}
						className='inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-blue-700 transition-all border border-blue-200 rounded-xl bg-blue-50 hover:bg-blue-100 hover:shadow-md'>
						<RefreshIcon className='w-4 h-4' /> Search Again
					</button>
				</div>
			</div>
			<div className='flex flex-wrap gap-6'>
				{/* Stream */}
				{stream && (
					<div>
						<p className='mb-1.5 text-xs font-semibold tracking-wider uppercase text-slate-400'>Stream</p>
						<span className='inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-bold rounded-xl bg-blue-600 text-white shadow-sm'>
							{stream}
						</span>
					</div>
				)}

				{/* Subjects */}
				{subjects.length > 0 && (
					<div>
						<p className='mb-1.5 text-xs font-semibold tracking-wider uppercase text-slate-400'>Subjects</p>
						<div className='flex flex-wrap gap-1.5'>
							{subjects.map((s) => (
								<span
									key={s}
									className='inline-flex items-center px-2.5 py-1 text-xs font-semibold rounded-lg bg-indigo-50 text-indigo-800 border border-indigo-200'>
									{s}
								</span>
							))}
						</div>
					</div>
				)}

				{/* District */}
				{district && (
					<div>
						<p className='mb-1.5 text-xs font-semibold tracking-wider uppercase text-slate-400'>District</p>
						<span className='inline-flex items-center px-2.5 py-1 text-xs font-semibold rounded-lg bg-cyan-50 text-cyan-800 border border-cyan-200'>
							{district}
						</span>
					</div>
				)}

				{/* Z-Score */}
				{zscore && (
					<div>
						<p className='mb-1.5 text-xs font-semibold tracking-wider uppercase text-slate-400'>Z-Score</p>
						<span className='inline-flex items-center px-2.5 py-1 text-xs font-bold rounded-lg bg-blue-600 text-white'>
							{zscore}
						</span>
					</div>
				)}

				{/* Interests */}
				{interests && interests.trim().length > 0 && (
					<div className='w-full'>
						<p className='mb-1.5 text-xs font-semibold tracking-wider uppercase text-slate-400'>Career Interests</p>
						<p className='text-sm italic leading-relaxed text-slate-600'>
							"{interests.length > 160 ? `${interests.slice(0, 160)}…` : interests}"
						</p>
					</div>
				)}
			</div>
		</div>
	);
}
