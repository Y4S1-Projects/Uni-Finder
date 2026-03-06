import React from "react";
import { Link } from "react-router-dom";
import { FaArrowRight, FaGlobe, FaGraduationCap, FaListOl } from "react-icons/fa";

export default function DegreeRecommendationsPage() {
	return (
		<div className='max-w-6xl p-8 mx-auto'>
			<h2 className='flex items-center gap-2 mb-3 text-3xl font-bold text-transparent bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text'>
				<FaGraduationCap /> Degree Recommendation System
			</h2>
			<p className='mb-8 text-lg text-gray-700'>
				Choose your pathway to use the correct recommendation flow and scenarios.
			</p>

			<div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
				<Link
					to='/degree-recommendations/al-students'
					className='block p-6 bg-white border-2 border-purple-200 shadow-sm rounded-2xl hover:border-purple-400 hover:shadow-md transition-all no-underline'>
					<div className='flex items-center justify-between'>
						<div className='inline-flex items-center gap-2 px-3 py-1 text-sm font-semibold text-purple-700 rounded-full bg-purple-50 border border-purple-200'>
							<FaListOl /> A/L Students
						</div>
						<FaArrowRight className='text-purple-600' />
					</div>
					<h3 className='mt-4 mb-2 text-xl font-bold text-gray-900'>A/L 4-Scenario Flow</h3>
					<p className='m-0 text-gray-600'>
						Run Scenario 01, 02, 04, and 05 with stream, subject, Z-score, and interest combinations.
					</p>
				</Link>

				<Link
					to='/degree-recommendations/all-students'
					className='block p-6 bg-white border-2 border-blue-200 shadow-sm rounded-2xl hover:border-blue-400 hover:shadow-md transition-all no-underline'>
					<div className='flex items-center justify-between'>
						<div className='inline-flex items-center gap-2 px-3 py-1 text-sm font-semibold text-blue-700 rounded-full bg-blue-50 border border-blue-200'>
							<FaGlobe /> All Students
						</div>
						<FaArrowRight className='text-blue-600' />
					</div>
					<h3 className='mt-4 mb-2 text-xl font-bold text-gray-900'>Scenario 03 · Interests Only</h3>
					<p className='m-0 text-gray-600'>
						Use interest-first recommendations without requiring manual stream/Z-score inputs.
					</p>
				</Link>
			</div>
		</div>
	);
}
