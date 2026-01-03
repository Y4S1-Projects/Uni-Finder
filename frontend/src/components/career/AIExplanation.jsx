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
    <div className="text-center py-12">
      <div className="text-5xl mb-4">🤖</div>
      <div className="text-gray-500">AI is analyzing this career path...</div>
    </div>
  );
}
