def calculate_macros(data):
    # BMR Mifflin-St Jeor
    if data.gender == "male":
        bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age + 5
    else:
        bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age - 161

    # Activity multiplier
    activity_multipliers = {
        "sedentary": 1.2,
        "moderate": 1.55,
        "active": 1.725, # Match user.py 1.725 for active
    }

    tdee = bmr * activity_multipliers.get(data.activityLevel, 1.2)

    # Goal adjustment (weight objective only)
    if data.generalGoal == "weight_loss":
        final_calories = tdee - 500
    elif data.generalGoal == "weight_gain":
        final_calories = tdee + 350
    else:  # maintain_weight
        final_calories = tdee

    # Clamp calories
    floor = 1200 if data.gender == "male" else 1000
    ceiling = 4500
    final_calories = max(floor, min(ceiling, final_calories))

    # Macros calculation Ratios (Matching user.py). Diabetes flag overrides diet.
    if data.diabetes:
        p_ratio, c_ratio, f_ratio = 0.25, 0.40, 0.35
    elif data.dietType == "keto":
        p_ratio, c_ratio, f_ratio = 0.25, 0.05, 0.70
    elif data.dietType == "high_protein":
        p_ratio, c_ratio, f_ratio = 0.35, 0.35, 0.30
    else:  # balanced
        p_ratio, c_ratio, f_ratio = 0.20, 0.50, 0.30

    protein = (final_calories * p_ratio) / 4.0
    carbs   = (final_calories * c_ratio) / 4.0
    fats    = (final_calories * f_ratio) / 9.0

    return {
        "calories": int(round(final_calories)),
        "protein": int(round(protein)),
        "carbs": int(round(carbs)),
        "fats": int(round(fats)),
    }
