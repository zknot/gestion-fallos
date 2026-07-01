import streamlit as st
import pandas as pd
import sqlite3
import os

# Configuración
DB_PATH = 'fallos.db'

def conectar_db():
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fallos (
            Num_factura TEXT, Fecha TEXT, Cliente TEXT, 
            Faltante TEXT, Devolucion TEXT, Cantidad INTEGER, 
            Motivo TEXT, Mes_Origen TEXT, Motivo_Estandarizado TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar
inicializar_db()

st.set_page_config(layout="wide", page_title="Gestión de Fallos")
st.title("📊 Gestor de Registro de Fallos")

# --- CARGA MULTIPLE ---
st.subheader("➕ Agregar nuevos registros")
col_a, col_b = st.columns(2)
with col_a:
    num_factura = st.text_input("Num factura")
    cliente_nombre = st.text_input("Nombre Cliente")
with col_b:
    fecha = st.date_input("Fecha")
    motivo_estandarizado = st.selectbox("Motivo Estandarizado", [
        "Comercial / Cliente", "Producto Dañado / Defectuoso", 
        "Error Logístico / Operativo", "Producción / Depósito", "Error de Empaque / Producto"
    ], index=None)

if 'df_editor' not in st.session_state:
    st.session_state.df_editor = pd.DataFrame(columns=['Cantidad', 'Faltante (SKU)', 'Devolución (SKU)', 'Motivo detallado'])

st.write("Detalle de productos:")
st.session_state.df_editor = st.data_editor(st.session_state.df_editor, num_rows="dynamic", use_container_width=True)

if st.button("Guardar todos los registros"):
    if not num_factura or not cliente_nombre or not motivo_estandarizado:
        st.error("Completa Num factura, Cliente y Motivo Estandarizado.")
    else:
        filas_nuevas = []
        for _, row in st.session_state.df_editor.dropna(how='all').iterrows():
            filas_nuevas.append({
                'Num_factura': num_factura,
                'Fecha': fecha.strftime('%Y-%m-%d'),
                'Cliente': cliente_nombre,
                'Cantidad': row['Cantidad'],
                'Faltante': str(row['Faltante (SKU)']),
                'Devolucion': str(row['Devolución (SKU)']),
                'Motivo': row['Motivo detallado'],
                'Mes_Origen': fecha.strftime('%m26'),
                'Motivo_Estandarizado': motivo_estandarizado
            })
        
        conn = conectar_db()
        pd.DataFrame(filas_nuevas).to_sql('fallos', conn, if_exists='append', index=False)
        conn.close()
        st.success("¡Registros guardados exitosamente!")
        st.session_state.df_editor = pd.DataFrame(columns=['Cantidad', 'Faltante (SKU)', 'Devolución (SKU)', 'Motivo detallado'])
        st.rerun()

# --- VISUALIZACIÓN ---
st.divider()
st.subheader("Registros existentes")
conn = conectar_db()
df_total = pd.read_sql_query("SELECT * FROM fallos", conn)
conn.close()
st.dataframe(df_total, use_container_width=True)