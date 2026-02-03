
import pypdf
import os

file_path = r"c:\Users\ngb\Desktop\cliente\BACKUP\AREA DE TRABALHO\PESSOAL\Gilney\Despacho Gilney.pdf"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

try:
    reader = pypdf.PdfReader(file_path)
    print(f"Number of pages: {len(reader.pages)}")
    
    # Read first page
    if len(reader.pages) > 0:
        page = reader.pages[0]
        text = page.extract_text()
        print("--- Content ---")
        print(text)
        
except Exception as e:
    print(f"Error reading PDF: {e}")
