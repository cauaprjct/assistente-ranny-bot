"""
Monitor Local de Arquivos - Envia automaticamente para o Telegram
Monitora pastas locais e envia arquivos Word/Excel/PDF quando salvos

Instalação:
pip install watchdog python-telegram-bot python-dotenv

Uso:
1. Configure o .env com BOT_TOKEN e CHAT_ID
2. Execute: python monitor_arquivos_local.py
3. O script ficará rodando em segundo plano
"""

import os
import time
import asyncio
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_arquivos.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurar encoding do console para UTF-8 no Windows
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
CHAT_ID = os.getenv('CHAT_ID')  # ID do chat/grupo do Telegram

# Mapeamento de extensões para tópicos (message_thread_id)
TOPICOS = {
    '.docx': int(os.getenv('TOPICO_DOCUMENTOS', '0')),
    '.xlsx': int(os.getenv('TOPICO_PLANILHAS', '0')),
    '.pdf': int(os.getenv('TOPICO_PDF', '0')),
    '.doc': int(os.getenv('TOPICO_DOCUMENTOS', '0')),
    '.xls': int(os.getenv('TOPICO_PLANILHAS', '0')),
}

# Pastas para monitorar (adicione as pastas que a Ranny usa)
PASTAS_MONITORADAS = [
    os.path.expanduser('~/OneDrive/Documentos'),
    os.path.expanduser('~/Documents'),
    os.path.expanduser('~/Desktop'),
]

# Extensões de arquivo para monitorar
EXTENSOES_MONITORADAS = {'.docx', '.xlsx', '.pdf', '.doc', '.xls'}

# Controle de arquivos recém-processados (evita duplicatas)
arquivos_processados = {}
TEMPO_COOLDOWN = 10  # segundos - reduzido pois agora captura moved+modified


