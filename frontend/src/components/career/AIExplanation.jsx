/**
 * AI Explanation Component
 * Displays the AI-generated career explanation with markdown formatting
 */
import React, { useState, useEffect, useRef } from "react";
import { HiSparkles } from "react-icons/hi2";
import {
  FaRobot,
  FaBrain,
  FaLightbulb,
  FaChartLine,
  FaCheckCircle,
} from "react-icons/fa";
import { BiTargetLock } from "react-icons/bi";

function formatExplanation(text) {
  if (!text) return "";

  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/^- /gm, "• ")
    .replace(/^(\d+)\. /gm, "<strong>$1.</strong> ")
    .replace(/\n/g, "<br/>");
}

export function AIExplanation({ explanation }) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const explanationRef = useRef(null);

  // Start typing animation when explanation is available
  useEffect(() => {
    if (!explanation) return;

    setDisplayedText("");
    setIsTyping(true);
    let currentIndex = 0;

    const intervalId = setInterval(() => {
      if (currentIndex < explanation.length) {
        setDisplayedText(explanation.substring(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(intervalId);
      }
    }, 15); // Adjust speed here (lower = faster)

    return () => clearInterval(intervalId);
  }, [explanation]);

  if (!explanation) return null;

  return (
    <div
      ref={explanationRef}
      className="relative overflow-hidden rounded-3xl shadow-2xl transform transition-all duration-700"
      style={{
        background:
          "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
      }}
    >
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-64 h-64 rounded-full blur-3xl opacity-20 animate-pulse"
          style={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            top: "-10%",
            right: "-10%",
          }}
        ></div>
        <div
          className="absolute w-96 h-96 rounded-full blur-3xl opacity-10 animate-pulse"
          style={{
            background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
            bottom: "-20%",
            left: "-15%",
            animationDelay: "1s",
          }}
        ></div>
      </div>

      {/* Main content */}
      <div className="relative z-10 p-8 backdrop-blur-sm bg-white/60 border-2 border-white/50">
        {/* Header with gradient and animated icons */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-110 transition-all duration-300"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              }}
            >
              <FaRobot className="text-2xl text-white animate-pulse" />
            </div>
            <div>
              <h3
                className="font-extrabold text-2xl bg-clip-text text-transparent"
                style={{
                  backgroundImage:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                }}
              >
                AI Career Insights
              </h3>
              <p className="text-sm text-gray-600 flex items-center gap-1">
                <HiSparkles className="text-yellow-500" />
                Powered by Advanced AI
              </p>
            </div>
          </div>

          {/* Status badge */}
          <div
            className="px-4 py-2 rounded-full text-white text-sm font-bold shadow-lg flex items-center gap-2"
            style={{
              background: isTyping
                ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            }}
          >
            {isTyping ? (
              <>
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                Analyzing
              </>
            ) : (
              <>
                <FaCheckCircle />
                Complete
              </>
            )}
          </div>
        </div>

        {/* Feature badges */}
        <div className="flex flex-wrap gap-2 mb-6">
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 rounded-full shadow-md border border-purple-100">
            <FaBrain className="text-purple-600" />
            <span className="text-sm font-semibold text-purple-700">
              Deep Analysis
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 rounded-full shadow-md border border-indigo-100">
            <BiTargetLock className="text-indigo-600" />
            <span className="text-sm font-semibold text-indigo-700">
              Personalized
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 rounded-full shadow-md border border-blue-100">
            <FaChartLine className="text-blue-600" />
            <span className="text-sm font-semibold text-blue-700">
              Data-Driven
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 rounded-full shadow-md border border-amber-100">
            <FaLightbulb className="text-amber-600" />
            <span className="text-sm font-semibold text-amber-700">
              Actionable Tips
            </span>
          </div>
        </div>

        {/* Explanation content with enhanced styling */}
        <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-inner border border-gray-100">
          {/* Decorative corner elements */}
          <div
            className="absolute top-0 left-0 w-20 h-20 rounded-br-full opacity-10"
            style={{
              background:
                "linear-gradient(135deg, #667eea 0%, transparent 100%)",
            }}
          ></div>
          <div
            className="absolute bottom-0 right-0 w-20 h-20 rounded-tl-full opacity-10"
            style={{
              background:
                "linear-gradient(135deg, transparent 0%, #764ba2 100%)",
            }}
          ></div>

          <div
            className="text-gray-800 leading-relaxed whitespace-pre-wrap relative z-10"
            style={{ fontSize: "15px", lineHeight: "1.8" }}
            dangerouslySetInnerHTML={{
              __html: formatExplanation(displayedText),
            }}
          />
          {isTyping && (
            <span
              className="inline-block w-1 h-5 ml-1 animate-blink"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              }}
            />
          )}
        </div>

        {/* Footer with AI branding */}
        {!isTyping && displayedText && (
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
            <HiSparkles className="text-purple-500" />
            <span>
              AI-generated insights based on industry data and best practices
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export function AILoadingState() {
  return (
    <div className="py-16 px-8 relative">
      {/* Animated gradient background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-64 h-64 rounded-full blur-3xl opacity-20 animate-pulse"
          style={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            top: "0%",
            left: "10%",
          }}
        ></div>
        <div
          className="absolute w-64 h-64 rounded-full blur-3xl opacity-20 animate-pulse"
          style={{
            background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
            bottom: "0%",
            right: "10%",
            animationDelay: "1s",
          }}
        ></div>
      </div>

      {/* Content */}
      <div className="relative">
        {/* AI Robot Icon with enhanced animation */}
        <div className="relative flex justify-center mb-8">
          {/* Pulsing rings */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="w-32 h-32 rounded-full opacity-20 animate-ping"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              }}
            ></div>
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="w-24 h-24 rounded-full opacity-30 animate-pulse"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              }}
            ></div>
          </div>

          {/* Robot icon */}
          <div
            className="relative w-28 h-28 rounded-3xl flex items-center justify-center shadow-2xl animate-bounce"
            style={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              boxShadow: "0 20px 60px rgba(102, 126, 234, 0.4)",
            }}
          >
            <FaRobot className="w-14 h-14 text-white" />
            <HiSparkles className="absolute -top-2 -right-2 text-yellow-300 text-2xl animate-pulse" />
          </div>
        </div>

        {/* Loading text with gradient */}
        <div className="text-center mb-8">
          <h3
            className="text-3xl font-extrabold mb-3 bg-clip-text text-transparent"
            style={{
              backgroundImage:
                "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            }}
          >
            AI is Analyzing Your Profile
          </h3>
          <p className="text-gray-600 text-base">
            Generating personalized career insights tailored to your skills...
          </p>
        </div>

        {/* Enhanced progress bar */}
        <div className="max-w-md mx-auto mb-8">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden shadow-inner">
            <div
              className="h-full rounded-full relative overflow-hidden"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                width: "70%",
                animation: "loading 1.5s ease-in-out infinite",
              }}
            >
              <div
                className="absolute inset-0 bg-white/30"
                style={{
                  animation: "shimmer 1s ease-in-out infinite",
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* Floating dots animation */}
        <div className="flex justify-center gap-3 mb-10">
          <span
            className="w-3 h-3 rounded-full animate-bounce shadow-lg"
            style={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              animationDelay: "0ms",
            }}
          />
          <span
            className="w-3 h-3 rounded-full animate-bounce shadow-lg"
            style={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              animationDelay: "150ms",
            }}
          />
          <span
            className="w-3 h-3 rounded-full animate-bounce shadow-lg"
            style={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              animationDelay: "300ms",
            }}
          />
        </div>

        {/* Info chips with icons */}
        <div className="flex flex-wrap justify-center gap-3">
          <div
            className="px-5 py-2.5 bg-white rounded-full text-sm font-semibold shadow-lg border-2 flex items-center gap-2 animate-fade-in"
            style={{
              borderColor: "#667eea",
              color: "#667eea",
              animationDelay: "0.2s",
            }}
          >
            <FaBrain className="text-lg" />
            Analyzing Skills
          </div>
          <div
            className="px-5 py-2.5 bg-white rounded-full text-sm font-semibold shadow-lg border-2 flex items-center gap-2 animate-fade-in"
            style={{
              borderColor: "#764ba2",
              color: "#764ba2",
              animationDelay: "0.4s",
            }}
          >
            <BiTargetLock className="text-lg" />
            Matching Careers
          </div>
          <div
            className="px-5 py-2.5 bg-white rounded-full text-sm font-semibold shadow-lg border-2 flex items-center gap-2 animate-fade-in"
            style={{
              borderColor: "#667eea",
              color: "#667eea",
              animationDelay: "0.6s",
            }}
          >
            <FaLightbulb className="text-lg" />
            Creating Insights
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
}
