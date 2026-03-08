import React, { useState, useEffect } from "react";

const loadingMessages = [
	"Analyzing UGC Cutoff Rules...",
	"Calculating Semantic Interest Match...",
	"Generating AI Explanations...",
	"Compiling Your Perfect Degrees...",
];

export default function LoadingState() {
	const [messageIndex, setMessageIndex] = useState(0);

	useEffect(() => {
		const interval = setInterval(() => {
			setMessageIndex((prev) => (prev + 1) % loadingMessages.length);
		}, 1500);
		return () => clearInterval(interval);
	}, []);

	return (
		<div className='flex flex-col items-center justify-center min-h-96'>
			{/* Animated Gradient Skeleton */}
			<div className='relative w-16 h-16 mb-6'>
				<div className='absolute inset-0 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 rounded-full opacity-75 blur-xl animate-pulse'></div>
				<div className='absolute inset-2 bg-white rounded-full flex items-center justify-center'>
					<div className='w-3 h-3 bg-purple-600 rounded-full animate-bounce' style={{ animationDelay: "0s" }}></div>
					<div
						className='w-3 h-3 bg-blue-600 rounded-full animate-bounce ml-2'
						style={{ animationDelay: "0.2s" }}></div>
					<div
						className='w-3 h-3 bg-purple-600 rounded-full animate-bounce ml-2'
						style={{ animationDelay: "0.4s" }}></div>
				</div>
			</div>

			{/* Dynamic Message */}
			<div className='h-12 flex items-center justify-center'>
				<p className='text-lg font-semibold text-gray-700 text-center transition-opacity duration-500'>
					{loadingMessages[messageIndex]}
				</p>
			</div>

			{/* Progress Indicator */}
			<div className='mt-6 w-48 h-1 bg-gray-200 rounded-full overflow-hidden'>
				<div className='h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse'></div>
			</div>
		</div>
	);
}
