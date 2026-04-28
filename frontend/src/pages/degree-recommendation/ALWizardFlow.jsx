import React, { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ProgressStepper from "../../components/degree/ProgressStepper";
import LoadingState from "../../components/degree/LoadingState";
import CourseCard from "../../components/degree/CourseCard";
import { fetchDegreeRecommendations } from "../../api/degreeRecommendationApi";

// Inline SVG Icons
const ArrowRightIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3' />
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
const MapPinIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z' />
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z'
		/>
	</svg>
);

// Sri Lanka A/L Streams & subject rules (UGC-style flexible combinations)
const ALABAMA_STREAMS = [
	{
		id: "physical-science",
		name: "Physical Science",
		backendName: "Physical Science",
		icon: "⚛️",
		color: "from-blue-400 to-blue-600",
		availableSubjects: [
			"Combined Mathematics",
			"Physics",
			"Chemistry",
			"Information & Communication Technology",
			"Higher Mathematics",
		],
	},
	{
		id: "biological-science",
		name: "Biological Science",
		backendName: "Biological Science",
		icon: "🔬",
		color: "from-green-400 to-green-600",
		availableSubjects: [
			"Biology",
			"Chemistry",
			"Physics",
			"Agricultural Science",
			"Information & Communication Technology",
		],
	},
	{
		id: "commerce",
		name: "Commerce",
		backendName: "Commerce",
		icon: "💼",
		color: "from-purple-400 to-purple-600",
		availableSubjects: [
			"Accounting",
			"Business Studies",
			"Economics",
			"Business Statistics",
			"Geography",
			"Political Science",
			"History",
			"Logic & Scientific Method",
			"English",
			"Information & Communication Technology",
			"Agricultural Science",
			"Combined Mathematics",
			"Physics",
			"French",
			"German",
		],
	},
	{
		id: "engineering-technology",
		name: "Engineering Technology",
		backendName: "Engineering Technology",
		icon: "🛠️",
		color: "from-cyan-400 to-cyan-600",
		availableSubjects: [
			"Engineering Technology",
			"Science for Technology",
			"Information & Communication Technology",
			"Economics",
			"Geography",
			"Home Economics",
			"English",
			"Communication & Media Studies",
			"Art",
			"Business Studies",
			"Accounting",
			"Mathematics",
			"Agricultural Science",
		],
	},
	{
		id: "bio-systems-technology",
		name: "Bio-Systems Technology",
		backendName: "Bio-Systems Technology",
		icon: "🌱",
		color: "from-teal-400 to-emerald-600",
		availableSubjects: [
			"Bio-Systems Technology",
			"Science for Technology",
			"Information & Communication Technology",
			"Economics",
			"Geography",
			"Home Economics",
			"English",
			"Communication & Media Studies",
			"Art",
			"Business Studies",
			"Accounting",
			"Mathematics",
			"Agricultural Science",
		],
	},
	{
		id: "arts",
		name: "Arts",
		backendName: "Arts",
		icon: "🎨",
		color: "from-pink-400 to-pink-600",
		availableSubjects: [
			"Economics",
			"Geography",
			"History",
			"Accounting",
			"Business Statistics",
			"Political Science",
			"Logic & Scientific Method",
			"Home Economics",
			"Communication & Media Studies",
			"Information & Communication Technology",
			"Agricultural Science",
			"Combined Mathematics",
			"Higher Mathematics",
			"Buddhism",
			"Hinduism",
			"Christianity",
			"Islam",
			"Islamic Civilization",
			"Greek & Roman Civilization",
			"Art",
			"Dance",
			"Music",
			"Drama",
			"Sinhala",
			"Tamil",
			"English",
			"Arabic",
			"Pali",
			"Sanskrit",
			"French",
			"German",
			"Russian",
			"Japanese",
			"Chinese",
			"Hindi",
			"Civil Tech",
			"Mechanical Tech",
			"Electrical/Electronic Tech",
			"Food Tech",
			"Agro Tech",
			"Bio-Resource Tech",
		],
	},
];

const SRI_LANKAN_DISTRICTS = [
	"Colombo",
	"Gampaha",
	"Kalutara",
	"Matara",
	"Galle",
	"Hambantota",
	"Jaffna",
	"Mullaitivu",
	"Batticaloa",
	"Ampara",
	"Trincomalee",
	"Kurunegala",
	"Puttalum",
	"Anuradhapura",
	"Polonnaruwa",
	"Matale",
	"Kandy",
	"Nuwara Eliya",
	"Badulla",
	"Monaragala",
	"Ratnapura",
	"Kegalle",
];

