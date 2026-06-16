import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getCurrentUser } from "../api/authApi";
import "./PremiumGate.css";

// Fetch + track the current user's premium status. Re-fetches on "authchange"
// (fired after login/logout/subscribe) so the UI unlocks without a reload.
export function usePremium() {
  const [state, setState] = useState({ loading: true, premium: false });

  useEffect(() => {
    let alive = true;
    const load = () => {
      getCurrentUser()
        .then((u) => alive && setState({ loading: false, premium: !!(u && u.is_premium) }))
        .catch(() => alive && setState({ loading: false, premium: false }));
    };
    load();
    window.addEventListener("authchange", load);
    return () => {
      alive = false;
      window.removeEventListener("authchange", load);
    };
  }, []);

  return state;
}

// The locked-feature card: gold padlock + upgrade message + Subscribe button.
// Bordered so it wraps just the feature, not the whole page.
export function PremiumLock({ feature = "This feature" }) {
  return (
    <div className="premium-lock">
      <div className="premium-lock-icon">🔒</div>
      <h3>Premium feature</h3>
      <p>
        {feature} is part of <strong>NutriTech Premium</strong>. Upgrade your
        plan to unlock it.
      </p>
      <Link to="/pricing" className="premium-lock-btn">
        Get Premium
      </Link>
    </div>
  );
}

// Route/section wrapper: shows the feature to premium users, the lock to free
// users, and a small loader while we check.
export default function PremiumGate({ feature, children }) {
  const { loading, premium } = usePremium();
  if (loading) return <div className="premium-gate-loading">Loading…</div>;
  if (premium) return children;
  return <PremiumLock feature={feature} />;
}
