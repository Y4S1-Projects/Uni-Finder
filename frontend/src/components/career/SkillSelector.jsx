import React, {
  useState,
  useMemo,
  useRef,
  useEffect,
  useCallback,
} from "react";
import skillsList from "../../data/skills.json";

// ── Category display configuration ────────────────────────────────────────────
const CATEGORY_MAP = {
  // Technical → Programming Languages & Frameworks
  backend: { group: "Technical Skills", sub: "Backend & Languages" },
  frontend: { group: "Technical Skills", sub: "Web & Frontend" },
  fullstack: { group: "Technical Skills", sub: "Full-Stack" },
  database: { group: "Technical Skills", sub: "Databases" },
  cloud: { group: "Technical Skills", sub: "Cloud Platforms" },
  devops: { group: "Technical Skills", sub: "DevOps & Infrastructure" },
  ai_ml: { group: "Technical Skills", sub: "AI/ML & Data Science" },
  ml_ai: { group: "Technical Skills", sub: "AI/ML & Data Science" },
  data: { group: "Technical Skills", sub: "Data Engineering" },
  analytics: { group: "Technical Skills", sub: "Analytics" },
  security: { group: "Technical Skills", sub: "Security" },
  mobile: { group: "Technical Skills", sub: "Mobile" },
  embedded: { group: "Technical Skills", sub: "Embedded & IoT" },
  blockchain: { group: "Technical Skills", sub: "Blockchain & Web3" },
  game_dev: { group: "Technical Skills", sub: "Game Development" },
  other: { group: "Technical Skills", sub: "Other Technical" },
  // Soft Skills
  soft_skill: { group: "Soft Skills", sub: "General" },
  communication: { group: "Soft Skills", sub: "Communication" },
  leadership: { group: "Soft Skills", sub: "Leadership" },
  project_mgmt: { group: "Soft Skills", sub: "Project Management" },
  business: { group: "Soft Skills", sub: "Business Analysis" },
  // Certifications
  certification: { group: "Certifications", sub: "Industry Certifications" },
};

const GROUP_ORDER = ["Technical Skills", "Soft Skills", "Certifications"];
const GROUP_ICONS = {
  "Technical Skills": "💻",
  "Soft Skills": "🤝",
  Certifications: "🏆",
};

// Popular skills (top-50 most common in job postings)
const POPULAR_IDS = new Set([
  "SK001",
  "SK002",
  "SK003",
  "SK004",
  "SK005",
  "SK006",
  "SK007",
  "SK008",
  "SK009",
  "SK010",
  "SK011",
  "SK012",
  "SK013",
  "SK014",
  "SK016",
  "SK017",
  "SK018",
  "SK020",
  "SK021",
  "SK024",
  "SK026",
  "SK027",
  "SK028",
  "SK031",
  "SK037",
  "SK041",
  "SK055",
  "SK057",
  "SK061",
  "SK067",
  "SK070",
  "SK071",
  "SK093",
  "SK107",
  "SK124",
  "SK132",
  "SK135",
  "SK136",
  "SK182",
  "SK201",
  "SK225",
  "SK239",
  "SK242",
  "SK271",
  "SK281",
  "SK286",
  "SK312",
  "SK619",
  "SK774",
  "SK911",
]);

