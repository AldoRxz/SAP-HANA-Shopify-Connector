from hdbcli import dbapi
import pandas as pd

# Configuración de conexión a SAP HANA
HANA_HOST = "192.168.0.201"
HANA_PORT = 30015
HANA_USER = "SYSTEM"
HANA_PASSWORD = "stmB1Admin"

try:
    # Conectar a SAP HANA
    connection = dbapi.connect(
        address=HANA_HOST,
        port=HANA_PORT,
        user=HANA_USER,
        password=HANA_PASSWORD
    )

    print("✅ Conexión exitosa a SAP HANA")

    # Crear cursor
    cursor = connection.cursor()

    # Consulta para obtener los nombres reales de las columnas
    query_test = 'SELECT * FROM "SBO_MANIJAUTO"."OITM" LIMIT 5'
    cursor.execute(query_test)

    # Obtener los nombres de las columnas reales
    column_names = [desc[0] for desc in cursor.description]
    print("📌 Columnas en OITM:", column_names)

    # Obtener algunos resultados de prueba
    results = cursor.fetchall()
    
    # Imprimir datos con sus nombres de columna
    for row in results:
        print(dict(zip(column_names, row)))

    # Consulta SQL para obtener productos con los campos necesarios para Shopify
    query = """
    SELECT COLUMN_NAME 
        FROM SYS.TABLE_COLUMNS 
        WHERE TABLE_NAME = 'OITM'
        AND SCHEMA_NAME = 'SBO_MANIJAUTO';

    """

    # Ejecutar la consulta principal
    cursor.execute(query)

    # Obtener los nombres de las columnas
    column_names = [desc[0] for desc in cursor.description]

    # Obtener los resultados
    results = cursor.fetchall()

    # Convertir resultados a DataFrame
    df_shopify = pd.DataFrame(results, columns=column_names)

    # Guardar en un archivo CSV para importar a Shopify
    csv_file = "productos_shopify.csv"
    df_shopify.to_csv(csv_file, index=False, encoding="utf-8-sig")

    print(f"✅ Archivo CSV generado con éxito: {csv_file}")

    # Cerrar conexión
    connection.close()

except Exception as e:
    print(f"❌ Error conectando a SAP HANA: {e}")
