import os
import json
import glob
import PIL.Image
import google.generativeai as genai
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

if not api_key:
    print("NO SE ENCONTRÓ LA CLAVE DE API EN .env NI api.env")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

blocks_to_process = [
    ("2011_2014", "webapp/src/data_2011_2014.json"),
    ("2015_2019", "webapp/src/data_2015_2019.json")
]

for block_dir, json_file in blocks_to_process:
    print(f"\\n=== PROCESANDO BLOQUE {block_dir} ===")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # Filtrar preguntas para no exceder tokens
    q_simple = [{"id": q["id"], "year": q["year"], "text": q["question"][:200]} for q in questions]

    image_files = glob.glob(f'webapp/public/imagenes_extraidas/{block_dir}/*.*')
    image_files.sort()
    
    batch_size = 25
    mapping_result = {}

    print(f"Total imágenes a mapear: {len(image_files)}")

    for i in range(0, len(image_files), batch_size):
        batch = image_files[i:i+batch_size]
        print(f"Lote {i//batch_size + 1} de {(len(image_files)-1)//batch_size + 1}...")
        
        prompt = f"""
        Aquí tienes una lista de preguntas de exámenes de biología (en formato JSON):
        {json.dumps(q_simple, ensure_ascii=False)}
        
        A continuación te paso {len(batch)} imágenes. El nombre de archivo contiene el año.
        Tu tarea es determinar a qué 'id' de pregunta pertenece cada imagen, fijándote en el texto.
        
        Devuelve estrictamente un único objeto JSON válido:
        {{
            "nombre_archivo.png": "q_1"
        }}
        Si una imagen no corresponde a ninguna pregunta, su valor debe ser null.
        """
        
        contents = [prompt]
        for img_path in batch:
            img_name = os.path.basename(img_path)
            img = PIL.Image.open(img_path).convert('RGB')
            contents.append(f"Archivo: {img_name}")
            contents.append(img)
            
        try:
            response = model.generate_content(contents)
            json_str = response.text
            match = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL)
            if match: json_str = match.group(1)
            else: json_str = re.sub(r'```.*?\n', '', json_str).replace('```', '')
                
            batch_map = json.loads(json_str)
            mapping_result.update(batch_map)
            print(f"  -> Mapeadas {len([k for k,v in batch_map.items() if v])} imágenes en este lote.")
        except Exception as e:
            print(f"  -> [X] Error parseando respuesta del lote: {e}")
                
        time.sleep(15) # Respetar límites de la API

    # Actualizar JSON
    asignaciones = 0
    for img_name, q_id in mapping_result.items():
        if q_id:
            for q in questions:
                if q['id'] == q_id:
                    q['image'] = f"/imagenes_extraidas/{block_dir}/{img_name}"
                    asignaciones += 1

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Bloque {block_dir} finalizado. {asignaciones} imágenes asignadas.")
