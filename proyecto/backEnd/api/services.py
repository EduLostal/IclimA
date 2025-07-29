import subprocess
import os
from datetime import datetime
from model.predictor import Predictor
from api.schemas import PrediccionResponse
import pandas as pd

# Rutas base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(BASE_DIR, "data", "historico_raw_madrid.json")
PARQUET_PATH = os.path.join(BASE_DIR, "data", "historico_limpio.parquet")
MODEL_PATH = os.path.join(BASE_DIR, "model", "modelo_entrenado.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "model", "feature_order.json")

def ejecutar_script(script_path: str):
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"✅ Ejecutado: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_path}: {e}")
        raise

# def parquet_desactualizado() -> bool:
#     try:
#         if not os.path.exists(PARQUET_PATH):
#             return True

#         df_json = pd.read_json(JSON_PATH)
#         df_parquet = pd.read_parquet(PARQUET_PATH)

#         fecha_json = pd.to_datetime(df_json["fecha"], errors="coerce").max()
#         fecha_parquet = pd.to_datetime(
#             df_parquet["año"].astype(str) + "-" +
#             df_parquet["mes"].astype(str) + "-" +
#             df_parquet["dia"].astype(str),
#             errors="coerce"
#         ).max()

#         if fecha_json > fecha_parquet:
#             print("📌 Parquet desactualizado respecto al JSON.")
#             return True
#         return False

#     except Exception as e:
#         print(f"⚠️ Error comparando fechas: {e}")
#         return True


def predecir_para_fecha_y_estacion(fecha: datetime, estacion: str):
    print("🔄 Ejecutando flujo completo...")


    ejecutar_script(os.path.join(BASE_DIR, "aemet", "daysCheck.py"))

    
    #if parquet_desactualizado():
        #ejecutar_script(os.path.join(BASE_DIR, "model", "trainer.py"))


    predictor = Predictor(MODEL_PATH, PARQUET_PATH, FEATURES_PATH)
    predictor.cargar_modelo_y_datos()
    input_df = predictor.preparar_input(fecha)

    if input_df is None:
        return None

    pred = predictor.predecir(input_df)
    if pred is None:
        return None

    return PrediccionResponse(
        fecha=fecha,
        estacion=estacion,
        tmed=round(pred[0][0], 1),
        tmax=round(pred[0][1], 1),
        tmin=round(pred[0][2], 1),
        prec=round(pred[0][3], 1),
    )

def consultar_historico_por_fecha(fecha: datetime, estacion: str):
    try:
        df = pd.read_parquet(PARQUET_PATH)
        fila = df[
            (df["año"] == fecha.year) &
            (df["mes"] == fecha.month) &
            (df["dia"] == fecha.day)
        ]
        if fila.empty:
            return None

        fila = fila.iloc[0]
        return PrediccionResponse(
            fecha=fecha,
            estacion=estacion,
            tmed=fila["tmed"],
            tmax=fila["tmax"],
            tmin=fila["tmin"],
            prec=fila["prec"],
        )

    except Exception as e:
        print(f"❌ Error al consultar histórico: {e}")
        return None
