/**
 * Career Ladder Page
 * Visual representation of career progression with animated ladder
 */
import React, { useState, useEffect, useLayoutEffect } from "react";
import { FaRocket, FaCheckCircle, FaLock, FaTrophy } from "react-icons/fa";

export default function CareerLadder() {
	const [activeStep, setActiveStep] = useState(1);

	// Scroll to top immediately before paint
	useLayoutEffect(() => {
		window.scrollTo(0, 0);
	}, []);

	// Example career ladder data
	const careerPath = [
		{
			id: 1,
			title: "Junior Software Engineer",
			level: "Entry",
			status: "current",
			skillsRequired: 5,
			yearsRequired: "0-2 years",
			salary: "LKR 60k - 100k/mo",
		},
		{
			id: 2,
			title: "Software Engineer",
			level: "Mid",
			status: "next",
			skillsRequired: 15,
			yearsRequired: "2-4 years",
			salary: "LKR 100k - 150k/mo",
		},
		{
			id: 3,
			title: "Senior Software Engineer",
			level: "Senior",
			status: "locked",
			skillsRequired: 25,
			yearsRequired: "4-7 years",
			salary: "LKR 150k - 250k/mo",
		},
		{
			id: 4,
			title: "Lead Software Engineer",
			level: "Lead",
			status: "locked",
			skillsRequired: 35,
			yearsRequired: "7-10 years",
			salary: "LKR 250k - 400k/mo",
		},
		{
			id: 5,
			title: "Principal Engineer",
			level: "Principal",
			status: "locked",
			skillsRequired: 45,
			yearsRequired: "10+ years",
			salary: "LKR 400k+/mo",
		},
	];

	return (
		<div
			className='relative min-h-screen px-4 py-16 overflow-hidden'
			style={{
				background: "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
			}}>
			{/* Animated Background Elements */}
			<div className='absolute inset-0 overflow-hidden pointer-events-none'>
				<div
					className='absolute rounded-full w-96 h-96 blur-3xl opacity-20 animate-pulse'
					style={{
						background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
						top: "10%",
						left: "10%",
					}}></div>
				<div
					className='absolute rounded-full w-96 h-96 blur-3xl opacity-20 animate-pulse'
					style={{
						background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
						bottom: "10%",
						right: "10%",
						animationDelay: "1s",
					}}></div>
				<div
					className='absolute w-64 h-64 rounded-full blur-3xl opacity-15 animate-pulse'
					style={{
						background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
						top: "50%",
						right: "5%",
						animationDelay: "2s",
					}}></div>
				<div
					className='absolute rounded-full w-80 h-80 blur-3xl opacity-15 animate-pulse'
					style={{
						background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
						top: "30%",
						left: "5%",
						animationDelay: "3s",
					}}></div>
			</div>

			<div className='relative z-10 max-w-5xl mx-auto'>
				{/* Header */}
				<div className='relative mb-16 text-center animate-fade-in'>
					{/* Decorative gradient behind header */}
					<div
						className='absolute top-0 w-full h-32 transform -translate-x-1/2 left-1/2 blur-2xl opacity-20 -z-10'
						style={{
							background: "linear-gradient(90deg, transparent, #667eea, #764ba2, transparent)",
						}}></div>
					<div className='inline-block mb-6 cursor-default pointer-events-none'>
						<div
							className='px-6 py-2 text-sm font-semibold text-white rounded-full shadow-lg'
							style={{
								background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
							}}>
							🎯 Career Progression Path
						</div>
					</div>
					<h1
						className='mb-4 text-5xl font-extrabold text-transparent md:text-6xl bg-clip-text'
						style={{
							backgroundImage: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
						}}>
						Your Career Ladder
					</h1>
					<p className='max-w-2xl mx-auto text-xl text-gray-600'>
						Chart your professional journey with clear milestones and actionable goals
					</p>
				</div>

				{/* Ladder Container */}
				<div className='relative'>
					{/* Gradient glow behind ladder rail */}
					<div
						className='absolute w-8 h-full transform -translate-x-1/2 left-1/2 blur-xl opacity-30'
						style={{
							background: "linear-gradient(to bottom, #667eea, #764ba2, transparent)",
						}}></div>
					{/* Vertical Line (Ladder Rail) - Enhanced */}
					<div
						className='absolute left-1/2 transform -translate-x-1/2 w-1.5 h-full rounded-full shadow-lg'
						style={{
							background: "linear-gradient(to bottom, #667eea, #764ba2, rgba(118, 75, 162, 0.3))",
						}}></div>

					{/* Career Steps */}
					<div className='space-y-8'>
						{careerPath.map((step, index) => (
							<CareerStep
								key={step.id}
								step={step}
								index={index}
								isActive={activeStep === step.id}
								onClick={() => setActiveStep(step.id)}
							/>
						))}
					</div>
				</div>

				{/* Achievement Badge - Enhanced */}
				<div className='mt-16 text-center animate-scale-in'>
					<div
						className='inline-flex items-center gap-3 px-8 py-4 text-white transition-all duration-300 shadow-2xl rounded-2xl hover:shadow-3xl hover:scale-105'
						style={{
							background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
						}}>
						<FaTrophy className='text-2xl text-yellow-300' />
						<div className='text-left'>
							<div className='text-lg font-bold'>Keep Climbing!</div>
							<div className='text-sm opacity-90'>Your journey to success continues</div>
						</div>
					</div>
				</div>

				{/* Stats Bar */}
				<div className='relative grid grid-cols-1 gap-6 mt-12 md:grid-cols-3'>
					{/* Background gradient for stats */}
					<div
						className='absolute inset-0 rounded-2xl blur-xl opacity-10 -z-10'
						style={{
							background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
						}}></div>
					<div
						className='relative p-6 overflow-hidden transition-all duration-300 shadow-lg bg-white/80 backdrop-blur-sm rounded-xl hover:shadow-xl group'
						style={{
							border: "2px solid transparent",
							backgroundImage: "linear-gradient(white, white), linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
							backgroundOrigin: "border-box",
							backgroundClip: "padding-box, border-box",
						}}>
						<div
							className='absolute top-0 right-0 w-20 h-20 transition-opacity duration-300 rounded-full opacity-0 blur-2xl group-hover:opacity-30'
							style={{
								background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
							}}></div>
						<div className='mb-2 text-3xl font-bold' style={{ color: "#667eea" }}>
							5
						</div>
						<div className='font-medium text-gray-600'>Career Levels</div>
					</div>
					<div
						className='relative p-6 overflow-hidden transition-all duration-300 shadow-lg bg-white/80 backdrop-blur-sm rounded-xl hover:shadow-xl group'
						style={{
							border: "2px solid transparent",
							backgroundImage: "linear-gradient(white, white), linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
							backgroundOrigin: "border-box",
							backgroundClip: "padding-box, border-box",
						}}>
						<div
							className='absolute top-0 right-0 w-20 h-20 transition-opacity duration-300 rounded-full opacity-0 blur-2xl group-hover:opacity-30'
							style={{
								background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
							}}></div>
						<div className='mb-2 text-3xl font-bold' style={{ color: "#764ba2" }}>
							2/5
						</div>
						<div className='font-medium text-gray-600'>Progress Made</div>
					</div>
					<div
						className='relative p-6 overflow-hidden transition-all duration-300 shadow-lg bg-white/80 backdrop-blur-sm rounded-xl hover:shadow-xl group'
						style={{
							border: "2px solid transparent",
							backgroundImage: "linear-gradient(white, white), linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
							backgroundOrigin: "border-box",
							backgroundClip: "padding-box, border-box",
						}}>
						<div
							className='absolute top-0 right-0 w-20 h-20 transition-opacity duration-300 rounded-full opacity-0 blur-2xl group-hover:opacity-30'
							style={{
								background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
							}}></div>
						<div className='mb-2 text-3xl font-bold' style={{ color: "#667eea" }}>
							10+
						</div>
						<div className='font-medium text-gray-600'>Years to Goal</div>
					</div>
				</div>
			</div>
		</div>
	);
}

