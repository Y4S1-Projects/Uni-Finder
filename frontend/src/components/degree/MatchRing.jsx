import React from "react";

export default function MatchRing({ score = 0, size = 56 }) {
	const normalizedScore = Math.min(Math.max(parseFloat(score) || 0, 0), 100);
	const isHighMatch = normalizedScore >= 80;
	const isMediumMatch = normalizedScore >= 60;

	const radius = size / 2 - 4;
	const circumference = 2 * Math.PI * radius;
	const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

	const colorClass =
		isHighMatch ? "from-emerald-400 to-emerald-600"
		: isMediumMatch ? "from-blue-400 to-blue-600"
		: "from-gray-400 to-gray-600";

	return (
		<div className='flex flex-col items-center'>
			<div className='relative' style={{ width: `${size}px`, height: `${size}px` }}>
				{/* Background circle */}
				<svg className='absolute inset-0 transform -rotate-90' width={size} height={size}>
					<circle cx={size / 2} cy={size / 2} r={radius} stroke='#e5e7eb' strokeWidth='3' fill='none' />
					{/* Progress circle */}
					<circle
						cx={size / 2}
						cy={size / 2}
						r={radius}
						stroke='url(#gradientStroke)'
						strokeWidth='3'
						fill='none'
						strokeDasharray={circumference}
						strokeDashoffset={strokeDashoffset}
						strokeLinecap='round'
						className='transition-all duration-500 ease-out'
					/>
					<defs>
						<linearGradient id='gradientStroke' x1='0%' y1='0%' x2='100%' y2='100%'>
							<stop
								offset='0%'
								stopColor={
									isHighMatch ? "#10b981"
									: isMediumMatch ?
										"#3b82f6"
									:	"#9ca3af"
								}
							/>
							<stop
								offset='100%'
								stopColor={
									isHighMatch ? "#047857"
									: isMediumMatch ?
										"#1d4ed8"
									:	"#6b7280"
								}
							/>
						</linearGradient>
					</defs>
				</svg>

				{/* Center text */}
				<div className='absolute inset-0 flex items-center justify-center'>
					<div className='text-center'>
						<div className='text-xs font-semibold text-gray-600'>Match</div>
						<div className={`text-lg font-bold bg-gradient-to-r ${colorClass} bg-clip-text text-transparent`}>
							{normalizedScore.toFixed(0)}%
						</div>
					</div>
				</div>
			</div>

			{/* Status label */}
			<div className='mt-2 text-xs font-semibold text-gray-600'>
				{isHighMatch ?
					"Excellent"
				: isMediumMatch ?
					"Good"
				:	"Fair"}
			</div>
		</div>
	);
}
