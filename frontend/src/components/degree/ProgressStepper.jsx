import React from "react";
import { FaCheck } from "react-icons/fa";

export default function ProgressStepper({ steps = [], currentStep = 0 }) {
	return (
		<div className='mb-8'>
			<div className='flex items-center justify-between'>
				{steps.map((step, index) => (
					<React.Fragment key={index}>
						<div className='flex flex-col items-center flex-1'>
							{/* Step Circle */}
							<div
								className={`
									w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm
									transition-all duration-300 mb-2
									${
										index < currentStep ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg"
										: index === currentStep ?
											"bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg ring-4 ring-purple-200"
										:	"bg-gray-200 text-gray-600"
									}
								`}>
								{index < currentStep ?
									<FaCheck />
								:	index + 1}
							</div>

							{/* Step Label */}
							<p
								className={`
									text-xs font-semibold text-center
									${index <= currentStep ? "text-gray-900" : "text-gray-500"}
								`}>
								{step}
							</p>
						</div>

						{/* Divider Line */}
						{index < steps.length - 1 && (
							<div className='flex-1 h-1 mx-2 mb-8 rounded-full' style={{ marginBottom: "32px" }}>
								<div
									className={`h-full rounded-full transition-all duration-300 ${
										index < currentStep ? "bg-gradient-to-r from-purple-500 to-blue-500" : "bg-gray-200"
									}`}></div>
							</div>
						)}
					</React.Fragment>
				))}
			</div>

			{/* Progress bar below */}
			<div className='w-full h-1 bg-gray-200 rounded-full overflow-hidden mt-4'>
				<div
					className='h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-300'
					style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}></div>
			</div>
		</div>
	);
}
