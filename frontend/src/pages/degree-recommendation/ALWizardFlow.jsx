import React, { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaArrowRight, FaUniversity, FaPercent, FaHeart, FaBook, FaSpinner } from "react-icons/fa";
import ProgressStepper from "../../components/degree/ProgressStepper";
import StickySearchHeader from "../../components/degree/StickySearchHeader";
import LoadingState from "../../components/degree/LoadingState";
import CourseCard from "../../components/degree/CourseCard";
import { fetchDegreeRecommendations } from "../../api/degreeRecommendationApi";

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
	const [detectedScenario, setDetectedScenario] = useState(null);

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

	const handleSkipToResults = () => {
		// Skip remaining steps and go straight to results
		handleSubmit();
	};

	const handleBack = () => {
		if (currentStep === 0) {
			navigate("/degree-recommendations");
		} else if (currentStep === 3) {
			// From results, go back to step 0
			setResults(null);
			setCurrentStep(0);
		} else {
			setCurrentStep(currentStep - 1);
		}
	};

	const handleSubmit = async () => {
		setLoading(true);
		setError("");

		try {
			// Detect which scenario applies based on inputs
			const scenario = detectScenario(formData);
			setDetectedScenario(scenario);

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
				<div className='space-y-6'>
					<div>
						<h2 className='flex items-center gap-2 mb-2 text-2xl font-bold text-gray-900'>
							<FaUniversity /> What's Your A/L Stream?
						</h2>
						<p className='text-gray-600'>Select the stream you're currently studying or plan to study.</p>
					</div>

					{/* Stream Grid */}
					<div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
						{ALABAMA_STREAMS.map((stream) => (
							<button
								key={stream.id}
								onClick={() => handleStreamSelect(stream.id)}
								className={`
									relative p-6 rounded-2xl border-2 transition-all duration-300 text-left
									${
										formData.stream === stream.name ?
											`border-purple-500 bg-gradient-to-br from-purple-50 to-blue-50 shadow-lg`
										:	`border-gray-200 bg-white hover:border-purple-300 hover:shadow-md`
									}
								`}>
								<div className={`inline-block text-3xl mb-3 p-2 rounded-lg bg-gradient-to-br ${stream.color}`}>
									{stream.icon}
								</div>
								<h3 className='font-bold text-gray-900'>{stream.name}</h3>
								{formData.stream === stream.name && (
									<div className='absolute flex items-center justify-center w-6 h-6 text-sm font-bold text-white rounded-full top-3 right-3 bg-gradient-to-r from-purple-500 to-blue-500'>
										✓
									</div>
								)}
							</button>
						))}
					</div>

					{/* District Selection */}
					<div>
						<label className='block mb-3 text-sm font-bold text-gray-900'>
							<FaBook className='inline mr-2' /> District of Residence
						</label>
						<select
							value={formData.district}
							onChange={(e) => setFormData({ ...formData, district: e.target.value })}
							className='w-full px-4 py-3 transition-colors border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none'>
							<option value=''>Select your district...</option>
							{SRI_LANKAN_DISTRICTS.map((district) => (
								<option key={district} value={district}>
									{district}
								</option>
							))}
						</select>
					</div>

					{/* Subject Selection - Shows after stream is selected */}
					{formData.stream && selectedStream && (
						<div className='pt-8 mt-8 border-t-2 border-gray-200'>
							<div className='mb-6'>
								<div className='flex items-center justify-between'>
									<div>
										<h3 className='flex items-center gap-2 mb-2 text-xl font-bold text-gray-900'>
											<FaBook className='text-purple-600' />
											Select Your 3 Subjects
										</h3>
										<p className='text-sm text-gray-600'>
											Choose exactly 3 subjects from the {selectedStream.name} stream
										</p>
									</div>
									<div
										className={`text-2xl font-bold px-4 py-2 rounded-lg ${
											formData.subjects.length === 3 ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
										}`}>
										{formData.subjects.length}/3
									</div>
								</div>
							</div>

							{/* Subject Selector Grid */}
							<div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
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
											p-4 rounded-xl border-2 transition-all duration-200 text-left font-semibold text-sm
											${
												formData.subjects.includes(subject) ?
													"border-purple-500 bg-gradient-to-r from-purple-50 to-blue-50 text-purple-900 shadow-md"
												: formData.subjects.length >= 3 ?
													"border-gray-200 bg-gray-50 text-gray-600 cursor-not-allowed opacity-50"
												:	"border-gray-300 bg-white text-gray-900 hover:border-purple-400 hover:bg-purple-50 cursor-pointer"
											}
										`}
										disabled={formData.subjects.length >= 3 && !formData.subjects.includes(subject)}>
										<div className='flex items-center gap-3'>
											<div
												className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
													formData.subjects.includes(subject) ? "border-purple-500 bg-purple-500" : "border-gray-300"
												}`}>
												{formData.subjects.includes(subject) && <span className='text-sm text-white'>✓</span>}
											</div>
											<span>{subject}</span>
										</div>
									</button>
								))}
							</div>

							{/* Validation Messages */}
							{formData.subjects.length < 3 && (
								<div className='p-4 mt-4 border border-yellow-200 rounded-lg bg-yellow-50'>
									<p className='text-sm text-yellow-800'>
										<strong>
											⚠️ Select {3 - formData.subjects.length} more subject
											{3 - formData.subjects.length !== 1 ? "s" : ""}
										</strong>{" "}
										to continue. You must select exactly 3 subjects.
									</p>
								</div>
							)}

							{formData.subjects.length === 3 && !subjectRuleError && (
								<div className='p-4 mt-4 border border-green-200 rounded-lg bg-green-50'>
									<p className='text-sm text-green-800'>
										<strong>✓ Perfect!</strong> You've selected a valid 3-subject combination:{" "}
										<span className='font-semibold'>{formData.subjects.join(", ")}</span>
									</p>
								</div>
							)}

							{formData.subjects.length === 3 && subjectRuleError && (
								<div className='p-4 mt-4 border border-red-200 rounded-lg bg-red-50'>
									<p className='text-sm text-red-800'>
										<strong>⚠ Invalid combination:</strong> {subjectRuleError}
									</p>
								</div>
							)}
						</div>
					)}
				</div>
			);
		}

		if (currentStep === 1) {
			// Z-Score Step (Optional)
			return (
				<div className='space-y-6'>
					<div>
						<h2 className='flex items-center gap-2 mb-2 text-2xl font-bold text-gray-900'>
							<FaPercent /> Your Z-Score <span className='text-sm font-normal text-gray-500'>(Optional)</span>
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

					<div className='flex items-center gap-3 p-4 border border-blue-200 rounded-lg bg-blue-50'>
						<div className='text-2xl'>💡</div>
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
							<FaHeart /> Your Career Interests <span className='text-sm font-normal text-gray-500'>(Optional)</span>
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
							className='w-full px-4 py-3 transition-colors border-2 border-gray-300 rounded-lg resize-none focus:border-purple-500 focus:outline-none'
							rows='6'
						/>
						<p className={`text-xs mt-2 ${formData.interests.length >= 10 ? "text-green-600" : "text-gray-500"}`}>
							{formData.interests.length} characters {formData.interests.length >= 10 ? "✓" : "(minimum 10)"}
						</p>
					</div>

					<div className='flex items-center gap-3 p-4 border border-purple-200 rounded-lg bg-purple-50'>
						<div className='text-2xl'>✨</div>
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
					<StickySearchHeader
						criteria={formData}
						onEdit={() => {
							setResults(null);
							setCurrentStep(0);
						}}
					/>

					<div className='max-w-6xl px-6 py-8 mx-auto'>
						{/* Detected Scenario Badge */}
						{detectedScenario && (
							<div className='p-4 mb-6 border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl'>
								<div className='flex items-start gap-3'>
									<div className='text-2xl'>🎯</div>
									<div>
										<h3 className='mb-1 font-bold text-purple-900'>{detectedScenario.name}</h3>
										<p className='text-sm text-gray-700'>{detectedScenario.description}</p>
									</div>
								</div>
							</div>
						)}

						<div className='mb-8'>
							<h2 className='mb-2 text-3xl font-bold text-gray-900'>Your Degree Recommendations</h2>
							<p className='text-gray-600'>
								Based on your {formData.stream} stream
								{formData.zscore && Number(formData.zscore) > 0 && `, Z-Score: ${formData.zscore}`}
								{formData.interests && formData.interests.length >= 10 && `, and career interests`}
							</p>
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
		<div className='min-h-screen bg-gradient-to-br from-slate-50 to-blue-50'>
			{currentStep < 3 && (
				<div className='p-6 text-white shadow-lg bg-gradient-to-r from-purple-600 to-blue-600'>
					<div className='max-w-6xl mx-auto'>
						<button
							onClick={handleBack}
							className='inline-flex items-center gap-2 px-4 py-2 mb-4 transition-all bg-white rounded-lg bg-opacity-20 hover:bg-opacity-30'>
							<FaArrowLeft /> Back
						</button>

						<h1 className='mb-6 text-4xl font-bold'>Find Your Perfect Degree</h1>
						<p className='mb-6 text-purple-100'>
							Fill in your details step by step. You can skip optional fields - we'll automatically find the best
							matches!
						</p>

						<ProgressStepper
							steps={["Stream & District", "Z-Score (Optional)", "Interests (Optional)", "Results"]}
							currentStep={currentStep}
						/>
					</div>
				</div>
			)}

			<div className='max-w-6xl px-6 py-8 mx-auto'>
				{currentStep < 3 && (
					<div className='p-8 mb-6 bg-white shadow-lg rounded-2xl'>
						{renderStep()}

						{error && (
							<div className='p-4 mt-6 text-red-700 border-2 border-red-200 rounded-lg bg-red-50'>
								<p className='font-bold'>Error</p>
								<p>{error}</p>
							</div>
						)}

						{/* Navigation buttons */}
						<div className='flex justify-between gap-4 mt-8'>
							<button
								onClick={handleBack}
								className='px-6 py-3 font-bold text-gray-900 transition-colors bg-gray-200 rounded-lg hover:bg-gray-300'>
								← Back
							</button>

							<div className='flex gap-3'>
								{/* Skip button for optional steps */}
								{currentStep > 0 && currentStep < 3 && (
									<button
										onClick={() => setCurrentStep(currentStep + 1)}
										className='px-6 py-3 font-semibold text-gray-700 transition-colors bg-gray-100 rounded-lg hover:bg-gray-200'>
										Skip Step →
									</button>
								)}

								{/* Show "Find Degrees" earlier if they have minimum required info */}
								{currentStep > 0 && formData.stream && formData.district && formData.subjects.length === 3 && (
									<button
										onClick={handleSkipToResults}
										disabled={loading}
										className='px-6 py-3 font-bold text-green-700 transition-colors bg-green-100 border-2 border-green-400 rounded-lg hover:bg-green-200'>
										{loading ?
											<FaSpinner className='inline mr-2 animate-spin' />
										:	"🎯"}{" "}
										Find Degrees Now
									</button>
								)}

								{/* Next button */}
								<button
									onClick={handleNext}
									disabled={!isStepValid || loading}
									className={`
										inline-flex items-center gap-2 px-6 py-3 rounded-lg font-bold transition-all
										${
											isStepValid && !loading ?
												"bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg cursor-pointer"
											:	"bg-gray-300 text-gray-600 cursor-not-allowed"
										}
									`}>
									{loading ?
										<>
											<FaSpinner className='animate-spin' /> Processing
										</>
									:	<>
											{currentStep === 2 ? "Find My Degrees" : "Next"} <FaArrowRight />
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
