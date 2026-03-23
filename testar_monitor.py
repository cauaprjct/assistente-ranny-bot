"""
🧪 Teste do Monitor - Versão Debug
Mostra TODOS os eventos que estão acontecendo
"""

import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Pastas para monitorar
PASTAS_MONITORADAS = [
    os.path.expanduser('~/Documents'),
    os.path.expanduser('~/Desktop'),
]

class MonitorDebug(FileSystemEventHandler):
    """Handler que mostra TODOS os eventos"""
    
    def on_any_event(self, event):
        """Mostra qualquer evento que acontecer"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        tipo = "DIR" if event.is_directory else "FILE"
        
        print(f"[{timestamp}] {event.event_type:12} | {tipo:4} | {event.src_path}")


def main():
    print("=" * 70)
    print("🔍 MONITOR DEBUG - Mostrando TODOS os eventos")
    print("=" * 70)
    print("\nPastas monitoradas:")
    
    observer = Observer()
    event_handler = MonitorDebug()
    
    for pasta in PASTAS_MONITORADAS:
        if os.path.exists(pasta):
            observer.schedule(event_handler, pasta, recursive=True)
            print(f"  ✅ {pasta}")
    
    print("\n" + "=" * 70)
    print("👀 Monitorando... Salve um arquivo Excel agora!")
    print("   Pressione Ctrl+C para parar")
    print("=" * 70)
    print()
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Parando monitor...")
        observer.stop()
    
    observer.join()
    print("✅ Monitor encerrado.")


if __name__ == "__main__":
    main()
