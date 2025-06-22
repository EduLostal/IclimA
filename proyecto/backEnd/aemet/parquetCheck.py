import pandas as pd

# Ruta al parquet generado
df = pd.read_parquet("data/historico_limpio.parquet")

# Ver las primeras filas
print(df.head())

# Ver tamaño del dataset
print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
