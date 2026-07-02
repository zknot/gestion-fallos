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
    # Solo crea la tabla si realmente no existe, nunca sobrescribe
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

try:
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fallos")
    count = cursor.fetchone()[0]
    st.info(f"Conexión exitosa. Registros en base de datos: {count}")
    conn.close()
except Exception as e:
    st.error(f"Error de conexión a la base de datos: {e}")

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

# Modifica la parte donde guardas los datos
if st.button("Guardar todos los registros"):
    # ... (tu validación inicial)
    
    filas_nuevas = []
    for _, row in st.session_state.df_editor.dropna(how='all').iterrows():
        filas_nuevas.append({
            'Num factura': num_factura,  # EXACTAMENTE como en el Excel
            'Fecha': fecha.strftime('%Y-%m-%d'),
            'Cliente': cliente_nombre,
            'Faltante': str(row['Faltante (SKU)']),
            'Devolucion': str(row['Devolución (SKU)']),
            'Cantidad': row['Cantidad'],
            'Motivo': row['Motivo detallado'],
            'Mes_Origen': fecha.strftime('%m26'),
            'Motivo Estandarizado': motivo_estandarizado
        })
    
    df_nuevos = pd.DataFrame(filas_nuevas)
    
    # FORZAR la conexión y la inserción
    conn = conectar_db()
    # Esto asegura que si falta alguna columna, no falle silenciosamente
    df_nuevos.to_sql('fallos', conn, if_exists='append', index=False)
    conn.close()
    
    st.success("¡Registros guardados!")
    st.rerun()

# --- VISUALIZACIÓN ---
# --- VISUALIZACIÓN A PRUEBA DE ERRORES ---
st.divider()
st.subheader("Registros existentes")

try:
    conn = conectar_db()
    # Listar tablas para confirmar el nombre
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    
    if not tablas:
        st.warning("La base de datos está vacía. ¡Aún no hay tablas!")
    else:
        # Intentar leer la tabla (usamos la primera que encuentre)
        nombre_tabla = tablas[0][0]
        st.write(f"Leyendo desde la tabla: **{nombre_tabla}**")
        df_total = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conn)
        
        if df_total.empty:
            st.info("La tabla existe pero no tiene registros.")
        else:
            st.dataframe(df_total, use_container_width=True)
            
    conn.close()
except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")
