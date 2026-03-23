"""
🚀 Instalador do Monitor Simples
Configura para iniciar automaticamente com o Windows
"""

import os
import sys
import subprocess
import winshell
from pathlib import Path

print("=" * 70)
print("🚀 INSTALADOR DO MONITOR SIMPLES")
print("=" * 70)
print()
print("Este instalador vai:")
print("  1. Criar atalho na pasta Inicializar")
print("  2. Configurar para rodar invisível (sem janela)")
print("  3. Iniciar automaticamente com o Windows")
print()
input("Pressione Enter para continuar...")
print()

# Obter caminhos
script_dir = Path(__file__).parent.absolute()
script_path = script_dir / "monitor_simples.py"
pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")

# Verificar se pythonw existe
if not os.path.exists(pythonw_path):
    print("❌ pythonw.exe não encontrado!")
    print(f"   Procurado em: {pythonw_path}")
    print()
    print("Solução: Reinstale o Python e marque 'Add Python to PATH'")
    input("\nPressione Enter para fechar...")
    sys.exit(1)

# Verificar se script existe
if not script_path.exists():
    print(f"❌ Script não encontrado: {script_path}")
    input("\nPressione Enter para fechar...")
    sys.exit(1)

print("=" * 70)
print("📋 VERIFICANDO INSTALAÇÃO")
print("=" * 70)
print()
print(f"✅ Python: {sys.executable}")
print(f"✅ PythonW: {pythonw_path}")
print(f"✅ Script: {script_path}")
print()

# Criar atalho na pasta Inicializar
print("=" * 70)
print("📁 CRIANDO ATALHO NA PASTA INICIALIZAR")
print("=" * 70)
print()

try:
    startup_folder = winshell.startup()
    shortcut_path = os.path.join(startup_folder, "Monitor Arquivos PC.lnk")
    
    # Criar atalho
    with winshell.shortcut(shortcut_path) as shortcut:
        shortcut.path = pythonw_path
        shortcut.arguments = f'"{script_path}"'
        shortcut.working_directory = str(script_dir)
        shortcut.description = "Monitor de Arquivos PC - Envia automaticamente para Telegram"
        shortcut.icon_location = (pythonw_path, 0)
    
    print(f"✅ Atalho criado: {shortcut_path}")
    print()
    
except Exception as e:
    print(f"❌ Erro ao criar atalho: {e}")
    print()
    print("Solução manual:")
    print(f"1. Pressione Win+R")
    print(f"2. Digite: shell:startup")
    print(f"3. Crie um atalho para: {pythonw_path}")
    print(f"4. Argumentos: \"{script_path}\"")
    input("\nPressione Enter para continuar...")

# Testar se está funcionando
print("=" * 70)
print("🧪 TESTANDO INSTALAÇÃO")
print("=" * 70)
print()

resposta = input("Deseja iniciar o monitor agora para testar? (s/n): ").strip().lower()

if resposta == 's':
    print()
    print("🔄 Iniciando monitor em segundo plano...")
    
    try:
        # Iniciar invisível
        subprocess.Popen(
            [pythonw_path, str(script_path)],
            cwd=str(script_dir),
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        import time
        time.sleep(2)
        
        # Verificar se está rodando
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
            capture_output=True,
            text=True
        )
        
        if 'pythonw.exe' in result.stdout:
            print("✅ Monitor iniciado com sucesso!")
            print()
            print("📋 O monitor está rodando em segundo plano (invisível).")
            print("   Salve um arquivo no Desktop ou Documentos para testar.")
        else:
            print("⚠️ Não foi possível verificar se o monitor iniciou.")
            print("   Verifique o arquivo monitor_simples.log")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")

print()
print("=" * 70)
print("✅ INSTALAÇÃO CONCLUÍDA!")
print("=" * 70)
print()
print("📋 O que foi feito:")
print("   ✅ Atalho criado na pasta Inicializar")
print("   ✅ Monitor configurado para rodar invisível")
print("   ✅ Vai iniciar automaticamente com o Windows")
print()
print("🔧 Comandos úteis:")
print("   - Parar: python parar_monitor.py")
print("   - Status: python status_monitor.py")
print("   - Ver logs: notepad monitor_simples.log")
print()
print("🎯 Próximos passos:")
print("   1. Reinicie o Windows para testar")
print("   2. Após login, aguarde 30 segundos")
print("   3. Salve um arquivo no Desktop")
print("   4. Verifique se aparece no Telegram!")
print()
print("=" * 70)

input("\nPressione Enter para fechar...")
