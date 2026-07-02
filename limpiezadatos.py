import pandas as pd
import re

# Cargar el archivo
df = pd.read_csv("Base_Maestra_Fallos.xlsx - Sheet1.csv")

# Función para separar el nombre del ID (buscando el último número al final del string)
def separar_cliente(texto):
    # Busca números al final del string
    match = re.search(r'(\D+)\s(\d+)$', str(texto))
    if match:
        nombre = match.group(1).strip()
        id_cliente = match.group(2)
        return nombre, id_cliente
    return texto, None

# Aplicar la separación
df[['Cliente_Nombre', 'ID_Cliente_Extraido']] = df['Cliente'].apply(
    lambda x: pd.Series(separar_cliente(x))
)

# Guardar el archivo limpio
df.to_excel("Base_Maestra_Limpia.xlsx", index=False)
print("Archivo 'Base_Maestra_Limpia.xlsx' creado exitosamente.")