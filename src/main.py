from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import json
from sklearn.linear_model import LinearRegression

app = FastAPI()


# Modelo para recibir datos
class RegressionData(BaseModel):
    submissionTotals: list[int]
    avgCorrect: list[float]
    correctSubmissions: list[int]
    newContest: list[float]  # Para la predicción
    
class ContestData(BaseModel):
    name : str
    total: int
    correct: float

@app.get("/predict/data")
def predict(data: RegressionData):
    
    # Convertir datos de entrada a arrays numpy
    X = np.column_stack((data.submissionTotals, data.avgCorrect))
    y = np.array(data.correctSubmissions)

    # Crear y entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)

    # Realizar la predicción
    print(f"Nuevo dato: {data.newContest}")
    prediccion = model.predict(np.array([data.newContest]))[0]
    print(f"Predicción para el nuevo dato: {prediccion}")


    # Calcular la malla para la superficie de regresión
    x_values = np.linspace(min(data.submissionTotals), max(data.submissionTotals), 100)
    y_values = np.linspace(min(data.avgCorrect), max(data.avgCorrect), 100)
    X_grid, Y_grid = np.meshgrid(x_values, y_values)
    Z_grid = model.predict(np.column_stack((X_grid.ravel(), Y_grid.ravel())))

    # Crear el JSON de respuesta
    response = {
        "prediccion": prediccion,
        "malla": {
            "x": X_grid.flatten().tolist(),
            "y": Y_grid.flatten().tolist(),
            "z": Z_grid.flatten().tolist()
        }
    }
    return response

@app.get("/predict/contest")
def predict_contest(data: list[ContestData]):

    if(len(data) < 5):
        return {"error": "Not enough data"}
    totalCount : int = 0
    contestCount : int = 0
    correctCount : int = 0
    
    submissionTotals : list[int] = []
    avgCorrect : list[float] = []
    correctSubmissions : list[int] = []
    newContest : list[str] = []
    
    for index,contest in enumerate(data):
        submissionTotals.append(totalCount)
        
        if(contestCount == 0):
            avgCorrect.append(0)
        else:
            avgCorrect.append(correctCount/(contestCount))
        correctSubmissions.append(contest.correct)
        
        totalCount += contest.total
        correctCount += contest.correct
        contestCount += 1
    
    mapedData : RegressionData = RegressionData(
        submissionTotals=submissionTotals, 
        avgCorrect=avgCorrect, 
        correctSubmissions=correctSubmissions, 
        newContest=[totalCount, correctCount/contestCount])
    
    print(mapedData)
    
    return predict(mapedData)
# Para correr el servidor: uvicorn main:app --reload
