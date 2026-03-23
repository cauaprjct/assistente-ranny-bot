# 🤖 O Que o Bot Faz - Revisão Completa

*Documento atualizado em: 23/03/2026*
*Baseado na análise do código: bot.py (2.640+ linhas)*

---

## 📋 Resumo das Funcionalidades

O **Assistente Ranny** é um bot Telegram inteligente que processa linguagem natural e gerencia todos os aspectos do negócio da GRN Pizzas através de conversa simples.

---

## 1. 💰 Controle Financeiro

### 1.1 Fechamento de Caixa
```
Ranny: fechei 4500
Bot: ✅ Fechamento registrado!

📊 Hoje: R$ 4.500,00
📅 Ontem: R$ 3.200,00 (📈 +40,6%)
📆 Semana: R$ 18.400,00

🎉 Melhor que ontem!
```

**Como funciona:**
- Detecta padrões: "fechei", "fechamento", "caixa" + valor
- Compara com dia anterior
- Acumula total da semana

### 1.2 Alertas de Vencimentos
```
Ranny: paguei a luz
Bot: ✅ Marcado como pago!
📄 Conta de Luz
💰 R$ 890,00

🔄 Próximo vencimento criado: 20/04/2026
```

**Como funciona:**
- Detecta quando usuário paga algo ("paguei", "pago")
- Busca vencimento pendente no banco
- Cria automaticamente próximo vencimento

---

## 2. 📝 Sistema de Lembretes

### 2.1 Criar Lembrete
```
Ranny: me lembra amanhã de pagar o FGTS
Bot: ✅ Lembrete criado!

📅 24/03/2026 às 09:00
📝 pagar o FGTS
```

**Como funciona:**
- Detecta verbos: "lembra", "lembre", "avisa", "avise"
- Parse de data/hora inteligente (amanhã, segunda, dia 15, às 14h)
- Suporta recorrência: "todo dia 7", "todo mês"

### 2.2 Listar/Cancelar Lembretes
```
Ranny: quais meus lembretes?
Bot: 📝 Seus lembretes ativos:

1. 📌 pagar o FGTS
   📅 24/03/2026 às 09:00

2. 📌 reunião com contador
   📅 25/03/2026 às 10:00
   🔄 Recorrente: mensal
```

```
Ranny: cancela lembrete do FGTS
Bot: ✅ Lembrete cancelado: pagar o FGTS
```

---

## 3. 📄 Gestão de Documentos

### 3.1 Receber e Classificar Documentos
```
Ranny: [envia foto de boleto]
Bot: 📄 Boleto Identificado

🏢 CPFL - Conta de Luz
💰 R$ 890,00
📅 Vence: 20/03/2026

✅ Salvo em Financeiro!
```

**Tipos suportados:**
- Fotos de boletos (extrai: valor, vencimento, código de barras)
- Comprovantes de pagamento
- Notas fiscais
- PDFs, DOCX, XLSX

**Categorias automáticas:**
- Financeiro
- Empresa
- Funcionários
- Jurídico
- Pessoal
- Outros

### 3.2 Buscar Documentos
```
Ranny: cadê o contrato do João?
Bot: Encontrei 2 arquivo(s) para 'contrato João':

1. contrato_locacao_joao.pdf
   Categoria: Jurídico

2. contrato_prestacao_servicos.pdf
   Categoria: Jurídico

Responda com o número (ex: 'manda o 1') para receber o arquivo.
```

### 3.3 Reenviar Documento
```
Ranny: manda o 1
Bot: 📁 contrato_locacao_joao.pdf

📂 Categoria: Jurídico
📅 Salvo em: 15/01/2026

💡 Você pode encontrar este arquivo no tópico Jurídico do grupo!
```

---

## 4. 📊 Planilhas de Entregadores

### 4.1 Criar Planilha Semanal
```
Ranny: Segunda teve 3 entregadores e 20 entregas
       Terça teve 3 entregadores e 18 entregas
       Quarta teve 2 entregadores e 15 entregas
       Quinta teve 3 entregadores e 22 entregas
       Sexta teve 4 entregadores e 30 entregas
       2 chegaram no horário
       Sábado teve 4 entregadores e 35 entregas
       3 chegaram no horário
       Domingo teve 3 entregadores e 25 entregas

Bot: ⏳ Analisando dados...

📊 Entendi! Vou criar a planilha:

SEMANA

• Segunda: 3 entregadores, 20 entregas = R$ 265,00
• Terça: 3 entregadores, 18 entregas = R$ 258,00
• Quarta: 2 entregadores, 15 entregas = R$ 204,00
• Quinta: 3 entregadores, 22 entregas = R$ 276,00
• Sexta: 4 entregadores, 2 no horário, 30 entregas = R$ 474,00
• Sábado: 4 entregadores, 3 no horário, 35 entregas = R$ 524,00
• Domingo: 3 entregadores, 25 entregas = R$ 325,00

━━━━━━━━━━━━━━━━━━━━
💰 TOTAL: R$ 2.326,00
━━━━━━━━━━━━━━━━━━━━

📋 Resumo:
• 7 dias
• 165 entregas

*Está correto?*
• Digite 'sim' para confirmar
• Digite 'não' para cancelar
• Ou me diga o que precisa corrigir
```

