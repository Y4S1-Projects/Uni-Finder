import React, { useState, useEffect, useCallback } from "react";
import { useLocation } from "react-router-dom";
import CareerLadderNetwork from "../components/CareerLadder/CareerLadderNetwork";
import CareerPathComparator from "../components/CareerLadder/CareerPathComparator";
import ViewModeSelector from "../components/CareerLadder/ViewModeSelector";
import { analyzeCareerProgression, compareCareerPaths, getAllDomains } from "../api/careerLadderApi";
import { FaProjectDiagram, FaGlobe } from "react-icons/fa";

export default function CareerLadderPage() {
	const location = useLocation();
	const { userSkills, recommendations, userProfile } = location.state || {};

	const [viewMode, setViewMode] = useState("network"); // comparison, network
	const [comparisonData, setComparisonData] = useState(null);
	const [availableDomains, setAvailableDomains] = useState([]);
	const [loading, setLoading] = useState(true);
	const [allProgressionsData, setAllProgressionsData] = useState(null);

	// Load data immediately on mount
	const loadDomains = useCallback(async () => {
		try {
			const data = await getAllDomains();

			// Extract top 5 domains based on best matching recommendations
			let topDomains = [];
			if (recommendations && recommendations.length > 0) {
				const domainSet = new Set();
				for (const rec of recommendations) {
					if (rec.domain && !domainSet.has(rec.domain)) {
						domainSet.add(rec.domain);
						const domainObj = data.domains.find((d) => d.domain_id === rec.domain);
						if (domainObj) topDomains.push(domainObj);
					}
					if (topDomains.length >= 5) break;
				}
			}

			// If we don't have 5 domains from recommendations, fill with remaining domains
			if (topDomains.length < 5) {
				const remaining = data.domains.filter((d) => !topDomains.find((td) => td.domain_id === d.domain_id));
				topDomains = [...topDomains, ...remaining].slice(0, 5);
			}

			setAvailableDomains(topDomains);
			return topDomains;
		} catch (error) {
			console.error("Error loading domains:", error);
			return [];
		}
	}, [recommendations]);

	const loadAllProgressions = useCallback(
		async (domains) => {
			try {
				if (!userSkills) return;
				const domainsToLoad = domains || availableDomains;
				const promises = domainsToLoad.map((d) =>
					analyzeCareerProgression({
						user_skill_ids: userSkills,
						target_domain: d.domain_id,
						current_role_id: recommendations?.[0]?.role_id,
						show_all_levels: true, // Show ALL levels in network/ecosystem view
					}),
				);
				const results = await Promise.all(promises);
				setAllProgressionsData(results);
			} catch (error) {
				console.error("Error loading all progressions:", error);
			}
		},
		[availableDomains, recommendations, userSkills],
	);

	useEffect(() => {
		window.scrollTo(0, 0);
		const init = async () => {
			setLoading(true);
			const domains = await loadDomains();
			if (viewMode === "network") {
				await loadAllProgressions(domains);
			}
			setLoading(false);
		};
		init();
	}, [userSkills, viewMode, loadDomains, loadAllProgressions]);

	const loadComparisonData = async (domains) => {
		setLoading(true);
		try {
			const data = await compareCareerPaths({
				user_skill_ids: userSkills,
				domains: domains,
			});
			setComparisonData(data);
		} catch (error) {
			console.error("Error loading comparison:", error);
		} finally {
			setLoading(false);
		}
	};

	const handleViewModeChange = (mode) => {
		setViewMode(mode);

		if (mode === "comparison" && !comparisonData) {
			// Load comparison for top 3 domains
			const topDomains = availableDomains.slice(0, 3).map((d) => d.domain_id);
			loadComparisonData(topDomains);
		} else if (mode === "network" && !allProgressionsData) {
			loadAllProgressions();
		}
	};

	if (loading) {
		return <LoadingSpinner />;
	}

	return (
		<div className='min-h-screen pt-0 overflow-x-hidden bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 text-slate-900'>
			<div className='relative z-10 p-0 m-0'>
				{/* 🚀 AI-Powered Ecosystem Header */}
				<header className='sticky top-[64px] z-40 bg-white/80 backdrop-blur-2xl border-b border-slate-200 shadow-sm mt-[64px]'>
					<div className='max-w-[2000px] mx-auto px-8 pt-8 pb-2 flex flex-col lg:flex-row items-center justify-between gap-4 w-full'>
						<div className='flex flex-col items-center justify-center gap-1 text-center lg:items-start lg:text-left group'>
							<div className='flex items-center gap-3'>
								<div
									className='p-2.5 rounded-xl shadow-lg relative transform transition-transform group-hover:rotate-12'
									style={{
										background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
									}}>
									<div className='absolute inset-0 rounded-full bg-blue-500/20 blur-xl' />
									<FaProjectDiagram className='relative text-2xl text-white' />
								</div>

								<h1
									className='text-3xl font-bold tracking-tight md:text-4xl'
									style={{
										background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
										WebkitBackgroundClip: "text",
										WebkitTextFillColor: "transparent",
										backgroundClip: "text",
									}}>
									Career Ladder
								</h1>
							</div>

							<p className='flex items-center gap-2 text-base font-medium text-gray-600'>
								<FaGlobe className='hidden text-blue-500/70 sm:inline-block' />
								Explore career pathways and discover the skills you need to advance in your journey
							</p>
						</div>

						<div className='flex flex-col items-center w-full gap-4 sm:flex-row lg:w-auto'>
							<div className='bg-white p-1.5 rounded-2xl border border-slate-200 shadow-sm flex items-center w-full sm:w-auto'>
								<ViewModeSelector mode={viewMode} onChange={handleViewModeChange} />
							</div>
						</div>
					</div>
				</header>

				{/* 🔮 Dynamic Full-Screen Canvas Area */}
				<main className='relative'>
					<div
						className={`${viewMode === "network" ? "h-[calc(100vh-140px)] w-full" : "max-w-7xl mx-auto pt-6 pb-16 px-6"}`}>
						{viewMode === "network" && allProgressionsData && (
							<div className='relative w-full h-full duration-1000 animate-in fade-in'>
								<div className='absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(59,130,246,0.08),transparent_50%)] pointer-events-none' />
								<CareerLadderNetwork
									allProgressions={allProgressionsData}
									userSkills={userSkills}
									userProfile={userProfile}
								/>
							</div>
						)}

						{viewMode === "comparison" && comparisonData && (
							<div className='bg-white rounded-[3rem] border border-slate-200 p-12 shadow-xl border-t-white'>
								<div className='flex flex-col justify-between gap-6 mb-12 md:flex-row md:items-end'>
									<div className='space-y-2'>
										<h2 className='text-4xl font-extrabold text-[#111827] tracking-tight'>Compare Paths</h2>
										<p className='max-w-2xl text-lg font-medium text-slate-600'>
											See how you match across different career domains and identify your strongest overlaps.
										</p>
									</div>
									<div className='h-0.5 flex-grow mx-12 border-t border-slate-200 hidden lg:block' />
								</div>
								<CareerPathComparator comparisonData={comparisonData} userSkills={userSkills} />
							</div>
						)}
					</div>
				</main>
			</div>
		</div>
	);
}

