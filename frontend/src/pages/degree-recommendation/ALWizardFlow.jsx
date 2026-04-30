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
import {
	ArrowRightIcon,
	ArrowLeftIcon,
	SpinnerIcon,
	GraduationIcon,
	RefreshIcon,
} from "../../components/ui/DegreeIcons";

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
			const maxResults = scenario?.id === "s1" ? 10 : 100;
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
				<div className='max-w-6xl px-6 py-8 mx-auto space-y-8'>
					{/* Profile summary */}
					<ALResultsSummary formData={formData} />

					{Array.isArray(results) && results.length > 0 ?
						<>
							{/* Results banner */}
							<div className='relative p-6 overflow-hidden border border-blue-200 shadow-lg bg-gradient-to-br from-blue-700 to-indigo-700 rounded-3xl'>
								<div className='absolute top-0 right-0 w-48 h-48 rounded-full pointer-events-none bg-cyan-400/20 blur-3xl' />
								<div className='absolute bottom-0 left-0 w-32 h-32 rounded-full pointer-events-none bg-indigo-400/20 blur-3xl' />
								<div className='relative z-10 flex flex-wrap items-center gap-4'>
									<div className='flex items-center justify-center w-12 h-12 text-blue-700 bg-white shadow-md rounded-2xl'>
										<GraduationIcon className='w-7 h-7' />
									</div>
									<div>
										<p className='text-xs font-bold tracking-widest uppercase text-blue-200 mb-0.5'>Results Ready</p>
										<h3 className='text-2xl font-extrabold text-white'>
											{results.length} Degree{results.length !== 1 ? "s" : ""} Found
										</h3>
									</div>
									{formData.stream && (
										<div className='flex-shrink-0 px-4 py-2 ml-auto text-sm font-semibold text-white border rounded-2xl bg-white/15 border-white/25'>
											{formData.stream}
										</div>
									)}
								</div>
							</div>

							{/* Degree list */}
							<div className='flex flex-col gap-4'>
								{results
									.sort((a, b) => (b.score || 0) - (a.score || 0))
									.map((course, idx) => (
										<CourseCard key={idx} course={course} isEligible={course.eligibility !== false} />
									))}
							</div>
						</>
					:	/* Empty state */
						<div className='flex flex-col items-center py-16 text-center border-2 border-blue-200 border-dashed bg-blue-50/40 rounded-3xl'>
							<div className='flex items-center justify-center w-16 h-16 mb-4 text-blue-400 bg-blue-100 rounded-2xl'>
								<GraduationIcon />
							</div>
							<h4 className='mb-2 text-lg font-bold text-slate-800'>No Results Found</h4>
							<p className='max-w-sm mb-6 text-sm text-slate-500'>
								We couldn't find any degrees matching your criteria. Try adjusting your stream, subjects, or Z-score.
							</p>
							<button
								onClick={() => {
									setResults(null);
									setCurrentStep(0);
								}}
								className='inline-flex items-center gap-2 px-6 py-3 text-sm font-bold text-white transition-all bg-blue-600 rounded-2xl hover:bg-blue-700 hover:shadow-lg'>
								<ArrowLeftIcon /> Try Again
							</button>
						</div>
					}

					{/* Footer actions */}
					<div className='flex flex-wrap items-center justify-center gap-4 pt-6 border-t border-slate-100'>
						<button
							onClick={() => {
								setResults(null);
								setCurrentStep(0);
							}}
							className='inline-flex items-center gap-2 px-6 py-3 text-sm font-bold text-blue-700 transition-all border-2 border-blue-200 rounded-2xl bg-blue-50 hover:bg-blue-100 hover:shadow-md'>
							<RefreshIcon className='w-5 h-5' /> Search Again
						</button>
						<button
							onClick={() => navigate("/degree-recommendations")}
							className='inline-flex items-center gap-2 px-6 py-3 text-sm font-bold transition-all bg-white border-2 text-slate-600 border-slate-200 rounded-2xl hover:bg-slate-50 hover:shadow-md'>
							<ArrowLeftIcon className='w-5 h-5' /> Main Menu
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

				<div className='relative z-10 max-w-6xl px-6 mx-auto'>
					<div className='inline-flex items-center gap-2 px-4 py-1.5 mb-4 text-xs font-bold tracking-widest uppercase rounded-full bg-blue-500/30 text-blue-200 border border-blue-400/40'>
						<GraduationIcon className='w-5 h-5' />
						<span>A/L Degree Finder</span>
					</div>

					<h1 className='mb-3 text-4xl font-extrabold tracking-tight text-white sm:text-5xl'>
						Find Your{" "}
						<span className='text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300'>
							Perfect Degree
						</span>
					</h1>
					<p className='max-w-xl mb-8 text-lg leading-relaxed text-blue-100/80'>
						Fill in your details step by step. Optional fields can be skipped, We'll find the best matches
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
										Skip
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
											Find My Degrees <ArrowRightIcon className='w-5 h-5' />
										</>
									:	<>
											Next <ArrowRightIcon className='w-5 h-5' />
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
