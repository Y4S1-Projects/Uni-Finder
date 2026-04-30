import React from "react";
import { SparkleIcon, InfoIcon } from "../../ui/DegreeIcons";

export default function InterestsStep({ interests, onChange }) {
	const charCount = interests.length;
	const isValid = charCount >= 10;
	return (
		<div className='space-y-6'>
			<div>
				<p className='mb-1 text-xs font-bold tracking-widest text-blue-600 uppercase'>Step 3 of 3 — Optional</p>
				<h2 className='mb-1 text-2xl font-extrabold tracking-tight text-slate-900'>What Are Your Career Goals?</h2>
				<p className='text-sm text-slate-500'>
					Tell us your interests and our AI will personalize degree recommendations specifically for you.
				</p>
			</div>
			<div className='flex items-center px-4 py-2 border-2 border-blue-100 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl'>
				<div className='flex items-center w-full gap-4 mt-1 -mb-2'>
					<div className='flex items-center justify-center flex-shrink-0 w-12 h-12 text-blue-600 bg-blue-100 rounded-xl'>
						<SparkleIcon className='w-5 h-5' />
					</div>
					<div className='flex flex-col flex-1'>
						<p className='text-sm font-bold text-blue-900'>AI-Powered Personalization</p>
						<p className='-mt-2 text-xs leading-relaxed text-blue-700'>
							Our AI analyses your goals and ranks degrees with the highest career match scores.
						</p>
					</div>
				</div>
			</div>
			<div>
				<label className='block mb-2 text-sm font-bold text-slate-800'>
					Career Goals &amp; Interests <span className='font-normal text-slate-400'>(optional)</span>
				</label>
				<textarea
					rows={3}
					placeholder="e.g. I love problem-solving and technology. I'd like to work in software engineering, AI or data science..."
					value={interests}
					onChange={(e) => onChange(e.target.value)}
					className={`w-full px-4 py-3 text-sm border-2 rounded-xl resize-none transition-all duration-200 outline-none leading-relaxed ${isValid ? "border-blue-400 ring-2 ring-blue-100 bg-blue-50/30" : "border-slate-200 bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100"}`}
				/>
				<div className='flex items-center justify-between mt-1.5'>
					<p className={`text-xs font-medium ${isValid ? "text-blue-600" : "text-slate-400"}`}>
						{isValid ? "AI personalization enabled" : `${10 - charCount} more characters needed`}
					</p>
					<p className={`text-xs font-semibold tabular-nums ${isValid ? "text-blue-600" : "text-slate-400"}`}>
						{charCount} chars
					</p>
				</div>
			</div>
			<div className='flex items-start gap-3 px-4 py-4 border border-slate-200 rounded-xl bg-slate-50'>
				<InfoIcon className='flex-shrink-0 w-5 h-5' />
				<p className='text-sm text-slate-600'>
					<strong className='text-slate-800'>Prefer to skip?</strong> Hit{" "}
					<span className='font-semibold text-blue-600'>Find My Degrees</span> to get all eligible courses without
					personalization.
				</p>
			</div>
		</div>
	);
}
