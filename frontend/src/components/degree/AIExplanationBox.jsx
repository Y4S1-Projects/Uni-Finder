import React from "react";
import { FaStar } from "react-icons/fa";

export default function AIExplanationBox({ explanation = "" }) {
	if (!explanation || explanation.trim().length === 0) {
		return null;
	}

	// Improved UX: Makes keywords look like they were highlighted with a marker pen
	const highlightKeywords = (text) => {
		// Note: Ideally, your backend should wrap matched keywords in <strong> tags before sending.
		// This is a fallback frontend parser.
		const keywords = [
			"AI",
			"interest",
			"match",
			"eligible",
			"requires",
			"strong",
			"perfect",
			"ideal",
			"stream",
			"degree",
			"career",
			"skills",
			"excellent",
			"great",
			"good",
			"best",
			"top",
		];
		let highlightedText = text;

		keywords.forEach((keyword) => {
			const regex = new RegExp(`\\b(${keyword}s?)\\b`, "gi");
			highlightedText = highlightedText.replace(
				regex,
				(match) =>
					`<strong class="bg-gradient-to-r from-purple-200 to-pink-200 text-purple-900 px-2 py-0.5 rounded font-bold">${match}</strong>`,
			);
		});

		return highlightedText;
	};

	return (
		<div className='relative p-4 overflow-hidden transition-all border border-purple-200 shadow-sm rounded-xl bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 hover:shadow-md'>
			{/* Decorative gradient background elements */}
			<div className='absolute w-20 h-20 bg-purple-300 rounded-full -top-6 -right-6 opacity-10 blur-xl'></div>
			<div className='absolute w-20 h-20 bg-blue-300 rounded-full -bottom-6 -left-6 opacity-10 blur-xl'></div>

			<div className='relative flex items-start gap-3'>
				{/* Icon Container */}
				<div className='p-2.5 bg-gradient-to-br from-purple-400 to-indigo-500 rounded-lg shadow-md flex-shrink-0 mt-0.5'>
					<FaStar className='text-sm text-white' />
				</div>

				{/* Text Content */}
				<div className='flex-1 min-w-0'>
					<h4 className='text-xs font-bold uppercase tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-indigo-700 mb-1.5'>
						✨ AI Insight
					</h4>
					<p
						className='text-sm font-medium leading-relaxed text-slate-700'
						dangerouslySetInnerHTML={{ __html: highlightKeywords(explanation) }}
					/>
				</div>
			</div>
		</div>
	);
}
