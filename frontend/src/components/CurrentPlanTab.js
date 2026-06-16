import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getCurrentPlan } from "../api/planApi";
import { humanize } from "../constants/nutrition";
import MealCard from "./MealCard";
import "./MealPlanner.css"; // reuse meal-card / meals-grid / plan-summary styles

// Read-only view of the user's saved daily plan. Generation stays in the
// Meal Planner page (linked below).
const CurrentPlanTab = () => {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setPlan(await getCurrentPlan());
      } catch {
        /* 404 => no saved plan yet */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <p>Loading…</p>;

  if (!plan) {
    return (
      <div className="tab-empty">
        <p>You don't have a saved meal plan yet.</p>
        <Link className="link-btn" to="/meal-planner">Go to Meal Planner →</Link>
      </div>
    );
  }

  const slots = Object.keys(plan.daily_plan.meals);

  return (
    <div className="plan-results">
      <div className="plan-summary">
        <h3>Your Current Plan</h3>
        <p className="plan-summary-line">
          Target: <strong>{Math.round(plan.daily_calories)} kcal</strong>
          {"  ·  "}Plan total:{" "}
          <strong>{Math.round(plan.daily_plan.total_calories)} kcal</strong>
        </p>
        <p className="plan-summary-macros">
          Daily macros — P {Math.round(plan.daily_protein)}g · C{" "}
          {Math.round(plan.daily_carbs)}g · F {Math.round(plan.daily_fat)}g
          {"  ·  "}Goal: {humanize(plan.final_goal)}
        </p>
        <Link className="link-btn" to="/meal-planner">Change in Meal Planner →</Link>
      </div>

      <div className="meals-grid">
        {slots.map((s) => (
          <MealCard key={s} slot={s} meal={plan.daily_plan.meals[s]} />
        ))}
      </div>
    </div>
  );
};

export default CurrentPlanTab;
