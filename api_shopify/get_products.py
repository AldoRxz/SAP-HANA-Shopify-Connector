import requests
import os
from dotenv import load_dotenv

print("🚀 El script ha comenzado a ejecutarse...")

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de la API
SHOP_NAME = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    
    # Manejo de errores HTTP
    if response.status_code == 200:
        data = response.json()
        print("✅ Productos obtenidos correctamente:")
        print(data)  # Puedes formatearlo mejor si hay muchos productos
    elif response.status_code == 401:
        print("❌ Error 401: No autorizado. Revisa tu ACCESS_TOKEN.")
    elif response.status_code == 404:
        print("❌ Error 404: URL no encontrada. Verifica SHOP_NAME y API_VERSION.")
    else:
        print(f"⚠️ Error {response.status_code}: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")
