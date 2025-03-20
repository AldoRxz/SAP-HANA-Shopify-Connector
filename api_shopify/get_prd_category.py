import requests
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de la API
SHOP_NAME = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# URLs de las colecciones
custom_collections_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/custom_collections.json"
smart_collections_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/smart_collections.json"

# Cabeceras de autenticación
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

try:
    print("🔍 Consultando colecciones personalizadas...")
    custom_response = requests.get(custom_collections_url, headers=headers)
    print(f"🔄 Código de respuesta: {custom_response.status_code}")

    if custom_response.status_code == 200:
        custom_collections = custom_response.json()
        print("✅ Colecciones personalizadas obtenidas correctamente:")
        print(custom_collections)
    else:
        print(f"⚠️ Error {custom_response.status_code}: {custom_response.text}")

    print("\n🔍 Consultando colecciones inteligentes...")
    smart_response = requests.get(smart_collections_url, headers=headers)
    print(f"🔄 Código de respuesta: {smart_response.status_code}")

    if smart_response.status_code == 200:
        smart_collections = smart_response.json()
        print("✅ Colecciones inteligentes obtenidas correctamente:")
        print(smart_collections)
    else:
        print(f"⚠️ Error {smart_response.status_code}: {smart_response.text}")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")
