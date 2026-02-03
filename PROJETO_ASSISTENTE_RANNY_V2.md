# 🤖 Assistente Ranny V2 - Especificação Completa

## 📊 Análise das Dores (baseado no backup)

### 1. GESTÃO DE FUNCIONÁRIOS (DOR CRÍTICA)
- **20+ processos trabalhistas** encontrados = problema recorrente
- Documentação de funcionários espalhada
- Controle de ASO, férias, advertências manual
- Funcionários: Cristian, Paloma, Alana, Jessica, Gleydson, Heloiza, Anna Karla, etc.

### 2. OBRIGAÇÕES FISCAIS/TRABALHISTAS (DOR ALTA)
- FGTS mensal (vence dia 7)
- INSS mensal (vence dia 20)
- DAS Simples Nacional (vence dia 20)
- DARF (vence dia 20)
- Vale Transporte
- 13º salário (1ª parcela nov, 2ª parcela dez)
- Parcelamento PGFN (5 parcelas)

### 3. CONTAS FIXAS (DOR MÉDIA)
- Light (energia)
- Internet
- Verisure (alarme)
- Aluguel
- Faturas cartão (Itaú, Nubank, Mastercard)

### 4. OPERACIONAL (DOR MÉDIA)
- Fechamento de caixa diário
- Inventário mensal
- Escalas de funcionários
- Controle de estoque

### 5. JURÍDICO (DOR ALTA)
- Muitos processos trabalhistas ativos
- Audiências para acompanhar
- Documentação para defesa

---

## 🎯 Funcionalidades do Bot

### TÓPICO: 💰 FINANCEIRO

**Receber e Guardar Comprovantes**
```
Ranny: [envia foto do comprovante de luz]
Bot: "Guardei o comprovante da Light! 💡
     Valor: R$ 342,50
     Vencimento: 15/02/2026
     Quer que eu te lembre 3 dias antes?"
```

**Consultar Pagamentos**
```
Ranny: "quanto gastei de luz esse ano?"
Bot: "Gastos com Light em 2026:
     Jan: R$ 298,00
     Total: R$ 298,00
     Média: R$ 298,00"
```

**Alertas Automáticos**
```
Bot: "🔔 Oi Ranny! Lembrete:
     - Light vence em 3 dias (R$ 342,50)
     - Internet vence amanhã (R$ 129,90)
     Quer os boletos?"
```

---

### TÓPICO: 🏢 EMPRESA

**Fechamento de Caixa**
```
Ranny: "fechamento hoje 4200"
Bot: "Anotado! 📊
     Hoje: R$ 4.200,00
     Ontem: R$ 3.800,00 (+10,5%)
     Semana: R$ 28.500,00
     Melhor dia do mês até agora! 🎉"
```

**Consultar Histórico**
```
Ranny: "como foi o mês passado?"
Bot: "Dezembro/2025:
     Total: R$ 98.500,00
     Média/dia: R$ 3.283,33
     Melhor dia: Sábado 21 (R$ 5.200)
     Pior dia: Segunda 16 (R$ 1.800)"
```

**Obrigações Fiscais**
```
Bot: "🔔 Obrigações do mês:
     ✅ DAS pago (20/01)
     ⏳ FGTS vence dia 07 (R$ 890,00)
     ⏳ INSS vence dia 20 (R$ 1.200,00)
     ⏳ DARF vence dia 20 (R$ 450,00)"
```

---

### TÓPICO: 👥 FUNCIONÁRIOS

**Cadastro Conversacional**
```
Ranny: "contratei uma funcionária nova"
Bot: "Oba! Me conta sobre ela:
     Qual o nome completo?"
Ranny: "Maria Silva Santos"
Bot: "Qual a função dela?"
Ranny: "atendente"
Bot: "Data de admissão?"
Ranny: "hoje"
Bot: "Cadastrei! Maria Silva Santos
     Função: Atendente
     Admissão: 14/01/2026
     
     Vou te lembrar:
     - ASO admissional (até 10 dias)
     - Fim experiência (13/04/2026)
     - Férias (14/01/2027)"
```

**Alertas de Funcionários**
```
Bot: "🔔 Alertas de RH:
     
     ⚠️ URGENTE:
     - ASO do Cristian vence em 5 dias
     
     📅 PRÓXIMOS 30 DIAS:
     - Férias da Paloma vencem em 25 dias
     - Fim experiência Jessica em 28 dias"
```

**Gerar Documentos**
```
Ranny: "faz uma advertência pro João por atraso"
Bot: "Vou preparar. Qual foi a data do atraso?"
Ranny: "ontem"
Bot: "Quantos minutos de atraso?"
Ranny: "45 minutos"
Bot: "Pronto! Advertência gerada 📄
     [envia PDF]
     
     É só imprimir e pegar assinatura.
     Quer que eu anote no histórico dele?"
```

**Histórico do Funcionário**
```
Ranny: "histórico do Gleydson"
Bot: "📋 Gleydson Silva
     Admissão: 15/03/2023
     Função: Pizzaiolo
     
     Histórico:
     - 10/05/2023: Advertência (atraso)
     - 15/08/2023: Advertência (falta)
     - 20/11/2023: Suspensão 2 dias
     - 05/01/2024: Rescisão
     
     Documentos: 12 arquivos
     Quer ver algum?"
```

---

