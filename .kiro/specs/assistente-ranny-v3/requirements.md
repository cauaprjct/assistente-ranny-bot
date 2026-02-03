# Requirements Document

## Introduction

Assistente Ranny V3 - Secretária virtual completa para GRN Pizzas via Telegram. O bot organiza documentos automaticamente, gerencia lembretes com notificações, gera relatórios financeiros interativos e se conecta ao notebook da Ranny via OneDrive.

## Glossary

- **Bot**: Assistente Ranny, bot do Telegram
- **Ranny**: Usuária principal, dona da GRN Pizzas
- **Tópico_Chat**: Tópico principal onde Ranny conversa com o bot (ID: 47)
- **Tópicos_Arquivo**: Tópicos organizacionais (Financeiro, Empresa, Jurídico, Pessoal, Funcionários, Manutenção, Outros)
- **Documento**: Qualquer arquivo enviado (foto, PDF, imagem)
- **Gemini**: IA do Google usada para classificação e conversação
- **OneDrive**: Serviço de nuvem da Microsoft no notebook da Ranny

## Requirements

### Requirement 1: Conversa Natural no Tópico Chat

**User Story:** Como Ranny, quero conversar naturalmente com o bot no tópico Chat, para que eu possa fazer qualquer coisa sem precisar saber comandos.

#### Acceptance Criteria

1. WHEN Ranny envia mensagem de texto no Tópico_Chat, THE Bot SHALL responder de forma amigável e contextual
2. WHEN Ranny envia documento no Tópico_Chat, THE Bot SHALL classificar e mover automaticamente para o Tópico_Arquivo correto
3. WHEN Ranny faz pergunta sobre seus dados, THE Bot SHALL buscar no banco e responder
4. WHEN Ranny pede lembrete, THE Bot SHALL criar o lembrete e confirmar
5. WHEN Ranny pede relatório financeiro, THE Bot SHALL gerar e enviar

### Requirement 2: Classificação e Organização Automática de Documentos

**User Story:** Como Ranny, quero que o bot organize meus documentos automaticamente, para que eu não precise escolher onde salvar.

#### Acceptance Criteria

1. WHEN documento é recebido no Tópico_Chat, THE Bot SHALL analisar com Gemini Vision e classificar em categoria
2. WHEN documento é classificado, THE Bot SHALL repostar no Tópico_Arquivo correspondente (Financeiro, Empresa, Jurídico, Pessoal, Funcionários, Outros)
3. WHEN documento é um boleto, THE Bot SHALL extrair valor e vencimento e perguntar se quer lembrete
4. WHEN documento é repostado, THE Bot SHALL confirmar no Tópico_Chat: "Guardei em [categoria]! 📁"
5. WHEN Ranny envia documento direto em Tópico_Arquivo, THE Bot SHALL apenas confirmar recebimento sem mover

### Requirement 3: Sistema de Lembretes com Notificações

**User Story:** Como Ranny, quero criar lembretes conversando com o bot, para que eu receba notificações no celular e não esqueça compromissos.

#### Acceptance Criteria

1. WHEN Ranny pede lembrete (ex: "me lembra amanhã de pagar FGTS"), THE Bot SHALL extrair data/hora e descrição e criar lembrete
2. WHEN Ranny não especifica hora, THE Bot SHALL usar 09:00 como padrão
3. WHEN chega a hora do lembrete, THE Bot SHALL enviar mensagem no Tópico_Chat
4. WHEN Ranny pergunta "quais meus lembretes?", THE Bot SHALL listar lembretes ativos
5. WHEN Ranny pede para cancelar lembrete, THE Bot SHALL desativar e confirmar
6. WHEN lembrete é recorrente (ex: "todo dia 7 lembra do FGTS"), THE Bot SHALL reagendar automaticamente após disparar

### Requirement 4: Fechamento de Caixa e Histórico Financeiro

**User Story:** Como Ranny, quero registrar fechamentos de caixa e ver histórico, para acompanhar o desempenho da pizzaria.

#### Acceptance Criteria

