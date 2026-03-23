import os
from pathlib import Path

def verificar_organizacao():
    """Verifica o estado atual da organização"""
    
    # Verificar arquivos na raiz
    raiz = Path('.')
    arquivos_raiz = [f.name for f in raiz.glob('*.md')]
    
    print("="*60)
    print("VERIFICAÇÃO DA ORGANIZAÇÃO")
    print("="*60)
    
    print(f"\n📁 Arquivos .md na RAIZ: {len(arquivos_raiz)}")
    if arquivos_raiz:
        for arq in sorted(arquivos_raiz):
            print(f"  - {arq}")
    else:
        print("  ✅ Nenhum arquivo solto na raiz!")
    
    # Verificar docs-organizados
    docs_org = Path('docs-organizados')
    if docs_org.exists():
        print(f"\n📂 Estrutura docs-organizados:")
        
        pastas = sorted([d for d in docs_org.iterdir() if d.is_dir()])
        total_arquivos = 0
        
        for pasta in pastas:
            arquivos = list(pasta.glob('*.md'))
            total_arquivos += len(arquivos)
            print(f"  {pasta.name}: {len(arquivos)} arquivos")
        
        print(f"\n📊 Total de arquivos organizados: {total_arquivos}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    verificar_organizacao()
