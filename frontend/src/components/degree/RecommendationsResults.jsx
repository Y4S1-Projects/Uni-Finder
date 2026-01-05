import React from "react";
import { FaInfoCircle, FaStar, FaUniversity } from "react-icons/fa";

function formatNumber(value) {
	if (value === undefined || value === null) return "N/A";
	const num = Number(value);
	if (Number.isNaN(num)) return String(value);
	return num.toFixed(4);
}

export default function RecommendationsResults({ results }) {
	if (!results) return null;

	if (!Array.isArray(results) || results.length === 0) {
		return (
			<div className='p-6 bg-white rounded-2xl border border-purple-200 shadow-sm'>
				<h3 className='text-xl font-semibold mb-2 bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent flex items-center gap-2'>
					<FaInfoCircle /> Results
				</h3>
				<p className='text-gray-600 m-0'>No eligible degree recommendations found.</p>
			</div>
		);
	}

	return (
		<div className='p-6 bg-white rounded-2xl border border-purple-200 shadow-sm'>
			<div className='flex items-center justify-between gap-4 mb-4'>
				<h3 className='text-xl font-semibold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent flex items-center gap-2 m-0'>
					<FaStar /> Recommendations
				</h3>
				<span className='px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200 text-sm font-semibold'>
					{results.length}
				</span>
			</div>

			<div className='space-y-3'>
				{results.map((item, idx) => (
					<div
						key={`${item.degree_name || "degree"}-${idx}`}
						className='p-4 rounded-xl border border-gray-200 hover:border-purple-200 transition-colors'>
						<div className='flex items-start justify-between gap-4'>
							<div className='min-w-0'>
								<div className='font-semibold text-gray-900 break-words'>{item.degree_name || "(Unnamed Degree)"}</div>

								{item.metadata?.institute || item.metadata?.faculty ? (
									<div className='text-gray-600 text-sm mt-1 break-words flex flex-wrap items-center gap-x-3 gap-y-1'>
										{item.metadata?.institute ? (
											<span className='inline-flex items-center gap-2'>
												<FaUniversity className='text-purple-600' />
												<span>
													<span className='font-semibold'>University:</span> {item.metadata.institute}
												</span>
											</span>
										) : null}
										{item.metadata?.faculty ? (
											<span>
												<span className='font-semibold'>Faculty:</span> {item.metadata.faculty}
											</span>
										) : null}
									</div>
								) : null}
							</div>

							<div className='flex-shrink-0 text-right'>
								<div className='text-sm text-gray-500'>Score</div>
								<div className='font-bold text-gray-900'>{formatNumber(item.score)}</div>
							</div>
						</div>

						<div className='mt-3 text-sm text-gray-600'>
							Similarity: <span className='font-semibold'>{formatNumber(item.similarity)}</span>
						</div>
					</div>
				))}
			</div>
		</div>
	);
}
