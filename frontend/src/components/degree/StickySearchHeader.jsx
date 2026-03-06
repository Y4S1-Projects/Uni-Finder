import React from "react";
import { FaPencilAlt, FaFilter } from "react-icons/fa";

export default function StickySearchHeader({ criteria = {}, onEdit }) {
	const { stream, zscore, district, interests } = criteria;

	const formatCriteria = () => {
		const parts = [];

		if (stream && stream !== "Any") parts.push(`A/L ${stream}`);
		if (zscore !== undefined && zscore !== null && zscore !== 0) parts.push(`Z-Score: ${zscore}`);
		if (district) parts.push(`District: ${district}`);
		if (interests) parts.push(`Interest: ${interests.substring(0, 40)}${interests.length > 40 ? "..." : ""}`);

		return parts.length > 0 ? parts.join(" | ") : "View Your Recommendations";
	};

	return (
		<div className='sticky top-0 z-40 bg-gradient-to-r from-purple-600 via-blue-600 to-purple-600 shadow-xl'>
			<div className='max-w-6xl mx-auto px-6 py-4'>
				<div className='flex items-center justify-between gap-4'>
					{/* Criteria display */}
					<div className='flex-1 min-w-0'>
						<div className='flex items-center gap-2 mb-1'>
							<FaFilter className='text-white flex-shrink-0' />
							<h2 className='text-white font-bold text-lg truncate'>{formatCriteria()}</h2>
						</div>
						<p className='text-purple-100 text-sm'>Based on your preferences</p>
					</div>

					{/* Edit button */}
					{onEdit && (
						<button
							onClick={onEdit}
							className='flex-shrink-0 inline-flex items-center gap-2 px-4 py-2 bg-white text-purple-700 rounded-full font-semibold hover:bg-purple-50 transition-colors'>
							<FaPencilAlt className='text-sm' />
							<span className='text-sm'>Edit</span>
						</button>
					)}
				</div>
			</div>
		</div>
	);
}
