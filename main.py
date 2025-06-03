import os
from fastapi import FastAPI, Response
import uvicorn
import pandas as pd
from io import BytesIO
from jinja2 import Template
from xhtml2pdf import pisa
from utils.api_client import fetch_weather_data  # Importar la función desde el archivo auxiliar
from pathlib import Path

from utils.report_generator import generate_csv_report, generate_excel_report, generate_pdf_report

app = FastAPI()

@app.get("/weather/{city}")
async def get_weather(city: str):
    try:
        weather_data = await fetch_weather_data(city)
        return weather_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/weather/{city}/excel")
async def get_weather_excel(city: str):
    try:
        weather_data = await fetch_weather_data(city)
        return generate_excel_report(weather_data)
    except Exception as e:
        return {"error": str(e)}

@app.get("/weather/{city}/csv")
async def get_weather_csv(city: str):
    try:
        weather_data = await fetch_weather_data(city)
        return generate_csv_report(weather_data)
    except Exception as e:
        return {"error": str(e)}

@app.get("/weather/{city}/pdf")
async def get_weather_pdf(city: str):
    try:
        weather_data = await fetch_weather_data(city)
        return generate_pdf_report(weather_data)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
