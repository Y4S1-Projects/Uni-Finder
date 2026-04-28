import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import CareerPathwayTree from "../../components/degree/CareerPathwayTree";

// Inline SVG Icons
const ArrowLeftIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18' />
	</svg>
);

const SparklesIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09l2.846.813-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z'
		/>
	</svg>
);

const UserIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z'
		/>
	</svg>
);

const ClipboardIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z'
		/>
	</svg>
);

const RefreshIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99'
		/>
	</svg>
);

export default function OLResultsPage() {
	const navigate = useNavigate();
	const location = useLocation();
	const { results, interests, olMarks } = location.state || {};

	// If no results (e.g. direct navigation), redirect back
	if (!results) {
		navigate("/degree-recommendations/all-students");
		return null;
	}

	// Build a readable list of O/L marks if provided
	const hasMarks =
		olMarks &&
		(Object.values(olMarks.core || {}).some((v) => v !== "") ||
			olMarks.bucket_1 ||
			olMarks.bucket_2 ||
			olMarks.bucket_3);

	const coreSubjectKeys = ["religion", "first_language", "mathematics", "science", "english", "history"];
	const coreLabels = {
		religion: "Religion",
		first_language: "First Language",
		mathematics: "Mathematics",
		science: "Science",
		english: "English",
		history: "History",
	};

	// Core marks: only the 6 defined subjects with a value
	const coreMarks = coreSubjectKeys
		.filter((k) => olMarks?.core?.[k])
		.map((k) => ({ label: coreLabels[k], grade: olMarks.core[k] }));

	// Optional subjects: pair bucket name + grade from core
	const optionals = [1, 2, 3]
		.map((n) => ({
			subject: olMarks?.[`bucket_${n}`],
			grade: olMarks?.core?.[`bucket_${n}_grade`] || olMarks?.[`bucket_${n}_grade`],
		}))
		.filter((o) => o.subject);

	return (
		<div className='min-h-screen pb-20 bg-slate-50'>
			{/* Hero Header */}
			<div className='relative pt-24 overflow-hidden border-b pb-28 border-green-900/40 bg-gradient-to-br from-teal-900 via-emerald-800 to-teal-900'>
				{/* Ambient Blobs */}
				<div className='absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen' />
				<div className='absolute bottom-0 left-10 w-[400px] h-[400px] bg-teal-400/15 rounded-full blur-[100px] pointer-events-none mix-blend-screen' />

				<div className='relative z-10 max-w-5xl px-6 mx-auto mt-4'>
					<h1 className='mb-4 text-4xl font-extrabold tracking-tight text-white sm:text-5xl'>
						Your Career{" "}
						<span className='text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 to-teal-300'>
							Pathway Map
						</span>
					</h1>
					<p className='max-w-xl text-lg leading-relaxed text-emerald-50/80'>
						We've discovered A/L streams perfectly matched to your interests and mapped out your ideal degree pathways.
					</p>
				</div>
			</div>

			{/* Main Content */}
			<div className='relative z-20 px-6 mx-auto -mt-16 max-w-7xl'>
				{/* User Input Summary Card */}
				<div className='p-6 mb-8 bg-white border border-green-100 shadow-xl rounded-3xl'>
					<div className='flex flex-wrap items-start gap-8'>
						{/* Interests */}
						<div className='flex-1 min-w-[200px]'>
							<div className='flex items-center gap-2 mb-2'>
								<div className='p-1.5 rounded-lg bg-emerald-100 text-emerald-700'>
									<UserIcon />
								</div>
								<p className='text-xs font-bold tracking-widest uppercase text-emerald-700'>Your Interests</p>
							</div>
							<p className='text-sm italic leading-relaxed text-slate-700'>"{interests}"</p>
						</div>

						{/* O/L Marks — only if provided */}
						{hasMarks && (
							<div className='flex-1 min-w-[260px]'>
								<div className='flex items-center gap-2 mb-3'>
									<div className='p-1.5 rounded-lg bg-emerald-100 text-emerald-700'>
										<ClipboardIcon />
									</div>
									<p className='text-xs font-bold tracking-widest uppercase text-emerald-700'>O/L Results</p>
								</div>

								{/* Core Subjects */}
								{coreMarks.length > 0 && (
									<div className='mb-3'>
										<p className='mb-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider'>
											Core Subjects
										</p>
										<div className='flex flex-wrap gap-1.5'>
											{coreMarks.map(({ label, grade }) => (
												<span
													key={label}
													className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200'>
													{label}:
													<span className='px-1.5 py-0.5 font-extrabold text-white bg-emerald-600 rounded-md'>
														{grade}
													</span>
												</span>
											))}
										</div>
									</div>
								)}

								{/* Optional Subjects */}
								{optionals.length > 0 && (
									<div>
										<p className='mb-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider'>
											Optional Subjects
										</p>
										<div className='flex flex-wrap gap-1.5'>
											{optionals.map(({ subject, grade }, i) => (
												<span
													key={i}
													className='inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg bg-teal-50 text-teal-800 border border-teal-200 capitalize'>
													{subject}
													{grade && (
														<span className='px-1.5 py-0.5 font-extrabold text-white bg-teal-600 rounded-md'>
															{grade}
														</span>
													)}
												</span>
											))}
										</div>
									</div>
								)}
							</div>
						)}

						{/* Quick action */}
						<div className='flex-shrink-0'>
							<button
								onClick={() => navigate("/degree-recommendations/all-students")}
								className='inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold transition-all border text-emerald-700 border-emerald-200 rounded-xl bg-emerald-50 hover:bg-emerald-100 hover:shadow-md'>
								<RefreshIcon /> Try Again
							</button>
						</div>
					</div>
				</div>

				{/* Career Tree Visualization */}
				<CareerPathwayTree treeData={results} />

				{/* Single Footer Action Row */}
				<div className='flex flex-wrap items-center justify-center gap-4 mt-16'>
					<button
						onClick={() => navigate("/degree-recommendations/all-students")}
						className='inline-flex items-center gap-2 px-8 py-3.5 font-semibold transition-all bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl hover:shadow-lg hover:-translate-y-0.5 shadow-emerald-500/25'>
						<RefreshIcon /> Explore Again
					</button>
					<button
						onClick={() => navigate("/degree-recommendations")}
						className='inline-flex items-center gap-2 px-6 py-3.5 font-medium transition-colors bg-white border shadow-sm rounded-xl text-slate-600 border-slate-200 hover:bg-slate-50'>
						<ArrowLeftIcon /> Back to Main Menu
					</button>
				</div>
			</div>
		</div>
	);
}
