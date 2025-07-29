import os
import json
import joblib
import numpy as np
import matplotlib.pyplot as plt


def mostrar_importancia_variables(model_path, features_path):
    import joblib
    import json

    # Cargar modelo y orden de columnas
    modelo = joblib.load(model_path)
    with open(features_path, "r") as f:
        columnas = json.load(f)

    # Comprobación
    if not hasattr(modelo, "estimators_"):
        print("❌ El modelo cargado no tiene estimadores individuales.")
        return

    # Para cada salida, extraer importancias
    salidas = ['tmed', 'tmax', 'tmin', 'prec']
    importancias_por_salida = {}

    for i, est in enumerate(modelo.estimators_):
        importancias = est.feature_importances_
        importancias_por_salida[salidas[i]] = importancias

    # Calcular media global
    media_importancia = np.mean(
        [importancias_por_salida[salida] for salida in salidas],
        axis=0
    )

    # Orden descendente por importancia
    indices_ordenados = np.argsort(media_importancia)[::-1]
    columnas_ordenadas = [columnas[i] for i in indices_ordenados]
    importancias_ordenadas = media_importancia[indices_ordenados]

    # Gráfico
    plt.figure(figsize=(12, 6))
    plt.bar(columnas_ordenadas, importancias_ordenadas)
    plt.xticks(rotation=45, ha="right")
    plt.title("Importancia media de cada variable en el modelo")
    plt.ylabel("Importancia relativa")
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.show()

# Llama a la función con tus rutas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
model_path = os.path.join(BASE_DIR, "model", "modelo_entrenado.pkl")
features_path = os.path.join(BASE_DIR, "model", "feature_order.json")

mostrar_importancia_variables(model_path, features_path)
