from pydantic import BaseModel
from datetime import date

class PrediccionRequest(BaseModel):
    fecha: date
    estacion: str 

class PrediccionResponse(BaseModel):
    fecha: date
    estacion: str
    tmed: float
    tmax: float
    tmin: float
    prec: float
