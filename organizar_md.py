import os
import shutil
from pathlib import Path

# Mapeamento de arquivos para pastas
mapeamento = {
    '04-status-relatorios': [
        'STATUS_', 'RELATORIO_', 'DIAGNOSTICO_', 'VERIFICACAO_', 
        'VALIDACAO_', 'TESTE_'
    ],
    '05-analises': [
        'ANALISE_', 'GESTAO_FINANCEIRA_ANALISE_COMPLETA.md'
    ],
    '06-implementacoes': [
        'IMPLEMENTACAO_', 'FASE1_IMPLEMENTACAO_', 'FASE2_IMPLEMENTACAO_',
        'INTEGRACAO_', 'MODIFICACOES_', 'PLANILHAS_', 'REVISAO_',
        'MELHORIA_', 'SOLUCAO_', 'REMOCAO_', 'CORRECAO_TOPICOS.md'
    ],
    '07-resumos': [
        'RESUMO_'
    ],
    '08-projeto': [
        'PROJETO_', 'README', 'INDICE_DOCUMENTACAO.md'
    ],
    '09-checklists': [
        'CHECKLIST_'
    ],
    '10-outros': [
        'MENSAGEM_', 'PARA_RANNY_', 'PROPOSTA_', 'PROXIMOS_PASSOS.md',
        'RESPOSTA_', 'SITUACAO_', 'CONFLITO_'
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

def organizar_arquivos():
    """Organiza todos os arquivos .md da raiz"""
    raiz = Path('.')
    arquivos_md = list(raiz.glob('*.md'))
    
    print(f"Encontrados {len(arquivos_md)} arquivos .md na raiz\n")
    
    movidos = 0
    
    for arquivo in arquivos_md:
        nome = arquivo.name
        movido = False
        
        # Verificar em qual pasta o arquivo deve ir
        for pasta, padroes in mapeamento.items():
            for padrao in padroes:
                if nome.startswith(padrao) or nome == padrao:
                    if mover_arquivo(arquivo, pasta):
                        movidos += 1
                        movido = True
                    break
            if movido:
                break
    
    print(f"\n{'='*50}")
    print(f"Total de arquivos movidos: {movidos}")
    print(f"{'='*50}")

if __name__ == '__main__':
    organizar_arquivos()
