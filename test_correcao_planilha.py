"""
Teste simples para verificar o fluxo de correção de planilhas
"""
import asyncio
import sys
import os

# Adiciona o diretório assistente-ranny ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistente-ranny'))

# Importa a função de correção
from ai import extrair_correcao_planilha


async def test_correcao_simples():
    """Testa correção simples de número de entregadores"""
    
    print("=" * 60)
    print("TESTE 1: Correção de número de entregadores")
    print("=" * 60)
    
    # Dados atuais da planilha
    dados_atuais = {
        "periodo": "Semana 10/02 - 16/02",
        "dias": [
            {"dia": "segunda", "entregadores": ["João", "Maria"], "chegaram_horario": 0, "entregas": 20},
            {"dia": "terça", "entregadores": ["João", "Pedro"], "chegaram_horario": 0, "entregas": 15},
            {"dia": "quarta", "entregadores": ["Maria", "Pedro", "Ana"], "chegaram_horario": 0, "entregas": 25}
        ]
    }
    
    # Correção solicitada
    texto_correcao = "terça teve 3 entregadores"
    
    print(f"\n📊 Dados atuais:")
    for dia in dados_atuais['dias']:
        print(f"  • {dia['dia']}: {len(dia['entregadores'])} entregadores, {dia['entregas']} entregas")
    
    print(f"\n✏️ Correção solicitada: '{texto_correcao}'")
    print("\n⏳ Processando...")
    
    # Chama a função de correção
    resultado = await extrair_correcao_planilha(texto_correcao, dados_atuais, 'semanal')
    
    print(f"\n📋 Resultado:")
    print(f"  Sucesso: {resultado['sucesso']}")
    
    if resultado['sucesso']:
        print(f"  Dias alterados: {resultado['mudancas']}")
        print(f"\n📊 Dados corrigidos:")
        for dia in resultado['dados_corrigidos']['dias']:
            marcador = " ← CORRIGIDO" if dia['dia'] in resultado['mudancas'] else ""
            num_entregadores = len(dia['entregadores']) if isinstance(dia['entregadores'], list) else dia['entregadores']
            print(f"  • {dia['dia']}: {num_entregadores} entregadores, {dia['entregas']} entregas{marcador}")
    else:
        print(f"  Erro: {resultado.get('erro', 'Desconhecido')}")
    
    return resultado['sucesso']


async def test_correcao_entregas():
    """Testa correção de número de entregas"""
    
    print("\n" + "=" * 60)
    print("TESTE 2: Correção de número de entregas")
    print("=" * 60)
    
    dados_atuais = {
        "periodo": "Semana 10/02 - 16/02",
        "dias": [
            {"dia": "segunda", "entregadores": ["João", "Maria"], "chegaram_horario": 0, "entregas": 20},
            {"dia": "terça", "entregadores": ["João", "Pedro"], "chegaram_horario": 0, "entregas": 15},
            {"dia": "quarta", "entregadores": ["Maria", "Pedro", "Ana"], "chegaram_horario": 0, "entregas": 25}
        ]
    }
    
    texto_correcao = "segunda teve 30 entregas"
    
    print(f"\n📊 Dados atuais:")
    for dia in dados_atuais['dias']:
        print(f"  • {dia['dia']}: {len(dia['entregadores'])} entregadores, {dia['entregas']} entregas")
    
    print(f"\n✏️ Correção solicitada: '{texto_correcao}'")
    print("\n⏳ Processando...")
    
    resultado = await extrair_correcao_planilha(texto_correcao, dados_atuais, 'semanal')
    
    print(f"\n📋 Resultado:")
    print(f"  Sucesso: {resultado['sucesso']}")
    
    if resultado['sucesso']:
        print(f"  Dias alterados: {resultado['mudancas']}")
        print(f"\n📊 Dados corrigidos:")
        for dia in resultado['dados_corrigidos']['dias']:
            marcador = " ← CORRIGIDO" if dia['dia'] in resultado['mudancas'] else ""
            num_entregadores = len(dia['entregadores']) if isinstance(dia['entregadores'], list) else dia['entregadores']
            print(f"  • {dia['dia']}: {num_entregadores} entregadores, {dia['entregas']} entregas{marcador}")
    else:
        print(f"  Erro: {resultado.get('erro', 'Desconhecido')}")
    
    return resultado['sucesso']


async def test_correcao_multipla():
    """Testa correção de múltiplos campos ao mesmo tempo"""
    
    print("\n" + "=" * 60)
    print("TESTE 3: Correção de múltiplos campos")
    print("=" * 60)
    
    dados_atuais = {
        "periodo": "Semana 10/02 - 16/02",
        "dias": [
            {"dia": "segunda", "entregadores": ["João", "Maria"], "chegaram_horario": 0, "entregas": 20},
            {"dia": "terça", "entregadores": ["João", "Pedro"], "chegaram_horario": 0, "entregas": 15},
            {"dia": "quarta", "entregadores": ["Maria", "Pedro", "Ana"], "chegaram_horario": 0, "entregas": 25}
        ]
    }
    
    texto_correcao = "quarta teve 4 entregadores e 30 entregas"
    
    print(f"\n📊 Dados atuais:")
    for dia in dados_atuais['dias']:
        print(f"  • {dia['dia']}: {len(dia['entregadores'])} entregadores, {dia['entregas']} entregas")
    
    print(f"\n✏️ Correção solicitada: '{texto_correcao}'")
    print("\n⏳ Processando...")
    
    resultado = await extrair_correcao_planilha(texto_correcao, dados_atuais, 'semanal')
    
    print(f"\n📋 Resultado:")
    print(f"  Sucesso: {resultado['sucesso']}")
    
    if resultado['sucesso']:
        print(f"  Dias alterados: {resultado['mudancas']}")
        print(f"\n📊 Dados corrigidos:")
        for dia in resultado['dados_corrigidos']['dias']:
            marcador = " ← CORRIGIDO" if dia['dia'] in resultado['mudancas'] else ""
            num_entregadores = len(dia['entregadores']) if isinstance(dia['entregadores'], list) else dia['entregadores']
            print(f"  • {dia['dia']}: {num_entregadores} entregadores, {dia['entregas']} entregas{marcador}")
    else:
        print(f"  Erro: {resultado.get('erro', 'Desconhecido')}")
    
    return resultado['sucesso']


async def main():
    """Executa todos os testes"""
    
    print("\n🧪 INICIANDO TESTES DO SISTEMA DE CORREÇÃO DE PLANILHAS\n")
    
    try:
        # Executa os testes
        teste1 = await test_correcao_simples()
        teste2 = await test_correcao_entregas()
        teste3 = await test_correcao_multipla()
        
        # Resumo
        print("\n" + "=" * 60)
        print("RESUMO DOS TESTES")
        print("=" * 60)
        print(f"Teste 1 (Correção de entregadores): {'✅ PASSOU' if teste1 else '❌ FALHOU'}")
        print(f"Teste 2 (Correção de entregas): {'✅ PASSOU' if teste2 else '❌ FALHOU'}")
        print(f"Teste 3 (Correção múltipla): {'✅ PASSOU' if teste3 else '❌ FALHOU'}")
        
        total = sum([teste1, teste2, teste3])
        print(f"\n📊 Total: {total}/3 testes passaram")
        
        if total == 3:
            print("\n🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        else:
            print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
