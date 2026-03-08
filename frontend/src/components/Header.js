import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { signout } from "../redux/User/userSlice";

const Header = () => {
	const [scrolled, setScrolled] = useState(false);
	const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
	const location = useLocation();
	const isHomePage = location.pathname === "/";

	useEffect(() => {
		const handleScroll = () => {
			const isScrolled = window.scrollY > 50;
			setScrolled(isScrolled);
		};

		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	const currentUser = useSelector((state) => state.user?.currentUser);
	const dispatch = useDispatch();
	const navigate = useNavigate();
	const isScholarshipAdmin = currentUser && ['scholarshipadmin', 'scholarshipadmin2'].includes(currentUser.username);
	const isOnAdminPage = location.pathname === '/scholarship-matcher/admin-datasets';
	const showAdminAuth = isScholarshipAdmin && isOnAdminPage;
	const API_BASE = process.env.REACT_APP_BACKEND_URL;

	const handleLogout = async () => {
		try {
			if (API_BASE) await fetch(`${API_BASE}/api/auth/signout`, { credentials: "include" });
		} catch (e) {}
		dispatch(signout());
		navigate("/signInNew");
		setMobileMenuOpen(false);
	};

	const navLinks = [
		{ label: "Home", href: "/", icon: "🏠" },
		{ label: "Degrees", href: "/degree-recommendations", icon: "🎓" },
		{ label: "Career", href: "/career", icon: "📈" },
		{ label: "Budget", href: "/budget-optimizer-new", icon: "💰" },
		{ label: "Scholarships", href: "/scholarship-matcher", icon: "🏆" },
	];

	const isActive = (path) => location.pathname === path;

	return (
		<header
			className={`fixed top-0 w-full z-50 transition-all duration-300 ${
				scrolled ? "bg-white shadow-lg border-b border-purple-100"
				: isHomePage ? "bg-white/20"
				: "bg-white shadow-md border-b border-purple-100"
			}`}>
			<div className='px-4 mx-auto max-w-7xl sm:px-6 lg:px-8'>
				<div className='flex items-center justify-between h-16'>
					{/* Logo Section */}
					<div className='flex items-center flex-shrink-0'>
						<Link to='/' className='flex items-center gap-2 group'>
							<div
								className={`flex items-center justify-center w-10 h-10 rounded-lg transition-all duration-300 ${
									scrolled || !isHomePage ?
										"bg-gradient-to-br from-purple-600 to-blue-600"
									:	"bg-white/20 backdrop-blur-md border border-white/30 group-hover:bg-white/30"
								}`}>
								<span className='text-xl'>🎓</span>
							</div>
							<span
								className={`text-xl font-bold transition-colors duration-300 ${
									scrolled || !isHomePage ? "text-slate-900" : "text-white"
								}`}>
								Uni-Finder
							</span>
						</Link>
					</div>

					{/* Desktop Navigation */}
					<nav className='items-center hidden gap-1 md:flex'>
						{navLinks.map((link) => (
							<Link
								key={link.href}
								to={link.href}
								className={`px-3 py-2 rounded-lg font-medium text-sm transition-all duration-300 flex items-center gap-1 ${
									isActive(link.href) ?
										scrolled || !isHomePage ?
											"text-purple-600 bg-purple-100"
										:	"text-white bg-white/20"
									: scrolled || !isHomePage ? "text-slate-700 hover:text-purple-600 hover:bg-purple-50"
									: "text-white/90 hover:text-white hover:bg-white/10"
								}`}>
								<span>{link.icon}</span>
								<span>{link.label}</span>
							</Link>
						))}
					</nav>

					{/* Auth Buttons - Desktop */}
					<div className='items-center hidden gap-3 md:flex'>
						{showAdminAuth ? (
							<>
								<span
									className={`text-sm font-medium ${
										scrolled || !isHomePage ? "text-slate-700" : "text-white/90"
									}`}>
									Admin
								</span>
								<button
									type='button'
									onClick={handleLogout}
									className='px-5 py-2 rounded-lg font-semibold text-sm transition-all duration-300 bg-purple-100 text-purple-700 hover:bg-purple-200 border border-purple-200'>
									Logout
								</button>
							</>
						) : (
							<>
								<Link
									to='/signInNew'
									className={`px-5 py-2 rounded-lg font-semibold text-sm transition-all duration-300 border-2 ${
										scrolled || !isHomePage ?
											"text-purple-600 border-purple-600 hover:bg-purple-50"
										:	"text-white border-white/40 hover:border-white hover:bg-white/10"
									}`}>
									Sign In
								</Link>
								<Link
									to='/signUp'
									className={`px-5 py-2 rounded-lg font-semibold text-sm transition-all duration-300 ${
										scrolled || !isHomePage ?
											"bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg hover:-translate-y-0.5"
										:	"bg-white text-purple-600 hover:shadow-lg hover:-translate-y-0.5"
									}`}>
									Get Started
								</Link>
							</>
						)}
					</div>

					{/* Mobile Menu Button */}
					<div className='flex items-center gap-3 md:hidden'>
						{showAdminAuth ? (
							<button
								type='button'
								onClick={handleLogout}
								className='px-3 py-1.5 rounded-lg font-semibold text-xs transition-all duration-300 bg-purple-100 text-purple-700 hover:bg-purple-200 border border-purple-200'>
								Logout
							</button>
						) : (
							<Link
								to='/signInNew'
								className={`px-3 py-1.5 rounded-lg font-semibold text-xs transition-all duration-300 ${
									scrolled || !isHomePage ?
										"text-purple-600 border border-purple-600"
									:	"text-white border border-white/40"
								}`}>
								Sign In
							</Link>
						)}
						<button
							onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
							className={`p-2 rounded-lg transition-all duration-300 ${
								scrolled || !isHomePage ? "text-slate-900 hover:bg-slate-100" : "text-white hover:bg-white/10"
							}`}
							aria-label='Toggle menu'>
							<svg className='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
								{mobileMenuOpen ?
									<path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M6 18L18 6M6 6l12 12' />
								:	<path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M4 6h16M4 12h16M4 18h16' />}
							</svg>
						</button>
					</div>
				</div>

				{/* Mobile Menu */}
				{mobileMenuOpen && (
					<div
						className={`md:hidden pb-4 space-y-2 border-t ${
							scrolled || !isHomePage ? "border-slate-200 bg-white" : "border-white/20 bg-black/20 backdrop-blur-md"
						}`}>
						{navLinks.map((link) => (
							<Link
								key={link.href}
								to={link.href}
								onClick={() => setMobileMenuOpen(false)}
								className={`block px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
									isActive(link.href) ?
										scrolled || !isHomePage ?
											"text-purple-600 bg-purple-100"
										:	"text-white bg-white/20"
									: scrolled || !isHomePage ? "text-slate-700 hover:text-purple-600 hover:bg-purple-50"
									: "text-white/90 hover:text-white hover:bg-white/10"
								}`}>
								<span className='inline-flex items-center gap-2'>
									<span>{link.icon}</span>
									<span>{link.label}</span>
								</span>
							</Link>
						))}
						{showAdminAuth ? (
							<button
								type='button'
								onClick={handleLogout}
								className='block w-full px-4 py-2 mt-4 text-sm font-semibold text-center text-purple-700 transition-all duration-300 rounded-lg bg-purple-100 hover:bg-purple-200 border border-purple-200'>
								Logout
							</button>
						) : (
							<Link
								to='/signUp'
								onClick={() => setMobileMenuOpen(false)}
								className='block w-full px-4 py-2 mt-4 text-sm font-semibold text-center text-white transition-all duration-300 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg'>
								Get Started Free
							</Link>
						)}
					</div>
				)}
			</div>
		</header>
	);
};

export default Header;
