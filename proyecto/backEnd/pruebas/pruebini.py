import pandas as pd

df = pd.read_parquet("data/historico_limpio.parquet")

print(df.head())  # Ver las primeras filas
print(df.shape)   # Ver el número de filas y columnas
