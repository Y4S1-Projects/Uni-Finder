import React, { useState } from "react";
import { Container, Row, Col, Card, Alert, Spinner } from "react-bootstrap";
import StudentProfileForm from "../components/degree/StudentProfileForm";
import RecommendationsResults from "../components/degree/RecommendationsResults";
import { fetchDegreeRecommendations } from "../api/degreeRecommendationApi";

const DEFAULT_FORM = {
	stream: "Science",
	subjects: ["Physics", "Chemistry", "Combined Mathematics"],
	zscore: "",
	interests: "Computer Science",
	district: "Colombo",
};

export default function DegreeRecommendationsPage() {
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [results, setResults] = useState(null);

	const handleSubmit = async (payload) => {
		setLoading(true);
		setError("");
		setResults(null);

		try {
			const data = await fetchDegreeRecommendations(payload);
			setResults(data);
		} catch (err) {
			setError("Failed to fetch degree recommendations. Please ensure API Gateway and degree service are running.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className='py-4 py-lg-5'>
			<Container>
				<Row className='justify-content-center'>
					<Col lg={10} xl={9}>
						<Card className='shadow'>
							<Card.Body>
								<div className='flex-wrap gap-3 px-4 d-flex align-items-start justify-content-between'>
									<div>
										<h2 className='mb-1 h4 fw-bold'>Degree Recommendations</h2>
										<div className='text-muted'>Enter student details to get AI-powered degree suggestions.</div>
									</div>
								</div>

								<hr className='my-4' />

								<StudentProfileForm initialValues={DEFAULT_FORM} onSubmit={handleSubmit} loading={loading} />

								{error && (
									<Alert variant='danger' className='mt-4 mb-0'>
										{error}
									</Alert>
								)}

								{loading && (
									<div className='gap-2 mt-4 d-flex align-items-center text-muted'>
										<Spinner animation='border' size='sm' />
										<span>Generating recommendations...</span>
									</div>
								)}
							</Card.Body>
						</Card>

						<div className='mt-4'>
							<RecommendationsResults results={results} />
						</div>
					</Col>
				</Row>
			</Container>
		</div>
	);
}
