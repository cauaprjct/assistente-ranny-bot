"""
📁 Monitor Simples de Arquivos - Versão Polling
Escaneia pastas a cada 30 segundos e envia arquivos novos/modificados

MUITO MAIS SIMPLES E CONFIÁVEL que watchdog!
"""

import os
import time
import json
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_simples.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurar encoding do console
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Mapeamento de extensões para tópicos
# Se TOPICO_PC_LOCAL estiver definido, usa ele para tudo
TOPICO_PC_LOCAL = os.getenv('TOPICO_PC_LOCAL')

if TOPICO_PC_LOCAL:
    # Usar tópico único para todos os arquivos do PC
    TOPICO_PC_LOCAL = int(TOPICO_PC_LOCAL)
    logger.info(f"Modo: Tópico único (ID: {TOPICO_PC_LOCAL})")
else:
    # Usar tópicos separados por tipo de arquivo
    TOPICOS = {
        '.docx': int(os.getenv('TOPICO_DOCUMENTOS', '3')),
        '.xlsx': int(os.getenv('TOPICO_PLANILHAS', '216')),
        '.pdf': int(os.getenv('TOPICO_PDF', '2')),
        '.doc': int(os.getenv('TOPICO_DOCUMENTOS', '3')),
        '.xls': int(os.getenv('TOPICO_PLANILHAS', '216')),
    }

# Pastas para monitorar
PASTAS_MONITORADAS = [
    os.path.expanduser('~/Documents'),
    os.path.expanduser('~/Desktop'),
]

# Extensões de arquivo para monitorar
EXTENSOES_MONITORADAS = {'.docx', '.xlsx', '.pdf', '.doc', '.xls'}

# Intervalo de verificação (segundos)
INTERVALO_VERIFICACAO = 30

# Arquivo para salvar hashes dos arquivos já enviados
ARQUIVO_HASHES = 'hashes_enviados.json'


