# 🤖 O QUE O BOT FAZ - Assistente Ranny V3

## 📋 Resumo Executivo

O **Assistente Ranny** é uma secretária virtual completa que funciona via Telegram. Ele automatiza a gestão de documentos, finanças, lembretes e muito mais para a GRN Pizzas.

---

## ✨ FUNCIONALIDADES PRINCIPAIS

### 1. 📁 GESTÃO DE DOCUMENTOS

#### Classificação Automática
- **Recebe** qualquer documento (foto, PDF, Word, Excel)
- **Analisa** o conteúdo com IA (Google Gemini)
- **Classifica** automaticamente em categorias
- **Organiza** enviando para o tópico correto do grupo

**Categorias:**
- 💰 Financeiro (boletos, comprovantes, extratos)
- 🏢 Empresa (notas fiscais, DAS, DARF)
- 👥 Funcionários (contratos, advertências, ASO)
- ⚖️ Jurídico (processos, intimações)
- 👤 Pessoal (documentos pessoais)
- 🔧 Operacional (manutenção, inventários)
- 📸 Mídia (fotos, capturas de tela)
- 📊 Controles (planilhas)
- 📎 Outros

#### Extração Inteligente de Dados

**Para Boletos:**
- 💰 Valor
- 📅 Data de vencimento
- 🏢 Beneficiário/Empresa
- 📋 Código de barras (clicável para copiar!)
- 🔥 Tipo de conta (luz, água, gás, internet, etc.)

**Para Comprovantes:**
- 💰 Valor pago
- 📅 Data do pagamento
- 👤 Destinatário
- 💳 Tipo de pagamento (PIX, transferência, etc.)

**Para QR Codes PIX:**
- 💰 Valor
- 🏢 Beneficiário
- 🔑 Chave PIX
- 🏙️ Cidade
- 📝 Referência

#### Busca de Documentos

**Como buscar:**
```
👤 "cadê o contrato?"
👤 "onde está o boleto da luz?"
👤 "procura nota fiscal"
👤 "tem algum comprovante de..."
```

**O bot retorna:**
- Lista numerada de documentos encontrados
- Categoria de cada um
- Link para a mensagem original
- Opção de reenvio: "manda o 1"

**Estatísticas:**
```
👤 "quantos documentos tenho?"
🤖 "📊 Total: 247 documentos salvos
    
    💰 Financeiro: 89
    🏢 Empresa: 45
    👥 Funcionários: 32
    ..."
```

---

### 2. 💰 GESTÃO FINANCEIRA

#### Fechamento de Caixa

**Como usar:**
```
👤 "fechei 2500"
🤖 "✅ Fechamento registrado!
    
    📊 Hoje: R$ 2.500,00
    📅 Ontem: R$ 2.200,00 (📈 +13.6%)
    📆 Semana: R$ 15.800,00
    
    🎉 Melhor que ontem!"
```

**Recursos:**
- Compara com dia anterior (% de crescimento)
- Soma da semana
- Identifica melhor e pior dia
- Histórico completo

#### Vencimentos e Alertas

**Criação automática:**
- Quando você envia um boleto, o bot cria o vencimento automaticamente
- Extrai valor, data e descrição

**Alertas automáticos:**
- 📆 **7 dias antes**: "Vencimento em 7 dias"
- ⚠️ **3 dias antes**: "Vencimento em 3 dias"
- 🚨 **1 dia antes**: "URGENTE! Vence amanhã"

**Marcar como pago:**
```
👤 "paguei a luz"
🤖 "✅ Marcado como pago!
    
    📄 Conta de luz - Janeiro
    💰 R$ 350,00
    
    🔄 Próximo vencimento criado: 20/02/2025"
```

**Vencimentos recorrentes:**
- Luz, água, internet, aluguel, etc.
- Ao marcar como pago, cria automaticamente o próximo mês

#### Relatórios com Gráficos

**Como gerar:**
```
👤 "mostra gráfico da semana"
👤 "relatório do mês"
👤 "gráfico do trimestre"
```

**O bot gera:**
- 📈 Gráfico de linha (faturamento diário)
- 📊 Gráfico de barras (comparativo)
- 🥧 Gráfico de pizza (gastos por categoria)
- Link para página web interativa (expira em 24h)

**Resumo semanal automático:**
- Todo domingo às 20h
- Envia relatório da semana no Chat
- Com link para gráficos completos

---

### 3. 📝 LEMBRETES INTELIGENTES

#### Criar Lembretes

**Datas naturais:**
```
👤 "me lembra amanhã de ligar pro contador"
👤 "me lembra segunda às 14h de pagar FGTS"
👤 "me lembra dia 15 de fazer pedido"
👤 "me lembra daqui 5 minutos"
👤 "me lembra daqui 2 horas"
```

