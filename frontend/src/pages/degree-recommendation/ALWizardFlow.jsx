import React, { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ProgressStepper from "../../components/degree/ProgressStepper";
import LoadingState from "../../components/degree/LoadingState";
import CourseCard from "../../components/degree/CourseCard";
import StreamSelector from "../../components/degree/al/StreamSelector";
import ZScoreStep from "../../components/degree/al/ZScoreStep";
import InterestsStep from "../../components/degree/al/InterestsStep";
import ALResultsSummary from "../../components/degree/al/ALResultsSummary";
import { AL_STREAMS, getSubjectRuleError } from "../../constants/degreeConstants";
import { fetchDegreeRecommendations } from "../../api/degreeRecommendationApi";

// ── Inline icons ──────────────────────────────────────────────────────────────
const ArrowRightIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2.5' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3' />
	</svg>
);
const ArrowLeftIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2.5' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18' />
	</svg>
);
const SpinnerIcon = () => (
	<svg className='w-4 h-4 animate-spin' fill='none' viewBox='0 0 24 24'>
		<circle className='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' strokeWidth='4' />
		<path
			className='opacity-75'
			fill='currentColor'
			d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
		/>
	</svg>
);
const GraduationIcon = () => (
	<svg className='w-5 h-5' fill='none' stroke='currentColor' strokeWidth='1.8' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5'
		/>
	</svg>
);
const HomeIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25'
		/>
	</svg>
);

const STEPS = ["Stream & District", "Z-Score", "Interests", "Results"];

