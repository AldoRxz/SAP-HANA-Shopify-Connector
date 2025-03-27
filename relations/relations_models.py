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

# Función para obtener marcas y sus modelos
def get_brands_and_models():
    # Conectar a MySQL
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        # Consulta SQL para obtener marcas y modelos
        query = """
            SELECT 
                t3.maDescripcion AS marca,
                t4.moDescripcion AS modelo
            FROM aplicaciones_ap t1
            JOIN tiposmarca_ap t3 ON t3.IdMarca = t1.id_marca
            LEFT JOIN tiposmodelo_ap t4 ON t4.IdModelo = t1.id_modelo
            GROUP BY t3.maDescripcion, t4.moDescripcion;
        """
        
        # Ejecutar consulta
        cursor.execute(query)
        results = cursor.fetchall()

        # Definir columnas
        columns = ['marca', 'modelo']

        # Convertir resultados a DataFrame de Pandas
        df = pd.DataFrame(results, columns=columns)

        # Agrupar modelos por marca
        brand_model_map = df.groupby('marca')['modelo'].apply(list).to_dict()

        # Convertir el diccionario en un DataFrame para una visualización más clara
        df_brand_model_map = pd.DataFrame(list(brand_model_map.items()), columns=['Marca', 'Modelos'])

        return df_brand_model_map

    except mysql.connector.Error as e:
        print(f"❌ Error en la consulta MySQL: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Ejecutar la función
df_brand_model_map = get_brands_and_models()

# Ajustar la visualización para mostrar todo el DataFrame sin truncamientos
pd.set_option('display.max_rows', None)  # Mostrar todas las filas
pd.set_option('display.max_columns', None)  # Mostrar todas las columnas
pd.set_option('display.width', None)  # Ajustar el ancho de la consola
pd.set_option('display.max_colwidth', None)  # No truncar el contenido de las columnas

# Mostrar el DataFrame completo
print(df_brand_model_map)



# Guardar el DataFrame en un archivo CSV
df_brand_model_map.to_csv('marcas_y_modelos.csv', index=False)

print("✅ El archivo CSV ha sido guardado exitosamente como 'marcas_y_modelos.csv'.")