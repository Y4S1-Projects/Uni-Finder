import React, { useState } from "react";
import { Link } from "react-router-dom";
import StudentProfileForm from "../components/degree/StudentProfileForm";
import RecommendationsResults from "../components/degree/RecommendationsResults";
import ScenarioSelector from "../components/degree/ScenarioSelector";
import { fetchDegreeRecommendations } from "../api/degreeRecommendationApi";
import { AL_SCENARIO_ORDER } from "../constants/degreeScenarios";
import { FaArrowLeft, FaExclamationTriangle, FaGraduationCap, FaSpinner } from "react-icons/fa";

const BASE_FORM = {
	stream: "Science",
	subjects: ["Physics", "Chemistry", "Combined Mathematics"],
	zscore: "",
	interests: "Computer Science",
	district: "Colombo",
};

export default function ALDegreeRecommendationsPage() {
	const [activeScenario, setActiveScenario] = useState(AL_SCENARIO_ORDER[0]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [results, setResults] = useState(null);

	const handleSubmit = async (payload) => {
		setLoading(true);
		setError("");
		setResults(null);

		try {
			const maxResults = activeScenario.id === "s1" ? 10 : 5;
			const data = await fetchDegreeRecommendations({
				...payload,
				max_results: maxResults,
			});
			setResults(data);
		} catch (err) {
			setError(err?.response?.data?.detail || "Failed to fetch A/L degree recommendations.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className='max-w-6xl p-8 mx-auto'>
			<Link
				to='/degree-recommendations'
				className='inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-5'>
				<FaArrowLeft /> Back to Degree Flows
			</Link>

			<h2 className='flex items-center gap-2 mb-2 text-3xl font-bold text-transparent bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text'>
				<FaGraduationCap /> A/L Degree Recommendation Scenarios
			</h2>
			<p className='mb-6 text-gray-700'>
				This page supports Scenario 01, 02, 04, and 05 with the same logic used in the upgraded A/L recommendation
				pipeline.
			</p>

			<ScenarioSelector
				scenarios={AL_SCENARIO_ORDER}
				activeScenarioId={activeScenario.id}
				onChange={(scenario) => {
					setActiveScenario(scenario);
					setResults(null);
					setError("");
				}}
			/>

			<StudentProfileForm
				key={activeScenario.id}
				initialValues={BASE_FORM}
				onSubmit={handleSubmit}
				loading={loading}
				scenarioConfig={activeScenario}
				submitLabel='Run Selected Scenario'
			/>

			{error ?
				<div className='flex items-start gap-3 p-4 mt-6 text-red-700 border border-red-200 rounded-lg bg-red-50'>
					<FaExclamationTriangle className='mt-0.5 flex-shrink-0' />
					<div className='min-w-0'>{error}</div>
				</div>
			:	null}

			{loading ?
				<div className='flex items-center gap-2 mt-6 text-gray-600'>
					<FaSpinner className='animate-spin' />
					<span>Running scenario and generating recommendations…</span>
				</div>
			:	null}

			<div className='mt-8'>
				<RecommendationsResults results={results} />
			</div>
		</div>
	);
}
