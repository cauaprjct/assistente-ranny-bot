"""
Script para indexar arquivos usando o relatório de upload
Lê o relatorio_upload_backup.json e adiciona ao banco de dados
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import database_adapter as db

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔍 INDEXADOR DE ARQUIVOS DO RELATÓRIO")
    logger.info("=" * 60)
    
    # Lê o relatório
    relatorio_path = Path('../relatorio_upload_backup.json')
    
    if not relatorio_path.exists():
        logger.error(f"❌ Relatório não encontrado: {relatorio_path}")
        return
    
    logger.info(f"📄 Lendo relatório: {relatorio_path}")
    
    with open(relatorio_path, 'r', encoding='utf-8') as f:
        relatorio = json.load(f)
    
    arquivos = relatorio.get('arquivos_enviados', [])
    logger.info(f"📁 Total de arquivos no relatório: {len(arquivos)}")
    
    # Indexa cada arquivo
    indexados = 0
    erros = 0
    duplicados = 0
    
    for arquivo in arquivos:
        try:
            nome = arquivo.get('nome', 'Sem nome')
            categoria = arquivo.get('categoria', 'outros')
            topico_id = arquivo.get('topico_id')
            message_id = arquivo.get('message_id')
            file_id = arquivo.get('file_id')
            
            if not message_id or not file_id:
                logger.warning(f"⚠️  Arquivo sem message_id ou file_id: {nome}")
                erros += 1
                continue
            
            # Verifica se já existe
            existing = db.buscar_documentos(nome)
            if existing:
                logger.debug(f"⏭️  Já indexado: {nome}")
                duplicados += 1
                continue
            
            # Determina o tipo MIME
            ext = Path(nome).suffix.lower()
            mime_types = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.txt': 'text/plain',
            }
            mime_type = mime_types.get(ext, 'application/octet-stream')
            
            # Adiciona ao banco
            db.add_documento(
                tipo=mime_type,
                descricao=nome,
                file_id=file_id,
                categoria=categoria,
                message_id=message_id,
                topic_id=topico_id,
                dados_extraidos={
                    'file_name': nome,
                    'categoria_original': categoria
                }
            )
            
            indexados += 1
            
            if indexados % 50 == 0:
                logger.info(f"📊 Progresso: {indexados} indexados...")
            
        except Exception as e:
            logger.error(f"❌ Erro ao indexar {arquivo.get('nome')}: {e}")
            erros += 1
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ INDEXAÇÃO CONCLUÍDA!")
    logger.info("=" * 60)
    logger.info(f"📊 Estatísticas:")
    logger.info(f"   ✅ Indexados: {indexados}")
    logger.info(f"   ⏭️  Duplicados: {duplicados}")
    logger.info(f"   ❌ Erros: {erros}")
    logger.info(f"   📁 Total: {len(arquivos)}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
