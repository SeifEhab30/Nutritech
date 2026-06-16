import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine,
} from "recharts";
import { getRange } from "../api/trackerApi";

const todayStr = () => new Date().toLocaleDateString("en-CA");
const daysAgo = (n) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toLocaleDateString("en-CA");
};

const ProgressDashboardTab = () => {
  const [span, setSpan] = useState(7); // 7 = week, 30 = month
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    getRange(daysAgo(span - 1), todayStr())
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [span]);

  const days = (data?.days || []).map((d) => ({ ...d, label: d.date.slice(5) }));
  const target = data?.target;

  // Summary stats over days that actually have logs.
  const logged = days.filter((d) => d.calories > 0);
  const avgCals = logged.length
    ? Math.round(logged.reduce((s, d) => s + d.calories, 0) / logged.length)
    : 0;
  const onTarget = target?.calories
    ? logged.filter(
        (d) => d.calories >= target.calories * 0.85 && d.calories <= target.calories * 1.15
      ).length
    : 0;
  const onTargetPct = logged.length ? Math.round((onTarget / logged.length) * 100) : 0;

  return (
    <div className="dashboard">
      <div className="dashboard-head">
        <h3>Progress</h3>
        <div className="mode-toggle">
          <button className={`mode-tab ${span === 7 ? "active" : ""}`}
            onClick={() => setSpan(7)}>Week</button>
          <button className={`mode-tab ${span === 30 ? "active" : ""}`}
            onClick={() => setSpan(30)}>Month</button>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Loading…</p>
      ) : (
        <>
          <div className="dash-stats">
            <div className="dash-stat">
              <span className="ds-val">{avgCals}</span>
              <span className="ds-lbl">Avg kcal / logged day</span>
            </div>
            <div className="dash-stat">
              <span className="ds-val">{logged.length}</span>
              <span className="ds-lbl">Days logged</span>
            </div>
            <div className="dash-stat">
              <span className="ds-val">{onTargetPct}%</span>
              <span className="ds-lbl">Days on target (±15%)</span>
            </div>
          </div>

          <div className="chart-card">
            <h4>Calories vs target</h4>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={days} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis dataKey="label" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                {target?.calories ? (
                  <ReferenceLine y={target.calories} stroke="#0F5132"
                    strokeDasharray="5 4"
                    label={{ value: "target", position: "right", fontSize: 11, fill: "#0F5132" }} />
                ) : null}
                <Line type="monotone" dataKey="calories" stroke="#34D399"
                  strokeWidth={2.5} dot={{ r: 2 }} name="kcal" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h4>Macros per day (g)</h4>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={days} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis dataKey="label" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                <Bar dataKey="protein" fill="#0F5132" name="Protein" />
                <Bar dataKey="carbs" fill="#34D399" name="Carbs" />
                <Bar dataKey="fat" fill="#A7F3D0" name="Fat" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
};

export default ProgressDashboardTab;
