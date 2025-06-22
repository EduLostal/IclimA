import pandas as pd
import json
import os

class DataConverter:
    def __init__(self, json_path: str, parquet_path: str):
        self.json_path = json_path
        self.parquet_path = parquet_path

    def json_to_parquet(self):
        try:
            print(f"Cargando JSON desde {self.json_path}...")
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            print("Convirtiendo a DataFrame...")
            df = pd.DataFrame(data)

            # Reemplazar valores no numéricos en columnas numéricas
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

            # Convertir columnas enteras (int)
            columnas_int = ['altitud', 'dir']
            for col in columnas_int:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Limpiar columnas con posibles valores tipo "Varias"
            columnas_horas = ['horatmin', 'horatmax', 'horaracha', 'horaPresMax', 'horaPresMin']
            for col in columnas_horas:
                if col in df.columns:
                    df[col] = df[col].replace("Varias", pd.NA)

            print(f"Guardando en formato Parquet: {self.parquet_path}")
            df.to_parquet(self.parquet_path, index=False)
            print("Conversión completada con éxito.")
        except Exception as e:
            print(f"Error en la conversión JSON → Parquet: {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = os.path.join(BASE_DIR, "data", "historico_raw_madrid.json")
    parquet_path = os.path.join(BASE_DIR, "data", "historico_limpio.parquet")

    converter = DataConverter(json_path, parquet_path)
    converter.json_to_parquet()
