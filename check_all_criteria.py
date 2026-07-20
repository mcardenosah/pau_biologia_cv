import os, fitz, glob

for path in glob.glob('2002-2010/*.pdf'):
    doc = fitz.open(path)
    text = "".join(page.get_text() for page in doc)
    if "criteri" in text.lower():
        print(f"Criteria FOUND in {path}")
    else:
        print(f"NO criteria in {path}")
