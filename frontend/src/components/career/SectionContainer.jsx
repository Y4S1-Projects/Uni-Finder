import React, { useEffect, useRef, useState } from "react";

export default function SectionContainer({
  title,
  subtitle,
  children,
  className = "",
}) {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    if (!sectionRef.current) return undefined;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 },
    );
    observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className={`relative p-6 md:p-8 rounded-2xl border border-gray-100 bg-white/70 backdrop-blur-xl shadow-lg transition-all duration-500 ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
      } ${className}`}
    >
      <div className="absolute inset-0 rounded-2xl opacity-70 -z-10 bg-gradient-to-br from-purple-100/60 to-blue-100/60" />
      {(title || subtitle) && (
        <div className="mb-6">
          {title && (
            <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-blue-700">
              {title}
            </h3>
          )}
          {subtitle && <p className="text-gray-600 mt-2">{subtitle}</p>}
        </div>
      )}
      {children}
    </section>
  );
}
