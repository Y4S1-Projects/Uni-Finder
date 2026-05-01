import React, { useState, useEffect } from "react";
import { BookIcon, FilterIcon, ChartBarIcon, SparkleIcon, StarIcon } from "../ui/DegreeIcons";

// ── Processing stages shown sequentially ──────────────────────────────────────
const DEFAULT_STAGES = [
	{ label: "Reading your stream & subjects", Icon: BookIcon },
	{ label: "Applying UGC eligibility rules", Icon: FilterIcon },
	{ label: "Matching your Z-score cutoffs", Icon: ChartBarIcon },
	{ label: "Running AI interest analysis", Icon: SparkleIcon },
	{ label: "Ranking your best-fit degrees", Icon: StarIcon },
];

export const OL_STAGES = [
	{ label: "Analyzing your O/L marks", Icon: BookIcon },
	{ label: "Mapping to A/L streams", Icon: FilterIcon },
	{ label: "Running AI interest analysis", Icon: SparkleIcon },
	{ label: "Finding potential degrees", Icon: StarIcon },
	{ label: "Generating best pathways", Icon: ChartBarIcon },
];

// ── Main component ────────────────────────────────────────────────────────────
export default function LoadingState({ theme = "blue", stages = DEFAULT_STAGES, title = "Finding Your Degrees" }) {
	const [stageIndex, setStageIndex] = useState(0);
	const [progress, setProgress] = useState(8);
	const [dots, setDots] = useState(1);

	// Advance stage every 1.4 s
	useEffect(() => {
		const id = setInterval(() => {
			setStageIndex((prev) => {
				const next = prev + 1;
				if (next >= stages.length) {
					clearInterval(id);
					return prev;
				}
				return next;
			});
		}, 1400);
		return () => clearInterval(id);
	}, [stages.length]);

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

	const isEmerald = theme === "emerald";

	return (
		<div className='flex flex-col items-center justify-center py-4 select-none min-h-80'>
			{/* ── Orbital spinner ── */}
			<div className='relative w-20 h-20 mb-8'>
				{/* Outer spinning ring */}
				<div
					className={`absolute inset-0 border-4 rounded-full ${isEmerald ? "border-emerald-100" : "border-blue-100"}`}
				/>
				<div
					className={`absolute inset-0 border-4 border-transparent rounded-full animate-spin ${isEmerald ? "border-t-emerald-500 border-r-teal-500" : "border-t-blue-500 border-r-indigo-500"}`}
					style={{ animationDuration: "1s" }}
				/>
				{/* Inner pulsing core */}
				<div
					className={`absolute flex items-center justify-center text-white rounded-full shadow-lg inset-3 animate-pulse ${isEmerald ? "bg-gradient-to-br from-emerald-500 to-teal-600" : "bg-gradient-to-br from-blue-500 to-indigo-600"}`}>
					<SparkleIcon className='w-4 h-4' />
				</div>
			</div>

			{/* ── Heading ── */}
			<h3 className='mb-1 text-lg font-extrabold tracking-tight text-slate-800'>
				{title}
				{".".repeat(dots)}
			</h3>
			<p className='mb-8 text-sm text-slate-400'>Our AI is analyzing your profile</p>

			{/* ── Stage checklist ── */}
			<div className='w-full max-w-sm space-y-2.5 mb-8'>
				{stages.map((s, i) => {
					const done = i < stageIndex;
					const active = i === stageIndex;

					let bgClass = "bg-white border-slate-100 opacity-40";
					let indicatorClass = "bg-slate-100 text-slate-400";
					let textClass = "text-slate-400";

					if (done) {
						bgClass =
							isEmerald ? "bg-emerald-50 border-emerald-200 opacity-70" : "bg-blue-50 border-blue-200 opacity-70";
						indicatorClass = isEmerald ? "bg-emerald-600 text-white" : "bg-blue-600 text-white";
						textClass = isEmerald ? "text-emerald-700" : "text-blue-700";
					} else if (active) {
						bgClass =
							isEmerald ?
								"bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-300 shadow-sm scale-[1.02]"
							:	"bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300 shadow-sm scale-[1.02]";
						indicatorClass =
							isEmerald ?
								"bg-gradient-to-br from-emerald-500 to-teal-600 text-white animate-pulse"
							:	"bg-gradient-to-br from-blue-500 to-indigo-600 text-white animate-pulse";
						textClass = isEmerald ? "text-emerald-900" : "text-blue-900";
					}

					return (
						<div
							key={i}
							className={`flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all duration-500 ${bgClass}`}>
							{/* Status indicator */}
							<div
								className={`flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-full text-xs transition-all duration-300 ${indicatorClass}`}>
								{done ?
									<svg className='w-3.5 h-3.5' fill='none' stroke='currentColor' strokeWidth='3' viewBox='0 0 24 24'>
										<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
									</svg>
								:	<s.Icon className='w-4 h-4' />}
							</div>

							<span className={`text-xs font-semibold leading-tight ${textClass}`}>{s.label}</span>

							{/* Active spinner */}
							{active && (
								<svg
									className={`flex-shrink-0 ml-auto w-3.5 h-3.5 animate-spin ${isEmerald ? "text-emerald-500" : "text-blue-500"}`}
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
						className={`h-full transition-all duration-200 ease-out rounded-full shadow-sm ${isEmerald ? "bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400" : "bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400"}`}
						style={{ width: `${progress}%` }}
					/>
				</div>
				<p className='mt-2 text-xs text-center text-slate-400'>This usually takes 5–15 seconds</p>
			</div>
		</div>
	);
}
