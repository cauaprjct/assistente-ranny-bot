# 🤖 Projeto Assistente Ranny - Telegram + IA

## Visão Geral

Assistente pessoal inteligente via Telegram que entende **linguagem natural** - sem comandos, sem barras, só conversa normal como se fosse um humano.

**Stack:**
- 📱 **Telegram** - Nuvem + interface
- 🧠 **Gemini AI** - Entende tudo naturalmente
- 🐍 **Python** - Bot + Script de sync

---

## 💬 Como Funciona (Exemplos Reais)

### Conversa Natural - Sem Comandos

```
Ranny: oi
Bot: Oi Ranny! Tudo bem? 😊

Ranny: cadê aquele contrato do aluguel?
Bot: Achei! É esse do João da Silva, R$3.500/mês?
     [contrato_locacao.pdf]

Ranny: isso, valeu
Bot: 👍
```

```
Ranny: [envia foto de PIX]
Bot: PIX de R$350 pro Fornecedor Massa, né? 
     Salvei em Financeiro! ✅
```

```
Ranny: paguei a light hoje
Bot: Boa! Quer me mandar o comprovante pra eu guardar?

Ranny: [envia comprovante]
Bot: Pronto! Light de R$890, vencia dia 20.
     Guardei em Financeiro.
     
     📌 Próximo vencimento: Internet dia 25 (R$150)
```

```
Ranny: quanto gastei esse mês?
Bot: Em janeiro até agora:

     💡 Light: R$890
     🌐 Internet: R$150  
     🏠 Aluguel: R$3.500
     
     Total: R$4.540
```

```
Ranny: o notebook travou de novo
Bot: De novo? 😕 O que aconteceu dessa vez?

Ranny: tela azul
Bot: Entendi. Anotei no histórico.
     Última vez foi dia 09/01, problema de HD.
     Quer que eu avise o Cauã?

Ranny: sim
Bot: Avisei ele! Deve responder logo.
```

```
Ranny: preciso dos documentos da paloma
Bot: Aqui os docs da Paloma:
     [Docs Func_ Paloma.pdf]
```

```
Ranny: fiz o fechamento, deu 3200
Bot: Ótimo dia! 📈 
     Melhor que ontem (R$2.800).
     Quer anotar alguma observação?

Ranny: nao
Bot: Beleza, registrado! ✅
```

---

## 🎯 Funcionalidades Baseadas no Dia a Dia da Ranny

### 1. 💰 Controle Financeiro

**O que ela já faz:**
- Paga boletos (Light, internet, aluguel)
- Recebe/envia PIX
- Paga FGTS dos funcionários
- Controla extratos

**Como o bot ajuda:**
```
Ranny: paguei o fgts
Bot: De qual mês? Novembro?

Ranny: isso
Bot: Beleza! Me manda a guia que eu guardo.

Ranny: [envia PDF]
Bot: FGTS competência 11/2025 - R$XXX
     Guardei em Financeiro! ✅
     
     ⏰ Lembrete: FGTS de dezembro vence dia 07/01
```

```
Ranny: quanto paguei de conta esse ano?
Bot: Em 2026 até agora:

     � Por categoria:
     • Energia: R$890
     • Internet: R$150
     • Aluguel: R$3.500
     • FGTS: R$1.200
     
     Total: R$5.740
```

---

### 2. 🏪 Gestão da Pizzaria (GRN)

**O que ela já faz:**
- Fechamento de caixa diário
- Controle de estoque
- Notas fiscais
- Inventário mensal

**Como o bot ajuda:**
```
Ranny: fechamento de hoje 4500
Bot: Excelente! 🍕📈
     
     Comparando:
     • Ontem: R$3.200
     • Semana passada (terça): R$4.100
     • Média do mês: R$3.800
     
     Melhor terça do mês! 🎉
```

```
Ranny: [envia foto de nota fiscal]
Bot: Nota fiscal de R$1.200 - Fornecedor Queijos Ltda
     Guardei em Empresa/Fiscal ✅
```

