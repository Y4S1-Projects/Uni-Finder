import { Link } from "react-router-dom";

const LogoMark = () => (
	<svg className='w-8 h-8' viewBox='0 0 32 32' fill='none'>
		<rect width='32' height='32' rx='8' fill='url(#flogo)' />
		<path d='M16 7L8 12v8l8 5 8-5v-8l-8-5z' stroke='#fff' strokeWidth='1.6' strokeLinejoin='round' fill='none' />
		<path d='M16 7v10m0 0l8-5m-8 5l-8-5m8 5v8' stroke='#fff' strokeWidth='1.2' strokeLinejoin='round' opacity='0.6' />
		<circle cx='16' cy='17' r='2.5' fill='#fff' />
		<defs>
			<linearGradient id='flogo' x1='0' y1='0' x2='32' y2='32'>
				<stop stopColor='#6366F1' />
				<stop offset='1' stopColor='#7C3AED' />
			</linearGradient>
		</defs>
	</svg>
);

const SocialIcon = ({ d, label, href }) => (
	<a
		href={href}
		target='_blank'
		rel='noopener noreferrer'
		aria-label={label}
		className='flex items-center justify-center transition-all duration-300 bg-white border rounded-lg w-9 h-9 border-slate-200 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200'>
		<svg className='w-4 h-4' fill='currentColor' viewBox='0 0 24 24'>
			<path d={d} />
		</svg>
	</a>
);

const Footer = () => {
	const year = new Date().getFullYear();

	const platformLinks = [
		{ label: "Home", href: "/" },
		{ label: "Degree Recommendations", href: "/degree-recommendations" },
		{ label: "Budget Optimizer", href: "/budget-optimizer-new" },
		{ label: "Career Guidance", href: "/career" },
		{ label: "Scholarships & Loans", href: "/scholarship-matcher" },
	];

	const legalLinks = [
		{ label: "Privacy Policy", href: "/privacy-policy" },
		{ label: "Terms of Service", href: "/terms-of-service" },
		{ label: "Cookie Policy", href: "/cookie-policy" },
		{ label: "Accessibility", href: "/accessibility" },
	];

	return (
		<footer
			id='site-footer'
			className='w-full mt-auto bg-gradient-to-br from-indigo-50/60 via-white to-purple-50/60 border-t border-white/80 shadow-[0_-8px_30px_-5px_rgba(79,70,229,0.08)]'>
			<div className='px-4 mx-auto max-w-7xl sm:px-6 lg:px-8'>
				{/* Main grid */}
				<div className='grid grid-cols-1 gap-10 py-14 md:grid-cols-3 lg:gap-16'>
					{/* Brand */}
					<div className='space-y-5'>
						<div className='flex items-center gap-2.5'>
							<LogoMark />
							<span className='text-lg font-bold tracking-tight text-slate-900'>Uni-Finder</span>
						</div>
						<p className='max-w-xs text-sm leading-relaxed text-slate-500'>
							Empowering Sri Lankan students with AI-driven guidance for degree selection, career planning, and
							financial management.
						</p>
						<div className='flex gap-2.5 pt-1'>
							<SocialIcon
								label='Facebook'
								href='https://facebook.com'
								d='M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3V2z'
							/>
							<SocialIcon
								label='Twitter'
								href='https://x.com'
								d='M22.46 6c-.77.35-1.6.58-2.46.69a4.3 4.3 0 0 0 1.88-2.38 8.59 8.59 0 0 1-2.72 1.04 4.28 4.28 0 0 0-7.32 3.91A12.16 12.16 0 0 1 3 4.79a4.28 4.28 0 0 0 1.32 5.72 4.24 4.24 0 0 1-1.94-.54v.05a4.28 4.28 0 0 0 3.43 4.2 4.27 4.27 0 0 1-1.93.07 4.29 4.29 0 0 0 4 2.98A8.59 8.59 0 0 1 2 19.54a12.13 12.13 0 0 0 6.56 1.92c7.88 0 12.2-6.53 12.2-12.2 0-.19 0-.37-.01-.56A8.72 8.72 0 0 0 23 6.29l-.54-.29z'
							/>
							<SocialIcon
								label='LinkedIn'
								href='https://linkedin.com'
								d='M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2V9zm2-5a2 2 0 1 1 0 4 2 2 0 0 1 0-4z'
							/>
						</div>
					</div>

					{/* Platform links */}
					<div className='space-y-4'>
						<h4 className='text-sm font-semibold tracking-wider uppercase text-slate-900'>Platform</h4>
						<ul className='pl-0 list-none space-y-2.5'>
							{platformLinks.map((link) => (
								<li key={link.href}>
									<Link
										to={link.href}
										className='text-sm no-underline transition-colors text-slate-500 hover:text-indigo-600'>
										{link.label}
									</Link>
								</li>
							))}
						</ul>
					</div>

					{/* Legal links */}
					<div className='space-y-4'>
						<h4 className='text-sm font-semibold tracking-wider uppercase text-slate-900'>Legal</h4>
						<ul className='pl-0 list-none space-y-2.5'>
							{legalLinks.map((link) => (
								<li key={link.href}>
									<Link
										to={link.href}
										className='text-sm no-underline transition-colors text-slate-500 hover:text-indigo-600'>
										{link.label}
									</Link>
								</li>
							))}
						</ul>
					</div>
				</div>

				{/* Bottom bar */}
				<div className='flex flex-col items-center justify-between gap-4 py-6 text-xs border-t sm:flex-row border-slate-200 text-slate-400'>
					<p>&copy; {year} Uni-Finder. All rights reserved.</p>
					<div className='flex gap-5'>
						<span>Free forever</span>
						<span className='w-0.5 h-3 bg-slate-200 rounded' />
						<span>100% Private</span>
						<span className='w-0.5 h-3 bg-slate-200 rounded' />
						<span>Made in Sri Lanka</span>
					</div>
				</div>
			</div>
		</footer>
	);
};

export default Footer;
