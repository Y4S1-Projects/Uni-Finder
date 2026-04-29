import React from "react";
import { AL_STREAMS } from "../../../constants/degreeConstants";
import { StreamIcon } from "./StreamIcons";
import { SRI_LANKA_DISTRICTS } from "../../../constants/degreeConstants";

// ── Inline SVG helpers ────────────────────────────────────────────────────────
const CheckIcon = () => (
	<svg className='w-3.5 h-3.5' fill='none' stroke='currentColor' strokeWidth='3' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
	</svg>
);

const MapPinIcon = () => (
	<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path strokeLinecap='round' strokeLinejoin='round' d='M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z' />
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z'
		/>
	</svg>
);

const InfoIcon = () => (
	<svg className='flex-shrink-0 w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z'
		/>
	</svg>
);

const AlertIcon = () => (
	<svg className='flex-shrink-0 w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
		<path
			strokeLinecap='round'
			strokeLinejoin='round'
			d='M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z'
		/>
	</svg>
);

// ── StreamSelector ────────────────────────────────────────────────────────────
/**
 * Step 0 — Stream, Subjects, and District selection.
 *
 * Props:
 *   formData        – { stream, subjects, district }
 *   setFormData     – state setter
 *   subjectRuleError – validation error string (from parent)
 */
export default function StreamSelector({ formData, setFormData, subjectRuleError }) {
	const selectedStream = AL_STREAMS.find((s) => s.name === formData.stream);

	const handleStreamSelect = (stream) => {
		setFormData((prev) => ({ ...prev, stream: stream.name, subjects: [] }));
	};

	const toggleSubject = (subject) => {
		if (formData.subjects.includes(subject)) {
			setFormData((prev) => ({ ...prev, subjects: prev.subjects.filter((s) => s !== subject) }));
		} else if (formData.subjects.length < 3) {
			setFormData((prev) => ({ ...prev, subjects: [...prev.subjects, subject] }));
		}
	};

	const subjectCount = formData.subjects.length;

	return (
		<div className='space-y-8'>
			{/* ── Stream selection ── */}
			<div>
				<p className='mb-1 text-xs font-bold tracking-widest text-blue-600 uppercase'>Step 1 of 3</p>
				<h2 className='mb-1 text-2xl font-extrabold tracking-tight text-slate-900'>Choose Your A/L Stream</h2>
				<p className='text-sm text-slate-500'>
					Select the stream you're studying — subjects will update automatically.
				</p>
			</div>

			<div className='grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3'>
				{AL_STREAMS.map((stream) => {
					const isSelected = formData.stream === stream.name;
					return (
						<button
							key={stream.id}
							onClick={() => handleStreamSelect(stream)}
							className={`
								relative p-4 rounded-2xl border-2 text-left transition-all duration-200
								hover:-translate-y-0.5 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-400
								${
									isSelected ?
										"border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-lg shadow-blue-100"
									:	"border-slate-200 bg-white hover:border-blue-300"
								}
							`}>
							{/* Icon */}
							<div
								className={`inline-flex items-center justify-center w-10 h-10 mb-3 rounded-xl bg-gradient-to-br ${stream.accentFrom} ${stream.accentTo} text-white shadow-sm`}>
								<StreamIcon iconKey={stream.icon} className='w-5 h-5' />
							</div>

							<h3
								className={`font-bold text-sm leading-tight mb-0.5 ${isSelected ? "text-blue-900" : "text-slate-800"}`}>
								{stream.name}
							</h3>
							<p className='text-xs leading-snug text-slate-500'>{stream.tagline}</p>

							{/* Selected check */}
							{isSelected && (
								<div className='absolute flex items-center justify-center w-5 h-5 text-white bg-blue-600 rounded-full shadow-sm top-3 right-3'>
									<CheckIcon />
								</div>
							)}
						</button>
					);
				})}
			</div>

			{/* ── Subject selection (after stream chosen) ── */}
			{formData.stream && selectedStream && (
				<div className='pt-6 border-t border-slate-100'>
					{/* Header */}
					<div className='flex items-center justify-between mb-4'>
						<div>
							<h3 className='text-base font-extrabold text-slate-900'>Select Your 3 Subjects</h3>
							<p className='text-xs text-slate-500 mt-0.5'>
								From the <span className='font-semibold text-blue-600'>{selectedStream.name}</span> stream
							</p>
						</div>

						{/* Counter badge */}
						<div
							className={`px-3 py-1.5 rounded-xl text-sm font-extrabold border transition-all ${
								subjectCount === 3 ?
									"bg-blue-600 text-white border-blue-700 shadow-sm"
								:	"bg-slate-100 text-slate-600 border-slate-200"
							}`}>
							{subjectCount}/3
						</div>
					</div>

					{/* Subject chips */}
					<div className='grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3'>
						{selectedStream.availableSubjects.map((subject) => {
							const isChosen = formData.subjects.includes(subject);
							const isDisabled = subjectCount >= 3 && !isChosen;

							return (
								<button
									key={subject}
									onClick={() => toggleSubject(subject)}
									disabled={isDisabled}
									className={`
										p-2.5 rounded-xl border-2 text-left text-xs font-semibold transition-all duration-150
										${
											isChosen ? "border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-900 shadow-sm"
											: isDisabled ? "border-slate-200 bg-slate-50 text-slate-400 cursor-not-allowed opacity-60"
											: "border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:bg-blue-50 cursor-pointer"
										}
									`}>
									<div className='flex items-center gap-2'>
										<div
											className={`w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all ${
												isChosen ? "border-blue-500 bg-blue-600" : "border-slate-300 bg-white"
											}`}>
											{isChosen && (
												<svg
													className='w-2.5 h-2.5 text-white'
													fill='none'
													stroke='currentColor'
													strokeWidth='3'
													viewBox='0 0 24 24'>
													<path strokeLinecap='round' strokeLinejoin='round' d='M4.5 12.75l6 6 9-13.5' />
												</svg>
											)}
										</div>
										<span className='leading-tight'>{subject}</span>
									</div>
								</button>
							);
						})}
					</div>

					{/* Validation feedback */}
					<div className='mt-4 space-y-2'>
						{subjectCount < 3 && (
							<div className='flex items-start gap-2 px-4 py-3 text-xs font-medium text-blue-800 border border-blue-200 rounded-xl bg-blue-50'>
								<InfoIcon />
								<span>
									Select{" "}
									<strong>
										{3 - subjectCount} more subject{3 - subjectCount !== 1 ? "s" : ""}
									</strong>{" "}
									to continue.
								</span>
							</div>
						)}

						{subjectCount === 3 && !subjectRuleError && (
							<div className='flex items-start gap-2 px-4 py-3 text-xs font-medium border rounded-xl bg-emerald-50 border-emerald-200 text-emerald-800'>
								<CheckIcon />
								<span>
									<strong>Valid combination:</strong> {formData.subjects.join(", ")}
								</span>
							</div>
						)}

						{subjectCount === 3 && subjectRuleError && (
							<div className='flex items-start gap-2 px-4 py-3 text-xs font-medium text-red-800 border border-red-200 rounded-xl bg-red-50'>
								<AlertIcon />
								<span>
									<strong>Invalid:</strong> {subjectRuleError}
								</span>
							</div>
						)}
					</div>
				</div>
			)}

			{/* ── District ── */}
			<div className='pt-4 border-t border-slate-100'>
				<label className='flex items-center gap-2 mb-2 text-sm font-bold text-slate-800'>
					<span className='p-1 text-blue-600 bg-blue-100 rounded-md'>
						<MapPinIcon />
					</span>
					District of Residence
				</label>
				<div className='relative'>
					<select
						value={formData.district}
						onChange={(e) => setFormData((prev) => ({ ...prev, district: e.target.value }))}
						className='w-full px-4 py-3 pr-10 text-sm transition-colors bg-white border-2 appearance-none text-slate-800 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none'>
						<option value=''>Select your district…</option>
						{SRI_LANKA_DISTRICTS.map((d) => (
							<option key={d} value={d}>
								{d}
							</option>
						))}
					</select>
					{/* Custom arrow */}
					<div className='absolute inset-y-0 flex items-center pointer-events-none right-3 text-slate-400'>
						<svg className='w-4 h-4' fill='none' stroke='currentColor' strokeWidth='2' viewBox='0 0 24 24'>
							<path strokeLinecap='round' strokeLinejoin='round' d='m19.5 8.25-7.5 7.5-7.5-7.5' />
						</svg>
					</div>
				</div>
			</div>
		</div>
	);
}
