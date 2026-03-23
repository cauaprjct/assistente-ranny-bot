"""
Script para indexar arquivos usando o relatório de upload
Lê o relatorio_upload_backup.json e adiciona ao banco de dados
COM message_id e topic_id para permitir reenvio e localização
"""

import json
import logging
from pathlib import Path
from datetime import datetime

import database_adapter as db

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def indexar_arquivos():
    """Indexa arquivos do relatório no banco de dados"""
    
    # Caminho do relatório
    relatorio_path = Path(__file__).parent.parent / 'relatorio_upload_backup.json'
    
    if not relatorio_path.exists():
        logger.error(f"Relatório não encontrado: {relatorio_path}")
        return
    
    # Carrega o relatório
    with open(relatorio_path, 'r', encoding='utf-8') as f:
        relatorio = json.load(f)
    
    arquivos = relatorio.get('arquivos', [])
    total = len(arquivos)
    
    logger.info(f"Relatório carregado: {total} arquivos")
    
    # Indexa cada arquivo
    indexados = 0
    erros = 0
    duplicados = 0
    
    for arquivo in arquivos:
        try:
            nome = arquivo.get('nome')
            categoria = arquivo.get('categoria', 'outros')
            topico_id = arquivo.get('topico')
            message_id = arquivo.get('message_id')
            file_id = arquivo.get('file_id')
            extensao = arquivo.get('extensao', '')
            caminho = arquivo.get('caminho_relativo', '')
            
            # Pula se não tem message_id ou file_id
            if not message_id or not file_id:
                logger.warning(f"Arquivo sem message_id ou file_id: {nome}")
                erros += 1
                continue
            
            # Verifica se já existe
            existing = db.buscar_documentos(nome)
            if existing:
                logger.debug(f"Já indexado: {nome}")
                duplicados += 1
                continue
            
            # Mapeia extensão para MIME type
            mime_types = {
                '.pdf': 'application/pdf',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.xls': 'application/vnd.ms-excel',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.txt': 'text/plain',
                '.csv': 'text/csv',
                '.xml': 'application/xml',
                '.zip': 'application/zip',
            }
            mime_type = mime_types.get(extensao.lower(), 'application/octet-stream')
            
            # Adiciona ao banco COM message_id e topic_id
            db.add_documento(
                tipo=mime_type,
                descricao=nome,
                file_id=file_id,
                categoria=categoria.lower(),
                message_id=message_id,   # IMPORTANTE: para localizar mensagem
                topic_id=topico_id,      # IMPORTANTE: para informar tópico
                dados_extraidos={
                    'caminho_original': caminho,
                    'indexado_de': 'relatorio_upload_backup.json',
                    'message_id': message_id,
                    'topic_id': topico_id
                }
            )
            
            indexados += 1
            
            if indexados % 50 == 0:
                logger.info(f"Progresso: {indexados} indexados...")
        
        except Exception as e:
            logger.error(f"Erro ao indexar {arquivo.get('nome')}: {e}")
            erros += 1
    
    logger.info("=" * 60)
    logger.info("INDEXAÇÃO CONCLUÍDA!")
    logger.info("=" * 60)
    logger.info(f"Total no relatório: {total}")
    logger.info(f"Indexados: {indexados}")
    logger.info(f"Duplicados: {duplicados}")
    logger.info(f"Erros: {erros}")
    logger.info("=" * 60)
    logger.info("Agora o bot pode:")
    logger.info("  - Buscar arquivos por nome/conteúdo")
    logger.info("  - Reenviar arquivos usando file_id")
    logger.info("  - Informar em qual tópico o arquivo está")


if __name__ == '__main__':
    indexar_arquivos()