export default function ALWizardFlow() {
	const navigate = useNavigate();
	const [currentStep, setCurrentStep] = useState(0); // 0: Stream, 1: Z-Score (optional), 2: Interests (optional), 3: Results
	const [formData, setFormData] = useState({
		stream: "",
		subjects: [],
		zscore: "",
		interests: "",
		district: "",
	});
	const [loading, setLoading] = useState(false);
	const [results, setResults] = useState(null);
	const [error, setError] = useState("");

	// Stepper display state:
	// - While submitting from step 3, show Results step as active.
	// - Once results are shown, mark all steps as completed (show check on step 4).
	const progressDisplayStep =
		loading && currentStep === 2 ? 3
		: currentStep === 3 ? 4
		: currentStep;

	// Scroll to top whenever step changes
	useEffect(() => {
		window.scrollTo({ top: 0, behavior: "smooth" });
	}, [currentStep]);

	// Auto-detect scenario based on provided inputs
	// Now that Z-Score is optional, all 4 scenarios are viable
	const detectScenario = (data) => {
		const hasStream = data.stream && data.stream.trim() !== "";
		const hasZscore = data.zscore && data.zscore !== "" && Number(data.zscore) >= -3 && Number(data.zscore) <= 3;
		const hasInterests = data.interests && data.interests.trim().length >= 10;
		const hasSubjects = data.subjects && data.subjects.length > 0;

		// Scenario 5: Stream + Subjects + Z-Score + Interests (Full Profile)
		if (hasStream && hasSubjects && hasZscore && hasInterests) {
			return {
				id: "s5",
				name: "Full Profile Matching (S5)",
				description: "Stream + Subjects + Z-Score + Interests - AI ranks courses by eligibility and interest",
			};
		}
		// Scenario 4: Stream + Subjects + Interests (No Z-Score) - Now viable!
		if (hasStream && hasSubjects && hasInterests && !hasZscore) {
			return {
				id: "s4",
				name: "Interest-Based Recommendations (S4)",
				description: "Stream + Subjects + Interests - All eligible courses ranked by interest match",
			};
		}
		// Scenario 2: Stream + Subjects + Z-Score (No Interests)
		if (hasStream && hasSubjects && hasZscore && !hasInterests) {
			return {
				id: "s2",
				name: "Z-Score Filtered Recommendations (S2)",
				description: "Stream + Subjects + Z-Score - Courses you're eligible for based on Z-Score",
			};
		}
		// Scenario 1: Stream + Subjects only (No Z-Score, No Interests) - Now viable!
		if (hasStream && hasSubjects && !hasZscore && !hasInterests) {
			return {
				id: "s1",
				name: "Stream Overview (S1)",
				description: "Stream + Subjects - All courses available in your stream",
			};
		}

		return null;
	};

	// Get available subjects for selected stream
	const selectedStream = useMemo(() => {
		return ALABAMA_STREAMS.find((s) => s.name === formData.stream);
	}, [formData.stream]);

	const getSubjectRuleError = (streamName, subjects) => {
		if (!streamName || subjects.length !== 3) return "";

		const set = new Set(subjects);
		const has = (subject) => set.has(subject);
		const countIn = (pool) => subjects.filter((subject) => pool.includes(subject)).length;

		if (streamName === "Physical Science") {
			if (!has("Combined Mathematics") || !has("Physics")) {
				return "Physical Science requires Combined Mathematics and Physics as compulsory subjects.";
			}
			const optionals = ["Chemistry", "Information & Communication Technology", "Higher Mathematics"];
			if (countIn(optionals) !== 1) {
				return "Physical Science requires exactly one optional subject: Chemistry, ICT, or Higher Mathematics.";
			}
		}

		if (streamName === "Biological Science") {
			if (!has("Biology") || !has("Chemistry")) {
				return "Biological Science requires Biology and Chemistry as compulsory subjects.";
			}
			const optionals = ["Physics", "Agricultural Science", "Information & Communication Technology"];
			if (countIn(optionals) !== 1) {
				return "Biological Science requires exactly one optional subject: Physics, Agricultural Science, or ICT.";
			}
		}

		if (streamName === "Commerce") {
			const standard = ["Accounting", "Business Studies", "Economics"];
			if (countIn(standard) < 2) {
				return "Commerce requires at least two of Accounting, Business Studies, and Economics.";
			}
		}

		if (streamName === "Engineering Technology") {
			if (!has("Engineering Technology") || !has("Science for Technology")) {
				return "Engineering Technology stream requires Engineering Technology and Science for Technology.";
			}
		}

		if (streamName === "Bio-Systems Technology") {
			if (!has("Bio-Systems Technology") || !has("Science for Technology")) {
				return "Bio-Systems Technology stream requires Bio-Systems Technology and Science for Technology.";
			}
		}

		if (streamName === "Arts") {
			const artsTech = [
				"Civil Tech",
				"Mechanical Tech",
				"Electrical/Electronic Tech",
				"Food Tech",
				"Agro Tech",
				"Bio-Resource Tech",
			];
			if (countIn(artsTech) > 1) {
				return "Arts allows a maximum of one technological subject.";
			}
		}

		return "";
	};

	const subjectRuleError = useMemo(
		() => getSubjectRuleError(formData.stream, formData.subjects),
		[formData.stream, formData.subjects],
	);

	// Validation - stream, district, exactly 3 subjects, and valid subject-rule combination required
	const isStepValid = useMemo(() => {
		if (currentStep === 0) {
			return Boolean(formData.stream && formData.district && formData.subjects.length === 3 && !subjectRuleError);
		}
		return true;
	}, [currentStep, formData, subjectRuleError]);

	const handleStreamSelect = (streamId) => {
		const stream = ALABAMA_STREAMS.find((s) => s.id === streamId);
		setFormData({
			...formData,
			stream: stream.name,
		});
	};

	const handleNext = () => {
		if (!isStepValid) return;

		if (currentStep === 2) {
			// Final step - submit form
			handleSubmit();
		} else {
			setCurrentStep(currentStep + 1);
		}
	};

	const handleBack = () => {
		if (currentStep === 0) {
			navigate("/degree-recommendations");
		} else if (currentStep === 3) {
			// From results, go back to step 0
			setResults(null);
			setCurrentStep(0);
			window.scrollTo(0, 0);
		} else {
			setCurrentStep(currentStep - 1);
			window.scrollTo(0, 0);
		}
	};

	const handleSubmit = async () => {
		setLoading(true);
		setError("");

		try {
			// Detect which scenario applies based on inputs
			const scenario = detectScenario(formData);

			const maxResults = scenario?.id === "s1" ? 10 : 5;
			const stream = ALABAMA_STREAMS.find((s) => s.name === formData.stream);

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
			setCurrentStep(3); // Go to results step
			window.scrollTo(0, 0);
			setLoading(false);
		} catch (err) {
			let errorMessage = "Failed to fetch recommendations.";

			if (err?.response?.data?.detail) {
				const detail = err.response.data.detail;
				// Handle Pydantic validation errors (array of error objects)
				if (Array.isArray(detail)) {
					errorMessage = detail.map((e) => e.msg || JSON.stringify(e)).join("; ");
				} else if (typeof detail === "string") {
					errorMessage = detail;
				} else if (detail.msg) {
					errorMessage = detail.msg;
				}
			}

			setError(errorMessage);
			setLoading(false);
		}
	};

	// Render different steps
	const renderStep = () => {
		if (loading) {
			return <LoadingState />;
		}

		if (currentStep === 0) {
			// Stream & District Selection
			return (
				<div className='space-y-5'>
					<div>
						<h2 className='flex items-center gap-2 mb-2 text-2xl font-bold text-gray-900'>What's Your A/L Stream?</h2>
						<p className='text-gray-600'>Select the stream you're currently studying or plan to study.</p>
					</div>

					{/* Stream Grid */}
					<div className='grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3'>
						{ALABAMA_STREAMS.map((stream) => (
							<button
								key={stream.id}
								onClick={() => handleStreamSelect(stream.id)}
								className={`
									relative p-4 rounded-xl border transition-all duration-300 text-left
									${
										formData.stream === stream.name ?
											`border-indigo-500 bg-gradient-to-br from-indigo-50 to-violet-50 shadow-lg`
										:	`border-gray-200 bg-white hover:border-indigo-300 hover:shadow-md`
									}
								`}>
								<div className='flex items-center gap-2'>
									<div
										className={`inline-flex items-center justify-center text-xl p-1.5 rounded-md bg-gradient-to-br ${stream.color}`}>
										{stream.icon}
									</div>
									<h3 className='ml-4 text-sm font-semibold leading-tight text-gray-900'>{stream.name}</h3>
								</div>
								{formData.stream === stream.name && (
									<div className='absolute flex items-center justify-center w-5 h-5 text-xs font-bold text-white rounded-full top-2 right-2 bg-gradient-to-r from-indigo-500 to-violet-500'>
										✓
									</div>
								)}
							</button>
						))}
					</div>

					{/* Subject Selection - Shows after stream is selected */}
					{formData.stream && selectedStream && (
						<div className='mt-4 border-t-2 border-gray-200 '>
							<div className='mb-2'>
								<div className='flex items-center justify-between'>
									<div>
										<h3 className='flex items-center gap-2 mb-1 text-lg font-bold text-gray-900'>
											Select Your 3 Subjects
										</h3>
										<p className='text-xs text-gray-600'>
											Choose exactly 3 subjects from the {selectedStream.name} stream
										</p>
									</div>
									<div
										className={`text-lg font-bold px-3 py-1.5 rounded-lg ${
											formData.subjects.length === 3 ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
										}`}>
										{formData.subjects.length}/3
									</div>
								</div>
							</div>

							{/* Subject Selector Grid */}
							<div className='grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3'>
								{selectedStream.availableSubjects.map((subject) => (
									<button
										key={subject}
										onClick={() => {
											if (formData.subjects.includes(subject)) {
												// Deselect
												setFormData({
													...formData,
													subjects: formData.subjects.filter((s) => s !== subject),
												});
											} else if (formData.subjects.length < 3) {
												// Select if less than 3
												setFormData({
													...formData,
													subjects: [...formData.subjects, subject],
												});
											}
										}}
										className={`
											p-2.5 rounded-lg  border transition-all duration-200 text-left font-semibold text-xs
											${
												formData.subjects.includes(subject) ?
													"border-indigo-500 bg-gradient-to-r from-indigo-50 to-violet-50 text-indigo-900 shadow-md"
												: formData.subjects.length >= 3 ?
													"border-gray-200 bg-gray-50 text-gray-600 cursor-not-allowed opacity-50"
												:	"border-gray-300 bg-white text-gray-900 hover:border-indigo-400 hover:bg-indigo-50 cursor-pointer"
											}
										`}
										disabled={formData.subjects.length >= 3 && !formData.subjects.includes(subject)}>
										<div className='flex items-center gap-2'>
											<div
												className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
													formData.subjects.includes(subject) ? "border-indigo-500 bg-indigo-500" : "border-gray-300"
												}`}>
												{formData.subjects.includes(subject) && <span className='text-xs text-white'>✓</span>}
											</div>
											<span className='leading-tight'>{subject}</span>
										</div>
									</button>
								))}
							</div>

							{/* Validation Messages */}
							{formData.subjects.length < 3 && (
								<div className='px-3 pt-3 mt-3 border border-yellow-200 rounded-lg bg-yellow-50'>
									<p className='text-xs text-yellow-800'>
										<strong>
											⚠️ Select {3 - formData.subjects.length} more subject
											{3 - formData.subjects.length !== 1 ? "s" : ""}
										</strong>{" "}
										to continue. You must select exactly 3 subjects.
									</p>
								</div>
							)}

							{formData.subjects.length === 3 && !subjectRuleError && (
								<div className='px-3 pt-3 mt-3 border border-green-200 rounded-lg bg-green-50'>
									<p className='text-xs text-green-800'>
										<strong>✓ Perfect!</strong> You've selected a valid 3-subject combination:{" "}
										<span className='font-semibold'>{formData.subjects.join(", ")}</span>
									</p>
								</div>
							)}

							{formData.subjects.length === 3 && subjectRuleError && (
								<div className='px-3 pt-3 mt-3 border border-red-200 rounded-lg bg-red-50'>
									<p className='text-xs text-red-800'>
										<strong>⚠ Invalid combination:</strong> {subjectRuleError}
									</p>
								</div>
							)}
						</div>
					)}

					{/* District Selection */}
					<div>
						<label className='block mb-3 text-sm font-bold text-gray-900'>
							<MapPinIcon className='inline mr-2' /> District of Residence
						</label>
						<select
							value={formData.district}
							onChange={(e) => setFormData({ ...formData, district: e.target.value })}
							className='w-full px-4 py-3 transition-colors border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none'>
							<option value=''>Select your district...</option>
							{SRI_LANKAN_DISTRICTS.map((district) => (
								<option key={district} value={district}>
									{district}
								</option>
							))}
						</select>
					</div>
				</div>
			);
		}

		if (currentStep === 1) {
			// Z-Score Step (Optional)
			return (
				<div className='space-y-6'>
					<div>
						<h2 className='flex items-center gap-2 mb-2 text-2xl font-bold text-gray-900'>
							Enter Your Z-Score <span className='text-sm font-normal text-gray-500'>(Optional)</span>
						</h2>
						<p className='text-gray-600'>
							Have your A/L results? Enter your Z-score to see courses you're eligible for. Or skip to view all courses
							in your stream.
						</p>
					</div>

					<div>
						<label className='block mb-2 text-sm font-bold text-gray-900'>Z-Score</label>
						<input
							type='number'
							step='0.01'
							placeholder='e.g., 1.85'
							value={formData.zscore}
							onChange={(e) => setFormData({ ...formData, zscore: e.target.value })}
							className='w-full px-4 py-3 transition-colors border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none'
						/>
						<p className='mt-2 text-xs text-gray-500'>Your Z-score determines which courses you can apply to</p>
					</div>

					<div className='flex items-center gap-2 px-4 pt-2 border border-blue-200 rounded-lg bg-blue-50'>
						<p className='text-sm text-gray-700'>
							<strong>Don't have Z-score yet?</strong> Skip this to explore all available courses in your stream, or add
							it later for accurate eligibility.
						</p>
					</div>
				</div>
			);
		}

		if (currentStep === 2) {
			// Interests Step (Optional)
			return (
				<div className='space-y-6'>
					<div>
						<h2 className='flex items-center gap-2 mb-2 text-2xl font-bold text-gray-900'>
							Enter Your Career Interests <span className='text-sm font-normal text-gray-500'>(Optional)</span>
						</h2>
						<p className='text-gray-600'>
							Want personalized recommendations? Tell us about your career goals and our AI will rank degrees that match
							your passions!
						</p>
					</div>

					<div>
						<label className='block mb-2 text-sm font-bold text-gray-900'>Career Goals & Interests</label>
						<textarea
							placeholder='e.g., I want to work in software development, AI/ML, or maybe start my own tech business. I love problem-solving and creative thinking...'
							value={formData.interests}
							onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
							className='w-full px-4 py-3 transition-colors border-2 border-gray-300 rounded-lg resize-none focus:border-indigo-500 focus:outline-none'
							rows='6'
						/>
						<p className={`text-xs mt-2 ${formData.interests.length >= 10 ? "text-indigo-600" : "text-gray-500"}`}>
							{formData.interests.length} characters {formData.interests.length >= 10 ? "✓" : "(minimum 10)"}
						</p>
					</div>

					<div className='flex items-center px-4 pt-3 border border-indigo-200 rounded-lg bg-indigo-50'>
						<p className='text-sm text-gray-700'>
							<strong>Why add interests?</strong> Our AI will analyze your goals and show you degrees with the highest
							career match scores - helping you find your perfect fit!
						</p>
					</div>
				</div>
			);
		}

		if (currentStep === 3) {
			// Results
			return (
				<div>
					<div className='max-w-6xl px-6 py-8 mx-auto'>
						<div className='mb-8'>
							<h2 className='mb-2 text-3xl font-bold text-gray-900'>Your Degree Recommendations</h2>
							<div className='p-4 border border-gray-200 rounded-xl bg-gray-50'>
								<h3 className='mb-2 text-sm font-bold text-gray-800'>Your Input Details</h3>
								<ul className='grid grid-cols-1 gap-2 text-sm text-gray-700 md:grid-cols-2'>
									<li className='grid grid-cols-[100px_1fr] gap-2'>
										<span className='font-semibold text-gray-900'>Stream:</span>
										<span>{formData.stream || "Not provided"}</span>
									</li>
									<li className='grid grid-cols-[100px_1fr] gap-2'>
										<span className='font-semibold text-gray-900'>District:</span>
										<span>{formData.district || "Not provided"}</span>
									</li>
									<li className='grid grid-cols-[100px_1fr] gap-2'>
										<span className='font-semibold text-gray-900'>Z-Score:</span>
										<span>{formData.zscore ? formData.zscore : "Not provided"}</span>
									</li>
									<li className='grid grid-cols-[100px_1fr] gap-2 '>
										<span className='font-semibold text-gray-900'>Subjects:</span>
										<span>{formData.subjects.length > 0 ? formData.subjects.join(", ") : "Not provided"}</span>
									</li>
									<li className='grid grid-cols-[100px_1fr] gap-2 '>
										<span className='font-semibold text-gray-900'>Interests:</span>
										<span>
											{formData.interests && formData.interests.trim().length > 0 ?
												formData.interests.length > 140 ?
													`${formData.interests.slice(0, 140)}...`
												:	formData.interests
											:	"Not provided"}
										</span>
									</li>
								</ul>
							</div>
						</div>

						{/* Display results - API returns array directly, sorted by score (highest first) */}
						{Array.isArray(results) && results.length > 0 ?
							<div className='space-y-4'>
								<h3 className='flex items-center gap-2 text-xl font-bold text-gray-900'>
									<div className='w-3 h-3 rounded-full bg-emerald-500'></div>
									Recommended Degrees ({results.length})
								</h3>
								<div className='grid gap-4'>
									{results
										.sort((a, b) => (b.score || 0) - (a.score || 0))
										.map((course, idx) => (
											<CourseCard key={idx} course={course} isEligible={course.eligibility !== false} />
										))}
								</div>
							</div>
						:	<div className='p-6 border border-gray-300 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl'>
								<p className='text-gray-600'>No recommendations found for your criteria. Try adjusting your inputs.</p>
							</div>
						}
					</div>
				</div>
			);
		}
	};

	return (
		<div className='min-h-screen pb-20 bg-slate-50'>
			{/* Hero Header — indigo/violet to match master design */}
			{currentStep <= 3 && (
				<div className='relative pt-24 overflow-hidden pb-28 bg-gradient-to-br from-indigo-900 via-violet-800 to-indigo-900'>
					{/* Ambient blobs */}
					<div className='absolute top-0 right-0 w-[500px] h-[500px] bg-violet-500/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen' />
					<div className='absolute bottom-0 left-10 w-[400px] h-[400px] bg-indigo-400/20 rounded-full blur-[100px] pointer-events-none mix-blend-screen' />

					<div className='relative z-10 max-w-6xl px-6 mx-auto'>
						<h1 className='mb-2 text-4xl font-extrabold tracking-tight text-white sm:text-5xl'>
							Find Your{" "}
							<span className='text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-violet-300'>
								Perfect Degree
							</span>
						</h1>
						<p className='max-w-2xl mb-6 text-lg text-indigo-100/80'>
							Fill in your details step by step. You can skip optional fields — we'll automatically find the best
							matches!
						</p>
						<ProgressStepper
							steps={["Stream & District", "Z-Score (Optional)", "Interests (Optional)", "Results"]}
							currentStep={progressDisplayStep}
						/>
					</div>
				</div>
			)}

			<div className='relative z-20 max-w-6xl px-6 mx-auto -mt-10'>
				{currentStep < 3 && (
					<div className='p-8 mb-6 bg-white border shadow-2xl sm:p-10 border-slate-200/60 rounded-3xl'>
						{renderStep()}

						{error && (
							<div className='flex gap-3 p-4 mt-6 text-red-700 border rounded-xl bg-red-50 border-red-200/60'>
								<div>
									<p className='font-semibold'>Error</p>
									<p className='text-sm'>{error}</p>
								</div>
							</div>
						)}

						{/* Navigation buttons */}
						<div className='flex justify-between gap-4 pt-6 mt-8 border-t border-slate-100'>
							<button
								onClick={handleBack}
								className='inline-flex items-center gap-2 px-5 py-2.5 font-semibold text-slate-700 transition-colors bg-white border rounded-xl border-slate-200 hover:bg-slate-50'>
								← Back
							</button>

							<div className='flex gap-3'>
								{/* Skip button for optional steps */}
								{currentStep > 0 && currentStep < 3 && (
									<button
										onClick={() => setCurrentStep(currentStep + 1)}
										className='px-5 py-2.5 font-semibold text-slate-600 transition-colors bg-slate-100 rounded-xl hover:bg-slate-200'>
										Skip Step
									</button>
								)}

								{/* Next / Submit button */}
								<button
									onClick={handleNext}
									disabled={!isStepValid || loading}
									className={`
										inline-flex items-center gap-2 px-7 py-2.5 rounded-xl font-semibold transition-all duration-300
										${
											isStepValid && !loading ?
												"bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:shadow-lg hover:-translate-y-0.5 cursor-pointer shadow-indigo-500/25"
											:	"bg-slate-100 text-slate-400 cursor-not-allowed"
										}
									`}>
									{loading ?
										<>
											<SpinnerIcon /> Processing...
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

				{currentStep === 3 && renderStep()}
			</div>
		</div>
	);
}
