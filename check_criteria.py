import fitz
doc = fitz.open('2002-2010/PAU_Biologia_2008.pdf')
text = ""
for page in doc:
    text += page.get_text() + "\n"
if "Criteri" in text or "criteri" in text.lower():
    print("Found criteria in text!")
    # print context around it
    idx = text.lower().find("criteri")
    print(text[max(0, idx-100):min(len(text), idx+500)])
else:
    print("No criteria found in 2008 document.")
