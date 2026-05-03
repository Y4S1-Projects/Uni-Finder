/**
 * Score Display Component
 * Displays match score or readiness score with visual indicator
 */
import React from "react";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useCountUp } from "../../hooks/useCountUp";

const MotionDiv = motion?.div || "div";

export function getScoreColor(score) {
  if (score >= 0.7) return "text-indigo-600";
  if (score >= 0.4) return "text-indigo-500";
  return "text-gray-600";
}

export function getScoreBgColor(score) {
  if (score >= 0.7) return "bg-indigo-600";
  if (score >= 0.4) return "bg-indigo-500";
  return "bg-gray-400";
}

export function ScoreCircle({ score, label, size = "normal" }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);
  const targetPercent = Number((score * 100).toFixed(0));
  const { value } = useCountUp(targetPercent, 1000, isVisible);

  useEffect(() => {
    if (!ref.current) return undefined;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.25 },
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  const colorClass = getScoreColor(score);
  const sizeClasses = {
    large: "text-3xl",
    normal: "text-2xl",
    small: "text-xl",
  };
  const labelSizeClasses = {
    large: "text-sm",
    normal: "text-xs",
    small: "text-xs",
  };

  return (
    <div ref={ref} className="text-right">
      <div className={`font-bold ${sizeClasses[size]} ${colorClass}`}>
        {value}%
      </div>
      <div className={`${labelSizeClasses[size]} text-gray-500`}>{label}</div>
    </div>
  );
}

export function ScoreCard({ score, label, variant = "blue" }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);
  const targetPercent = Number((score * 100).toFixed(0));
  const { value } = useCountUp(targetPercent, 1000, isVisible);

  useEffect(() => {
    if (!ref.current) return undefined;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.25 },
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  const variants = {
    blue: "bg-indigo-50 text-indigo-700 border border-indigo-200",
    green:
      "bg-teal-50 text-teal-700 border border-teal-200",
    purple:
      "bg-indigo-50 text-indigo-700 border border-indigo-200",
  };

  return (
    <div
      ref={ref}
      className={`flex-1 p-5 rounded-xl text-center shadow-md hover:shadow-lg transition-all duration-300 ${
        variants[variant] || variants.blue
      }`}
    >
      <div className="text-4xl font-bold">{value}%</div>
      <div className="text-xs font-semibold text-gray-600 mt-1">{label}</div>
    </div>
  );
}

export function ProgressBar({ score, height = "h-2" }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);
  const targetPercent = Number((score * 100).toFixed(0));
  useCountUp(targetPercent, 1000, isVisible, 0);
  const bgColorClass = getScoreBgColor(score);

  useEffect(() => {
    if (!ref.current) return undefined;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.25 },
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={`bg-gray-200 rounded-full ${height} overflow-hidden w-full block`}>
      <MotionDiv
        className={`${height} ${bgColorClass} rounded-full`}
        initial={{ width: 0 }}
        animate={isVisible ? { width: `${targetPercent}%` } : { width: 0 }}
        transition={{ duration: 1, ease: "easeOut" }}
      />
    </div>
  );
}
