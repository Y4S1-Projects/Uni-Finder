/**
 * AI Explanation Component
 * Displays the AI-generated career explanation with markdown formatting
 */
import React from "react";

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
  if (!explanation) return null;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-violet-50 p-6 rounded-xl border border-purple-200">
      <h3 className="flex items-center gap-2 text-purple-600 font-semibold mb-4">
        🤖 AI Career Analysis
      </h3>
      <div
        className="text-purple-900 leading-relaxed whitespace-pre-wrap"
        dangerouslySetInnerHTML={{
          __html: formatExplanation(explanation),
        }}
      />
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
          <div className="w-32 h-32 bg-gradient-to-r from-purple-400 via-pink-500 to-blue-500 rounded-full blur-3xl opacity-30 animate-pulse" />
        </div>

        {/* AI Robot Icon with animation */}
        <div className="relative flex justify-center mb-6">
          <div className="w-24 h-24 bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl shadow-purple-500/30 animate-bounce">
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
        </div>

        {/* Loading text */}
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-2">
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
              className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-full animate-pulse"
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
            className="w-2 h-2 bg-pink-500 rounded-full animate-bounce"
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
            🎯 Matching Skills
          </span>
          <span className="px-3 py-1 bg-pink-100 text-pink-600 rounded-full text-xs font-medium">
            📊 Analyzing Fit
          </span>
          <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
            💡 Generating Tips
          </span>
        </div>
      </div>
    </div>
  );
}
