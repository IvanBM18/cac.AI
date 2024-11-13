from pydantic import BaseModel
from typing import Optional

# Modelo para recibir datos
class RegressionData(BaseModel):
    avgDifficulty: list[float]
    avgCorrect: list[float]
    correctSubmissions: list[int]
    newContest: list[float]  # Para la predicción