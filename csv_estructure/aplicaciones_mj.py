import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT", 0)),
    'database': os.getenv("MYSQL_DATABASE"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'charset': os.getenv("MYSQL_CHARSET")
}

try:
    # Conectar a MySQL
    connection = mysql.connector.connect(**DB_CONFIG)
    print("✅ Conexión exitosa a MySQL")

    # Crear cursor
    cursor = connection.cursor()

    # Consulta SQL para obtener los datos requeridos
    query = """
        SELECT 
            codigo, 
            tipo_parte, 
            link_rewrite, 
            tags, 
            name, 
            descripcionl 
        FROM descripciones_ap
        LIMIT 10;
    """

    # Ejecutar consulta
    cursor.execute(query)

    # Obtener resultados y convertir a DataFrame
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['Código', 'Tipo de Parte', 'Link Rewrite', 'Tags', 'Nombre', 'Descripción'])

    # Mostrar tabla en consola
    print(df.to_string(index=False))

    # Cerrar conexión
    cursor.close()
    connection.close()

except mysql.connector.Error as e:
    print(f"❌ Error conectando a MySQL: {e}")
