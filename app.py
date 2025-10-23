
import streamlit as st
import pandas as pd
from datetime import datetime
from db import init_db, list_clients, create_client, update_client, delete_client, \
               add_measurement, get_measurements, add_meal_plan, list_meal_plans, \
               add_training_plan, list_training_plans, get_client_by_id
from gs_preset import mifflin_st_jeor, build_gs_meal_plan
from pdf_utils import build_client_pdf

st.set_page_config(page_title="GS — Registro de clientes", page_icon="💪", layout="wide")

# Initialize DB
init_db()

# Sidebar
st.sidebar.title("GS — Panel")
page = st.sidebar.radio("Navegación", ["Clientes", "Mediciones", "Planes", "Exportar PDF", "Ayuda"])
st.sidebar.caption("Hecho para Galaxy Tab • Streamlit")

def _id_selectbox(df, key):
    if df.empty:
        st.info("No hay clientes todavía.")
        return None
    return st.selectbox("Selecciona cliente por ID", df["id"].tolist(), key=key)

# ---- Clientes ----
if page == "Clientes":
    st.header("👤 Clientes")
    with st.expander("➕ Registrar nuevo cliente", expanded=True):
        with st.form("form_new_client"):
            c1, c2, c3, c4 = st.columns([2,1,1,1])
            name = c1.text_input("Nombre completo *")
            sex = c2.selectbox("Sexo", ["F","M","Otro"], index=1)
            age = c3.number_input("Edad", min_value=1, max_value=120, value=30)
            height_cm = c4.number_input("Estatura (cm)", min_value=80.0, max_value=230.0, value=170.0)

            c5, c6, c7 = st.columns(3)
            weight_kg = c5.number_input("Peso (kg)", min_value=10.0, max_value=400.0, value=70.0)
            body_fat_pct = c6.number_input("% Grasa", min_value=0.0, max_value=80.0, value=20.0)
            muscle_pct = c7.number_input("% Músculo", min_value=0.0, max_value=80.0, value=35.0)

            c8, c9, c10 = st.columns(3)
            visceral_fat = c8.number_input("Grasa visceral", min_value=0, max_value=30, value=5)
            meals_per_day = c9.number_input("Ingestas/día", min_value=1, max_value=8, value=3)
            economic_level = c10.selectbox("Nivel económico", ["Bajo","Medio","Alto"], index=1)

            skinfolds = st.text_input("Pliegues cutáneos (formato libre)")
            preferred_foods = st.text_input("Alimentos preferidos (coma-separado)")
            allergies = st.text_input("Alergias")
            occupation = st.text_input("Ocupación")
            notes = st.text_area("Notas")

            submitted = st.form_submit_button("Guardar cliente")
            if submitted:
                if not name:
                    st.warning("El nombre es obligatorio.")
                else:
                    new_id = create_client(
                        name=name, sex=sex, age=int(age), height_cm=float(height_cm),
                        weight_kg=float(weight_kg), skinfolds=skinfolds, body_fat_pct=float(body_fat_pct),
                        muscle_pct=float(muscle_pct), visceral_fat=int(visceral_fat), preferred_foods=preferred_foods,
                        meals_per_day=int(meals_per_day), allergies=allergies, economic_level=economic_level,
                        occupation=occupation, notes=notes, created_at=datetime.now().isoformat()
                    )
                    st.success(f"Cliente creado (ID {new_id}).")

    st.divider()
    st.write("🔎 Buscar")
    q = st.text_input("Nombre / ocupación / notas")
    df = list_clients(search=q.strip() or None)
    st.caption(f"{len(df)} cliente(s)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("✏️ Editar / 🗑️ Eliminar")
    if len(df):
        cid = _id_selectbox(df, key="cid_edit")
        if cid:
            row = df[df.id == cid].iloc[0]
            with st.form("edit_client"):
                ec1, ec2, ec3, ec4 = st.columns([2,1,1,1])
                name = ec1.text_input("Nombre", row["name"])
                sex = ec2.selectbox("Sexo", ["F","M","Otro"], index=["F","M","Otro"].index(row["sex"]) if row["sex"] in ["F","M","Otro"] else 1)
                age = ec3.number_input("Edad", 1, 120, int(row["age"]) if row["age"] else 30)
                height_cm = ec4.number_input("Estatura (cm)", 80.0, 230.0, float(row["height_cm"]) if row["height_cm"] else 170.0)

                ec5, ec6, ec7 = st.columns(3)
                weight_kg = ec5.number_input("Peso (kg)", 10.0, 400.0, float(row["weight_kg"]) if row["weight_kg"] else 70.0)
                body_fat_pct = ec6.number_input("% Grasa", 0.0, 80.0, float(row["body_fat_pct"]) if row["body_fat_pct"] else 20.0)
                muscle_pct = ec7.number_input("% Músculo", 0.0, 80.0, float(row["muscle_pct"]) if row["muscle_pct"] else 35.0)

                ec8, ec9, ec10 = st.columns(3)
                visceral_fat = ec8.number_input("Grasa visceral", 0, 30, int(row["visceral_fat"]) if row["visceral_fat"] else 5)
                meals_per_day = ec9.number_input("Ingestas/día", 1, 8, int(row["meals_per_day"]) if row["meals_per_day"] else 3)
                economic_level = ec10.selectbox("Nivel económico", ["Bajo","Medio","Alto"], index=["Bajo","Medio","Alto"].index(row["economic_level"]) if row["economic_level"] in ["Bajo","Medio","Alto"] else 1)

                skinfolds = st.text_input("Pliegues cutáneos", value=row["skinfolds"] or "")
                preferred_foods = st.text_input("Alimentos preferidos", value=row["preferred_foods"] or "")
                allergies = st.text_input("Alergias", value=row["allergies"] or "")
                occupation = st.text_input("Ocupación", value=row["occupation"] or "")
                notes = st.text_area("Notas", value=row["notes"] or "")

                colA, colB = st.columns(2)
                save = colA.form_submit_button("Guardar cambios")
                remove = colB.form_submit_button("Eliminar cliente", type="primary")
                if save:
                    update_client(int(cid),
                        name=name, sex=sex, age=int(age), height_cm=float(height_cm),
                        weight_kg=float(weight_kg), skinfolds=skinfolds, body_fat_pct=float(body_fat_pct),
                        muscle_pct=float(muscle_pct), visceral_fat=int(visceral_fat), preferred_foods=preferred_foods,
                        meals_per_day=int(meals_per_day), allergies=allergies, economic_level=economic_level,
                        occupation=occupation, notes=notes
                    )
                    st.success("Guardado.")
                if remove:
                    delete_client(int(cid))
                    st.success("Eliminado. Actualiza la lista con la búsqueda.")

# ---- Mediciones ----
elif page == "Mediciones":
    st.header("📏 Mediciones")
    clients = list_clients()
    cid = _id_selectbox(clients, key="cid_meas")
    if cid:
        st.subheader(f"Cliente ID {cid}")
        with st.form("form_meas"):
            date = st.date_input("Fecha", value=datetime.today())
            c1, c2, c3 = st.columns(3)
            weight_kg = c1.number_input("Peso (kg)", 10.0, 400.0, 70.0)
            body_fat_pct = c2.number_input("% Grasa", 0.0, 80.0, 20.0)
            muscle_pct = c3.number_input("% Músculo", 0.0, 80.0, 35.0)
            c4, c5, c6 = st.columns(3)
            visceral_fat = c4.number_input("Grasa visceral", 0, 30, 5)
            waist_cm = c5.number_input("Cintura (cm)", 20.0, 200.0, 80.0)
            hip_cm = c6.number_input("Cadera (cm)", 20.0, 200.0, 95.0)
            c7, c8, c9 = st.columns(3)
            chest_cm = c7.number_input("Pecho (cm)", 20.0, 200.0, 95.0)
            thigh_cm = c8.number_input("Muslo (cm)", 20.0, 200.0, 55.0)
            arm_cm = c9.number_input("Brazo (cm)", 10.0, 80.0, 32.0)
            notes = st.text_area("Notas")
            submit = st.form_submit_button("Guardar medición")
            if submit:
                add_measurement(
                    client_id=int(cid), date=date.isoformat(), weight_kg=float(weight_kg),
                    body_fat_pct=float(body_fat_pct), muscle_pct=float(muscle_pct), visceral_fat=int(visceral_fat),
                    waist_cm=float(waist_cm), hip_cm=float(hip_cm), chest_cm=float(chest_cm),
                    thigh_cm=float(thigh_cm), arm_cm=float(arm_cm), notes=notes
                )
                st.success("Medición guardada.")
        st.divider()
        dfm = get_measurements(int(cid))
        st.subheader("Histórico")
        st.dataframe(dfm, use_container_width=True, hide_index=True)

# ---- Planes ----
elif page == "Planes":
    st.header("🥗🏋️ Planes")
    clients = list_clients()
    cid = _id_selectbox(clients, key="cid_plans")
    if cid:
        row = get_client_by_id(int(cid))
        st.subheader(f"Cliente: {row['name']}")
        st.caption("Macros con Mifflin-St Jeor + Preset GS (opcional)")

        with st.form("form_macros"):
            c1, c2, c3, c4 = st.columns(4)
            weight = c1.number_input("Peso (kg)", 10.0, 400.0, float(row["weight_kg"]) if row["weight_kg"] else 70.0)
            height = c2.number_input("Estatura (cm)", 80.0, 230.0, float(row["height_cm"]) if row["height_cm"] else 170.0)
            age = c3.number_input("Edad", 1, 120, int(row["age"]) if row["age"] else 30)
            sex = c4.selectbox("Sexo", ["M","F"], index=0 if row["sex"]=="M" else 1)

            c5, c6 = st.columns(2)
            activity = c5.selectbox("Actividad", ["sedentario","ligero","moderado","alto","atleta"], index=2)
            objective = c6.selectbox("Objetivo", ["recomposición","pérdida de grasa","mantenimiento","ganancia de masa"], index=0)

            generate = st.form_submit_button("Calcular macros + Generar menú GS")
            if generate:
                tmb, tdee = mifflin_st_jeor(weight, height, int(age), sex, activity)
                plan = build_gs_meal_plan(tdee, objective, meals_per_day=int(row["meals_per_day"] or 3))
                add_meal_plan(client_id=int(cid), date=datetime.now().date().isoformat(),
                              calories=int(plan["calories"]), protein_g=plan["protein_g"], fats_g=plan["fats_g"],
                              carbs_g=plan["carbs_g"], meals_json=pd.Series(plan["meals"]).to_json(orient="values"),
                              notes=f"Objetivo: {objective}. Preset GS.")
                st.success(f"Plan guardado. TMB: {int(tmb)} kcal • TDEE: {int(tdee)} kcal")

        st.divider()
        st.subheader("Planes de alimentación")
        mp = list_meal_plans(int(cid))
        st.dataframe(mp, use_container_width=True, hide_index=True)

        st.subheader("Plan de entrenamiento")
        with st.form("form_train"):
            goal = st.text_input("Objetivo", "Recomposición / Hipertrofia")
            split = st.text_input("Split", "5 días (3 hombro, 2 pierna)")
            days_per_week = st.number_input("Días por semana", 1, 7, 5)
            session_duration_min = st.number_input("Duración sesión (min)", 30, 180, 90)
            cardio_plan = st.text_area("Cardio", "LISS post-entreno 15–25 min, 3–4x/sem")
            routine_text = st.text_area("Rutina (texto libre)", "Día 1 Hombro anterior ...")
            notes = st.text_area("Notas", "")
            save_train = st.form_submit_button("Guardar entrenamiento")
            if save_train:
                add_training_plan(client_id=int(cid), date=datetime.now().date().isoformat(),
                                  goal=goal, split=split, days_per_week=int(days_per_week),
                                  session_duration_min=int(session_duration_min), cardio_plan=cardio_plan,
                                  routine_text=routine_text, notes=notes)
                st.success("Entrenamiento guardado.")
        st.subheader("Histórico de entrenamientos")
        tp = list_training_plans(int(cid))
        st.dataframe(tp, use_container_width=True, hide_index=True)

# ---- Exportar PDF ----
elif page == "Exportar PDF":
    st.header("🧾 Exportar PDF (formato Carlos Estrada)")
    clients = list_clients()
    cid = _id_selectbox(clients, key="cid_pdf")
    if cid:
        include_meal = st.checkbox("Incluir plan de alimentación (último)", value=True)
        include_train = st.checkbox("Incluir plan de entrenamiento (último)", value=True)
        if st.button("Generar PDF"):
            pdf_path = build_client_pdf(int(cid), include_meal=include_meal, include_train=include_train)
            with open(pdf_path, "rb") as f:
                st.download_button("Descargar PDF", f, file_name=f"FichaCliente_{cid}.pdf", mime="application/pdf")
            st.success("PDF generado.")

# ---- Ayuda ----
else:
    st.header("🛟 Ayuda rápida")
    st.markdown("""
**Flujo sugerido**  
1) Registra al cliente.  
2) Carga mediciones iniciales.  
3) En «Planes», calcula TMB/TDEE (Mifflin‑St Jeor) y genera menú con **Preset GS**.  
4) Guarda rutina en «Planes».  
5) Exporta PDF con el formato estilo *Carlos Estrada* (título centrado, fecha izquierda, cuadros grises).

**Despliegue en la nube (Streamlit Community Cloud)**  
- Sube estos archivos a un repositorio de GitHub.  
- Ve a [share.streamlit.io](https://share.streamlit.io/), conecta el repo y elige **app.py** como entrypoint.  
- Listo: tendrás una URL pública para usar en tu Galaxy Tab.
    """)
