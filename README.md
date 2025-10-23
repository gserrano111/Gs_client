
# GS — Registro de Clientes (Streamlit)

Panel web para llevar **clientes, mediciones, planes de alimentación y entrenamiento** con:
- Cálculo **Mifflin‑St Jeor** y generación de menú con **Preset GS**.
- Exportación a **PDF** estilo "Carlos Estrada" (cuadros grises, título centrado).

## Despliegue en Streamlit Community Cloud
1. Crea un repositorio en GitHub y sube estos archivos.
2. Entra a https://share.streamlit.io/ e inicia un nuevo deploy apuntando a `app.py`.
3. Listo: tendrás una URL pública para usar desde tu Galaxy Tab.

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

> La base se guarda como `client_app.db` en el directorio de la app.
