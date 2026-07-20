import fitz
import os
import glob

def extract_images_from_modern_pdfs(folder_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    
    total_images = 0
    for pdf_path in pdf_files:
        doc = fitz.open(pdf_path)
        pdf_basename = os.path.basename(pdf_path).replace(".pdf", "")
        
        for i, page in enumerate(doc):
            images = page.get_images(full=True)
            for j, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                img_filename = f"{pdf_basename}_p{i+1}_i{j}.{image_ext}"
                img_filepath = os.path.join(output_dir, img_filename)
                
                with open(img_filepath, "wb") as f:
                    f.write(image_bytes)
                total_images += 1
                
    print(f"Extracción finalizada. {total_images} imágenes guardadas en {output_dir}")

if __name__ == "__main__":
    extract_images_from_modern_pdfs("2011-2014", "webapp/public/imagenes_extraidas/2011_2014")
    extract_images_from_modern_pdfs("2015-2019", "webapp/public/imagenes_extraidas/2015_2019")
