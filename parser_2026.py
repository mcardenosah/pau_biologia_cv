import os
import json
import time
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

class ExamQuestion(BaseModel):
    block: str = Field(description="Número y título del bloque temático (ej. '1-COMPONENTS', '2-METABOLISME', '3-CITOLOGIA', '4-GENETICA', '5-MICROORGANISMES')")
    year: str = Field(description="Año del examen, ej. '2026'")
    month: str = Field(description="Mes o convocatoria, ej. 'Junio'")
    option: str = Field(description="Opción A o B")
    question: str = Field(description="Texto completo del enunciado de la pregunta")
    criteria: str = Field(description="Texto completo de los criterios de corrección para esta pregunta")

class ExamExtraction(BaseModel):
    questions: list[ExamQuestion]

SYSTEM_INSTRUCTION = """
Eres un asistente experto en biología y procesamiento de documentos.
Tu tarea es extraer TODAS las preguntas y sus correspondientes criterios de corrección del examen PAU de Biología.
El documento contiene los enunciados y a continuación los criterios.

Para cada pregunta extrae:
- block: Clasifica la pregunta en uno de estos 5 bloques: 1-COMPONENTS, 2-METABOLISME, 3-CITOLOGIA, 4-GENETICA, 5-MICROORGANISMES.
- year: 2026
- month: Junio
- option: Opción A o B
- question: Texto completo del enunciado.
- criteria: Texto completo de los criterios de corrección de ESA pregunta específica.

Asegúrate de emparejar correctamente cada pregunta con su criterio. No resumas el texto, extraelo tal cual.
"""

def main():
    pdf_path = "2026/BIO junio 2026.pdf"
    print(f"Subiendo {pdf_path} a Gemini...")
    uploaded_file = client.files.upload(file=pdf_path)
    
    while True:
        info = client.files.get(name=uploaded_file.name)
        if info.state == "ACTIVE":
            break
        elif info.state == "FAILED":
            print("Error procesando archivo.")
            return
        time.sleep(2)
        
    print("Extrayendo preguntas...")
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[uploaded_file, "Extrae todas las preguntas y sus criterios de corrección. Devuelve un JSON estructurado."],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ExamExtraction,
            temperature=0.0
        )
    )
    
    questions = json.loads(response.text).get("questions", [])
    
    # Añadir id e imagen vacía
    for i, q in enumerate(questions):
        q['id'] = f"2026_{q['month']}_{q['option']}_{i+1}"
        q['image'] = ""
        
    with open("data_2026.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        
    try:
        client.files.delete(name=uploaded_file.name)
    except:
        pass
        
    print(f"¡Éxito! Se han extraído {len(questions)} preguntas a data_2026.json")

if __name__ == "__main__":
    main()
