# 📊 Nova Funcionalidade: Planilha de Entregadores Automática

## 🎯 O que faz?

O bot agora cria **automaticamente** planilhas Excel completas para controle de entregadores! Você só precisa **descrever a semana** em texto normal, e o bot faz todo o resto.

---

## 💡 Como usar?

### **Passo 1: Descreva a semana no tópico Chat**

Escreva do seu jeito, exemplo:

```
Oi bot, faz a planilha da semana pra mim

Segunda teve 3 entregadores e fizeram 20 entregas
Terça teve 3 entregadores e fizeram 18 entregas  
Quarta teve 3 entregadores e fizeram 22 entregas
Quinta teve 3 entregadores e fizeram 19 entregas
Sexta teve 4 entregadores, 3 chegaram no horário, fizeram 30 entregas
Sábado teve 4 entregadores, todos chegaram no horário, fizeram 35 entregas
Domingo teve 4 entregadores, 3 chegaram no horário, fizeram 28 entregas
```

### **Passo 2: Bot mostra resumo e pede confirmação**

O bot vai responder algo assim:

```
📊 Entendi! Vou criar a planilha:

Semana 10/02 a 16/02

• Segunda: 3 entregadores, 20 entregas = R$ 243,00
• Terça: 3 entregadores, 18 entregas = R$ 219,00
• Quarta: 3 entregadores, 22 entregas = R$ 267,00
• Quinta: 3 entregadores, 19 entregas = R$ 231,00
• Sexta: 4 entregadores, 3 no horário, 30 entregas = R$ 430,00
• Sábado: 4 entregadores, 4 no horário, 35 entregas = R$ 500,00
• Domingo: 4 entregadores, 3 no horário, 28 entregas = R$ 406,00

━━━━━━━━━━━━━━━━━━━━
💰 TOTAL DA SEMANA: R$ 2.296,00
━━━━━━━━━━━━━━━━━━━━

📋 Resumo:
• 7 dias
• 172 entregas

Está correto? (responda 'sim' ou 'confirma')
```

### **Passo 3: Confirme**

Responda simplesmente:
- "sim"
- "confirma"
- "ok"
- "correto"

### **Passo 4: Bot cria tudo automaticamente!**

O bot vai:
1. ✅ Criar planilha Excel **completa** com todas as fórmulas
2. ✅ Criar tópico novo (ex: "📊 Entregadores - Semana 10/02 a 16/02")
3. ✅ Enviar planilha no tópico
4. ✅ Confirmar que está pronto

---

## 📋 O que tem na planilha?

A planilha vem **100% pronta** com:

### **Colunas:**
- Dia da semana
- Número de entregadores
- Quantos chegaram até 18:10h
- Total de entregas
- Custo dos entregadores (calculado automaticamente)
- Bônus de horário (calculado automaticamente)
- Custo das entregas (calculado automaticamente)
- **TOTAL do dia** (calculado automaticamente)

### **Última linha:**
- **TOTAL GERAL** da semana (soma tudo)

### **Formatação:**
- ✅ Cores diferentes para fim de semana (amarelo)
- ✅ Linhas alternadas (cinza claro)
- ✅ Cabeçalhos azuis
- ✅ Total em verde
- ✅ Bordas em todas as células
- ✅ Valores em formato de moeda (R$)

---

## 💰 Regras de cálculo (automáticas)

O bot já sabe as regras e calcula tudo sozinho:

### **Segunda a Quinta:**
- R$ 1,00 por cada entregador escalado
- **SEM** bônus de horário

### **Sexta a Domingo:**
- R$ 10,00 por cada entregador escalado
- **+R$ 10,00** por cada um que chegar até 18:10h

### **Sempre:**
- R$ 12,00 por cada entrega realizada

---

## 🎨 Exemplo de planilha gerada:

```
┌──────────┬─────────────┬────────────┬──────────┬──────────────┬─────────────┬──────────────┬────────────┐
│ Dia      │ Entregadores│ Chegaram   │ Entregas │ Custo        │ Bônus       │ Custo        │ TOTAL      │
│          │             │ 18:10      │          │ Entregadores │ Horário     │ Entregas     │            │
├──────────┼─────────────┼────────────┼──────────┼──────────────┼─────────────┼──────────────┼────────────┤
│ Segunda  │ 3           │ -          │ 20       │ R$ 3,00      │ -           │ R$ 240,00    │ R$ 243,00  │
│ Terça    │ 3           │ -          │ 18       │ R$ 3,00      │ -           │ R$ 216,00    │ R$ 219,00  │
│ Quarta   │ 3           │ -          │ 22       │ R$ 3,00      │ -           │ R$ 264,00    │ R$ 267,00  │
│ Quinta   │ 3           │ -          │ 19       │ R$ 3,00      │ -           │ R$ 228,00    │ R$ 231,00  │
│ Sexta    │ 4           │ 3          │ 30       │ R$ 40,00     │ R$ 30,00    │ R$ 360,00    │ R$ 430,00  │
│ Sábado   │ 4           │ 4          │ 35       │ R$ 40,00     │ R$ 40,00    │ R$ 420,00    │ R$ 500,00  │
│ Domingo  │ 4           │ 3          │ 28       │ R$ 40,00     │ R$ 30,00    │ R$ 336,00    │ R$ 406,00  │
├──────────┼─────────────┼────────────┼──────────┼──────────────┼─────────────┼──────────────┼────────────┤
│ TOTAL    │ 24          │ 10         │ 172      │ R$ 152,00    │ R$ 100,00   │ R$ 2.064,00  │ R$ 2.316,00│
└──────────┴─────────────┴────────────┴──────────┴──────────────┴─────────────┴──────────────┴────────────┘
```

