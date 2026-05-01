import React, { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const ArrowIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3' />
	</svg>
);
const ChevronDown = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='m19.5 8.25-7.5 7.5-7.5-7.5' />
	</svg>
);

const HomePage = () => {
	const navigate = useNavigate();
	const revealRefs = useRef([]);

	useEffect(() => {
		const obs = new IntersectionObserver(
			(entries) =>
				entries.forEach((e) => {
					if (e.isIntersecting) e.target.classList.add("in-view");
				}),
			{ threshold: 0.1, rootMargin: "0px 0px -30px 0px" },
		);
		revealRefs.current.forEach((el) => el && obs.observe(el));
		return () => obs.disconnect();
	}, []);
	const addRef = (el) => {
		if (el && !revealRefs.current.includes(el)) revealRefs.current.push(el);
	};

	const features = [
		{
			title: "Degree Recommendations",
			desc: "Get personalized university degree suggestions based on your A/L results, interests, and career goals using advanced AI algorithms.",
			img: "/images/feature-degree1.png",
			gradient: "from-blue-500 to-indigo-600",
			tagBg: "bg-blue-50 text-blue-700",
			tag: "AI-Powered",
			action: () => navigate("/degree-recommendations"),
			cta: "Find Degrees",
		},
		{
			title: "Budget Optimizer",
			desc: "Plan your university expenses with AI-powered budget predictions based on real-time cost of living data across Sri Lanka.",
			img: "/images/feature-budget1.png",
			gradient: "from-emerald-500 to-teal-600",
			tagBg: "bg-emerald-50 text-emerald-700",
			tag: "Live Data",
			action: () => navigate("/budget-optimizer-new"),
			cta: "Optimize Budget",
		},
		{
			title: "Career Guidance",
			desc: "Explore career paths, salary forecasts, and skill requirements to make informed decisions about your professional future.",
			img: "/images/feature-career1.png",
			gradient: "from-amber-500 to-orange-600",
			tagBg: "bg-amber-50 text-amber-700",
			tag: "Market Trends",
			action: () => navigate("/career"),
			cta: "Plan Career",
		},
		{
			title: "Scholarship & Loan Matcher",
			desc: "Discover scholarships and educational loans you're eligible for with our intelligent matching system.",
			img: "/images/feature-scholarship1.png",
			gradient: "from-rose-500 to-pink-600",
			tagBg: "bg-rose-50 text-rose-700",
			tag: "Auto-Match",
			action: () => navigate("/scholarship-matcher"),
			cta: "Find Matches",
		},
	];

	const steps = [
		{
			num: "01",
			title: "Create Profile",
			desc: "Enter your A/L results, interests, and preferences to build your student profile.",
			color: "from-blue-500 to-indigo-600",
		},
		{
			num: "02",
			title: "AI Analysis",
			desc: "Our algorithms analyze thousands of data points to understand your needs.",
			color: "from-violet-500 to-purple-600",
		},
		{
			num: "03",
			title: "Get Recommendations",
			desc: "Receive personalized suggestions for degrees, budgets, and careers.",
			color: "from-pink-500 to-rose-600",
		},
		{
			num: "04",
			title: "Plan Your Future",
			desc: "Make informed decisions with data-driven, transparent insights.",
			color: "from-amber-500 to-orange-600",
		},
	];

	return (
		<div className='w-full overflow-hidden'>
			{/* ══════ HERO ══════ */}
			<section id='hero-section' className='relative min-h-[100vh] flex items-center px-4 overflow-hidden'>
				{/* Background image */}
				<div className='absolute inset-0'>
					<img src='/images/hero-2.png' alt='' aria-hidden='true' className='object-cover w-full h-full' />
					{/* Gradient overlay for readability */}
					<div
						className='absolute inset-0'
						style={{
							background:
								"linear-gradient(to right, rgba(67,56,202,0.92) 0%, rgba(144, 145, 228, 0.777) 35%, rgba(129, 141, 248, 0.105) 60%, rgba(165, 180, 252, 0) 80%, rgba(199,210,254,0.2) 100%)",
						}}
					/>
				</div>

				{/* Ambient light orbs */}
				<div className='absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-violet-400/20 rounded-full blur-[160px] pointer-events-none' />
				<div className='absolute bottom-[-10%] right-[10%] w-[400px] h-[400px] bg-blue-300/10 rounded-full blur-[140px] pointer-events-none' />

				<div className='relative w-full mx-auto max-w-7xl'>
					{/* Left-aligned text content */}
					<div className='max-w-xl py-24 space-y-7 animate-slideUp lg:max-w-2xl'>
						<div className='inline-flex items-center gap-2 px-4 py-1.5 text-sm font-medium border rounded-full bg-white/20 border-white/25 text-white backdrop-blur-sm'>
							<span className='w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse' />
							AI-powered guidance for Sri Lankan students
						</div>

						<h1 className='text-4xl font-extrabold leading-[1.08] tracking-tight text-white sm:text-5xl lg:text-6xl'>
							Your pathway to the
							<span className='block mt-1 text-transparent bg-clip-text bg-gradient-to-r from-white via-violet-200 to-amber-200'>
								right education
							</span>
						</h1>

						<p className='max-w-lg text-lg leading-relaxed text-white/80'>
							Choose the right degree, manage budgets, plan careers, and discover scholarships — all with data-driven
							clarity.
						</p>

						<div className='flex flex-col gap-3 sm:flex-row sm:gap-4'>
							<button
								type='button'
								id='hero-get-started'
								onClick={() => navigate("/degree-recommendations")}
								className='group inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-semibold rounded-xl bg-white text-indigo-700 shadow-lg shadow-indigo-500/25 transition-all duration-300 hover:shadow-xl hover:-translate-y-0.5'>
								Get Started
								<span className='transition-transform duration-300 group-hover:translate-x-1'>
									<ArrowIcon />
								</span>
							</button>
							<button
								type='button'
								id='hero-explore'
								onClick={() => {
									const el = document.getElementById("features-section");
									if (el) el.scrollIntoView({ behavior: "smooth" });
								}}
								className='inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-semibold rounded-xl border border-white/30 text-white bg-white/15 backdrop-blur-sm transition-all duration-300 hover:bg-white/25 hover:-translate-y-0.5'>
								Explore Features <ChevronDown />
							</button>
						</div>

						{/* Trust stats */}
						<div className='flex flex-wrap gap-8 pt-4 border-t border-white/15'>
							{[
								{ val: "350K+", label: "Students reached" },
								{ val: "95%", label: "Match accuracy" },
								{ val: "100%", label: "Free to use" },
							].map((s) => (
								<div key={s.label}>
									<div className='text-2xl font-bold text-white'>{s.val}</div>
									<div className='text-xs font-medium tracking-wide uppercase text-white/50'>{s.label}</div>
								</div>
							))}
						</div>
					</div>
				</div>

				{/* Scroll indicator */}
				<div className='absolute z-10 hidden transform -translate-x-1/2 sm:block bottom-6 left-1/2'>
					<div className='flex items-start justify-center w-7 h-11 p-1.5 border border-white/20 rounded-full'>
						<div className='w-1 h-2.5 rounded-full bg-white/50 animate-bounce' />
					</div>
				</div>
			</section>

			{/* ══════ FEATURES ══════ */}
			<section id='features-section' className='relative px-4 bg-white py-28'>
				<div className='mx-auto max-w-7xl'>
					<div className='mb-20 text-center reveal' ref={addRef}>
						<p className='mb-3 text-sm font-semibold tracking-widest text-indigo-600 uppercase'>What we offer</p>
						<h2 className='mb-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl'>
							Smart tools for every step of your journey
						</h2>
						<p className='max-w-2xl mx-auto text-base leading-relaxed text-slate-500'>
							Navigate education, finances, careers, and funding with guided steps and transparent recommendations.
						</p>
					</div>

					{/* Alternating left-right layout for features */}
					<div className='space-y-20'>
						{features.map((f, i) => (
							<div key={f.title} className='reveal' ref={addRef} style={{ animationDelay: `${i * 0.08}s` }}>
								<div
									className={`grid items-center gap-10 lg:gap-16 lg:grid-cols-2 ${i % 2 === 1 ? "lg:direction-rtl" : ""}`}>
									{/* Image — shown first on even, second on odd (handled by order) */}
									<div className={`${i % 2 === 1 ? "lg:order-2" : ""}`}>
										<div className='relative group'>
											<div
												className={`absolute -inset-3 rounded-2xl bg-gradient-to-br ${f.gradient} opacity-[0.07] group-hover:opacity-[0.12] blur-xl transition-opacity duration-500`}
											/>
											<div className='relative overflow-hidden border shadow-lg rounded-2xl border-slate-200/70 shadow-slate-200/50'>
												<img
													src={f.img}
													alt={f.title}
													className='w-full transition-transform duration-700 bg-white'
													style={{ aspectRatio: "16/9", objectFit: "contain" }}
												/>
											</div>
										</div>
									</div>

									{/* Content */}
									<div className={`space-y-5 ${i % 2 === 1 ? "lg:order-1" : ""}`}>
										<span className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${f.tagBg}`}>
											{f.tag}
										</span>
										<h3 className='text-2xl font-bold text-slate-900 sm:text-3xl'>{f.title}</h3>
										<p className='text-base leading-relaxed text-slate-500'>{f.desc}</p>
										<button
											type='button'
											onClick={f.action}
											className={`group inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold rounded-xl bg-gradient-to-r ${f.gradient} text-white shadow-md transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5`}>
											{f.cta}
											<span className='transition-transform duration-300 group-hover:translate-x-1'>
												<ArrowIcon />
											</span>
										</button>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			</section>

			{/* ══════ HOW IT WORKS ══════ */}
			<section
				id='how-it-works'
				className='relative px-4 overflow-hidden py-28 bg-gradient-to-br from-indigo-50 via-violet-50 to-purple-50'>
				<div className='absolute top-0 left-1/4 w-[400px] h-[400px] bg-indigo-300/20 rounded-full blur-[120px] pointer-events-none' />
				<div className='absolute bottom-0 right-1/4 w-[300px] h-[300px] bg-violet-300/20 rounded-full blur-[100px] pointer-events-none' />

				<div className='relative mx-auto max-w-7xl'>
					<div className='mb-16 text-center reveal' ref={addRef}>
						<p className='mb-3 text-sm font-semibold tracking-widest text-indigo-600 uppercase'>How it works</p>
						<h2 className='mb-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl'>
							Get started in four simple steps
						</h2>
						<p className='max-w-xl mx-auto text-base text-slate-500'>
							From profile creation to personalized recommendations in minutes.
						</p>
					</div>

					<div className='grid gap-5 sm:grid-cols-2 lg:grid-cols-4'>
						{steps.map((step, i) => (
							<div key={step.num} className='relative reveal' ref={addRef} style={{ animationDelay: `${i * 0.1}s` }}>
								{i < steps.length - 1 && (
									<div className='hidden lg:block absolute top-10 left-[calc(50%+40px)] w-[calc(100%-80px)] h-px bg-gradient-to-r from-indigo-300/50 to-transparent z-0' />
								)}
								<div className='relative z-10 flex flex-col items-center text-center transition-all duration-300 bg-white border shadow-sm p-7 rounded-2xl border-slate-200/80 hover:shadow-lg hover:border-indigo-200 group'>
									<div
										className={`flex items-center justify-center w-16 h-16 mb-5 rounded-2xl bg-gradient-to-br ${step.color} shadow-lg shadow-indigo-400/20 transition-transform duration-300 group-hover:scale-110`}>
										<span className='text-xl font-bold text-white'>{step.num}</span>
									</div>
									<h3 className='mb-2 text-lg font-semibold text-slate-900'>{step.title}</h3>
									<p className='text-sm leading-relaxed text-slate-500'>{step.desc}</p>
								</div>
							</div>
						))}
					</div>
				</div>
			</section>

			{/* ══════ CTA ══════ */}
			<section
				id='cta-section'
				className='relative px-4 overflow-hidden py-28'
				style={{ background: "linear-gradient(135deg, #6366F1 0%, #818CF8 30%, #7C3AED 60%, #A78BFA 100%)" }}>
				<div className='absolute top-0 right-0 w-[500px] h-[500px] bg-pink-300/15 rounded-full blur-[140px] pointer-events-none' />
				<div className='absolute bottom-0 left-0 w-[400px] h-[400px] bg-blue-300/15 rounded-full blur-[120px] pointer-events-none' />

				<div className='relative max-w-3xl mx-auto text-center reveal' ref={addRef}>
					<h2 className='mb-5 text-3xl font-bold text-white sm:text-4xl lg:text-5xl'>Ready to shape your future?</h2>
					<p className='max-w-xl mx-auto mb-10 text-lg text-white/75'>
						Join thousands of Sri Lankan students making smarter decisions about their education and career.
					</p>

					<div className='flex flex-col justify-center gap-4 sm:flex-row'>
						<button
							type='button'
							id='cta-get-started'
							onClick={() => navigate("/degree-recommendations")}
							className='group inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold rounded-xl bg-white text-indigo-700 shadow-lg shadow-indigo-500/20 transition-all duration-300 hover:shadow-xl hover:-translate-y-0.5'>
							Get Started Now
							<span className='transition-transform duration-300 group-hover:translate-x-1'>
								<ArrowIcon />
							</span>
						</button>
						<button
							type='button'
							id='cta-signin'
							onClick={() => navigate("/signInNew")}
							className='inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold border rounded-xl border-white/30 text-white bg-white/10 backdrop-blur-sm transition-all duration-300 hover:bg-white/20 hover:-translate-y-0.5'>
							Sign In
						</button>
					</div>

					<div className='flex items-center justify-center gap-6 mt-10 text-sm font-medium text-white/60'>
						<span>Free forever</span>
						<span className='w-1 h-1 rounded-full bg-white/30' />
						<span>Secure & Private</span>
						<span className='w-1 h-1 rounded-full bg-white/30' />
						<span>Made for Sri Lanka</span>
					</div>
				</div>
			</section>
		</div>
	);
};

export default HomePage;
