/**
 * AI Explanation Component
 * Displays the AI-generated career explanation with markdown formatting
 */
import React from "react";
import { HiSparkles } from "react-icons/hi2";
import { FaRobot } from "react-icons/fa";

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
  const [displayedText, setDisplayedText] = React.useState("");
  const [isTyping, setIsTyping] = React.useState(true);

  React.useEffect(() => {
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
      className="bg-gradient-to-br from-purple-50 via-violet-50 to-indigo-50 p-6 rounded-2xl border-2 border-purple-200 shadow-lg animate-fade-in-up"
      style={{ animationDelay: "0.4s" }}
    >
      <h3 className="flex items-center gap-2 text-purple-700 font-bold mb-4 text-lg">
        <FaRobot className="text-2xl" /> AI Career Analysis
      </h3>
      <div
        className="text-purple-900 leading-relaxed whitespace-pre-wrap"
        dangerouslySetInnerHTML={{
          __html: formatExplanation(displayedText),
        }}
      />
      {isTyping && (
        <span className="inline-block w-1 h-4 bg-purple-600 ml-1 animate-blink" />
      )}
    </div>
  );
}

export function AILoadingState() {
  return (
    <div className="py-16 px-8">
      {/* Animated gradient background */}
      <div className="relative">
        {/* Glow effect */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-32 h-32 bg-gradient-to-r from-purple-400 to-blue-500 rounded-full blur-3xl opacity-30 animate-pulse" />
        </div>

        {/* AI Robot Icon with animation */}
        <div className="relative flex justify-center mb-6">
          <div className="w-24 h-24 bg-gradient-to-br from-purple-500 via-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-xl shadow-purple-500/30 animate-bounce">
            <FaRobot className="w-12 h-12 text-white" />
          </div>
        </div>

        {/* Loading text */}
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
            AI is Analyzing
          </h3>
          <p className="text-gray-500 text-sm">
            Generating personalized career insights...
          </p>
        </div>

        {/* Animated progress bar */}
        <div className="max-w-xs mx-auto">
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse"
              style={{
                width: "70%",
                animation: "loading 1.5s ease-in-out infinite",
              }}
            />
          </div>
        </div>

        {/* Floating dots animation */}
        <div className="flex justify-center gap-2 mt-6">
          <span
            className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          />
          <span
            className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"
            style={{ animationDelay: "150ms" }}
          />
          <span
            className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          />
        </div>

        {/* Info chips */}
        <div className="flex flex-wrap justify-center gap-2 mt-8">
          <span className="px-3 py-1 bg-purple-100 text-purple-600 rounded-full text-xs font-medium">
            Matching Skills
          </span>
          <span className="px-3 py-1 bg-indigo-100 text-indigo-600 rounded-full text-xs font-medium">
            Analyzing Fit
          </span>
          <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
            Generating Tips
          </span>
        </div>
      </div>
    </div>
  );
}