def calcular_hash(caminho):
    """Calcula hash MD5 de um arquivo"""
    try:
        hash_md5 = hashlib.md5()
        with open(caminho, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Erro ao calcular hash de {caminho}: {e}")
        return None


def carregar_hashes():
    """Carrega hashes dos arquivos já enviados"""
    if os.path.exists(ARQUIVO_HASHES):
        try:
            with open(ARQUIVO_HASHES, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar hashes: {e}")
            return {}
    return {}


def salvar_hashes(hashes):
    """Salva hashes dos arquivos enviados"""
    try:
        with open(ARQUIVO_HASHES, 'w', encoding='utf-8') as f:
            json.dump(hashes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar hashes: {e}")


def escanear_arquivos():
    """Escaneia pastas e retorna lista de arquivos relevantes (modificados nas últimas 24h)"""
    arquivos = []
    
    # Timestamp de 24 horas atrás
    agora = time.time()
    limite_24h = agora - (24 * 60 * 60)
    
    for pasta in PASTAS_MONITORADAS:
        if not os.path.exists(pasta):
            continue
        
        try:
            for root, dirs, files in os.walk(pasta):
                for arquivo in files:
                    # Ignorar arquivos temporários
                    if arquivo.startswith('~$') or arquivo.startswith('.'):
                        continue
                    
                    # Verificar extensão
                    extensao = Path(arquivo).suffix.lower()
                    if extensao not in EXTENSOES_MONITORADAS:
                        continue
                    
                    caminho_completo = os.path.join(root, arquivo)
                    
                    # Verificar se arquivo está acessível
                    try:
                        tamanho = os.path.getsize(caminho_completo)
                        if tamanho == 0:
                            continue
                        
                        # NOVO: Verificar data de modificação
                        mtime = os.path.getmtime(caminho_completo)
                        if mtime < limite_24h:
                            # Arquivo antigo (mais de 24h), ignorar
                            continue
                        
                        arquivos.append({
                            'caminho': caminho_completo,
                            'nome': arquivo,
                            'extensao': extensao,
                            'tamanho': tamanho,
                            'modificado': mtime
                        })
                    except (PermissionError, FileNotFoundError):
                        continue
                        
        except Exception as e:
            logger.error(f"Erro ao escanear pasta {pasta}: {e}")
    
    return arquivos


async def enviar_arquivo(bot, arquivo_info, hash_arquivo):
    """Envia arquivo para o Telegram"""
    try:
        caminho = arquivo_info['caminho']
        nome = arquivo_info['nome']
        extensao = arquivo_info['extensao']
        tamanho = arquivo_info['tamanho']
        
        # Verificar tamanho (Telegram tem limite de 50MB)
        if tamanho > 50 * 1024 * 1024:
            logger.warning(f"Arquivo muito grande (>50MB): {nome}")
            return False
        
        # Obter tópico
        if TOPICO_PC_LOCAL:
            # Usar tópico único para todos os arquivos
            topico_id = TOPICO_PC_LOCAL
        else:
            # Usar tópico específico por tipo de arquivo
            topico_id = TOPICOS.get(extensao, 0)
        
        # Preparar mensagem
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        mensagem = f"Arquivo: {nome}\n{timestamp}"
        
        # Enviar arquivo
        with open(caminho, 'rb') as arquivo:
            if topico_id > 0:
                await bot.send_document(
                    chat_id=CHAT_ID,
                    document=arquivo,
                    caption=mensagem,
                    message_thread_id=topico_id
                )
            else:
                await bot.send_document(
                    chat_id=CHAT_ID,
                    document=arquivo,
                    caption=mensagem
                )
        
        logger.info(f"OK: Arquivo enviado: {nome}")
        return True
        
    except TelegramError as e:
        logger.error(f"Erro do Telegram ao enviar {nome}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar arquivo {nome}: {e}")
        return False


async def verificar_e_enviar():
    """Verifica arquivos e envia os novos/modificados"""
    logger.info(">> Verificando arquivos...")
    
    # Carregar hashes dos arquivos já enviados
    hashes_enviados = carregar_hashes()
    
    # Escanear arquivos
    arquivos = escanear_arquivos()
    logger.info(f"   Encontrados {len(arquivos)} arquivos")
    
    # Criar bot
    bot = Bot(token=BOT_TOKEN)
    
    # Verificar cada arquivo
    novos_enviados = 0
    for arquivo_info in arquivos:
        caminho = arquivo_info['caminho']
        nome = arquivo_info['nome']
        
        # Calcular hash
        hash_atual = calcular_hash(caminho)
        if not hash_atual:
            continue
        
        # Verificar se já foi enviado
        hash_salvo = hashes_enviados.get(caminho)
        
        if hash_salvo == hash_atual:
            # Arquivo já foi enviado e não mudou
            continue
        
        # Arquivo novo ou modificado - enviar!
        logger.info(f"   Novo/modificado: {nome}")
        
        if await enviar_arquivo(bot, arquivo_info, hash_atual):
            # Salvar hash
            hashes_enviados[caminho] = hash_atual
            novos_enviados += 1
            
            # Aguardar um pouco entre envios
            await asyncio.sleep(1)
    
    # Salvar hashes atualizados
    if novos_enviados > 0:
        salvar_hashes(hashes_enviados)
        logger.info(f"OK: {novos_enviados} arquivo(s) enviado(s)")
    else:
        logger.info("   Nenhum arquivo novo")


async def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info(">> Monitor Simples de Arquivos")
    logger.info("=" * 60)
    
    # Verificar configuração
    if not BOT_TOKEN:
        logger.error("ERRO: BOT_TOKEN nao configurado no .env")
        return
    
    if not CHAT_ID:
        logger.error("ERRO: CHAT_ID nao configurado no .env")
        return
    
    pastas_existentes = [p for p in PASTAS_MONITORADAS if os.path.exists(p)]
    if not pastas_existentes:
        logger.error(f"ERRO: Nenhuma pasta monitorada existe")
        return
    
    logger.info(f"OK: Configuracao OK")
    logger.info(f">> Pastas: {pastas_existentes}")
    logger.info(f">> Extensoes: {EXTENSOES_MONITORADAS}")
    logger.info(f">> Intervalo: {INTERVALO_VERIFICACAO}s")
    logger.info(f">> Filtro: Apenas arquivos modificados nas ultimas 24h")
    logger.info("=" * 60)
    logger.info("OK: Monitor iniciado!")
    logger.info(f"   Verificando a cada {INTERVALO_VERIFICACAO} segundos...")
    logger.info("   Pressione Ctrl+C para parar")
    logger.info("=" * 60)
    
    try:
        while True:
            await verificar_e_enviar()
            await asyncio.sleep(INTERVALO_VERIFICACAO)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info(">> Parando monitor...")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    
    logger.info("OK: Monitor encerrado.")


if __name__ == "__main__":
    asyncio.run(main())
