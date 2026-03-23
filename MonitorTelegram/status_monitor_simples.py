"""
📊 Status do Monitor Simples
"""

import subprocess
import os
from datetime import datetime

print("=" * 60)
print("📊 STATUS DO MONITOR DE ARQUIVOS")
print("=" * 60)
print()

# Verificar se está rodando
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
    capture_output=True,
    text=True
)

if 'pythonw.exe' in result.stdout:
    print("✅ STATUS: RODANDO")
    print()
    print("📋 Processos Python em segundo plano:")
    subprocess.run(['tasklist', '/FI', 'IMAGENAME eq pythonw.exe', '/FO', 'TABLE'])
else:
    print("⚠️ STATUS: PARADO")
    print()
    print("O monitor não está rodando.")
    print("Para iniciar: python iniciar_monitor_simples.py")

print()
print("=" * 60)
print("📁 ÚLTIMAS LINHAS DO LOG")
print("=" * 60)
print()

# Mostrar últimas 15 linhas do log
if os.path.exists("monitor_simples.log"):
    try:
        with open("monitor_simples.log", 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            ultimas = linhas[-15:] if len(linhas) > 15 else linhas
            for linha in ultimas:
                print(linha.rstrip())
    except Exception as e:
        print(f"Erro ao ler log: {e}")
else:
    print("ℹ️ Arquivo de log não encontrado.")
    print("O log será criado quando o monitor for iniciado.")

print()
print("=" * 60)
print("🔧 COMANDOS DISPONÍVEIS")
print("=" * 60)
print()
print("- python iniciar_monitor_simples.py  : Inicia o monitor")
print("- python parar_monitor_simples.py    : Para o monitor")
print("- python status_monitor_simples.py   : Mostra este status")
print("- notepad monitor_simples.log        : Abre o log completo")
print()

input("Pressione Enter para fechar...")
