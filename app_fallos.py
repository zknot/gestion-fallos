import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

# 1. Configuración
st.set_page_config(page_title="Gestión de Fallos", layout="wide")

# 2. Funciones de Base de Datos y Procesamiento
with st.form("form_fallos", clear_on_submit=True):
    st.subheader("➕ Agregar nuevos registros")
    col_a, col_b = st.columns(2)
    
    with col_a:
        fecha = st.date_input("Fecha", datetime.now())
             
        # Selector de cliente
        df_clientes = pd.read_excel('clientes_interior.xlsx', dtype=str)
        df_clientes['Etiqueta'] = df_clientes['ID'].astype(str) + " - " + df_clientes['Nombre'].astype(str)
        cliente_seleccionado = st.selectbox("Seleccione Cliente", options=df_clientes['Etiqueta'].tolist(), index=None)
                       
        num_factura = st.text_input("Num factura")
        
        motivo_detallado = st.text_input("Motivo detallado")
        
        
        
    with col_b:
        
        faltante_sku = st.text_input("Faltante (SKU)")
        
        devolucion_sku = st.text_input("Devolución (SKU)")
        
        # NUEVO: Campo Cantidad
        cantidad = st.number_input(
        "Cantidad", 
        min_value=1, 
        value=None, 
        step=1, 
        placeholder="Ingrese cantidad..."
        )
        
        motivo_estandarizado = st.selectbox("Motivo Estandarizado", [
            "Comercial / Cliente", "Producto Dañado / Defectuoso", 
            "Error Logístico / Operativo", "Producción / Depósito", "Error de Empaque / Producto"
        ])
        
        

    submit = st.form_submit_button("Guardar registro")

    if submit:
        # Validación de obligatoriedad
        if not num_factura or not cliente_seleccionado:
            st.error("⚠️ La Factura y el Cliente son obligatorios.")
        elif not faltante_sku and not devolucion_sku:
            st.error("⚠️ Debe completar al menos uno: 'Faltante (SKU)' o 'Devolución (SKU)'.")
        elif cantidad is None or cantidad <= 0:
            st.error("⚠️ La cantidad es obligatoria y debe ser mayor a 0.")
        else:
            # Procesamiento
            id_c, nombre_c = cliente_seleccionado.split(" - ", 1)
            
            conn = sqlite3.connect('fallos.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO fallos 
                              ("Num factura", "ID Cliente", "Cliente", "Fecha", 
                               "Motivo Estandarizado", "Faltante", "Devolucion", "Cantidad") 
                              VALUES (?,?,?,?,?,?,?,?)''', 
                           (num_factura, id_c, nombre_c, fecha, motivo_estandarizado, 
                            faltante_sku, devolucion_sku, cantidad))
            conn.commit()
            conn.close()
            
            st.success("¡Registro guardado exitosamente!")
            st.rerun()



@st.cache_data
def obtener_datos():
    conn = sqlite3.connect('fallos.db')
    df_fallos = pd.read_sql_query("SELECT * FROM fallos", conn)
    conn.close()
    
    df_clientes = pd.read_excel('clientes_interior.xlsx', dtype=str)
    
    # --- PASO DE LIMPIEZA CLAVE ---
    # 1. Convertimos a string, quitamos espacios en blanco, y eliminamos cualquier carácter no numérico
    df_fallos['ID Cliente'] = df_fallos['ID Cliente'].astype(str).str.strip()
    df_clientes['ID'] = df_clientes['ID'].astype(str).str.strip()
    
    # 2. Realizamos el merge
    df_vista = pd.merge(
        df_fallos, 
        df_clientes, 
        left_on='ID Cliente', 
        right_on='ID', 
        how='left'
    )
    # 4. Aseguramos que las columnas existan, si no, las creamos vacías
    columnas_necesarias = [
        'id', 'Num factura', 'Fecha', 'ID Cliente', 'Faltante', 
        'Devolucion', 'Cantidad', 'Motivo', 'Motivo Estandarizado', 'Nombre'
    ]
    
    for col in columnas_necesarias:
        if col not in df_vista.columns:
            df_vista[col] = ""
            
    return df_vista.fillna("")

def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Registros')
    return output.getvalue()

# 3. Interfaz Principal
st.title("📦 Sistema de Gestión de Fallos")

# --- Lógica de visualización ---
df_vista = obtener_datos()

columnas_a_mostrar = [
    "ID Cliente",
    "Nombre", 
    "Num factura", 
    "Fecha", 
    "Faltante", 
    "Devolucion",
    "Cantidad", 
    "Motivo Estandarizado", 
    "Motivo", 
    "Borrar"
]

# Definimos el orden de columnas y nombres amigables
orden_columnas = ["Nombre", "factura", "fecha", "cantidad", "faltante_sku", "devolucion_sku", "motivo_detallado", "motivo_estandarizado", "Borrar"]
# Filtramos solo las que existen
columnas_finales = [col for col in columnas_a_mostrar if col in df_vista.columns]
df_final = df_vista[columnas_finales]

st.subheader("📋 Registros Cargados")

# Editor de datos
editado = st.data_editor(
    df_final,
    column_config={
        "Nombre": st.column_config.TextColumn("Cliente", disabled=True),
        "Num factura": st.column_config.TextColumn("Factura"),
        "Borrar": st.column_config.CheckboxColumn("Borrar fila")
    },
    hide_index=True,
    use_container_width=True
)

# 4. Lógica de eliminación
if st.button("Confirmar eliminación de seleccionados"):
    ids_a_borrar = df_vista[editado['Borrar'] == True]['id'].tolist()
    if ids_a_borrar:
        conn = sqlite3.connect('fallos.db')
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM fallos WHERE id IN ({','.join(map(str, ids_a_borrar))})")
        conn.commit()
        conn.close()
        st.success("Registros eliminados.")
        st.rerun()
    else:
        st.warning("No se seleccionó ningún registro.")

# 5. Descarga
st.download_button(
    label="📥 Descargar registros en Excel",
    data=convertir_a_excel(df_vista.drop(columns=['Borrar'], errors='ignore')),
    file_name='registros_fallos.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)