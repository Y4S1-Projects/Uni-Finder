import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
	const navigate = useNavigate();
	const [isVisible, setIsVisible] = useState(false);

	useEffect(() => {
		setIsVisible(true);
	}, []);

	const handleGetStarted = () => {
		navigate("/degree-recommendations");
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

	const handleCareerPath = () => {
		navigate("/career");
	};

	const handleExploreSolutions = () => {
		const el = document.getElementById("home-features");
		if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
	};

	// Feature cards data
	const features = [
		{
			title: "Degree Recommendations",
			description:
				"Get personalized university degree suggestions based on your A/L results, interests, and career goals using advanced AI algorithms.",
			icon: "🎯",
			gradient: "from-blue-500 to-purple-600",
			bgColor: "bg-blue-50",
			action: handleDegreeRecommendations,
			tags: ["AI-Powered", "350K+ Students", "95% Match Rate"],
		},
		{
			title: "Budget Optimizer",
			description:
				"Plan your university expenses with AI-powered budget predictions based on real-time cost of living data across Sri Lanka.",
			icon: "💰",
			gradient: "from-green-500 to-emerald-600",
			bgColor: "bg-green-50",
			action: handleBudgetOptimizer,
			tags: ["Live Data", "Cost Tracking", "Smart Savings"],
		},
		{
			title: "Career Guidance",
			description:
				"Explore career paths, salary forecasts, and skill requirements to make informed decisions about your professional future.",
			icon: "📈",
			gradient: "from-purple-500 to-pink-600",
			bgColor: "bg-purple-50",
			action: handleCareerPath,
			tags: ["Market Trends", "Skill Gap Analysis", "Salary Insights"],
		},
		{
			title: "Scholarship & Loan Matcher",
			description:
				"Discover scholarships and educational loans you're eligible for with our intelligent matching system.",
			icon: "🏆",
			gradient: "from-orange-500 to-red-600",
			bgColor: "bg-orange-50",
			action: handleScholarshipMatcher,
			tags: ["Auto-Match", "Deadline Alerts", "Max Funding"],
		},
	];

	// How it works steps
	const steps = [
		{
			number: "01",
			title: "Create Your Profile",
			description: "Enter your A/L results, interests, and preferences to build your personalized student profile.",
			icon: "📝",
		},
		{
			number: "02",
			title: "AI Analysis",
			description: "Our advanced algorithms analyze thousands of data points to understand your unique situation.",
			icon: "🔍",
		},
		{
			number: "03",
			title: "Get Recommendations",
			description: "Receive personalized suggestions for degrees, budgets, careers, and funding opportunities.",
			icon: "🎯",
		},
		{
			number: "04",
			title: "Plan Your Future",
			description: "Make informed decisions with data-driven insights and transparent explanations.",
			icon: "🚀",
		},
	];

	// Benefits data
	const benefits = [
		{
			title: "Data-Driven Decisions",
			description: "Every recommendation is backed by real UGC data, cost indices, and labor market statistics.",
			icon: "📊",
		},
		{
			title: "Personalized for You",
			description: "AI algorithms adapt to your unique profile, ensuring relevant and actionable guidance.",
			icon: "🎨",
		},
		{
			title: "Always Up-to-Date",
			description: "Real-time data integration keeps recommendations current with latest trends and opportunities.",
			icon: "⚡",
		},
		{
			title: "Transparent & Explainable",
			description: "Understand the 'why' behind each suggestion with clear, detailed explanations.",
			icon: "💡",
		},
		{
			title: "Comprehensive Coverage",
			description: "From degree selection to career planning, we guide you through every step of your journey.",
			icon: "🗺️",
		},
		{
			title: "Free for Students",
			description: "Access powerful AI tools and insights at no cost, empowering every Sri Lankan student.",
			icon: "🎁",
		},
	];

	return (
		<div className='w-full overflow-hidden bg-[#F5EFFD]'>
			{/* Hero Section */}
			<section className='relative flex items-center justify-center min-h-screen px-4 pt-20 pb-16 overflow-hidden'>
				{/* Background image with overlay */}
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
					{/* Animated blobs on top */}
					<div className='absolute bg-purple-400 rounded-full top-20 left-10 w-72 h-72 mix-blend-multiply filter blur-xl opacity-30 animate-blob'></div>
					<div className='absolute bg-yellow-300 rounded-full top-40 right-10 w-72 h-72 mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000'></div>
					<div className='absolute bg-pink-400 rounded-full -bottom-8 left-40 w-72 h-72 mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000'></div>
				</div>

				<div className='relative grid items-center gap-12 mx-auto max-w-7xl lg:grid-cols-2'>
					{/* Left side - Content */}
					<div className={`space-y-8 ${isVisible ? "animate-slideUp" : "opacity-0"}`}>
						<div className='inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-[#E7E4F6] border border-white/20 backdrop-blur-md shadow-md'>
							<span className='text-base'>✨</span>
							<span>AI guidance for Sri Lankan students</span>
						</div>

						<h1 className='text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-[1.15] drop-shadow-[0_8px_30px_rgba(0,0,0,0.25)]'>
							Transforming Education
							<br className='hidden sm:block' />
							<span className='text-[#C1B4FF]'>with AI precision</span>
						</h1>

						<p className='text-base sm:text-lg text-[#D7D5F1] leading-7 sm:leading-8 max-w-xl'>
							Choose the right degree, manage budgets, plan careers, and discover scholarships with a platform built for
							clarity and confidence.
						</p>

						<div className='flex flex-col sm:flex-row gap-3.5 sm:gap-4'>
							<button
								type='button'
								onClick={handleGetStarted}
								className='group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-gradient-to-r from-[#6C7BFF] via-[#7B5BFF] to-[#A15CFF] px-6 py-3 text-white font-semibold shadow-lg shadow-[#6C7BFF]/25 transition-all duration-300 hover:shadow-[#6C7BFF]/40 hover:-translate-y-0.5'>
								<span className='absolute inset-0 transition-opacity duration-300 opacity-0 bg-white/10 group-hover:opacity-100' />
								<span className='relative'>Get Started</span>
								<span className='relative text-lg transition-transform duration-300 group-hover:translate-x-1'>→</span>
							</button>
							<button
								type='button'
								onClick={handleExploreSolutions}
								className='inline-flex items-center justify-center gap-2 rounded-full border border-white/25 bg-white/15 px-6 py-3 text-sm font-semibold text-white backdrop-blur-md shadow-sm transition-all duration-300 hover:bg-white/25 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-white/10'>
								Explore Solutions
								<span className='text-base'>⤵</span>
							</button>
						</div>

						{/* Floating cards moved from right panel */}
						<div className='grid gap-4 mt-8 sm:mt-10 sm:grid-cols-3'>
							<div className='p-4 bg-white shadow-xl rounded-2xl animate-float animation-delay-1000'>
								<div className='mb-2 text-3xl'>🎯</div>
								<div className='font-bold text-gray-800'>Degree Match</div>
								<div className='text-sm text-gray-600'>95% Accuracy</div>
							</div>

							<div className='p-4 bg-white shadow-xl rounded-2xl animate-float animation-delay-3000'>
								<div className='mb-2 text-3xl'>💰</div>
								<div className='font-bold text-gray-800'>Budget Plan</div>
								<div className='text-sm text-gray-600'>Live Costs</div>
							</div>

							<div className='p-4 bg-white shadow-xl rounded-2xl animate-float animation-delay-5000'>
								<div className='mb-2 text-3xl'>🏆</div>
								<div className='font-bold text-gray-800'>Scholarships</div>
								<div className='text-sm text-gray-600'>Auto-Match</div>
							</div>
						</div>
					</div>
				</div>

				{/* Scroll indicator */}
				<div className='absolute transform -translate-x-1/2 bottom-8 left-1/2 animate-bounce'>
					<div className='flex items-start justify-center w-8 h-12 p-2 border-2 border-purple-400 rounded-full'>
						<div className='w-1.5 h-3 bg-purple-400 rounded-full animate-pulse'></div>
					</div>
				</div>
			</section>

			{/* Features Section */}
			<section id='home-features' className='relative px-4 py-20'>
				{/* Background image */}
				<div className='absolute inset-0'>
					<img
						src='https://api.builder.io/api/v1/image/assets/TEMP/3d3feca384e29ba254d0f805131373400b541c87?width=2048'
						alt='Abstract soft shapes'
						className='object-cover w-full h-full'
					/>
				</div>

				<div className='relative mx-auto max-w-7xl'>
					{/* Section header */}
					<div className='mb-16 text-center animate-slideUp'>
						<span className='inline-flex items-center gap-2 rounded-full bg-[#ECE9FF] text-[#5B4DB2] px-3 py-1 text-xs font-semibold shadow-sm mb-3'>
							Smart pathways · Real outcomes
						</span>
						<h2 className='text-2xl sm:text-3xl font-bold text-[#2D2A4A] mb-3'>
							Empowering students with smart AI solutions
						</h2>
						<p className='text-sm sm:text-base text-[#6B6780] max-w-2xl mx-auto'>
							Navigate education, finances, careers, and funding with guided steps, live data, and transparent
							recommendations.
						</p>
					</div>

					{/* Feature cards grid */}
					<div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 sm:gap-5'>
						{features.map((feature, index) => {
							const images = [
								"https://api.builder.io/api/v1/image/assets/TEMP/ae754e01dd0924ed6678c60f6cb67a17a159ea48?width=436",
								"https://api.builder.io/api/v1/image/assets/TEMP/87c61f1758db5d87fff09a279d27033dffd1db13?width=432",
								"https://api.builder.io/api/v1/image/assets/TEMP/a848690c81bf511ce5f0606e8076f3f7914e8888?width=432",
								"https://api.builder.io/api/v1/image/assets/TEMP/c6f5f821e3a9eb58495c3aa8670eabb72cf63d1b?width=434",
							];
							const accents = [
								"from-[#8EB2FF] to-[#7A7DFF]",
								"from-[#7DE5C2] to-[#46B592]",
								"from-[#F7C77D] to-[#F59E0B]",
								"from-[#FF9BC5] to-[#F472B6]",
							];
							const ctaLabels = ["Find Degrees", "Optimize Budget", "Plan Career", "Find Matches"];

							return (
								<div
									key={index}
									onClick={feature.action}
									onKeyDown={(e) => {
										if (e.key === "Enter" || e.key === " ") {
											e.preventDefault();
											feature.action();
										}
									}}
									tabIndex={0}
									role='button'
									aria-label={`${feature.title} module`}
									className='group relative overflow-hidden rounded-2xl bg-white shadow-[0_12px_40px_rgba(64,64,128,0.12)] border border-[#ECE9FF] transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_16px_50px_rgba(64,64,128,0.16)] cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED]/40'>
									{/* Card image with gradient accent */}
									<div className='relative h-32 overflow-hidden'>
										<img
											src={images[index]}
											alt={feature.title}
											className='object-cover w-full h-full transition-transform duration-500 group-hover:scale-105'
										/>
										<div className={`absolute inset-x-0 bottom-0 h-1.5 bg-gradient-to-r ${accents[index]}`} />
									</div>

									{/* Card content */}
									<div className='flex flex-col h-full gap-3 p-5'>
										<h3 className='text-lg font-semibold text-[#2D2A4A]'>{feature.title}</h3>
										<p className='text-sm text-[#6B6780] leading-6 flex-1'>{feature.description}</p>

										{/* Action buttons */}
										<div className='flex flex-wrap gap-2 pt-1'>
											<button
												type='button'
												onClick={(e) => {
													e.stopPropagation();
													feature.action();
												}}
												className='inline-flex items-center justify-center gap-2 rounded-full bg-[#F5F3FF] text-[#5B4DB2] px-4 py-2 text-sm font-semibold transition-all duration-300 hover:bg-[#ECE9FF] hover:text-[#4338CA] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED]/40'>
												{ctaLabels[index]}
												<span className='text-base transition-transform duration-300 group-hover:translate-x-1'>→</span>
											</button>
											<button
												type='button'
												onClick={(e) => {
													e.stopPropagation();
													feature.action();
												}}
												className='inline-flex items-center justify-center gap-2 rounded-full border border-[#E5E1FF] bg-white px-3.5 py-2 text-sm font-semibold text-[#4C3FA8] transition-all duration-300 hover:bg-[#F5F3FF] hover:border-[#D6D0FF] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED]/30'>
												More details
												<span className='text-sm'>↗</span>
											</button>
										</div>
									</div>
								</div>
							);
						})}
					</div>
				</div>
			</section>

			{/* How It Works Section */}
			<section className='relative px-4 py-20 bg-white'>
				<div className='mx-auto max-w-7xl'>
					<div className='mb-16 text-center'>
						<span className='inline-block px-4 py-2 mb-4 text-sm font-semibold text-blue-700 bg-blue-100 rounded-full'>
							⚙️ Simple Process
						</span>
						<h2 className='mb-4 text-4xl font-bold text-gray-900 md:text-5xl'>How It Works</h2>
						<p className='max-w-2xl mx-auto text-xl text-gray-600'>Get started in just four simple steps</p>
					</div>

					<div className='grid gap-8 md:grid-cols-2 lg:grid-cols-4'>
						{steps.map((step, index) => (
							<div key={index} className='relative'>
								{/* Connecting line (hidden on last item) */}
								{index < steps.length - 1 && (
									<div className='hidden lg:block absolute top-20 left-full w-full h-0.5 bg-gradient-to-r from-purple-300 to-transparent transform -translate-x-1/2 z-0'></div>
								)}

								<div className='relative z-10 p-6 transition-all duration-300 border-2 border-purple-100 shadow-md bg-gradient-to-br from-white to-purple-50 rounded-2xl hover:border-purple-300 hover:shadow-xl'>
									{/* Number badge */}
									<div className='absolute flex items-center justify-center w-12 h-12 text-lg font-bold text-white rounded-full shadow-lg -top-4 -left-4 bg-gradient-to-br from-purple-600 to-blue-600'>
										{step.number}
									</div>

									{/* Icon */}
									<div className='mt-4 mb-4 text-5xl'>{step.icon}</div>

									{/* Content */}
									<h3 className='mb-3 text-xl font-bold text-gray-900'>{step.title}</h3>
									<p className='leading-relaxed text-gray-600'>{step.description}</p>
								</div>
							</div>
						))}
					</div>
				</div>
			</section>

			{/* Benefits Section */}
			<section className='relative px-4 py-20 text-white bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900'>
				<div className='mx-auto max-w-7xl'>
					<div className='mb-16 text-center'>
						<span className='inline-block px-4 py-2 mb-4 text-sm font-semibold text-white rounded-full bg-white/20 backdrop-blur-sm'>
							💎 Why Choose Us
						</span>
						<h2 className='mb-4 text-4xl font-bold md:text-5xl'>Built for Sri Lankan Students</h2>
						<p className='max-w-2xl mx-auto text-xl text-purple-200'>
							Comprehensive AI-powered guidance tailored to the Sri Lankan education system
						</p>
					</div>

					<div className='grid gap-8 md:grid-cols-2 lg:grid-cols-3'>
						{benefits.map((benefit, index) => (
							<div
								key={index}
								className='p-6 transition-all duration-300 border bg-white/10 backdrop-blur-sm rounded-2xl border-white/20 hover:bg-white/20 hover:border-white/40'>
								<div className='mb-4 text-4xl'>{benefit.icon}</div>
								<h3 className='mb-3 text-xl font-bold'>{benefit.title}</h3>
								<p className='leading-relaxed text-purple-200'>{benefit.description}</p>
							</div>
						))}
					</div>
				</div>

				{/* Decorative elements */}
				<div className='absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none'>
					<div className='absolute w-64 h-64 bg-purple-500 rounded-full top-20 left-10 mix-blend-multiply filter blur-3xl opacity-20 animate-blob'></div>
					<div className='absolute w-64 h-64 bg-blue-500 rounded-full bottom-20 right-10 mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000'></div>
				</div>
			</section>

			{/* Impact Stats Section */}
			<section className='relative px-4 py-20 bg-white'>
				<div className='mx-auto max-w-7xl'>
					<div className='p-12 shadow-2xl bg-gradient-to-br from-purple-600 to-blue-600 rounded-3xl'>
						<div className='mb-12 text-center'>
							<h2 className='mb-4 text-4xl font-bold text-white md:text-5xl'>Making Real Impact</h2>
							<p className='text-xl text-purple-100'>Addressing critical challenges in Sri Lankan higher education</p>
						</div>

						<div className='grid gap-8 text-white md:grid-cols-3'>
							<div className='p-6 text-center border bg-white/10 backdrop-blur-sm rounded-2xl border-white/20'>
								<div className='mb-2 text-5xl font-bold'>350,000+</div>
								<div className='mb-2 text-xl font-semibold'>A/L Candidates Annually</div>
								<div className='text-purple-100'>Competing for limited university seats</div>
							</div>

							<div className='p-6 text-center border bg-white/10 backdrop-blur-sm rounded-2xl border-white/20'>
								<div className='mb-2 text-5xl font-bold'>300,000+</div>
								<div className='mb-2 text-xl font-semibold'>Need Alternative Guidance</div>
								<div className='text-purple-100'>Students without university placement</div>
							</div>

							<div className='p-6 text-center border bg-white/10 backdrop-blur-sm rounded-2xl border-white/20'>
								<div className='mb-2 text-5xl font-bold'>15%</div>
								<div className='mb-2 text-xl font-semibold'>Cost Increase</div>
								<div className='text-purple-100'>Living expenses over 5 years</div>
							</div>
						</div>
					</div>
				</div>
			</section>

			{/* CTA Section */}
			<section className='relative px-4 py-24'>
				<div className='max-w-4xl mx-auto text-center'>
					<div className='mb-6 text-5xl'>🚀</div>
					<h2 className='mb-6 text-4xl font-bold text-gray-900 md:text-5xl'>Ready to Start Your Journey?</h2>
					<p className='max-w-2xl mx-auto mb-8 text-xl text-gray-600'>
						Join thousands of Sri Lankan students making smarter decisions about their education and future
					</p>

					<div className='flex flex-col justify-center gap-4 sm:flex-row'>
						<button
							onClick={handleGetStarted}
							className='px-10 py-5 text-lg font-bold text-white transition-all duration-300 transform rounded-full shadow-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-2xl hover:-translate-y-1'>
							Get Started Now →
						</button>

						<button
							onClick={() => navigate("/signin")}
							className='px-10 py-5 text-lg font-bold text-purple-700 transition-all duration-300 transform bg-white border-2 border-purple-200 rounded-full shadow-lg hover:border-purple-400 hover:shadow-xl hover:-translate-y-1'>
							Sign In
						</button>
					</div>

					<p className='mt-8 text-gray-500'>✨ Free forever • 🔒 Secure & Private • 🇱🇰 Made for Sri Lanka</p>
				</div>
			</section>
		</div>
	);
};

export default HomePage;
