import React, { useState, useMemo } from "react";
import skillsList from "../data/skills.json";

export default function SkillSelector({ selected = [], onChange }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

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
    if (!q) return normalized.slice(0, 50);
    return normalized
      .filter(
        (s) =>
          s.label.toLowerCase().includes(q) || s.id.toLowerCase().includes(q)
      )
      .slice(0, 50);
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

  return (
    <div style={{ position: "relative" }}>
      <div
        style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 6 }}
      >
        {selectedIds.map((id, idx) => (
          <div
            key={id || `sel-${idx}`}
            style={{
              background: "#e6eef8",
              padding: "6px 8px",
              borderRadius: 16,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span style={{ fontSize: 12 }}>{labelFor(id)}</span>
            <button
              type="button"
              onMouseDown={(e) => {
                e.preventDefault();
                e.stopPropagation();
                remove(id);
              }}
              title={`Remove ${labelFor(id)}`}
              aria-label={`Remove ${labelFor(id)}`}
              style={{
                background: "transparent",
                border: "none",
                cursor: "pointer",
                fontSize: 12,
                lineHeight: 1,
                padding: 4,
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        placeholder="Type to search skills (e.g. python, sql)"
        style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
      />

      {open && (
        <div
          style={{
            position: "absolute",
            zIndex: 40,
            background: "white",
            border: "1px solid #ddd",
            width: "100%",
            maxHeight: 220,
            overflow: "auto",
            marginTop: 6,
          }}
        >
          {filtered.map((s) => (
            <div
              key={s.id}
              onMouseDown={(e) => {
                e.preventDefault();
                toggle(s.id);
              }}
              style={{
                padding: 8,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                cursor: "pointer",
              }}
            >
              <div>
                <div style={{ fontSize: 14 }}>{s.label}</div>
              </div>
              <div style={{ marginLeft: 8 }}>
                {selectedSetLower.has(String(s.id).toLowerCase()) ? "✓" : ""}
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ padding: 8, color: "#666" }}>No skills found</div>
          )}
        </div>
      )}
    </div>
  );
}
