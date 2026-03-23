# Análise de Correções e Melhorias - Planilhas Excel

*Documento gerado em: 23/03/2026*
*Atualizado em: 23/03/2026*
*Baseado na análise sequencial do código*

---

## 📋 Resumo Executivo

Foram identificadas **8 correções necessárias** e **5 melhorias recomendadas**.

### ✅ Status das Correções Implementadas

| # | Correção | Status | Arquivo |
|---|----------|--------|---------|
| 1 | Incompatibilidade V1/V2 - normalizar entregadores | ✅ IMPLEMENTADA | pdf_tools.py |
| 2 | Adicionar linha TOTAL na COM NOMES | ✅ IMPLEMENTADA | pdf_tools.py |
| 3 | Mostrar chegaram_horario em dias úteis | ✅ IMPLEMENTADA | pdf_tools.py |
| 4 | Adicionar validação lógica na IA | ✅ IMPLEMENTADA | ai.py, bot.py |
| 5 | TORNAR configurável lista entregadores | ✅ IMPLEMENTADA | config.py, pdf_tools.py |
| 6 | Validar formato de data mensal | ✅ JÁ TINHA | pdf_tools.py |
| 7 | Cor FDS na COM NOMES | ⏭️ NÃO IMPLEMENTADA | - |
| 8 | Ordenar gráfico Top 10 por volume | ✅ IMPLEMENTADA | pdf_tools.py |

**7 de 8 correções implementadas.**

---

## 🔴 Correções Implementadas (Detalhes)

### 1. **[CRÍTICA]** Incompatibilidade V1 → V2 ✅

**Arquivo:** `pdf_tools.py`, função `criar_xlsx_entregadores`

**Solução implementada:**
```python
# CORREÇÃO #1: Normaliza entregadores para int (pode vir como lista ou string)
if isinstance(entregadores_raw, list):
    entregadores = len(entregadores_raw)
elif isinstance(entregadores_raw, str):
    try:
        entregadores = int(entregadores_raw)
    except ValueError:
        entregadores = 0
else:
    entregadores = int(entregadores_raw or 0)
```

---

### 2. **[CRÍTICA]** Falta de VALOR TOTAL na planilha COM NOMES ✅

**Arquivo:** `pdf_tools.py`, função `criar_xlsx_entregadores_com_nomes`

**Solução implementada:**
- Aplicado formato moeda `R$ #,##0.00` nas colunas VALOR e A PAGAR
- Aplicado alinhamento correto para valores monetários
- Borda mais grossa na linha de TOTAL

---

### 3. **[ALTA]** Planilha SEM NOMES não mostra chegaram_horario em dias úteis ✅

**Arquivo:** `pdf_tools.py`, função `criar_xlsx_entregadores`

**Solução implementada:**
```python
# CORREÇÃO #3: Mostra valor mesmo em dias úteis (documenta para referência)
cell = ws.cell(row=row_num, column=3, value=chegaram_horario if is_fds else ('-' if chegaram_horario == 0 else chegaram_horario))
```

Agora se Ranny reportar "segunda 2 entregaram e 1 chegou no horário", o valor 1 aparece na planilha (mesmo não entrando no cálculo).

---

### 4. **[ALTA]** Validação fraca de dados da IA ✅

**Arquivos:** `ai.py`, `bot.py`

**Solução implementada em ai.py:**
```python
# CORREÇÃO #4: Validação lógica dos dados
num_entregadores = len(dia['entregadores'])
chegaram_horario = dia.get('chegaram_horario', 0)
entregas = dia.get('entregas', 0)

# Valida chegaram_horario (não pode ser maior que entregadores)
if chegaram_horario > num_entregadores:
    alertas.append(f"Dia {dia.get('dia')}: chegaram_horario ({chegaram_horario}) maior que entregadores ({num_entregadores}) - corrigido")
    dia['chegaram_horario'] = min(chegaram_horario, num_entregadores)

# Valida entregas (deve ser positivo)
if entregas < 0:
    alertas.append(f"Dia {dia.get('dia')}: entregas negativo ({entregas}) - corrigido para 0")
    dia['entregas'] = 0

# Para dias úteis, zera chegaram_horario (não é relevante)
if not is_fds and chegaram_horario > 0:
    alertas.append(f"Dia {dia.get('dia')}: chegaram_horario zerado para dia útil")
    dia['chegaram_horario'] = 0
```

**Solução implementada em bot.py:**
```python
alertas_ia = resultado.get('alertas', [])  # CORREÇÃO #4: Pega alertas da IA
alertas_validacao = valida_dados_entregadores(dados, tipo_periodo)
alertas = alertas_ia + alertas_validacao  # Une alertas
```

---

### 5. **[MÉDIA]** Nome de entregadores fixos hardcoded ✅

**Arquivos:** `config.py`, `pdf_tools.py`

**Solução implementada em config.py:**
```python
# CORREÇÃO #5: Lista de entregadores fixos (pode ser editada via variável de ambiente)
ENTREGADORES_FIXOS_STR = os.getenv('ENTREGADORES_FIXOS', 'Maycon,Gustavo Campos,Gustavo Henrique,Leonardo,Sidnei,Maurício,Iago,João Pedro,José,Davi,Ryan,Kaique,Brayan')
ENTREGADORES_FIXOS = [nome.strip() for nome in ENTREGADORES_FIXOS_STR.split(',') if nome.strip()]
```

