import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { subscribe, unsubscribe } from "../api/authApi";
import { usePremium } from "./PremiumGate";
import "./Pricing.css";

const FREE_FEATURES = [
  { label: "Macros Calculator", ok: true },
  { label: "Food Search", ok: true },
  { label: "Daily Meal Plan", ok: true },
  { label: "Profile & Daily Tracker", ok: true },
  { label: "AI Chatbot", ok: false },
  { label: "Image Recognition", ok: false },
  { label: "Weekly Meal Plans", ok: false },
];

const PREMIUM_FEATURES = [
  "Everything in Free",
  "AI Nutrition Chatbot",
  "Food Image Recognition",
  "Weekly Meal Plans",
];

const Pricing = () => {
  const { loading, premium } = usePremium();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubscribe = async () => {
    setBusy(true);
    setError(null);
    try {
      await subscribe();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const handleDowngrade = async () => {
    setBusy(true);
    setError(null);
    try {
      await unsubscribe();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="pricing-page">
      <div className="pricing-header">
        <h1>Choose your plan</h1>
        <p>Start free. Upgrade to Premium to unlock the AI features.</p>
      </div>

      {error && <p className="pricing-error">{error}</p>}

      <div className="pricing-grid">
        {/* Free tier */}
        <div className={`tier-card ${!premium && !loading ? "current" : ""}`}>
          {!premium && !loading && <span className="tier-badge">Current plan</span>}
          <h2 className="tier-name">Free</h2>
          <div className="tier-price">
            $0<span>/mo</span>
          </div>
          <ul className="tier-features">
            {FREE_FEATURES.map((f) => (
              <li key={f.label} className={f.ok ? "yes" : "no"}>
                {f.ok ? "✓" : "✕"} {f.label}
              </li>
            ))}
          </ul>
          <button className="tier-btn ghost" disabled>
            {premium ? "Downgrade available below" : "Your current plan"}
          </button>
        </div>

        {/* Premium tier */}
        <div className={`tier-card premium ${premium ? "current" : ""}`}>
          <span className="tier-flag">★ Premium</span>
          {premium && <span className="tier-badge gold">Current plan</span>}
          <h2 className="tier-name">Premium</h2>
          <div className="tier-price">
            $9<span>/mo</span>
          </div>
          <ul className="tier-features">
            {PREMIUM_FEATURES.map((f) => (
              <li key={f} className="yes gold-check">
                ✓ {f}
              </li>
            ))}
          </ul>
          {premium ? (
            <>
              <button className="tier-btn gold" onClick={() => navigate("/")} disabled={busy}>
                You're Premium ✓
              </button>
              <button className="tier-downgrade" onClick={handleDowngrade} disabled={busy}>
                {busy ? "…" : "Downgrade to Free"}
              </button>
            </>
          ) : (
            <button className="tier-btn gold" onClick={handleSubscribe} disabled={busy || loading}>
              {busy ? "Processing…" : "Subscribe"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Pricing;
