import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MySQL
DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT", 3306)),
    'database': os.getenv("MYSQL_DATABASE"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'charset': os.getenv("MYSQL_CHARSET", "utf8mb4")
}

# Función para obtener partes y sus marcas asociadas
def get_parts_and_brands():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        query = """
            SELECT 
                t2.Descripcion AS parte,
                t3.maDescripcion AS marca
            FROM aplicaciones_ap t1
            JOIN tiposparte_ap t2 ON t2.Id = t1.tipo_parte
            JOIN tiposmarca_ap t3 ON t3.IdMarca = t1.id_marca
            GROUP BY t2.Descripcion, t3.maDescripcion;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        columns = ['parte', 'marca']
        df = pd.DataFrame(results, columns=columns)

        # Agrupar marcas por parte
        part_brand_map = df.groupby('parte')['marca'].apply(list).to_dict()

        # Convertir a DataFrame
        df_part_brand_map = pd.DataFrame(list(part_brand_map.items()), columns=['Parte', 'Marcas'])

        return df_part_brand_map

    except mysql.connector.Error as e:
        print(f"❌ Error en la consulta MySQL: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Ejecutar
df_part_brand_map = get_parts_and_brands()

# Opciones de visualización
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Mostrar resultado
print(df_part_brand_map)

# Guardar en CSV
df_part_brand_map.to_csv('partes_y_marcas.csv', index=False)

print("✅ El archivo CSV ha sido guardado exitosamente como 'partes_y_marcas.csv'.")
