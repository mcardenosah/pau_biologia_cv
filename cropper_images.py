import os
import json
import fitz
import cv2
import numpy as np

json_path = 'webapp/src/data_2002_2010.json'
output_dir = 'webapp/public/imagenes_extraidas'
os.makedirs(output_dir, exist_ok=True)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Agrupamos las imágenes por (year, page) para procesar cada página solo una vez
pages_to_process = {}

for q in data:
    img_url = q.get('image')
    if not img_url:
        continue
        
    basename = img_url.split('/')[-1]
    parts = basename.replace('.png', '').replace('.jpeg', '').split('_')
    if len(parts) >= 4:
        year = parts[2]
        page_num = int(parts[3].replace('p', ''))
        
        pdf_path = f"2002-2010/PAU_Biologia_{year}.pdf"
        if os.path.exists(pdf_path):
            if pdf_path not in pages_to_process:
                pages_to_process[pdf_path] = set()
            pages_to_process[pdf_path].add(page_num)

print(f"Páginas a procesar: {sum(len(v) for v in pages_to_process.values())}")

for pdf_path, pages in pages_to_process.items():
    doc = fitz.open(pdf_path)
    year = os.path.basename(pdf_path).replace('PAU_Biologia_', '').replace('.pdf', '')
    
    for page_num in pages:
        print(f"Procesando {year} página {page_num}...")
        page = doc[page_num - 1]
        
        # Render a 150 DPI
        zoom = 150 / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convertir a numpy array para OpenCV
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
            
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Binarizar (invertido)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Operación morfológica para conectar trazos del diagrama
        # Usamos un kernel moderado para no conectar el texto con el dibujo
        kernel = np.ones((7,7), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_rects = []
        page_area = pix.width * pix.height
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            
            # Filtrar ruido y marcos de página gigantes
            if area > 8000 and area < 0.8 * page_area:
                # Filtrar si es una línea muy fina (ej. separadores de texto)
                aspect_ratio = float(w) / h
                if 0.1 < aspect_ratio < 10:
                    valid_rects.append([x, y, x+w, y+h])
        
        if not valid_rects:
            print(f"  [X] No se detectó contorno válido en la página {page_num}")
            continue
            
        # Fusionar rectángulos cercanos (los diagramas pueden tener partes sueltas)
        # Tomamos el bounding box global de todos los componentes gráficos válidos
        min_x = min(r[0] for r in valid_rects)
        min_y = min(r[1] for r in valid_rects)
        max_x = max(r[2] for r in valid_rects)
        max_y = max(r[3] for r in valid_rects)
        
        # Pad
        pad = 15
        min_x = max(0, min_x - pad)
        min_y = max(0, min_y - pad)
        max_x = min(pix.width, max_x + pad)
        max_y = min(pix.height, max_y + pad)
        
        # Recortar de la imagen original a color
        cropped = img_bgr[min_y:max_y, min_x:max_x]
        
        # Guardar la imagen sobreescribiendo el archivo anterior (usaremos el formato genérico _pX_diagram.png)
        new_filename = f"PAU_Biologia_{year}_p{page_num}_diagram.png"
        new_filepath = os.path.join(output_dir, new_filename)
        cv2.imwrite(new_filepath, cropped)
        print(f"  [V] Guardado {new_filename} (Tamaño: {cropped.shape})")
        
        # Actualizar el JSON con la nueva ruta
        for q in data:
            if q.get('image') and f"_p{page_num}_" in q['image'] and str(q.get('year')) == str(year):
                q['image'] = f"/imagenes_extraidas/{new_filename}"

# Guardar los cambios en el JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    
print("\n¡Recorte con OpenCV finalizado y JSON actualizado!")
