import pandas as pd
from io import BytesIO
from fastapi import Response
from jinja2 import Template
from xhtml2pdf import pisa
from pathlib import Path

def generate_excel_report(weather_data):
    # Generar el archivo Excel en memoria
    buffer = BytesIO()
    df = pd.DataFrame(weather_data["weather_data"])
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Clima")
    buffer.seek(0)
    # Enviar el archivo Excel al cliente
    return Response(
        buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=weather_data.xlsx"}
    )

def generate_csv_report(weather_data):
    # Generar el archivo CSV en memoria
    buffer = BytesIO()
    df = pd.DataFrame(weather_data["weather_data"])
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    # Enviar el archivo CSV al cliente
    return Response(
        buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_data.csv"}
    )

def generate_pdf_report(weather_data):
    # Preparar los datos para la plantilla
    weather_data_prepared = {
        "city": weather_data["city"],
        "latitude": weather_data["latitude"],
        "longitude": weather_data["longitude"],
        "weather_data": [
            {
                "time": time,
                "temperature_2m": temp,
                "relative_humidity_2m": humidity,
                "rain": rain
            }
            for time, temp, humidity, rain in zip(
                weather_data["weather_data"]["time"],
                weather_data["weather_data"]["temperature_2m"],
                weather_data["weather_data"]["relative_humidity_2m"],
                weather_data["weather_data"]["rain"]
            )
        ]
    }

    # Cargar la plantilla HTML desde el archivo externo
    template_path = Path("views/pdf_template.html")
    html_template = template_path.read_text(encoding="utf-8")
    template = Template(html_template)
    rendered_html = template.render(weather=weather_data_prepared)

    # Convertir el HTML a PDF con xhtml2pdf
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_buffer)
    if pisa_status.err:
        return {"error": "Error al generar el PDF"}
    pdf_buffer.seek(0)
    
    # Enviar el archivo PDF al cliente
    return Response(
        pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=weather_data.pdf"}
    )