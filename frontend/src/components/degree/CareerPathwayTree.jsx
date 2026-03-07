import React from "react";
import {
	FaGraduationCap,
	FaBriefcase,
	FaUniversity,
	FaCheckCircle,
	FaExclamationTriangle,
	FaStar,
	FaArrowDown,
	FaLightbulb,
} from "react-icons/fa";

export default function CareerPathwayTree({ treeData }) {
	if (!treeData || !treeData.pathways) {
		return null;
	}

	const { student_goal, pathways, ai_counselor_advice, total_streams, total_degrees } = treeData;

	// Color schemes for readiness status
	const getReadinessStyle = (status) => {
		switch (status) {
			case "excellent":
				return {
					border: "border-emerald-400",
					bg: "from-emerald-50 to-teal-50",
					badge: "bg-emerald-100 text-emerald-800 border-emerald-300",
					icon: "text-emerald-600",
					glow: "shadow-emerald-100",
				};
			case "good":
				return {
					border: "border-blue-400",
					bg: "from-blue-50 to-cyan-50",
					badge: "bg-blue-100 text-blue-800 border-blue-300",
					icon: "text-blue-600",
					glow: "shadow-blue-200",
				};
			case "needs_improvement":
				return {
					border: "border-amber-400",
					bg: "from-amber-50 to-orange-50",
					badge: "bg-amber-100 text-amber-800 border-amber-300",
					icon: "text-amber-600",
					glow: "shadow-amber-100",
				};
			default:
				return {
					border: "border-gray-300",
					bg: "from-gray-50 to-slate-50",
					badge: "bg-gray-100 text-gray-800 border-gray-300",
					icon: "text-gray-600",
					glow: "shadow-gray-200",
				};
		}
	};

	const getReadinessIcon = (status) => {
		if (status === "excellent" || status === "good") {
			return <FaCheckCircle className='text-lg' />;
		}
		return <FaExclamationTriangle className='text-lg' />;
	};

	return (
		<div className='space-y-12'>
			{/* The Root - Student's Goal */}
			<div className='flex flex-col items-center'>
				<div className='relative w-full max-w-2xl'>
					{/* Animated gradient glow background */}
					<div className='absolute inset-0 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 rounded-3xl blur-xl opacity-20 animate-pulse'></div>

					<div className='relative p-8 text-center border-4 border-purple-300 shadow-2xl bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 rounded-3xl'>
						<div className='flex items-center justify-center gap-3 mb-4'>
							<div className='p-3 shadow-lg bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl'>
								<FaLightbulb className='text-2xl text-white' />
							</div>
							<h2 className='text-2xl font-black text-transparent uppercase md:text-3xl bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600'>
								Your Career Goal
							</h2>
						</div>

						<p className='text-lg font-bold leading-relaxed md:text-xl text-slate-800'>{student_goal}</p>

						<div className='flex flex-wrap items-center justify-center gap-4 mt-6'>
							<div className='flex items-center gap-2 px-4 py-2 border-2 border-purple-200 rounded-full bg-white/50'>
								<FaStar className='text-purple-500' />
								<span className='text-sm font-bold text-purple-700'>{total_streams} Potential Streams</span>
							</div>
							<div className='flex items-center gap-2 px-4 py-2 border-2 border-pink-200 rounded-full bg-white/50'>
								<FaGraduationCap className='text-pink-500' />
								<span className='text-sm font-bold text-pink-700'>{total_degrees} Degree Options</span>
							</div>
						</div>
					</div>
				</div>

				{/* Connecting Line */}
				<div className='relative flex items-center justify-center w-full h-16'>
					<div className='absolute w-1 h-full rounded-full bg-gradient-to-b from-purple-400 to-blue-400 animate-pulse'></div>
					<FaArrowDown className='relative z-10 p-2 text-2xl text-white rounded-full shadow-lg bg-gradient-to-br from-purple-500 to-blue-500' />
				</div>
			</div>

			{/* The Branches - Stream Pathways */}
			<div className='grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3'>
				{pathways.map((pathway, idx) => {
					const styles = getReadinessStyle(pathway.readiness_status);

					return (
						<div
							key={idx}
							className={`relative flex flex-col h-full overflow-hidden border transition-all duration-300  shadow-xl bg-gradient-to-br ${styles.bg} ${styles.border} ${styles.glow} rounded-3xl hover:shadow-2xl hover:-translate-y-2`}>
							{/* Top accent bar with match score */}
							<div className='relative h-2 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400'></div>

							<div className='flex flex-col flex-1 p-6'>
								{/* Stream Header */}
								<div className='mb-4'>
									<div className='flex items-start justify-between gap-3 mb-3'>
										<h3 className='flex-1 text-2xl font-black leading-tight text-slate-900'>{pathway.stream_name}</h3>
										<div className='flex-shrink-0 px-3 py-1 text-xl font-black text-purple-700 bg-purple-100 border-2 border-purple-300 rounded-xl'>
											{pathway.match_score.toFixed(0)}%
										</div>
									</div>

									{/* O/L Readiness Badge */}
									<div
										className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-bold border-2 rounded-xl ${styles.badge}`}>
										<span className={styles.icon}>{getReadinessIcon(pathway.readiness_status)}</span>
										<span>{pathway.ol_readiness}</span>
									</div>
								</div>

								{/* Potential Degrees */}
								<div className='mb-4'>
									<p className='flex items-center gap-2 mb-3 text-xs font-black tracking-wider uppercase text-slate-600'>
										<FaGraduationCap className='text-base' />
										Potential Degrees
									</p>
									<div className='space-y-2'>
										{pathway.potential_degrees.map((degree, degIdx) => (
											<div
												key={degIdx}
												className='p-3 transition-all duration-200 bg-white border-2 shadow-sm border-slate-200 rounded-xl hover:shadow-md hover:border-purple-300'>
												<div className='flex items-start justify-between gap-2 mb-2'>
													<h4 className='flex-1 text-sm font-bold leading-tight text-slate-800'>
														{degree.course_name}
													</h4>
													<span className='flex-shrink-0 px-2 py-1 text-xs font-bold text-purple-700 bg-purple-100 rounded-lg'>
														{degree.match_score_percentage.toFixed(0)}%
													</span>
												</div>
												{degree.universities && degree.universities.length > 0 && (
													<div className='flex flex-wrap gap-1.5 mt-2'>
														{degree.universities.slice(0, 3).map((uni, uniIdx) => (
															<span
																key={uniIdx}
																className='inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold border rounded-lg bg-slate-50 text-slate-600 border-slate-200'>
																<FaUniversity className='text-xs' />
																{uni}
															</span>
														))}
													</div>
												)}
											</div>
										))}
									</div>
								</div>

								{/* Target Careers */}
								<div className='mt-auto'>
									<p className='flex items-center gap-2 mb-3 text-xs font-black tracking-wider uppercase text-slate-600'>
										<FaBriefcase className='text-base' />
										Target Careers
									</p>
									<div className='flex flex-wrap gap-2'>
										{pathway.target_careers.map((career, carIdx) => (
											<span
												key={carIdx}
												className='inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-white transition-all duration-200 shadow-sm bg-gradient-to-r from-purple-500 to-blue-500 rounded-full hover:shadow-md hover:scale-105'>
												<FaBriefcase className='text-xs' />
												{career}
											</span>
										))}
									</div>
								</div>
							</div>
						</div>
					);
				})}
			</div>

			{/* AI Counselor Advice */}
			<div className='relative p-8 overflow-hidden border-4 border-indigo-300 shadow-2xl bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-3xl'>
				{/* Decorative elements */}
				<div className='absolute w-32 h-32 bg-purple-300 rounded-full -top-10 -right-10 opacity-20 blur-3xl'></div>
				<div className='absolute w-32 h-32 bg-pink-300 rounded-full -bottom-10 -left-10 opacity-20 blur-3xl'></div>

				<div className='relative flex items-start gap-4'>
					<div className='flex-shrink-0 p-4 shadow-lg bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl'>
						<FaLightbulb className='text-3xl text-white' />
					</div>

					<div className='flex-1'>
						<h3 className='mb-3 text-2xl font-black text-transparent uppercase bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600'>
							💡 Your Personal Counselor's Advice
						</h3>
						<p
							className='text-base font-medium leading-relaxed md:text-lg text-slate-800'
							dangerouslySetInnerHTML={{ __html: ai_counselor_advice }}></p>
					</div>
				</div>
			</div>

			{/* Next Steps Footer */}
			<div className='p-6 border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl'>
				<div className='flex gap-4'>
					<div className='text-4xl'>🎯</div>
					<div>
						<h3 className='mb-2 text-lg font-bold text-gray-900'>What's Next?</h3>
						<p className='text-sm leading-relaxed text-gray-700'>
							Ready to dive deeper? Once you choose your A/L stream, come back and use the "A/L Students" flow to
							explore detailed eligibility requirements, z-score cutoffs, and specific university programs. Make sure to
							attend university open days and talk to current students in your chosen field!
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
