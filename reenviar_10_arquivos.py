"""
Reenvia os 10 primeiros arquivos para ter message_id e topic_id salvos
"""

import subprocess
import sys

print("=" * 80)
print("🔄 REENVIANDO 10 ARQUIVOS COM INDEXAÇÃO COMPLETA")
print("=" * 80)
print("\n⚠️  IMPORTANTE: Vou deletar as mensagens antigas do Telegram primeiro!")
print("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
input()

print("\n🚀 Executando upload...")
print("=" * 80)

# Executa o script de upload
subprocess.run([
    sys.executable,
    'organizar_backup_telegram.py'
], input=b's\n2\n')  # s = sim, 2 = 10 arquivos
