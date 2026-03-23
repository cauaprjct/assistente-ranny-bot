"""
🚀 Iniciar Monitor - Versão Python
"""

import os
import sys
import subprocess
import time

print("=" * 60)
print("🚀 INICIANDO MONITOR DE ARQUIVOS")
print("=" * 60)
print()

# Verificar se já está rodando
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
    capture_output=True,
    text=True
)

if 'pythonw.exe' in result.stdout:
    print("⚠️ O monitor já está rodando!")
    print()
    print("Para parar, execute: python parar_monitor.py")
    input("\nPressione Enter para fechar...")
    sys.exit(0)

# Verificar se o script existe
script_path = os.path.join(os.path.dirname(__file__), 'monitor_arquivos_local.py')
if not os.path.exists(script_path):
    print(f"❌ Script não encontrado: {script_path}")
    input("\nPressione Enter para fechar...")
    sys.exit(1)

# Iniciar o monitor em segundo plano (invisível)
print("🔄 Iniciando monitor em segundo plano...")

if sys.platform == 'win32':
    # Windows: usar pythonw.exe (sem janela)
    subprocess.Popen(
        ['pythonw', script_path],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    )
else:
    # Linux/Mac: usar nohup
    subprocess.Popen(
        ['nohup', 'python', script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# Aguardar um pouco
time.sleep(2)

# Verificar se iniciou
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
    capture_output=True,
    text=True
)

if 'pythonw.exe' in result.stdout:
    print("✅ Monitor iniciado com sucesso!")
    print()
    print("📋 O monitor está rodando em segundo plano.")
    print("   Ele vai enviar automaticamente arquivos para o Telegram.")
    print()
    print("🔧 Comandos úteis:")
    print("   - Parar: python parar_monitor.py")
    print("   - Status: python status_monitor.py")
    print("   - Ver logs: notepad monitor_arquivos.log")
else:
    print("❌ Erro ao iniciar o monitor")
    print()
    print("Tente executar manualmente para ver o erro:")
    print(f"   python {script_path}")

print()
input("Pressione Enter para fechar...")
