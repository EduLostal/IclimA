import os
import json
import requests
from datetime import datetime, timedelta
from time import sleep
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("API_KEY")
IDEMA = "3195"  # Estación del Retiro

# Ruta absoluta al JSON
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SALIDA = os.path.join(BASE_DIR, "data", "historico_raw_madrid.json")

def cargar_json_existente():
    if os.path.exists(SALIDA):
        with open(SALIDA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def obtener_ultima_fecha(datos):
    if not datos:
        return None
    fechas = [datetime.strptime(d["fecha"][:10], "%Y-%m-%d") for d in datos if "fecha" in d]
    return max(fechas) if fechas else None

def descargar_mes_a_mes(desde: str, hasta: str):
    fecha_ini = datetime.strptime(desde, "%Y-%m-%d")
    fecha_fin = datetime.strptime(hasta, "%Y-%m-%d")

    datos_existentes = cargar_json_existente()
    ultima_fecha = obtener_ultima_fecha(datos_existentes)

    if ultima_fecha:
        print(f"📌 Última fecha en el JSON: {ultima_fecha.strftime('%Y-%m-%d')}")
    else:
        print("📭 No hay datos en el JSON.")

    if ultima_fecha and ultima_fecha >= fecha_ini:
        fecha_ini = ultima_fecha + timedelta(days=1)

    print(f"📆 Descargando desde: {fecha_ini.strftime('%Y-%m-%d')} hasta {fecha_fin.strftime('%Y-%m-%d')}")

    datos_mes = []
    mes_actual = None
    resultados = datos_existentes.copy()
    total_dias = (fecha_fin - fecha_ini).days + 1

    for i in range(total_dias):
        fecha = fecha_ini + timedelta(days=i)
        fecha_str = fecha.strftime("%Y-%m-%dT00:00:00UTC")
        fecha_log = fecha.strftime("%Y-%m-%d")

        print(f"📅 {fecha_log} - descargando...")

        url = (
            f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/"
            f"datos/fechaini/{fecha_str}/fechafin/{fecha_str}/estacion/{IDEMA}"
        )
        headers = {"api_key": API_KEY}

        intentos = 0
        exito = False
        while intentos < 3 and not exito:
            try:
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    url_datos = r.json().get("datos")
                    if not url_datos:
                        print("⚠️ No se encontró URL de datos.")
                        break

                    r_datos = requests.get(url_datos)
                    if r_datos.status_code == 200:
                        datos_dia = r_datos.json()
                        if datos_dia:
                            datos_mes.append(datos_dia[0])
                            print("✅ Datos guardados en memoria.")
                        else:
                            print("⚪ Sin datos para este día.")
                        exito = True
                    else:
                        print(f"❌ Error en JSON real ({r_datos.status_code})")
                        intentos += 1
                        sleep(2)
                else:
                    print(f"❌ Error en petición ({r.status_code}). Reintentando...")
                    intentos += 1
                    sleep(30)
            except Exception as e:
                print(f"💥 Excepción: {e}")
                intentos += 1
                sleep(30)

        if not exito:
            print(f"🚫 Día {fecha_log} fallido tras 3 intentos. Saltando.\n")

        # Guardar si cambiamos de mes o es el último día
        nuevo_mes = fecha.month
        if mes_actual is None:
            mes_actual = nuevo_mes

        if nuevo_mes != mes_actual or i == total_dias - 1:
            resultados.extend(datos_mes)
            with open(SALIDA, "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"💾 Datos del mes {mes_actual:02d} guardados en {SALIDA} ✅\n")
            datos_mes = []
            mes_actual = nuevo_mes

        sleep(1.5)

    print("🎉 Descarga finalizada.")

if __name__ == "__main__":
    desde = sys.argv[1] if len(sys.argv) > 1 else "2005-01-01"
    hasta = sys.argv[2] if len(sys.argv) > 2 else datetime.today().strftime("%Y-%m-%d")
    descargar_mes_a_mes(desde, hasta)
