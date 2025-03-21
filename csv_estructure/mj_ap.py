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

    # Consulta SQL con los campos requeridos
    query = """
        SELECT 
            t1.codigo AS codigo,
            t2.Descripcion AS Descripcion,
            t3.maDescripcion AS Marca,
            t4.moDescripcion AS Modelo,
            t5.vDescripcion AS Version,
            CAST(t6.Anio AS UNSIGNED) AS AnioInicio,
            CAST(t61.Anio AS UNSIGNED) AS AnioFin,
            lad.lado_description AS Lado
        FROM aplicaciones_ap t1
        JOIN descripciones_ap t7 ON t1.codigo = t7.codigo
        LEFT JOIN tiposparte_ap t2 ON t2.Id = t1.tipo_parte
        LEFT JOIN tiposmarca_ap t3 ON t3.IdMarca = t1.id_marca
        LEFT JOIN tiposmodelo_ap t4 ON t4.IdModelo = t1.id_modelo
        LEFT JOIN tiposversion_ap t5 ON t5.IdVersion = t1.id_version
        LEFT JOIN anios t6 ON t6.Id = t1.id_ano_in
        LEFT JOIN anios t61 ON t61.Id = t1.id_ano_fin
        LEFT JOIN lado_ap lad ON lad.id_lado = t1.id_lado
        ORDER BY t2.Descripcion, t3.maDescripcion, t4.moDescripcion, t5.vDescripcion;
    """

    # Ejecutar consulta
    cursor.execute(query)

    # Obtener resultados y convertir a DataFrame
    results = cursor.fetchall()
    columns = ['Código', 'Descripción', 'Marca', 'Modelo', 'Versión', 'Año Inicio', 'Año Fin', 'Lado']
    df = pd.DataFrame(results, columns=columns)

    # Convertir los años a enteros, manejando valores nulos
    df['Año Inicio'] = df['Año Inicio'].fillna(0).astype(int)
    df['Año Fin'] = df['Año Fin'].fillna(0).astype(int)

    # Mostrar tabla en consola
    print(df.to_string(index=False))

    # Cerrar conexión
    cursor.close()
    connection.close()

except mysql.connector.Error as e:
    print(f"❌ Error conectando a MySQL: {e}")
