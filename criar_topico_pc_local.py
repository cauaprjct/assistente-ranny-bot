"""
📁 Criar Tópico "Arquivos PC (Local)"
Cria o tópico automaticamente e retorna o ID
"""

import asyncio
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


async def criar_topico():
    """Cria o tópico e retorna o ID"""
    bot = Bot(token=BOT_TOKEN)
    
    print("=" * 60)
    print("📁 CRIANDO TÓPICO 'ARQUIVOS PC (LOCAL)'")
    print("=" * 60)
    print()
    
    try:
        # Criar tópico
        print("🔄 Criando tópico...")
        result = await bot.create_forum_topic(
            chat_id=CHAT_ID,
            name="📁 Arquivos PC (Local)",
            icon_color=0x6FB9F0,  # Azul claro
            icon_custom_emoji_id=None
        )
        
        topico_id = result.message_thread_id
        
        print("✅ Tópico criado com sucesso!")
        print()
        print("=" * 60)
        print(f"📋 ID DO TÓPICO: {topico_id}")
        print("=" * 60)
        print()
        
        # Enviar mensagem de boas-vindas no tópico
        mensagem_boas_vindas = (
            "🤖 Tópico configurado!\n\n"
            "📁 Este tópico receberá automaticamente todos os arquivos "
            "salvos no PC (Desktop e Documentos).\n\n"
            "✅ Tipos de arquivo monitorados:\n"
            "   • Excel (.xlsx, .xls)\n"
            "   • Word (.docx, .doc)\n"
            "   • PDF (.pdf)\n\n"
            "⏱️ Verificação: a cada 30 segundos\n"
            "📅 Filtro: apenas arquivos modificados nas últimas 24h"
        )
        
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=topico_id,
            text=mensagem_boas_vindas
        )
        
        print("✅ Mensagem de boas-vindas enviada!")
        print()
        
        # Atualizar .env
        print("🔄 Atualizando arquivo .env...")
        atualizar_env(topico_id)
        
        print()
        print("=" * 60)
        print("✅ CONFIGURAÇÃO COMPLETA!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. O arquivo .env foi atualizado automaticamente")
        print("2. Execute: python monitor_simples.py")
        print("3. Salve um arquivo no Desktop ou Documentos")
        print("4. Aguarde até 30 segundos")
        print("5. O arquivo aparecerá no tópico novo!")
        print()
        
        return topico_id
        
    except TelegramError as e:
        print(f"❌ Erro do Telegram: {e}")
        print()
        
        if "not enough rights" in str(e).lower():
            print("⚠️ O bot não tem permissão para criar tópicos!")
            print()
            print("Solução:")
            print("1. Abra o grupo no Telegram")
            print("2. Clique no nome do grupo")
            print("3. Clique em 'Administradores'")
            print("4. Encontre o bot 'Assistente Ranny'")
            print("5. Ative a permissão 'Gerenciar tópicos'")
            print("6. Execute este script novamente")
        
        return None
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def atualizar_env(topico_id):
    """Atualiza o arquivo .env com o ID do tópico"""
    try:
        # Ler .env atual
        with open('.env', 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Verificar se já existe TOPICO_PC_LOCAL
        topico_existe = False
        for i, linha in enumerate(linhas):
            if linha.startswith('TOPICO_PC_LOCAL='):
                linhas[i] = f'TOPICO_PC_LOCAL={topico_id}\n'
                topico_existe = True
                break
        
        # Se não existe, adicionar no final
        if not topico_existe:
            linhas.append(f'\n# Tópico para arquivos do PC local\n')
            linhas.append(f'TOPICO_PC_LOCAL={topico_id}\n')
        
        # Salvar .env atualizado
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(linhas)
        
        print(f"✅ Arquivo .env atualizado: TOPICO_PC_LOCAL={topico_id}")
        
    except Exception as e:
        print(f"⚠️ Erro ao atualizar .env: {e}")
        print(f"   Adicione manualmente: TOPICO_PC_LOCAL={topico_id}")


if __name__ == "__main__":
    topico_id = asyncio.run(criar_topico())
    
    if topico_id:
        print(f"\n🎉 Sucesso! ID do tópico: {topico_id}")
    else:
        print("\n❌ Falha ao criar tópico")
    
    input("\nPressione Enter para fechar...")
