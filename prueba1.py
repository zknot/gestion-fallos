import pandas as pd
import sqlite3

def crear_base_limpia(archivo_excel):
    # Leer forzando TODO como texto para preservar ceros y puntos
    df = pd.read_excel(archivo_excel, dtype=str)
    
    # Asegurarnos de que no haya nulos molestos
    df = df.fillna("")
    
    # Crear ID único para la gestión en Streamlit
    df.insert(0, 'id', range(1, len(df) + 1))
    
    # Guardar en SQLite
    conn = sqlite3.connect('fallos.db')
    df.to_sql('fallos', conn, if_exists='replace', index=False)
    conn.close()
    print("Base de datos creada exitosamente con los datos del Excel.")

crear_base_limpia('Base_Maestra_Fallos.xlsx')