#!/usr/bin/env python3
"""
Script para verificar permissões do bot e criar tópicos manualmente
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Adiciona o diretório assistente-ranny ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistente-ranny'))

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    print("❌ python-telegram-bot não instalado")
    print("Execute: pip install python-telegram-bot")
    sys.exit(1)

# Carrega variáveis de ambiente
load_dotenv('assistente-ranny/.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', 0))

async def verificar_permissoes():
    """Verifica permissões do bot no grupo"""
    print("="*80)
    print("🔍 VERIFICANDO PERMISSÕES DO BOT")
    print("="*80)
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado no .env")
        return False
    
    if not GROUP_ID:
        print("❌ GROUP_ID não encontrado no .env")
        return False
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Pega informações do bot
        bot_info = await bot.get_me()
        print(f"\n🤖 Bot: @{bot_info.username}")
        print(f"📝 Nome: {bot_info.first_name}")
        print(f"🆔 ID: {bot_info.id}")
        
        # Pega informações do grupo
        print(f"\n📱 Verificando grupo {GROUP_ID}...")
        chat = await bot.get_chat(chat_id=GROUP_ID)
        print(f"📝 Nome do grupo: {chat.title}")
        print(f"🔖 Tipo: {chat.type}")
        
        # Verifica se é supergrupo
        if chat.type != 'supergroup':
            print(f"\n⚠️  PROBLEMA: O grupo não é um 'supergroup'!")
            print(f"   Tipo atual: {chat.type}")
            print(f"   Para criar tópicos, o grupo precisa ser um supergrupo.")
            return False
        
        # Verifica se tópicos estão habilitados
        if hasattr(chat, 'is_forum'):
            if chat.is_forum:
                print(f"✅ Tópicos estão HABILITADOS no grupo")
            else:
                print(f"\n⚠️  PROBLEMA: Tópicos NÃO estão habilitados!")
                print(f"   Para habilitar:")
                print(f"   1. Abra o grupo no Telegram")
                print(f"   2. Vá em Configurações do Grupo")
                print(f"   3. Ative 'Tópicos'")
                return False
        else:
            print(f"⚠️  Não foi possível verificar se tópicos estão habilitados")
        
        # Verifica permissões do bot
        print(f"\n🔐 Verificando permissões do bot...")
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=bot_info.id)
        print(f"📊 Status: {member.status}")
        
        if member.status not in ['administrator', 'creator']:
            print(f"\n⚠️  PROBLEMA: Bot não é administrador!")
            print(f"   Status atual: {member.status}")
            print(f"   Para criar tópicos, o bot precisa ser administrador.")
            return False
        
        print(f"✅ Bot é {member.status}")
        
        # Verifica permissões específicas
        if hasattr(member, 'can_manage_topics'):
            if member.can_manage_topics:
                print(f"✅ Bot pode GERENCIAR TÓPICOS")
            else:
                print(f"\n⚠️  PROBLEMA: Bot NÃO pode gerenciar tópicos!")
                print(f"   Para corrigir:")
                print(f"   1. Abra o grupo no Telegram")
                print(f"   2. Vá em Administradores")
                print(f"   3. Clique no bot")
                print(f"   4. Ative 'Gerenciar Tópicos'")
                return False
        else:
            print(f"⚠️  Não foi possível verificar permissão de gerenciar tópicos")
        
        print(f"\n" + "="*80)
        print(f"✅ TUDO OK! Bot pode criar tópicos!")
        print(f"="*80)
        return True
        
    except TelegramError as e:
        print(f"\n❌ Erro do Telegram: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

async def criar_topico_manual(nome_topico):
    """Cria um tópico manualmente"""
    print(f"\n🆕 Criando tópico: {nome_topico}")
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Tenta criar o tópico
        result = await bot.create_forum_topic(
            chat_id=GROUP_ID,
            name=nome_topico
        )
        
        topico_id = result.message_thread_id
        print(f"✅ Tópico criado com sucesso!")
        print(f"   Nome: {nome_topico}")
        print(f"   ID: {topico_id}")
        print(f"\n💡 Adicione no .env:")
        print(f"   TOPIC_{nome_topico.upper()}={topico_id}")
        
        return topico_id
        
    except TelegramError as e:
        print(f"❌ Erro ao criar tópico: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("="*80)
    print("🔧 VERIFICADOR DE PERMISSÕES E CRIADOR DE TÓPICOS")
    print("="*80)
    
    # Verifica permissões
    if not await verificar_permissoes():
        print("\n⚠️  Corrija os problemas acima antes de criar tópicos.")
        return
    
    # Pergunta se quer criar tópicos
    print("\n" + "="*80)
    print("Deseja criar os novos tópicos agora?")
    print("Tópicos necessários:")
    print("  1. OPERACIONAL")
    print("  2. MIDIA")
    print("  3. CONTROLES")
    print("="*80)
    
    resposta = input("\nCriar tópicos? (s/n): ").strip().lower()
    if resposta != 's':
        print("❌ Operação cancelada")
        return
    
    # Cria os tópicos
    topicos_criados = {}
    
    for nome in ['OPERACIONAL', 'MIDIA', 'CONTROLES']:
        topico_id = await criar_topico_manual(nome)
        if topico_id:
            topicos_criados[nome] = topico_id
    
    # Mostra resumo
    if topicos_criados:
        print("\n" + "="*80)
        print("✅ TÓPICOS CRIADOS COM SUCESSO!")
        print("="*80)
        print("\n📝 Adicione estas linhas no assistente-ranny/.env:")
        print()
        for nome, topico_id in topicos_criados.items():
            print(f"TOPIC_{nome}={topico_id}")
        print("\n" + "="*80)
    else:
        print("\n❌ Nenhum tópico foi criado")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
