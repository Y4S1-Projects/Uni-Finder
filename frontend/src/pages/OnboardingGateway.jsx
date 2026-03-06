import React from "react";
import { useNavigate } from "react-router-dom";
import { FaCompass, FaGraduationCap, FaArrowRight, FaMagic } from "react-icons/fa";

export default function OnboardingGateway() {
	const navigate = useNavigate();

	return (
		<div className='flex items-center justify-center min-h-screen px-4 py-12 bg-gradient-to-br from-slate-50 via-purple-50 to-blue-50'>
			{/* Animated background elements */}
			<div className='absolute top-0 left-0 bg-purple-300 rounded-full w-96 h-96 mix-blend-multiply filter blur-3xl opacity-20 animate-blob'></div>
			<div
				className='absolute top-0 right-0 bg-blue-300 rounded-full w-96 h-96 mix-blend-multiply filter blur-3xl opacity-20 animate-blob'
				style={{ animationDelay: "2s" }}></div>
			<div
				className='absolute bg-pink-300 rounded-full -bottom-8 left-20 w-96 h-96 mix-blend-multiply filter blur-3xl opacity-20 animate-blob'
				style={{ animationDelay: "4s" }}></div>

			{/* Main container */}
			<div className='relative z-10 w-full max-w-5xl'>
				{/* Header section */}
				<div className='mb-16 text-center'>
					<div className='inline-flex items-center justify-center gap-2 px-4 py-2 mb-6 bg-white border border-purple-200 rounded-full shadow-sm'>
						<FaMagic className='text-purple-600' />
						<span className='text-sm font-semibold text-purple-700'>AI-Powered Degree Discovery</span>
					</div>

					<h1 className='mb-6 text-5xl font-black leading-tight text-transparent md:text-6xl bg-gradient-to-r from-purple-900 via-blue-800 to-purple-900 bg-clip-text'>
						Discover Your Perfect University Path
					</h1>

					<p className='max-w-2xl mx-auto text-xl leading-relaxed text-gray-700'>
						Tell us where you are in your academic journey, and our intelligent system will map out exactly where you
						can go. Every degree recommendation is personalized based on your stream, grades, interests, and career
						goals.
					</p>
				</div>

				{/* Two pathway cards */}
				<div className='grid grid-cols-1 gap-8 md:grid-cols-2 md:gap-6'>
					{/* O/L Students Card */}
					<button
						onClick={() => navigate("/degree-recommendations/all-students")}
						className='relative p-8 text-left transition-all duration-300 transform bg-white border-2 shadow-lg group rounded-3xl hover:shadow-2xl hover:scale-105 hover:-translate-y-1 border-emerald-200 hover:border-emerald-400'>
						{/* Gradient overlay on hover */}
						<div className='absolute inset-0 transition-opacity duration-300 opacity-0 rounded-3xl bg-gradient-to-br from-emerald-50 to-teal-50 group-hover:opacity-100'></div>

						<div className='relative z-10'>
							{/* Icon */}
							<div className='flex items-center justify-center w-16 h-16 mb-6 transition-transform duration-300 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl group-hover:scale-110'>
								<FaCompass className='text-2xl text-white' />
							</div>

							{/* Content */}
							<div className='mb-6'>
								<div className='inline-block px-3 py-1 mb-4 text-xs font-bold rounded-full bg-emerald-100 text-emerald-700'>
									O/L Students
								</div>

								<h2 className='mb-3 text-3xl font-bold text-gray-900'>Explore Career Paths</h2>

								<p className='text-base leading-relaxed text-gray-700'>
									Planning your A/L stream? Tell us about your interests and strengths. We'll suggest degrees and career
									paths that align with your passion.
								</p>
							</div>

							{/* Features */}
							<div className='mb-6 space-y-3'>
								<div className='flex items-start gap-3'>
									<span className='text-emerald-600 font-bold text-lg mt-0.5'>✓</span>
									<span className='text-sm text-gray-700'>Interest-based recommendations</span>
								</div>
								<div className='flex items-start gap-3'>
									<span className='text-emerald-600 font-bold text-lg mt-0.5'>✓</span>
									<span className='text-sm text-gray-700'>AI-powered career insights</span>
								</div>
								<div className='flex items-start gap-3'>
									<span className='text-emerald-600 font-bold text-lg mt-0.5'>✓</span>
									<span className='text-sm text-gray-700'>Stream recommendations</span>
								</div>
							</div>

							{/* Button */}
							<div className='flex items-center gap-2 font-bold transition-all text-emerald-600 group-hover:gap-3'>
								<span>Start Exploring</span>
								<FaArrowRight className='text-sm' />
							</div>
						</div>
					</button>

					{/* A/L Students Card */}
					<button
						onClick={() => navigate("/degree-recommendations/al-students")}
						className='relative p-8 text-left transition-all duration-300 transform bg-white border-2 border-blue-200 shadow-lg group rounded-3xl hover:shadow-2xl hover:scale-105 hover:-translate-y-1 hover:border-blue-400'>
						{/* Gradient overlay on hover */}
						<div className='absolute inset-0 transition-opacity duration-300 opacity-0 rounded-3xl bg-gradient-to-br from-blue-50 to-indigo-50 group-hover:opacity-100'></div>

						<div className='relative z-10'>
							{/* Icon */}
							<div className='flex items-center justify-center w-16 h-16 mb-6 transition-transform duration-300 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-2xl group-hover:scale-110'>
								<FaGraduationCap className='text-2xl text-white' />
							</div>

							{/* Content */}
							<div className='mb-6'>
								<div className='inline-block px-3 py-1 mb-4 text-xs font-bold text-blue-700 bg-blue-100 rounded-full'>
									A/L Students
								</div>

								<h2 className='mb-3 text-3xl font-bold text-gray-900'>Check Degree Eligibility</h2>

								<p className='text-base leading-relaxed text-gray-700'>
									Just provide your details step-by-step! Our AI automatically detects the best matching approach based
									on what you share - stream, Z-score, and interests.
								</p>
							</div>

							{/* Features */}
							<div className='mb-6 space-y-3'>
								<div className='flex items-start gap-3'>
									<span className='text-blue-600 font-bold text-lg mt-0.5'>✓</span>
									<span className='text-sm text-gray-700'>Smart scenario detection</span>
								</div>
								<div className='flex items-start gap-3'>
									<span className='text-blue-600 font-bold text-lg mt-0.5'>✓</span>
									<span className='text-sm text-gray-700'>Skip optional fields anytime</span>
								</div>
								<div className='flex items-start gap-3'>
									<span className='text-blue-600 font-bold text-lg mt-0.5'>✓</span>
									<span className='text-sm text-gray-700'>AI-powered interest matching</span>
								</div>
							</div>

							{/* Button */}
							<div className='flex items-center gap-2 font-bold text-blue-600 transition-all group-hover:gap-3'>
								<span>Check Eligibility</span>
								<FaArrowRight className='text-sm' />
							</div>
						</div>
					</button>
				</div>

				{/* Footer info */}
				<div className='mt-16 text-center'>
					<div className='inline-flex items-center justify-center gap-2 px-6 py-4 bg-white border border-gray-200 shadow-sm rounded-2xl'>
						<FaMagic className='text-lg text-purple-600' />
						<p className='text-sm text-gray-700'>
							<span className='font-bold text-gray-900'>Powered by AI:</span> Our system analyzes UGC cutoffs, semantic
							similarity, and career pathways to give you personalized recommendations.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
