import React from "react";

const UserIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z'
		/>
	</svg>
);

const Badge = ({ label, value, colorClass }) =>
	value ?
		<span
			className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg border ${colorClass}`}>
			{label}: <span className='font-extrabold'>{value}</span>
		</span>
	:	null;

/**
 * ALResultsSummary — shown at top of Step 3 results.
 * Displays the user's inputs as a clean summary card.
 */
export default function ALResultsSummary({ formData }) {
	const { stream, subjects, district, zscore, interests } = formData;

	return (
		<div className='p-6 mb-8 bg-white border-2 border-blue-100 shadow-lg rounded-3xl'>
			<div className='flex items-center gap-2 mb-4'>
				<div className='p-1.5 rounded-lg bg-blue-100 text-blue-600'>
					<UserIcon />
				</div>
				<p className='text-xs font-bold tracking-widest text-blue-600 uppercase'>Your Profile Summary</p>
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
