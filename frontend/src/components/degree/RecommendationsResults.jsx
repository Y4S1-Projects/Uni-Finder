import React from "react";
import { FaBullseye, FaCheckCircle, FaExclamationTriangle, FaInfoCircle, FaStar, FaUniversity } from "react-icons/fa";

function formatNumber(value) {
	if (value === undefined || value === null) return "N/A";
	const num = Number(value);
	if (Number.isNaN(num)) return String(value);
	return num.toFixed(4);
}

function renderCourseList(items, emptyMessage = "No recommendations found.") {
	if (!Array.isArray(items) || items.length === 0) {
		return <p className='text-gray-600 m-0'>{emptyMessage}</p>;
	}

	return (
		<div className='space-y-3'>
			{items.map((item, idx) => (
				<div
					key={`${item.course_code || item.degree_name || "degree"}-${idx}`}
					className='p-4 rounded-xl border border-gray-200 hover:border-purple-200 transition-colors'>
					<div className='flex items-start justify-between gap-4'>
						<div className='min-w-0'>
							<div className='font-semibold text-gray-900 break-words'>
								{item.course_name || item.degree_name || "(Unnamed Degree)"}
							</div>

							{Array.isArray(item.universities) && item.universities.length > 0 ?
								<div className='text-gray-600 text-sm mt-1 break-words flex flex-wrap items-center gap-x-3 gap-y-1'>
									<span className='inline-flex items-center gap-2'>
										<FaUniversity className='text-purple-600' />
										<span>
											<span className='font-semibold'>Universities:</span> {item.universities.slice(0, 2).join(", ")}
										</span>
									</span>
								</div>
							:	null}
						</div>

						<div className='flex-shrink-0 text-right'>
							<div className='text-sm text-gray-500'>Score</div>
							<div className='font-bold text-gray-900'>
								{formatNumber(item.interest_match_score ?? item.match_score_percentage ?? item.score)}
							</div>
						</div>
					</div>

					{item.eligibility_reason ?
						<div className='mt-3 text-sm text-gray-600'>
							Eligibility: <span className='font-semibold'>{item.eligibility_reason}</span>
						</div>
					:	null}

					{item.explanation ?
						<div className='mt-3 text-sm text-gray-700'>{item.explanation}</div>
					:	null}
				</div>
			))}
		</div>
	);
}

export default function RecommendationsResults({ results }) {
	if (!results) return null;

	const recommendations =
		Array.isArray(results) ? results
		: Array.isArray(results.recommendations) ? results.recommendations
		: [];

	const allEligible = Array.isArray(results?.all_eligible_courses) ? results.all_eligible_courses : [];

	if (recommendations.length === 0 && allEligible.length === 0) {
		return (
			<div className='p-6 bg-white rounded-2xl border border-purple-200 shadow-sm'>
				<h3 className='text-xl font-semibold mb-2 bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent flex items-center gap-2'>
					<FaInfoCircle /> Results
				</h3>
				<p className='text-gray-600 m-0'>No eligible degree recommendations found.</p>
				{Array.isArray(results?.aspirational_courses) && results.aspirational_courses.length > 0 ?
					<div className='mt-4'>
						<h4 className='font-semibold text-gray-800 mb-2'>Suggested Alternatives</h4>
						{renderCourseList(results.aspirational_courses)}
					</div>
				:	null}
			</div>
		);
	}

	return (
		<div className='p-6 bg-white rounded-2xl border border-purple-200 shadow-sm'>
			{results?.has_mismatch && results?.dream_course ?
				<div className='mb-4 p-4 rounded-xl border border-amber-300 bg-amber-50 text-amber-900'>
					<div className='font-semibold flex items-center gap-2'>
						<FaExclamationTriangle /> Dream vs Reality Mismatch Detected
					</div>
					<p className='mt-2 text-sm mb-0'>
						Dream: <span className='font-semibold'>{results.dream_course.course_name}</span>
						{results.dream_course.ineligibility_reason ? ` · ${results.dream_course.ineligibility_reason}` : ""}
					</p>
				</div>
			:	null}

			<div className='flex items-center justify-between gap-4 mb-4'>
				<h3 className='text-xl font-semibold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent flex items-center gap-2 m-0'>
					<FaStar /> Interest-Ranked Recommendations
				</h3>
				<span className='px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200 text-sm font-semibold'>
					{recommendations.length}
				</span>
			</div>

			{renderCourseList(recommendations, "No ranked recommendations found.")}

			{allEligible.length > 0 ?
				<div className='mt-6'>
					<div className='flex items-center justify-between gap-4 mb-3'>
						<h4 className='text-lg font-semibold text-gray-900 flex items-center gap-2 m-0'>
							<FaCheckCircle className='text-emerald-600' /> All Eligible Courses
						</h4>
						<span className='px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-sm font-semibold'>
							{allEligible.length}
						</span>
					</div>
					{renderCourseList(allEligible)}
				</div>
			:	null}

			{results?.pipeline_steps ?
				<div className='mt-6 rounded-xl border border-blue-200 bg-blue-50 p-4'>
					<div className='font-semibold text-blue-900 flex items-center gap-2'>
						<FaBullseye /> Pipeline Steps
					</div>
					<ul className='mt-2 mb-0 text-sm text-blue-900 list-disc pl-5'>
						{Object.values(results.pipeline_steps).map((step, index) => (
							<li key={`${step}-${index}`}>{step}</li>
						))}
					</ul>
				</div>
			:	null}
		</div>
	);
}
