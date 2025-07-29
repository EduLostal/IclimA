from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import PrediccionRequest, PrediccionResponse
from api.services import predecir_para_fecha_y_estacion, consultar_historico_por_fecha

from datetime import date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API de Predicción Meteorológica por estación y fecha"}

@app.post("/predict", response_model=PrediccionResponse)
def predecir(req: PrediccionRequest):
    resultado = predecir_para_fecha_y_estacion(req.fecha, req.estacion)
    if resultado is None:
        raise HTTPException(status_code=404, detail="No se pudo predecir con los datos disponibles")
    return resultado

@app.get("/historico", response_model=PrediccionResponse)
def consultar_historico(fecha: date = Query(...), estacion: str = Query(...)):
    resultado = consultar_historico_por_fecha(fecha, estacion)
    if resultado is None:
        raise HTTPException(status_code=404, detail="No hay datos históricos para esa fecha")
    return resultado