function CareerStep({ step, index, isActive, onClick }) {
	const [isVisible, setIsVisible] = useState(false);
	const stepRef = React.useRef(null);

	useEffect(() => {
		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						setIsVisible(true);
					}
				});
			},
			{
				threshold: 0.2,
				rootMargin: "0px 0px -50px 0px",
			},
		);

		const observedNode = stepRef.current;
		if (observedNode) {
			observer.observe(observedNode);
		}

		return () => {
			if (observedNode) {
				observer.unobserve(observedNode);
			}
		};
	}, []);

	const getStatusStyles = () => {
		switch (step.status) {
			case "current":
				return {
					gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
					border: "#667eea",
					text: "text-white",
					icon: <FaRocket className='text-2xl animate-bounce' />,
					iconBg: "rgba(255, 255, 255, 0.25)",
					glow: "0 10px 40px rgba(102, 126, 234, 0.4)",
				};
			case "next":
				return {
					gradient: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
					border: "#764ba2",
					text: "text-white",
					icon: <FaCheckCircle className='text-2xl' />,
					iconBg: "rgba(255, 255, 255, 0.25)",
					glow: "0 10px 40px rgba(118, 75, 162, 0.4)",
				};
			case "locked":
				return {
					gradient: "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)",
					border: "#e5e7eb",
					text: "text-gray-700",
					icon: <FaLock className='text-2xl text-gray-400' />,
					iconBg: "#f3f4f6",
					glow: "0 4px 15px rgba(0, 0, 0, 0.1)",
				};
			default:
				return {
					gradient: "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)",
					border: "#e5e7eb",
					text: "text-gray-700",
					icon: <FaCheckCircle className='text-2xl text-gray-400' />,
					iconBg: "#f3f4f6",
					glow: "0 4px 15px rgba(0, 0, 0, 0.1)",
				};
		}
	};

	const styles = getStatusStyles();
	const isLeft = index % 2 === 0;

	return (
		<div
			ref={stepRef}
			className={`relative transform transition-all duration-700 ease-out ${
				isVisible ? "translate-x-0 opacity-100"
				: isLeft ? "-translate-x-32 opacity-0"
				: "translate-x-32 opacity-0"
			}`}>
			{/* Step Card */}
			<div className={`flex ${isLeft ? "justify-start" : "justify-end"}`} onClick={onClick}>
				<div
					className='w-5/12 p-8 transition-all duration-500 transform cursor-pointer rounded-3xl hover:scale-105 backdrop-blur-sm'
					style={{
						background: styles.gradient,
						border: `2px solid ${styles.border}`,
						boxShadow: styles.glow,
					}}>
					{/* Level Badge */}
					<div className='flex items-center justify-between mb-4'>
						<div
							className='px-4 py-2 text-xs font-bold rounded-full shadow-md backdrop-blur-md'
							style={{
								background: step.status === "locked" ? "#f3f4f6" : "rgba(255, 255, 255, 0.3)",
								color: step.status === "locked" ? "#6b7280" : "white",
							}}>
							{step.level}
						</div>
						<div
							className='flex items-center justify-center rounded-full shadow-lg w-14 h-14'
							style={{
								background: styles.iconBg,
							}}>
							{styles.icon}
						</div>
					</div>

					{/* Title */}
					<h3 className={`text-2xl font-extrabold mb-4 ${step.status === "locked" ? "text-gray-800" : "text-white"}`}>
						{step.title}
					</h3>

					{/* Details */}
					<div className={`space-y-3 text-sm ${step.status === "locked" ? "text-gray-600" : "text-white/95"}`}>
						<div
							className='flex items-center gap-3 p-2 rounded-lg'
							style={{
								background: step.status === "locked" ? "rgba(0,0,0,0.03)" : "rgba(255,255,255,0.1)",
							}}>
							<span className='font-bold'>💼</span>
							<div>
								<span className='font-semibold'>Skills: </span>
								<span>{step.skillsRequired} required</span>
							</div>
						</div>
						<div
							className='flex items-center gap-3 p-2 rounded-lg'
							style={{
								background: step.status === "locked" ? "rgba(0,0,0,0.03)" : "rgba(255,255,255,0.1)",
							}}>
							<span className='font-bold'>⏱️</span>
							<div>
								<span className='font-semibold'>Experience: </span>
								<span>{step.yearsRequired}</span>
							</div>
						</div>
						<div
							className='flex items-center gap-3 p-2 rounded-lg'
							style={{
								background: step.status === "locked" ? "rgba(0,0,0,0.03)" : "rgba(255,255,255,0.1)",
							}}>
							<span className='font-bold'>💰</span>
							<div>
								<span className='font-semibold'>Salary: </span>
								<span className='font-bold'>{step.salary}</span>
							</div>
						</div>
					</div>

					{/* Status Indicator */}
					{step.status === "current" && (
						<div className='px-4 py-2 mt-5 text-center shadow-lg bg-white/25 backdrop-blur-md rounded-xl'>
							<span className='text-sm font-extrabold tracking-wide text-white'>✨ YOU ARE HERE</span>
						</div>
					)}
					{step.status === "next" && (
						<div className='px-4 py-2 mt-5 text-center shadow-lg bg-white/25 backdrop-blur-md rounded-xl'>
							<span className='text-sm font-extrabold tracking-wide text-white'>🎯 NEXT MILESTONE</span>
						</div>
					)}
				</div>
			</div>

			{/* Connecting Node - Enhanced */}
			<div
				className='absolute z-10 w-8 h-8 transform -translate-x-1/2 -translate-y-1/2 border-4 border-white rounded-full shadow-2xl top-1/2 left-1/2'
				style={{
					background: step.status === "locked" ? "#d1d5db" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
					animation: step.status !== "locked" ? "pulse 2s ease-in-out infinite" : "none",
				}}></div>

			{/* Ladder Rung (Horizontal Line) - Enhanced */}
			<div
				className={`absolute top-1/2 ${
					isLeft ? "left-1/2 ml-4" : "right-1/2 mr-4"
				} w-20 h-1.5 rounded-full shadow-md transform -translate-y-1/2`}
				style={{
					background:
						step.status === "locked" ?
							"linear-gradient(to right, #d1d5db, transparent)"
						:	"linear-gradient(to right, #667eea, transparent)",
				}}></div>
		</div>
	);
}
