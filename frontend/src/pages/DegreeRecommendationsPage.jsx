import React, { useState } from "react";
import StudentProfileForm from "../components/degree/StudentProfileForm";
import RecommendationsResults from "../components/degree/RecommendationsResults";
import { fetchDegreeRecommendations } from "../api/degreeRecommendationApi";
import { FaExclamationTriangle, FaGraduationCap, FaSpinner } from "react-icons/fa";

const DEFAULT_FORM = {
	stream: "Science",
	subjects: ["Physics", "Chemistry", "Combined Mathematics"],
	zscore: "",
	interests: "Computer Science",
	district: "Colombo",
};

export default function DegreeRecommendationsPage() {
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [results, setResults] = useState(null);

	const handleSubmit = async (payload) => {
		setLoading(true);
		setError("");
		setResults(null);

		try {
			const data = await fetchDegreeRecommendations(payload);
			setResults(data);
		} catch (err) {
			setError("Failed to fetch degree recommendations. Please ensure API Gateway and degree service are running.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className='max-w-5xl p-8 mx-auto'>
			{/* Header */}
			<h2 className='flex items-center gap-2 mb-3 text-3xl font-bold text-transparent bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text'>
				<FaGraduationCap /> Degree Recommendations
			</h2>
			<p className='mb-8 text-lg text-gray-700'>
				Enter your A/L stream, subjects, and interests to get AI-powered degree suggestions.
			</p>

			{/* Form */}
			<StudentProfileForm initialValues={DEFAULT_FORM} onSubmit={handleSubmit} loading={loading} />

			{/* Error */}
			{error ? (
				<div className='flex items-start gap-3 p-4 mt-6 text-red-700 border border-red-200 rounded-lg bg-red-50'>
					<FaExclamationTriangle className='mt-0.5 flex-shrink-0' />
					<div className='min-w-0'>{error}</div>
				</div>
			) : null}

			{/* Loading */}
			{loading ? (
				<div className='flex items-center gap-2 mt-6 text-gray-600'>
					<FaSpinner className='animate-spin' />
					<span>Generating recommendations…</span>
				</div>
			) : null}

			{/* Results */}
			<div className='mt-8'>
				<RecommendationsResults results={results} />
			</div>
		</div>
	);
}