1. WHEN Ranny informa fechamento (ex: "fechei 2500"), THE Bot SHALL salvar valor com data atual
2. WHEN fechamento é salvo, THE Bot SHALL comparar com dia anterior e mostrar variação percentual
3. WHEN fechamento é salvo, THE Bot SHALL mostrar soma da semana
4. WHEN Ranny pergunta sobre fechamentos (ex: "como foi a semana?"), THE Bot SHALL mostrar resumo com valores

### Requirement 5: Relatórios e Gráficos Financeiros Interativos

**User Story:** Como Ranny, quero ver gráficos do meu faturamento, para entender melhor o desempenho do negócio.

#### Acceptance Criteria

1. WHEN Ranny pede relatório (ex: "mostra gráfico do mês"), THE Bot SHALL gerar página web interativa com gráficos
2. WHEN relatório é gerado, THE Bot SHALL enviar link temporário (expira em 24h)
3. WHEN página é acessada, THE Sistema_Web SHALL mostrar gráficos interativos (zoom, hover, filtros)
4. WHEN é domingo à noite, THE Bot SHALL enviar automaticamente resumo semanal com gráfico
5. WHEN Ranny nunca pediu relatório, THE Bot SHALL enviar um relatório proativamente para "mostrar serviço"

### Requirement 6: Busca de Documentos

**User Story:** Como Ranny, quero encontrar documentos perguntando ao bot, para não precisar procurar manualmente.

#### Acceptance Criteria

1. WHEN Ranny pergunta "cadê o contrato?" ou similar, THE Bot SHALL buscar nos documentos salvos no Telegram
2. WHEN documento é encontrado, THE Bot SHALL enviar o arquivo ou link para a mensagem original
3. WHEN documento não é encontrado no Telegram, THE Bot SHALL buscar no OneDrive (se conectado)
4. WHEN documento não é encontrado em lugar nenhum, THE Bot SHALL informar e sugerir enviar o documento

### Requirement 7: Conexão com Notebook via OneDrive

**User Story:** Como Ranny, quero que o bot acesse arquivos do meu notebook, para buscar documentos mesmo quando não estão no Telegram.

#### Acceptance Criteria

1. WHEN Ranny pede para acessar notebook e OneDrive está conectado, THE Bot SHALL buscar arquivos na pasta sincronizada
2. WHEN Ranny pede para acessar notebook e OneDrive não está conectado, THE Bot SHALL informar: "Seu notebook tá desligado ou sem internet, não consigo acessar agora"
3. WHEN OneDrive reconecta, THE Bot SHALL poder sincronizar novos arquivos
4. WHEN arquivo é encontrado no OneDrive, THE Bot SHALL enviar cópia para o Telegram e organizar no tópico correto

### Requirement 8: Alertas Automáticos de Vencimentos

**User Story:** Como Ranny, quero ser avisada de contas a vencer, para não atrasar pagamentos.

#### Acceptance Criteria

1. WHEN vencimento está a 7 dias, THE Bot SHALL enviar primeiro alerta no Tópico_Chat
2. WHEN vencimento está a 3 dias, THE Bot SHALL enviar segundo alerta
3. WHEN vencimento está a 1 dia, THE Bot SHALL enviar alerta urgente
4. WHEN Ranny marca como pago, THE Bot SHALL cancelar alertas futuros daquele vencimento
5. WHEN vencimento é recorrente (ex: luz todo mês), THE Bot SHALL criar próximo vencimento automaticamente

### Requirement 9: Hospedagem 24/7 na Nuvem

**User Story:** Como Ranny, quero que o bot funcione sempre, para poder usar do celular a qualquer hora.

#### Acceptance Criteria

1. THE Bot SHALL rodar em servidor Railway 24 horas por dia
2. WHEN servidor reinicia, THE Bot SHALL reconectar automaticamente
3. WHEN há erro de rede, THE Bot SHALL tentar reconectar sem intervenção manual
4. THE Sistema_Web SHALL rodar no mesmo servidor que o Bot
