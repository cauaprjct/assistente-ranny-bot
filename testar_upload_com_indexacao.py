#!/usr/bin/env python3
"""
Script de teste para verificar se o upload com indexação está funcionando
Testa com apenas 3 arquivos
"""

import asyncio
import sys
import os

# Adiciona o diretório assistente-ranny ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistente-ranny'))

import database_adapter as db

async def main():
    print("="*80)
    print("🧪 TESTE DE UPLOAD COM INDEXAÇÃO")
    print("="*80)
    
    # Importa o organizador
    from organizar_backup_telegram import OrganizadorBackup
    
    organizador = OrganizadorBackup()
    
    # Inicializa
    print("\n1️⃣ Inicializando...")
    if not organizador.inicializar():
        print("❌ Falha na inicialização")
        return
    
    # Escaneia backup
    print("\n2️⃣ Escaneando backup...")
    if not organizador.escanear_backup():
        print("❌ Falha no escaneamento")
        return
    
    print(f"\n✅ {len(organizador.arquivos_escaneados)} arquivos encontrados")
    
    # Verifica quantos documentos existem no banco ANTES
    print("\n3️⃣ Verificando banco de dados ANTES do upload...")
    try:
        docs_antes = db.buscar_documentos('')
        print(f"📊 Documentos no banco ANTES: {len(docs_antes)}")
    except Exception as e:
        print(f"⚠️  Erro ao buscar documentos: {e}")
        docs_antes = []
    
    # Faz upload de apenas 3 arquivos
    print("\n4️⃣ Fazendo upload de 3 arquivos de teste...")
    resposta = input("Deseja continuar? (s/n): ").strip().lower()
    if resposta != 's':
        print("❌ Teste cancelado")
        return
    
    sucesso, erros = await organizador.fazer_upload(limite=3)
    
    # Verifica quantos documentos existem no banco DEPOIS
    print("\n5️⃣ Verificando banco de dados DEPOIS do upload...")
    try:
        docs_depois = db.buscar_documentos('')
        print(f"📊 Documentos no banco DEPOIS: {len(docs_depois)}")
        print(f"📈 Novos documentos indexados: {len(docs_depois) - len(docs_antes)}")
        
        # Mostra os últimos 3 documentos
        if docs_depois:
            print("\n📄 Últimos documentos indexados:")
            for doc in docs_depois[-3:]:
                print(f"  • {doc.get('descricao', 'Sem descrição')}")
                print(f"    Categoria: {doc.get('categoria', 'N/A')}")
                print(f"    File ID: {doc.get('file_id', 'N/A')[:20]}...")
                print(f"    Message ID: {doc.get('message_id', 'N/A')}")
                print()
    except Exception as e:
        print(f"⚠️  Erro ao buscar documentos: {e}")
    
    # Gera relatório
    print("\n6️⃣ Gerando relatório...")
    organizador.gerar_relatorio('relatorio_teste_indexacao.json')
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO!")
    print("="*80)
    print(f"\n📊 Resumo:")
    print(f"  • Arquivos enviados: {sucesso}")
    print(f"  • Erros: {erros}")
    print(f"  • Documentos indexados: {len(docs_depois) - len(docs_antes)}")
    print(f"\n💡 Verifique o arquivo 'relatorio_teste_indexacao.json' para detalhes")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
