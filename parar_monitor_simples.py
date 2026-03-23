"""
⏹️ Parar Monitor Simples
"""

import subprocess
import sys

print("=" * 60)
print("⏹️  PARANDO MONITOR DE ARQUIVOS")
print("=" * 60)
print()

# Verificar se está rodando
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
    capture_output=True,
    text=True
)

if 'pythonw.exe' not in result.stdout:
    print("ℹ️ O monitor não está rodando.")
    input("\nPressione Enter para fechar...")
    sys.exit(0)

print("🔄 Parando monitor...")

# Parar todos os processos pythonw.exe
subprocess.run(['taskkill', '/F', '/IM', 'pythonw.exe'], 
               capture_output=True)

import time
time.sleep(1)

# Verificar se parou
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
    capture_output=True,
    text=True
)

if 'pythonw.exe' not in result.stdout:
    print("✅ Monitor parado com sucesso!")
else:
    print("⚠️ Alguns processos podem ainda estar rodando")
    print("   Tente fechar manualmente pelo Gerenciador de Tarefas")

print()
input("Pressione Enter para fechar...")
