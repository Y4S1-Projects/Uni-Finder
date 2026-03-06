import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaArrowRight, FaHeart, FaFire, FaBook, FaSpinner } from "react-icons/fa";
import StickySearchHeader from "../../components/degree/StickySearchHeader";
import CourseCard from "../../components/degree/CourseCard";
import { fetchAllDegreeCourses, fetchInterestOnlyRecommendations } from "../../api/degreeRecommendationApi";

const CAREER_INTEREST_PROMPTS = [
	"I love working with technology and solving complex problems",
	"I'm passionate about business, entrepreneurship, and managing people",
	"I want to make a positive impact in healthcare and science",
	"I'm interested in creative fields like design, art, and media",
	"I love teaching and helping others learn",
	"I'm fascinated by law, justice, and policy",
	"I want to work in finance, accounting, or economics",
];

export default function OLExplorerFlow() {
	const navigate = useNavigate();
	const [step, setStep] = useState(0); // 0: Input, 1: Results
	const [interests, setInterests] = useState("");
	const [olMarks, setOlMarks] = useState({
		math: "",
		science: "",
	});
	const [loading, setLoading] = useState(false);
	const [results, setResults] = useState(null);
	const [error, setError] = useState("");

	const isFormValid = interests.trim().length >= 10;

	const handleSubmit = async () => {
		if (!isFormValid) return;

		setLoading(true);
		setError("");

		try {
			// Fetch all degree courses
			const coursesResponse = await fetchAllDegreeCourses();
			const courseCodes = coursesResponse.courses.map((c) => c.course_code || c.code);

			// Call interests pipeline
			const data = await fetchInterestOnlyRecommendations({
				studentInput: interests,
				eligibleCourseCodes: courseCodes,
				maxResults: 15,
				explain: true,
			});

			setResults(data);
			setStep(1); // Go to results
		} catch (err) {
			let errorMessage = "Failed to fetch career recommendations.";

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
		} finally {
			setLoading(false);
		}
	};

	const handleBack = () => {
		if (step === 0) {
			navigate("/degree-recommendations");
		} else {
			setStep(0);
		}
	};

	if (step === 0) {
		// Input Step
		return (
			<div className='min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50'>
				{/* Header */}
				<div className='bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6 shadow-lg'>
					<div className='max-w-4xl mx-auto'>
						<button
							onClick={handleBack}
							className='inline-flex items-center gap-2 mb-6 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-all'>
							<FaArrowLeft /> Back
						</button>

						<h1 className='text-4xl font-bold mb-3'>Explore Your Career Path</h1>
						<p className='text-emerald-100'>
							For O/L students planning their A/L stream and beyond. Tell us what you're passionate about!
						</p>
					</div>
				</div>

				{/* Main Content */}
				<div className='max-w-4xl mx-auto px-6 py-8'>
					<div className='bg-white rounded-2xl shadow-lg p-8'>
						<div className='mb-8'>
							<h2 className='text-3xl font-bold text-gray-900 mb-3 flex items-center gap-2'>
								<FaHeart className='text-red-500' /> What are you passionate about?
							</h2>
							<p className='text-gray-600 text-lg'>
								Share your interests, dreams, and hobbies. Our AI will suggest degrees and career paths that match your
								passions.
							</p>
						</div>

						{/* Main Textarea */}
						<div className='mb-6'>
							<label className='block text-sm font-bold text-gray-900 mb-3'>Your Career Goals & Interests</label>
							<textarea
								placeholder={CAREER_INTEREST_PROMPTS[Math.floor(Math.random() * CAREER_INTEREST_PROMPTS.length)]}
								value={interests}
								onChange={(e) => setInterests(e.target.value)}
								className='w-full px-4 py-4 border-2 border-emerald-300 rounded-xl focus:border-emerald-600 focus:outline-none transition-colors resize-none text-base'
								rows='6'
							/>
							<p className={`text-xs mt-2 ${interests.length >= 10 ? "text-emerald-600" : "text-gray-500"}`}>
								{interests.length} characters (minimum 10)
							</p>
						</div>

						{/* Optional O/L Marks */}
						<details className='mb-8 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border-2 border-gray-200 group'>
							<summary className='font-bold text-gray-900 cursor-pointer flex items-center gap-2 text-base'>
								<FaBook className='text-emerald-600' />
								Add Your O/L Marks (Optional)
								<span className='text-xs text-gray-600 font-normal ml-auto'>Click to expand</span>
							</summary>

							<div className='mt-4 grid grid-cols-1 md:grid-cols-2 gap-4'>
								<div>
									<label className='block text-sm font-bold text-gray-900 mb-2'>Mathematics Grade</label>
									<select
										value={olMarks.math}
										onChange={(e) => setOlMarks({ ...olMarks, math: e.target.value })}
										className='w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
										<option value=''>Select Grade</option>
										<option value='A'>A (Excellent)</option>
										<option value='B'>B (Very Good)</option>
										<option value='C'>C (Good)</option>
										<option value='S'>S (Satisfactory)</option>
										<option value='W'>W (Weak)</option>
									</select>
								</div>

								<div>
									<label className='block text-sm font-bold text-gray-900 mb-2'>Science Grade</label>
									<select
										value={olMarks.science}
										onChange={(e) => setOlMarks({ ...olMarks, science: e.target.value })}
										className='w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
										<option value=''>Select Grade</option>
										<option value='A'>A (Excellent)</option>
										<option value='B'>B (Very Good)</option>
										<option value='C'>C (Good)</option>
										<option value='S'>S (Satisfactory)</option>
										<option value='W'>W (Weak)</option>
									</select>
								</div>
							</div>
						</details>

						{/* Error */}
						{error && (
							<div className='p-4 bg-red-50 border-2 border-red-200 rounded-lg text-red-700 mb-6'>
								<p className='font-bold'>Error</p>
								<p>{error}</p>
							</div>
						)}

						{/* Action Buttons */}
						<div className='flex gap-4 justify-between'>
							<button
								onClick={handleBack}
								className='px-6 py-3 bg-gray-200 text-gray-900 rounded-lg font-bold hover:bg-gray-300 transition-colors'>
								← Back
							</button>

							<button
								onClick={handleSubmit}
								disabled={!isFormValid || loading}
								className={`
									inline-flex items-center gap-2 px-8 py-3 rounded-lg font-bold transition-all
									${
										isFormValid && !loading ?
											"bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-lg cursor-pointer"
										:	"bg-gray-300 text-gray-600 cursor-not-allowed"
									}
								`}>
								{loading ?
									<>
										<FaSpinner className='animate-spin' /> Analyzing...
									</>
								:	<>
										Generate My Career Map <FaArrowRight />
									</>
								}
							</button>
						</div>
					</div>
				</div>
			</div>
		);
	}

	// Results Step
	return (
		<div className='min-h-screen bg-gradient-to-br from-slate-50 to-blue-50'>
			{results && (
				<StickySearchHeader
					criteria={{ interests }}
					onEdit={() => {
						setResults(null);
						setStep(0);
						setInterests("");
					}}
				/>
			)}

			<div className='max-w-6xl mx-auto px-6 py-8'>
				<div className='mb-8'>
					<h2 className='text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2'>
						<FaFire className='text-orange-500' /> Your Perfect Career Matches
					</h2>
					<p className='text-gray-600'>
						These degrees align brilliantly with your interests. Start exploring A/L streams for these paths!
					</p>
				</div>

				{/* Recommendations */}
				{results?.recommendations && results.recommendations.length > 0 ?
					<div className='space-y-4'>
						<div className='grid gap-4'>
							{results.recommendations.map((course, idx) => (
								<CourseCard key={idx} course={course} isEligible={true} isAspirationnal={idx > 4 ? true : false} />
							))}
						</div>
					</div>
				:	<div className='p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl border-2 border-gray-300 text-center'>
						<FaBook className='text-gray-400 text-4xl mx-auto mb-3' />
						<p className='text-gray-700 font-semibold'>No matching degrees found.</p>
						<p className='text-gray-600 text-sm mt-1'>Try describing your interests in more detail.</p>
					</div>
				}

				{/* Footer info */}
				<div className='mt-12 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl border-2 border-blue-200'>
					<div className='flex gap-4'>
						<div className='text-4xl'>💡</div>
						<div>
							<h3 className='font-bold text-gray-900'>Next Steps</h3>
							<p className='text-gray-700 text-sm mt-2'>
								Once you choose your A/L stream based on these career paths, come back using the "A/L Students" flow to
								checkout eligibility requirements and specific degree programs. Explore university websites, attend open
								days, and reach out to career counselors to learn more!
							</p>
						</div>
					</div>
				</div>

				{/* Back button */}
				<div className='mt-8'>
					<button
						onClick={() => navigate("/degree-recommendations")}
						className='px-6 py-3 bg-gray-200 text-gray-900 rounded-lg font-bold hover:bg-gray-300 transition-colors'>
						← Back to Main
					</button>
				</div>
			</div>
		</div>
	);
}
