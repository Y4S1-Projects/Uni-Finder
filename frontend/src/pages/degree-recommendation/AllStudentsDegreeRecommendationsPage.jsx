import React, { useState } from "react";
import { Link } from "react-router-dom";
import RecommendationsResults from "../components/degree/RecommendationsResults";
import { fetchAllDegreeCourses, fetchInterestOnlyRecommendations } from "../api/degreeRecommendationApi";
import { FaArrowLeft, FaExclamationTriangle, FaGlobe, FaSpinner, FaStar } from "react-icons/fa";

export default function AllStudentsDegreeRecommendationsPage() {
	const [studentInput, setStudentInput] = useState("I like technology, software, AI, and problem solving");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [results, setResults] = useState(null);

	const handleSubmit = async (event) => {
		event.preventDefault();
		if (!studentInput.trim()) {
			setError("Please enter your interests or career goals.");
			return;
		}

		setLoading(true);
		setError("");
		setResults(null);

		try {
			const coursesPayload = await fetchAllDegreeCourses();
			const allCourseCodes = (coursesPayload?.courses || [])
				.map((course) => String(course.course_code || "").trim())
				.filter(Boolean);

			if (allCourseCodes.length === 0) {
				throw new Error("No courses available to run interests-only recommendations.");
			}

			const data = await fetchInterestOnlyRecommendations({
				studentInput: studentInput.trim(),
				eligibleCourseCodes: allCourseCodes,
				maxResults: 5,
				explain: true,
			});

			setResults(data);
		} catch (err) {
			setError(err?.response?.data?.detail || err?.message || "Failed to fetch interests-only recommendations.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className='max-w-5xl p-8 mx-auto'>
			<Link
				to='/degree-recommendations'
				className='inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-5'>
				<FaArrowLeft /> Back to Degree Flows
			</Link>

			<h2 className='flex items-center gap-2 mb-2 text-3xl font-bold text-transparent bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text'>
				<FaGlobe /> All Students · Scenario 03 (Interests Only)
			</h2>
			<p className='mb-6 text-gray-700'>
				Provide your interests and career goals. The system will rank degree options using semantic interest matching.
			</p>

			<form onSubmit={handleSubmit} className='p-8 bg-white border-2 border-blue-200 shadow-lg rounded-2xl'>
				<label className='flex items-center gap-2 mb-3 text-lg font-semibold text-gray-800'>
					<FaStar className='text-blue-600' />
					<span>Interests / Career Goals</span>
					<span className='text-red-500'>*</span>
				</label>
				<textarea
					value={studentInput}
					onChange={(e) => setStudentInput(e.target.value)}
					rows={5}
					disabled={loading}
					placeholder='Example: I enjoy coding, AI, statistics, and building software products.'
					className='w-full px-4 py-3 rounded-xl border-2 border-gray-200 bg-white transition-colors focus:outline-none focus:border-blue-400'
				/>
				<p className='mt-2 text-sm text-gray-500'>
					Minimum 10 characters. Add skills, interests, and career direction.
				</p>

				<div className='flex items-center justify-end mt-6'>
					<button
						type='submit'
						disabled={loading || studentInput.trim().length < 10}
						className='px-6 py-3 font-semibold text-white transition-all duration-300 shadow-lg rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed'>
						{loading ? "Generating…" : "Run Scenario 03"}
					</button>
				</div>
			</form>

			{error ?
				<div className='flex items-start gap-3 p-4 mt-6 text-red-700 border border-red-200 rounded-lg bg-red-50'>
					<FaExclamationTriangle className='mt-0.5 flex-shrink-0' />
					<div className='min-w-0'>{error}</div>
				</div>
			:	null}

			{loading ?
				<div className='flex items-center gap-2 mt-6 text-gray-600'>
					<FaSpinner className='animate-spin' />
					<span>Running interest-matching pipeline…</span>
				</div>
			:	null}

			<div className='mt-8'>
				<RecommendationsResults results={results} />
			</div>
		</div>
	);
}
