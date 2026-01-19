import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- ⚙️ ZONA DE CONFIGURACIÓN (EDITA ESTO) ---
# Escribe aquí los nombres EXACTOS que has puesto en la Google Sheet
USER_A = "Pequeña👩🏻"     # Cambia "Ana" por el nombre real de la columna A
USER_B = "Pequeño👨🏻"  # Cambia "Carlos" por el nombre real de la columna B
SHEET_URL = "Hoja 1" # Nombre de la pestaña de la hoja (suele ser "Hoja 1")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reto: 1 Dulce al Mes", page_icon="🍩", layout="centered")

# --- TÍTULO ---
st.title(f"🍩 Reto: 1 Dulce al Mes")
st.markdown("---")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Leemos las columnas por nombre para evitar errores
    return conn.read(worksheet=SHEET_URL, usecols=[0, 1, 2], ttl=0)

try:
    df = load_data()
    # Verificamos que las columnas existen
    if USER_A not in df.columns or USER_B not in df.columns:
        st.error(f"⚠️ Error: No encuentro las columnas '{USER_A}' o '{USER_B}' en la hoja. Revisa que coincidan exactamente.")
        st.stop()
except Exception as e:
    st.error("⚠️ Error conectando a Google Sheets.")
    st.stop()

# --- LÓGICA ---
STATE_MAP = {"pending": "⏳", "done": "🍩", "failed": "❌"}
NEXT_STATE = {"pending": "done", "done": "failed", "failed": "pending"}

def update_status(month_index, user_column):
    current_val = df.at[month_index, user_column]
    if current_val not in NEXT_STATE: current_val = "pending"
    new_val = NEXT_STATE[current_val]
    df.at[month_index, user_column] = new_val
    conn.update(worksheet=SHEET_URL, data=df)
    st.toast(f"¡{user_column} actualizado!")

def calculate_score(user_col):
    return df[user_col].value_counts().get("done", 0)

score_a = calculate_score(USER_A)
score_b = calculate_score(USER_B)

# --- INTERFAZ ---
col1, col2 = st.columns(2)
with col1:
    st.metric(f"{USER_A}", f"{score_a}/12")
    st.progress(score_a / 12)
with col2:
    st.metric(f"{USER_B}", f"{score_b}/12")
    st.progress(score_b / 12)

st.markdown("### 📅 Calendario")

# Encabezados
h1, h2, h3 = st.columns([1, 2, 2])
h1.markdown("**Mes**")
h2.markdown(f"**{USER_A}**")
h3.markdown(f"**{USER_B}**")

for index, row in df.iterrows():
    month = row['Mes']
    # Botones dinámicos usando las variables
    with h1: st.write("") # Espaciador si hace falta, o dejar el loop anterior
    
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: st.markdown(f"**{month}**")
    
    with c2:
        st.button(STATE_MAP.get(row[USER_A], "⏳"), key=f"a_{index}", on_click=update_status, args=(index, USER_A), use_container_width=True)
    with c3:
        st.button(STATE_MAP.get(row[USER_B], "⏳"), key=f"b_{index}", on_click=update_status, args=(index, USER_B), use_container_width=True)

st.markdown("---")
st.caption("Hecho con ❤️ y Python")
