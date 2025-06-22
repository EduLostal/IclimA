import subprocess
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOADER_PATH = os.path.join(BASE_DIR, "aemet", "downloader.py")
FORMATTER_PATH = os.path.join(BASE_DIR, "aemet", "formatter.py")

def ejecutar_script(command):
    try:
        print(f"▶ Ejecutando: {' '.join(command)}")
        subprocess.run(command, check=True)
        print("✅ Ejecutado correctamente.\n")
    except subprocess.CalledProcessError as e:
        print("❌ Error ejecutando el script.")
        print(e)

if __name__ == "__main__":
    hoy = datetime.today().date()
    hasta = hoy - timedelta(days=4)

    ejecutar_script(["python", DOWNLOADER_PATH, "2005-01-01", hasta.strftime("%Y-%m-%d")])
    ejecutar_script(["python", FORMATTER_PATH])
