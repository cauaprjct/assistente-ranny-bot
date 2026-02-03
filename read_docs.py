
import pypdf
import os

files_to_check = [
    r"c:\Users\ngb\Desktop\cliente\BACKUP\AREA DE TRABALHO\GRN PIZZAS\DOCS PIZZA\PROCURAÇÃO RANNY.pdf",
    r"c:\Users\ngb\Desktop\cliente\BACKUP\AREA DE TRABALHO\GRN PIZZAS\RANNY FERREIRA.PDF"
]

for file_path in files_to_check:
    print(f"\nChecking file: {file_path}")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

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
