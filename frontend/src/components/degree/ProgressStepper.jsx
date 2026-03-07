import React from "react";
import { FaCheck } from "react-icons/fa";

export default function ProgressStepper({ steps = [], currentStep = 0 }) {
	return (
		<div className=''>
			<div className='flex items-center justify-between'>
				{steps.map((step, index) => (
					<React.Fragment key={index}>
						<div className='relative flex flex-col items-center flex-1'>
							{/* Step Circle */}
							<div
								className={`
									w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
									transition-all duration-300 ease-out mb-2 relative z-10
									${
										index < currentStep ?
											"bg-gradient-to-br from-green-400 to-emerald-500 text-white shadow-lg scale-100 border-2 border-green-200"
										: index === currentStep ?
											"bg-gradient-to-br from-green-400 to-emerald-500 text-white shadow-xl scale-105 border-2 border-green-200 ring-2 ring-green-200/70"
										:	"bg-white border-2 border-gray-300 text-gray-500 shadow-sm scale-95"
									}
								`}>
								{index < currentStep ?
									<FaCheck className='text-sm' />
								:	index + 1}
							</div>

							{/* Step Label */}
							<p
								className={`
									text-[11px] leading-tight font-semibold text-center transition-all duration-300 px-1 max-w-[96px]
									${
										index === currentStep ? "text-white drop-shadow scale-105"
										: index < currentStep ? "text-white/90"
										: "text-white/60"
									}
								`}>
								{step}
							</p>
						</div>

						{/* Divider Line */}
						{index < steps.length - 1 && (
							<div className='relative flex-1 h-1 mx-2 mb-7'>
								{/* Background line */}
								<div className='absolute inset-0 rounded-full bg-white/30'></div>
								{/* Progress line with animation */}
								<div
									className={`absolute inset-0 rounded-full transition-all duration-700 ease-out ${
										index < currentStep ?
											"bg-gradient-to-r from-green-400 to-emerald-500 shadow-md scale-x-100"
										:	"bg-white/20 scale-x-0"
									}`}
									style={{ transformOrigin: "left" }}></div>
							</div>
						)}
					</React.Fragment>
				))}
			</div>
		</div>
	);
}
