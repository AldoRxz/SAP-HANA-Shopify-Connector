from hdbcli import dbapi
import mysql.connector
import pandas as pd
import requests
import json
import time
import os
from decimal import Decimal
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

# Configuración de Shopify
SHOP_NAME = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOPIFY_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# Función para convertir Decimals a float
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

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
    hana_df = pd.DataFrame(hana_results, columns=['ItemCode', 'Vendor', 'Estado', 'OnHand', 'Price'])

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
    mysql_df = pd.DataFrame(mysql_results, columns=['ItemCode', 'Type', 'Handle', 'Tags', 'Title', 'Body (HTML)', 'SEO Description'])

    # Unir los datos usando ItemCode como clave
    merged_df = pd.merge(hana_df, mysql_df, on='ItemCode', how='inner')

    # Renombrar columnas y agregar valores fijos para Shopify
    merged_df['SEO Title'] = merged_df['Handle']
    merged_df['Product Category'] = 'Autopartes'
    merged_df['Published'] = True
    merged_df['Variant Inventory Tracker'] = 'shopify'
    merged_df['Variant Inventory Policy'] = 'deny'
    merged_df['Variant Requires Shipping'] = True
    merged_df['Variant Taxable'] = False

    # Renombrar columnas de SAP HANA
    merged_df.rename(columns={
        'ItemCode': 'Variant SKU',
        'OnHand': 'Variant Inventory Qty',
        'Price': 'Variant Price'
    }, inplace=True)

    # Convertir datos en JSON para Shopify
    for _, row in merged_df.iterrows():
        product_data = {
        "product": {
            "title": row['Title'],
            "body_html": row['Body (HTML)'],
            "vendor": row['Vendor'],
            "product_type": row['Type'],
            "handle": row['Handle'],
            "tags": row['Tags'],
            "product_category": 340,
            "published": True,
            "images": [{
                "src": f"https://www.manijauto.com.mx/imagenes/{row['Variant SKU']}.jpg"
            }],
            "variants": [{
                "sku": row['Variant SKU'],
                "price": float(row['Variant Price']),
                "inventory_quantity": int(row['Variant Inventory Qty']),
                "inventory_management": "shopify",
                "inventory_policy": "deny",
                "requires_shipping": True,
                "taxable": False
            }],
            "metafields": [
                {
                    "namespace": "global",
                    "key": "seo_title",
                    "value": row['SEO Title'],
                    "type": "string"
                },
                {
                    "namespace": "global",
                    "key": "seo_description",
                    "value": row['SEO Description'],
                    "type": "string"
                }
            ]
        }
    }
        try:
            response = requests.post(SHOPIFY_URL, headers=HEADERS, json=product_data, verify=True)
            if response.status_code == 201:
                print(f"✅ Producto {row['Title']} subido correctamente")
            else:
                print(f"❌ Error al subir {row['Title']}: {response.text}")
        except requests.exceptions.RequestException as req_error:
            print(f"⚠️ Error en la solicitud: {req_error}")
        
        time.sleep(1)  # Evita exceder el límite de Shopify

    # Cerrar conexiones
    hana_cursor.close()
    hana_conn.close()
    mysql_cursor.close()
    mysql_conn.close()

except Exception as e:
    print(f"❌ Error en la conexión o consulta: {e}")
