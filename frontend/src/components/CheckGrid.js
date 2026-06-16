import React from "react";
import "./CheckGrid.css";

// A clear multi-select grid: white cards by default, filled when checked,
// with a visible checkbox. `variant="allergen"` tints the selected fill red.
const CheckGrid = ({ options, selected, onToggle, variant = "" }) => (
  <div className="check-grid">
    {options.map((o) => {
      const checked = selected.includes(o.value);
      return (
        <button
          type="button"
          key={o.value}
          className={`check-item ${variant} ${checked ? "checked" : ""}`}
          aria-pressed={checked}
          onClick={() => onToggle(o.value)}
        >
          <span className="check-box">{checked ? "✓" : ""}</span>
          <span className="check-label">{o.label}</span>
        </button>
      );
    })}
  </div>
);

export default CheckGrid;
