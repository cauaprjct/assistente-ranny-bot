"""
Upload automatizado de 10 arquivos
"""

import subprocess
import sys

# Prepara as respostas: s (sim) + 2 (10 arquivos)
inputs = "s\n2\n"

print("🚀 Iniciando upload automatizado de 10 arquivos...")
print("=" * 80)

# Executa o script com as respostas automáticas
process = subprocess.Popen(
    [sys.executable, 'organizar_backup_telegram.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Envia as respostas
process.stdin.write(inputs)
process.stdin.flush()

# Lê a saída em tempo real
for line in process.stdout:
    print(line, end='')

process.wait()

print("\n" + "=" * 80)
print(f"✅ Processo concluído! Código de saída: {process.returncode}")
