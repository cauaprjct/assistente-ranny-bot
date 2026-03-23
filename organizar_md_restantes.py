import os
import shutil
from pathlib import Path

# Arquivos específicos restantes
arquivos_especificos = {
    '06-implementacoes': [
        'CORRECAO_TOPICOS.md',
        'FASE1_IMPLEMENTACAO_DOCX_AVANCADO.md',
        'FASE2_IMPLEMENTACAO_TEMPLATES.md',
        'IMPLEMENTACAO_COMPLETA_PLANILHAS.md',
        'IMPLEMENTACAO_DOCUMENTOS_WORD.md',
        'IMPLEMENTACAO_PLANILHAS_PESSOAIS.md',
        'IMPLEMENTACAO_VERSAO_2_PLANILHA.md',
        'INTEGRACAO_ONEDRIVE_IMPLEMENTADA.md',
        'MELHORIA_CORRECAO_PLANILHAS.md',
        'MODIFICACOES_UPLOAD_COM_INDEXACAO.md',
        'PLANILHAS_PERSONALIZADAS_IMPLEMENTADO.md',
        'REMOCAO_ONEDRIVE_COMPLETA.md',
        'REMOCAO_SUPABASE_COMPLETA.md',
        'REVISAO_PLANILHAS_PERSONALIZADAS.md',
        'SOLUCAO_BUSCA_TELEGRAM.md',
        'SOLUCAO_HIBRIDA_IMPLEMENTADA.md',
        'SOLUCAO_IMPLEMENTADA.md'
    ]
}

def mover_arquivo(arquivo, destino):
    """Move um arquivo para o destino"""
    try:
        origem = Path(arquivo)
        dest_path = Path('docs-organizados') / destino / origem.name
        
        if origem.exists():
            shutil.move(str(origem), str(dest_path))
            print(f"✓ Movido: {origem.name} -> {destino}")
            return True
    except Exception as e:
        print(f"✗ Erro ao mover {arquivo}: {e}")
    return False

def organizar_restantes():
    """Organiza arquivos restantes específicos"""
    movidos = 0
    
    for pasta, arquivos in arquivos_especificos.items():
        for arquivo in arquivos:
            if mover_arquivo(arquivo, pasta):
                movidos += 1
    
    print(f"\n{'='*50}")
    print(f"Total de arquivos movidos: {movidos}")
    print(f"{'='*50}")
    
    # Verificar se ainda há arquivos .md na raiz
    raiz = Path('.')
    restantes = list(raiz.glob('*.md'))
    
    if restantes:
        print(f"\nAinda restam {len(restantes)} arquivos .md na raiz:")
        for arq in restantes:
            print(f"  - {arq.name}")
    else:
        print("\n✅ Todos os arquivos .md foram organizados!")

if __name__ == '__main__':
    organizar_restantes()