### TÓPICO: ⚖️ JURÍDICO

**Cadastrar Processo**
```
Ranny: "recebi intimação de processo novo"
Bot: "Me manda a foto que eu cadastro"
Ranny: [envia foto]
Bot: "Cadastrei o processo:
     Nº: 0100573-71.2022.5.01.0018
     Tipo: Trabalhista
     Reclamante: Fulano de Tal
     
     Tem audiência marcada?"
```

**Alertas de Audiências**
```
Bot: "🔔 AUDIÊNCIA EM 3 DIAS!
     
     Processo: 0100573-71.2022.5.01.0018
     Data: 17/01/2026 às 14h
     Local: TRT 1ª Região
     
     Documentos necessários:
     - Folhas de ponto ✅
     - Comprovantes pagamento ✅
     - Contrato trabalho ✅
     
     Quer que eu prepare a pasta?"
```

---

### TÓPICO: 🔧 MANUTENÇÃO/TI

**Registrar Problema**
```
Ranny: "o computador tá travando muito"
Bot: "Entendi. Vou anotar pra o Cauã.
     Quando começou?"
Ranny: "ontem"
Bot: "Tá fazendo algo específico quando trava?"
Ranny: "quando abre o sistema de pedidos"
Bot: "Anotado! 📝
     Problema: PC travando ao abrir sistema
     Início: 13/01/2026
     
     Vou avisar o Cauã. Enquanto isso,
     tenta reiniciar o PC."
```

**Histórico para Cauã**
```
Cauã: "problemas da ranny"
Bot: "📋 Histórico de TI - GRN Pizzas:
     
     🔴 ABERTO:
     - PC travando (14/01) - sistema pedidos
     
     ✅ RESOLVIDO:
     - Impressora não imprimia (10/01)
     - Nobreak apitando (05/01)"
```

---

### TÓPICO: 📎 LEMBRETES (NOVO!)

**Criar Lembrete Conversacional**
```
Ranny: "me lembra de ligar pro contador segunda"
Bot: "Anotado! Vou te lembrar segunda (20/01)
     às 9h. Quer outro horário?"
```

**Lembrete Recorrente**
```
Ranny: "todo dia 5 me lembra do FGTS"
Bot: "Pronto! Todo dia 5 vou te lembrar:
     '🔔 FGTS vence dia 7!'
     
     Quer que eu já puxe o valor?"
```

**Lembretes Inteligentes**
```
Bot: "🔔 Bom dia Ranny!
     
     HOJE:
     - Ligar pro contador
     - Vencimento Light
     
     ESSA SEMANA:
     - FGTS (dia 07)
     - Audiência processo (dia 17)
     
     Bom trabalho! 💪"
```

---

## 🗂️ Estrutura de Tópicos do Grupo

```
📱 Grupo: Documentos Ranny
│
├── 💰 Financeiro
│   └── Comprovantes, boletos, extratos
│
├── 🏢 Empresa  
│   └── Fechamentos, notas fiscais, DAS
│
├── 👥 Funcionários
│   └── Docs de funcionários, advertências
│
├── ⚖️ Jurídico
│   └── Processos, intimações, audiências
│
├── 🔧 Manutenção
│   └── Problemas de TI, histórico
│
├── 📎 Lembretes (NOVO!)
│   └── Configuração de alertas
│
└── 📊 Relatórios (NOVO!)
    └── Resumos semanais/mensais
```

---

## 🧠 Inteligência do Bot

### OCR + Gemini Vision
- Extrai dados de boletos automaticamente
- Lê comprovantes de pagamento
- Identifica tipo de documento
- Extrai datas de vencimento

### Classificação Automática
- Documento recebido → identifica categoria
- Salva no tópico correto
- Indexa para busca futura

### Alertas Proativos
- Vencimentos (1, 3, 7 dias antes)
- Obrigações trabalhistas
- Férias/ASO de funcionários
- Audiências de processos

### Geração de Documentos
- Advertência (template Word)
- Declaração de trabalho
- Recibo de pagamento
- Termo de responsabilidade

---

## 📅 Calendário de Obrigações (Pré-configurado)

| Dia | Obrigação |
|-----|-----------|
| 05 | Lembrete FGTS |
| 07 | Vencimento FGTS |
| 15 | Lembrete INSS/DAS |
| 20 | Vencimento INSS/DAS/DARF |
| 25 | Lembrete VT |
| 30 | Fechamento mensal |

---

## 🔄 Fluxos Automáticos

### Novo Funcionário
1. Cadastro básico
2. Alerta ASO admissional (10 dias)
3. Alerta fim experiência (90 dias)
4. Alerta férias (12 meses)
5. Alerta ASO periódico (12 meses)

### Novo Processo
1. Cadastro do processo
2. Vincula funcionário (se trabalhista)
3. Alerta de audiências
4. Prepara documentação

### Pagamento Registrado
1. Guarda comprovante
2. Atualiza status (pago)
3. Calcula próximo vencimento
4. Agenda lembrete

---

## 💡 Diferenciais

1. **100% Conversacional** - Sem comandos, só papo
2. **Proativo** - Avisa antes de vencer
3. **Inteligente** - Entende contexto
4. **Organizado** - Tudo no lugar certo
5. **Histórico** - Nunca perde nada
6. **Acessível** - Funciona no celular
7. **Backup** - Telegram guarda tudo na nuvem
