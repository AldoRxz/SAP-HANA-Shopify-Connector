from hdbcli import dbapi
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Configuración de SAP HANA desde el .env
HANA_CONFIG = {
    'address': os.getenv("HANA_ADDRESS"),
    'port': int(os.getenv("HANA_PORT")),
    'user': os.getenv("HANA_USER"),
    'password': os.getenv("HANA_PASSWORD")
}

# Configuración de MySQL desde el .env
MYSQL_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT")),
    'database': os.getenv("MYSQL_DATABASE"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'charset': os.getenv("MYSQL_CHARSET")
}

try:
    # Conectar a SAP HANA
    hana_conn = dbapi.connect(**HANA_CONFIG)
    hana_cursor = hana_conn.cursor()
    print("✅ Conexión exitosa a SAP HANA")

    # Consulta en SAP HANA
    hana_query = """
        SELECT  
            O."ItemCode",  
            O."SWW" AS "Vendor", 
            O."U_ESTA_PROD" AS "Estado",  
            COALESCE(W."OnHand", 0) AS "OnHand",  
            COALESCE(P."Price", 0) AS "Price"  
        FROM "SBO_MANIJAUTO"."OITM" O
        LEFT JOIN "SBO_MANIJAUTO"."OITW" W 
            ON O."ItemCode" = W."ItemCode" 
            AND W."WhsCode" = 'M'
        LEFT JOIN "SBO_MANIJAUTO"."ITM1" P
            ON O."ItemCode" = P."ItemCode" 
            AND P."PriceList" = 1
        WHERE O."validFor" = 'Y'
        AND O."ItemType" = 'I'
    """
    hana_cursor.execute(hana_query)
    hana_results = hana_cursor.fetchall()
    hana_df = pd.DataFrame(hana_results, columns=['ItemCode', 'Vendor', 'Estado', 'OnHand', 'Price'])

    # Conectar a MySQL
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    print("✅ Conexión exitosa a MySQL")

    # Consulta en MySQL con los campos requeridos
    mysql_query = """
        SELECT 
            t1.codigo AS ItemCode,
            t2.Descripcion AS parte,
            t3.maDescripcion AS marca,
            t4.moDescripcion AS modelo,
            t5.vDescripcion AS version,
            CAST(t6.Anio AS UNSIGNED) AS ano_inicio,
            CAST(t61.Anio AS UNSIGNED) AS ano_fin,
            lad.lado_description AS lado,
            t7.link_rewrite AS LinkRewrite,
            t7.tags AS Tags,
            t7.name AS Nombre,
            t7.descripcionl AS DescripciónLarga,
            t7.meta_description AS MetaDescripción
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
    mysql_cursor.execute(mysql_query)
    mysql_results = mysql_cursor.fetchall()
    mysql_df = pd.DataFrame(mysql_results, columns=['ItemCode', 'parte', 'marca', 'modelo', 'version', 'ano_inicio', 'ano_fin', 'lado', 'LinkRewrite', 'Tags', 'Nombre', 'DescripciónLarga', 'MetaDescripción'])

    # Convertir los años a enteros, manejando valores nulos
    mysql_df['ano_inicio'] = mysql_df['ano_inicio'].fillna(0).astype(int)
    mysql_df['ano_fin'] = mysql_df['ano_fin'].fillna(0).astype(int)

    # Unir los datos usando ItemCode como clave
    merged_df = pd.merge(hana_df, mysql_df, on='ItemCode', how='inner')

    # Limitar la salida a 10 registros
    merged_df = merged_df.head(10)

    # Mostrar la tabla combinada en consola
    print(merged_df.to_string(index=False))

    # Cerrar conexiones
    hana_cursor.close()
    hana_conn.close()
    mysql_cursor.close()
    mysql_conn.close()

except Exception as e:
    print(f"❌ Error en la conexión o consulta: {e}")