// ── Scenario detection ────────────────────────────────────────────────────────
function detectScenario(data) {
	const hasStream = data.stream?.trim() !== "";
	const hasZscore = data.zscore !== "" && Number(data.zscore) >= -3 && Number(data.zscore) <= 3;
	const hasInterests = data.interests?.trim().length >= 10;
	const hasSubjects = data.subjects?.length > 0;

	if (hasStream && hasSubjects && hasZscore && hasInterests) return { id: "s5" };
	if (hasStream && hasSubjects && hasInterests && !hasZscore) return { id: "s4" };
	if (hasStream && hasSubjects && hasZscore && !hasInterests) return { id: "s2" };
	if (hasStream && hasSubjects && !hasZscore && !hasInterests) return { id: "s1" };
	return null;
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function ALWizardFlow() {
	const navigate = useNavigate();

	const [currentStep, setCurrentStep] = useState(0);
	const [formData, setFormData] = useState({ stream: "", subjects: [], zscore: "", interests: "", district: "" });
	const [loading, setLoading] = useState(false);
	const [results, setResults] = useState(null);
	const [error, setError] = useState("");

	// Stepper display: while loading show step 3 as active; on results mark all done (step 4)
	const progressDisplayStep =
		loading && currentStep === 2 ? 3
		: currentStep === 3 ? 4
		: currentStep;

	useEffect(() => {
		window.scrollTo({ top: 0, behavior: "smooth" });
	}, [currentStep]);

	// Subject rule validation (memoised)
	const subjectRuleError = useMemo(
		() => getSubjectRuleError(formData.stream, formData.subjects),
		[formData.stream, formData.subjects],
	);

	// Step 0 valid: stream + district + exactly 3 valid subjects
	const isStepValid = useMemo(() => {
		if (currentStep === 0) {
			return Boolean(formData.stream && formData.district && formData.subjects.length === 3 && !subjectRuleError);
		}
		return true;
	}, [currentStep, formData, subjectRuleError]);

	// ── Handlers ────────────────────────────────────────────────────────────────
	const handleNext = () => {
		if (!isStepValid) return;
		if (currentStep === 2) handleSubmit();
		else setCurrentStep((s) => s + 1);
	};

	const handleBack = () => {
		if (currentStep === 0) navigate("/degree-recommendations");
		else if (currentStep === 3) {
			setResults(null);
			setCurrentStep(0);
			window.scrollTo(0, 0);
		} else {
			setCurrentStep((s) => s - 1);
			window.scrollTo(0, 0);
		}
	};

	const handleSubmit = async () => {
		setLoading(true);
		setError("");
		try {
			const scenario = detectScenario(formData);
			const maxResults = scenario?.id === "s1" ? 10 : 5;
			const stream = AL_STREAMS.find((s) => s.name === formData.stream);

			const payload = {
				student: {
					stream: stream?.backendName || formData.stream,
					subjects: formData.subjects.length > 0 ? formData.subjects : ["All"],
					zscore: formData.zscore !== "" ? Number(formData.zscore) : null,
					interests: formData.interests || "General university studies",
				},
				district: formData.district,
				max_results: maxResults,
			};

			const data = await fetchDegreeRecommendations(payload);
			setResults(data);
			setCurrentStep(3);
			window.scrollTo(0, 0);
		} catch (err) {
			let msg = "Failed to fetch recommendations.";
			const detail = err?.response?.data?.detail;
			if (Array.isArray(detail)) msg = detail.map((e) => e.msg || JSON.stringify(e)).join("; ");
			else if (typeof detail === "string") msg = detail;
			else if (detail?.msg) msg = detail.msg;
			setError(msg);
		} finally {
			setLoading(false);
		}
	};

	// ── Step renderer ────────────────────────────────────────────────────────────
	const renderStep = () => {
		if (loading) return <LoadingState />;

		if (currentStep === 0)
			return <StreamSelector formData={formData} setFormData={setFormData} subjectRuleError={subjectRuleError} />;

		if (currentStep === 1)
			return (
				<ZScoreStep zscore={formData.zscore} onChange={(val) => setFormData((prev) => ({ ...prev, zscore: val }))} />
			);

		if (currentStep === 2)
			return (
				<InterestsStep
					interests={formData.interests}
					onChange={(val) => setFormData((prev) => ({ ...prev, interests: val }))}
				/>
			);

		if (currentStep === 3)
			return (
				<div className='max-w-6xl px-6 py-8 mx-auto'>
					<ALResultsSummary formData={formData} />

					{Array.isArray(results) && results.length > 0 ?
						<div className='space-y-4'>
							{/* Results header */}
							<div className='flex items-center gap-3 mb-2'>
								<div className='flex items-center justify-center w-8 h-8 text-white bg-blue-600 shadow-sm rounded-xl'>
									<GraduationIcon />
								</div>
								<h3 className='text-xl font-extrabold text-slate-900'>
									Recommended Degrees <span className='text-base font-semibold text-slate-400'>({results.length})</span>
								</h3>
							</div>
							<div className='grid gap-4'>
								{results
									.sort((a, b) => (b.score || 0) - (a.score || 0))
									.map((course, idx) => (
										<CourseCard key={idx} course={course} isEligible={course.eligibility !== false} />
									))}
							</div>
						</div>
					:	<div className='p-8 text-center border-2 border-blue-100 bg-blue-50/40 rounded-3xl'>
							<p className='text-slate-600'>No recommendations found for your criteria. Try adjusting your inputs.</p>
							<button
								onClick={() => {
									setResults(null);
									setCurrentStep(0);
								}}
								className='inline-flex items-center gap-2 px-5 py-2.5 mt-4 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-colors'>
								<ArrowLeftIcon /> Try Again
							</button>
						</div>
					}

					{/* Footer actions */}
					<div className='flex flex-wrap items-center justify-center gap-4 mt-12'>
						<button
							onClick={() => {
								setResults(null);
								setCurrentStep(0);
							}}
							className='inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold text-blue-700 transition-all border-2 border-blue-200 rounded-2xl bg-blue-50 hover:bg-blue-100 hover:shadow-md'>
							<ArrowLeftIcon /> Search Again
						</button>
						<button
							onClick={() => navigate("/degree-recommendations")}
							className='inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold transition-all bg-white border-2 text-slate-600 border-slate-200 rounded-2xl hover:bg-slate-50 hover:shadow-md'>
							<HomeIcon /> Main Menu
						</button>
					</div>
				</div>
			);
	};

	// ── Render ───────────────────────────────────────────────────────────────────
	return (
		<div className='min-h-screen pb-20 bg-slate-50'>
			{/* ── Hero header ── */}
			<div className='relative pt-24 overflow-hidden border-b pb-28 border-blue-900/30 bg-gradient-to-br from-blue-900 via-indigo-800 to-blue-900'>
				{/* Ambient blobs */}
				<div className='absolute top-0 right-0 w-[500px] h-[500px] bg-cyan-400/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen' />
				<div className='absolute bottom-0 left-10 w-[400px] h-[400px] bg-blue-400/15 rounded-full blur-[100px] pointer-events-none mix-blend-screen' />

				<div className='relative z-10 max-w-6xl px-6 mx-auto mt-4'>
					<div className='inline-flex items-center gap-2 px-4 py-1.5 mb-4 text-xs font-bold tracking-widest uppercase rounded-full bg-blue-500/30 text-blue-200 border border-blue-400/40'>
						<GraduationIcon />
						<span>A/L Degree Finder</span>
					</div>
					<h1 className='mb-3 text-4xl font-extrabold tracking-tight text-white sm:text-5xl'>
						Find Your{" "}
						<span className='text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300'>
							Perfect Degree
						</span>
					</h1>
					<p className='max-w-xl mb-8 text-lg leading-relaxed text-blue-100/80'>
						Fill in your details step by step. Optional fields can be skipped — we'll find the best matches
						automatically.
					</p>
					<ProgressStepper steps={STEPS} currentStep={progressDisplayStep} theme='blue' />
				</div>
			</div>

			{/* ── Main content ── */}
			<div className='relative z-20 max-w-6xl px-6 mx-auto -mt-16'>
				{currentStep < 3 && (
					<div className='p-8 mb-6 bg-white border shadow-2xl sm:p-10 border-blue-100/60 rounded-3xl'>
						{renderStep()}

						{/* Error */}
						{error && (
							<div className='flex gap-3 p-4 mt-6 text-red-700 border border-red-200 rounded-xl bg-red-50'>
								<div>
									<p className='font-bold'>Something went wrong</p>
									<p className='text-sm mt-0.5'>{error}</p>
								</div>
							</div>
						)}

						{/* Navigation */}
						<div className='flex items-center justify-between gap-4 pt-6 mt-8 border-t border-slate-100'>
							<button
								onClick={handleBack}
								className='inline-flex items-center gap-2 px-5 py-2.5 font-semibold text-slate-600 transition-colors bg-white border-2 rounded-xl border-slate-200 hover:bg-slate-50'>
								<ArrowLeftIcon /> Back
							</button>

							<div className='flex gap-3'>
								{/* Skip (optional steps only) */}
								{currentStep > 0 && (
									<button
										onClick={() => {
											if (currentStep === 2) handleSubmit();
											else setCurrentStep((s) => s + 1);
										}}
										className='px-5 py-2.5 font-semibold text-slate-500 transition-colors rounded-xl bg-slate-100 hover:bg-slate-200'>
										Skip Step
									</button>
								)}

								{/* Next / Find */}
								<button
									onClick={handleNext}
									disabled={!isStepValid || loading}
									className={`
										inline-flex items-center gap-2 px-7 py-2.5 rounded-xl font-semibold transition-all duration-300
										${
											isStepValid && !loading ?
												"bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-lg hover:-translate-y-0.5 shadow-blue-500/25 cursor-pointer"
											:	"bg-slate-100 text-slate-400 cursor-not-allowed"
										}
									`}>
									{loading ?
										<>
											<SpinnerIcon /> Processing…
										</>
									: currentStep === 2 ?
										<>
											Find My Degrees <ArrowRightIcon />
										</>
									:	<>
											Next Step <ArrowRightIcon />
										</>
									}
								</button>
							</div>
						</div>
					</div>
				)}

				{currentStep === 3 && !loading && renderStep()}
			</div>
		</div>
	);
}
