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

    # Consulta SQL con los campos necesarios para Shopify
    query = """
    SELECT 
        "ItemCode", 
        "ItemName",  
        "U_Marca",
        "ItmsGrpCod",
        "U_FAMILIA",
        "U_SUB_FAM",
        "U_LINEA",
        ("OnHand" - "IsCommited") AS Variant_Inventory_Qty, 
        "Price",
        "U_Peso",
        "U_CodigoBarras"
    FROM "SBO_MANIJAUTO"."OITM";
    """

    # Ejecutar la consulta
    cursor.execute(query)

    # Obtener los nombres de las columnas
    column_names = [desc[0] for desc in cursor.description]

    # Obtener los resultados
    results = cursor.fetchall()

    # Convertir resultados a DataFrame
    df = pd.DataFrame(results, columns=column_names)

    # Convertir datos al formato de Shopify
    df_shopify = pd.DataFrame({
        "Handle": df["ItemCode"].str.lower().str.replace(" ", "-"),  # URL amigable
        "Title": df["ItemName"],
        "Body (HTML)": df["ItemName"],  # Usamos ItemName como descripción
        "Vendor": df["U_Marca"],
        "Type": df["ItmsGrpCod"].astype(str),
        "Tags": df["U_FAMILIA"].fillna('') + ", " + df["U_SUB_FAM"].fillna('') + ", " + df["U_LINEA"].fillna(''),
        "Published": "TRUE",
        "Option1 Name": "Title",
        "Option1 Value": "Default Title",
        "Variant SKU": df["ItemCode"],
        "Variant Grams": (df["U_Peso"] * 1000).fillna(0),  # Convertir KG a gramos
        "Variant Inventory Tracker": "shopify",
        "Variant Inventory Qty": df["Variant_Inventory_Qty"].fillna(0),
        "Variant Inventory Policy": "continue",
        "Variant Fulfillment Service": "manual",
        "Variant Price": df["Price"].fillna(0),
        "Variant Compare At Price": "",  # Vacío si no hay descuentos
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
        "Variant Barcode": df["U_CodigoBarras"].fillna(''),
        "Image Src": ""  # Puedes agregar imágenes después
    })

    # Guardar en un archivo CSV para Shopify
    csv_file = "productos_shopify.csv"
    df_shopify.to_csv(csv_file, index=False, encoding="utf-8-sig")

    print(f"✅ Archivo CSV generado con éxito: {csv_file}")

    # Cerrar conexión
    connection.close()

except Exception as e:
    print(f"❌ Error conectando a SAP HANA: {e}")
