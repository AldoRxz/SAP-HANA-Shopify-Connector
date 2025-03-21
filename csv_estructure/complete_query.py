from hdbcli import dbapi
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de SAP HANA
HANA_CONFIG = {
    'address': os.getenv("HANA_ADDRESS"),
    'port': int(os.getenv("HANA_PORT", 0)),
    'user': os.getenv("HANA_USER"),
    'password': os.getenv("HANA_PASSWORD")
}

# Configuración de MySQL
MYSQL_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT", 0)),
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
            O."SWW", 
            O."U_ESTA_PROD",  
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
    hana_df = pd.DataFrame(hana_results, columns=['ItemCode', 'Marca', 'Estado', 'OnHand', 'Price'])

    # Conectar a MySQL
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    print("✅ Conexión exitosa a MySQL")

    # Consulta en MySQL
    mysql_query = """
        SELECT 
            codigo, 
            tipo_parte, 
            link_rewrite, 
            tags, 
            name, 
            descripcionl,
            meta_description
        FROM descripciones_ap
    """
    mysql_cursor.execute(mysql_query)
    mysql_results = mysql_cursor.fetchall()
    mysql_df = pd.DataFrame(mysql_results, columns=['ItemCode', 'Tipo de Parte', 'Link Rewrite', 'Tags', 'Nombre', 'Descripción', 'meta_description'])

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