function LoadingSpinner() {
	return (
		<div className='flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 via-white to-purple-50'>
			<div className='relative flex items-center justify-center'>
				{/* Decorative outer rings */}
				<div
					className='absolute inset-0 border-4 border-indigo-100 rounded-full animate-ping'
					style={{ animationDuration: "3s" }}></div>
				<div
					className='absolute inset-[-10px] border-2 border-purple-100 rounded-full animate-ping'
					style={{ animationDuration: "2s", animationDelay: "0.5s" }}></div>

				{/* Main spinning element */}
				<div className='w-24 h-24 border-[5px] border-purple-100 border-t-purple-600 rounded-full animate-spin shadow-lg relative z-10'></div>

				{/* Center Icon */}
				<div className='absolute inset-0 z-20 flex items-center justify-center'>
					<FaProjectDiagram className='text-3xl text-purple-600 animate-pulse' />
				</div>
			</div>

			<h3 className='mt-8 text-2xl font-bold text-transparent bg-gradient-to-r from-purple-700 to-indigo-700 bg-clip-text'>
				Mapping Career Ecosystem...
			</h3>
			<p className='mt-2 font-medium tracking-wide text-gray-500'>Analyzing skill vectors & generating pathways</p>

			{/* Skeleton-like decorative nodes */}
			<div className='flex gap-3 mt-8 opacity-70'>
				<div className='w-3 h-3 bg-blue-400 rounded-full animate-bounce' style={{ animationDelay: "0ms" }}></div>
				<div className='w-3 h-3 bg-purple-400 rounded-full animate-bounce' style={{ animationDelay: "150ms" }}></div>
				<div className='w-3 h-3 bg-indigo-400 rounded-full animate-bounce' style={{ animationDelay: "300ms" }}></div>
				<div className='w-3 h-3 bg-pink-400 rounded-full animate-bounce' style={{ animationDelay: "450ms" }}></div>
			</div>
		</div>
	);
}
