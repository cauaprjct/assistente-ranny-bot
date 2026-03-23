"""
Teste da funcionalidade de planilha de entregadores
"""
import asyncio
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(__file__))

import ai
import pdf_tools


async def testar_extracao():
    """Testa extração de dados com IA"""
    print("=" * 80)
    print("🧪 TESTE 1: Extração de dados com IA")
    print("=" * 80)
    print()
    
    texto_teste = """
    Oi bot, faz a planilha da semana pra mim
    
    Segunda teve 3 entregadores e fizeram 20 entregas
    Terça teve 3 entregadores e fizeram 18 entregas  
    Quarta teve 3 entregadores e fizeram 22 entregas
    Quinta teve 3 entregadores e fizeram 19 entregas
    Sexta teve 4 entregadores, 3 chegaram no horário, fizeram 30 entregas
    Sábado teve 4 entregadores, todos chegaram no horário, fizeram 35 entregas
    Domingo teve 4 entregadores, 3 chegaram no horário, fizeram 28 entregas
    """
    
    print("📝 Texto de entrada:")
    print(texto_teste)
    print()
    
    print("⏳ Extraindo dados com IA...")
    resultado = await ai.extrair_dados_entregadores(texto_teste)
    
    if resultado['sucesso']:
        print("✅ Extração bem-sucedida!")
        print()
        print("📊 Dados extraídos:")
        
        import json
        print(json.dumps(resultado['dados'], indent=2, ensure_ascii=False))
        
        return resultado['dados']
    else:
        print(f"❌ Erro na extração: {resultado.get('erro')}")
        return None


def testar_criacao_excel(dados):
    """Testa criação do Excel"""
    print()
    print("=" * 80)
    print("🧪 TESTE 2: Criação de planilha Excel")
    print("=" * 80)
    print()
    
    if not dados:
        print("❌ Sem dados para criar Excel")
        return False
    
    print("⏳ Criando planilha Excel...")
    xlsx_bytes = pdf_tools.criar_xlsx_entregadores(dados)
    
    if xlsx_bytes:
        print(f"✅ Excel criado com sucesso! ({len(xlsx_bytes)} bytes)")
        
        # Salva arquivo para inspeção
        nome_arquivo = "teste_entregadores.xlsx"
        with open(nome_arquivo, 'wb') as f:
            f.write(xlsx_bytes)
        
        print(f"📁 Arquivo salvo: {nome_arquivo}")
        print("   Abra o arquivo para verificar a formatação!")
        
        return True
    else:
        print("❌ Erro ao criar Excel")
        return False


async def main():
    """Função principal de teste"""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "TESTE DE PLANILHA DE ENTREGADORES" + " " * 25 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Teste 1: Extração
    dados = await testar_extracao()
    
    # Teste 2: Criação de Excel
    if dados:
        sucesso = testar_criacao_excel(dados)
        
        if sucesso:
            print()
            print("=" * 80)
            print("✅ TODOS OS TESTES PASSARAM!")
            print("=" * 80)
            print()
            print("📋 Próximos passos:")
            print("1. Abra o arquivo teste_entregadores.xlsx")
            print("2. Verifique se as fórmulas estão corretas")
            print("3. Verifique a formatação (cores, bordas, etc)")
            print("4. Teste no bot enviando uma mensagem no Telegram")
            print()
        else:
            print()
            print("=" * 80)
            print("❌ TESTE DE EXCEL FALHOU")
            print("=" * 80)
    else:
        print()
        print("=" * 80)
        print("❌ TESTE DE EXTRAÇÃO FALHOU")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
