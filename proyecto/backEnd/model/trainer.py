import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os
import json

class Trainer:
    def __init__(self, parquet_path: str, model_path: str, features_path: str):
        self.parquet_path = parquet_path
        self.model_path = model_path
        self.features_path = features_path

    def entrenar_modelo(self):
        try:
            print(f"Cargando datos desde {self.parquet_path}...")
            df = pd.read_parquet(self.parquet_path)

            print("Creando nuevas features (lags)...")
            # Crear variables del día anterior (lag 1)
            df = df.sort_values(by=["año", "mes", "dia"])  # Aseguramos orden temporal
            df["tmed_lag1"] = df["tmed"].shift(1)
            df["tmax_lag1"] = df["tmax"].shift(1)
            df["tmin_lag1"] = df["tmin"].shift(1)
            df["prec_lag1"] = df["prec"].shift(1)
        

            # Eliminamos la primera fila que tendrá NaN en los lags
            df = df.dropna().reset_index(drop=True)

            print("Preparando variables de entrada y salida...")
            variables_objetivo = ['tmed', 'tmax', 'tmin', 'prec']
            X = df.drop(columns=variables_objetivo)
            y = df[variables_objetivo]

            # Guardar el orden de las columnas
            feature_order = list(X.columns)
            with open(self.features_path, "w") as f:
                json.dump(feature_order, f)
            print(f"Orden de columnas guardado en {self.features_path}.")

            # Separar en entrenamiento y test (80% train / 20% test)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            print(f"Entrenando modelo sobre {X_train.shape[0]} muestras y {X_train.shape[1]} características...")
            modelo_base = RandomForestRegressor(
                n_estimators=300,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            modelo = MultiOutputRegressor(modelo_base)
            modelo.fit(X_train, y_train)

            # Métricas en conjunto de entrenamiento
            y_train_pred = modelo.predict(X_train)
            r2_train = r2_score(y_train, y_train_pred, multioutput='uniform_average')
            mae_train = mean_absolute_error(y_train, y_train_pred)

            print("Resultados en conjunto de entrenamiento:")
            print(f"R2 Score (train): {r2_train:.4f}")
            print(f"Mean Absolute Error (MAE train): {mae_train:.4f}")

            # Métricas en conjunto de test
            print("Evaluando modelo...")
            y_pred = modelo.predict(X_test)
            r2 = r2_score(y_test, y_pred, multioutput='uniform_average')
            mae = mean_absolute_error(y_test, y_pred)

            print(f"Resultados en conjunto de test:")
            print(f"R2 Score (test): {r2:.4f}")
            print(f"Mean Absolute Error (MAE test): {mae:.4f}")

            print(f"Guardando modelo en {self.model_path}...")
            joblib.dump(modelo, self.model_path)

            if os.path.exists(self.model_path):
                print(" Modelo entrenado y guardado correctamente.")
            else:
                print(" Error: El modelo no se ha guardado correctamente.")

        except Exception as e:
            print(f"Error durante el entrenamiento: {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    parquet_path = os.path.join(BASE_DIR, "data", "historico_limpio.parquet")
    model_path = os.path.join(BASE_DIR, "model", "modelo_entrenado.pkl")
    features_path = os.path.join(BASE_DIR, "model", "feature_order.json")

    trainer = Trainer(parquet_path, model_path, features_path)
    trainer.entrenar_modelo()
