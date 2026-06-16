import React, { useState, useEffect } from "react";
import { getProfile } from "../api/profileApi";
import { calculateMacros } from "../api/planApi";
import OptionCard from "./OptionCard";
import { GOALS, ACTIVITY_LEVELS, DIET_TYPES } from "../constants/nutrition";
import "./MacrosCalculator.css";

const MacrosCalculator = () => {
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("male");
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [activityLevel, setActivityLevel] = useState("sedentary");
  const [generalGoal, setGeneralGoal] = useState("weight_loss");
  const [dietType, setDietType] = useState("balanced");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Prefill from the saved profile so the calculator reflects your settings.
  useEffect(() => {
    (async () => {
      try {
        const p = await getProfile();
        if (p.age) setAge(p.age);
        if (p.gender) setGender(p.gender);
        if (p.height) setHeight(p.height);
        if (p.weight) setWeight(p.weight);
        if (p.activity_level) setActivityLevel(p.activity_level);
        if (p.general_goal) setGeneralGoal(p.general_goal);
        if (p.diet_type) setDietType(p.diet_type);
      } catch {
        /* no profile yet — keep defaults */
      }
    })();
  }, []);

  // Keto only valid with weight_loss.
  useEffect(() => {
    if (generalGoal !== "weight_loss" && dietType === "keto") {
      setDietType("balanced");
    }
  }, [generalGoal, dietType]);

  const handleInputChange = (setter) => (e) => {
    const value = e.target.value;
    if (value >= 0) setter(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!age || !height || !weight) {
      setError("Please fill all fields");
      return;
    }
    setError(null);
    try {
      const data = await calculateMacros({
        age: Number(age),
        gender,
        height: Number(height),
        weight: Number(weight),
        activityLevel,
        generalGoal,
        dietType,
      });
      setResults(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReset = () => {
    setAge("");
    setGender("male");
    setHeight("");
    setWeight("");
    setActivityLevel("sedentary");
    setGeneralGoal("weight_loss");
    setDietType("balanced");
    setResults(null);
    setError(null);
  };

  const handleShare = () => {
    const shareText = `My daily needs:
Calories: ${results.calories} kcal
Protein: ${results.protein} g
Carbs: ${results.carbs} g
Fats: ${results.fats} g`;
    navigator.clipboard.writeText(shareText);
    alert("Results copied to clipboard!");
  };

  const dietOptions = DIET_TYPES.filter(
    (d) => !d.goal || d.goal === generalGoal
  );

  return (
    <div className="macros-calculator-page">
      <div className="macros-calculator">
        <h2>Macros Calculator</h2>
        <p className="calc-sub">
          A what-if calculator — it won't change your saved profile.
        </p>
        {error && <p className="error-message">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Age</label>
              <input type="number" value={age} onChange={handleInputChange(setAge)} min="1" step="1" required />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <div className="options-container">
                <OptionCard label="Male" value="male" selectedValue={gender} onClick={setGender} />
                <OptionCard label="Female" value="female" selectedValue={gender} onClick={setGender} />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Height (cm)</label>
              <input type="number" value={height} onChange={handleInputChange(setHeight)} min="1" step="0.1" required />
            </div>
            <div className="form-group">
              <label>Weight (kg)</label>
              <input type="number" value={weight} onChange={handleInputChange(setWeight)} min="1" step="0.1" required />
            </div>
          </div>

          <div className="form-group">
            <label>Activity Level</label>
            <div className="options-container">
              {ACTIVITY_LEVELS.map((a) => (
                <OptionCard key={a.value} label={a.label} value={a.value}
                  selectedValue={activityLevel} onClick={setActivityLevel} />
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Goal</label>
            <div className="options-container">
              {GOALS.map((g) => (
                <OptionCard key={g.value} label={g.label} value={g.value}
                  selectedValue={generalGoal} onClick={setGeneralGoal} />
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Diet Type</label>
            <select value={dietType} onChange={(e) => setDietType(e.target.value)}>
              {dietOptions.map((d) => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>


          <button type="submit">Calculate</button>
          <button type="button" onClick={handleReset}>Reset</button>
        </form>
      </div>

      {results && (
        <div className="results-section">
          <h3>Your Daily Needs</h3>
          <div className="results-grid">
            <div className="result-card"><h4>Calories</h4><p>{results.calories} kcal</p></div>
            <div className="result-card"><h4>Protein</h4><p>{results.protein} g</p></div>
            <div className="result-card"><h4>Carbs</h4><p>{results.carbs} g</p></div>
            <div className="result-card"><h4>Fats</h4><p>{results.fats} g</p></div>
          </div>
          <button type="button" onClick={handleShare}>Share</button>
        </div>
      )}
    </div>
  );
};

export default MacrosCalculator;