class MonitorArquivos(FileSystemEventHandler):
    """Handler para eventos de sistema de arquivos"""
    
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def on_created(self, event):
        """Chamado quando um arquivo é criado"""
        if event.is_directory:
            return
        
        self.processar_arquivo(event.src_path, 'criado')
    
    def on_modified(self, event):
        """Chamado quando um arquivo é modificado"""
        if event.is_directory:
            return
        
        # Processar modificações (quando salva arquivo existente)
        self.processar_arquivo(event.src_path, 'salvo')
    
    def on_moved(self, event):
        """Chamado quando um arquivo é movido/renomeado"""
        if event.is_directory:
            return
        
        # Excel salva criando arquivo temporário e depois renomeando
        # Processar o arquivo de destino
        self.processar_arquivo(event.dest_path, 'salvo')
    
    def processar_arquivo(self, caminho, acao):
        """Processa um arquivo detectado"""
        try:
            # Obter nome do arquivo
            nome_arquivo = os.path.basename(caminho)
            
            # Ignorar arquivos temporários do Office (começam com ~$)
            if nome_arquivo.startswith('~$'):
                logger.debug(f"Arquivo temporario ignorado: {nome_arquivo}")
                return
            
            # Ignorar arquivos de backup
            if nome_arquivo.endswith('.bak') or nome_arquivo.endswith('.tmp'):
                logger.debug(f"Arquivo de backup ignorado: {nome_arquivo}")
                return
            
            # Verificar extensão
            extensao = Path(caminho).suffix.lower()
            if extensao not in EXTENSOES_MONITORADAS:
                return
            
            # Verificar se arquivo existe e não está sendo escrito
            if not os.path.exists(caminho):
                return
            
            # Aguardar arquivo ser completamente escrito
            time.sleep(3)
            
            # Verificar se o arquivo ainda existe e está acessível
            if not os.path.exists(caminho):
                logger.debug(f"Arquivo não existe mais: {nome_arquivo}")
                return
            
            # Verificar se consegue abrir (arquivo não está bloqueado)
            try:
                with open(caminho, 'rb') as f:
                    f.read(1)
            except (PermissionError, IOError):
                logger.debug(f"Arquivo ainda bloqueado: {nome_arquivo}")
                return
            
            # Verificar cooldown (evitar duplicatas)
            agora = time.time()
            if caminho in arquivos_processados:
                ultimo_envio = arquivos_processados[caminho]
                if agora - ultimo_envio < TEMPO_COOLDOWN:
                    logger.debug(f"Arquivo em cooldown: {caminho} (aguardando {TEMPO_COOLDOWN - (agora - ultimo_envio):.1f}s)")
                    return
            
            logger.info(f"Processando arquivo {acao}: {caminho} ({tamanho} bytes)")
            
            # Verificar tamanho do arquivo (Telegram tem limite de 50MB)
            tamanho = os.path.getsize(caminho)
            if tamanho == 0:
                logger.debug(f"Arquivo vazio ignorado: {caminho}")
                return
            
            if tamanho > 50 * 1024 * 1024:  # 50MB
                logger.warning(f"Arquivo muito grande (>50MB): {caminho}")
                self.enviar_mensagem_erro(caminho, "Arquivo muito grande (>50MB)")
                return
            
            # Enviar para o Telegram
            logger.info(f"Arquivo {acao}: {caminho} ({tamanho} bytes)")
            self.enviar_arquivo(caminho, extensao, acao)
            
            # Registrar envio
            arquivos_processados[caminho] = agora
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {caminho}: {e}")
    
    def enviar_arquivo(self, caminho, extensao, acao):
        """Envia arquivo para o Telegram"""
        try:
            nome_arquivo = os.path.basename(caminho)
            topico_id = TOPICOS.get(extensao, 0)
            
            # Preparar mensagem
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            mensagem = f"Arquivo {acao}: {nome_arquivo}\n{timestamp}"
            
            # Enviar arquivo
            with open(caminho, 'rb') as arquivo:
                if topico_id > 0:
                    # Enviar para tópico específico
                    self.loop.run_until_complete(
                        self.bot.send_document(
                            chat_id=CHAT_ID,
                            document=arquivo,
                            caption=mensagem,
                            message_thread_id=topico_id
                        )
                    )
                else:
                    # Enviar para chat principal
                    self.loop.run_until_complete(
                        self.bot.send_document(
                            chat_id=CHAT_ID,
                            document=arquivo,
                            caption=mensagem
                        )
                    )
            
            logger.info(f"OK: Arquivo enviado com sucesso: {nome_arquivo}")
            
        except TelegramError as e:
            logger.error(f"Erro do Telegram ao enviar {caminho}: {e}")
            self.enviar_mensagem_erro(caminho, str(e))
        except Exception as e:
            logger.error(f"Erro ao enviar arquivo {caminho}: {e}")
    
    def enviar_mensagem_erro(self, caminho, erro):
        """Envia mensagem de erro para o Telegram"""
        try:
            nome_arquivo = os.path.basename(caminho)
            mensagem = f"ERRO ao enviar arquivo: {nome_arquivo}\n\n{erro}"
            
            self.loop.run_until_complete(
                self.bot.send_message(
                    chat_id=CHAT_ID,
                    text=mensagem
                )
            )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {e}")


def verificar_configuracao():
    """Verifica se as configurações estão corretas"""
    if not BOT_TOKEN:
        logger.error("ERRO: BOT_TOKEN nao configurado no .env")
        return False
    
    if not CHAT_ID:
        logger.error("ERRO: CHAT_ID nao configurado no .env")
        return False
    
    # Verificar se pelo menos uma pasta existe
    pastas_existentes = [p for p in PASTAS_MONITORADAS if os.path.exists(p)]
    if not pastas_existentes:
        logger.error(f"ERRO: Nenhuma pasta monitorada existe: {PASTAS_MONITORADAS}")
        return False
    
    logger.info(f"OK: Configuracao OK")
    logger.info(f">> Pastas monitoradas: {pastas_existentes}")
    logger.info(f">> Extensoes: {EXTENSOES_MONITORADAS}")
    
    return True


def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info(">> Iniciando Monitor de Arquivos Local")
    logger.info("=" * 60)
    
    # Verificar configuração
    if not verificar_configuracao():
        logger.error("ERRO: Configuracao invalida. Encerrando.")
        return
    
    # Criar handler
    event_handler = MonitorArquivos()
    
    # Criar observer
    observer = Observer()
    
    # Adicionar pastas para monitorar
    for pasta in PASTAS_MONITORADAS:
        if os.path.exists(pasta):
            observer.schedule(event_handler, pasta, recursive=True)
            logger.info(f">> Monitorando: {pasta}")
    
    # Iniciar monitoramento
    observer.start()
    logger.info("OK: Monitor iniciado! Pressione Ctrl+C para parar.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(">> Parando monitor...")
        observer.stop()
    
    observer.join()
    logger.info("OK: Monitor encerrado.")


if __name__ == "__main__":
    main()
