#!/usr/bin/env python3
"""
Script para analisar e organizar o BACKUP_ORGANIZADO no Telegram

Funcionalidades:
1. Escaneia todos os arquivos do backup
2. Analisa e classifica usando IA
3. Sugere mapeamento para tópicos do Telegram
4. Cria novos tópicos se necessário
5. Faz upload organizado dos arquivos
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Adiciona o diretório assistente-ranny ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistente-ranny'))

try:
    from dotenv import load_dotenv
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Erro ao importar bibliotecas: {e}")
    print("Execute: pip install python-dotenv google-generativeai")
    sys.exit(1)

# Importa database adapter para indexar arquivos
try:
    import database_adapter as db
    DB_DISPONIVEL = True
except ImportError as e:
    print(f"⚠️  Database adapter não disponível: {e}")
    DB_DISPONIVEL = False

# Importa telegram de forma mais robusta
try:
    from telegram import Bot
    from telegram.constants import ParseMode
    TELEGRAM_DISPONIVEL = True
except ImportError:
    print("⚠️  python-telegram-bot não disponível. Modo análise apenas.")
    TELEGRAM_DISPONIVEL = False
    Bot = None
    ParseMode = None

# Carrega variáveis de ambiente
load_dotenv('assistente-ranny/.env')

# Configurações
BACKUP_DIR = "BACKUP_ORGANIZADO"
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', 0))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Tópicos existentes
TOPICOS_EXISTENTES = {
    'CHAT': int(os.getenv('TOPIC_CHAT', 47)),
    'FINANCEIRO': int(os.getenv('TOPIC_FINANCEIRO', 2)),
    'EMPRESA': int(os.getenv('TOPIC_EMPRESA', 3)),
    'JURIDICO': int(os.getenv('TOPIC_JURIDICO', 5)),
    'PESSOAL': int(os.getenv('TOPIC_PESSOAL', 4)),
    'FUNCIONARIOS': int(os.getenv('TOPIC_FUNCIONARIOS', 6)),
    'MANUTENCAO': int(os.getenv('TOPIC_MANUTENCAO', 7)),
    'OUTROS': int(os.getenv('TOPIC_OUTROS', 8)),
    'OPERACIONAL': int(os.getenv('TOPIC_OPERACIONAL', 214)),
    'MIDIA': int(os.getenv('TOPIC_MIDIA', 215)),
    'CONTROLES': int(os.getenv('TOPIC_CONTROLES', 216)),
}

# Mapeamento de pastas para tópicos
MAPEAMENTO_PASTAS = {
    '01_EMPRESA_GRN_PIZZAS/DOCUMENTOS_EMPRESA': 'EMPRESA',
    '01_EMPRESA_GRN_PIZZAS/FISCAL': 'EMPRESA',
    '01_EMPRESA_GRN_PIZZAS/OPERACIONAL': 'OPERACIONAL',  # Novo tópico
    '01_EMPRESA_GRN_PIZZAS/RH_DEPARTAMENTO_PESSOAL': 'FUNCIONARIOS',
    '02_FINANCEIRO': 'FINANCEIRO',
    '03_PESSOAL_RANNY': 'PESSOAL',
    '04_JURIDICO': 'JURIDICO',
    '05_CURRICULOS': 'FUNCIONARIOS',
    '07_MIDIA': 'MIDIA',  # Novo tópico
    '08_PLANILHAS_CONTROLES': 'CONTROLES',  # Novo tópico
    '10_ARQUIVOS_TEMPORARIOS': None,  # Não enviar
    '11_OUTROS': 'OUTROS',
}

# Extensões suportadas
EXTENSOES_SUPORTADAS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.zip', '.rar', '.7z',
    '.mp3', '.mp4', '.avi', '.mov',
    '.csv', '.xml', '.json'
}

# Arquivos a ignorar
IGNORAR_ARQUIVOS = {
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    'roaming.lock', 'settings.dat'
}

class OrganizadorBackup:
    def __init__(self):
        self.bot = None
        self.genai_model = None
        self.arquivos_escaneados = []
        self.estatisticas = defaultdict(int)
        self.novos_topicos_necessarios = set()
        
    def inicializar(self):
        """Inicializa conexões com Telegram e Gemini"""
        print("🔧 Inicializando...")
        
        # Verifica configurações
        if not TELEGRAM_BOT_TOKEN:
            print("❌ TELEGRAM_BOT_TOKEN não encontrado no .env")
            return False
        if not GROUP_ID:
            print("❌ GROUP_ID não encontrado no .env")
            return False
        if not GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY não encontrado no .env")
            return False
            
        # Inicializa Telegram
        if TELEGRAM_DISPONIVEL:
            try:
                self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
                print("✅ Bot do Telegram conectado")
            except Exception as e:
                print(f"❌ Erro ao conectar no Telegram: {e}")
                return False
        else:
            print("⚠️  Telegram não disponível - modo análise apenas")
            
        # Inicializa Gemini
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini AI conectado")
        except Exception as e:
            print(f"⚠️  Gemini não disponível: {e}")
            self.genai_model = None
            
        return True
    
    def escanear_backup(self):
        """Escaneia todos os arquivos do backup"""
        print(f"\n📂 Escaneando {BACKUP_DIR}...")
        
        backup_path = Path(BACKUP_DIR)
        if not backup_path.exists():
            print(f"❌ Pasta {BACKUP_DIR} não encontrada!")
            return False
            
        for root, dirs, files in os.walk(backup_path):
            for filename in files:
                # Ignora arquivos temporários e ocultos
                if filename in IGNORAR_ARQUIVOS or filename.startswith('~$'):
                    continue
                    
                filepath = Path(root) / filename
                extensao = filepath.suffix.lower()
                
                # Verifica extensão
                if extensao not in EXTENSOES_SUPORTADAS:
                    self.estatisticas['ignorados_extensao'] += 1
                    continue
                
                # Verifica tamanho (limite 50MB do Telegram)
                tamanho_mb = filepath.stat().st_size / (1024 * 1024)
                if tamanho_mb > 50:
                    self.estatisticas['ignorados_tamanho'] += 1
                    continue
                
                # Determina categoria baseado no caminho
                caminho_relativo = str(filepath.relative_to(backup_path))
                categoria = self._determinar_categoria(caminho_relativo)
                
                self.arquivos_escaneados.append({
                    'caminho': str(filepath),
                    'nome': filename,
                    'extensao': extensao,
                    'tamanho_mb': round(tamanho_mb, 2),
                    'categoria': categoria,
                    'topico': self._mapear_topico(categoria),
                    'caminho_relativo': caminho_relativo
                })
                
                self.estatisticas['total_arquivos'] += 1
                self.estatisticas[f'ext_{extensao}'] += 1
                
                if categoria:
                    self.estatisticas[f'cat_{categoria}'] += 1
        
        print(f"✅ Escaneamento concluído: {self.estatisticas['total_arquivos']} arquivos")
        return True
    
    def _determinar_categoria(self, caminho):
        """Determina a categoria baseado no caminho do arquivo"""
        # Normaliza o caminho para usar / em vez de \
        caminho_normalizado = caminho.replace('\\', '/')
        
        for pasta, categoria in MAPEAMENTO_PASTAS.items():
            if caminho_normalizado.startswith(pasta):
                return categoria
        return 'OUTROS'
    
    def _mapear_topico(self, categoria):
        """Mapeia categoria para tópico do Telegram"""
        if categoria in TOPICOS_EXISTENTES:
            return TOPICOS_EXISTENTES[categoria]
        else:
            # Marca como novo tópico necessário
            if categoria and categoria != 'OUTROS':
                self.novos_topicos_necessarios.add(categoria)
            return None
    
    def _get_mime_type(self, extensao):
        """Retorna MIME type baseado na extensão"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.csv': 'text/csv',
            '.xml': 'application/xml',
            '.json': 'application/json',
        }
        return mime_types.get(extensao.lower(), 'application/octet-stream')
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas do escaneamento"""
        print("\n" + "="*80)
        print("📊 ESTATÍSTICAS DO BACKUP")
        print("="*80)
        
        print(f"\n📁 Total de arquivos: {self.estatisticas['total_arquivos']}")
        print(f"⚠️  Ignorados (extensão): {self.estatisticas.get('ignorados_extensao', 0)}")
        print(f"⚠️  Ignorados (tamanho >50MB): {self.estatisticas.get('ignorados_tamanho', 0)}")
        
        print("\n📂 Por categoria:")
        categorias = {}
        for key, value in self.estatisticas.items():
            if key.startswith('cat_'):
                cat = key.replace('cat_', '')
                categorias[cat] = value
        
        for cat in sorted(categorias.keys()):
            topico = TOPICOS_EXISTENTES.get(cat, 'NOVO TÓPICO')
            print(f"  • {cat:20} → {topico:15} ({categorias[cat]} arquivos)")
        
        print("\n📄 Por tipo de arquivo:")
        extensoes = {}
        for key, value in self.estatisticas.items():
            if key.startswith('ext_'):
                ext = key.replace('ext_', '')
                extensoes[ext] = value
        
        for ext in sorted(extensoes.keys(), key=lambda x: extensoes[x], reverse=True)[:10]:
            print(f"  • {ext:10} {extensoes[ext]:4} arquivos")
        
        if self.novos_topicos_necessarios:
            print(f"\n🆕 Novos tópicos necessários:")
            for topico in sorted(self.novos_topicos_necessarios):
                print(f"  • {topico}")
        
        print("\n" + "="*80)
    
    async def criar_novos_topicos(self):
        """Cria novos tópicos no Telegram se necessário"""
        if not self.novos_topicos_necessarios:
            return True
            
        print(f"\n🆕 Criando {len(self.novos_topicos_necessarios)} novos tópicos...")
        
        for topico_nome in sorted(self.novos_topicos_necessarios):
            try:
                # Cria tópico no grupo
                result = await self.bot.create_forum_topic(
                    chat_id=GROUP_ID,
                    name=topico_nome
                )
                topico_id = result.message_thread_id
                TOPICOS_EXISTENTES[topico_nome] = topico_id
                print(f"  ✅ {topico_nome} (ID: {topico_id})")
                await asyncio.sleep(1)  # Delay para não sobrecarregar
            except Exception as e:
                print(f"  ❌ Erro ao criar {topico_nome}: {e}")
                return False
        
        return True
    
    async def fazer_upload(self, limite=None, dry_run=False):
        """Faz upload dos arquivos para o Telegram"""
        if not TELEGRAM_DISPONIVEL or not self.bot:
            print("❌ Telegram não disponível. Use modo dry run para simular.")
            return 0, 0
            
        total = len(self.arquivos_escaneados)
        if limite:
            total = min(total, limite)
        
        print(f"\n📤 {'[DRY RUN] ' if dry_run else ''}Fazendo upload de {total} arquivos...")
        
        sucesso = 0
        erros = 0
        indexados = 0
        
        for i, arquivo in enumerate(self.arquivos_escaneados[:total], 1):
            try:
                # Determina tópico
                topico_id = arquivo['topico']
                if not topico_id:
                    categoria = arquivo['categoria']
                    topico_id = TOPICOS_EXISTENTES.get(categoria, TOPICOS_EXISTENTES['OUTROS'])
                
                # Prepara caption
                caption = f"📁 {arquivo['nome']}\n"
                caption += f"📂 Categoria: {arquivo['categoria']}\n"
                caption += f"📊 Tamanho: {arquivo['tamanho_mb']} MB"
                
                if dry_run:
                    print(f"  [{i}/{total}] {arquivo['nome']} → Tópico {topico_id}")
                else:
                    # Faz upload
                    with open(arquivo['caminho'], 'rb') as f:
                        result = await self.bot.send_document(
                            chat_id=GROUP_ID,
                            document=f,
                            caption=caption,
                            message_thread_id=topico_id
                        )
                    
                    # Salva message_id e file_id no registro
                    arquivo['message_id'] = result.message_id
                    arquivo['file_id'] = result.document.file_id
                    
                    # Indexa no banco de dados
                    if DB_DISPONIVEL:
                        try:
                            mime_type = self._get_mime_type(arquivo['extensao'])
                            db.add_documento(
                                tipo=mime_type,
                                descricao=arquivo['nome'],
                                file_id=result.document.file_id,
                                categoria=arquivo['categoria'],
                                message_id=result.message_id,
                                topic_id=topico_id,
                                dados_extraidos={
                                    'file_name': arquivo['nome'],
                                    'caminho_relativo': arquivo['caminho_relativo'],
                                    'tamanho_mb': arquivo['tamanho_mb'],
                                    'extensao': arquivo['extensao']
                                }
                            )
                            indexados += 1
                            print(f"  ✅ [{i}/{total}] {arquivo['nome']} (indexado)")
                        except Exception as e:
                            logger.error(f"Erro ao indexar {arquivo['nome']}: {e}")
                            print(f"  ✅ [{i}/{total}] {arquivo['nome']} (não indexado)")
                    else:
                        print(f"  ✅ [{i}/{total}] {arquivo['nome']}")
                    
                    sucesso += 1
                    await asyncio.sleep(2)  # Delay para não sobrecarregar
                    
            except Exception as e:
                print(f"  ❌ [{i}/{total}] {arquivo['nome']}: {e}")
                erros += 1
        
        print(f"\n{'='*80}")
        print(f"✅ Sucesso: {sucesso}")
        print(f"❌ Erros: {erros}")
        if DB_DISPONIVEL:
            print(f"📊 Indexados no banco: {indexados}")
        print(f"{'='*80}")
        
        return sucesso, erros
    
    def gerar_relatorio(self, filename='relatorio_upload_backup.json'):
        """Gera relatório em JSON"""
        relatorio = {
            'data': datetime.now().isoformat(),
            'estatisticas': dict(self.estatisticas),
            'topicos_existentes': TOPICOS_EXISTENTES,
            'novos_topicos': list(self.novos_topicos_necessarios),
            'total_arquivos': len(self.arquivos_escaneados),
            'arquivos': self.arquivos_escaneados
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {filename}")

async def main():
    print("="*80)
    print("🤖 ORGANIZADOR DE BACKUP PARA TELEGRAM")
    print("="*80)
    
    organizador = OrganizadorBackup()
    
    # Inicializa
    if not organizador.inicializar():
        return
    
    # Escaneia backup
    if not organizador.escanear_backup():
        return
    
    # Mostra estatísticas
    organizador.mostrar_estatisticas()
    
    # Pergunta se quer continuar
    print("\n" + "="*80)
    resposta = input("Deseja continuar? (s/n): ").strip().lower()
    if resposta != 's':
        print("❌ Operação cancelada")
        return
    
    # Cria novos tópicos se necessário
    if organizador.novos_topicos_necessarios:
        print("\n" + "="*80)
        resposta = input(f"Criar {len(organizador.novos_topicos_necessarios)} novos tópicos? (s/n): ").strip().lower()
        if resposta == 's':
            if not await organizador.criar_novos_topicos():
                print("❌ Erro ao criar tópicos")
                return
        else:
            print("⚠️  Arquivos sem tópico serão enviados para OUTROS")
    
    # Pergunta sobre upload
    print("\n" + "="*80)
    print("Opções de upload:")
    print("1. Fazer upload de TODOS os arquivos")
    print("2. Fazer upload de apenas 10 arquivos (teste)")
    print("3. Simular upload (dry run)")
    print("4. Cancelar")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == '1':
        await organizador.fazer_upload()
    elif opcao == '2':
        await organizador.fazer_upload(limite=10)
    elif opcao == '3':
        await organizador.fazer_upload(dry_run=True)
    else:
        print("❌ Operação cancelada")
        return
    
    # Gera relatório
    organizador.gerar_relatorio()
    
    print("\n✅ Processo concluído!")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
