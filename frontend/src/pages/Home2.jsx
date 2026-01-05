import React from "react";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
	const navigate = useNavigate();

	const handleGetStarted = () => {
		navigate("/keywords");
	};

	const handleBudgetOptimizer = () => {
		navigate("/budget-optimizer-new");
	};

	const handleDegreeRecommendations = () => {
		navigate("/degree-recommendations");
	};

	const handleScholarshipMatcher = () => {
		navigate("/scholarship-matcher");
	};

	const handleExploreSolutions = () => {
		// Simple, predictable behavior: scroll to the feature section
		const el = document.getElementById("home-features");
		if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
	};

	return (
		<div className='w-full bg-[#F5EFFD] text-[#111827] mt-14'>
			{/* Hero Section */}
			<section className='relative w-full overflow-hidden min-h-[560px] sm:min-h-[620px]'>
				<div className='absolute inset-0'>
					<img
						src='https://api.builder.io/api/v1/image/assets/TEMP/71573ca0dfbd2c49ea7a1e6a82a43175191d7150?width=2048'
						alt='Abstract background'
						className='object-cover w-full h-full'
					/>
					<div
						className='absolute inset-0 mix-blend-multiply'
						style={{
							backgroundImage:
								"linear-gradient(90deg, rgba(11,16,37,0.4) 0%, rgba(27,35,83,0.2) 25%, rgba(122,92,243,0.1) 75%, rgba(255,255,255,0.05) 100%)",
						}}
					/>
				</div>

				<div className='relative px-4 pt-12 pb-10 sm:px-6 lg:px-16 sm:pt-16 lg:pt-14 sm:pb-14 lg:pb-18'>
					<div className='max-w-7xl mx-auto grid lg:grid-cols-[1.05fr_0.95fr] gap-10 items-center'>
						{/* Hero Content */}
						<div className='max-w-2xl'>
							<div className='inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm font-medium text-[#E7E4F6] border border-white/20 backdrop-blur-md shadow-md mb-5'>
								<span className='text-base'>✨</span>
								<span>AI guidance for Sri Lankan students</span>
							</div>

							<h1 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-white leading-[1.15] mb-5 sm:mb-6 drop-shadow-[0_8px_30px_rgba(0,0,0,0.25)]'>
								Transforming Education
								<br className='hidden sm:block' />
								<span className='text-[#C1B4FF]'>with AI precision</span>
							</h1>

							<p className='text-base sm:text-lg text-[#D7D5F1] leading-7 sm:leading-8 max-w-xl mb-7 sm:mb-8'>
								Choose the right degree, manage budgets, plan careers, and discover scholarships with a platform built
								for clarity and confidence.
							</p>

							<div className='flex flex-col sm:flex-row gap-3.5 sm:gap-4'>
								<button
									type='button'
									onClick={handleGetStarted}
									className='group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-gradient-to-r from-[#6C7BFF] via-[#7B5BFF] to-[#A15CFF] px-6 py-3 text-white font-semibold shadow-lg shadow-[#6C7BFF]/25 transition-all duration-300 hover:shadow-[#6C7BFF]/40 hover:-translate-y-0.5'>
									<span className='absolute inset-0 transition-opacity duration-300 opacity-0 bg-white/10 group-hover:opacity-100' />
									<span className='relative'>Get Started</span>
									<span className='relative text-lg transition-transform duration-300 group-hover:translate-x-1'>
										→
									</span>
								</button>
								<button
									type='button'
									onClick={handleExploreSolutions}
									className='inline-flex items-center justify-center gap-2 rounded-full border border-white/25 bg-white/15 px-6 py-3 text-sm font-semibold text-white backdrop-blur-md shadow-sm transition-all duration-300 hover:bg-white/25 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-white/10'>
									Explore Solutions
									<span className='text-base'>⤵</span>
								</button>
							</div>

							<div className='grid gap-4 mt-8 sm:mt-10 sm:grid-cols-2 text-white/90'>
								<div className='flex items-center gap-3 px-4 py-3 border shadow-md rounded-2xl bg-white/10 border-white/15 backdrop-blur-md shadow-black/10'>
									<div className='flex items-center justify-center text-xl h-11 w-11 rounded-xl bg-white/20'>🎯</div>
									<div>
										<p className='text-sm font-semibold text-white'>Personalized journeys</p>
										<p className='text-xs text-white/80'>Tailored to your goals and constraints</p>
									</div>
								</div>
								<div className='flex items-center gap-3 px-4 py-3 border shadow-md rounded-2xl bg-white/10 border-white/15 backdrop-blur-md shadow-black/10'>
									<div className='flex items-center justify-center text-xl h-11 w-11 rounded-xl bg-white/20'>⚡</div>
									<div>
										<p className='text-sm font-semibold text-white'>Actionable insights</p>
										<p className='text-xs text-white/80'>Live costs, funding, and demand trends</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</section>

			{/* Features Section */}
			<section id='home-features' className='relative w-full pt-10 pb-12 sm:pb-16 lg:pb-20 sm:pt-12 lg:pt-14'>
				<div className='absolute inset-0'>
					<img
						src='https://api.builder.io/api/v1/image/assets/TEMP/3d3feca384e29ba254d0f805131373400b541c87?width=2048'
						alt='Abstract soft shapes'
						className='object-cover w-full h-full'
					/>
				</div>

				<div className='relative px-4 sm:px-6 lg:px-12'>
					<div className='mx-auto max-w-7xl'>
						{/* Section Header */}
						<div className='mb-10 text-center sm:mb-12'>
							<p className='inline-flex items-center gap-2 rounded-full bg-[#ECE9FF] text-[#5B4DB2] px-3 py-1 text-xs font-semibold shadow-sm mb-3'>
								Smart pathways · Real outcomes
							</p>
							<h2 className='text-2xl sm:text-3xl font-bold text-[#2D2A4A] mb-3'>
								Empowering students with smart AI solutions
							</h2>
							<p className='text-sm sm:text-base text-[#6B6780] max-w-2xl mx-auto'>
								Navigate education, finances, careers, and funding with guided steps, live data, and transparent
								recommendations.
							</p>
						</div>

						{/* Feature Cards Grid */}
						<div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 sm:gap-5'>
							{[
								{
									title: "Degree Recommendation",
									description: "Personalized degree suggestions based on interests, strengths, and cut-offs.",
									image:
										"https://api.builder.io/api/v1/image/assets/TEMP/ae754e01dd0924ed6678c60f6cb67a17a159ea48?width=436",
									action: handleDegreeRecommendations,
									cta: "Find Degrees",
									accent: "from-[#8EB2FF] to-[#7A7DFF]",
								},
								{
									title: "Budget Optimizer",
									description: "Plan costs, surface savings, and track living expenses with clarity.",
									image:
										"https://api.builder.io/api/v1/image/assets/TEMP/87c61f1758db5d87fff09a279d27033dffd1db13?width=432",
									action: handleBudgetOptimizer,
									cta: "Optimize Budget",
									accent: "from-[#7DE5C2] to-[#46B592]",
								},
								{
									title: "Career Guidance",
									description: "Explore roles, skills, and salary outlooks to build a confident path.",
									image:
										"https://api.builder.io/api/v1/image/assets/TEMP/a848690c81bf511ce5f0606e8076f3f7914e8888?width=432",
									action: () => navigate("/career"),
									cta: "Plan Career",
									accent: "from-[#F7C77D] to-[#F59E0B]",
								},
								{
									title: "Scholarship & Loan Matcher",
									description: "Match scholarships and loans you qualify for, with clear eligibility signals.",
									image:
										"https://api.builder.io/api/v1/image/assets/TEMP/c6f5f821e3a9eb58495c3aa8670eabb72cf63d1b?width=434",
									action: handleScholarshipMatcher,
									cta: "Find Matches",
									accent: "from-[#FF9BC5] to-[#F472B6]",
								},
							].map((card) => (
								<div
									key={card.title}
									onClick={card.action}
									onKeyDown={(e) => {
										if (e.key === "Enter" || e.key === " ") {
											e.preventDefault();
											card.action();
										}
									}}
									tabIndex={0}
									role='button'
									aria-label={`${card.title} module`}
									className='group relative overflow-hidden rounded-2xl bg-white shadow-[0_12px_40px_rgba(64,64,128,0.12)] border border-[#ECE9FF] transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_16px_50px_rgba(64,64,128,0.16)] cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED]/40'>
									<div className='relative h-32 overflow-hidden'>
										<img
											src={card.image}
											alt={card.title}
											className='object-cover w-full h-full transition-transform duration-500 group-hover:scale-105'
										/>
										<div className={`absolute inset-x-0 bottom-0 h-1.5 bg-gradient-to-r ${card.accent}`} />
									</div>
									<div className='flex flex-col h-full gap-3 p-5'>
										<h3 className='text-lg font-semibold text-[#2D2A4A]'>{card.title}</h3>
										<p className='text-sm text-[#6B6780] leading-6 flex-1'>{card.description}</p>
										<div className='flex flex-wrap gap-2 pt-1'>
											<button
												type='button'
												onClick={(e) => {
													e.stopPropagation();
													card.action();
												}}
												className='inline-flex items-center justify-center gap-2 rounded-full bg-[#F5F3FF] text-[#5B4DB2] px-4 py-2 text-sm font-semibold transition-all duration-300 hover:bg-[#ECE9FF] hover:text-[#4338CA] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED]/40'>
												{card.cta}
												<span className='text-base transition-transform duration-300 group-hover:translate-x-1'>→</span>
											</button>
											<button
												type='button'
												onClick={(e) => {
													e.stopPropagation();
													card.action();
												}}
												className='inline-flex items-center justify-center gap-2 rounded-full border border-[#E5E1FF] bg-white px-3.5 py-2 text-sm font-semibold text-[#4C3FA8] transition-all duration-300 hover:bg-[#F5F3FF] hover:border-[#D6D0FF] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED]/30'>
												More details
												<span className='text-sm'>↗</span>
											</button>
										</div>
									</div>
								</div>
							))}
						</div>
					</div>
				</div>
			</section>
		</div>
	);
}
