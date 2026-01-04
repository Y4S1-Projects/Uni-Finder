import React from "react";
import { Card, ListGroup, Badge } from "react-bootstrap";

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
			<Card className='shadow-sm'>
				<Card.Body>
					<Card.Title className='mb-2'>Results</Card.Title>
					<div className='text-muted'>No eligible degree recommendations found.</div>
				</Card.Body>
			</Card>
		);
	}

	return (
		<Card className='shadow-sm'>
			<Card.Body>
				<div className='mb-3 d-flex align-items-center justify-content-between'>
					<Card.Title className='mb-0'>Recommendations</Card.Title>
					<Badge bg='secondary'>{results.length}</Badge>
				</div>
				<ListGroup variant='flush'>
					{results.map((item, idx) => (
						<ListGroup.Item key={`${item.degree_name || "degree"}-${idx}`}>
							<div className='gap-3 d-flex justify-content-between align-items-start'>
								<div className='min-w-0 flex-grow-1'>
									<div className='fw-semibold text-break'>{item.degree_name || "(Unnamed Degree)"}</div>
									{(item.metadata?.institute || item.metadata?.faculty) && (
										<div className='text-muted small text-break'>
											{item.metadata?.institute ? (
												<span>
													<span className='fw-semibold'>University:</span> {item.metadata.institute}
												</span>
											) : null}
											{item.metadata?.institute && item.metadata?.faculty ? " • " : null}
											{item.metadata?.faculty ? (
												<span>
													<span className='fw-semibold'>Faculty:</span> {item.metadata.faculty}
												</span>
											) : null}
										</div>
									)}
								</div>
								<div className='flex-shrink-0 text-end'>
									<div className='small text-muted'>Score</div>
									<div className='fw-bold'>{formatNumber(item.score)}</div>
								</div>
							</div>

							<div className='gap-3 mt-2 d-flex small text-muted'>
								<div>
									Similarity: <span className='fw-semibold'>{formatNumber(item.similarity)}</span>
								</div>
							</div>
						</ListGroup.Item>
					))}
				</ListGroup>
			</Card.Body>
		</Card>
	);
}
