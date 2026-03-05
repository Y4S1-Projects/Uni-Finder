import React from "react";
import { useNavigate } from "react-router-dom";
import { Container, Row, Col, Button } from "react-bootstrap";
import "./home.css";

const HomePage = () => {
	const navigate = useNavigate();

	const handleGetStarted = () => {
		navigate("/keywords"); // Navigate to the keywords page
	};

	const handleBudgetOptimizer = () => {
		// Navigate to the budget optimizer page within the frontend
		navigate("/budget-optimizer-new");
	};

	const handleDegreeRecommendations = () => {
		navigate("/degree-recommendations");
	};

	const handleScholarshipMatcher = () => {
		window.location.href = "http://localhost:3001/scholarship-matcher";
	};

	const handleCareerPredictor = () => {
		navigate("/career");
	};

	return (
		<div className='homepage-container'>
			{/* Professional Header Section */}
			<section
				className='hero-header'
				style={{
					background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
					minHeight: "100vh",
					display: "flex",
					alignItems: "center",
					color: "white",
					position: "relative",
					overflow: "hidden",
				}}>
				{/* Background Pattern */}
				<div
					style={{
						position: "absolute",
						top: 0,
						left: 0,
						right: 0,
						bottom: 0,
						opacity: 0.1,
						backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Ccircle cx='7' cy='7' r='7'/%3E%3Ccircle cx='53' cy='7' r='7'/%3E%3Ccircle cx='7' cy='53' r='7'/%3E%3Ccircle cx='53' cy='53' r='7'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
					}}
				/>

				<Container>
					<Row className='align-items-center min-vh-100'>
						{/* Left Side - Vertical Header Content */}
						<Col lg={6} className='header-content'>
							<div
								className='header-left'
								style={{
									display: "flex",
									flexDirection: "column",
									justifyContent: "center",
									height: "80vh",
									paddingRight: "2rem",
								}}>
								<div className='mb-4 brand-logo'>
									<div
										style={{
											width: "80px",
											height: "80px",
											background: "rgba(255,255,255,0.2)",
											borderRadius: "20px",
											display: "flex",
											alignItems: "center",
											justifyContent: "center",
											fontSize: "36px",
											marginBottom: "20px",
											backdropFilter: "blur(10px)",
											border: "1px solid rgba(255,255,255,0.3)",
										}}>
										🎓
									</div>
								</div>

								<h1
									className='mb-4 display-4 fw-bold'
									style={{
										fontSize: "clamp(2.5rem, 5vw, 4rem)",
										lineHeight: "1.2",
										textShadow: "2px 2px 4px rgba(0,0,0,0.3)",
									}}>
									AI-Powered
									<br />
									<span style={{ color: "#ffd700" }}>Educational</span>
									<br />
									Guidance Platform
								</h1>

								<p
									className='mb-4 lead'
									style={{
										fontSize: "1.25rem",
										opacity: 0.9,
										maxWidth: "500px",
									}}>
									Empowering Sri Lankan students with data-driven insights for academic and career success through
									cutting-edge AI technology
								</p>

								<div className='mb-4 cta-buttons'>
									<Button
										variant='light'
										size='lg'
										onClick={handleGetStarted}
										className='mb-3 me-3'
										style={{
											borderRadius: "50px",
											padding: "12px 30px",
											fontWeight: "600",
											boxShadow: "0 4px 15px rgba(0,0,0,0.2)",
											transition: "all 0.3s ease",
										}}>
										🚀 Explore Our Solutions
									</Button>
									<Button
										variant='outline-light'
										size='lg'
										className='mb-3'
										style={{
											borderRadius: "50px",
											padding: "12px 30px",
											fontWeight: "600",
											borderWidth: "2px",
										}}>
										📊 View Research
									</Button>
								</div>

								{/* Statistics Bar */}
								<div
									className='stats-bar'
									style={{
										display: "flex",
										gap: "2rem",
										marginTop: "2rem",
										flexWrap: "wrap",
									}}>
									<div className='text-center stat-item'>
										<div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ffd700" }}>350K+</div>
										<div style={{ fontSize: "0.9rem", opacity: 0.8 }}>A/L Candidates</div>
									</div>
									<div className='text-center stat-item'>
										<div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ffd700" }}>4</div>
										<div style={{ fontSize: "0.9rem", opacity: 0.8 }}>AI Modules</div>
									</div>
									<div className='text-center stat-item'>
										<div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ffd700" }}>95%</div>
										<div style={{ fontSize: "0.9rem", opacity: 0.8 }}>Accuracy</div>
									</div>
								</div>
							</div>
						</Col>

						{/* Right Side - Visual Elements */}
						<Col lg={6} className='d-none d-lg-block'>
							<div
								className='header-visual'
								style={{
									display: "flex",
									flexDirection: "column",
									alignItems: "center",
									height: "80vh",
									justifyContent: "center",
								}}>
								{/* Floating Cards Animation */}
								<div style={{ position: "relative", width: "100%", height: "600px" }}>
									<div
										className='floating-card'
										style={{
											position: "absolute",
											top: "30px",
											right: "50px",
											width: "200px",
											height: "120px",
											background: "rgba(255,255,255,0.2)",
											borderRadius: "15px",
											backdropFilter: "blur(10px)",
											border: "1px solid rgba(255,255,255,0.3)",
											display: "flex",
											flexDirection: "column",
											alignItems: "center",
											justifyContent: "center",
											animation: "float 6s ease-in-out infinite",
											cursor: "pointer",
											transition: "all 0.3s ease",
										}}
										onClick={handleDegreeRecommendations}
										onMouseEnter={(e) => {
											e.currentTarget.style.transform = "scale(1.05)";
											e.currentTarget.style.background = "rgba(255,255,255,0.3)";
										}}
										onMouseLeave={(e) => {
											e.currentTarget.style.transform = "scale(1)";
											e.currentTarget.style.background = "rgba(255,255,255,0.2)";
										}}>
										<div style={{ fontSize: "2rem", marginBottom: "10px" }}>🎯</div>
										<div style={{ fontSize: "0.9rem", fontWeight: "600" }}>Degree Recommendations</div>
										<div style={{ fontSize: "0.7rem", opacity: 0.8, marginTop: "5px" }}>Click to Launch</div>
									</div>

									<div
										className='floating-card'
										style={{
											position: "absolute",
											top: "170px",
											left: "20px",
											width: "200px",
											height: "120px",
											background: "rgba(255,255,255,0.2)",
											borderRadius: "15px",
											backdropFilter: "blur(10px)",
											border: "1px solid rgba(255,255,255,0.3)",
											display: "flex",
											flexDirection: "column",
											alignItems: "center",
											justifyContent: "center",
											animation: "float 6s ease-in-out infinite 2s",
											cursor: "pointer",
											transition: "all 0.3s ease",
										}}
										onClick={handleBudgetOptimizer}
										onMouseEnter={(e) => {
											e.currentTarget.style.transform = "scale(1.05)";
											e.currentTarget.style.background = "rgba(255,255,255,0.3)";
										}}
										onMouseLeave={(e) => {
											e.currentTarget.style.transform = "scale(1)";
											e.currentTarget.style.background = "rgba(255,255,255,0.2)";
										}}>
										<div style={{ fontSize: "2rem", marginBottom: "10px" }}>💰</div>
										<div style={{ fontSize: "0.9rem", fontWeight: "600" }}>Budget Optimizer</div>
										<div style={{ fontSize: "0.7rem", opacity: 0.8, marginTop: "5px" }}>Click to Launch</div>
									</div>

									<div
										className='floating-card'
										style={{
											position: "absolute",
											top: "180px",
											right: "30px",
											width: "200px",
											height: "120px",
											background: "rgba(255,255,255,0.2)",
											borderRadius: "15px",
											backdropFilter: "blur(10px)",
											border: "1px solid rgba(255,255,255,0.3)",
											display: "flex",
											flexDirection: "column",
											alignItems: "center",
											justifyContent: "center",
											animation: "float 6s ease-in-out infinite 3s",
											cursor: "pointer",
											transition: "all 0.3s ease",
										}}
										onClick={handleScholarshipMatcher}
										onMouseEnter={(e) => {
											e.currentTarget.style.transform = "scale(1.05)";
											e.currentTarget.style.background = "rgba(255,255,255,0.3)";
										}}
										onMouseLeave={(e) => {
											e.currentTarget.style.transform = "scale(1)";
											e.currentTarget.style.background = "rgba(255,255,255,0.2)";
										}}>
										<div style={{ fontSize: "2rem", marginBottom: "10px" }}>🏆</div>
										<div style={{ fontSize: "0.9rem", fontWeight: "600", textAlign: "center" }}>
											Scholarship & Loan Matcher
										</div>
									</div>

									<div
										className='floating-card'
										style={{
											position: "absolute",
											top: "330px",
											left: "60px",
											width: "200px",
											height: "120px",
											background: "rgba(255,255,255,0.2)",
											borderRadius: "15px",
											backdropFilter: "blur(10px)",
											border: "1px solid rgba(255,255,255,0.3)",
											display: "flex",
											flexDirection: "column",
											alignItems: "center",
											justifyContent: "center",
											animation: "float 6s ease-in-out infinite 4s",
											cursor: "pointer",
											transition: "all 0.3s ease",
										}}
										onClick={handleCareerPredictor}
										onMouseEnter={(e) => {
											e.currentTarget.style.transform = "scale(1.05)";
											e.currentTarget.style.background = "rgba(255,255,255,0.3)";
										}}
										onMouseLeave={(e) => {
											e.currentTarget.style.transform = "scale(1)";
											e.currentTarget.style.background = "rgba(255,255,255,0.2)";
										}}>
										<div style={{ fontSize: "2rem", marginBottom: "10px" }}>📈</div>
										<div style={{ fontSize: "0.9rem", fontWeight: "600" }}>Career Predictor</div>
										<div style={{ fontSize: "0.7rem", opacity: 0.8, marginTop: "5px" }}>Click to Launch</div>
									</div>
								</div>
							</div>
						</Col>
					</Row>
				</Container>

				{/* Scroll Indicator */}
				<div
					style={{
						position: "absolute",
						bottom: "30px",
						left: "50%",
						transform: "translateX(-50%)",
						animation: "bounce 2s infinite",
					}}>
					<div
						style={{
							width: "30px",
							height: "50px",
							border: "2px solid rgba(255,255,255,0.8)",
							borderRadius: "15px",
							position: "relative",
						}}>
						<div
							style={{
								width: "6px",
								height: "6px",
								background: "rgba(255,255,255,0.8)",
								borderRadius: "50%",
								position: "absolute",
								top: "8px",
								left: "50%",
								transform: "translateX(-50%)",
								animation: "scroll 2s infinite",
							}}
						/>
					</div>
				</div>
			</section>

			{/* Main Content */}
			<Container className='mt-5'>
				<div style={{ paddingTop: "2rem" }}>
					<div className='mb-5 text-center'>
						<h1 id='main-topic' className='mb-3 gradient-text'>
							Transforming Education Through AI
						</h1>
						<p className='lead text-muted' style={{ maxWidth: "800px", margin: "0 auto" }}>
							Discover how our advanced AI modules are revolutionizing educational guidance for Sri Lankan students
						</p>
					</div>

					<div
						className='project-overview'
						style={{ padding: "20px", backgroundColor: "#f8f9fa", margin: "20px 0", borderRadius: "10px" }}>
						<h3>Addressing Educational Challenges in Sri Lanka</h3>
						<p style={{ fontSize: "16px", lineHeight: "1.6", textAlign: "justify" }}>
							Approximately 350,000 G.C.E. A/L candidates annually compete for about 44,000 state university seats,
							leaving over 300,000 students to navigate private, external, or vocational pathways without personalized
							support. Rising living costs—up 15% over the past five years—combined with opaque scholarship and loan
							eligibility criteria contribute to widespread under-utilization of financial aid. Meanwhile, graduates
							face persistent mismatches between their qualifications and labor-market demands. Overall tertiary
							graduate unemployment remains under 5%, but underemployment and skill-gap issues endure due to limited
							access to localized salary forecasts and demand trends during academic planning.
						</p>
					</div>

					<h2 id='atrractive-img'> ----Our AI Solutions---- </h2>
					<div
						className='ai-modules-container'
						style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "30px", margin: "30px 0" }}>
						<div
							className='module-card'
							style={{
								backgroundColor: "#e3f2fd",
								padding: "25px",
								borderRadius: "15px",
								boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
							}}>
							<div className='module-icon' style={{ fontSize: "48px", textAlign: "center", marginBottom: "15px" }}>
								🎯
							</div>
							<h3 style={{ color: "#1976d2", marginBottom: "15px", textAlign: "center" }}>
								1. Degree Recommendation System
							</h3>
							<p style={{ fontSize: "14px", lineHeight: "1.5", textAlign: "justify" }}>
								Employing hybrid machine learning approaches including content-based filtering, collaborative filtering,
								and Multi-Criteria Decision Making (MCDM) with Z-score filters to provide personalized degree
								recommendations based on student profiles, academic performance, and career aspirations.
							</p>
						</div>

						<div
							className='module-card'
							style={{
								backgroundColor: "#e8f5e8",
								padding: "25px",
								borderRadius: "15px",
								boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
								cursor: "pointer",
								transition: "all 0.3s ease",
								position: "relative",
							}}
							onClick={handleBudgetOptimizer}
							onMouseEnter={(e) => {
								e.currentTarget.style.transform = "translateY(-5px)";
								e.currentTarget.style.boxShadow = "0 8px 25px rgba(0,0,0,0.2)";
								e.currentTarget.style.backgroundColor = "#e0f2e0";
							}}
							onMouseLeave={(e) => {
								e.currentTarget.style.transform = "translateY(0)";
								e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)";
								e.currentTarget.style.backgroundColor = "#e8f5e8";
							}}>
							<div className='module-icon' style={{ fontSize: "48px", textAlign: "center", marginBottom: "15px" }}>
								💰
							</div>
							<h3 style={{ color: "#388e3c", marginBottom: "15px", textAlign: "center" }}>
								2. Student Budget Optimizer
							</h3>
							<p style={{ fontSize: "14px", lineHeight: "1.5", textAlign: "justify" }}>
								Advanced expense forecasting system that generates personalized budget plans for students, incorporating
								real-time cost-of-living indices, accommodation costs, and educational expenses to help students make
								informed financial decisions throughout their academic journey.
							</p>

							{/* Launch Indicator */}
							<div
								style={{
									position: "absolute",
									top: "15px",
									right: "15px",
									background: "rgba(56, 142, 60, 0.2)",
									color: "#388e3c",
									padding: "5px 10px",
									borderRadius: "20px",
									fontSize: "12px",
									fontWeight: "600",
								}}>
								🚀 Live Demo
							</div>

							<div
								style={{
									textAlign: "center",
									marginTop: "15px",
									padding: "10px",
									background: "rgba(56, 142, 60, 0.1)",
									borderRadius: "8px",
									fontSize: "13px",
									fontWeight: "600",
									color: "#2e7d32",
								}}>
								Click to access AI Budget Optimizer →
							</div>
						</div>

						<div
							className='module-card'
							style={{
								backgroundColor: "#fff3e0",
								padding: "25px",
								borderRadius: "15px",
								boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
							}}>
							<div className='module-icon' style={{ fontSize: "48px", textAlign: "center", marginBottom: "15px" }}>
								🏆
							</div>
							<h3 style={{ color: "#f57c00", marginBottom: "15px", textAlign: "center" }}>
								3. Scholarship & Loan Matcher
							</h3>
							<p style={{ fontSize: "14px", lineHeight: "1.5", textAlign: "justify" }}>
								Intelligent matching system with eligibility prediction algorithms, automated deadline alerts, and fraud
								detection capabilities. This module helps students discover and apply for relevant scholarships and
								loans while protecting them from fraudulent schemes.
							</p>
						</div>

						<div
							className='module-card'
							style={{
								backgroundColor: "#f3e5f5",
								padding: "25px",
								borderRadius: "15px",
								boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
							}}>
							<div className='module-icon' style={{ fontSize: "48px", textAlign: "center", marginBottom: "15px" }}>
								📈
							</div>
							<h3 style={{ color: "#7b1fa2", marginBottom: "15px", textAlign: "center" }}>
								4. Career Outcome Predictor
							</h3>
							<p style={{ fontSize: "14px", lineHeight: "1.5", textAlign: "justify" }}>
								Leveraging time-series forecasting and comprehensive skill-gap analysis to predict career outcomes,
								salary expectations, and job market trends. This module provides students with data-driven insights into
								future employment prospects and skill requirements.
							</p>
						</div>
					</div>

					<div
						className='platform-overview'
						style={{
							backgroundColor: "#fff",
							padding: "30px",
							margin: "30px 0",
							borderRadius: "15px",
							boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
						}}>
						<h3 style={{ color: "#333", textAlign: "center", marginBottom: "20px" }}>
							Integrated Data-Driven Platform
						</h3>
						<p style={{ fontSize: "16px", lineHeight: "1.6", textAlign: "justify", marginBottom: "20px" }}>
							By integrating UGC admissions data, real-time cost-of-living indices, comprehensive scholarship
							frameworks, and current labor-market statistics, our platform applies advanced machine learning
							algorithms, rule-based logic, and sophisticated forecasting models to deliver personalized, data-driven
							guidance.
						</p>

						<div
							className='tech-stack'
							style={{ display: "flex", justifyContent: "space-around", flexWrap: "wrap", marginTop: "25px" }}>
							<div className='tech-item' style={{ textAlign: "center", margin: "10px" }}>
								<div style={{ fontSize: "32px", marginBottom: "10px" }}>🤖</div>
								<h5>Machine Learning</h5>
								<p style={{ fontSize: "12px", color: "#666" }}>Hybrid ML Models</p>
							</div>
							<div className='tech-item' style={{ textAlign: "center", margin: "10px" }}>
								<div style={{ fontSize: "32px", marginBottom: "10px" }}>📊</div>
								<h5>Data Analytics</h5>
								<p style={{ fontSize: "12px", color: "#666" }}>Real-time Processing</p>
							</div>
							<div className='tech-item' style={{ textAlign: "center", margin: "10px" }}>
								<div style={{ fontSize: "32px", marginBottom: "10px" }}>🔮</div>
								<h5>Forecasting</h5>
								<p style={{ fontSize: "12px", color: "#666" }}>Time-series Analysis</p>
							</div>
							<div className='tech-item' style={{ textAlign: "center", margin: "10px" }}>
								<div style={{ fontSize: "32px", marginBottom: "10px" }}>🎯</div>
								<h5>Personalization</h5>
								<p style={{ fontSize: "12px", color: "#666" }}>Individual Guidance</p>
							</div>
						</div>
					</div>

					<div
						className='research-impact'
						style={{
							backgroundColor: "#f8f9fa",
							padding: "30px",
							margin: "30px 0",
							borderRadius: "15px",
							border: "2px solid #dee2e6",
						}}>
						<h3 style={{ color: "#495057", textAlign: "center", marginBottom: "20px" }}>Research Impact & Goals</h3>
						<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "25px" }}>
							<div>
								<h5 style={{ color: "#007bff", marginBottom: "15px" }}>🎯 Target Demographics</h5>
								<ul style={{ fontSize: "14px", lineHeight: "1.6" }}>
									<li>350,000+ G.C.E. A/L candidates annually</li>
									<li>300,000+ students seeking alternative pathways</li>
									<li>University graduates facing employment challenges</li>
									<li>Students from diverse socio-economic backgrounds</li>
								</ul>
							</div>
							<div>
								<h5 style={{ color: "#28a745", marginBottom: "15px" }}>📈 Expected Outcomes</h5>
								<ul style={{ fontSize: "14px", lineHeight: "1.6" }}>
									<li>Improved degree-career alignment</li>
									<li>Enhanced financial planning capabilities</li>
									<li>Increased scholarship utilization rates</li>
									<li>Reduced skill-gap unemployment</li>
								</ul>
							</div>
						</div>
					</div>

					<h2 id='about-name'>About Our Research Team</h2>

					<p id='about-details'>
						We are a dedicated team of researchers and developers committed to revolutionizing educational guidance in
						Sri Lanka through artificial intelligence and data-driven insights. Our interdisciplinary approach combines
						expertise in machine learning, educational psychology, labor economics, and software engineering to create
						comprehensive solutions for Sri Lankan students. By leveraging cutting-edge technology and extensive
						research, we aim to bridge the gap between academic aspirations and career realities, ensuring every student
						has access to personalized, evidence-based guidance for their educational and professional journey.
					</p>

					<table id='more-details'>
						<tr>
							<th>WHY CHOOSE OUR AI PLATFORM</th>
						</tr>
						<tr>
							<td>
								<h4>ADVANCED AI ALGORITHMS</h4>
								Our platform utilizes state-of-the-art machine learning models including hybrid recommendation systems,
								time-series forecasting, and multi-criteria decision making. These sophisticated algorithms analyze vast
								amounts of data to provide personalized recommendations tailored to each student's unique profile and
								circumstances.
							</td>
							<td>
								<h4>COMPREHENSIVE DATA INTEGRATION</h4>
								We integrate diverse data sources including UGC admissions statistics, real-time cost-of-living indices,
								scholarship databases, and labor market trends. This comprehensive approach ensures our recommendations
								are based on the most current and relevant information available.
							</td>
						</tr>

						<tr>
							<td>
								<h4>EVIDENCE-BASED GUIDANCE</h4>
								Every recommendation is backed by extensive research and data analysis. We don't rely on intuition or
								generic advice - our platform provides evidence-based guidance that helps students make informed
								decisions about their academic and career paths with confidence.
							</td>

							<td>
								<h4>TRANSPARENT METHODOLOGY</h4>
								Our platform provides clear explanations of how recommendations are generated, ensuring students
								understand the reasoning behind each suggestion. This transparency helps build trust and enables
								students to make well-informed decisions.
							</td>
						</tr>

						<tr>
							<td>
								<h4>PERSONALIZED EXPERIENCE</h4>
								Each student receives tailored recommendations based on their academic performance, financial situation,
								career interests, and personal circumstances. Our AI adapts to individual needs, ensuring relevant and
								actionable guidance for every user.
							</td>
							<td>
								<h4>CONTINUOUS IMPROVEMENT</h4>
								Our models continuously learn and improve from new data and user feedback. This ensures that our
								recommendations become more accurate and relevant over time, providing increasingly valuable insights to
								Sri Lankan students.
							</td>
						</tr>
					</table>
					<br />
					<br />
					<br />
				</div>
			</Container>
		</div>
	);
};

export default HomePage;
