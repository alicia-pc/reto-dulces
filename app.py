import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Reto: 1 Dulce al Mes",
    page_icon="🍩",
    layout="centered"
)

# --- TÍTULO Y ESTILOS ---
st.title("🍩 Reto Anual: 1 Dulce al Mes")
st.markdown("---")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Creamos la conexión usando el objeto connection de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos (con cache para no saturar, pero TTL bajo para ver cambios)
def load_data():
    # Lee la hoja completa. Usamos usecols para asegurar orden
    return conn.read(worksheet="Hoja 1", usecols=[0, 1, 2], ttl=0)

# Intentamos cargar los datos
try:
    df = load_data()
except Exception as e:
    st.error("⚠️ Error conectando a Google Sheets. Revisa tus 'Secrets'.")
    st.stop()

# --- LÓGICA DE ESTADOS ---
# Diccionario para mapear texto a Emoji
STATE_MAP = {
    "pending": "⏳",
    "done": "🍩",
    "failed": "❌"
}

# Diccionario para definir el siguiente estado (Ciclo)
NEXT_STATE = {
    "pending": "done",
    "done": "failed",
    "failed": "pending"
}

# --- FUNCIÓN DE ACTUALIZACIÓN ---
def update_status(month_index, user_column):
    """
    1. Lee el estado actual del dataframe.
    2. Calcula el nuevo estado.
    3. Actualiza el Dataframe local.
    4. Sube el cambio a Google Sheets.
    """
    current_val = df.at[month_index, user_column]
    
    # Si la celda está vacía o tiene un valor raro, asumimos pending
    if current_val not in NEXT_STATE:
        current_val = "pending"
        
    new_val = NEXT_STATE[current_val]
    
    # Actualizamos el dataframe localmente
    df.at[month_index, user_column] = new_val
    
    # Actualizamos la hoja de cálculo
    conn.update(worksheet="Hoja 1", data=df)
    st.toast(f"Estado actualizado a: {STATE_MAP[new_val]}")

# --- CÁLCULO DE PROGRESO ---
def calculate_score(user_col):
    # Cuenta cuántas veces aparece "done"
    score = df[user_col].value_counts().get("done", 0)
    return score

score_a = calculate_score("UsuarioA")
score_b = calculate_score("UsuarioB")
total_months = 12

# --- INTERFAZ GRÁFICA ---

# Métricas Globales
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric("Usuario A (Puntos)", f"{score_a}/{total_months}")
    st.progress(score_a / total_months)
with col_m2:
    st.metric("Usuario B (Puntos)", f"{score_b}/{total_months}")
    st.progress(score_b / total_months)

st.markdown("### 📅 Calendario de Seguimiento")
st.markdown("Pulsa en el icono para cambiar tu estado.")

# Cabeceras de columnas
h1, h2, h3 = st.columns([1, 2, 2])
h1.markdown("**Mes**")
h2.markdown("**Usuario A**")
h3.markdown("**Usuario B**")

# Iteramos por cada mes (fila del dataframe)
for index, row in df.iterrows():
    month = row['Mes']
    state_a = row['UsuarioA']
    state_b = row['UsuarioB']
    
    # Validar que el estado existe, si no, poner pending visualmente
    icon_a = STATE_MAP.get(state_a, "⏳")
    icon_b = STATE_MAP.get(state_b, "⏳")

    c1, c2, c3 = st.columns([1, 2, 2])
    
    # Columna Mes
    with c1:
        st.markdown(f"**{month}**") # Texto verticalmente centrado
    
    # Botón Usuario A
    with c2:
        # Usamos key único combinando usuario y mes
        st.button(
            icon_a, 
            key=f"btn_a_{index}", 
            on_click=update_status, 
            args=(index, "UsuarioA"),
            use_container_width=True
        )

    # Botón Usuario B
    with c3:
        st.button(
            icon_b, 
            key=f"btn_b_{index}", 
            on_click=update_status, 
            args=(index, "UsuarioB"),
            use_container_width=True
        )

st.markdown("---")
st.caption("Hecho con 🐍 Python y Streamlit")