**Lembretes recorrentes:**
```
👤 "todo dia lembra de conferir caixa"
👤 "toda segunda lembra da reunião"
👤 "todo dia 7 lembra do FGTS"
```

**Tipos de recorrência:**
- 📅 Diário
- 📆 Semanal
- 🗓️ Mensal

#### Gerenciar Lembretes

**Listar:**
```
👤 "quais meus lembretes?"
🤖 "📝 Seus lembretes ativos:
    
    1. 📌 Ligar pro contador
       📅 05/02/2026 às 14:00
    
    2. 📌 Pagar FGTS
       📅 07/02/2026 às 09:00
       🔄 mensal"
```

**Cancelar:**
```
👤 "cancela lembrete do FGTS"
🤖 "✅ Lembrete cancelado: Pagar FGTS"
```

---

### 4. 📄 CRIAÇÃO E EDIÇÃO DE ARQUIVOS

#### Criar Documentos

**PDF:**
```
👤 "cria um pdf com: Lista de compras - Queijo, Presunto, Tomate"
🤖 📄 [envia arquivo lista_de_compras.pdf]
```

**Word:**
```
👤 "cria um word com: Relatório mensal de vendas..."
🤖 📄 [envia arquivo relatorio_mensal.docx]
```

**Excel:**
```
👤 "cria uma planilha com: Nome, Valor, Data | João, 100, 01/01"
🤖 📄 [envia arquivo planilha.xlsx]
```

#### Ler Documentos

**Word:**
```
👤 [anexa arquivo.docx] "lê esse documento"
🤖 "📄 Conteúdo do documento:
    
    📝 5 parágrafos, 2 tabelas
    
    Parágrafo 1: ...
    Parágrafo 2: ..."
```

**Excel:**
```
👤 [anexa planilha.xlsx] "lê essa planilha"
🤖 "📊 Conteúdo da planilha:
    
    📋 2 planilha(s)
    
    | Nome | Valor | Data |
    | João | 100   | 01/01 |"
```

#### Editar Documentos

**Adicionar texto:**
```
👤 [anexa arquivo.docx] "adiciona: Novo parágrafo no final"
🤖 📄 [envia arquivo editado]
```

**Adicionar linha na planilha:**
```
👤 [anexa planilha.xlsx] "adiciona linha: Maria, 200, 02/01"
🤖 📄 [envia planilha com nova linha]
```

**Substituir texto:**
```
👤 [anexa arquivo.docx] "substitui João por Pedro"
🤖 "✅ 3 substituição(ões) feita(s)"
    📄 [envia arquivo editado]
```

---

### 5. 🤖 CONVERSA COM IA

**O bot conversa naturalmente:**
```
👤 "oi, tudo bem?"
🤖 "Oi! Tudo ótimo! E você? Em que posso ajudar?"

👤 "quanto faturamos essa semana?"
🤖 "Essa semana vocês faturaram R$ 15.800,00!
    A média diária foi de R$ 2.257,14.
    O melhor dia foi terça com R$ 2.800,00 🎉"

👤 "quais contas vencem essa semana?"
🤖 "Você tem 3 contas vencendo:
    
    💡 Luz - R$ 350,00 (vence em 2 dias)
    💧 Água - R$ 120,00 (vence em 5 dias)
    🌐 Internet - R$ 200,00 (vence em 6 dias)"
```

**Contexto inteligente:**
- O bot lembra da conversa anterior
- Conhece os dados do seu negócio
- Responde com base em informações reais

---

### 6. ⚙️ AUTOMAÇÕES

#### Jobs Automáticos

**Lembretes (a cada 1 minuto):**
- Verifica lembretes que devem ser disparados
- Envia notificação no horário certo
- Cria próximo lembrete se for recorrente

**Alertas de Vencimento (todo dia às 8h):**
- Verifica contas a vencer
- Envia alertas 7, 3 e 1 dia antes
- Evita alertas duplicados

**Resumo Semanal (domingo às 20h):**
- Gera relatório da semana
- Envia com gráficos interativos
- Compara com semanas anteriores

**Keep-Alive (a cada 10 minutos):**
- Mantém o bot acordado no servidor
- Evita que o serviço durma por inatividade
- Garante disponibilidade 24/7

---

### 7. ☁️ INTEGRAÇÃO ONEDRIVE (Em Desenvolvimento)

**Funcionalidades planejadas:**
- Buscar arquivos na nuvem
- Sincronizar documentos
- Backup automático
- Acesso sem PC ligado

---

