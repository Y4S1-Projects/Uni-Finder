import { useNavigate } from "react-router-dom";

const ArrowIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3' />
	</svg>
);

const CompassIcon = () => (
	<svg className='w-6 h-6' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M15.042 21.672 13.684 16.6m0 0-2.51 2.225.569-9.47 5.227 7.917-3.286-.672ZM12 2.25V4.5m5.834.166-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243-1.59-1.59'
		/>
	</svg>
);

const CapIcon = () => (
	<svg className='w-6 h-6' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5'
		/>
	</svg>
);

const SparklesIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09l2.846.813-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z'
		/>
	</svg>
);

const CheckIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2.5' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
	</svg>
);

export default function OnboardingGateway() {
	const navigate = useNavigate();

	return (
		<div className='flex items-center justify-center min-h-screen px-4 pt-24 pb-12 overflow-hidden bg-gradient-to-br from-indigo-50/60 via-white to-purple-50/60'>
			{/* Ambient light orbs */}
			<div className='absolute top-[-10%] right-[-5%] w-[600px] h-[600px] bg-violet-400/10 rounded-full blur-[140px] pointer-events-none' />
			<div className='absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-blue-300/10 rounded-full blur-[120px] pointer-events-none' />
			<div className='absolute top-[40%] right-[30%] w-[250px] h-[250px] bg-pink-300/10 rounded-full blur-[100px] pointer-events-none' />

			{/* Main container */}
			<div className='relative z-10 w-full max-w-5xl mx-auto'>
				{/* Header section */}
				<div className='mb-16 text-center animate-slideUp'>
					<div className='inline-flex items-center gap-2 px-4 py-1.5 mb-6 text-sm font-semibold border rounded-full shadow-sm bg-white border-indigo-100 text-indigo-700'>
						<SparklesIcon />
						<span>AI-Powered Degree Discovery</span>
					</div>

					<h1 className='mb-5 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl'>
						Discover Your Perfect
						<br />
						<span className='text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600'>
							University Path
						</span>
					</h1>

					<p className='max-w-2xl mx-auto text-lg leading-relaxed text-slate-500'>
						Tell us where you are in your academic journey, and our intelligent system will map out exactly where you
						can go based on your stream, grades, and career goals.
					</p>
				</div>

				{/* Two pathway cards */}
				<div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
					{/* O/L Students Card */}
					<button
						type='button'
						onClick={() => navigate("/degree-recommendations/all-students")}
						className='relative flex flex-col p-8 text-left transition-all duration-300 border shadow-lg bg-emerald-50 group rounded-3xl hover:shadow-xl hover:-translate-y-1 border-slate-200/80 hover:border-emerald-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/40'>
						<div className='absolute inset-0 transition-opacity duration-300 opacity-0 rounded-3xl bg-gradient-to-br from-emerald-50/50 to-teal-50/50 group-hover:opacity-100' />

						<div className='relative z-10 flex flex-col h-full'>
							{/* Header area */}
							<div className='flex items-start justify-between mb-8'>
								<div className='flex items-center justify-center transition-transform duration-300 shadow-md w-14 h-14 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl group-hover:scale-110 shadow-emerald-500/20'>
									<CompassIcon className='text-white' />
								</div>
								<div className='px-3 py-1 text-xs font-bold border rounded-full bg-emerald-50 text-emerald-700 border-emerald-100'>
									O/L Students
								</div>
							</div>

							{/* Content */}
							<div className='flex-1 mb-8'>
								<h2 className='mb-3 text-2xl font-bold transition-colors text-slate-900 group-hover:text-emerald-900'>
									Explore Career Paths
								</h2>
								<p className='text-sm leading-relaxed text-slate-500'>
									Planning your A/L stream? Tell us about your interests and strengths. We'll suggest degrees and career
									paths that align with your passion.
								</p>
							</div>

							{/* Features */}
							<div className='mb-8 space-y-3'>
								{["Interest-based recommendations", "AI-powered career insights", "Stream recommendations"].map(
									(feature, idx) => (
										<div key={idx} className='flex items-start gap-3'>
											<CheckIcon className='w-5 h-5 mt-0.5 text-emerald-500' />
											<span className='text-sm font-medium text-slate-600'>{feature}</span>
										</div>
									),
								)}
							</div>

							{/* Action */}
							<div className='inline-flex items-center gap-2 mt-auto text-sm font-bold transition-all text-emerald-600 group-hover:gap-3'>
								<span>Start Exploring</span>
								<ArrowIcon />
							</div>
						</div>
					</button>

					{/* A/L Students Card */}
					<button
						type='button'
						onClick={() => navigate("/degree-recommendations/al-students")}
						className='relative flex flex-col p-8 text-left transition-all duration-300 bg-white border shadow-lg group rounded-3xl hover:shadow-xl hover:-translate-y-1 border-slate-200/80 hover:border-blue-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40'>
						<div className='absolute inset-0 transition-opacity duration-300 opacity-0 rounded-3xl bg-gradient-to-br from-blue-50/50 to-indigo-50/50 group-hover:opacity-100' />

						<div className='relative z-10 flex flex-col h-full'>
							{/* Header area */}
							<div className='flex items-start justify-between mb-8'>
								<div className='flex items-center justify-center transition-transform duration-300 shadow-md w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl group-hover:scale-110 shadow-indigo-500/20'>
									<CapIcon className='text-white' />
								</div>
								<div className='px-3 py-1 text-xs font-bold text-blue-700 border border-blue-100 rounded-full bg-blue-50'>
									A/L Students
								</div>
							</div>

							{/* Content */}
							<div className='flex-1 mb-8'>
								<h2 className='mb-3 text-2xl font-bold transition-colors text-slate-900 group-hover:text-blue-900'>
									Check Degree Eligibility
								</h2>
								<p className='text-sm leading-relaxed text-slate-500'>
									Just provide your details step-by-step! Our AI automatically detects the best matching approach based
									on what you share - stream, Z-score, and interests.
								</p>
							</div>

							{/* Features */}
							<div className='mb-8 space-y-3'>
								{["Smart scenario detection", "Skip optional fields anytime", "AI-powered interest matching"].map(
									(feature, idx) => (
										<div key={idx} className='flex items-start gap-3'>
											<CheckIcon className='w-5 h-5 mt-0.5 text-blue-500' />
											<span className='text-sm font-medium text-slate-600'>{feature}</span>
										</div>
									),
								)}
							</div>

							{/* Action */}
							<div className='inline-flex items-center gap-2 mt-auto text-sm font-bold text-blue-600 transition-all group-hover:gap-3'>
								<span>Check Eligibility</span>
								<ArrowIcon />
							</div>
						</div>
					</button>
				</div>

				{/* Footer info */}
				<div className='mt-16 text-center animate-fadeIn' style={{ animationDelay: "0.4s" }}>
					<div className='inline-flex items-center justify-center gap-3 px-6 py-4 bg-white border shadow-sm border-slate-200 rounded-2xl'>
						<SparklesIcon className='w-5 h-5 text-indigo-500' />
						<p className='text-sm text-slate-600'>
							<span className='font-bold text-slate-900'>Powered by AI:</span> Our system analyzes UGC cutoffs, semantic
							similarity, and career pathways.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
