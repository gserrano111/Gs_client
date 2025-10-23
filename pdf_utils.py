
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from db import get_client_by_id, list_meal_plans, list_training_plans
import os

def build_client_pdf(client_id: int, include_meal=True, include_train=True) -> str:
    client = get_client_by_id(client_id)
    name = client["name"]
    today = datetime.now().strftime("%Y-%m-%d")

    filename = f"FichaCliente_{client_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    normal = styles["Normal"]

    elements = []
    # Header
    elements.append(Paragraph(f"Ficha de cliente — {name}", title_style))
    elements.append(Paragraph(f"Fecha: {today}", normal))
    elements.append(Spacer(1, 12))

    # Client data box (Carlos Estrada style: cuadros grises)
    data = [
        ["Sexo", client["sex"] or "-", "Edad", client["age"] or "-"],
        ["Estatura (cm)", client["height_cm"] or "-", "Peso (kg)", client["weight_kg"] or "-"],
        ["% Grasa", client["body_fat_pct"] or "-", "% Músculo", client["muscle_pct"] or "-"],
        ["Grasa visceral", client["visceral_fat"] or "-", "Ingestas/día", client["meals_per_day"] or "-"],
        ["Alergias", client["allergies"] or "-", "Ocupación", client["occupation"] or "-"],
    ]
    tbl = Table(data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.whitesmoke),
        ("BOX", (0,0), (-1,-1), 1, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.whitesmoke, colors.lightgrey])
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # Meal plan (last)
    if include_meal:
        mdf = list_meal_plans(client_id)
        if not mdf.empty:
            last = mdf.iloc[0]
            elements.append(Paragraph("Plan de alimentación (último)", styles["Heading2"]))
            macros = [
                ["Calorías", last["calories"], "Proteína (g)", last["protein_g"]],
                ["Grasas (g)", last["fats_g"], "Carbohidratos (g)", last["carbs_g"]],
            ]
            tmac = Table(macros, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
            tmac.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.whitesmoke),
                ("BOX", (0,0), (-1,-1), 1, colors.grey),
                ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0,0), (-1,-1), 9),
            ]))
            elements.append(tmac)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Comidas sugeridas (Preset GS):", styles["Heading3"]))
            # Meals_json is not included here for simplicity; we show note
            elements.append(Paragraph("• Desayuno / Comida / Cena — ver panel para detalle por ingredientes.", normal))
            elements.append(Spacer(1, 12))

    # Training plan (last)
    if include_train:
        tdf = list_training_plans(client_id)
        if not tdf.empty:
            lastt = tdf.iloc[0]
            elements.append(Paragraph("Plan de entrenamiento (último)", styles["Heading2"]))
            ttbl = Table([
                ["Objetivo", lastt["goal"]],
                ["Split", lastt["split"]],
                ["Días/semana", lastt["days_per_week"]],
                ["Duración sesión (min)", lastt["session_duration_min"]],
            ], colWidths=[6*cm, 10*cm])
            ttbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.whitesmoke),
                ("BOX", (0,0), (-1,-1), 1, colors.grey),
                ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0,0), (-1,-1), 9),
            ]))
            elements.append(ttbl)

    doc.build(elements)
    return os.path.abspath(filename)