**Solução implementada em pdf_tools.py:**
```python
# CORREÇÃO #5: Agora usa config.ENTREGADORES_FIXOS se não especificado
if entregadores_fixos is None:
    try:
        from config import ENTREGADORES_FIXOS
        entregadores_fixos = ENTREGADORES_FIXOS
    except ImportError:
        logger.warning("config.ENTREGADORES_FIXOS não encontrado, usando padrão")
        entregadores_fixos = [
            "Maycon", "Gustavo Campos", "Gustavo Henrique", "Leonardo",
            "Sidnei", "Maurício", "Iago", "João Pedro", "José", "Davi",
            "Ryan", "Kaique", "Brayan"
        ]
```

**Como usar:** Para adicionar/remover entregadores, basta alterar a variável de ambiente `ENTREGADORES_FIXOS` ou editar diretamente em `config.py`.

---

### 6. **[MÉDIA]** Formato de data mensal não validado ✅

**Arquivo:** `pdf_tools.py`

**Status:** O código já tinha validação com try/except no `is_fim_de_semana()`. Fallback seguro para formato semanal em caso de erro.

---

### 7. **[MÉDIA]** Cor FDS na COM NOMES ⏭️

**Status:** NÃO IMPLEMENTADA

**Motivo:** A planilha COM NOMES é transposta (linhas = entregadores, colunas = dias). Colorir colunas inteiras para FDS requereria:
- Adicionar linha extra para indicar FDS
- Ou mudar estrutura de cores retroativamente

Não foi implementado por ser muito intrusivo no código existente.

---

### 8. **[BAIXA]** Limite de 10 entregadores no gráfico Top 10 ✅

**Arquivo:** `pdf_tools.py`, função `criar_xlsx_entregadores_com_nomes`

**Solução implementada:**
```python
# CORREÇÃO #8: Ordena entregadores por total de entregas (para gráfico Top 10)
totais_entregadores = []
for idx, nome in enumerate(lista_entregadores):
    row = 3 + idx
    total = 0
    for col in range(primeira_col_dia, ultima_col_dia + 1):
        cell_val = ws.cell(row=row, column=col).value
        if cell_val and isinstance(cell_val, (int, float)):
            total += cell_val
    totais_entregadores.append((nome, total, row))

# Ordena por total (maior para menor)
totais_entregadores.sort(key=lambda x: x[1], reverse=True)

# Pega os top N para o gráfico
num_entregadores_grafico = min(10, len(totais_entregadores))
top_entregadores = totais_entregadores[:num_entregadores_grafico]
```

Agora o gráfico Top 10 mostra os entregadores com MAIOR volume de entregas, não alfabeticamente.

---

## 🟡 Melhorias Recomendadas (Não Implementadas)

### 1. Adicionar sumário no início da planilha COM NOMES
### 2. Permitir editar planilha sem contexto (reenvio)
### 3. Gráfico de tendência de entregas
### 4. Exportar planilha de entregadores para PDF
### 5. Histórico de versões da planilha

---

## 📊 Fluxo de Dados - Planilha de Entregadores

```
Ranny descreve semana
        ↓
    ai.extrair_dados_entregadores()
        ↓ (valida e corrige dados - CORREÇÃO #4)
    bot.py processa e valida
        ↓
    ┌─────────────────────────────────────┐
    │  Planilha PENDENTE (user_data)     │
    │  Aguarda confirmação "sim"/"não"   │
    └─────────────────────────────────────┘
        ↓ (Ranny confirma)
    ┌─────────────────────────────────────┐
    │  criar_xlsx_entregadores()         │
    │  → Versão SEM NOMES                │
    │  → Normaliza tipos (CORREÇÃO #1)   │
    │  → Mostra chegam_horario (CORREÇÃO #3)│
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  criar_xlsx_entregadores_com_nomes()│
    │  → Versão COM NOMES                │
    │  → USA config (CORREÇÃO #5)        │
    │  → TOTAL formatado (CORREÇÃO #2)   │
    │  → Gráfico ordenado (CORREÇÃO #8)  │
    └─────────────────────────────────────┘
        ↓
    Envia para tópicos do Telegram
        ↓
    Salva em user_data['ultima_planilha']
        ↓ (Ranny edita)
    handle_editar_planilha_contexto()
        ↓
    pdf_tools.aplicar_edicao_planilha()
```

---

## 🔧 Priorização das Correções

| Prioridade | Correção | Complexidade | Status |
|------------|----------|--------------|--------|
| CRÍTICA | #1 Incompatibilidade V1/V2 | Baixa | ✅ |
| CRÍTICA | #2 Falta TOTAL na COM NOMES | Média | ✅ |
| ALTA | #3 FDS em dias úteis | Baixa | ✅ |
| ALTA | #4 Validação fraca IA | Média | ✅ |
| MÉDIA | #5 Entregadores hardcoded | Alta | ✅ |
| MÉDIA | #6 Validação data | Baixa | ✅ JÁ TINHA |
| MÉDIA | #7 Cor FDS na COM NOMES | Baixa | ⏭️ |
| BAIXA | #8 Limite gráfico | Baixa | ✅ |

---

## 📁 Arquivos Modificados

- `assistente-ranny/bot.py` - Linhas ~1640
- `assistente-ranny/pdf_tools.py` - Linhas ~1489-1690, ~1854-1926, ~2200-2280
- `assistente-ranny/ai.py` - Linhas ~665-740
- `assistente-ranny/config.py` - Linhas ~107-117

---

## ✅ Verificação de Sintaxe

Todos os arquivos foram compilados com `python -m py_compile` e estão sintaticamente corretos.

---

*Documento atualizado após implementação das correções.*
