import React, { useState, useEffect } from "react";

// ── Processing stages shown sequentially ──────────────────────────────────────
const STAGES = [
	{ label: "Reading your stream & subjects", icon: BookIcon },
	{ label: "Applying UGC eligibility rules", icon: FilterIcon },
	{ label: "Matching your Z-score cutoffs", icon: ChartIcon },
	{ label: "Running AI interest analysis", icon: SparkleIcon },
	{ label: "Ranking your best-fit degrees", icon: StarIcon },
];

// ── Inline SVG icons ──────────────────────────────────────────────────────────
function BookIcon() {
	return (
		<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
			<path
				strokeLinecap='round'
				strokeLinejoin='round'
				d='M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25'
			/>
		</svg>
	);
}
function FilterIcon() {
	return (
		<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
			<path
				strokeLinecap='round'
				strokeLinejoin='round'
				d='M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z'
			/>
		</svg>
	);
}
function ChartIcon() {
	return (
		<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
			<path
				strokeLinecap='round'
				strokeLinejoin='round'
				d='M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z'
			/>
		</svg>
	);
}
function SparkleIcon() {
	return (
		<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
			<path
				strokeLinecap='round'
				strokeLinejoin='round'
				d='M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z'
			/>
		</svg>
	);
}
function StarIcon() {
	return (
		<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
			<path
				strokeLinecap='round'
				strokeLinejoin='round'
				d='M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.499Z'
			/>
		</svg>
	);
}

// ── Main component ────────────────────────────────────────────────────────────
export default function LoadingState() {
	const [stageIndex, setStageIndex] = useState(0);
	const [progress, setProgress] = useState(8);
	const [dots, setDots] = useState(1);

	// Advance stage every 1.4 s
	useEffect(() => {
		const id = setInterval(() => {
			setStageIndex((prev) => {
				const next = prev + 1;
				if (next >= STAGES.length) {
					clearInterval(id);
					return prev;
				}
				return next;
			});
		}, 1400);
		return () => clearInterval(id);
	}, []);

	// Smooth progress bar that fills over ~7 s
	useEffect(() => {
		const id = setInterval(() => {
			setProgress((p) => {
				if (p >= 95) return 95; // hold near end until real result arrives
				return p + 1.2;
			});
		}, 100);
		return () => clearInterval(id);
	}, []);

	// Animated ellipsis
	useEffect(() => {
		const id = setInterval(() => setDots((d) => (d % 3) + 1), 500);
		return () => clearInterval(id);
	}, []);

	return (
		<div className='flex flex-col items-center justify-center py-4 select-none min-h-80'>
			{/* ── Orbital spinner ── */}
			<div className='relative w-20 h-20 mb-8'>
				{/* Outer spinning ring */}
				<div className='absolute inset-0 border-4 border-blue-100 rounded-full' />
				<div
					className='absolute inset-0 border-4 border-transparent rounded-full border-t-blue-500 border-r-indigo-500 animate-spin'
					style={{ animationDuration: "1s" }}
				/>
				{/* Inner pulsing core */}
				<div className='absolute flex items-center justify-center text-white rounded-full shadow-lg inset-3 bg-gradient-to-br from-blue-500 to-indigo-600 animate-pulse'>
					<SparkleIcon />
				</div>
			</div>

			{/* ── Heading ── */}
			<h3 className='mb-1 text-lg font-extrabold tracking-tight text-slate-800'>
				Finding Your Degrees{".".repeat(dots)}
			</h3>
			<p className='mb-8 text-sm text-slate-400'>Our AI is analyzing your profile</p>

			{/* ── Stage checklist ── */}
			<div className='w-full max-w-sm space-y-2.5 mb-8'>
				{STAGES.map((s, i) => {
					const done = i < stageIndex;
					const active = i === stageIndex;
					return (
						<div
							key={i}
							className={`flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all duration-500 ${
								done ? "bg-blue-50 border-blue-200 opacity-70"
								: active ? "bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300 shadow-sm scale-[1.02]"
								: "bg-white border-slate-100 opacity-40"
							}`}>
							{/* Status indicator */}
							<div
								className={`flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-full text-xs transition-all duration-300 ${
									done ? "bg-blue-600 text-white"
									: active ? "bg-gradient-to-br from-blue-500 to-indigo-600 text-white animate-pulse"
									: "bg-slate-100 text-slate-400"
								}`}>
								{done ?
									<svg className='w-3.5 h-3.5' fill='none' stroke='currentColor' strokeWidth='3' viewBox='0 0 24 24'>
										<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
									</svg>
								:	<s.icon />}
							</div>

							<span
								className={`text-xs font-semibold leading-tight ${
									done ? "text-blue-700"
									: active ? "text-blue-900"
									: "text-slate-400"
								}`}>
								{s.label}
							</span>

							{/* Active spinner */}
							{active && (
								<svg
									className='flex-shrink-0 ml-auto w-3.5 h-3.5 text-blue-500 animate-spin'
									fill='none'
									viewBox='0 0 24 24'>
									<circle className='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' strokeWidth='4' />
									<path className='opacity-75' fill='currentColor' d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z' />
								</svg>
							)}
						</div>
					);
				})}
			</div>

			{/* ── Progress bar ── */}
			<div className='w-full max-w-sm'>
				<div className='flex justify-between mb-1.5 text-xs font-semibold text-slate-400'>
					<span>Processing</span>
					<span className='tabular-nums'>{Math.round(progress)}%</span>
				</div>
				<div className='w-full h-2 overflow-hidden rounded-full bg-slate-100'>
					<div
						className='h-full transition-all duration-200 ease-out rounded-full shadow-sm bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400'
						style={{ width: `${progress}%` }}
					/>
				</div>
				<p className='mt-2 text-xs text-center text-slate-400'>This usually takes 5–15 seconds</p>
			</div>
		</div>
	);
}
