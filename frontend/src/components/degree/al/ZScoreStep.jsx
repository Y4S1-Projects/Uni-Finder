import React from "react";
import { InfoIcon, ZScoreIcon } from "../../ui/DegreeIcons";

/**
 * ZScoreStep — Step 1 (optional)
 *
 * Props:
 *   zscore      – string value
 *   onChange    – (val: string) => void
 */
export default function ZScoreStep({ zscore, onChange }) {
	// allow numbers with optional leading -, optional decimal with up to 4 digits
	const DECIMAL_REGEX = /^-?\d*(?:\.\d{0,4})?$/;
	const numericValue = zscore === "" ? NaN : Number(zscore);
	const isValid =
		zscore !== "" &&
		DECIMAL_REGEX.test(zscore) &&
		!Number.isNaN(numericValue) &&
		numericValue >= -3 &&
		numericValue <= 3;

	const handleChange = (e) => {
		const val = e.target.value;

		// Always allow clearing
		if (val === "" || val === "-") {
			onChange(val);
			return;
		}

		// Reject anything that doesn't match the allowed format
		// Format: optional '-', digits, optional '.' followed by up to 4 decimal digits
		if (!DECIMAL_REGEX.test(val)) return;

		// Allow still-typing states like "-1." or "1." without blocking
		const endsWithDot = val.endsWith(".");
		if (!endsWithDot) {
			const n = Number(val);
			if (Number.isNaN(n)) return;
			// Hard block out-of-range
			if (n < -3 || n > 3) return;
		}

		onChange(val);
	};

	return (
		<div className='space-y-6'>
			{/* Header */}
			<div>
				<p className='mb-1 text-xs font-bold tracking-widest text-blue-600 uppercase'>Step 2 of 3 — Optional</p>
				<h2 className='mb-1 text-2xl font-extrabold tracking-tight text-slate-900'>What's Your Z-Score?</h2>
				<p className='text-sm text-slate-500'>
					Enter your A/L Z-score to see only courses you're eligible for. You can skip and view all courses.
				</p>
			</div>

			{/* Z-Score illustration card */}
			<div className='items-center border-2 border-blue-100 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl'>
				<div className='flex flex-row gap-4 px-5 pt-3'>
					<div className='flex items-center justify-center flex-shrink-0 w-12 h-12 text-blue-600 bg-blue-100 rounded-xl'>
						<ZScoreIcon className='w-6 h-6' />
					</div>
					<div className='flex flex-col justify-center flex-1'>
						<p className='text-sm font-bold text-blue-900'>What is a Z-Score?</p>
						<p className='-mt-2 text-xs leading-relaxed text-blue-700'>
							A standardized score (typically −3 to +3) used by the UGC to rank applicants for university admission.
						</p>
					</div>
				</div>
			</div>

			{/* Input */}
			<div>
				<label className='block mb-2 text-sm font-bold text-slate-800'>
					Z-Score <span className='font-normal text-slate-400'>(optional)</span>
				</label>
				<input
					type='text'
					inputMode='decimal'
					placeholder='e.g. 1.8500'
					value={zscore}
					onChange={handleChange}
					className={`
						w-full px-4 py-3 text-base border-2 rounded-xl transition-all duration-200 outline-none
						${
							isValid ? "border-blue-500 bg-blue-50/50 ring-2 ring-blue-100"
							: zscore !== "" && zscore !== "-" ? "border-red-300 bg-red-50/40 ring-2 ring-red-100"
							: "border-slate-200 bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
						}
					`}
				/>

				{/* Hint row */}
				<div className='flex items-center justify-between mt-1.5'>
					<p
						className={`text-xs font-medium ${
							isValid ? "text-blue-600"
							: zscore !== "" && zscore !== "-" ? "text-red-600"
							: "text-slate-400"
						}`}>
						{isValid ?
							"Z-Score recorded — we'll filter courses you're eligible for."
						: zscore !== "" && zscore !== "-" ?
							"Value must be between −3.0000 and +3.0000."
						:	"Range: −3.0000 to +3.0000, up to 4 decimal places"}
					</p>
					{zscore !== "" && zscore !== "-" && (
						<p className={`text-xs font-semibold tabular-nums ${isValid ? "text-blue-600" : "text-red-500"}`}>
							{zscore}
						</p>
					)}
				</div>
			</div>

			{/* Skip hint */}
			<div className='flex items-start gap-3 px-4 pt-3 border border-slate-200 rounded-xl bg-slate-50'>
				<InfoIcon className='flex-shrink-0 w-5 h-5' />
				<p className='text-sm text-slate-600'>
					<strong className='text-slate-800'>Don't have your Z-score yet?</strong> Hit{" "}
					<span className='font-semibold text-blue-600'>Skip</span> to explore all courses available in your stream — no
					Z-score required.
				</p>
			</div>
		</div>
	);
}
