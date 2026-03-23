"""
🗑️ Limpar Hashes - Recomeçar do zero
"""

import os

arquivo_hashes = 'hashes_enviados.json'

if os.path.exists(arquivo_hashes):
    os.remove(arquivo_hashes)
    print(f"✅ Arquivo {arquivo_hashes} removido!")
    print("\nAgora o monitor vai considerar apenas arquivos")
    print("modificados nas últimas 24 horas como 'novos'.")
else:
    print(f"ℹ️ Arquivo {arquivo_hashes} não existe.")

print("\nPressione Enter para fechar...")
input()
