const Footer = () => {
	const currentYear = new Date().getFullYear();

	return (
		<footer className='w-full bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 text-white border-t border-purple-800/30 mt-auto'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				{/* Main footer content */}
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 py-12'>
					{/* Brand section */}
					<div className='space-y-4'>
						<div className='flex items-center gap-2'>
							<span className='text-2xl'>🎓</span>
							<h3 className='text-xl font-bold text-white'>Uni-Finder</h3>
						</div>
						<p className='text-sm text-slate-300 leading-relaxed'>
							Empowering Sri Lankan students with AI-driven guidance for degree selection, career planning, and
							financial management.
						</p>
						<div className='flex gap-3 pt-2'>
							<a
								href='#'
								aria-label='Facebook'
								className='w-10 h-10 rounded-full bg-purple-600/20 hover:bg-purple-600/40 flex items-center justify-center transition-colors'>
								f
							</a>
							<a
								href='#'
								aria-label='Twitter'
								className='w-10 h-10 rounded-full bg-purple-600/20 hover:bg-purple-600/40 flex items-center justify-center transition-colors'>
								𝕏
							</a>
							<a
								href='#'
								aria-label='LinkedIn'
								className='w-10 h-10 rounded-full bg-purple-600/20 hover:bg-purple-600/40 flex items-center justify-center transition-colors'>
								in
							</a>
						</div>
					</div>

					{/* Platform section */}
					<div className='space-y-4'>
						<h4 className='text-lg font-semibold text-white flex items-center gap-2'>
							<span>⚙️</span> Platform
						</h4>
						<ul className='space-y-2 text-sm'>
							<li>
								<a href='/' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Home
								</a>
							</li>
							<li>
								<a href='/degree-recommendations' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Degree Recommendations
								</a>
							</li>
							<li>
								<a href='/budget-optimizer-new' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Budget Optimizer
								</a>
							</li>
							<li>
								<a href='/career' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Career Guidance
								</a>
							</li>
							<li>
								<a href='/scholarship-matcher' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Scholarships & Loans
								</a>
							</li>
						</ul>
					</div>

					{/* Resources section */}
					<div className='space-y-4'>
						<h4 className='text-lg font-semibold text-white flex items-center gap-2'>
							<span>📚</span> Resources
						</h4>
						<ul className='space-y-2 text-sm'>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									How It Works
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Blog & Articles
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									FAQs
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Contact Support
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Status Page
								</a>
							</li>
						</ul>
					</div>

					{/* Legal section */}
					<div className='space-y-4'>
						<h4 className='text-lg font-semibold text-white flex items-center gap-2'>
							<span>⚖️</span> Legal
						</h4>
						<ul className='space-y-2 text-sm'>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Privacy Policy
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Terms of Service
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Cookie Policy
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Data Protection
								</a>
							</li>
							<li>
								<a href='#' className='text-slate-300 hover:text-purple-400 transition-colors'>
									Accessibility
								</a>
							</li>
						</ul>
					</div>
				</div>

				{/* Divider */}
				<div className='border-t border-purple-800/20'></div>

				{/* Bottom bar */}
				<div className='py-6 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-slate-400'>
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
