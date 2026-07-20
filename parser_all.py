import os
import json
import time
import glob
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
  1: Base molecular y fisicoquímica de la vida
  2: Metabolismo
  3: Citología / Estructura celular
  4: Genética
  5: Microbiología e Inmunología
- year: Año (ej. 2008)
- month: Convocatoria (ej. Junio, Julio, Septiembre)
- option: Opción A o B
- question_text: Texto completo del enunciado, sin traducir.
- criteria_text: Texto completo de los criterios de corrección de ESA pregunta específica, sin traducir.

Asegúrate de NO dejarte ninguna pregunta. Empareja correctamente cada pregunta con su criterio aunque estén en páginas distintas.
"""

def extract_pdf(pdf_path: str) -> list[dict]:
    print(f"Subiendo {pdf_path}...")
    try:
        uploaded_file = client.files.upload(file=pdf_path)
        # Wait for file to be active
        while True:
            file_info = client.files.get(name=uploaded_file.name)
            if file_info.state == "ACTIVE":
                break
            elif file_info.state == "FAILED":
                print(f"File failed to process.")
                return []
            time.sleep(2)
    except Exception as e:
        print(f"Error subiendo {pdf_path}: {e}")
        return []
    
    max_retries = 3
    result = []
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
            
            if response.text:
                result = json.loads(response.text).get("questions", [])
            break
            
        except Exception as e:
            print(f"Intento {attempt+1} fallido en {pdf_path}: {e}")
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                print("Límite de cuota alcanzado. Esperando 65 segundos...")
                time.sleep(65)
            else:
                time.sleep(10)
            
    # Always try to delete at the end safely
    try:
        client.files.delete(name=uploaded_file.name)
    except Exception:
        pass
        
    return result

def generate_markdown(folder_path: str, questions: list):
    # Sort by block, then year, then month
    questions.sort(key=lambda x: (x.get('thematic_block_id', 0), x.get('year', 0), x.get('month', ''), x.get('option', '')))
    
    blocks = {
        1: "ELS COMPONENTS QUÍMICS DE LA CÈL·LULA",
        2: "METABOLISME",
        3: "CITOLOGIA",
        4: "GENÈTICA",
        5: "MICROORGANISMES I IMMUNITAT"
    }
    
    md_content = f"# Recopilatorio Exámenes PAU Biología - {folder_path}\\n\\n"
    current_block = -1
    
    for q in questions:
        b_id = q.get('thematic_block_id')
        if b_id != current_block:
            current_block = b_id
            block_title = blocks.get(b_id, "OTROS")
            md_content += f"\\n## BLOQUE {b_id} - {block_title}\\n\\n"
            
        md_content += f"**({q.get('year')} {q.get('month')}, Opción {q.get('option')})**\\n\\n"
        md_content += f"> **Pregunta:** {q.get('question_text')}\\n>\\n"
        crit = q.get('criteria_text', '').strip()
        if crit:
            md_content += f"> **Criterios de corrección:** {crit}\\n\\n"
        else:
            md_content += f"> **Criterios de corrección:** *(No disponibles en este examen)*\\n\\n"
        md_content += "---\\n\\n"
            
    out_file = f"Recopilatorio_{os.path.basename(folder_path)}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Archivo generado: {out_file}")

if __name__ == "__main__":
    folders = ["2015-2019", "2020-2025"]
    
    for folder in folders:
        print(f"\\n--- PROCESANDO CARPETA {folder} ---")
        pdfs = glob.glob(f"{folder}/*.pdf")
        all_questions = []
        for pdf in pdfs:
            print(f"Procesando {pdf}...")
            qs = extract_pdf(pdf)
            all_questions.extend(qs)
            time.sleep(5) # Pequeña pausa
            
        if all_questions:
            generate_markdown(folder, all_questions)
        else:
            print(f"No se extrajeron preguntas de {folder}")
        
    print("\\n¡PROCESO COMPLETADO! Se han generado todos los recopilatorios.")
