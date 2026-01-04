import React, { useMemo, useState } from "react";
import { Button, Form, Row, Col } from "react-bootstrap";
import DropdownSearchSelect from "../ui/DropdownSearchSelect";
import MultiSelectDropdown from "../ui/MultiSelectDropdown";
import {
	STREAMS,
	SRI_LANKA_AL_SUBJECTS,
	PHYSICAL_SCIENCE_INTERESTS,
	SRI_LANKA_DISTRICTS,
} from "../../constants/degreeConstants";

export default function StudentProfileForm({ initialValues, onSubmit, loading }) {
	const [stream, setStream] = useState(initialValues.stream);
	const [district, setDistrict] = useState(initialValues.district);
	const [zscore, setZscore] = useState(
		initialValues.zscore === undefined || initialValues.zscore === null || initialValues.zscore === ""
			? ""
			: String(initialValues.zscore)
	);
	const [subjects, setSubjects] = useState(Array.isArray(initialValues.subjects) ? initialValues.subjects : []);
	const [interests, setInterests] = useState(initialValues.interests || "");
	const [attemptedSubmit, setAttemptedSubmit] = useState(false);

	const errors = useMemo(() => {
		const next = {};
		const zText = String(zscore || "").trim();
		const z = zText === "" ? null : Number(zText);

		if (!stream.trim()) next.stream = "Please select a stream.";
		if (!district.trim()) next.district = "Please select your district.";
		if (z !== null && !Number.isFinite(z)) next.zscore = "Please enter a valid Z-score.";
		else if (z !== null && (z < -3 || z > 3)) next.zscore = "Z-score must be between -3.0000 and +3.0000.";
		if (!Array.isArray(subjects) || subjects.length === 0) next.subjects = "Please add at least one subject.";
		if (!interests.trim()) next.interests = "Please select or type at least one interest.";

		return next;
	}, [district, interests, stream, subjects, zscore]);

	const canSubmit = Object.keys(errors).length === 0;

	const handleSubmit = (e) => {
		e.preventDefault();
		setAttemptedSubmit(true);

		if (!canSubmit) return;

		onSubmit({
			student: {
				stream: stream.trim(),
				subjects,
				zscore: String(zscore || "").trim() === "" ? null : Number(zscore),
				interests: interests.trim(),
			},
			district: district.trim(),
		});
	};

	return (
		<Form onSubmit={handleSubmit} className=''>
			<Row className='g-3'>
				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Stream</Form.Label>
						<Form.Select
							value={stream}
							onChange={(e) => setStream(e.target.value)}
							required
							isInvalid={attemptedSubmit && Boolean(errors.stream)}
							disabled={loading}>
							<option value=''>Select stream</option>
							{STREAMS.map((s) => (
								<option key={s} value={s}>
									{s}
								</option>
							))}
						</Form.Select>
						{attemptedSubmit && errors.stream ? (
							<Form.Control.Feedback type='invalid'>{errors.stream}</Form.Control.Feedback>
						) : null}
					</Form.Group>
				</Col>

				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>District</Form.Label>
						<Form.Select
							value={district}
							onChange={(e) => setDistrict(e.target.value)}
							required
							disabled={loading}
							isInvalid={attemptedSubmit && Boolean(errors.district)}>
							<option value=''>Select district</option>
							{SRI_LANKA_DISTRICTS.map((d) => (
								<option key={d} value={d}>
									{d}
								</option>
							))}
						</Form.Select>
						{attemptedSubmit && errors.district ? (
							<Form.Control.Feedback type='invalid'>{errors.district}</Form.Control.Feedback>
						) : null}
					</Form.Group>
				</Col>

				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Z-Score</Form.Label>
						<Form.Control
							type='number'
							step='0.0001'
							min='-3'
							max='3'
							value={zscore}
							onChange={(e) => setZscore(e.target.value)}
							placeholder='Optional (range -3.0000 to +3.0000)'
							disabled={loading}
							isInvalid={attemptedSubmit && Boolean(errors.zscore)}
						/>
						<Form.Text className='mt-1 text-muted d-block'>
							Leave empty to ignore Z-score and view recommendations based on interests.
						</Form.Text>
						{attemptedSubmit && errors.zscore ? (
							<Form.Control.Feedback type='invalid'>{errors.zscore}</Form.Control.Feedback>
						) : null}
					</Form.Group>
				</Col>

				<Col md={12}>
					<MultiSelectDropdown
						label='A/L Subjects'
						values={subjects}
						onChange={setSubjects}
						options={SRI_LANKA_AL_SUBJECTS}
						placeholder='Click to see all subjects (you can also type to search)'
						required
						disabled={loading}
						error={attemptedSubmit ? errors.subjects : ""}
						helpText='Select the subjects you sat for at A/L (you can add multiple).'
						addLabel='Add'
					/>
				</Col>

				<Col md={12}>
					<DropdownSearchSelect
						label='Interests'
						value={interests}
						onChange={setInterests}
						options={PHYSICAL_SCIENCE_INTERESTS}
						placeholder='Click to see all interests (you can also type to search)'
						required
						disabled={loading}
						error={attemptedSubmit ? errors.interests : ""}
						helpText='Pick from the list or type your own interest.'
					/>
				</Col>

				<Col md={12} className='d-flex justify-content-end'>
					<Button type='submit' variant='success' disabled={!canSubmit || loading} className='px-4'>
						{loading ? "Generating..." : "Get Degree Recommendations"}
					</Button>
				</Col>
			</Row>
		</Form>
	);
}
