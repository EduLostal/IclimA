import pandas as pd
import json
import os

class Formatter:
    def __init__(self, json_path: str, parquet_path: str):
        self.json_path = json_path
        self.parquet_path = parquet_path

    def procesar_datos(self):
        try:
            print(f"Cargando JSON desde {self.json_path}...")
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            print("Convirtiendo a DataFrame...")
            df = pd.DataFrame(data)

            # 1. Convertir números con coma en decimales
            columnas_float = [
                'tmed', 'prec', 'tmin', 'tmax', 'velmedia', 'racha',
                'presMax', 'presMin', 'sol', 'hrMedia'
            ]
            for col in columnas_float:
                if col in df.columns:
                    df[col] = (
                        df[col]
                        .replace({"Ip": None, "": None, "-": None})
                        .str.replace(",", ".", regex=False)
                        .astype(float)
                    )

            # 2. Convertir columnas enteras (int)
            columnas_int = ['altitud', 'dir']
            for col in columnas_int:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 3. Procesar fecha
            if "fecha" in df.columns:
                df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
                df["año"] = df["fecha"].dt.year
                df["mes"] = df["fecha"].dt.month
                df["dia"] = df["fecha"].dt.day
                df["dia_del_año"] = df["fecha"].dt.dayofyear
                df["dia_semana"] = df["fecha"].dt.weekday

            # 4. Eliminar columnas no predictoras
            columnas_no_utiles = ['nombre', 'provincia', 'indicativo', 'fecha']
            df = df.drop(columns=[col for col in columnas_no_utiles if col in df.columns])

            # 5. Eliminar columnas de horas (incluyendo hrMax, horaHrMax, hrMin, horaHrMin)
            columnas_horas = [
                'horatmin', 'horatmax', 'horaracha', 'horaPresMax', 'horaPresMin',
                'hrMax', 'horaHrMax', 'hrMin', 'horaHrMin'
            ]
            df = df.drop(columns=[col for col in columnas_horas if col in df.columns])

            # 6. Rellenar NaN SOLO en columnas numéricas
            for col in df.select_dtypes(include=['float64', 'int64']).columns:
                df[col] = df[col].fillna(df[col].mean())

            # 7. Guardar resultado
            print(f"Guardando en formato Parquet en {self.parquet_path}...")
            df.to_parquet(self.parquet_path, index=False)
            print("Conversión y limpieza completadas con éxito.")

        except Exception as e:
            print(f"Error en el formateo de datos: {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = os.path.join(BASE_DIR, "data", "historico_raw_madrid.json")
    parquet_path = os.path.join(BASE_DIR, "data", "historico_limpio.parquet")

    formatter = Formatter(json_path, parquet_path)
    formatter.procesar_datos()
