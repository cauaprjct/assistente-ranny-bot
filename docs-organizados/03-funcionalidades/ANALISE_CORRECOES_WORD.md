# Análise de Correções e Melhorias - Word/DOCX

*Documento gerado em: 23/03/2026*
*Atualizado em: 23/03/2026*
*Baseado na análise sequencial do código*

---

## 📋 Resumo Executivo

Foram identificadas **7 correções** e **5 melhorias** nas funcionalidades de Word/DOCX do bot.

### ✅ Status das Correções Implementadas

| # | Correção | Status | Arquivo |
|---|----------|--------|---------|
| 1 | Listas numeradas (`1.` e `1)`) | ✅ IMPLEMENTADA | pdf_tools.py |
| 2 | Substituição case-insensitive | ✅ IMPLEMENTADA | pdf_tools.py |
| 3 | Runs divididos na substituição | ✅ IMPLEMENTADA | pdf_tools.py |
| 4 | Headers/footers em ler_docx | ✅ IMPLEMENTADA | pdf_tools.py, bot.py |
| 5 | Validação de templates | ✅ IMPLEMENTADA | docx_templates.py |
| 6 | Posição inicio/fim no handler | ✅ IMPLEMENTADA | bot.py |
| 7 | Função duplicar documento | ✅ IMPLEMENTADA | pdf_tools.py |

**7 de 7 correções implementadas.**

---

## 🔴 Correções Implementadas (Detalhes)

### 1. **[ALTA]** Listas numeradas em `criar_docx_texto` ✅

**Arquivo:** `pdf_tools.py`, função `criar_docx_texto`

**Solução implementada:**
```python
# CORREÇÃO #1: Adiciona suporte a listas numeradas
if re.match(r'^\d+[.\)]\s', p):
    # Lista numerada (1. ou 1) )
    item_texto = re.sub(r'^\d+[.\)]\s', '', p).strip()
    doc.add_paragraph(item_texto, style='List Number')
elif p.startswith('•') or p.startswith('-'):
    # Lista com símbolos (• ou -)
    item_texto = p.lstrip('•-').strip()
    doc.add_paragraph(item_texto, style='List Bullet')
```

---

### 2. **[ALTA]** Substituição case-insensitive ✅

**Arquivo:** `pdf_tools.py`, função `editar_docx_substituir`

**Solução implementada:**
```python
# CORREÇÃO #2: Usa padrão case-insensitive
texto_antigo_lower = texto_antigo.lower()

for para in doc.paragraphs:
    texto_para = para.text
    if texto_antigo_lower in texto_para.lower():
        # Substitui usando regex com flags=re.IGNORECASE
        run.text = re.sub(re.escape(texto_antigo), texto_novo, run.text, flags=re.IGNORECASE)
```

Agora "FGTS", "fgts" e "Fgts" são todos encontrados e substituídos.

---

### 3. **[MÉDIA]** Runs divididos na substituição ✅

**Arquivo:** `pdf_tools.py`, função `editar_docx_substituir`

**Solução implementada:**
```python
# CORREÇÃO #3: Lida melhor com runs divididos
if len(para.runs) > 1:
    # Texto dividido em múltiplos runs
    novo_texto = re.sub(re.escape(texto_antigo), texto_novo, para.text, flags=re.IGNORECASE)
    # Limpa todos os runs e recria com o texto novo
    for run in para.runs:
        run.text = ''
    if para.runs:
        para.runs[0].text = novo_texto
```

---

### 4. **[MÉDIA]** Headers/footers em `ler_docx` ✅

**Arquivo:** `pdf_tools.py`, função `ler_docx`

**Solução implementada:**
```python
# CORREÇÃO #4: Extrai headers e footers
for section in doc.sections:
    header = section.header
    if header.is_linked_to_previous == False:
        for para in header.paragraphs:
            if para.text.strip():
                headers.append(para.text)

    footer = section.footer
    if footer.is_linked_to_previous == False:
        for para in footer.paragraphs:
            if para.text.strip():
                footers.append(para.text)

return {
    ...
    'headers': headers,
    'footers': footers,
    'num_headers': len(headers),
    'num_footers': len(footers)
}
```

**Handler atualizado para exibir headers na resposta.**

---

### 5. **[MÉDIA]** Validação de templates ✅

**Arquivo:** `docx_templates.py`, função `renderizar_template`

**Solução implementada:**
```python
# CORREÇÃO #5: Valida variáveis obrigatórias
variaveis_obrigatorias = template_info.get('variaveis', [])
variaveis_faltantes = []

for var in variaveis_obrigatorias:
    if var not in contexto or not contexto[var]:
        variaveis_faltantes.append(var)

if variaveis_faltantes:
    logger.warning(f"Variáveis faltantes: {variaveis_faltantes}")
    # Preenche com placeholder visível
    for var in variaveis_faltantes:
        contexto[var] = f"[{var.upper()}]"
```

---

### 6. **[BAIXA]** Posição inicio/fim no handler ✅

**Arquivo:** `bot.py`, função `handle_docx_contexto`

**Solução implementada:**
```python
# CORREÇÃO #6: Suporta "adiciona no inicio:" e "adiciona no fim:"
match = re.search(r'adiciona\s+(?:no\s+)?(inicio|fim)?[:\s]+(.+)', text, re.IGNORECASE | re.DOTALL)
if match:
    posicao = match.group(1) or 'fim'
    texto_novo = match.group(2).strip()
```

Agora usuário pode usar:
- `adiciona: texto` → adiciona no fim
- `adiciona no fim: texto` → adiciona no fim
- `adiciona no inicio: texto` → adiciona no início

---

### 7. **[BAIXA]** Função duplicar documento ✅

**Arquivo:** `pdf_tools.py`, função `duplicar_docx`

**Solução implementada:**
```python
def duplicar_docx(docx_bytes: bytes, novo_nome: str = None) -> Optional[bytes]:
    """Duplica um documento DOCX"""
    doc = Document(io.BytesIO(docx_bytes))
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()
```

---

## 🟡 Melhorias Recomendadas (Não Implementadas)

### 1. Adicionar suporte a negrito/itálico no texto adicionado
### 2. Preview do documento antes de criar
### 3. Histórico de versões do documento
### 4. Suporte a tabelas simples na criação
### 5. Undo/Desfazer para edições

---

## 📁 Arquivos Modificados

- `assistente-ranny/pdf_tools.py`
  - Linhas ~14: Added `import re`
  - Linhas ~709-721: Listas numeradas
  - Linhas ~1170-1276: Substituição case-insensitive + runs divididos
  - Linhas ~1034-1095: Headers/footers em ler_docx
  - Linhas ~1316-1346: Função duplicar_docx

- `assistente-ranny/bot.py`
  - Linhas ~1089-1115: Headers na resposta de leitura
  - Linhas ~2317-2329: Posição inicio/fim

- `assistente-ranny/docx_templates.py`
  - Linhas ~95-118: Validação de templates

---

## ✅ Verificação de Sintaxe

Todos os arquivos foram compilados com `python -m py_compile` e estão sintaticamente corretos.

---

*Documento atualizado após implementação das correções.*
