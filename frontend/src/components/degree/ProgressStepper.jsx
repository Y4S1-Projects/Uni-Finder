import React from "react";

const CheckIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2.5' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
	</svg>
);

/**
 * ProgressStepper
 * @param {string[]} steps
 * @param {number}   currentStep
 * @param {"emerald"|"blue"} theme  — default "emerald" (OL path), "blue" for AL path
 */
export default function ProgressStepper({ steps = [], currentStep = 0, theme = "emerald" }) {
	const active =
		theme === "blue" ?
			"bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-xl scale-105 border-2 border-blue-300 ring-2 ring-blue-300/60"
		:	"bg-gradient-to-br from-emerald-400 to-teal-500 text-white shadow-xl scale-105 border-2 border-emerald-200 ring-2 ring-emerald-200/70";

	const done =
		theme === "blue" ?
			"bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg scale-100 border-2 border-blue-300"
		:	"bg-gradient-to-br from-emerald-400 to-teal-500 text-white shadow-lg scale-100 border-2 border-emerald-200";

	const progressLine =
		theme === "blue" ?
			"bg-gradient-to-r from-blue-400 to-indigo-500 shadow-md"
		:	"bg-gradient-to-r from-emerald-400 to-teal-500 shadow-md";

	return (
		<div>
			<div className='flex items-center justify-between'>
				{steps.map((step, index) => (
					<React.Fragment key={index}>
						<div className='relative flex flex-col items-center flex-1'>
							{/* Step circle */}
							<div
								className={`
									w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
									transition-all duration-300 ease-out mb-2 relative z-10
									${
										index < currentStep ? done
										: index === currentStep ? active
										: "bg-white border-2 border-gray-300 text-gray-500 shadow-sm scale-95"
									}
								`}>
								{index < currentStep ?
									<CheckIcon />
								:	index + 1}
							</div>

							{/* Step label */}
							<p
								className={`
									text-[11px] leading-tight font-semibold text-center transition-all duration-300 px-1 max-w-[96px]
									${
										index === currentStep ? "text-white drop-shadow scale-105"
										: index < currentStep ? "text-white/90"
										: "text-white/55"
									}
								`}>
								{step}
							</p>
						</div>

						{/* Connector line */}
						{index < steps.length - 1 && (
							<div className='relative flex-1 h-1 mx-2 mb-7'>
								<div className='absolute inset-0 rounded-full bg-white/25' />
								<div
									className={`absolute inset-0 rounded-full transition-all duration-700 ease-out ${
										index < currentStep ? `${progressLine} scale-x-100` : "bg-white/15 scale-x-0"
									}`}
									style={{ transformOrigin: "left" }}
								/>
							</div>
						)}
					</React.Fragment>
				))}
			</div>
		</div>
	);
}