### 4.2 Correção de Planilha
```
Ranny: terça teve 4 entregadores

Bot: ⏳ Entendendo sua correção...

✅ Correção aplicada!

• Terça: 4 entregadores (CORRIGIDO), 18 entregas = R$ 258,00

*Está correto?*
```

### 4.3 Planilhas Geradas
O bot cria **duas versões**:
1. **COM NOMES** → Enviada no tópico "📊 Planilhas COM NOMES (Ranny)"
2. **SEM NOMES** → Enviada no tópico "📊 Planilhas SEM NOMES (Responsável)"

**Fórmulas automáticas:**
- Segunda a Quinta: R$ 1,00 por entregador
- Sexta a Domingo: R$ 10,00 por entregador
- Bônus horário (FDS): R$ 10,00 se chegou até 18:10h
- Custo por entrega: R$ 12,00

---

## 5. 📈 Planilhas Personalizadas

### 5.1 Criar Planilha Personalizada
```
Ranny: cria planilha de gastos mensais

Bot: ⏳ Analisando sua solicitação...

📊 Entendi! Vou criar:

planilha_gastos_mensais

Colunas:
1. 📅 Data (data)
2. 📝 Descrição (texto)
3. 💰 Valor (moeda)
4. 📂 Categoria (texto)

✅ Com linha de TOTAL

Quer que eu adicione dados de exemplo? (responda 'sim' ou 'não')
```

### 5.2 Editar Planilha (via contexto)
```
Ranny: adiciona: 15/03, Aluguel, 3500, Empresa

Bot: 📊 planilha_gastos_mensais (v2)

✅ Linha adicionada com sucesso!

💡 Você pode continuar editando por mais 2 horas.
```

### 5.3 Operações de Edição
- **Adicionar:** "adiciona: valor1, valor2, ..."
- **Substituir:** "substitui X por Y"
- **Remover:** "remove linha 3"

---

## 6. 📄 Documentos Word (DOCX)

### 6.1 Criar Documento
```
Ranny: cria um documento com:
       Título: Lista de Tarefas
       1. Ligar pro contador
       2. Pagar FGTS
       3. Verificar estoque

Bot: Documento criado com sucesso!

💾 Salvo no contexto por 2 horas
💡 Você pode editar dizendo: 'adiciona: [texto]' ou 'substitui X por Y'
```

### 6.2 Editar Documento
- **Adicionar texto:** "adiciona: nova tarefa no final"
- **Substituir:** "substitui FGTS por INSS"
- **Remover parágrafo:** "remove: Ligar pro contador"

### 6.3 Ler Documento
```
Ranny: [envia arquivo.docx]

Bot: 📄 Conteúdo do documento:

📝 5 parágrafos, 2 tabelas

[Conteúdo truncado em 1000 caracteres]
```

---

## 7. 📋 Templates de Documentos

Templates pré-definidos disponíveis:

| Template | Descrição |
|----------|-----------|
| `contrato_entregador` | Contrato de trabalho para entregador |
| `relatorio_semanal` | Relatório semanal de atividades |
| `comprovante_pagamento` | Comprovante de pagamento |
| `recibo_simples` | Recibo genérico |
| `lista_presenca` | Lista de presença |

### Exemplo de Uso:
```
Ranny: cria um contrato de entregador pro João

Bot: 📝 Contrato de entregador

Dados:
• Nome: João Silva
• Função: Entregador
• Salário: R$ 1.500,00

Confirma? (sim/não)
```

---

## 8. 📊 Relatórios com Gráficos

```
Ranny: gráfico da semana

Bot: 📊 Relatório - Última semana

💰 Total: R$ 22.400,00
📊 Média diária: R$ 3.200,00
📅 7 dias registrados

🔗 [Ver gráficos interativos](link)
⏰ O link expira em 24 horas
```

### Períodos disponíveis:
- "hoje" → 1 dia
- "semana" → 7 dias
- "quinzena" → 15 dias
- "trimestre" → 90 dias
- (padrão) → 30 dias

---

## 9. 🤖 Conversa com IA

Quando não reconhece nenhum comando específico, o bot usa **Google Gemini 2.5 Flash** para:

