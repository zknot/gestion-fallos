import pandas as pd
import sqlite3

# 1. Cargamos el archivo que SÍ tiene los datos
df = pd.read_excel('Base_Maestra_Fallos.xlsx')

# 2. Conectamos a la base de datos
conn = sqlite3.connect('fallos.db')

# 3. Exportamos con los nombres EXACTOS que tiene el Excel
df.to_sql('fallos', conn, if_exists='replace', index=False)

# 4. Verificamos
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM fallos")
print(f"Registros insertados correctamente: {cursor.fetchone()[0]}")
conn.close()