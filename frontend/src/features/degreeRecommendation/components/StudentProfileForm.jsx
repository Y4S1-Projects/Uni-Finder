import React, { useMemo, useState } from "react";
import { Button, Form, Row, Col } from "react-bootstrap";

const DEFAULT_STREAMS = ["Science", "Commerce", "Arts", "Technology"];

function normalizeSubjects(subjectsText) {
	return subjectsText
		.split(",")
		.map((s) => s.trim())
		.filter(Boolean);
}

export default function StudentProfileForm({ initialValues, onSubmit, loading }) {
	const [stream, setStream] = useState(initialValues.stream);
	const [district, setDistrict] = useState(initialValues.district);
	const [zscore, setZscore] = useState(String(initialValues.zscore));
	const [maxResults, setMaxResults] = useState(String(initialValues.max_results));
	const [interests, setInterests] = useState(initialValues.interests);
	const [subjectsText, setSubjectsText] = useState(initialValues.subjects.join(", "));

	const subjectsPreview = useMemo(() => normalizeSubjects(subjectsText), [subjectsText]);

	const canSubmit =
		stream.trim() &&
		district.trim() &&
		interests.trim() &&
		!Number.isNaN(Number(zscore)) &&
		Number(zscore) >= 0 &&
		Number(maxResults) >= 1;

	const handleSubmit = (e) => {
		e.preventDefault();

		if (!canSubmit) return;

		onSubmit({
			student: {
				stream: stream.trim(),
				subjects: subjectsPreview,
				zscore: Number(zscore),
				interests: interests.trim(),
			},
			district: district.trim(),
			max_results: Number(maxResults),
		});
	};

	return (
		<Form onSubmit={handleSubmit} className='w-full'>
			<Row className='g-3'>
				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Stream</Form.Label>
						<Form.Select value={stream} onChange={(e) => setStream(e.target.value)} required>
							<option value=''>Select stream</option>
							{DEFAULT_STREAMS.map((s) => (
								<option key={s} value={s}>
									{s}
								</option>
							))}
						</Form.Select>
					</Form.Group>
				</Col>

				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>District</Form.Label>
						<Form.Control
							value={district}
							onChange={(e) => setDistrict(e.target.value)}
							placeholder='e.g., Colombo'
							required
						/>
					</Form.Group>
				</Col>

				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Z-Score</Form.Label>
						<Form.Control
							type='number'
							step='0.0001'
							min='0'
							value={zscore}
							onChange={(e) => setZscore(e.target.value)}
							placeholder='e.g., 1.5000'
							required
						/>
					</Form.Group>
				</Col>

				<Col md={6}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Max Results</Form.Label>
						<Form.Control
							type='number'
							min='1'
							max='20'
							value={maxResults}
							onChange={(e) => setMaxResults(e.target.value)}
							required
						/>
					</Form.Group>
				</Col>

				<Col md={12}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Subjects</Form.Label>
						<Form.Control
							value={subjectsText}
							onChange={(e) => setSubjectsText(e.target.value)}
							placeholder='Comma-separated (e.g., Physics, Chemistry, Combined Mathematics)'
						/>
						<div className='mt-2 text-muted small'>
							Parsed: {subjectsPreview.length ? subjectsPreview.join(" • ") : "(none)"}
						</div>
					</Form.Group>
				</Col>

				<Col md={12}>
					<Form.Group>
						<Form.Label className='fw-semibold'>Interests</Form.Label>
						<Form.Control
							as='textarea'
							rows={3}
							value={interests}
							onChange={(e) => setInterests(e.target.value)}
							placeholder='e.g., computer science, software engineering, AI'
							required
						/>
					</Form.Group>
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
