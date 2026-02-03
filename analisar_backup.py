"""Script para analisar documentos importantes do backup"""
from docx import Document
import os

def ler_docx(caminho):
    """Lê um arquivo Word e retorna o texto"""
    try:
        doc = Document(caminho)
        texto = []
        for para in doc.paragraphs:
            if para.text.strip():
                texto.append(para.text)
        return "\n".join(texto)
    except Exception as e:
        return f"Erro ao ler: {e}"

# Documentos para analisar
documentos = {
    "Escalas": [
        "BACKUP_ORGANIZADO/01_EMPRESA_GRN_PIZZAS/OPERACIONAL/Escalas/ESCALA ATUAL.docx",
        "BACKUP_ORGANIZADO/01_EMPRESA_GRN_PIZZAS/OPERACIONAL/Escalas/ESCALA MOTOS.docx"
    ],
    "POPs": [
        "BACKUP_ORGANIZADO/01_EMPRESA_GRN_PIZZAS/OPERACIONAL/POPs_Procedimentos/CHECK LIST.xlsx"
    ],
    "RH": [
        "BACKUP_ORGANIZADO/01_EMPRESA_GRN_PIZZAS/RH_DEPARTAMENTO_PESSOAL/Advertencias_Suspensoes/modelo advertencia disciplinar.docx",
        "BACKUP_ORGANIZADO/01_EMPRESA_GRN_PIZZAS/RH_DEPARTAMENTO_PESSOAL/Advertencias_Suspensoes/MODELO suspensao-de-funcionario.docx"
    ],
    "Outros": [
        "BACKUP_ORGANIZADO/11_OUTROS/POLÍTICA USO CELULAR.docx",
        "BACKUP_ORGANIZADO/11_OUTROS/POP_Abertura_e_Fechamento_Unidade.docx",
        "BACKUP_ORGANIZADO/11_OUTROS/Termo_Ciencia_Cameras_Audio.docx"
    ]
}

base_path = os.path.dirname(os.path.abspath(__file__))

print("="*80)
print("ANÁLISE DE DOCUMENTOS DO BACKUP")
print("="*80)

for categoria, arquivos in documentos.items():
    print(f"\n{'─'*80}")
    print(f"CATEGORIA: {categoria}")
    print(f"{'─'*80}\n")
    
    for arquivo in arquivos:
        caminho_completo = os.path.join(base_path, arquivo)
        
        if not os.path.exists(caminho_completo):
            print(f"❌ Não encontrado: {arquivo}\n")
            continue
        
        print(f"📄 {os.path.basename(arquivo)}")
        print(f"   Caminho: {arquivo}")
        
        if arquivo.endswith('.docx'):
            conteudo = ler_docx(caminho_completo)
            print(f"\n{conteudo[:500]}...")  # Primeiros 500 caracteres
        elif arquivo.endswith('.xlsx'):
            print("   [Arquivo Excel - já analisado separadamente]")
        
        print("\n" + "─"*80 + "\n")
