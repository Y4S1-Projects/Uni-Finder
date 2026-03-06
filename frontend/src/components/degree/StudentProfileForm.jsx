import React, { useMemo, useState } from "react";
import {
	STREAMS,
	SRI_LANKA_AL_SUBJECTS,
	PHYSICAL_SCIENCE_INTERESTS,
	SRI_LANKA_DISTRICTS,
} from "../../constants/degreeConstants";
import {
	FaBook,
	FaGraduationCap,
	FaLightbulb,
	FaMapMarkerAlt,
	FaPlus,
	FaStar,
	FaTimes,
	FaTrophy,
} from "react-icons/fa";

const DEFAULT_SCENARIO_CONFIG = {
	showStream: true,
	requireStream: true,
	showZscore: true,
	requireZscore: false,
	showInterests: true,
	requireInterests: true,
	defaultInterests: "",
	defaultZscore: null,
};

export default function StudentProfileForm({
	initialValues,
	onSubmit,
	loading,
	scenarioConfig = DEFAULT_SCENARIO_CONFIG,
	submitLabel,
}) {
	const config = { ...DEFAULT_SCENARIO_CONFIG, ...scenarioConfig };
	const [stream, setStream] = useState(initialValues.stream);
	const [district, setDistrict] = useState(initialValues.district);
	const [zscore, setZscore] = useState(
		initialValues.zscore === undefined || initialValues.zscore === null || initialValues.zscore === "" ?
			""
		:	String(initialValues.zscore),
	);
	const [subjects, setSubjects] = useState(Array.isArray(initialValues.subjects) ? initialValues.subjects : []);
	const [interests, setInterests] = useState(initialValues.interests || "");
	const [subjectDraft, setSubjectDraft] = useState("");
	const [attemptedSubmit, setAttemptedSubmit] = useState(false);

	const errors = useMemo(() => {
		const next = {};
		const zText = String(zscore || "").trim();
		const z = zText === "" ? null : Number(zText);

		if (config.requireStream && !stream.trim()) next.stream = "Please select a stream.";
		if (!district.trim()) next.district = "Please select your district.";
		if (config.requireZscore && z === null) next.zscore = "Please enter your Z-score.";
		if (z !== null && !Number.isFinite(z)) next.zscore = "Please enter a valid Z-score.";
		else if (z !== null && (z < -3 || z > 3)) next.zscore = "Z-score must be between -3.0000 and +3.0000.";
		if (!Array.isArray(subjects) || subjects.length === 0) next.subjects = "Please add at least one subject.";
		if (config.requireInterests && !interests.trim()) next.interests = "Please select or type at least one interest.";

		return next;
	}, [
		config.requireInterests,
		config.requireStream,
		config.requireZscore,
		district,
		interests,
		stream,
		subjects,
		zscore,
	]);

	const canSubmit = Object.keys(errors).length === 0;

	const normalizedSubjects = useMemo(
		() => (Array.isArray(subjects) ? subjects : []).map((s) => String(s || "").trim()).filter(Boolean),
		[subjects],
	);

	const addSubject = (valueToAdd) => {
		const next = String(valueToAdd || "").trim();
		if (!next) return;
		if (normalizedSubjects.some((s) => s.toLowerCase() === next.toLowerCase())) {
			setSubjectDraft("");
			return;
		}
		setSubjects([...normalizedSubjects, next]);
		setSubjectDraft("");
	};

	const removeSubject = (subjectToRemove) => {
		setSubjects(normalizedSubjects.filter((s) => s !== subjectToRemove));
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		setAttemptedSubmit(true);

		if (!canSubmit) return;

		const normalizedInterests = interests.trim() || config.defaultInterests || "General university studies";
		const normalizedZscore = String(zscore || "").trim() === "" ? config.defaultZscore : Number(zscore);

		onSubmit({
			student: {
				stream: stream.trim(),
				subjects: normalizedSubjects,
				zscore: normalizedZscore,
				interests: normalizedInterests,
			},
			district: district.trim(),
		});
	};

	return (
		<form onSubmit={handleSubmit} className='p-8 bg-white border-2 border-purple-200 shadow-lg rounded-2xl'>
			{/* Two-column grid for core fields */}
			<div className='grid grid-cols-1 gap-6 mb-6 md:grid-cols-2'>
				{/* Stream */}
				{config.showStream ?
					<div>
						<label className='flex items-center gap-2 mb-3 text-lg font-semibold text-gray-800'>
							<FaGraduationCap className='text-purple-600' />
							<span>Stream</span>
							{config.requireStream ?
								<span className='text-red-500'>*</span>
							:	null}
						</label>
						<select
							value={stream}
							onChange={(e) => setStream(e.target.value)}
							disabled={loading}
							className={`w-full px-4 py-3 rounded-xl border-2 bg-white transition-colors focus:outline-none ${
								attemptedSubmit && errors.stream ?
									"border-red-300 focus:border-red-400"
								:	"border-gray-200 focus:border-purple-400"
							}`}>
							<option value=''>Select stream</option>
							{STREAMS.map((s) => (
								<option key={s} value={s}>
									{s}
								</option>
							))}
						</select>
						{attemptedSubmit && errors.stream ?
							<p className='mt-2 text-sm text-red-500'>{errors.stream}</p>
						:	null}
					</div>
				:	null}

				{/* District */}
				<div>
					<label className='flex items-center gap-2 mb-3 text-lg font-semibold text-gray-800'>
						<FaMapMarkerAlt className='text-purple-600' />
						<span>District</span>
						<span className='text-red-500'>*</span>
					</label>
					<select
						value={district}
						onChange={(e) => setDistrict(e.target.value)}
						disabled={loading}
						className={`w-full px-4 py-3 rounded-xl border-2 bg-white transition-colors focus:outline-none ${
							attemptedSubmit && errors.district ?
								"border-red-300 focus:border-red-400"
							:	"border-gray-200 focus:border-purple-400"
						}`}>
						<option value=''>Select district</option>
						{SRI_LANKA_DISTRICTS.map((d) => (
							<option key={d} value={d}>
								{d}
							</option>
						))}
					</select>
					{attemptedSubmit && errors.district ?
						<p className='mt-2 text-sm text-red-500'>{errors.district}</p>
					:	null}
				</div>

				{/* Z-Score */}
				{config.showZscore ?
					<div className='md:col-span-2'>
						<label className='flex items-center gap-2 mb-3 text-lg font-semibold text-gray-800'>
							<FaTrophy className='text-purple-600' />
							<span>Z-Score</span>
							{config.requireZscore ?
								<span className='text-red-500'>*</span>
							:	<span className='ml-2 text-sm font-normal text-gray-500'>(Optional)</span>}
						</label>
						<input
							type='number'
							step='0.0001'
							min={-3}
							max={3}
							value={zscore}
							onChange={(e) => setZscore(e.target.value)}
							placeholder='Optional (range -3.0000 to +3.0000)'
							disabled={loading}
							className={`w-full px-4 py-3 rounded-xl border-2 bg-white transition-colors focus:outline-none ${
								attemptedSubmit && errors.zscore ?
									"border-red-300 focus:border-red-400"
								:	"border-gray-200 focus:border-purple-400"
							}`}
						/>
						{!config.requireZscore ?
							<p className='flex items-start gap-2 mt-2 text-sm text-gray-500'>
								<FaLightbulb className='mt-0.5 flex-shrink-0 text-purple-600' />
								<span>Leave empty to ignore Z-score and recommend based on interests.</span>
							</p>
						:	null}
						{attemptedSubmit && errors.zscore ?
							<p className='mt-2 text-sm text-red-500'>{errors.zscore}</p>
						:	null}
					</div>
				:	null}
			</div>

			{/* Subjects */}
			<div className='mb-6'>
				<label className='flex items-center gap-2 mb-3 text-lg font-semibold text-gray-800'>
					<FaBook className='text-purple-600' />
					<span>A/L Subjects</span>
					<span className='text-red-500'>*</span>
					<span className='ml-2 text-sm font-normal text-gray-500'>(Add at least 1)</span>
				</label>
				<div className='flex flex-col gap-3 sm:flex-row'>
					<div className='flex-1 min-w-0'>
						<input
							value={subjectDraft}
							onChange={(e) => setSubjectDraft(e.target.value)}
							onKeyDown={(e) => {
								if (e.key === "Enter") {
									e.preventDefault();
									addSubject(subjectDraft);
								}
							}}
							placeholder='Type a subject (e.g., Physics)'
							disabled={loading}
							list='al-subjects'
							className={`w-full px-4 py-3 rounded-xl border-2 bg-white transition-colors focus:outline-none ${
								attemptedSubmit && errors.subjects ?
									"border-red-300 focus:border-red-400"
								:	"border-gray-200 focus:border-purple-400"
							}`}
						/>
						<datalist id='al-subjects'>
							{(SRI_LANKA_AL_SUBJECTS || []).map((s) => (
								<option key={s} value={s} />
							))}
						</datalist>
						<p className='mt-2 text-sm text-gray-500'>Pick from the list or type your own.</p>
					</div>
					<button
						type='button'
						onClick={() => addSubject(subjectDraft)}
						disabled={loading || String(subjectDraft || "").trim().length === 0}
						className='flex items-center justify-center gap-2 px-5 py-3 font-medium text-gray-700 bg-white border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'>
						<FaPlus className='text-purple-600' /> Add
					</button>
				</div>

				{attemptedSubmit && errors.subjects ?
					<p className='mt-2 text-sm text-red-500'>{errors.subjects}</p>
				:	null}

				{normalizedSubjects.length > 0 ?
					<div className='flex flex-wrap gap-2 mt-4'>
						{normalizedSubjects.map((s) => (
							<span
								key={s}
								className='inline-flex items-center gap-2 px-3 py-2 text-gray-700 bg-gray-100 border border-gray-200 rounded-full'>
								<span className='truncate max-w-[260px]'>{s}</span>
								<button
									type='button'
									onClick={() => removeSubject(s)}
									disabled={loading}
									className='text-gray-500 hover:text-gray-700 disabled:opacity-50'
									aria-label={`Remove ${s}`}>
									<FaTimes />
								</button>
							</span>
						))}
					</div>
				:	null}
			</div>

			{/* Interests */}
			{config.showInterests ?
				<div className='mb-6'>
					<label className='flex items-center gap-2 mb-3 text-lg font-semibold text-gray-800'>
						<FaStar className='text-purple-600' />
						<span>Interests</span>
						{config.requireInterests ?
							<span className='text-red-500'>*</span>
						:	null}
					</label>
					<input
						value={interests}
						onChange={(e) => setInterests(e.target.value)}
						placeholder='Type an interest (e.g., Computer Science)'
						disabled={loading}
						list='degree-interests'
						className={`w-full px-4 py-3 rounded-xl border-2 bg-white transition-colors focus:outline-none ${
							attemptedSubmit && errors.interests ?
								"border-red-300 focus:border-red-400"
							:	"border-gray-200 focus:border-purple-400"
						}`}
					/>
					<datalist id='degree-interests'>
						{(PHYSICAL_SCIENCE_INTERESTS || []).map((i) => (
							<option key={i} value={i} />
						))}
					</datalist>
					<p className='mt-2 text-sm text-gray-500'>Pick from the list or type your own interest.</p>
					{attemptedSubmit && errors.interests ?
						<p className='mt-2 text-sm text-red-500'>{errors.interests}</p>
					:	null}
				</div>
			:	null}

			{/* Submit */}
			<div className='flex items-center justify-end mt-6'>
				<button
					type='submit'
					disabled={!canSubmit || loading}
					className='px-6 py-3 font-semibold text-white transition-all duration-300 shadow-lg rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed'>
					{loading ? "Generating…" : submitLabel || "Get Degree Recommendations"}
				</button>
			</div>
		</form>
	);
}
