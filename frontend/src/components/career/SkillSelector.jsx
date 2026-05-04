import React, {
  useState,
  useMemo,
  useRef,
  useEffect,
  useCallback,
} from "react";
import skillsList from "../../data/skills.json";
import {
  mergeCareerButton,
  careerBaseButton,
  careerMutedButton,
  careerSecondaryDestructiveButton,
} from "./careerClassNames";

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
  other: { group: "Technical Skills", sub: "Other Technical" },
  // Soft Skills
  soft_skill: { group: "Soft Skills", sub: "General" },
  communication: { group: "Soft Skills", sub: "Communication" },
  leadership: { group: "Soft Skills", sub: "Leadership" },
  project_mgmt: { group: "Soft Skills", sub: "Project Management" },
  business: { group: "Soft Skills", sub: "Project Management" },
};

const GROUP_ORDER = ["Technical Skills", "Soft Skills"];
const GROUP_ICONS = {
  "Technical Skills": "💻",
  "Soft Skills": "🤝",
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
  { label: "Popular", filter: (s) => POPULAR_IDS.has(s.skill_id) },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
const WINDOW_SIZE = 80;
const DEBOUNCE_MS = 200;
const MAX_VISIBLE_TAGS = 30;

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
export default function SkillSelector({
  selectedSkills = [],
  onChange,
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState(0); // index into QUICK_FILTERS
  const [activeCategory, setActiveCategory] = useState("All");
  const [expandedGroups, setExpandedGroups] = useState(
    () => new Set(GROUP_ORDER),
  );
  const [visibleCount, setVisibleCount] = useState(WINDOW_SIZE);
  const [showAllSkills, setShowAllSkills] = useState(false);
  const containerRef = useRef(null);
  const listRef = useRef(null);
  const inputRef = useRef(null);

  const debouncedQuery = useDebounce(query, DEBOUNCE_MS);

  // ── Normalized skills list (cached once) ──────────────────────────────
  const normalized = useMemo(() => {
    return skillsList
      .filter(
        (s) =>
          (s.category || "other") !== "game_dev" &&
          s.category !== "certification" &&
          s.type !== "credential",
      )
      .map((s) => ({
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
    return (selectedSkills || [])
      .map((s) => {
        if (s == null) return "";
        if (typeof s === "string" || typeof s === "number") return String(s);
        return String(s.id ?? s.skill_id ?? s.skillId ?? "");
      })
      .filter(Boolean);
  }, [selectedSkills]);

  const selectedSetLower = useMemo(
    () => new Set(selectedIds.map((s) => s.toLowerCase())),
    [selectedIds],
  );

  const visibleSelectedIds = useMemo(() => {
    if (showAllSkills || selectedIds.length <= MAX_VISIBLE_TAGS) {
      return selectedIds;
    }
    return selectedIds.slice(0, MAX_VISIBLE_TAGS);
  }, [selectedIds, showAllSkills]);

  const hiddenTagCount = selectedIds.length - MAX_VISIBLE_TAGS;

  useEffect(() => {
    if (selectedIds.length <= MAX_VISIBLE_TAGS) {
      setShowAllSkills(false);
    }
  }, [selectedIds.length]);

  // Reset active category on top-level filter change
  useEffect(() => {
    setActiveCategory("All");
  }, [activeFilter]);

  // ── Filtered + grouped skills ────────────────────────────────────────
  const { grouped, flatFiltered, totalMatches, availableCategories } =
    useMemo(() => {
      const quickFn = QUICK_FILTERS[activeFilter].filter;
      const q = debouncedQuery.trim();

      // 1. Filter by Quick Filter & Search Query
      const baseMatches = normalized.filter((s) => {
        if (!quickFn(s)) return false;

        const mapping = CATEGORY_MAP[s.category] || {
          group: "Technical Skills",
          sub: "Other",
        };
        const searchableText =
          `${s.label} ${mapping.group} ${mapping.sub}`.toLowerCase();
        return fuzzyMatch(searchableText, q) || fuzzyMatch(s.id, q);
      });

      // 2. Extract available categories from base matching results
      const categoriesSet = new Set();
      for (const s of baseMatches) {
        const mapping = CATEGORY_MAP[s.category] || { sub: "Other" };
        categoriesSet.add(mapping.sub);
      }
      const availableCategories = Array.from(categoriesSet).sort();

      // 3. Apply active category filter
      const matches =
        activeCategory === "All"
          ? baseMatches
          : baseMatches.filter((s) => {
              const mapping = CATEGORY_MAP[s.category] || { sub: "Other" };
              return mapping.sub === activeCategory;
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
        availableCategories,
      };
    }, [normalized, debouncedQuery, activeFilter, activeCategory]);

  // Reset visible count on filter/query/category change
  useEffect(() => {
    setVisibleCount(WINDOW_SIZE);
  }, [debouncedQuery, activeFilter, activeCategory]);

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

  const handleClearAllSkills = useCallback(() => {
    if (typeof onChange === "function") onChange([]);
  }, [onChange]);

  const handleClearCategorySkills = useCallback((category) => {
    if (typeof onChange !== "function") return;
    if (category === "All") {
      onChange([]);
      return;
    }
    const newSelection = selectedIds.filter((id) => {
      const skill = normalized.find((s) => s.id === id);
      if (!skill) return true;
      const mapping = CATEGORY_MAP[skill.category] || { sub: "Other" };
      return mapping.sub !== category;
    });
    onChange(newSelection);
  }, [onChange, selectedIds, normalized]);

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

  // ── Anchor viewport to search input on open/close to prevent jumps ───
  useEffect(() => {
    // Use requestAnimationFrame to wait for DOM to settle after tags show/hide
    const raf = requestAnimationFrame(() => {
      if (inputRef.current) {
        inputRef.current.scrollIntoView({
          block: "nearest",
          behavior: "instant",
        });
      }
    });
    return () => cancelAnimationFrame(raf);
  }, [open]);

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
          className={`flex justify-between items-center gap-3 px-4 py-2 cursor-pointer
                     transition-all duration-200 ease-in-out
                     ${
                       isSelected
                         ? "bg-indigo-50 text-indigo-700"
                         : "hover:bg-gray-100 text-gray-600"
                     }`}
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
          <div
            className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0
                       transition-colors duration-100
                       ${
                         isSelected
                           ? "bg-indigo-600 border-indigo-600"
                           : "border-gray-300 hover:border-indigo-400"
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
          </div>
          <span className="text-[10px] text-gray-400 uppercase tracking-wide flex-shrink-0">
            {s.category.replace("_", " ")}
          </span>
        </div>
      );
    },
    [selectedSetLower, selectedIds], // eslint-disable-line react-hooks/exhaustive-deps
  );

  // ── Build windowed flat list ─────────────────────────────────────────
  const windowedItems = useMemo(() => {
    // If searching or using a non-default filter/category, show flat list (windowed)
    if (
      debouncedQuery.trim() ||
      activeFilter !== 0 ||
      activeCategory !== "All"
    ) {
      return flatFiltered.slice(0, visibleCount);
    }
    return null; // signal to use grouped view
  }, [
    debouncedQuery,
    activeFilter,
    activeCategory,
    flatFiltered,
    visibleCount,
  ]);

  return (
    <div className="relative z-20" ref={containerRef}>
      {/* ── Selected Skills (tags) — hidden while dropdown is open to prevent layout shift ── */}
      {selectedIds.length > 0 && !open && (
        <div className="mb-3">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">
              Selected ({selectedIds.length})
            </span>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                handleClearAllSkills();
              }}
              className={mergeCareerButton(
                careerBaseButton,
                careerSecondaryDestructiveButton,
                "text-[11px] px-3 py-1 rounded-lg font-semibold hover:scale-[1.02]",
              )}
            >
              Clear All
            </button>
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            {visibleSelectedIds.map((id, idx) => (
              <div
                key={id || `sel-${idx}`}
                className="group flex items-center gap-1.5 bg-indigo-50
                           border border-indigo-200 px-2.5 py-1 rounded-full
                           shadow-sm hover:shadow-md hover:border-indigo-300
                           transition-all duration-200"
              >
                <span className="text-xs font-medium text-indigo-700 max-w-[140px] truncate">
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
                             bg-transparent text-indigo-500 hover:bg-red-50 hover:text-red-500
                             transition-colors duration-150 text-[10px] font-bold
                             border border-transparent focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
                >
                  ✕
                </button>
              </div>
            ))}
            {!showAllSkills && hiddenTagCount > 0 && (
              <button
                type="button"
                onClick={() => setShowAllSkills(true)}
                className="text-sm font-medium text-indigo-600 hover:text-indigo-800 hover:underline transition-all duration-200 ease-in-out px-1 py-0.5 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              >
                +{hiddenTagCount} more
              </button>
            )}
            {showAllSkills && selectedIds.length > MAX_VISIBLE_TAGS && (
              <button
                type="button"
                onClick={() => setShowAllSkills(false)}
                className="text-sm text-gray-500 hover:text-gray-700 hover:underline transition-all duration-200 ease-in-out px-1 py-0.5 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              >
                Show less
              </button>
            )}
          </div>
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
          ref={inputRef}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!open) setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Search 1,147 skills (e.g. Python, React, AWS…)"
          className="w-full pl-10 pr-20 py-3
                     border border-gray-200 rounded-xl
                     bg-white/90 text-gray-700 placeholder-gray-400
                     focus:border-purple-300 focus:ring-2 focus:ring-purple-500/30
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
              className="text-gray-400 hover:text-gray-600 transition-all duration-200 bg-transparent p-1 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-purple-500/30 hover:scale-105 active:scale-[0.95]"
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
            className="text-gray-400 hover:text-gray-600 transition-all duration-200 bg-transparent p-1 rounded-lg border border-transparent focus:outline-none focus:ring-2 focus:ring-purple-500/30 hover:scale-105 active:scale-[0.95]"
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
          className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-gray-200
                     rounded-2xl shadow-xl overflow-hidden animate-fadeIn transition-all duration-200 ease-in-out"
        >
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2.5 flex justify-between items-center gap-3">
            <span className="text-sm font-semibold tracking-tight">
              Browse skills
            </span>
            <span className="text-xs font-medium text-white/90 tabular-nums">
              {totalMatches.toLocaleString()} available
            </span>
          </div>
          {selectedIds.length > 0 && (
            <div className="flex items-center justify-between px-4 py-2 bg-gray-50/90 border-b border-gray-100">
              <span className="text-xs font-bold text-gray-700">
                ✓ {selectedIds.length} skill
                {selectedIds.length !== 1 ? "s" : ""} selected
              </span>
              <button
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  if (typeof onChange === "function") onChange([]);
                }}
                className={mergeCareerButton(
                  careerBaseButton,
                  careerSecondaryDestructiveButton,
                  "text-[11px] px-3 py-1 rounded-lg font-semibold",
                )}
              >
                Clear All
              </button>
            </div>
          )}

          {/* Quick filters */}
          <div className="flex items-center gap-1 px-3 py-2 bg-gray-50 border-b border-gray-100 overflow-x-auto scrollbar-hide">
            {QUICK_FILTERS.map((f, i) => (
              <button
                key={f.label}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  setActiveFilter(i);
                }}
                className={`px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap
                           transition-all duration-200 border border-transparent
                           focus:outline-none focus:ring-2 focus:ring-purple-500/30
                           hover:scale-[1.02] active:scale-[0.98]
                           ${
                             activeFilter === i
                               ? "bg-[#9333ea] text-white shadow-sm"
                               : "bg-white/90 text-gray-600 hover:bg-gray-50 border-gray-200 shadow-sm"
                           }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Category Filters */}
          {availableCategories.length > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-2 bg-white border-b border-gray-100 overflow-x-auto scrollbar-hide">
              <button
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  setActiveCategory("All");
                }}
                className={`px-3 py-1.5 rounded-md text-[13px] font-bold whitespace-nowrap transition-all duration-200
                           border border-transparent focus:outline-none focus:ring-2 focus:ring-purple-500/30
                           hover:scale-[1.02] active:scale-[0.98]
                           ${
                             activeCategory === "All"
                               ? "bg-[#0d6efd] text-white shadow-sm"
                               : "bg-white/90 text-gray-600 hover:bg-gray-50 border-gray-200 shadow-sm"
                           }`}
              >
                All Categories
              </button>
              {availableCategories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    setActiveCategory(cat);
                  }}
                  className={`px-3 py-1.5 rounded-md text-[13px] font-bold whitespace-nowrap transition-all duration-200
                             border border-transparent focus:outline-none focus:ring-2 focus:ring-purple-500/30
                             hover:scale-[1.02] active:scale-[0.98]
                             ${
                               activeCategory === cat
                                 ? "bg-[#0d6efd] text-white shadow-sm"
                                 : "bg-white/90 text-gray-600 border-gray-200 hover:bg-gray-50 shadow-sm"
                             }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          )}

          {/* Action Header / Select All (when filtered) */}
          {(activeFilter !== 0 ||
            activeCategory !== "All" ||
            debouncedQuery.trim() !== "") &&
            totalMatches > 0 && (
              <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-inner">
                <div className="text-xs font-semibold">
                  {totalMatches} matching skills
                </div>
                <button
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    selectAllInSub(flatFiltered);
                  }}
                  className={mergeCareerButton(
                    careerBaseButton,
                    careerMutedButton,
                    "text-xs px-3 py-1.5 rounded-lg font-bold shadow-sm hover:scale-[1.02]",
                  )}
                >
                  Select All
                </button>
              </div>
            )}

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
                  <div className="divide-y divide-gray-100">
                    {windowedItems.map(renderSkillRow)}
                  </div>
                  {visibleCount < totalMatches && (
                    <div className="px-4 py-3 text-center text-xs text-gray-400">
                      Showing {visibleCount} of {totalMatches} — scroll for more
                    </div>
                  )}
                </>
              ) : (
                /* ── Grouped / categorised view (no search) ─────── */
                Object.entries(grouped).map(([group, subs], groupIndex) => (
                  <div key={group}>
                    {groupIndex > 0 && (
                      <div className="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent my-4" />
                    )}
                    <div
                      onMouseDown={(e) => {
                        e.preventDefault();
                        toggleGroup(group);
                      }}
                      className="flex items-center justify-between px-4 py-2.5 bg-gray-50/95
                                 border-b border-gray-100 cursor-pointer
                                 hover:bg-gray-100 transition-all duration-200 ease-in-out sticky top-0 z-10"
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
                      Object.entries(subs).map(([sub, skills], subIndex, subEntries) => (
                        <div key={sub} className="mb-4 last:mb-0">
                          <div className="flex items-start sm:items-center justify-between gap-2 px-4 pt-3 pb-2">
                            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide px-1">
                              {sub}
                              <span className="ml-1.5 font-normal normal-case text-gray-400">
                                ({skills.length})
                              </span>
                            </div>
                            <button
                              type="button"
                              onMouseDown={(e) => {
                                e.preventDefault();
                                selectAllInSub(skills);
                              }}
                              className={mergeCareerButton(
                                careerBaseButton,
                                careerMutedButton,
                                "text-[10px] px-2.5 py-1 rounded-lg font-bold shrink-0 uppercase tracking-wide",
                              )}
                            >
                              Select All
                            </button>
                          </div>
                          <div className="space-y-0 mx-2 rounded-xl border border-gray-100/90 overflow-hidden divide-y divide-gray-100 bg-white/80">
                            {skills
                              .slice(0, visibleCount)
                              .map(renderSkillRow)}
                          </div>
                          {subIndex < subEntries.length - 1 && (
                            <div className="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent my-4 mx-1" />
                          )}
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
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between gap-4 sticky bottom-0 z-20 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
              <div className="flex flex-col">
                <p className="text-xs text-gray-500 font-medium">
                  {totalMatches.toLocaleString()} skills
                  {debouncedQuery.trim() || activeCategory !== "All"
                    ? " matching filters"
                    : " available"}
                </p>
              </div>

              {selectedIds.length > 0 && (
                <button
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    handleClearCategorySkills(activeCategory);
                  }}
                  className={mergeCareerButton(
                    careerBaseButton,
                    careerSecondaryDestructiveButton,
                    "text-xs px-3 py-1.5 rounded-lg font-bold",
                  )}
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
