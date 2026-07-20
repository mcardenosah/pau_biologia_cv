import os
import json
import glob
import PIL.Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import re

# Buscar API Key en .env o api.env
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    for env_file in ['.env', 'api.env']:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if 'GEMINI_API_KEY' in line or 'GOOGLE_API_KEY' in line:
                        api_key = line.split('=')[1].strip()
                        break
        if api_key: break

if not api_key:
    print("NO SE ENCONTRÓ LA CLAVE DE API EN .env NI api.env")
    exit(1)

genai.configure(api_key=api_key)

with open('webapp/src/data_2020_2025.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Filtrar un poco las preguntas para no exceder tokens (solo año y extracto)
q_simple = [{"id": q["id"], "year": q["year"], "text": q["question"][:200]} for q in questions]

image_files = glob.glob('webapp/public/imagenes_extraidas/2020_2025/*.*')

# Ordenar por nombre para agrupar por año
image_files.sort()

model = genai.GenerativeModel('gemini-3.5-flash')

batch_size = 15
mapping_result = {}

print(f"Total imágenes a mapear: {len(image_files)}")

for i in range(0, len(image_files), batch_size):
    batch = image_files[i:i+batch_size]
    print(f"Procesando lote {i//batch_size + 1} de {(len(image_files)-1)//batch_size + 1}...")
    
    prompt = f"""
    Aquí tienes una lista de preguntas de exámenes de biología (en formato JSON):
    {json.dumps(q_simple, ensure_ascii=False)}
    
    A continuación te paso {len(batch)} imágenes. Cada imagen viene precedida por su nombre de archivo.
    Tu tarea es determinar a qué 'id' de pregunta pertenece cada imagen. Fíjate en los textos y dibujos de la imagen para relacionarlos con el texto de la pregunta. El nombre del archivo contiene el año del examen, úsalo para filtrar.
    
    Devuelve estrictamente un único objeto JSON válido con este formato exacto:
    {{
        "nombre_archivo.png": "q_1",
        "nombre_archivo2.jpeg": "q_5"
    }}
    Si una imagen no corresponde a ninguna pregunta (por ejemplo es un logo institucional, la cabecera de la página, un escudo de la universidad o texto genérico), su valor debe ser null.
    NO escribas nada más aparte del JSON.
    """
    
    contents = [prompt]
    for img_path in batch:
        img_name = os.path.basename(img_path)
        img = PIL.Image.open(img_path)
        # Convertir a RGB por si hay canales alfa raros
        img = img.convert('RGB')
        contents.append(f"Archivo: {img_name}")
        contents.append(img)
        
    try:
        response = model.generate_content(contents)
        json_str = response.text
        # Limpiar posibles delimitadores markdown
        match = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = re.sub(r'```.*?\n', '', json_str)
            json_str = re.sub(r'```', '', json_str)
            
        batch_map = json.loads(json_str)
        mapping_result.update(batch_map)
        print(f"  -> Lote mapeado con éxito: {len([k for k,v in batch_map.items() if v])} emparejamientos encontrados.")
    except Exception as e:
        print(f"  -> [X] Error parseando respuesta del lote: {e}")
        try:
            print("  Respuesta cruda:", response.text[:200])
        except:
            pass
            
    time.sleep(2) # Respetar límites de la API

# Actualizar JSON principal
asignaciones = 0
for img_name, q_id in mapping_result.items():
    if q_id:
        for q in questions:
            if q['id'] == q_id:
                q['image'] = f"/imagenes_extraidas/2020_2025/{img_name}"
                asignaciones += 1

with open('webapp/src/data_2020_2025.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"\nMapeo finalizado y guardado en data_2020_2025.json. Se asignaron {asignaciones} imágenes.")
