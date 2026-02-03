
import pypdf
import os

file_path = r"c:\Users\ngb\Desktop\cliente\BACKUP_ORGANIZADO\04_JURIDICO\Processos_Trabalhistas\PROCESSO_  - AÇÃO TRABALHISTA - comprovantes pgnto.pdf"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

try:
    reader = pypdf.PdfReader(file_path)
    print(f"Number of pages: {len(reader.pages)}")
    
    # Read first 5 pages to get an idea
    for i in range(min(5, len(reader.pages))):
        print(f"\n--- Page {i+1} ---")
        page = reader.pages[i]
        text = page.extract_text()
        print(text)
        
except Exception as e:
    print(f"Error reading PDF: {e}")
