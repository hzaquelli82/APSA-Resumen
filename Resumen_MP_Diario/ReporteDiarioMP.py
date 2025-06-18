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
# fecha_actual = "2025-04-03"
fecha_actual = fecha_actual.strftime("%Y-%m-%d")

fecha_ayer = datetime.now() - timedelta(days=1)
# fecha_ayer = "2025-04-02"
fecha_ayer = fecha_ayer.strftime('%Y-%m-%d')

# print(f"Fecha actual: {fecha_actual}")
# print(f"Fecha de ayer: {fecha_ayer}")

# Ejecutar la consulta
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
        (tareaseje.Fecha = %s AND tareaseje.Hora >= '23:00:00') OR 
        (tareaseje.Fecha > %s AND tareaseje.Fecha <= %s AND tareaseje.Hora < '23:00:00')
    GROUP BY 
        productox.Nombre
""", (fecha_ayer, fecha_ayer, fecha_actual))

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
# df_cod = pd.read_excel('codigos.xlsx')
# ruta_codigos = r"\\192.168.0.12\samba-share\public\Resumen_MP_Diario\codigos.xlsx"
# df_cod = pd.read_excel(ruta_codigos)
df_cod = pd.read_excel('/samba/public/Resumen_MP_Diario/codigos.xlsx')
# Unir los DataFrames
df_result = pd.merge(df, df_cod, on='Producto')

# Dar formato al DataFrame final
df_result.dropna(inplace=True)
# df_result.drop(['Codigo','Producto'], axis=1, inplace=True)
df_result = df_result[['Cod','Dosificado']]
df_result['Dosificado'] = df_result['Dosificado'] * (-1)

# Especificamos la ruta de la carpeta que deseamos usar
# ruta_carpeta = 'ReporteDiario'
# ruta_carpeta = f'C:\Users\Hugo\Documents\APSA-ResumenMP\Resumen MP diario\ReporteDiario'
ruta_carpeta = '/samba/public/Resumen_MP_Diario'

# Verificamos si la carpeta ya existe
if not os.path.exists(ruta_carpeta):
    # Creamos la carpeta si no existe
    os.mkdir(ruta_carpeta)
    
# Exportamos el DataFrame a un archivo de Excel
# df_result.to_csv(f"ReporteDiario/{fecha_actual}.csv", index=False, header=False, sep=';')
# df_result.to_csv(f"C:\Users\Hugo\Documents\APSA-ResumenMP\Resumen MP diario\ReporteDiario\{fecha_actual}.csv", index=False, header=False, sep=';')
df_result.to_csv(f"{ruta_carpeta}/{fecha_actual}.csv", index=False, header=False, sep=';')