import React from "react";

export default function CareerToast({ visible, type, message }) {
  if (!visible || !message) return null;
  const isError = type === "error";
  return (
    <div
      role="status"
      className="fixed bottom-5 right-5 z-[100] max-w-sm animate-slide-in-up transition-all duration-200"
    >
      <div className="bg-white shadow-lg hover:shadow-xl border border-gray-200 px-4 py-3 rounded-xl flex items-center gap-3">
        <span
          className={`text-lg leading-none shrink-0 ${isError ? "text-red-500" : "text-green-500"}`}
          aria-hidden={true}
        >
          {isError ? "!" : "✔"}
        </span>
        <span className="text-sm text-gray-700 leading-snug">{message}</span>
      </div>
    </div>
  );
}
