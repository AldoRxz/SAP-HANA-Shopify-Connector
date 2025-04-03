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

try:
    # Conectar a MySQL
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Consulta SQL para obtener todos los detalles de los productos
    query = """
        SELECT 
            t2.Descripcion AS parte,
            t3.maDescripcion AS marca,
            t4.moDescripcion AS modelo,
            t5.vDescripcion AS version,
            t6.Anio AS a_o_inicio,
            t61.Anio AS ano_fin,
            lad.lado_description AS lado
        FROM aplicaciones_ap t1
        JOIN descripciones_ap t7 ON t1.codigo = t7.codigo
        LEFT JOIN tiposparte_ap t2 ON t2.Id = t1.tipo_parte
        LEFT JOIN tiposmarca_ap t3 ON t3.IdMarca = t1.id_marca
        LEFT JOIN tiposmodelo_ap t4 ON t4.IdModelo = t1.id_modelo
        LEFT JOIN tiposversion_ap t5 ON t5.IdVersion = t1.id_version
        LEFT JOIN anios t6 ON t6.Id = t1.id_ano_in
        LEFT JOIN anios t61 ON t61.Id = t1.id_ano_fin
        LEFT JOIN lado_ap lad ON lad.id_lado = t1.id_lado;
    """

    # Ejecutar consulta
    cursor.execute(query)
    results = cursor.fetchall()

    # Definir columnas
    columns = ['parte', 'marca', 'modelo', 'version', 'a_o_inicio', 'ano_fin', 'lado']

    # Convertir resultados a DataFrame de Pandas
    df = pd.DataFrame(results, columns=columns)

    # Asegurar que los años sean enteros
    df['a_o_inicio'] = df['a_o_inicio'].fillna(0).astype('Int64')
    df['ano_fin'] = df['ano_fin'].fillna(0).astype('Int64')

    # Obtener listas de valores únicos para los campos solicitados
    unique_parte = sorted(df["parte"].dropna().unique().tolist())
    unique_marca = sorted(df["marca"].dropna().unique().tolist())

    # Imprimir solo las listas de partes y marcas
    print("\n🔑 Valores únicos de cada campo:")
    print(f"Partes: {unique_parte}")
    print(f"Marcas: {unique_marca}")

except mysql.connector.Error as e:
    print(f"❌ Error conectando a MySQL: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
