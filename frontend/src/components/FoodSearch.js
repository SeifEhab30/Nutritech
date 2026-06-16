import React, { useState } from "react";
import { searchFoods } from "../api/foodsApi";
import "./FoodSearch.css";

const FoodSearch = () => {
  const [q, setQ] = useState("");
  const [results, setResults] = useState(null);
  const [usdaError, setUsdaError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    const query = q.trim();
    if (query.length < 2) {
      setError("Type at least 2 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await searchFoods(query);
      setResults(data.results);
      setUsdaError(data.usda_error || null);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const macroRow = (label, m) => (
    <div className="fs-macros">
      <span className="fs-macros-label">{label}</span>
      <span><strong>{Math.round(m.calories)}</strong> kcal</span>
      <span>P {Math.round(m.protein)}g</span>
      <span>C {Math.round(m.carbs)}g</span>
      <span>F {Math.round(m.fat)}g</span>
    </div>
  );

  return (
    <div className="food-search-page">
      <div className="food-search-container">
       <div className="fs-box">
        <div className="fs-header">
          <h2>Food & Macros Search</h2>
          <p>Look up any food and see its nutrition — powered by USDA FoodData Central + our curated dishes.</p>
        </div>

        <form className="fs-form" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="e.g. grilled chicken, banana, koshari…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
        </form>

        {error && <p className="fs-error">{error}</p>}

        {usdaError && (
          <p className="fs-notice">
            {usdaError === "rate_limited"
              ? "USDA search is rate-limited (using the shared demo key). Add a free USDA API key for full results — showing curated foods only."
              : "USDA search is temporarily unavailable — showing curated foods only."}
          </p>
        )}

        {results && results.length === 0 && (
          <p className="fs-empty">No foods found for “{q}”.</p>
        )}

        {results && results.length > 0 && (
          <ul className="fs-results">
            {results.map((r, i) => (
              <li key={`${r.source}-${i}`} className="fs-card">
                <div className="fs-card-head">
                  <span className="fs-name">{r.name}</span>
                  <span className={`fs-badge ${r.source}`}>
                    {r.source === "usda" ? "USDA" : "Curated"}
                  </span>
                </div>
                {macroRow("per 100g", r.per_100g)}
                {r.per_serving && macroRow(`per serving (${Math.round(r.serving_g)}g)`, r.per_serving)}
              </li>
            ))}
          </ul>
        )}
       </div>
      </div>
    </div>
  );
};

export default FoodSearch;
