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

# URL de la API de colecciones personalizadas
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/custom_collections.json"

# Cabeceras de autenticación
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

try:
    print(f"🔍 Consultando categorías (colecciones) en: {url}")
    
    response = requests.get(url, headers=headers)
    print(f"🔄 Código de respuesta: {response.status_code}")

    if response.status_code == 200:
        collections = response.json()
        print("✅ Categorías obtenidas correctamente:")
        print(collections)
    else:
        print(f"⚠️ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")