- Responder perguntas sobre o negócio
- Manter contexto da conversa
- Ajudar com dúvidas gerais

```
Ranny: oi
Bot: Oi Ranny! Tudo bem? 😊

Ranny: quanto gastei de luz esse ano?
Bot: Analisando seus registros...

💡 Light: R$ 890 (janeiro)
    Light: R$ 920 (fevereiro)

Total até agora: R$ 1.810,00
```

---

## 10. 🔧 Detecção Automática de Intenção

O bot processa mensagens nesta ordem:

1. **Fechamento de caixa** → "fechei", "caixa"
2. **Lembretes** → "lembra", "avisa"
3. **Vencimentos** → "paguei", "pago"
4. **Planilha entregadores** → palavras específicas + números
5. **Busca documentos** → "cadê", "onde está"
6. **Reenvio documento** → "manda o 1"
7. **Relatórios** → "gráfico", "relatório"
8. **Edição planilha** → "adiciona", "muda", "remove"
9. **Criação planilha** → "cria planilha"
10. **Templates** → "contrato", "recibo"
11. **Criação arquivos** → "cria pdf", "cria word"
12. **Conversa IA** → fallback

---

## 11. 📁 Estrutura de Pastas (Tópicos Telegram)

O bot salva documentos automaticamente em tópicos:

| Tópico | Conteúdo |
|--------|----------|
| 💰 Financeiro | Boletos, comprovantes, extratos |
| 🏢 Empresa | Documentos da pizzaria |
| 👥 Funcionários | Docs admissionais, folha de ponto |
| ⚖️ Jurídico | Contratos, processos |
| 👤 Pessoal | Documentos pessoais |
| 🔧 Manutenção | Histórico de equipamentos |
| 📎 Outros | Diversos |
| 📊 Planilhas COM NOMES | Planilhas de entregadores (Ranny) |
| 📊 Planilhas SEM NOMES | Planilhas de entregadores (Responsável) |

---

## 12. ⏰ Sistema de Alertas Automáticos

O bot envia alertas automaticamente:

| Quando | O que |
|--------|-------|
| 7 dias antes | Lembrete de vencimento |
| 3 dias antes | Alerta de vencimento |
| 1 dia antes | Último aviso |
| Manhã | Resumo do dia |

---

## 13. 📱 Formatos de Arquivo Suportados

### Leitura:
- `.docx` - Documentos Word
- `.xlsx` - Planilhas Excel
- `.pdf` - PDFs (texto e imagens)

### Criação:
- `.pdf` - Documentos PDF
- `.docx` - Documentos Word
- `.xlsx` - Planilhas Excel

### Edição:
- `.docx` - Adicionar/substituir/remover texto
- `.xlsx` - Adicionar/remover linhas, substituir valores

---

## 14. 🔒 Sistema de Contexto

O bot mantém **contexto** por 2 horas para:

- Editar planilhas sem reenviar arquivo
- Editar documentos Word
- Confirmar/corrigir operações
- Acompanhar conversas

---

## 📝 Exemplos de Uso Completo

### Exemplo 1: Pagamento de Conta
```
Ranny: paguei a internet hoje
Bot: De qual valor?

Ranny: 150
Bot: ✅ Marcado como pago!

📄 Internet
💰 R$ 150,00

🔄 Próximo vencimento: 25/04/2026
```

### Exemplo 2: Criação de Lembrete Recorrente
```
Ranny: todo dia 7 me lembra do FGTS
Bot: ✅ Lembrete criado!

📅 Todo dia 7 às 09:00
📝 FGTS
🔄 Lembrete mensal
```

### Exemplo 3: Busca e Reenvio
```
Ranny: onde está o contrato da luz?
Bot: Encontrei 1 arquivo(s) para 'contrato luz':

1. contrato_fornecimento_energia.pdf
   Categoria: Financeiro

Responda com o número para receber.

Ranny: manda o 1
Bot: 📁 contrato_fornecimento_energia.pdf

📂 Categoria: Financeiro
📅 Salvo em: 10/01/2026

💡 Você pode encontrar este arquivo no tópico Financeiro do grupo!
```

---

## 🚀 Tecnologias Utilizadas

| Tecnologia | Função |
|-----------|--------|
| Python 3.11+ | Linguagem principal |
| Telegram Bot API | Interface de mensagens |
| Google Gemini 2.5 Flash | Inteligência artificial |
| PostgreSQL (Supabase) | Banco de dados |
| SQLite | Fallback local |
| python-docx | Criação/edição Word |
| openpyxl | Planilhas Excel |
| reportlab | Criação PDF |
| FastAPI | Servidor de relatórios |

---

*Este documento reflete exatamente o que o bot **faz atualmente** baseado no código fonte.*
