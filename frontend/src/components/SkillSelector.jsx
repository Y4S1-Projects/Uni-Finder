import React, { useState, useMemo } from "react";
import skillsList from "../data/skills.json";

export default function SkillSelector({ selected = [], onChange }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  const normalized = useMemo(() => {
    return skillsList.map((s) => ({ id: s.skill_id, label: s.name }));
  }, []);

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

  function toggle(id) {
    const exists = selected.includes(id);
    const next = exists ? selected.filter((x) => x !== id) : [...selected, id];
    onChange(next);
  }

  function remove(id) {
    onChange(selected.filter((x) => x !== id));
  }

  function labelFor(id) {
    const found = normalized.find((s) => s.id === id);
    return found ? found.label : id;
  }

  return (
    <div style={{ position: "relative" }}>
      <div
        style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 6 }}
      >
        {selected.map((id) => (
          <div
            key={id}
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
              onClick={() => remove(id)}
              style={{
                background: "transparent",
                border: "none",
                cursor: "pointer",
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
              onMouseDown={() => toggle(s.id)}
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
                <div style={{ fontSize: 11, color: "#666" }}>{s.id}</div>
              </div>
              <div style={{ marginLeft: 8 }}>
                {selected.includes(s.id) ? "✓" : ""}
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
