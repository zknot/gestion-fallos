import sqlite3
import pandas as pd

conn = sqlite3.connect('fallos.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(fallos)")
columnas = cursor.fetchall()
for col in columnas:
    print(col[1]) # Esto imprimirá los nombres reales de tus columnas
conn.close()