```
Ranny: preciso do inventário de outubro
Bot: Aqui:
     [Inventário_Pizza REF OUT.xlsx]
```

---

### 3. � Gestão de Funcionários

**O que ela já faz:**
- Guarda documentos de funcionários
- Controla folhas de ponto
- Lida com processos trabalhistas
- Recebe currículos

**Como o bot ajuda:**
```
Ranny: documentos da anna karla
Bot: Aqui os docs da Anna Karla:
     [DOCS ANNA KARLA.pdf]
     
     Ela entrou em qual data mesmo?
```

```
Ranny: chegou currículo novo
Bot: Me manda que eu guardo!

Ranny: [envia PDF]
Bot: Currículo de Maria Silva, 25 anos
     Experiência em atendimento.
     
     Guardei em Currículos/Recebidos ✅
     Quer agendar entrevista?
```

```
Ranny: folha de ponto do gabriel
Bot: De qual mês?

Ranny: agosto
Bot: Aqui:
     [Folha Gabriel Agosto.pdf]
```

---

### 4. ⚖️ Jurídico

**O que ela já faz:**
- Guarda contratos
- Acompanha processos trabalhistas
- Mantém acordos e certidões

**Como o bot ajuda:**
```
Ranny: tem audiência quando?
Bot: Achei nos seus documentos:
     
     📅 Próxima audiência: 14/02/2026
     Processo trabalhista - Rito Ordinário
     
     Quer que eu te lembre na véspera?
```

```
Ranny: [envia contrato novo]
Bot: Contrato de prestação de serviços
     Valor: R$500/mês
     Vigência: 12 meses
     
     ⚠️ Atenção: Multa de 2x em caso de rescisão
     
     Salvo em Jurídico ✅
```

---

### 5. � Histórico de Manutenção (PC/Notebook)

**Problema dela:**
- PC e notebook dão problema frequente
- Precisa de histórico pra você (Cauã) consultar

**Como o bot ajuda:**
```
Ranny: o pc da loja nao liga
Bot: O que acontece quando tenta ligar?

Ranny: fica na tela preta
Bot: Entendi. Anotei no histórico:
     
     � 13/01/2026 - PC Loja
     ❌ Problema: Não liga, tela preta
     
     Histórico recente desse PC:
     • 09/01: HD não detectado
     • 25/11: Teclado mexendo sozinho
     
     Quer que eu avise o Cauã?
```

```
Ranny: o cauã arrumou o notebook
Bot: Boa! O que ele fez?

Ranny: trocou um cabo
Bot: Anotado! ✅
     
     📅 13/01/2026 - Notebook
     ✅ Resolvido: Troca de cabo
     🔧 Técnico: Cauã
```

---

### 6. ⏰ Lembretes Automáticos

O bot aprende os padrões e avisa proativamente:

```
Bot: Bom dia Ranny! ☀️

     📌 Lembretes de hoje:
     • Boleto Light vence amanhã (R$890)
     • FGTS competência 12 vence dia 07
     
     💰 Fechamento de ontem: R$3.200
```

```
Bot: Oi Ranny! 
     
     ⚠️ Amanhã tem audiência trabalhista às 14h
     Processo: 0001234-XX.2025
     
     Quer que eu separe os documentos relacionados?
```

---

### 7. � Resumos e Relatórios

```
Ranny: como foi a semana?
Bot: Resumo da semana (07-13/01):

     🍕 Vendas:
     • Total: R$22.400
     • Média/dia: R$3.200
     • Melhor dia: Sábado (R$4.800)
     
     💸 Contas pagas:
     • Light: R$890
     • Internet: R$150
     
     📁 Documentos salvos: 12
     
     Quer mais detalhes de algo?
```

```
Ranny: me faz um resumo do ano passado
Bot: Resumo 2025:

     📁 Documentos organizados: 847
     💰 Contas registradas: R$45.000
     👥 Funcionários com docs: 8
     ⚖️ Processos: 2 (1 encerrado)
     
     Quer exportar pra Excel?
```

