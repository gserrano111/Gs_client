
from typing import Tuple, Dict

def mifflin_st_jeor(weight_kg: float, height_cm: float, age: int, sex: str, activity: str):
    # BMR
    if sex.upper() == "M":
        bmr = 10*weight_kg + 6.25*height_cm - 5*age + 5
    else:
        bmr = 10*weight_kg + 6.25*height_cm - 5*age - 161
    # Activity multipliers
    mult = {
        "sedentario": 1.2,
        "ligero": 1.375,
        "moderado": 1.55,
        "alto": 1.725,
        "atleta": 1.9
    }.get(activity, 1.55)
    tdee = bmr * mult
    return bmr, tdee

def build_gs_meal_plan(tdee: float, objective: str, meals_per_day: int = 3) -> Dict:
    # Objective deltas
    if objective == "pérdida de grasa":
        calories = tdee - 300
        protein_g = 2.0  # g/kg (aprox, se ajusta al registrar)
    elif objective == "ganancia de masa":
        calories = tdee + 200
        protein_g = 1.8
    elif objective == "mantenimiento":
        calories = tdee
        protein_g = 1.6
    else:  # recomposición
        calories = tdee - 100
        protein_g = 2.0

    # Macro splits por estilo GS (carbos moderados, fruta 1x en desayuno)
    # Tomamos 30% protein, 25% fat, 45% carbs como base, ajustable
    p = 0.30
    f = 0.25
    c = 0.45
    protein_g_total = round((calories*p)/4)
    fats_g_total = round((calories*f)/9)
    carbs_g_total = round((calories*c)/4)

    # Construcción de comidas (simplificada)
    meals = []
    base_meals = [
        "Desayuno: proteína (huevo/claras) + carbos (avena/tortillas) + verdura + 1 fruta + aguacate",
        "Comida: proteína (pollo/res magra/pescado) + carbos (arroz/pasta/papas/tortillas) + verdura + aguacate",
        "Cena: proteína (tilapia/atún/pollo) + carbos bajos (tostadas/verduras) + ensalada con aguacate"
    ]
    for i in range(meals_per_day):
        meals.append(base_meals[i % len(base_meals)])

    return {
        "calories": round(calories),
        "protein_g": protein_g_total,
        "fats_g": fats_g_total,
        "carbs_g": carbs_g_total,
        "meals": meals
    }
