#!/usr/bin/env python3
"""Script para reenviar o último arquivo que falhou"""

import asyncio
import json
from pathlib import Path
from telegram import Bot
from dotenv import load_dotenv
import os

# Carrega .env
load_dotenv(Path('assistente-ranny/.env'))

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))

async def main():
    # Carrega relatório
    with open('relatorio_upload_backup.json', 'r', encoding='utf-8') as f:
        relatorio = json.load(f)
    
    # Encontra o arquivo
    arquivo = None
    for arq in relatorio['arquivos']:
        if arq['nome'] == 'ImpressaoPDF.pdf':
            arquivo = arq
            break
    
    if not arquivo:
        print("❌ Arquivo não encontrado no relatório")
        return
    
    print("📤 Tentando enviar: ImpressaoPDF.pdf")
    print(f"   Categoria: {arquivo['categoria']}")
    print(f"   Tópico: {arquivo['topico']}")
    print()
    
    bot = Bot(token=BOT_TOKEN)
    
    caminho = Path(arquivo['caminho'])
    legenda = (
        f"📁 {arquivo['nome']}\n"
        f"📂 Categoria: {arquivo['categoria']}\n"
        f"📊 Tamanho: {arquivo['tamanho_mb']} MB"
    )
    
    try:
        with open(caminho, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                document=f,
                caption=legenda,
                message_thread_id=arquivo['topico'],
                read_timeout=60,
                write_timeout=60
            )
        print("✅ Arquivo enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    asyncio.run(main())
