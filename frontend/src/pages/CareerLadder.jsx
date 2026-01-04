/**
 * Career Ladder Page
 * Visual representation of career progression with animated ladder
 */
import React, { useState, useEffect } from "react";
import { FaRocket, FaCheckCircle, FaLock, FaTrophy } from "react-icons/fa";

export default function CareerLadder() {
  const [activeStep, setActiveStep] = useState(1);

  // Example career ladder data
  const careerPath = [
    {
      id: 1,
      title: "Junior Software Engineer",
      level: "Entry",
      status: "current",
      skillsRequired: 5,
      yearsRequired: "0-2 years",
      salary: "$50k - $70k",
    },
    {
      id: 2,
      title: "Software Engineer",
      level: "Mid",
      status: "next",
      skillsRequired: 15,
      yearsRequired: "2-4 years",
      salary: "$70k - $90k",
    },
    {
      id: 3,
      title: "Senior Software Engineer",
      level: "Senior",
      status: "locked",
      skillsRequired: 25,
      yearsRequired: "4-7 years",
      salary: "$90k - $120k",
    },
    {
      id: 4,
      title: "Lead Software Engineer",
      level: "Lead",
      status: "locked",
      skillsRequired: 35,
      yearsRequired: "7-10 years",
      salary: "$120k - $150k",
    },
    {
      id: 5,
      title: "Principal Engineer",
      level: "Principal",
      status: "locked",
      skillsRequired: 45,
      yearsRequired: "10+ years",
      salary: "$150k+",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            Your Career Ladder
          </h1>
          <p className="text-gray-600 text-lg">
            Visualize your journey to success
          </p>
        </div>

        {/* Ladder Container */}
        <div className="relative">
          {/* Vertical Line (Ladder Rail) */}
          <div className="absolute left-1/2 transform -translate-x-1/2 w-1 bg-gradient-to-b from-purple-300 via-blue-300 to-gray-300 h-full rounded-full"></div>

          {/* Career Steps */}
          <div className="space-y-8">
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

        {/* Achievement Badge */}
        <div className="mt-12 text-center animate-scale-in">
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full shadow-lg">
            <FaTrophy className="text-yellow-300" />
            <span className="font-semibold">
              Keep climbing to reach the top!
            </span>
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
        threshold: 0.2, // Trigger when 20% of the element is visible
        rootMargin: "0px 0px -50px 0px", // Start animation slightly before element is fully in view
      }
    );

    if (stepRef.current) {
      observer.observe(stepRef.current);
    }

    return () => {
      if (stepRef.current) {
        observer.unobserve(stepRef.current);
      }
    };
  }, []);

  const getStatusStyles = () => {
    switch (step.status) {
      case "current":
        return {
          bg: "bg-gradient-to-r from-purple-600 to-blue-600",
          border: "border-purple-600",
          text: "text-white",
          icon: <FaRocket className="text-2xl" />,
          iconBg: "bg-white/20",
        };
      case "next":
        return {
          bg: "bg-gradient-to-r from-blue-500 to-indigo-500",
          border: "border-blue-500",
          text: "text-white",
          icon: <FaCheckCircle className="text-2xl" />,
          iconBg: "bg-white/20",
        };
      case "locked":
        return {
          bg: "bg-white",
          border: "border-gray-300",
          text: "text-gray-700",
          icon: <FaLock className="text-2xl text-gray-400" />,
          iconBg: "bg-gray-100",
        };
      default:
        return {
          bg: "bg-white",
          border: "border-gray-300",
          text: "text-gray-700",
          icon: <FaCheckCircle className="text-2xl text-gray-400" />,
          iconBg: "bg-gray-100",
        };
    }
  };

  const styles = getStatusStyles();
  const isLeft = index % 2 === 0;

  return (
    <div
      ref={stepRef}
      className={`relative transform transition-all duration-700 ease-out ${
        isVisible
          ? "translate-x-0 opacity-100"
          : isLeft
          ? "-translate-x-32 opacity-0"
          : "translate-x-32 opacity-0"
      }`}
    >
      {/* Step Card */}
      <div
        className={`flex ${isLeft ? "justify-start" : "justify-end"}`}
        onClick={onClick}
      >
        <div
          className={`w-5/12 ${styles.bg} ${
            step.status === "locked" ? "border-2" : ""
          } ${
            styles.border
          } rounded-2xl p-6 shadow-xl hover:shadow-2xl cursor-pointer transform hover:scale-105 transition-all duration-300 ${
            isActive ? "ring-4 ring-purple-300" : ""
          }`}
        >
          {/* Level Badge */}
          <div className="flex items-center justify-between mb-3">
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                step.status === "locked"
                  ? "bg-gray-200 text-gray-600"
                  : "bg-white/30 text-white"
              }`}
            >
              {step.level}
            </span>
            <div
              className={`w-12 h-12 rounded-full ${styles.iconBg} flex items-center justify-center`}
            >
              {styles.icon}
            </div>
          </div>

          {/* Title */}
          <h3
            className={`text-xl font-bold mb-2 ${
              step.status === "locked" ? "text-gray-700" : "text-white"
            }`}
          >
            {step.title}
          </h3>

          {/* Details */}
          <div
            className={`space-y-2 text-sm ${
              step.status === "locked" ? "text-gray-600" : "text-white/90"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="font-semibold">Skills:</span>
              <span>{step.skillsRequired} required</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Experience:</span>
              <span>{step.yearsRequired}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">Salary:</span>
              <span>{step.salary}</span>
            </div>
          </div>

          {/* Status Indicator */}
          {step.status === "current" && (
            <div className="mt-4 px-3 py-1 bg-white/20 rounded-full text-center">
              <span className="text-xs font-bold text-white">YOU ARE HERE</span>
            </div>
          )}
          {step.status === "next" && (
            <div className="mt-4 px-3 py-1 bg-white/20 rounded-full text-center">
              <span className="text-xs font-bold text-white">NEXT STEP</span>
            </div>
          )}
        </div>
      </div>

      {/* Connecting Node */}
      <div
        className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-6 h-6 rounded-full ${
          step.status === "locked"
            ? "bg-gray-300"
            : "bg-gradient-to-r from-purple-500 to-blue-500"
        } border-4 border-white shadow-lg z-10 animate-pulse-slow`}
      ></div>

      {/* Ladder Rung (Horizontal Line) */}
      <div
        className={`absolute top-1/2 ${
          isLeft ? "left-1/2 ml-3" : "right-1/2 mr-3"
        } w-16 h-1 bg-gradient-to-r ${
          step.status === "locked"
            ? "from-gray-300 to-transparent"
            : "from-purple-400 to-transparent"
        } transform -translate-y-1/2`}
      ></div>
    </div>
  );
}
