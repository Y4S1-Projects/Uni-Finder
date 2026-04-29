import React from "react";

const SparkleIcon = () => (
	<svg className='flex-shrink-0 w-5 h-5' fill='none' stroke='currentColor' strokeWidth='1.8' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z'
		/>
	</svg>
);
const InfoIcon = () => (
	<svg className='flex-shrink-0 w-5 h-5' fill='none' stroke='currentColor' strokeWidth='1.8' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z'
		/>
	</svg>
);

export default function InterestsStep({ interests, onChange }) {
	const charCount = interests.length;
	const isValid = charCount >= 10;
	return (
		<div className='space-y-6'>
			<div>
				<p className='mb-1 text-xs font-bold tracking-widest text-blue-600 uppercase'>Step 3 of 3 — Optional</p>
				<h2 className='mb-1 text-2xl font-extrabold tracking-tight text-slate-900'>What Are Your Career Goals?</h2>
				<p className='text-sm text-slate-500'>
					Tell us your interests and our AI will personalise degree recommendations specifically for you.
				</p>
			</div>
			<div className='flex items-center gap-4 p-5 border-2 border-blue-100 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl'>
				<div className='flex items-center justify-center flex-shrink-0 w-12 h-12 text-blue-600 bg-blue-100 rounded-xl'>
					<SparkleIcon />
				</div>
				<div>
					<p className='text-sm font-bold text-blue-900'>AI-Powered Personalisation</p>
					<p className='text-xs leading-relaxed text-blue-700 mt-0.5'>
						Our AI analyses your goals and ranks degrees with the highest career match scores.
					</p>
				</div>
			</div>
			<div>
				<label className='block mb-2 text-sm font-bold text-slate-800'>
					Career Goals &amp; Interests <span className='font-normal text-slate-400'>(optional)</span>
				</label>
				<textarea
					rows={6}
					placeholder="e.g. I love problem-solving and technology. I'd like to work in software engineering, AI or data science..."
					value={interests}
					onChange={(e) => onChange(e.target.value)}
					className={`w-full px-4 py-3 text-sm border-2 rounded-xl resize-none transition-all duration-200 outline-none leading-relaxed ${isValid ? "border-blue-400 ring-2 ring-blue-100 bg-blue-50/30" : "border-slate-200 bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100"}`}
				/>
				<div className='flex items-center justify-between mt-1.5'>
					<p className={`text-xs font-medium ${isValid ? "text-blue-600" : "text-slate-400"}`}>
						{isValid ? "AI personalisation enabled" : `${10 - charCount} more characters needed`}
					</p>
					<p className={`text-xs font-semibold tabular-nums ${isValid ? "text-blue-600" : "text-slate-400"}`}>
						{charCount} chars
					</p>
				</div>
			</div>
			<div className='flex items-start gap-3 px-4 py-4 border border-slate-200 rounded-xl bg-slate-50'>
				<InfoIcon />
				<p className='text-sm text-slate-600'>
					<strong className='text-slate-800'>Prefer to skip?</strong> Hit{" "}
					<span className='font-semibold text-blue-600'>Find My Degrees</span> to get all eligible courses without
					personalisation.
				</p>
			</div>
		</div>
	);
}
