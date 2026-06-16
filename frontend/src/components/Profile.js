import React, { useState } from "react";
import PreferencesTab from "./PreferencesTab";
import CurrentPlanTab from "./CurrentPlanTab";
import DailyTrackerTab from "./DailyTrackerTab";
import ProgressDashboardTab from "./ProgressDashboardTab";
import "./Profile.css";

const TABS = [
  { key: "preferences", label: "Preferences" },
  { key: "plan", label: "Current Plan" },
  { key: "tracker", label: "Daily Tracker" },
  { key: "progress", label: "Progress" },
];

const Profile = () => {
  const [tab, setTab] = useState("preferences");

  return (
    <div className="profile-container">
      <div className="profile-shell">
        <div className="profile-box">
          <h2>My Profile</h2>
          <p className="profile-sub">
            Your preferences, plan, daily tracking and progress in one place.
          </p>

          <div className="profile-tabs">
            {TABS.map((t) => (
              <button key={t.key}
                className={`profile-tab ${tab === t.key ? "active" : ""}`}
                onClick={() => setTab(t.key)}>
                {t.label}
              </button>
            ))}
          </div>

          <div className="profile-tab-body">
            {tab === "preferences" && <PreferencesTab />}
            {tab === "plan" && <CurrentPlanTab />}
            {tab === "tracker" && <DailyTrackerTab />}
            {tab === "progress" && <ProgressDashboardTab />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