---

## ✨ Vantagens

### **Antes (manual):**
- ❌ Abrir Excel
- ❌ Criar tabela
- ❌ Digitar todos os dados
- ❌ Criar fórmulas
- ❌ Formatar células
- ❌ Salvar arquivo
- ❌ Enviar no Telegram
- ⏱️ **Tempo: 15-20 minutos**

### **Agora (automático):**
- ✅ Descrever a semana em texto
- ✅ Confirmar
- ✅ **Pronto!**
- ⏱️ **Tempo: 1 minuto**

---

## 🎯 Exemplos de uso

### **Exemplo 1: Semana normal**

```
Cria planilha da semana

Segunda: 3 entregadores, 20 entregas
Terça: 3 entregadores, 18 entregas
Quarta: 3 entregadores, 22 entregas
Quinta: 3 entregadores, 19 entregas
Sexta: 4 entregadores, 3 no horário, 30 entregas
Sábado: 4 entregadores, 4 no horário, 35 entregas
Domingo: 4 entregadores, 3 no horário, 28 entregas
```

### **Exemplo 2: Descrição mais natural**

```
Oi bot, preciso da planilha de entregadores

Essa semana foi assim:
- De segunda a quinta tivemos 3 entregadores por dia
- Segunda fizeram 20 entregas
- Terça 18 entregas
- Quarta 22 entregas
- Quinta 19 entregas

No fim de semana:
- Sexta: 4 entregadores, 3 chegaram cedo, 30 entregas
- Sábado: 4 entregadores, todos chegaram cedo, 35 entregas
- Domingo: 4 entregadores, 3 chegaram cedo, 28 entregas
```

### **Exemplo 3: Bem resumido**

```
Planilha da semana:
Seg-Qui: 3 entregadores, 20/18/22/19 entregas
Sex: 4 entregadores (3 no horário), 30 entregas
Sab: 4 entregadores (4 no horário), 35 entregas
Dom: 4 entregadores (3 no horário), 28 entregas
```

**A IA entende todos esses formatos!** 🤖

---

## ❓ Perguntas frequentes

### **P: E se eu errar algum número?**
R: Sem problema! O bot mostra o resumo antes de criar. Se estiver errado, responda "não" e descreva novamente.

### **P: Posso editar a planilha depois?**
R: Sim! É um arquivo Excel normal. Baixe e edite no computador ou celular.

### **P: O bot cria um tópico novo toda vez?**
R: Sim! Cada semana tem seu próprio tópico para ficar organizado.

### **P: E se eu não mencionar quem chegou no horário?**
R: O bot assume que ninguém chegou (0). Você pode corrigir depois na planilha.

### **P: Funciona para qualquer período?**
R: Sim! Pode ser uma semana, alguns dias, ou até um mês inteiro.

---

## 🚀 Implementação técnica

### **Arquivos modificados:**
1. `ai.py` - Nova função `extrair_dados_entregadores()`
2. `pdf_tools.py` - Nova função `criar_xlsx_entregadores()`
3. `bot.py` - Nova função `handle_planilha_entregadores()`

### **Tecnologias usadas:**
- **Gemini 2.0 Flash** - Extração de dados com IA
- **openpyxl** - Criação de planilhas Excel
- **Telegram Bot API** - Criação de tópicos e envio de arquivos

### **Fluxo:**
```
Ranny descreve → IA extrai dados → Bot calcula totais → 
Mostra resumo → Ranny confirma → Bot cria Excel → 
Bot cria tópico → Bot envia planilha → Pronto! ✅
```

---

## 📝 Teste

Para testar a funcionalidade:

```bash
cd assistente-ranny
python test_planilha_entregadores.py
```

Isso vai:
1. Testar extração de dados com IA
2. Criar um arquivo Excel de exemplo
3. Salvar como `teste_entregadores.xlsx`

---

## ✅ Status

- ✅ Extração de dados com IA implementada
- ✅ Criação de Excel formatado implementada
- ✅ Integração com bot implementada
- ✅ Criação de tópicos implementada
- ✅ Cálculos automáticos implementados
- ✅ Formatação com cores implementada
- ✅ Sistema de confirmação implementado
- ✅ Documentação completa

**PRONTO PARA USO!** 🎉

---

**Desenvolvido com ❤️ para facilitar a vida da Ranny!**
