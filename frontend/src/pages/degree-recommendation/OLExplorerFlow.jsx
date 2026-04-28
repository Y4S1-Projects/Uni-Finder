import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowRight, FaBook, FaSpinner } from "react-icons/fa";
import StickySearchHeader from "../../components/degree/StickySearchHeader";
import CareerPathwayTree from "../../components/degree/CareerPathwayTree";
import { fetchAllDegreeCourses, fetchOLCareerTree } from "../../api/degreeRecommendationApi";
import olSubjectsConfig from "../../config/ol_subjects_config.json";

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
		core: {
			religion: "",
			first_language: "",
			mathematics: "",
			science: "",
			english: "",
			history: "",
			bucket_1_grade: "",
			bucket_2_grade: "",
			bucket_3_grade: "",
		},
		bucket_1: "",
		bucket_2: "",
		bucket_3: "",
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
			// Get all degree courses
			const coursesResponse = await fetchAllDegreeCourses();
			const courseCodes = coursesResponse.courses.map((c) => c.course_code || c.code);

			// Call career tree API with O/L marks
			const treeData = await fetchOLCareerTree({
				studentInput: interests,
				eligibleCourseCodes: courseCodes,
				olMarks: olMarks,
			});

			setResults(treeData);
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
				<div className='p-6 text-white shadow-lg bg-gradient-to-r from-emerald-500 to-teal-600'>
					<div className='max-w-4xl mx-auto mt-24'>
						<h1 className='mb-3 text-4xl font-bold'>Explore Your Career Path</h1>
						<p className='text-emerald-100'>
							For O/L students planning their A/L stream and beyond. Tell us what you're passionate about!
						</p>
					</div>
				</div>

				{/* Main Content */}
				<div className='max-w-4xl px-6 py-8 mx-auto'>
					<div className='p-8 bg-white shadow-lg rounded-2xl'>
						<div className='mb-8'>
							<h2 className='flex items-center gap-2 mb-3 text-3xl font-bold text-gray-900'>
								What are you passionate about?
							</h2>
							<p className='text-lg text-gray-600'>
								Share your interests, dreams, and hobbies. Our AI will suggest degrees and career paths that match your
								passions.
							</p>
						</div>

						{/* Main Textarea */}
						<div className='mb-6'>
							<label className='block mb-3 text-sm font-bold text-gray-900'>Your Career Goals & Interests</label>
							<textarea
								placeholder={CAREER_INTEREST_PROMPTS[Math.floor(Math.random() * CAREER_INTEREST_PROMPTS.length)]}
								value={interests}
								onChange={(e) => setInterests(e.target.value)}
								className='w-full px-4 py-4 text-base transition-colors border-2 resize-none border-emerald-300 rounded-xl focus:border-emerald-600 focus:outline-none'
								rows='6'
							/>
							<p className={`text-xs mt-2 ${interests.length >= 10 ? "text-emerald-600" : "text-gray-500"}`}>
								{interests.length} characters (minimum 10)
							</p>
						</div>

						{/* Optional O/L Marks */}
						<details className='p-4 mb-8 border-2 border-gray-200 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl group'>
							<summary className='flex items-center gap-2 text-base font-bold text-gray-900 cursor-pointer'>
								<FaBook className='text-emerald-600' />
								Add Your O/L Marks (Optional) - Helps us understand your strengths
								<span className='ml-auto text-xs font-normal text-gray-600'>Click to expand</span>
							</summary>

							<div className='mt-6 space-y-8'>
								{/* Core Subjects */}
								<div>
									<h3 className='mb-4 text-sm font-bold text-gray-900'>6 Compulsory (Core) Subjects</h3>
									<div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
										{olSubjectsConfig.core_subjects.map((subject) => (
											<div key={subject.id}>
												<label className='block mb-2 text-xs font-bold text-gray-800'>
													{subject.name}
													{subject.critical && <span className='text-red-600 ml-1'>*</span>}
												</label>
												<select
													value={olMarks.core[subject.id] || ""}
													onChange={(e) =>
														setOlMarks({
															...olMarks,
															core: { ...olMarks.core, [subject.id]: e.target.value },
														})
													}
													className='w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
													<option value=''>Select Grade</option>
													{olSubjectsConfig.grading_scale.map((grade) => (
														<option key={grade} value={grade}>
															{grade} ({olSubjectsConfig.grade_descriptions[grade]})
														</option>
													))}
												</select>
											</div>
										))}
									</div>
								</div>

								{/* Bucket 1 */}
								<div>
									<h3 className='mb-2 text-sm font-bold text-gray-900'>
										{olSubjectsConfig.bucket_1.name} ({olSubjectsConfig.bucket_1.category})
									</h3>
									<p className='mb-4 text-xs text-gray-600'>{olSubjectsConfig.bucket_1.description}</p>
									<select
										value={olMarks.bucket_1 || ""}
										onChange={(e) => setOlMarks({ ...olMarks, bucket_1: e.target.value })}
										className='w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
										<option value=''>Select one subject...</option>
										{olSubjectsConfig.bucket_1.subjects.map((subject) => (
											<option key={subject.id} value={subject.id}>
												{subject.name}
											</option>
										))}
									</select>
									{olMarks.bucket_1 && (
										<select
											value={olMarks.core.bucket_1_grade || ""}
											onChange={(e) =>
												setOlMarks({
													...olMarks,
													core: { ...olMarks.core, bucket_1_grade: e.target.value },
												})
											}
											className='w-full px-3 py-2 mt-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
											<option value=''>Grade</option>
											{olSubjectsConfig.grading_scale.map((grade) => (
												<option key={grade} value={grade}>
													{grade}
												</option>
											))}
										</select>
									)}
								</div>

								{/* Bucket 2 */}
								<div>
									<h3 className='mb-2 text-sm font-bold text-gray-900'>
										{olSubjectsConfig.bucket_2.name} ({olSubjectsConfig.bucket_2.category})
									</h3>
									<p className='mb-4 text-xs text-gray-600'>{olSubjectsConfig.bucket_2.description}</p>
									<select
										value={olMarks.bucket_2 || ""}
										onChange={(e) => setOlMarks({ ...olMarks, bucket_2: e.target.value })}
										className='w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
										<option value=''>Select one subject...</option>
										{olSubjectsConfig.bucket_2.subjects.map((subject) => (
											<option key={subject.id} value={subject.id}>
												{subject.name}
											</option>
										))}
									</select>
									{olMarks.bucket_2 && (
										<select
											value={olMarks.core.bucket_2_grade || ""}
											onChange={(e) =>
												setOlMarks({
													...olMarks,
													core: { ...olMarks.core, bucket_2_grade: e.target.value },
												})
											}
											className='w-full px-3 py-2 mt-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
											<option value=''>Grade</option>
											{olSubjectsConfig.grading_scale.map((grade) => (
												<option key={grade} value={grade}>
													{grade}
												</option>
											))}
										</select>
									)}
								</div>

								{/* Bucket 3 */}
								<div>
									<h3 className='mb-2 text-sm font-bold text-gray-900'>
										{olSubjectsConfig.bucket_3.name} ({olSubjectsConfig.bucket_3.category})
									</h3>
									<p className='mb-4 text-xs text-gray-600'>{olSubjectsConfig.bucket_3.description}</p>
									<select
										value={olMarks.bucket_3 || ""}
										onChange={(e) => setOlMarks({ ...olMarks, bucket_3: e.target.value })}
										className='w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
										<option value=''>Select one subject...</option>
										{olSubjectsConfig.bucket_3.subjects.map((subject) => (
											<option key={subject.id} value={subject.id}>
												{subject.name}
											</option>
										))}
									</select>
									{olMarks.bucket_3 && (
										<select
											value={olMarks.core.bucket_3_grade || ""}
											onChange={(e) =>
												setOlMarks({
													...olMarks,
													core: { ...olMarks.core, bucket_3_grade: e.target.value },
												})
											}
											className='w-full px-3 py-2 mt-2 text-sm border border-gray-300 rounded-lg focus:border-emerald-500 focus:outline-none'>
											<option value=''>Grade</option>
											{olSubjectsConfig.grading_scale.map((grade) => (
												<option key={grade} value={grade}>
													{grade}
												</option>
											))}
										</select>
									)}
								</div>
							</div>
						</details>

						{/* Error */}
						{error && (
							<div className='p-4 mb-6 text-red-700 border-2 border-red-200 rounded-lg bg-red-50'>
								<p className='font-bold'>Error</p>
								<p>{error}</p>
							</div>
						)}

						{/* Action Buttons */}
						<div className='flex justify-between gap-4'>
							<button
								onClick={handleBack}
								className='px-6 py-3 font-bold text-gray-900 transition-colors bg-gray-200 rounded-lg hover:bg-gray-300'>
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

			<div className='max-w-7xl px-6 py-8 mx-auto'>
				<div className='mb-8 text-center'>
					<h2 className='mb-3 text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600'>
						🌟 Your Career Pathway Explorer
					</h2>
					<p className='text-lg text-gray-600'>
						Discover A/L streams perfectly matched to your interests and O/L performance
					</p>
				</div>

				{/* Career Tree Visualization */}
				{results && <CareerPathwayTree treeData={results} />}

				{/* Back button */}
				<div className='mt-12 text-center'>
					<button
						onClick={() => navigate("/degree-recommendations")}
						className='px-8 py-3 font-bold text-white transition-all rounded-lg shadow-lg bg-gradient-to-r from-purple-500 to-pink-500 hover:shadow-xl hover:scale-105'>
						← Back to Main Menu
					</button>
				</div>
			</div>
		</div>
	);
}
