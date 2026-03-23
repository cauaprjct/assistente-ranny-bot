"""Teste de extração de múltiplas linhas de dados"""
import asyncio
import sys
sys.path.insert(0, 'assistente-ranny')

from ai import extrair_estrutura_planilha

async def test_multiplas_linhas():
    """Testa se a IA extrai múltiplas linhas de dados"""
    
    # Mensagem do usuário (sem quebras de linha entre dados)
    descricao = """Cria planilha excel com:
Data, Tipo, Instituição, Valor Aplicado, Taxa, Vencimento, Valor Atual, Rentabilidade, Status
05/01, Tesouro Direto, Tesouro Nacional, 5000.00, 12.5%, 01/01/2027, 5625.00, 625.00, Ativo
10/01, CDB, Banco Inter, 3000.00, 110% CDI, 10/07/2026, 3165.00, 165.00, Ativo"""
    
    print("🧪 Testando extração de múltiplas linhas...")
    print(f"📝 Descrição:\n{descricao}\n")
    
    resultado = await extrair_estrutura_planilha(descricao)
    
    if not resultado['sucesso']:
        print(f"❌ FALHOU: {resultado.get('erro')}")
        return False
    
    estrutura = resultado['estrutura']
    dados = estrutura.get('dados_exemplo', [])
    
    print(f"✅ Estrutura extraída:")
    print(f"   Título: {estrutura.get('titulo')}")
    print(f"   Colunas: {len(estrutura.get('colunas', []))}")
    print(f"   Linhas de dados: {len(dados)}")
    print(f"   Tem total: {estrutura.get('tem_total')}")
    
    if len(dados) < 2:
        print(f"\n❌ PROBLEMA: Esperava 2+ linhas, mas extraiu apenas {len(dados)}")
        print(f"   Dados extraídos: {dados}")
        return False
    
    print(f"\n✅ SUCESSO! Extraiu {len(dados)} linhas:")
    for idx, linha in enumerate(dados, 1):
        print(f"   Linha {idx}: {linha[:3]}... ({len(linha)} valores)")
    
    return True

if __name__ == "__main__":
    sucesso = asyncio.run(test_multiplas_linhas())
    sys.exit(0 if sucesso else 1)
