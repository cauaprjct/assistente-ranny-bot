#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reenviar arquivos que falharam no upload inicial
Lê o relatorio_upload_backup.json e reenvia apenas os arquivos sem message_id
"""

import json
import os
import sys
import io
import time
from pathlib import Path

# Fix encoding no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Importar módulos do bot
sys.path.insert(0, str(Path(__file__).parent / 'assistente-ranny'))
from config import TELEGRAM_BOT_TOKEN, GROUP_ID
import database_adapter as db
from telegram import Bot
from telegram.error import TelegramError, TimedOut, NetworkError

def carregar_relatorio():
    """Carrega o relatório de upload"""
    with open('relatorio_upload_backup.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extrair_arquivos_falhados(relatorio):
    """Extrai lista de arquivos que não têm message_id"""
    falhados = []
    for arquivo in relatorio['arquivos']:
        if 'message_id' not in arquivo or arquivo['message_id'] is None:
            falhados.append(arquivo)
    return falhados

def fazer_upload_arquivo(bot, arquivo, index, total):
    """Faz upload de um arquivo para o Telegram"""
    caminho = arquivo['caminho']
    nome = arquivo['nome']
    categoria = arquivo['categoria']
    topico = arquivo['topico']
    
    print(f"\n[{index}/{total}] Enviando: {nome}")
    print(f"   Categoria: {categoria} | Tópico: {topico}")
    
    try:
        # Verificar se arquivo existe
        if not os.path.exists(caminho):
            print(f"   ❌ Arquivo não encontrado: {caminho}")
            return False
        
        # Verificar tamanho
        tamanho_mb = os.path.getsize(caminho) / (1024 * 1024)
        if tamanho_mb > 50:
            print(f"   ⚠️  Arquivo muito grande ({tamanho_mb:.2f}MB), pulando...")
            return False
        
        # Fazer upload
        with open(caminho, 'rb') as f:
            message = bot.send_document(
                chat_id=GROUP_ID,
                document=f,
                filename=nome,
                caption=f"📁 {nome}\n🏷️ Categoria: {categoria}",
                message_thread_id=topico,
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60
            )
        
        # Indexar no banco usando add_documento
        file_id = message.document.file_id
        message_id = message.message_id
        
        db.add_documento(
            tipo='arquivo',
            descricao=nome,
            file_id=file_id,
            categoria=categoria,
            message_id=message_id,
            topic_id=topico
        )
        
        print(f"   ✅ Sucesso! message_id={message_id}")
        return True
        
    except TimedOut:
        print(f"   ⏱️  Timeout - arquivo muito grande ou conexão lenta")
        return False
    except NetworkError as e:
        print(f"   🌐 Erro de rede: {e}")
        return False
    except TelegramError as e:
        if "flood" in str(e).lower():
            print(f"   🚫 Flood control - aguardando 60 segundos...")
            time.sleep(60)
            return False
        else:
            print(f"   ❌ Erro do Telegram: {e}")
            return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False

def main():
    print("=" * 80)
    print("🔄 REENVIO DE ARQUIVOS FALHADOS")
    print("=" * 80)
    
    # Carregar relatório
    print("\n📂 Carregando relatório...")
    relatorio = carregar_relatorio()
    
    # Extrair falhados
    falhados = extrair_arquivos_falhados(relatorio)
    print(f"✅ Encontrados {len(falhados)} arquivos falhados")
    
    if len(falhados) == 0:
        print("\n🎉 Nenhum arquivo para reenviar!")
        return
    
    # Mostrar lista
    print("\n📋 Arquivos que serão reenviados:")
    for i, arq in enumerate(falhados, 1):
        print(f"   {i}. {arq['nome']} ({arq['categoria']})")
    
    # Confirmar
    print("\n" + "=" * 80)
    resposta = input("Deseja continuar com o reenvio? (s/n): ").strip().lower()
    if resposta != 's':
        print("❌ Operação cancelada")
        return
    
    # Inicializar bot e banco
    print("\n🔧 Inicializando...")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    db.init_database()
    print("✅ Bot e banco conectados")
    
    # Fazer upload
    print("\n📤 Iniciando reenvio...")
    print("=" * 80)
    
    sucesso = 0
    erros = 0
    
    for i, arquivo in enumerate(falhados, 1):
        if fazer_upload_arquivo(bot, arquivo, i, len(falhados)):
            sucesso += 1
        else:
            erros += 1
        
        # Delay entre uploads para evitar flood
        if i < len(falhados):
            print("   ⏳ Aguardando 3 segundos...")
            time.sleep(3)
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DO REENVIO")
    print("=" * 80)
    print(f"✅ Sucesso: {sucesso}")
    print(f"❌ Erros: {erros}")
    print(f"📊 Total: {len(falhados)}")
    print("=" * 80)
    
    # Salvar relatório atualizado
    print("\n💾 Salvando relatório atualizado...")
    with open('relatorio_reenvio.json', 'w', encoding='utf-8') as f:
        json.dump({
            'data': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_falhados': len(falhados),
            'sucesso': sucesso,
            'erros': erros,
            'arquivos': falhados
        }, f, indent=2, ensure_ascii=False)
    print("✅ Relatório salvo em: relatorio_reenvio.json")
    
    print("\n✅ Processo concluído!")

if __name__ == '__main__':
    main()
