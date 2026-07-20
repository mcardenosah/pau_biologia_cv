import os
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types

load_dotenv("api.env")
client = genai.Client()

class CriteriaRecovered(BaseModel):
    id: str = Field(description="El mismo ID de la pregunta que se te ha proporcionado (ej. q_19)")
    criteria_text: str = Field(description="El texto EXACTO y LITERAL de los criterios de corrección extraídos del PDF para esta pregunta. Si realmente no existe en el PDF, pon '(No disponibles en este examen)'")

class RecoverExtraction(BaseModel):
    results: List[CriteriaRecovered]

def process_year(year: str, questions: list) -> list:
    pdf_path = f"2002-2010/PAU_Biologia_{year}.pdf"
    if not os.path.exists(pdf_path):
        print(f"No se encuentra el PDF {pdf_path}")
        return []
        
    print(f"\n--- Procesando Año {year} ({len(questions)} preguntas) ---")
    print(f"Subiendo {pdf_path}...")
    try:
        uploaded_file = client.files.upload(file=pdf_path)
        while True:
            file_info = client.files.get(name=uploaded_file.name)
            if file_info.state == "ACTIVE":
                break
            elif file_info.state == "FAILED":
                print("Error: File failed to process.")
                return []
            time.sleep(2)
    except Exception as e:
        print(f"Error subiendo {pdf_path}: {e}")
        return []

    # Construir el prompt con la lista de preguntas
    q_list_text = "\n".join([f"ID: {q['id']}\nEnunciado: {q['question']}\n---" for q in questions])
    
    prompt = f"""
Eres un asistente experto. El documento adjunto es un examen de Biología de las Pruebas de Acceso a la Universidad (PAU).
Como sabes, en estos documentos los enunciados de los exámenes están al principio y las Soluciones / Criterios de Corrección están AGRUPADOS AL FINAL DEL DOCUMENTO.

Tu tarea es buscar en las páginas finales de este PDF y extraer EL TEXTO LITERAL del criterio de corrección oficial correspondiente a cada una de las preguntas de la siguiente lista.

Aquí tienes la lista de preguntas huérfanas:
{q_list_text}

IMPORTANTE: 
- El texto debe ser fiel al original del tribunal. No inventes respuestas.
- Devuelve un JSON donde cada objeto corresponda a un ID de la lista.
"""

    max_retries = 3
    result = []
    
    for attempt in range(max_retries):
        try:
            print(f"Generando contenido para {year}... (Intento {attempt+1})")
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[
                    uploaded_file,
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RecoverExtraction,
                    temperature=0.0
                )
            )
            if response.text:
                result = json.loads(response.text).get("results", [])
                print(f"¡Éxito! Extraídas {len(result)} respuestas para el año {year}.")
            break
        except Exception as e:
            print(f"Error en intento {attempt+1}: {e}")
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                print("Límite de cuota alcanzado. Esperando 65 segundos...")
                time.sleep(65)
            else:
                time.sleep(10)
                
    try:
        client.files.delete(name=uploaded_file.name)
    except Exception:
        pass
        
    return result

if __name__ == "__main__":
    json_path = "webapp/src/data_2002_2010.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Agrupar preguntas sin criterios por año
    missing_by_year = {}
    for q in data:
        if 'disponible' in (q.get('criteria') or '').lower():
            year = q.get('year')
            if year:
                if year not in missing_by_year:
                    missing_by_year[year] = []
                missing_by_year[year].append(q)
                
    print(f"Años con preguntas huérfanas: {list(missing_by_year.keys())}")
    
    # Procesar año por año
    updates_map = {}
    for year, qs in missing_by_year.items():
        results = process_year(year, qs)
        for r in results:
            updates_map[r['id']] = r['criteria_text']
            
        print("Esperando 10 segundos antes del siguiente año para no saturar la API...")
        time.sleep(10)
        
    # Actualizar la base de datos JSON
    updated_count = 0
    for q in data:
        q_id = q.get('id')
        if q_id in updates_map:
            new_criteria = updates_map[q_id]
            if "No disponible" not in new_criteria:
                q['criteria'] = new_criteria
                updated_count += 1
                
    # Guardar cambios
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nProceso finalizado. Se han recuperado e inyectado {updated_count} criterios en la base de datos.")
