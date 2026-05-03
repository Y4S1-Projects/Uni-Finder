import React from "react";

export default function CareerToast({ visible, type, message }) {
  if (!visible || !message) return null;
  const isError = type === "error";
  return (
    <div
      role="status"
      className="fixed bottom-5 right-5 z-[100] max-w-sm animate-slide-in-up transition-all duration-200"
    >
      <div className={`shadow-lg hover:shadow-xl px-4 py-3 rounded-xl flex items-center gap-3 ${isError ? "bg-red-50 border border-red-200 text-red-700" : "bg-green-50 border border-green-200 text-green-700"}`}>
        <span
          className={`text-lg leading-none shrink-0 ${isError ? "text-red-500" : "text-green-500"}`}
          aria-hidden={true}
        >
          {isError ? "!" : "✔"}
        </span>
        <span className="text-sm font-medium leading-snug">{message}</span>
      </div>
    </div>
  );
}