// ── Quick filter presets ──────────────────────────────────────────────────────
const QUICK_FILTERS = [
  { label: "All", filter: () => true },
  { label: "Technical", filter: (s) => s.type === "technical" },
  { label: "Soft Skills", filter: (s) => s.type === "soft" },
  { label: "Certifications", filter: (s) => s.type === "credential" },
  { label: "Popular", filter: (s) => POPULAR_IDS.has(s.skill_id) },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
const WINDOW_SIZE = 80; // render at most N items at a time in the dropdown
const DEBOUNCE_MS = 200;

function fuzzyMatch(text, query) {
  if (!query) return true;
  const t = text.toLowerCase();
  const q = query.toLowerCase();
  // exact substring
  if (t.includes(q)) return true;
  // token match (all query tokens must appear)
  const tokens = q.split(/\s+/).filter(Boolean);
  return tokens.every((tok) => t.includes(tok));
}

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const h = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(h);
  }, [value, delay]);
  return debounced;
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function SkillSelector({ selected = [], onChange }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState(0); // index into QUICK_FILTERS
  const [expandedGroups, setExpandedGroups] = useState(
    () => new Set(GROUP_ORDER),
  );
  const [visibleCount, setVisibleCount] = useState(WINDOW_SIZE);
  const containerRef = useRef(null);
  const listRef = useRef(null);

  const debouncedQuery = useDebounce(query, DEBOUNCE_MS);

  // ── Normalized skills list (cached once) ──────────────────────────────
  const normalized = useMemo(() => {
    return skillsList.map((s) => ({
      id: String(s.skill_id),
      label: s.name,
      category: s.category || "other",
      type: s.type || "technical",
      skill_id: s.skill_id,
    }));
  }, []);

  const idToLabel = useMemo(() => {
    const m = new Map();
    for (const s of normalized) m.set(s.id.toLowerCase(), s.label);
    return m;
  }, [normalized]);

  // ── Selected IDs ──────────────────────────────────────────────────────
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
    [selectedIds],
  );

  // ── Filtered + grouped skills ────────────────────────────────────────
  const { grouped, flatFiltered, totalMatches } = useMemo(() => {
    const quickFn = QUICK_FILTERS[activeFilter].filter;
    const q = debouncedQuery.trim();

    const matches = normalized.filter((s) => {
      if (!quickFn(s)) return false;
      return fuzzyMatch(s.label, q) || fuzzyMatch(s.id, q);
    });

    // Group by group → sub
    const groups = {};
    for (const s of matches) {
      const mapping = CATEGORY_MAP[s.category] || {
        group: "Technical Skills",
        sub: "Other",
      };
      if (!groups[mapping.group]) groups[mapping.group] = {};
      if (!groups[mapping.group][mapping.sub])
        groups[mapping.group][mapping.sub] = [];
      groups[mapping.group][mapping.sub].push(s);
    }

    // Sort groups by GROUP_ORDER
    const ordered = {};
    for (const g of GROUP_ORDER) {
      if (groups[g]) {
        ordered[g] = {};
        for (const sub of Object.keys(groups[g]).sort()) {
          ordered[g][sub] = groups[g][sub];
        }
      }
    }

    // Flat list for windowed rendering
    const flat = matches;
    return {
      grouped: ordered,
      flatFiltered: flat,
      totalMatches: matches.length,
    };
  }, [normalized, debouncedQuery, activeFilter]);

  // Reset visible count on filter/query change
  useEffect(() => {
    setVisibleCount(WINDOW_SIZE);
  }, [debouncedQuery, activeFilter]);

  // Infinite-scroll: load more when scrolled near bottom
  const handleScroll = useCallback(() => {
    const el = listRef.current;
    if (!el) return;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 40) {
      setVisibleCount((prev) => Math.min(prev + WINDOW_SIZE, totalMatches));
    }
  }, [totalMatches]);

  // ── Toggle / Remove ──────────────────────────────────────────────────
  function toggle(id) {
    const sid = String(id);
    if (selectedSetLower.has(sid.toLowerCase())) {
      remove(sid);
    } else {
      const next = [...selectedIds, sid];
      if (typeof onChange === "function") onChange(next);
    }
  }

  function remove(id) {
    const sid = String(id);
    const next = selectedIds.filter(
      (x) => x.toLowerCase() !== sid.toLowerCase(),
    );
    if (typeof onChange === "function") onChange(next);
  }

  function selectAllInSub(skills) {
    const toAdd = skills
      .filter((s) => !selectedSetLower.has(s.id.toLowerCase()))
      .map((s) => s.id);
    if (toAdd.length > 0) {
      const next = [...selectedIds, ...toAdd];
      if (typeof onChange === "function") onChange(next);
    }
  }

  function labelFor(id) {
    if (!id && id !== 0) return "";
    return idToLabel.get(String(id).toLowerCase()) || String(id);
  }

  function toggleGroup(group) {
    setExpandedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(group)) next.delete(group);
      else next.add(group);
      return next;
    });
  }

  // ── Click outside → close ────────────────────────────────────────────
  useEffect(() => {
    if (!open) return;
    function handleClickOutside(event) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  // ── Render helpers ───────────────────────────────────────────────────
  const renderSkillRow = useCallback(
    (s) => {
      const isSelected = selectedSetLower.has(s.id.toLowerCase());
      return (
        <div
          key={s.id}
          onMouseDown={(e) => {
            e.preventDefault();
            toggle(s.id);
          }}
          className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer
                     border-b border-gray-50 last:border-b-0
                     transition-all duration-100
                     ${
                       isSelected
                         ? "bg-blue-50 text-blue-700"
                         : "hover:bg-gray-50 text-gray-700"
                     }`}
        >
          {/* Checkbox */}
          <div
            className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0
                       transition-colors duration-100
                       ${
                         isSelected
                           ? "bg-blue-500 border-blue-500"
                           : "border-gray-300 hover:border-blue-400"
                       }`}
          >
            {isSelected && (
              <svg
                className="w-3 h-3 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </div>
          <span className="text-sm font-medium truncate">{s.label}</span>
          <span className="ml-auto text-[10px] text-gray-400 uppercase tracking-wide flex-shrink-0">
            {s.category.replace("_", " ")}
          </span>
        </div>
      );
    },
    [selectedSetLower, selectedIds], // eslint-disable-line react-hooks/exhaustive-deps
  );

  // ── Build windowed flat list ─────────────────────────────────────────
  const windowedItems = useMemo(() => {
    // If searching or using a non-default filter, show flat list (windowed)
    if (debouncedQuery.trim() || activeFilter !== 0) {
      return flatFiltered.slice(0, visibleCount);
    }
    return null; // signal to use grouped view
  }, [debouncedQuery, activeFilter, flatFiltered, visibleCount]);

  return (
    <div className="relative" ref={containerRef}>
      {/* ── Selected Skills (tags) ──────────────────────────────────────── */}
      {selectedIds.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {selectedIds.map((id, idx) => (
            <div
              key={id || `sel-${idx}`}
              className="group flex items-center gap-1.5 bg-gradient-to-r from-blue-50 to-indigo-50
                         border border-blue-200 px-2.5 py-1 rounded-full
                         shadow-sm hover:shadow-md hover:border-blue-300
                         transition-all duration-200"
            >
              <span className="text-xs font-medium text-blue-700 max-w-[140px] truncate">
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
                className="w-4 h-4 flex items-center justify-center rounded-full
                           bg-blue-100 text-blue-500 hover:bg-red-100 hover:text-red-500
                           transition-colors duration-150 text-[10px] font-bold"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ── Search Input ────────────────────────────────────────────────── */}
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
          placeholder="Search 1,147 skills (e.g. Python, React, AWS…)"
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
              className={`h-6 w-6 transform transition-transform duration-200 ${open ? "rotate-180" : ""}`}
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

      {/* ── Dropdown ────────────────────────────────────────────────────── */}
      {open && (
        <div
          className="absolute z-50 w-full mt-2 bg-white border border-gray-200
                     rounded-xl shadow-xl overflow-hidden
                     animate-in fade-in slide-in-from-top-2 duration-200"
        >
          {/* Quick filters */}
          <div className="flex items-center gap-1 px-3 py-2 bg-gray-50 border-b border-gray-100 overflow-x-auto">
            {QUICK_FILTERS.map((f, i) => (
              <button
                key={f.label}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  setActiveFilter(i);
                }}
                className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap
                           transition-colors duration-150
                           ${
                             activeFilter === i
                               ? "bg-blue-500 text-white"
                               : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
                           }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Scrollable list */}
          <div
            ref={listRef}
            className="max-h-72 overflow-auto"
            onScroll={handleScroll}
          >
            {totalMatches > 0 ? (
              windowedItems ? (
                /* ── Flat windowed list (search / filter active) ─── */
                <>
                  {windowedItems.map(renderSkillRow)}
                  {visibleCount < totalMatches && (
                    <div className="px-4 py-3 text-center text-xs text-gray-400">
                      Showing {visibleCount} of {totalMatches} — scroll for more
                    </div>
                  )}
                </>
              ) : (
                /* ── Grouped / categorised view (no search) ─────── */
                Object.entries(grouped).map(([group, subs]) => (
                  <div key={group}>
                    {/* Group header */}
                    <div
                      onMouseDown={(e) => {
                        e.preventDefault();
                        toggleGroup(group);
                      }}
                      className="flex items-center justify-between px-4 py-2 bg-gray-50
                                 border-b border-gray-100 cursor-pointer
                                 hover:bg-gray-100 transition-colors sticky top-0 z-10"
                    >
                      <div className="flex items-center gap-2">
                        <span>{GROUP_ICONS[group] || "📂"}</span>
                        <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                          {group}
                        </span>
                        <span className="text-[10px] text-gray-400">
                          (
                          {Object.values(subs).reduce(
                            (a, b) => a + b.length,
                            0,
                          )}
                          )
                        </span>
                      </div>
                      <svg
                        className={`w-4 h-4 text-gray-400 transform transition-transform ${
                          expandedGroups.has(group) ? "rotate-180" : ""
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
                    </div>

                    {expandedGroups.has(group) &&
                      Object.entries(subs).map(([sub, skills]) => (
                        <div key={sub}>
                          {/* Sub-category header */}
                          <div className="flex items-center justify-between px-6 py-1.5 bg-white border-b border-gray-50">
                            <span className="text-[11px] font-semibold text-gray-500">
                              {sub}
                              <span className="ml-1 text-gray-400">
                                ({skills.length})
                              </span>
                            </span>
                            <button
                              type="button"
                              onMouseDown={(e) => {
                                e.preventDefault();
                                selectAllInSub(skills);
                              }}
                              className="text-[10px] text-blue-500 hover:text-blue-700 font-semibold"
                            >
                              Select all
                            </button>
                          </div>
                          {skills.slice(0, visibleCount).map(renderSkillRow)}
                        </div>
                      ))}
                  </div>
                ))
              )
            ) : (
              /* ── Empty state ────────────────────────────────── */
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

          {/* Footer */}
          {totalMatches > 0 && (
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
              <p className="text-xs text-gray-400">
                💡 {totalMatches.toLocaleString()} skills
                {debouncedQuery.trim() ? " matching" : " available"} • Click to
                toggle
              </p>
              {selectedIds.length > 0 && (
                <button
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    if (typeof onChange === "function") onChange([]);
                  }}
                  className="text-[10px] text-red-500 hover:text-red-700 font-semibold"
                >
                  Clear all
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Selected count badge ────────────────────────────────────────── */}
      {selectedIds.length > 0 && (
        <div className="mt-3 flex items-center gap-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
            ✓ {selectedIds.length} skill{selectedIds.length !== 1 ? "s" : ""}{" "}
            selected
          </span>
        </div>
      )}
    </div>
  );
}
