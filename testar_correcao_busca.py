"""
Testa a correção do bug de busca
"""
import re

def processar_termo_busca(text_lower):
    """Processa o termo de busca removendo palavras desnecessárias"""
    termo = text_lower
    
    # Remove apenas palavras de busca, não palavras importantes
    # Usa regex com word boundaries para evitar remover partes de palavras
    palavras_remover = [
        r'\bcadê\b', r'\bcade\b', r'\bonde está\b', r'\bonde esta\b', r'\bonde tá\b', r'\bonde ta\b',
        r'\bprocura\b', r'\bbusca\b', r'\bbuscar\b', r'\bacha\b', r'\bachar\b',
        r'\bvocê tem\b', r'\btem algum\b',
        r'\bmostra\b', r'\bmostre\b', r'\bme dá\b', r'\bme da\b',
        r'\bo\b', r'\ba\b', r'\bos\b', r'\bas\b', r'\bum\b', r'\buma\b',
        r'\bguardados\b', r'\bsalvos\b', r'\barquivos\b', r'\bdocumentos\b'
    ]
    
    for pattern in palavras_remover:
        termo = re.sub(pattern, ' ', termo, flags=re.IGNORECASE)
    
    termo = ' '.join(termo.split())  # Remove espaços extras
    
    return termo


# Testes
testes = [
    ("buscar boleto", "boleto"),
    ("buscar nubank", "nubank"),
    ("cadê o contrato", "contrato"),
    ("procura nota fiscal", "nota fiscal"),
    ("onde está o comprovante", "comprovante"),
    ("busca arquivo pizza", "arquivo pizza"),
    ("mostra os documentos de 2024", "2024"),
    ("achar processo trabalhista", "processo trabalhista"),
]

print("=" * 60)
print("TESTE DE CORREÇÃO DO BUG DE BUSCA")
print("=" * 60)

todos_passaram = True

for entrada, esperado in testes:
    resultado = processar_termo_busca(entrada.lower())
    passou = resultado == esperado
    
    status = "✅ PASSOU" if passou else "❌ FALHOU"
    print(f"\n{status}")
    print(f"  Entrada:  '{entrada}'")
    print(f"  Esperado: '{esperado}'")
    print(f"  Obtido:   '{resultado}'")
    
    if not passou:
        todos_passaram = False

print("\n" + "=" * 60)
if todos_passaram:
    print("✅ TODOS OS TESTES PASSARAM!")
else:
    print("❌ ALGUNS TESTES FALHARAM")
print("=" * 60)
