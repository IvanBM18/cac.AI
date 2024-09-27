from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import json
from sklearn.linear_model import LinearRegression

app = FastAPI()


# Modelo para recibir datos
class RegressionData(BaseModel):
    submissions_totales: list[int]
    promedio_respuestas: list[float]
    submissions_correctas: list[int]
    nuevo_dato: list[float]  # Para la predicción

@app.get("/predict/")
def predict(data: RegressionData):
    
    # Convertir datos de entrada a arrays numpy
    X = np.column_stack((data.submissions_totales, data.promedio_respuestas))
    y = np.array(data.submissions_correctas)

    # Crear y entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)

    # Realizar la predicción
    prediccion = model.predict(np.array([data.nuevo_dato]))[0]

    # Calcular la malla para la superficie de regresión
    x_values = np.linspace(min(data.submissions_totales), max(data.submissions_totales), 100)
    y_values = np.linspace(min(data.promedio_respuestas), max(data.promedio_respuestas), 100)
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

# Para correr el servidor: uvicorn main:app --reload
