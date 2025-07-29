import pandas as pd
import joblib
import os
import json
from datetime import datetime, timedelta

class Predictor:
    def __init__(self, model_path: str, parquet_path: str, features_path: str):
        self.model_path = model_path
        self.parquet_path = parquet_path
        self.features_path = features_path
        self.modelo = None
        self.df = None
        self.orden_columnas = None

    def cargar_modelo_y_datos(self):
        print(f"Cargando modelo desde {self.model_path}...")
        self.modelo = joblib.load(self.model_path)

        print(f"Cargando datos históricos desde {self.parquet_path}...")
        self.df = pd.read_parquet(self.parquet_path)

        print(f"Cargando orden correcto de columnas desde {self.features_path}...")
        with open(self.features_path, "r") as f:
            self.orden_columnas = json.load(f)

        print("Modelo, datos y orden de columnas cargados correctamente.\n")

    def preparar_input(self, fecha_prediccion: datetime):
        if self.df is None:
            raise ValueError("Debes cargar los datos primero.")

        # Buscar el dato más cercano posible hacia atrás 
        encontrado = False
        dias_retroceso = 1

        while dias_retroceso <= 7: #Máximo 7 días
            fecha_busqueda = fecha_prediccion - timedelta(days=dias_retroceso)
            print(f"Buscando datos de {fecha_busqueda.strftime('%Y-%m-%d')} para predecir {fecha_prediccion.strftime('%Y-%m-%d')}...")

            fila_lag = self.df[
                (self.df["año"] == fecha_busqueda.year) &
                (self.df["mes"] == fecha_busqueda.month) &
                (self.df["dia"] == fecha_busqueda.day)
            ]

            if not fila_lag.empty:
                fila_lag = fila_lag.iloc[0]
                encontrado = True
                break

            dias_retroceso += 1

        if not encontrado:
            print("❌ No se encontraron datos en los últimos 30 días.")
            return None

        entrada = {
            "altitud": fila_lag["altitud"],
            "dir": fila_lag["dir"],
            "velmedia": fila_lag["velmedia"],
            "presMax": fila_lag["presMax"],
            "presMin": fila_lag["presMin"],
            "sol": fila_lag["sol"],
            "hrMedia": fila_lag["hrMedia"],
            "racha": fila_lag["racha"],
            "tmed_lag1": fila_lag["tmed"],
            "tmax_lag1": fila_lag["tmax"],
            "tmin_lag1": fila_lag["tmin"],
            "prec_lag1": fila_lag["prec"],
            "año": fecha_prediccion.year,
            "mes": fecha_prediccion.month,
            "dia": fecha_prediccion.day,
            "dia_del_año": fecha_prediccion.timetuple().tm_yday,
            "dia_semana": fecha_prediccion.weekday()
        }


        input_df = pd.DataFrame([entrada])

        # Reordenar columnas
        input_df = input_df[self.orden_columnas]

        return input_df

    def predecir(self, input_df: pd.DataFrame):
        if self.modelo is None:
            raise ValueError("Debes cargar el modelo primero.")
        if input_df is None:
            print("No hay datos de entrada. No se puede predecir.")
            return None

        prediccion = self.modelo.predict(input_df)
        return prediccion

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_path = os.path.join(BASE_DIR, "model", "modelo_entrenado.pkl")
    parquet_path = os.path.join(BASE_DIR, "data", "historico_limpio.parquet")
    features_path = os.path.join(BASE_DIR, "model", "feature_order.json")

    predictor = Predictor(model_path, parquet_path, features_path)
    predictor.cargar_modelo_y_datos()

    # Definir la fecha que quieres predecir
    fecha_prediccion = datetime(2025, 4, 28)  

    input_df = predictor.preparar_input(fecha_prediccion)

    if input_df is not None:
        prediccion = predictor.predecir(input_df)
        if prediccion is not None:
            print(f"\nPredicción para {fecha_prediccion.strftime('%Y-%m-%d')}:")
            print(f"tmed (ºC): {prediccion[0][0]:.2f}")
            print(f"tmax (ºC): {prediccion[0][1]:.2f}")
            print(f"tmin (ºC): {prediccion[0][2]:.2f}")
            print(f"prec (mm): {prediccion[0][3]:.2f}")
    else:
        print("No se pudo preparar entrada para el modelo.")
