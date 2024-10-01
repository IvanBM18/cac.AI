from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import numpy as np
import json
from sklearn.linear_model import LinearRegression

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelo para recibir datos
class RegressionData(BaseModel):
    avgDifficulty: list[float]
    avgCorrect: list[float]
    correctSubmissions: list[int]
    newContest: list[float]  # Para la predicción
    
class ContestData(BaseModel):
    name : str
    total: Optional[int] = None
    correct: Optional[float] = None
    difficulty: float

@app.get("/predict/data")
def predict(data: RegressionData):
    
    # Convertir datos de entrada a arrays numpy
    X = np.column_stack((data.avgDifficulty, data.avgCorrect))
    y = np.array(data.correctSubmissions)

    # Crear y entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)

    # Realizar la predicción
    print(f"Nuevo dato: {data.newContest}")
    prediccion = model.predict(np.array([data.newContest]))[0]
    print(f"Predicción para el nuevo dato: {prediccion}")


    # Calcular la malla para la superficie de regresión
    x_values = np.linspace(min(data.avgDifficulty), max(data.avgDifficulty), 100)
    y_values = np.linspace(min(data.avgCorrect), max(data.avgCorrect), 100)
    X_grid, Y_grid = np.meshgrid(x_values, y_values)
    Z_grid = model.predict(np.column_stack((X_grid.ravel(), Y_grid.ravel()))).reshape(X_grid.shape)

    # Crear el JSON de respuesta
    response = {
        "input": data.newContest,
        "output": prediccion,
        "malla": {
            "x": X_grid.tolist(),
            "y": Y_grid.tolist(),
            "z": Z_grid.tolist()
        }
    }
    return response

@app.get("/predict/contest")
def predict_contest(data: list[ContestData]):

    if(len(data) < 5):
        return {"error": "Not enough data"}
    
    contestCount : int = 0
    correctCount : int = 0
    totalDifficulty : float = 0
    
    avgCorrect : list[float] = []
    avgDifficulty : list[float] = []
    correctSubmissions : list[int] = []
    
    for index,contest in enumerate(data):
        
        if(contestCount == 0):
            avgCorrect.append(0)
            avgDifficulty.append(0)
        else:
            avgCorrect.append(correctCount/(contestCount))
            avgDifficulty.append(totalDifficulty/(contestCount))
        correctSubmissions.append(contest.correct if contest.correct != None else 0)
        
        #If contestsDifficulty is null, set it to 0
        totalDifficulty += contest.difficulty if contest.difficulty != None else 0
        correctCount += contest.correct if contest.correct != None else 0
        contestCount += 1
    
    mapedData : RegressionData = RegressionData(
        avgDifficulty=avgDifficulty, 
        avgCorrect=avgCorrect, 
        correctSubmissions=correctSubmissions, 
        newContest=[totalDifficulty/contestCount, correctCount/contestCount])
    
    print(mapedData)
    
    return predict(mapedData)
# Para correr el servidor: uvicorn main:app --reload
