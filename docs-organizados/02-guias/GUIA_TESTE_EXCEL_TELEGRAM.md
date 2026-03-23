# 🧪 Guia de Teste - Correções Excel no Telegram

## ✅ Testes Locais Concluídos
Todos os 23 testes passaram localmente! As correções estão funcionando:
- ✅ Estilos preservados ao adicionar linhas
- ✅ Validação de limites ao remover linhas
- ✅ Integração entre funções

---

## 📱 Como Testar no Telegram (Bot no Render)

### 1️⃣ Criar uma Planilha Base

Envie para o bot:
```
cria planilha excel com:
Nome, Idade, Cidade
João, 25, São Paulo
Maria, 30, Rio de Janeiro
Pedro, 28, Belo Horizonte
```

O bot vai criar uma planilha formatada com bordas e estilos.

---

### 2️⃣ Testar Adição de Linha (COM ESTILOS)

**Responda à planilha** que o bot enviou com:
```
adiciona linha: Ana, 22, Curitiba
```

**Resultado esperado:**
- ✅ Nova linha adicionada
- ✅ Linha tem bordas (thin)
- ✅ Alinhamento correto
- ✅ Mantém formatação da planilha

---

### 3️⃣ Testar Remoção de Linha (COM VALIDAÇÃO)

**Responda à planilha** com:
```
remove linha 3
```

**Resultado esperado:**
- ✅ Linha 3 removida (Maria)
- ✅ Planilha reorganizada

**Teste de validação** - tente remover linha inválida:
```
remove linha 0
```
ou
```
remove linha 999
```

**Resultado esperado:**
- ✅ Bot retorna erro informativo
- ✅ Não quebra/trava
- ✅ Planilha não é corrompida

---

### 4️⃣ Testar Substituição de Texto

**Responda à planilha** com:
```
substitui "São Paulo" por "Sampa"
```

**Resultado esperado:**
- ✅ Texto substituído
- ✅ Bot informa quantas substituições foram feitas
- ✅ Estilos mantidos

---

### 5️⃣ Testar Múltiplas Operações

Crie uma planilha e faça várias operações em sequência:

1. Cria planilha
2. Adiciona 2 linhas
3. Remove 1 linha
4. Substitui texto
5. Adiciona mais 1 linha

**Resultado esperado:**
- ✅ Todas operações funcionam
- ✅ Estilos consistentes em toda planilha
- ✅ Sem erros ou travamentos

---

## 🎯 O Que Mudou (Antes vs Depois)

### ❌ ANTES (Problemas)
- Linhas adicionadas SEM bordas/estilos
- Remover linha 0 ou 999 causava erro
- Planilhas ficavam inconsistentes visualmente

### ✅ DEPOIS (Corrigido)
- Linhas adicionadas COM bordas e alinhamento
- Validação impede remoção de linhas inválidas
- Planilhas mantêm formatação profissional

---

## 📊 Comandos Rápidos para Teste

```
# Criar planilha
cria planilha excel com:
Produto, Preço
Café, 5.00
Pão, 3.50

# Adicionar linha
adiciona linha: Leite, 4.00

# Remover linha
remove linha 2

# Substituir
substitui "Café" por "Café Premium"

# Teste de erro (deve retornar mensagem amigável)
remove linha 0
remove linha 100
```

---

## 🔍 Verificação Visual

Após cada operação, **baixe a planilha** e abra no Excel/LibreOffice para verificar:

1. ✅ Todas células têm bordas
2. ✅ Alinhamento consistente
3. ✅ Cores alternadas (zebra stripes) se aplicável
4. ✅ Sem células vazias ou mal formatadas

---

## 🚀 Status Atual

- ✅ Código corrigido e testado localmente (23/23 testes)
- ✅ Push realizado para GitHub
- ✅ Render deve ter atualizado automaticamente
- ✅ Bot pronto para testes no Telegram

---

## 💡 Dica

Se encontrar algum problema:
1. Verifique os logs do Render
2. Confirme que não há bot local rodando (conflito)
3. Teste com planilhas pequenas primeiro
4. Reporte qualquer comportamento inesperado

**Bons testes! 🎉**
