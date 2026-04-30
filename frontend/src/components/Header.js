import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { signout } from "../redux/User/userSlice";

/* ── SVG Icon Components ── */
const LogoMark = ({ className = "w-8 h-8" }) => (
	<svg className={className} viewBox='0 0 32 32' fill='none'>
		<rect width='32' height='32' rx='8' fill='url(#logo-grad)' />
		<path d='M16 7L8 12v8l8 5 8-5v-8l-8-5z' stroke='#fff' strokeWidth='1.6' strokeLinejoin='round' fill='none' />
		<path d='M16 7v10m0 0l8-5m-8 5l-8-5m8 5v8' stroke='#fff' strokeWidth='1.2' strokeLinejoin='round' opacity='0.6' />
		<circle cx='16' cy='17' r='2.5' fill='#fff' />
		<defs>
			<linearGradient id='logo-grad' x1='0' y1='0' x2='32' y2='32'>
				<stop stopColor='#6366F1' />
				<stop offset='1' stopColor='#7C3AED' />
			</linearGradient>
		</defs>
	</svg>
);

const MenuIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' d='M4 7h16M4 12h16M4 17h16' />
	</svg>
);

const CloseIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' d='M6 18L18 6M6 6l12 12' />
	</svg>
);

const Header = () => {
	const [scrolled, setScrolled] = useState(false);
	const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
	const location = useLocation();
	const isHomePage = location.pathname === "/";

	useEffect(() => {
		const handleScroll = () => setScrolled(window.scrollY > 32);
		window.addEventListener("scroll", handleScroll, { passive: true });
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	// Close mobile menu on route change
	useEffect(() => {
		setMobileMenuOpen(false);
	}, [location.pathname]);

	const currentUser = useSelector((state) => state.user?.currentUser);
	const dispatch = useDispatch();
	const navigate = useNavigate();
	const isScholarshipAdmin = currentUser && ["scholarshipadmin", "scholarshipadmin2"].includes(currentUser.username);
	const isOnAdminPage = location.pathname === "/scholarship-matcher/admin-datasets";
	const showAdminAuth = isScholarshipAdmin && isOnAdminPage;
	const API_BASE = process.env.REACT_APP_BACKEND_URL;

	const handleLogout = async () => {
		try {
			if (API_BASE) await fetch(`${API_BASE}/api/auth/signout`, { credentials: "include" });
		} catch (e) {}
		dispatch(signout());
		navigate("/signInNew");
	};

	const navLinks = [
		{ label: "Home", href: "/" },
		{ label: "Degrees", href: "/degree-recommendations" },
		{ label: "Career", href: "/career" },
		{ label: "Budget", href: "/budget-optimizer-new" },
		{ label: "Scholarships", href: "/scholarship-matcher" },
	];

	const isActive = (path) => location.pathname === path;

	// Determine header visual style
	const isTransparent = isHomePage && !scrolled;

	return (
		<header
			id='site-header'
			className={`fixed top-0 w-full z-50 transition-all duration-500 ${
				isTransparent ?
					"rgba(67,56,202,0.92) backdrop-blur-md shadow-sm"
				:	"bg-white/90 backdrop-blur-xl shadow-[0_1px_3px_rgba(0,0,0,0.06)] border-b border-slate-200/60"
			}`}>
			<div className='px-4 mx-auto max-w-7xl sm:px-6 lg:px-8'>
				<div className='flex items-center justify-between h-16'>
					{/* Logo */}
					<Link to='/' className='flex items-center gap-2.5 group no-underline' id='header-logo'>
						<LogoMark className='transition-transform duration-300 w-9 h-9 group-hover:scale-105' />
						<span
							className={`text-lg font-bold tracking-tight transition-colors duration-300 ${
								isTransparent ? "text-white" : "text-slate-900"
							}`}>
							Uni-Finder
						</span>
					</Link>

					{/* Desktop Nav */}
					<nav className='items-center hidden gap-1 md:flex' id='desktop-nav'>
						{navLinks.map((link) => (
							<Link
								key={link.href}
								to={link.href}
								className={`relative px-2 py-2 mx-1.5 text-md font-bold no-underline transition-colors duration-300 group ${
									isActive(link.href) ?
										isTransparent ? "text-white"
										:	"text-indigo-600"
									: isTransparent ? "text-white/80 hover:text-white"
									: "text-slate-600 hover:text-indigo-600"
								}`}>
								{link.label}
								{/* Animated Underline */}
								<span
									className={`absolute bottom-1 left-0 w-full h-0.5 rounded-full transition-transform duration-300 origin-left ${
										isActive(link.href) ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"
									} ${isTransparent ? "bg-white" : "bg-indigo-600"}`}
								/>
							</Link>
						))}
					</nav>

					{/* Desktop Auth */}
					<div className='items-center hidden gap-3 md:flex' id='desktop-auth'>
						{showAdminAuth ?
							<>
								<span className={`text-sm font-medium ${isTransparent ? "text-white/80" : "text-slate-500"}`}>
									Admin
								</span>
								<button
									type='button'
									onClick={handleLogout}
									className='px-4 py-2 text-sm font-semibold text-indigo-600 transition-all duration-300 border border-indigo-200 rounded-lg bg-indigo-50 hover:bg-indigo-100'>
									Logout
								</button>
							</>
						:	<>
								<Link
									to='/signInNew'
									id='header-signin'
									className={`px-4 py-2 text-sm font-semibold no-underline transition-all duration-300 rounded-lg ${
										isTransparent ?
											"text-white border border-white/30 hover:bg-white/10"
										:	"text-slate-700 hover:text-indigo-600 hover:bg-slate-50"
									}`}>
									Sign In
								</Link>
								<Link
									to='/signUp'
									id='header-signup'
									className={`px-5 py-2 text-sm font-semibold no-underline transition-all duration-300 rounded-lg ${
										isTransparent ?
											"bg-white text-indigo-600 hover:bg-white/90 shadow-lg shadow-white/10"
										:	"bg-indigo-600 text-white hover:bg-indigo-700 shadow-md shadow-indigo-600/20"
									}`}>
									Get Started
								</Link>
							</>
						}
					</div>

					{/* Mobile Controls */}
					<div className='flex items-center gap-2 md:hidden'>
						{showAdminAuth ?
							<button
								type='button'
								onClick={handleLogout}
								className='px-3 py-1.5 text-xs font-semibold rounded-lg text-indigo-600 bg-indigo-50 border border-indigo-200'>
								Logout
							</button>
						:	<Link
								to='/signInNew'
								className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
									isTransparent ? "text-white border border-white/30" : "text-indigo-600 border border-indigo-200"
								}`}>
								Sign In
							</Link>
						}
						<button
							onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
							className={`p-2 rounded-lg transition-all duration-300 ${
								isTransparent ? "text-white hover:bg-white/10" : "text-slate-700 hover:bg-slate-100"
							}`}
							aria-label='Toggle menu'
							id='mobile-menu-toggle'>
							{mobileMenuOpen ?
								<CloseIcon />
							:	<MenuIcon />}
						</button>
					</div>
				</div>

				{/* Mobile Menu */}
				<div
					className={`md:hidden overflow-hidden transition-all duration-400 ease-in-out ${
						mobileMenuOpen ? "max-h-96 opacity-100 pb-5" : "max-h-0 opacity-0"
					}`}
					id='mobile-menu'>
					<div className={`pt-3 mt-2 space-y-1 border-t ${isTransparent ? "border-white/15" : "border-slate-200"}`}>
						{navLinks.map((link) => (
							<Link
								key={link.href}
								to={link.href}
								className={`block px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${
									isActive(link.href) ?
										isTransparent ? "text-white bg-white/15"
										:	"text-indigo-600 bg-indigo-50"
									: isTransparent ? "text-white/80 hover:text-white hover:bg-white/10"
									: "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
								}`}>
								{link.label}
							</Link>
						))}
						{!showAdminAuth && (
							<Link
								to='/signUp'
								className='block w-full px-4 py-2.5 mt-3 text-sm font-semibold text-center text-white rounded-lg bg-indigo-600 hover:bg-indigo-700 transition-all'>
								Get Started Free
							</Link>
						)}
					</div>
				</div>
			</div>
		</header>
	);
};

export default Header;
