import React, { useState, useMemo, useRef, useEffect } from "react";
import skillsList from "../../data/skills.json";

export default function SkillSelector({ selected = [], onChange }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  const normalized = useMemo(() => {
    return skillsList.map((s) => ({ id: String(s.skill_id), label: s.name }));
  }, []);

  const idToLabel = useMemo(() => {
    const m = new Map();
    for (const s of normalized) {
      m.set(String(s.id).toLowerCase(), s.label);
    }
    return m;
  }, [normalized]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return normalized;
    return normalized.filter(
      (s) => s.label.toLowerCase().includes(q) || s.id.toLowerCase().includes(q)
    );
  }, [normalized, query]);

  // Convert selected to array of string IDs
  const selectedIds = useMemo(() => {
    return (selected || [])
      .map((s) => {
        if (s == null) return "";
        if (typeof s === "string" || typeof s === "number") return String(s);
        return String(s.id ?? s.skill_id ?? s.skillId ?? "");
      })
      .filter(Boolean);
  }, [selected]);

  const selectedSetLower = useMemo(
    () => new Set(selectedIds.map((s) => s.toLowerCase())),
    [selectedIds]
  );

  function toggle(id) {
    const sid = String(id);
    const exists = selectedSetLower.has(sid.toLowerCase());
    if (exists) return; // Use ✕ button to remove
    const next = [...selectedIds, sid];
    if (typeof onChange === "function") onChange(next);
  }

  function remove(id) {
    const sid = String(id);
    const next = selectedIds.filter(
      (x) => x.toLowerCase() !== sid.toLowerCase()
    );
    if (typeof onChange === "function") onChange(next);
  }

  function labelFor(id) {
    if (!id && id !== 0) return "";
    const key = String(id).toLowerCase();
    const exact = idToLabel.get(key);
    if (exact) return exact;
    const partial = normalized.find(
      (s) => s.id.toLowerCase() === key || s.label.toLowerCase() === key
    );
    if (partial) return partial.label;
    return String(id);
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    }

    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [open]);

  return (
    <div className="relative" ref={containerRef}>
      {/* Selected Skills */}
      {selectedIds.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {selectedIds.map((id, idx) => (
            <div
              key={id || `sel-${idx}`}
              className="group flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 
                         border border-blue-200 px-3 py-1.5 rounded-full 
                         shadow-sm hover:shadow-md hover:border-blue-300 
                         transition-all duration-200"
            >
              <span className="text-sm font-medium text-blue-700">
                {labelFor(id)}
              </span>
              <button
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  remove(id);
                }}
                title={`Remove ${labelFor(id)}`}
                aria-label={`Remove ${labelFor(id)}`}
                className="w-5 h-5 flex items-center justify-center rounded-full 
                           bg-blue-100 text-blue-500 hover:bg-red-100 hover:text-red-500
                           transition-colors duration-150 text-xs font-bold"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!open) setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Search skills (e.g. Python, React, SQL...)"
          className="w-full pl-10 pr-20 py-3 
                     border-2 border-gray-200 rounded-xl
                     bg-white text-gray-700 placeholder-gray-400
                     focus:border-blue-400 focus:ring-4 focus:ring-blue-100 
                     hover:border-gray-300
                     transition-all duration-200 outline-none
                     text-sm font-medium"
        />
        <div className="absolute inset-y-0 right-0 flex items-center gap-1 pr-3">
          {query && (
            <button
              type="button"
              onMouseDown={(e) => {
                e.preventDefault();
                setQuery("");
              }}
              className="text-gray-400 hover:text-gray-600 transition-colors bg-transparent p-0"
              title="Clear search"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
          <button
            type="button"
            onClick={() => setOpen(!open)}
            className="text-gray-400 hover:text-gray-600 transition-colors bg-transparent p-0"
            title={open ? "Close dropdown" : "Open dropdown"}
          >
            <svg
              className={`h-6 w-6 transform transition-transform duration-200 ${
                open ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Dropdown */}
      {open && (
        <div
          className="absolute z-50 w-full mt-2 bg-white border border-gray-200 
                     rounded-xl shadow-xl overflow-hidden
                     animate-in fade-in slide-in-from-top-2 duration-200"
        >
          <div className="max-h-64 overflow-auto">
            {filtered.length > 0 ? (
              filtered.map((s) => {
                const isSelected = selectedSetLower.has(
                  String(s.id).toLowerCase()
                );
                return (
                  <div
                    key={s.id}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      toggle(s.id);
                    }}
                    className={`flex items-center justify-between px-4 py-3 cursor-pointer
                               border-b border-gray-50 last:border-b-0
                               transition-all duration-150
                               ${
                                 isSelected
                                   ? "bg-blue-50 text-blue-700"
                                   : "hover:bg-gray-50 text-gray-700"
                               }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold
                                   ${
                                     isSelected
                                       ? "bg-blue-500 text-white"
                                       : "bg-gray-100 text-gray-500"
                                   }`}
                      >
                        {s.label.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium">{s.label}</span>
                    </div>
                    {isSelected && (
                      <div className="flex items-center gap-1 text-blue-500">
                        <svg
                          className="w-5 h-5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <span className="text-xs font-semibold">Added</span>
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="px-4 py-8 text-center">
                <div className="text-gray-400 mb-2">
                  <svg
                    className="w-12 h-12 mx-auto"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <p className="text-gray-500 font-medium">No skills found</p>
                <p className="text-gray-400 text-sm">
                  Try a different search term
                </p>
              </div>
            )}
          </div>

          {/* Footer hint */}
          {filtered.length > 0 && (
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
              <p className="text-xs text-gray-400">
                💡 Showing {filtered.length} skills • Click to add
              </p>
            </div>
          )}
        </div>
      )}

      {/* Selected count badge */}
      {selectedIds.length > 0 && (
        <div className="mt-3 flex items-center gap-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
            ✓ {selectedIds.length} skill{selectedIds.length !== 1 ? "s" : ""}{" "}
            selected
          </span>
        </div>
      )}
    </div>
  );
}
