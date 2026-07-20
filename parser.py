import os
import json
import time
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

class ExamQuestion(BaseModel):
    thematic_block_id: int = Field(description="ID del bloque del 1 al 5: 1 (Components), 2 (Metabolisme), 3 (Citologia), 4 (Genètica), 5 (Microorganismes)")
    year: int = Field(description="Año del examen")
    month: str = Field(description="Mes o convocatoria (Junio, Julio, Septiembre, etc.)")
    option: str = Field(description="Opción A o B, si aplica")
    question_text: str = Field(description="Texto del enunciado de la pregunta")
    criteria_text: str = Field(description="Texto de los criterios de corrección asociados a esta pregunta. Si no hay, dejar vacío.")

class ExamExtraction(BaseModel):
    questions: List[ExamQuestion]

SYSTEM_INSTRUCTION = """
Eres un asistente experto en biología y procesamiento de documentos.
Tu tarea es extraer TODAS las preguntas y sus correspondientes criterios de corrección de los exámenes PAU de Biología.
El documento (PDF) contiene los enunciados de los exámenes, los criterios de corrección, o ambos entrelazados o separados.

Para cada pregunta extrae:
- thematic_block_id: Clasifica la pregunta en uno de estos 5 bloques temáticos (1 al 5):
  1: Base molecular y fisicoquímica de la vida (Biomoléculas, glúcidos, lípidos, proteínas, ácidos nucleicos, enzimas)
  2: Metabolismo (Respiración celular, fotosíntesis, fermentación, catabolismo, anabolismo)
  3: Citología / Estructura celular (Orgánulos, membrana, núcleo, transporte, mitosis, meiosis)
  4: Genética (Herencia, genética mendeliana y molecular, replicación, transcripción, traducción, mutaciones)
  5: Microbiología e Inmunología (Bacterias, virus, anticuerpos, respuesta inmunitaria, biotecnología)
- year: Año (ej. 2008)
- month: Convocatoria (ej. Junio, Julio, Septiembre)
- option: Opción A o B
- question_text: Texto completo del enunciado, sin traducir.
- criteria_text: Texto completo de los criterios de corrección de ESA pregunta específica, sin traducir.

Asegúrate de NO dejarte ninguna pregunta. Empareja correctamente cada pregunta con su criterio aunque estén en páginas distintas.
"""

def extract_pdf(pdf_path: str) -> list[dict]:
    print(f"Uploading {pdf_path}...")
    uploaded_file = client.files.upload(file=pdf_path)
    print(f"File uploaded: {uploaded_file.name}. Generando JSON...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[
                    uploaded_file,
                    "Extrae todas las preguntas y sus criterios de corrección de este documento. Devuelve el resultado en JSON estructurado."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=ExamExtraction,
                    temperature=0.0
                )
            )
            client.files.delete(name=uploaded_file.name)
            
            # The API returns raw JSON
            return json.loads(response.text)["questions"]
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                client.files.delete(name=uploaded_file.name)
                raise e
            time.sleep(20)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = extract_pdf(sys.argv[1])
        with open("output_temp.json", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
        print("Extraction saved to output_temp.json")
