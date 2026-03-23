"""
🚀 Iniciar Monitor Simples
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
    print("Para parar: python parar_monitor_simples.py")
    input("\nPressione Enter para fechar...")
    sys.exit(0)

# Verificar se o script existe
script_path = os.path.join(os.path.dirname(__file__), 'monitor_simples.py')
if not os.path.exists(script_path):
    print(f"❌ Script não encontrado: {script_path}")
    input("\nPressione Enter para fechar...")
    sys.exit(1)

# Obter pythonw.exe
pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
if not os.path.exists(pythonw_path):
    print("❌ pythonw.exe não encontrado!")
    print("   Usando python.exe (com janela visível)")
    pythonw_path = sys.executable

# Iniciar o monitor em segundo plano (invisível)
print("🔄 Iniciando monitor em segundo plano...")

try:
    subprocess.Popen(
        [pythonw_path, script_path],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
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
        print("   - Parar: python parar_monitor_simples.py")
        print("   - Status: python status_monitor_simples.py")
        print("   - Ver logs: notepad monitor_simples.log")
    else:
        print("⚠️ Não foi possível verificar se o monitor iniciou.")
        print("   Verifique o arquivo monitor_simples.log")
        
except Exception as e:
    print(f"❌ Erro ao iniciar o monitor: {e}")
    print()
    print("Tente executar manualmente para ver o erro:")
    print(f"   python {script_path}")

print()
input("Pressione Enter para fechar...")
