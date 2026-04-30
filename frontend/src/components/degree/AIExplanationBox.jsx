import React from "react";

const SparkleIcon = () => (
	<svg className='w-6 h-6' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z'
		/>
	</svg>
);

const KEYWORDS = [
	"AI",
	"interest",
	"match",
	"eligible",
	"requires",
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
	"recommended",
];

function highlightText(text, extraKeywords = []) {
	// Strip any existing HTML from the input first
	const safe = text
		.replace(/<[^>]*>/g, "")
		.replace(/\s+/g, " ")
		.trim();

	const allKws = [...KEYWORDS, ...extraKeywords].filter(Boolean);
	if (allKws.length === 0) return safe;

	// Build ONE combined regex so each position is replaced at most once
	// (avoids re-processing already-injected <strong> tags)
	const escaped = allKws.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
	const combined = new RegExp(`\\b(${escaped.join("|")}s?)\\b`, "gi");

	return safe.replace(
		combined,
		(m) => `<strong class="bg-blue-100 text-blue-800 px-1 py-0.5 rounded font-bold">${m}</strong>`,
	);
}

export default function AIExplanationBox({ explanation = "", olMarks = null }) {
	if (!explanation || explanation.trim().length === 0) return null;

	// Extra keywords from student subjects
	const extras = [];
	if (olMarks?.core) {
		Object.keys(olMarks.core).forEach((k) => {
			if (!k.includes("bucket") && !k.includes("grade")) extras.push(k.replace(/_/g, " "));
		});
	}
	["bucket_1", "bucket_2", "bucket_3"].forEach((b) => {
		if (olMarks?.[b]) extras.push(olMarks[b].replace(/_/g, " "));
	});

	return (
		<div className='relative overflow-hidden border border-blue-200 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50'>
			{/* Ambient orb */}
			<div className='absolute w-16 h-16 rounded-full pointer-events-none -top-4 -right-4 bg-blue-300/20 blur-xl' />

			{/* Top accent stripe */}
			<div className='h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400' />

			<div className='flex items-start gap-3 px-4 pt-3'>
				{/* Icon */}
				<div className='flex-shrink-0 px-2 py-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-sm mt-0.5'>
					<SparkleIcon />
				</div>

				{/* Text */}
				<div className='flex-1 min-w-0'>
					<p className='mb-1.5 text-xs font-bold tracking-widest uppercase text-blue-600'>AI Insight</p>
					<p
						className='text-sm leading-relaxed text-slate-700'
						dangerouslySetInnerHTML={{ __html: highlightText(explanation, extras) }}
					/>
				</div>
			</div>
		</div>
	);
}
