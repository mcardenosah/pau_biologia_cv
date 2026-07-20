import os
import re
import json

def convert_md_to_json(md_path, json_path):
    if not os.path.exists(md_path):
        print(f"Archivo no encontrado: {md_path}")
        return
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Limpiar todos los literales \n que se colaron en la escritura del MD
    content = content.replace('\\n', '\n')
    
    blocks = re.split(r'## BLOQUE (\d+ - .*?)\n', content)
    questions_data = []
    
    for i in range(1, len(blocks), 2):
        block_name = blocks[i].strip()
        block_content = blocks[i+1]
        
        q_blocks = re.split(r'---', block_content)
        
        for qb in q_blocks:
            if not qb.strip():
                continue
                
            meta_match = re.search(r'\*\*\((.*?)\)\*\*', qb)
            if not meta_match:
                continue
            meta = meta_match.group(1).split(', Opción')
            date_info = meta[0].strip().split(' ')
            year = date_info[0] if len(date_info) > 0 else ""
            month = date_info[1] if len(date_info) > 1 else ""
            option = meta[1].strip() if len(meta) > 1 else ""
            
            pregunta_start = qb.find('**Pregunta:**')
            criterios_start = qb.find('**Criterios de')
            
            question_text = ""
            criteria_text = ""
            
            if pregunta_start != -1:
                end_pos = criterios_start if criterios_start != -1 else len(qb)
                raw_q = qb[pregunta_start + len('**Pregunta:**'):end_pos]
                question_text = re.sub(r'(?m)^>\s*', '', raw_q).strip()
                # Fix literal \n and trailing garbage
                question_text = question_text.replace('\\n', '\n')
                question_text = re.sub(r'[\n>\s]+$', '', question_text)
                
            if criterios_start != -1:
                criterios_match = re.search(r'\*\*Criterios de .*?\*\*(.*)', qb[criterios_start:], re.DOTALL)
                if criterios_match:
                    raw_c = criterios_match.group(1)
                    criteria_text = re.sub(r'(?m)^>\s*', '', raw_c).strip()
                    criteria_text = criteria_text.replace('\\n', '\n')
                    criteria_text = re.sub(r'[\n>\s]+$', '', criteria_text)
            
            img_match = re.search(r'!\[.*?\]\((.*?)\)', qb)
            image_path = img_match.group(1) if img_match else None
            
            questions_data.append({
                "id": f"q_{len(questions_data)+1}",
                "block": block_name,
                "year": year,
                "month": month,
                "option": option,
                "question": question_text,
                "criteria": criteria_text,
                "image": image_path,
                "a": 1.0,  # Discriminación
                "b": 0.5   # Dificultad por defecto (Selectividad)
            })
            
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
    print(f"Exportado exitosamente a {json_path} con {len(questions_data)} preguntas.")

if __name__ == "__main__":
    convert_md_to_json("Recopilatorio_2002-2010.md", "webapp/src/data_2002_2010.json")
