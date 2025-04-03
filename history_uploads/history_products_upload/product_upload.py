from hdbcli import dbapi
import mysql.connector
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# SAP HANA configuration
HANA_CONFIG = {
    'address': os.getenv("HANA_ADDRESS"),
    'port': int(os.getenv("HANA_PORT", 0)),
    'user': os.getenv("HANA_USER"),
    'password': os.getenv("HANA_PASSWORD")
}

# MySQL configuration
MYSQL_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT", 0)),
    'database': os.getenv("MYSQL_DATABASE"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'charset': os.getenv("MYSQL_CHARSET")
}

try:
    # Connect to SAP HANA
    hana_conn = dbapi.connect(**HANA_CONFIG)
    hana_cursor = hana_conn.cursor()
    print("✅ Successfully connected to SAP HANA")

    # Query SAP HANA
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
    hana_df = pd.DataFrame(hana_results, columns=['ItemCode', 'Vendor', 'Estado', 'OnHand', 'Price'])

    # Connect to MySQL
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    print("✅ Successfully connected to MySQL")

    # Query MySQL
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
    mysql_df = pd.DataFrame(mysql_results, columns=['ItemCode', 'Type', 'Handle', 'Tags', 'Title', 'Body (HTML)', 'SEO Description'])

    # Merge SAP and MySQL data on ItemCode
    merged_df = pd.merge(hana_df, mysql_df, on='ItemCode', how='inner')

    # Add Shopify-specific fields
    merged_df['SEO Title'] = merged_df['Handle']
    merged_df['Product Category'] = 'Autoparts'
    merged_df['Published'] = True
    merged_df['Variant Inventory Tracker'] = 'shopify'
    merged_df['Variant Inventory Policy'] = 'deny'
    merged_df['Variant Requires Shipping'] = True
    merged_df['Variant Taxable'] = False

    # Rename SAP columns to match Shopify fields
    merged_df.rename(columns={
        'ItemCode': 'Variant SKU',
        'OnHand': 'Variant Inventory Qty',
        'Price': 'Variant Price'
    }, inplace=True)

    # Create a list to store all product data for export
    product_data_list = []

    # Loop through filtered products and collect the data for export
    for _, row in merged_df.iterrows():
        product_data = {
            "Title": row['Title'],
            "Body (HTML)": row['Body (HTML)'],
            "Vendor": row['Vendor'],
            "Type": row['Type'],
            "Handle": row['Handle'],
            "Tags": row['Tags'],
            "SEO Title": row['SEO Title'],
            "SEO Description": row['SEO Description'],
            "Variant SKU": row['Variant SKU'],
            "Variant Price": float(row['Variant Price']),
            "Variant Inventory Qty": int(row['Variant Inventory Qty']),
            "Images": ""  # No se verifica imagen, dejamos la columna vacía
        }

        product_data_list.append(product_data)

    # Convertir la lista de datos a un DataFrame
    export_df = pd.DataFrame(product_data_list)

    # Guardar el DataFrame en un archivo Excel
    export_path = "productos_exportados.xlsx"
    export_df.to_excel(export_path, index=False)
    print(f"✅ Excel file '{export_path}' created successfully.")

    # Close database connections
    hana_cursor.close()
    hana_conn.close()
    mysql_cursor.close()
    mysql_conn.close()

except Exception as e:
    print(f"❌ Connection or query error: {e}")