---

## 🏗️ Arquitetura

```
┌──────────────────┐     ┌──────────────────┐
│  NOTEBOOK RANNY  │     │   iPHONE RANNY   │
│                  │     │                  │
│  📁 Pasta Sync/  │     │  📱 Telegram     │
│       │          │     │       │          │
│       ▼          │     │  "paguei a luz"  │
│  🐍 Script       │     │       │          │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         └───────────┬────────────┘
                     ▼
         ┌───────────────────────┐
         │     🤖 BOT TELEGRAM   │
         │           │           │
         │     🧠 GEMINI AI      │
         │  • Entende português  │
         │  • Lembra contexto    │
         │  • Aprende padrões    │
         │  • Responde natural   │
         └───────────┬───────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  📁 GRUPO COM TÓPICOS (NUVEM TELEGRAM)      │
│                                             │
│  💰 Financeiro                              │
│  🏢 Empresa                                 │
│  👤 Pessoal                                 │
│  ⚖️ Jurídico                                │
│  👥 Funcionários                            │
│  🔧 Manutenção                              │
│  📎 Outros                                  │
└─────────────────────────────────────────────┘
```

---

## 🧠 Personalidade do Bot

O bot deve ser:
- **Amigável** - Fala como amigo, não como robô
- **Proativo** - Avisa coisas importantes sem pedir
- **Paciente** - Ela pode errar, bot entende
- **Contextual** - Lembra conversas anteriores
- **Simples** - Sem termos técnicos
- **Útil** - Sempre tenta ajudar

**Tom de voz:**
```
❌ "Documento categorizado com sucesso no diretório Financeiro"
✅ "Guardei em Financeiro! ✅"

❌ "Não foi possível identificar o tipo de documento"
✅ "Não entendi bem esse documento, é o quê?"

❌ "Deseja criar um lembrete para esta data?"
✅ "Quer que eu te lembre?"
```

---

## 💰 Custos

| Item | Custo | Observação |
|------|-------|------------|
| Telegram | R$ 0 | API gratuita |
| Gemini AI | R$ 0 | Tier grátis suficiente |
| Hospedagem | R$ 0-20 | Pode rodar no notebook |
| **TOTAL** | **R$ 0-20** | Praticamente grátis |

---

## 📅 Implementação

### Fase 1 - Setup (1-2 horas)
- [ ] Criar bot no @BotFather
- [ ] Criar grupo com tópicos
- [ ] Configurar Gemini API
- [ ] Adicionar Ranny no grupo

### Fase 2 - Bot Conversacional (2-3 dias)
- [ ] Integração Telegram + Gemini
- [ ] Entendimento de linguagem natural
- [ ] Receber e categorizar arquivos
- [ ] Memória de contexto
- [ ] Respostas amigáveis

### Fase 3 - Funcionalidades (2 dias)
- [ ] Controle financeiro
- [ ] Fechamento de caixa
- [ ] Gestão de funcionários
- [ ] Histórico de manutenção
- [ ] Lembretes automáticos

### Fase 4 - Script Notebook (meio dia)
- [ ] Monitorar pasta Sync
- [ ] Enviar arquivos pro bot
- [ ] Rodar em background

### Fase 5 - Testes (1 semana)
- [ ] Testar com Ranny
- [ ] Ajustar respostas
- [ ] Corrigir erros

---

## 🎯 Resultado Final

**Antes:**
- Arquivos espalhados
- Esquece vencimentos
- Não acha documentos
- Perde dados quando PC quebra
- Precisa de ajuda pra tudo

**Depois:**
- Só conversa com o bot
- Bot organiza tudo
- Bot lembra vencimentos
- Bot acha qualquer documento
- Tudo seguro na nuvem
- Independente de PC

---

*Documento atualizado em: 13/01/2026*
*Autor: Cauã*
*Cliente: Ranny M. Morett*
