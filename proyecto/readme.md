# IclimA - Predicción Meteorológica por IA

Este proyecto permite consultar predicciones meteorológicas para una estación concreta (Madrid, Retiro - IDEMA: 3195), utilizando un modelo de machine learning entrenado con datos históricos de AEMET. La predicción se realiza desde un frontend sencillo en React que se comunica con una API construida en FastAPI.

---

## Requisitos

### Backend 

- Python 3.10
- Anaconda (recomendado)
- Entorno con las siguientes dependencias:

```bash
conda create -n prediccion_meteo python=3.10
conda activate prediccion_meteo
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```
fastapi
uvicorn
pandas
scikit-learn
joblib
python-dotenv
requests
pyarrow
```

### Frontend (React)

- Node.js 
- npm 

Instalación de dependencias:

```bash
npm install
```

---

## Estructura del Proyecto

```
proyecto/
│
├── backEnd/
│   ├── api/
│   │   ├── main.py
│   │   ├── services.py
│   │   └── schemas.py
│   ├── model/
│   │   ├── predictor.py
│   │   ├── trainer.py
│   │   └── feature_order.json
│   ├── aemet/
│   │   ├── daysCheck.py
│   │   ├── downloader.py
│   │   └── formatter.py
│   ├── data/
│   │   ├── historico_raw_madrid.json
│   │   └── historico_limpio.parquet
│   │
│   │
│   └── requirements.txt
│
└── frontEnd/
    ├── src/
    │   ├── App.jsx
    │   ├── index.css
    │   └── assets/logoIclimA.png
    └── package.json
```

---

## Ejecución

### 1. Backend

```bash
cd backEnd
uvicorn api.main:app --reload
```

- Asegúrate de tener configurado el archivo `.env` con tu clave de API de AEMET:

```
API_KEY=tu_clave_de_aemet
```

### 2. Frontend

```bash
cd frontEnd
cd prediccion-meteo
npm run dev
```

---

## Notas importantes

### CORS y conexión frontend-backend

El backend FastAPI tiene habilitado CORS con:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Esto permite que el frontend (en otro puerto) pueda comunicarse sin restricciones con la API.

### Limitaciones de datos

- Los datos de AEMET se actualizan con una demora habitual de 2-3 días.
- Si se solicita una predicción para una fecha futura y no existen datos reales del día anterior, se utilizarán los datos más recientes disponibles (dentro de los últimos 7 días). Esto puede reducir la precisión de la predicción.

