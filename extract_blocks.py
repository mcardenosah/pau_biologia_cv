import fitz

doc = fitz.open('2002-2010/PAU_Biologia_2008.pdf')
for i in range(min(5, len(doc))):
    print(f"--- PAGE {i} ---")
    print(doc[i].get_text()[:500])  # Only print first 500 chars to avoid clutter
