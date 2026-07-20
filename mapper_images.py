import os
import fitz
import glob
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from difflib import SequenceMatcher

load_dotenv("api.env")
client = genai.Client()

class ImageMapping(BaseModel):
    page_number: int = Field(description="Número de página física en el PDF (1-indexed) donde aparece la imagen didáctica.")
    description: str = Field(description="Breve descripción de la imagen (ej. 'Esquema del ciclo de Krebs').")
    question_snippet: str = Field(description="Las primeras 5-10 palabras del enunciado de la pregunta exacta a la que pertenece esta imagen.")

class ExamImages(BaseModel):
    images: List[ImageMapping]

def extract_images_from_pdf(pdf_path: str, output_dir: str):
    """Extrae las imágenes de un PDF usando PyMuPDF y las guarda."""
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    extracted_data = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        valid_images = []
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image["width"]
            height = base_image["height"]
            
            if width < 150 or height < 150:
                continue
                
            img_filename = f"{os.path.basename(pdf_path).replace('.pdf', '')}_p{page_num+1}_i{img_index}.{image_ext}"
            img_filepath = os.path.join(output_dir, img_filename)
            
            with open(img_filepath, "wb") as f:
                f.write(image_bytes)
                
            valid_images.append(img_filename)
            
        if valid_images:
            extracted_data[page_num + 1] = valid_images
            
    return extracted_data

def ask_gemini_for_mapping(pdf_path: str):
    """Sube el PDF a Gemini y le pide que identifique las páginas con imágenes y sus enunciados."""
    try:
        uploaded_file = client.files.upload(file=pdf_path)
        while True:
            info = client.files.get(name=uploaded_file.name)
            if info.state == "ACTIVE": break
            if info.state == "FAILED": return []
            time.sleep(2)
            
        instruction = "Eres un asistente experto. Revisa visualmente este PDF de examen de Biología. Identifica todas las gráficas, dibujos, esquemas metabólicos o células (imágenes didácticas). IGNORA logos institucionales o escudos. Devuelve un JSON detallando en qué PÁGINA (empezando por 1) está cada imagen, una breve descripción, y un fragmento (las primeras 10 palabras) del enunciado de la pregunta a la que pertenece."
        
        print("Esperando la respuesta de la IA...")
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[uploaded_file, "Identifica las imágenes didácticas y sus enunciados."],
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                response_mime_type="application/json",
                response_schema=ExamImages,
                temperature=0.0
            )
        )
        
        client.files.delete(name=uploaded_file.name)
        
        if response.text:
            return json.loads(response.text).get("images", [])
        return []
        
    except Exception as e:
        print(f"Error con Gemini en {pdf_path}: {e}")
        return []

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def update_json_with_images(json_path: str, year: str, mapping_data: list, local_images: dict):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in mapping_data:
        snippet = item['question_snippet']
        page = item['page_number']
        
        if page not in local_images or not local_images[page]:
            continue
            
        img_filename = local_images[page][0] # Cogemos la primera imagen válida de la página
        img_url = f"/imagenes_extraidas/{img_filename}"
        
        best_match = None
        best_ratio = 0
        
        for q in data:
            if q.get('year') == year:
                # Extraemos las primeras palabras para comparar
                q_text = q['question']
                ratio = similar(snippet[:50], q_text[:50])
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = q
                    
        if best_match and best_ratio > 0.4:
            print(f"   => Emparejado: '{snippet}' -> Pregunta: {best_match['id']} (Certeza: {best_ratio:.2f})")
            best_match['image'] = img_url
            
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    folder = "2002-2010"
    pdfs = glob.glob(f"{folder}/*.pdf")
    img_dir = "webapp/public/imagenes_extraidas"
    json_path = "webapp/src/data_2002_2010.json"
    
    print("Iniciando extracción y mapeo híbrido para 2002-2010...")
    
    for pdf in pdfs:
        year = os.path.basename(pdf).replace("PAU_Biologia_", "").replace(".pdf", "")
        print(f"\nProcesando {pdf} (Año {year})")
        print("1. Extrayendo imágenes físicas con PyMuPDF...")
        local_images = extract_images_from_pdf(pdf, img_dir)
        print(f"Imágenes encontradas en las páginas: {list(local_images.keys())}")
        
        if not local_images:
            print("No hay imágenes grandes en este examen. Saltando IA.")
            continue
            
        print("2. Consultando a Gemini-1.5-Pro para mapear...")
        ai_mapping = ask_gemini_for_mapping(pdf)
        
        print("3. Inyectando en la Base de Datos JSON...")
        update_json_with_images(json_path, year, ai_mapping, local_images)
        
        print("Esperando 10s para no saturar...")
        time.sleep(10)
        
    print("\n¡PROCESO DE IMÁGENES COMPLETADO!")
