const Footer = () => {
	const currentYear = new Date().getFullYear();

	return (
		<footer className='w-full mt-auto text-white border-t bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 border-purple-800/30'>
			<div className='px-4 mx-auto max-w-7xl sm:px-6 lg:px-8'>
				{/* Main footer content */}
				<div className='grid grid-cols-1 gap-8 py-12 md:grid-cols-2 lg:grid-cols-4'>
					{/* Brand section */}
					<div className='space-y-4'>
						<div className='flex items-center gap-2'>
							<span className='text-2xl'>🎓</span>
							<h3 className='text-xl font-bold text-white'>Uni-Finder</h3>
						</div>
						<p className='text-sm leading-relaxed text-slate-300'>
							Empowering Sri Lankan students with AI-driven guidance for degree selection, career planning, and
							financial management.
						</p>
						<div className='flex gap-3 pt-2'>
							<a
								href='https://facebook.com'
								target='_blank'
								rel='noopener noreferrer'
								aria-label='Facebook'
								className='flex items-center justify-center w-10 h-10 transition-colors rounded-full bg-purple-600/20 hover:bg-purple-600/40'>
								f
							</a>
							<a
								href='https://x.com'
								target='_blank'
								rel='noopener noreferrer'
								aria-label='Twitter'
								className='flex items-center justify-center w-10 h-10 transition-colors rounded-full bg-purple-600/20 hover:bg-purple-600/40'>
								𝕏
							</a>
							<a
								href='https://linkedin.com'
								target='_blank'
								rel='noopener noreferrer'
								aria-label='LinkedIn'
								className='flex items-center justify-center w-10 h-10 transition-colors rounded-full bg-purple-600/20 hover:bg-purple-600/40'>
								in
							</a>
						</div>
					</div>

					{/* Platform section */}
					<div className='space-y-4'>
						<h4 className='flex items-center gap-2 text-lg font-semibold text-white'>
							<span>⚙️</span> Platform
						</h4>
						<ul className='space-y-2 text-sm'>
							<li>
								<a href='/' className='transition-colors text-slate-300 hover:text-purple-400'>
									Home
								</a>
							</li>
							<li>
								<a href='/degree-recommendations' className='transition-colors text-slate-300 hover:text-purple-400'>
									Degree Recommendations
								</a>
							</li>
							<li>
								<a href='/budget-optimizer-new' className='transition-colors text-slate-300 hover:text-purple-400'>
									Budget Optimizer
								</a>
							</li>
							<li>
								<a href='/career' className='transition-colors text-slate-300 hover:text-purple-400'>
									Career Guidance
								</a>
							</li>
							<li>
								<a href='/scholarship-matcher' className='transition-colors text-slate-300 hover:text-purple-400'>
									Scholarships & Loans
								</a>
							</li>
						</ul>
					</div>

					{/* Resources section */}
					<div className='space-y-4'>
						<h4 className='flex items-center gap-2 text-lg font-semibold text-white'>
							<span>📚</span> Resources
						</h4>
						<ul className='space-y-2 text-sm'>
							<li>
								<a href='/how-it-works' className='transition-colors text-slate-300 hover:text-purple-400'>
									How It Works
								</a>
							</li>
							<li>
								<a href='/blog' className='transition-colors text-slate-300 hover:text-purple-400'>
									Blog & Articles
								</a>
							</li>
							<li>
								<a href='/faq' className='transition-colors text-slate-300 hover:text-purple-400'>
									FAQs
								</a>
							</li>
							<li>
								<a href='/support' className='transition-colors text-slate-300 hover:text-purple-400'>
									Contact Support
								</a>
							</li>
							<li>
								<a href='/status' className='transition-colors text-slate-300 hover:text-purple-400'>
									Status Page
								</a>
							</li>
						</ul>
					</div>

					{/* Legal section */}
					<div className='space-y-4'>
						<h4 className='flex items-center gap-2 text-lg font-semibold text-white'>
							<span>⚖️</span> Legal
						</h4>
						<ul className='space-y-2 text-sm'>
							<li>
								<a href='/privacy-policy' className='transition-colors text-slate-300 hover:text-purple-400'>
									Privacy Policy
								</a>
							</li>
							<li>
								<a href='/terms-of-service' className='transition-colors text-slate-300 hover:text-purple-400'>
									Terms of Service
								</a>
							</li>
							<li>
								<a href='/cookie-policy' className='transition-colors text-slate-300 hover:text-purple-400'>
									Cookie Policy
								</a>
							</li>
							<li>
								<a href='/data-protection' className='transition-colors text-slate-300 hover:text-purple-400'>
									Data Protection
								</a>
							</li>
							<li>
								<a href='/accessibility' className='transition-colors text-slate-300 hover:text-purple-400'>
									Accessibility
								</a>
							</li>
						</ul>
					</div>
				</div>

				{/* Divider */}
				<div className='border-t border-purple-800/20'></div>

				{/* Bottom bar */}
				<div className='flex flex-col items-center justify-between gap-4 py-6 text-sm sm:flex-row text-slate-400'>
					<div>
						<p>&copy; {currentYear} Uni-Finder. All rights reserved. | Made with 💜 for Sri Lankan students</p>
					</div>
					<div className='flex gap-6'>
						<span className='flex items-center gap-2'>✨ Free forever</span>
						<span className='flex items-center gap-2'>🔒 100% Private</span>
						<span className='flex items-center gap-2'>🇱🇰 Sri Lanka</span>
					</div>
				</div>
			</div>
		</footer>
	);
};

export default Footer;
