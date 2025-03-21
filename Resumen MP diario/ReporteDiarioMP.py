import MySQLdb
from datetime import datetime, timedelta
import pandas as pd
import os

db = MySQLdb.connect(host="192.168.0.12",    # tu host, usualmente localhost
                     user="operario",         # tu usuario
                     passwd="",  # tu password
                     db="dbp8100")        # el nombre de la base de datos
cur = db.cursor()


fecha_actual = datetime.now()
fecha_actual = fecha_actual.strftime("%Y-%m-%d")

fecha_ayer = datetime.now()
fecha_ayer = fecha_ayer.strftime('%Y-%m-%d')


cur.execute("""
    SELECT 
        productox.Codigo AS Codigo, 
        productox.Nombre AS Producto, 
        SUM(dcaptura.Valor) AS Dosificado 
    FROM 
        dbp8100.dcaptura AS dcaptura
    JOIN 
        dbp8100.tareaseje AS tareaseje ON dcaptura.IDT = tareaseje.NroID
    JOIN 
        dbp8100.productox AS productox ON productox.NroID = dcaptura.IDP 
    WHERE 
        tareaseje.Fecha >= %s AND 
        tareaseje.Fecha <= %s 
    GROUP BY 
        productox.Nombre
""", (fecha_ayer, fecha_actual))

# Obtener los resultados
resultados = cur.fetchall()

# Obtener los nombres de las columnas
columnas = [desc[0] for desc in cur.description]

# Crear un DataFrame de pandas
df = pd.DataFrame(resultados, columns=columnas)

# Cerrar el cursor y la conexión
cur.close()
db.close()

# Cargar códigos de productos
df_cod = pd.read_excel('codigos.xlsx')

# Unir los DataFrames
df_result = pd.merge(df, df_cod, on='Producto')

# Dar formato al DataFrame final
df_result.dropna(inplace=True)
df_result.drop(['Codigo','Producto'], axis=1, inplace=True)
df_result = df_result[['Cod','Dosificado']]

# Crear carpeta si no existe
# Especificamos la ruta de la carpeta que deseamos crear
ruta_carpeta = 'ReporteDiario'

# Verificamos si la carpeta ya existe
if not os.path.exists(ruta_carpeta):
    # Creamos la carpeta si no existe
    os.mkdir(ruta_carpeta)
    
# Exportamos el DataFrame a un archivo de Excel
df_result.to_csv(f"ReporteDiario/{fecha_actual}.csv", index=False)