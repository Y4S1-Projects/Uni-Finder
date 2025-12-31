import React, { useState, useEffect } from "react";
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from "react-bootstrap";
import "./BudgetOptimizer.css";

const API_GATEWAY = process.env.REACT_APP_API_GATEWAY_URL || "http://localhost:8080";
const BUDGET_API_BASE = `${API_GATEWAY}/budget-service`;

const BudgetOptimizer = () => {
	const [formData, setFormData] = useState({
		income: 30000,
		degree_type: "Engineering",
		location: "Colombo",
		semester: 5,
		target_savings_rate: 20,
	});

	const [predictionResult, setPredictionResult] = useState(null);
	const [optimizationResult, setOptimizationResult] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const [modelPerformance, setModelPerformance] = useState(null);

	useEffect(() => {
		// Load model performance on component mount
		fetchModelPerformance();
	}, []);

	const fetchModelPerformance = async () => {
		try {
			const response = await fetch(`${BUDGET_API_BASE}/api/model/performance`);
			if (response.ok) {
				const result = await response.json();
				setModelPerformance(result.performance);
			}
		} catch (error) {
			console.log("Model performance check failed:", error);
		}
	};

	const handleInputChange = (e) => {
		const { name, value } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: ["income", "semester", "target_savings_rate"].includes(name) ? parseInt(value) : value,
		}));
	};

	const predictExpenses = async () => {
		setLoading(true);
		setError(null);

		try {
			const dataToSend = {
				...formData,
				month: new Date().getMonth() + 1,
				year: new Date().getFullYear(),
			};

			const response = await fetch(`${BUDGET_API_BASE}/api/budget/predict`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(dataToSend),
			});

			if (response.ok) {
				const result = await response.json();
				const normalized = result.prediction || result;
				setPredictionResult({
					predicted_total_expenses: normalized.predicted_total_expenses || normalized.predicted_budget || 0,
					confidence: normalized.confidence || normalized.accuracy || 0,
					prediction_date: normalized.prediction_date || new Date().toISOString(),
				});
				setOptimizationResult(null); // Clear optimization when new prediction is made
			} else {
				const errorData = await response.json();
				setError(errorData.error || "Failed to predict expenses");
			}
		} catch (error) {
			setError("Network error. Please check if the backend server is running.");
		} finally {
			setLoading(false);
		}
	};

	const optimizeBudget = async () => {
		setLoading(true);
		setError(null);

		try {
			const dataToSend = {
				...formData,
				target_savings_rate: formData.target_savings_rate / 100, // Convert percentage to decimal
				month: new Date().getMonth() + 1,
				year: new Date().getFullYear(),
			};

			const response = await fetch(`${BUDGET_API_BASE}/api/budget/complete-analysis`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(dataToSend),
			});

			if (response.ok) {
				const result = await response.json();
				const financial = result.financial_summary || {};
				const breakdown = result.expense_breakdown || {};
				setOptimizationResult({
					total_expenses: financial.total_expenses,
					projected_savings: financial.monthly_savings,
					target_savings_rate: (financial.savings_rate || 0) / 100,
					optimized_budget: breakdown,
				});
				setPredictionResult(null); // Clear prediction when new optimization is made
			} else {
				const errorData = await response.json();
				setError(errorData.error || "Failed to optimize budget");
			}
		} catch (error) {
			setError("Network error. Please check if the backend server is running.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className='budget-optimizer-page'>
			<Container className='my-5'>
				{/* Header */}
				<Row className='mb-5'>
					<Col>
						<div className='text-center'>
							<h1 className='display-4 gradient-text mb-3'>🎯 AI-Powered Student Budget Optimizer</h1>
							<p className='lead text-muted'>Component 2 of UniFinder LK Platform | Designed for Sri Lankan Students</p>
							{modelPerformance && modelPerformance.status === "ready" && (
								<Alert variant='success' className='d-inline-block'>
									✅ AI Models Ready | Accuracy: {modelPerformance.accuracy_metrics?.expense_prediction?.accuracy}%
								</Alert>
							)}
						</div>
					</Col>
				</Row>

				<Row>
					{/* Input Form */}
					<Col lg={6}>
						<Card className='shadow-lg border-0 mb-4'>
							<Card.Header className='bg-gradient-primary text-white'>
								<h4 className='mb-0'>📋 Student Profile</h4>
							</Card.Header>
							<Card.Body className='p-4'>
								<Form>
									<Row>
										<Col md={6}>
											<Form.Group className='mb-3'>
												<Form.Label>
													<strong>Monthly Income (LKR) *</strong>
												</Form.Label>
												<Form.Control
													type='number'
													name='income'
													value={formData.income}
													onChange={handleInputChange}
													required
												/>
											</Form.Group>
										</Col>
										<Col md={6}>
											<Form.Group className='mb-3'>
												<Form.Label>
													<strong>Current Semester</strong>
												</Form.Label>
												<Form.Select name='semester' value={formData.semester} onChange={handleInputChange}>
													{[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => (
														<option key={sem} value={sem}>
															Semester {sem}
														</option>
													))}
												</Form.Select>
											</Form.Group>
										</Col>
									</Row>

									<Row>
										<Col md={6}>
											<Form.Group className='mb-3'>
												<Form.Label>
													<strong>Degree Type</strong>
												</Form.Label>
												<Form.Select name='degree_type' value={formData.degree_type} onChange={handleInputChange}>
													<option value='Engineering'>Engineering</option>
													<option value='Medicine'>Medicine</option>
													<option value='Arts'>Arts</option>
													<option value='Science'>Science</option>
													<option value='Commerce'>Commerce</option>
													<option value='Law'>Law</option>
												</Form.Select>
											</Form.Group>
										</Col>
										<Col md={6}>
											<Form.Group className='mb-3'>
												<Form.Label>
													<strong>Location</strong>
												</Form.Label>
												<Form.Select name='location' value={formData.location} onChange={handleInputChange}>
													<option value='Colombo'>Colombo</option>
													<option value='Kandy'>Kandy</option>
													<option value='Galle'>Galle</option>
													<option value='Jaffna'>Jaffna</option>
													<option value='Matara'>Matara</option>
													<option value='Ratnapura'>Ratnapura</option>
												</Form.Select>
											</Form.Group>
										</Col>
									</Row>

									<Form.Group className='mb-4'>
										<Form.Label>
											<strong>Target Savings Rate (%)</strong>
										</Form.Label>
										<Form.Control
											type='number'
											name='target_savings_rate'
											value={formData.target_savings_rate}
											onChange={handleInputChange}
											min='0'
											max='50'
										/>
									</Form.Group>

									<div className='d-grid gap-2'>
										<Button variant='primary' size='lg' onClick={predictExpenses} disabled={loading} className='mb-2'>
											{loading ? <Spinner animation='border' size='sm' className='me-2' /> : "📊"}
											Predict Expenses
										</Button>
										<Button variant='success' size='lg' onClick={optimizeBudget} disabled={loading}>
											{loading ? <Spinner animation='border' size='sm' className='me-2' /> : "💰"}
											Optimize Budget
										</Button>
									</div>
								</Form>
							</Card.Body>
						</Card>
					</Col>

					{/* Results */}
					<Col lg={6}>
						{error && (
							<Alert variant='danger' className='mb-4'>
								<Alert.Heading>❌ Error</Alert.Heading>
								{error}
							</Alert>
						)}

						{predictionResult && (
							<Card className='shadow-lg border-0 mb-4'>
								<Card.Header className='bg-gradient-info text-white'>
									<h4 className='mb-0'>📊 Expense Prediction Results</h4>
								</Card.Header>
								<Card.Body>
									<div className='result-metric'>
										<div className='d-flex justify-content-between align-items-center py-2 border-bottom'>
											<span>
												<strong>Predicted Monthly Expenses:</strong>
											</span>
											<span className='fs-4 fw-bold text-primary'>
												LKR {predictionResult.predicted_total_expenses?.toLocaleString()}
											</span>
										</div>
										<div className='d-flex justify-content-between align-items-center py-2 border-bottom'>
											<span>Model Confidence:</span>
											<span className='fw-bold'>{predictionResult.confidence}%</span>
										</div>
										<div className='d-flex justify-content-between align-items-center py-2'>
											<span>Prediction Date:</span>
											<span>{new Date(predictionResult.prediction_date).toLocaleString()}</span>
										</div>
									</div>
								</Card.Body>
							</Card>
						)}

						{optimizationResult && (
							<Card className='shadow-lg border-0 mb-4'>
								<Card.Header className='bg-gradient-success text-white'>
									<h4 className='mb-0'>💰 Budget Optimization Results</h4>
								</Card.Header>
								<Card.Body>
									<div className='result-metric mb-3'>
										<div className='d-flex justify-content-between align-items-center py-2 border-bottom'>
											<span>
												<strong>Total Optimized Expenses:</strong>
											</span>
											<span className='fs-4 fw-bold text-success'>
												LKR {optimizationResult.total_expenses?.toLocaleString()}
											</span>
										</div>
										<div className='d-flex justify-content-between align-items-center py-2 border-bottom'>
											<span>
												<strong>Projected Savings:</strong>
											</span>
											<span className='fs-4 fw-bold text-success'>
												LKR {optimizationResult.projected_savings?.toLocaleString()}
											</span>
										</div>
										<div className='d-flex justify-content-between align-items-center py-2'>
											<span>Target Savings Rate:</span>
											<span className='fw-bold'>{(optimizationResult.target_savings_rate * 100).toFixed(1)}%</span>
										</div>
									</div>

									<h5 className='mt-4 mb-3'>📋 Optimized Budget Breakdown:</h5>
									{optimizationResult.optimized_budget &&
										Object.entries(optimizationResult.optimized_budget).map(([category, amount]) => {
											const percentage = ((amount / optimizationResult.total_expenses) * 100).toFixed(1);
											return (
												<div
													key={category}
													className='d-flex justify-content-between align-items-center py-2 border-bottom'>
													<span>
														<strong>{category.charAt(0).toUpperCase() + category.slice(1)}:</strong>
													</span>
													<span className='fw-bold'>
														LKR {amount?.toLocaleString()} ({percentage}%)
													</span>
												</div>
											);
										})}
								</Card.Body>
							</Card>
						)}
					</Col>
				</Row>

				{/* Sri Lanka Context */}
				<Row className='mt-5'>
					<Col>
						<Card className='border-0 bg-light'>
							<Card.Body className='p-4'>
								<h4 className='text-center mb-4'>🇱🇰 Sri Lanka-Specific Features</h4>
								<Row>
									<Col md={3} className='text-center mb-3'>
										<div className='feature-icon mb-2'>💰</div>
										<h6>LKR Currency</h6>
										<small className='text-muted'>Local currency calculations</small>
									</Col>
									<Col md={3} className='text-center mb-3'>
										<div className='feature-icon mb-2'>🏙️</div>
										<h6>City-specific Costs</h6>
										<small className='text-muted'>Colombo, Kandy, Galle data</small>
									</Col>
									<Col md={3} className='text-center mb-3'>
										<div className='feature-icon mb-2'>🎓</div>
										<h6>Student Patterns</h6>
										<small className='text-muted'>Academic calendar aligned</small>
									</Col>
									<Col md={3} className='text-center mb-3'>
										<div className='feature-icon mb-2'>📈</div>
										<h6>86.89% Accuracy</h6>
										<small className='text-muted'>AI-powered predictions</small>
									</Col>
								</Row>
							</Card.Body>
						</Card>
					</Col>
				</Row>
			</Container>
		</div>
	);
};

export default BudgetOptimizer;
