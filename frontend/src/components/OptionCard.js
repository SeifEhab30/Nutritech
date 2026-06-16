import React from "react";

// Selectable card used by the Profile editor and Macros Calculator.
// `icon` is optional. Active state is driven by selectedValue === value.
const OptionCard = ({ icon, label, value, selectedValue, onClick }) => (
  <div
    className={`option-card ${selectedValue === value ? "active" : ""}`}
    onClick={() => onClick(value)}
  >
    {icon}
    <span>{label}</span>
  </div>
);

export default OptionCard;