## 🎯 COMANDOS PRINCIPAIS

| Comando | O que faz |
|---------|-----------|
| `/start` | Apresentação do bot |
| `/help` | Lista de comandos e exemplos |
| Enviar foto/PDF | Classifica e guarda automaticamente |
| "fechei 2500" | Registra fechamento de caixa |
| "me lembra..." | Cria lembrete |
| "paguei a luz" | Marca vencimento como pago |
| "cadê o contrato?" | Busca documentos |
| "manda o 1" | Mostra onde está o documento |
| "mostra gráfico" | Gera relatório com gráficos |
| "cria um pdf com..." | Cria documento PDF |
| "quantos documentos?" | Estatísticas do banco |

---

## 🔧 TECNOLOGIAS USADAS

- **Python 3.13** - Linguagem principal
- **Telegram Bot API** - Interface com usuário
- **Google Gemini 2.5 Flash** - Inteligência artificial
- **Supabase (PostgreSQL)** - Banco de dados
- **FastAPI** - Servidor web para relatórios
- **Plotly** - Gráficos interativos
- **APScheduler** - Jobs automáticos
- **pdfplumber** - Leitura de PDFs
- **python-docx** - Criação/edição de Word
- **openpyxl** - Criação/edição de Excel
- **Render** - Hospedagem 24/7

---

## 📊 ESTATÍSTICAS DO PROJETO

- ✅ **113 testes automatizados** (todos passando)
- 📁 **1.375 linhas** no arquivo principal (bot.py)
- 🔧 **15+ módulos** especializados
- 🤖 **30+ funcionalidades** diferentes
- ⚡ **Resposta em < 2 segundos** (média)
- 🌐 **Disponível 24/7** no Render

---

## 🎯 CASOS DE USO REAIS

### Dia a Dia da Pizzaria

**Manhã (8h):**
- 🔔 Bot envia alertas de contas a vencer
- 📊 Ranny verifica vencimentos do dia

**Durante o dia:**
- 📸 Funcionário envia foto de boleto → Bot classifica e guarda
- 💰 Fornecedor envia comprovante → Bot extrai dados e arquiva
- 📝 Ranny cria lembrete: "me lembra às 15h de ligar pro contador"

**Fechamento (noite):**
- 💵 Ranny: "fechei 3200"
- 🤖 Bot: "Melhor que ontem! +15% 🎉"

**Domingo (20h):**
- 📊 Bot envia resumo semanal automaticamente
- 📈 Ranny vê gráficos de faturamento da semana

### Gestão de Documentos

**Recebeu boleto por email:**
1. Salva PDF no celular
2. Envia no Chat do Telegram
3. Bot analisa, extrai dados e guarda no tópico Financeiro
4. Cria vencimento automaticamente
5. Vai alertar 7, 3 e 1 dia antes

**Precisa encontrar um documento:**
1. "cadê o contrato do fornecedor?"
2. Bot lista documentos encontrados
3. "manda o 1"
4. Bot mostra em qual tópico está

---

## 💡 DIFERENCIAIS

### 1. Processamento Inteligente
- PDFs com texto → extração local (economiza API)
- PDFs escaneados → converte para imagem + IA
- QR Codes PIX → decodifica automaticamente

### 2. Código de Barras Clicável
- Extrai código de barras de boletos
- Formata em texto clicável no Telegram
- Basta tocar para copiar!

### 3. Lembretes Naturais
- Entende português: "amanhã", "segunda", "daqui 5 minutos"
- Suporta recorrência: "todo dia", "toda semana"
- Reagenda automaticamente

### 4. Busca Inteligente
- Busca por descrição, tipo ou categoria
- Mostra onde o documento está
- Estatísticas completas

### 5. Relatórios Interativos
- Gráficos Plotly (zoom, hover, download)
- Link temporário (24h)
- Responsivo (funciona no celular)

---

## 🚀 PRÓXIMAS FUNCIONALIDADES

- ☁️ Integração completa com OneDrive
- 📱 App mobile nativo
- 🔔 Notificações push personalizadas
- 📊 Dashboard web completo
- 🤖 Mais automações inteligentes
- 🗣️ Comandos por voz
- 📸 OCR melhorado para documentos manuscritos

---

## 📞 SUPORTE

O bot está **online 24/7** e responde instantaneamente!

Se tiver dúvidas, basta perguntar:
- "como funciona?"
- "o que você faz?"
- "me ajuda com..."

---

<p align="center">
  <b>🍕 Desenvolvido com ❤️ para a Ranny e GRN Pizzas</b><br>
  <i>Seu assistente virtual está sempre pronto para ajudar!</i>
</p>
