import MySQLdb
from datetime import datetime, timedelta
import pandas as pd
import os
from tkinter import Tk, Label, Button, filedialog, StringVar
from tkcalendar import DateEntry

def seleccionar_fechas():
    def procesar():
        # Obtener fechas seleccionadas
        fecha_fin = cal_fin.get_date().strftime("%Y-%m-%d")
        fecha_inicio = cal_inicio.get_date().strftime("%Y-%m-%d")

        # Conectar a la base de datos
        db = MySQLdb.connect(host="192.168.0.12", user="operario", passwd="", db="dbp8100")
        cur = db.cursor()

        # Ejecutar consulta
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
        """, (fecha_inicio, fecha_fin))

        # Obtener resultados y cerrar conexión
        resultados = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
        cur.close()
        db.close()

        # Crear DataFrame
        df = pd.DataFrame(resultados, columns=columnas)

        # Cargar códigos de productos
        ruta_codigos = r"\\192.168.0.12\samba-share\public\Resumen_MP_Diario\codigos.xlsx"
        #ruta_codigos = filedialog.askopenfilename(title="Selecciona el archivo de códigos", filetypes=[("Archivos Excel", "*.xlsx")])
        #if not ruta_codigos:
        #    print("Operación cancelada: No se seleccionó un archivo de códigos.")
        #    return

        df_cod = pd.read_excel(ruta_codigos)

        # Unir DataFrames
        df_result = pd.merge(df, df_cod, on='Producto')
        df_result.dropna(inplace=True)
        df_result.drop(['Codigo', 'Producto'], axis=1, inplace=True)
        df_result = df_result[['Cod', 'Dosificado']]

        # Seleccionar carpeta de salida
        ruta_salida = filedialog.askdirectory(title="Selecciona la carpeta para guardar el archivo")
        if not ruta_salida:
            print("Operación cancelada: No se seleccionó una carpeta de salida.")
            return

        # Guardar archivo
        nombre_archivo = os.path.join(ruta_salida, f"{fecha_actual}.csv")
        df_result.to_csv(nombre_archivo, index=False, header=False, sep=';')
        print(f"Archivo guardado en: {nombre_archivo}")

        # Cerrar ventana
        ventana.destroy()

    # Crear ventana
    ventana = Tk()
    ventana.title("Seleccionar Fechas")

    # Etiquetas y calendarios
    Label(ventana, text="Fecha Inicio:").grid(row=0, column=0, padx=10, pady=10)
    cal_inicio = DateEntry(ventana, date_pattern='yyyy-mm-dd')
    cal_inicio.grid(row=0, column=1, padx=10, pady=10)

    Label(ventana, text="Fecha Final:").grid(row=1, column=0, padx=10, pady=10)
    cal_fin = DateEntry(ventana, date_pattern='yyyy-mm-dd')
    cal_fin.grid(row=1, column=1, padx=10, pady=10)

    # Botón para procesar
    Button(ventana, text="Procesar", command=procesar).grid(row=2, column=0, columnspan=2, pady=20)

    ventana.mainloop()

if __name__ == "__main__":
    seleccionar_fechas()
