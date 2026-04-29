import React from "react";

const InfoIcon = () => (
	<svg className='flex-shrink-0 w-5 h-5' fill='none' stroke='currentColor' strokeWidth='1.8' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z'
		/>
	</svg>
);

const ZScoreIcon = () => (
	<svg className='w-6 h-6' fill='none' stroke='currentColor' strokeWidth='1.5' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5m.75-9 3-3 2.148 2.148A12.061 12.061 0 0 1 16.5 7.605'
		/>
	</svg>
);

/**
 * ZScoreStep — Step 1 (optional)
 *
 * Props:
 *   zscore      – string value
 *   onChange    – (val: string) => void
 */
export default function ZScoreStep({ zscore, onChange }) {
	const isValid = zscore !== "" && Number(zscore) >= -3 && Number(zscore) <= 3;

	return (
		<div className='space-y-6'>
			{/* Header */}
			<div>
				<p className='mb-1 text-xs font-bold tracking-widest text-blue-600 uppercase'>Step 2 of 3 — Optional</p>
				<h2 className='mb-1 text-2xl font-extrabold tracking-tight text-slate-900'>What's Your Z-Score?</h2>
				<p className='text-sm text-slate-500'>
					Enter your A/L Z-score to see only courses you're eligible for. You can skip and view all courses.
				</p>
			</div>

			{/* Z-Score illustration card */}
			<div className='flex items-center gap-4 p-5 border-2 border-blue-100 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl'>
				<div className='flex items-center justify-center flex-shrink-0 w-12 h-12 text-blue-600 bg-blue-100 rounded-xl'>
					<ZScoreIcon />
				</div>
				<div>
					<p className='text-sm font-bold text-blue-900'>What is a Z-Score?</p>
					<p className='text-xs leading-relaxed text-blue-700 mt-0.5'>
						A standardised score (typically −3 to +3) used by the UGC to rank applicants for university admission.
					</p>
				</div>
			</div>

			{/* Input */}
			<div>
				<label className='block mb-2 text-sm font-bold text-slate-800'>
					Z-Score <span className='font-normal text-slate-400'>(optional)</span>
				</label>
				<input
					type='number'
					step='0.01'
					min='-3'
					max='3'
					placeholder='e.g. 1.85'
					value={zscore}
					onChange={(e) => onChange(e.target.value)}
					className={`
						w-full px-4 py-3 text-base border-2 rounded-xl transition-all duration-200 outline-none
						${
							isValid ? "border-blue-500 bg-blue-50/50 ring-2 ring-blue-100"
							: zscore !== "" ? "border-red-300 bg-red-50/40 ring-2 ring-red-100"
							: "border-slate-200 bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
						}
					`}
				/>
				{zscore !== "" && !isValid && (
					<p className='mt-1.5 text-xs text-red-600 font-medium'>Please enter a valid Z-score between −3 and +3.</p>
				)}
				{isValid && (
					<p className='mt-1.5 text-xs text-blue-600 font-medium'>
						Z-Score recorded — we'll filter courses you're eligible for.
					</p>
				)}
			</div>

			{/* Skip hint */}
			<div className='flex items-start gap-3 px-4 py-4 border border-slate-200 rounded-xl bg-slate-50'>
				<InfoIcon />
				<p className='text-sm text-slate-600'>
					<strong className='text-slate-800'>Don't have your Z-score yet?</strong> Hit{" "}
					<span className='font-semibold text-blue-600'>Skip Step</span> to explore all courses available in your stream
					— no Z-score required.
				</p>
			</div>
		</div>
	);
}
