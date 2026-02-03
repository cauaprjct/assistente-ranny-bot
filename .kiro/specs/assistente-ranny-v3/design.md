# Design Document: Assistente Ranny V3

## Overview

Sistema completo de assistente virtual para GRN Pizzas composto por:
- **Bot Telegram** - Interface principal com a Ranny
- **Servidor Web (FastAPI)** - Gera relatórios interativos
- **Scheduler** - Dispara lembretes e alertas
- **Banco de Dados** - Supabase (PostgreSQL)
- **Integração OneDrive** - Acesso aos arquivos do notebook

Tudo roda em um único container no Railway.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Telegram   │  │   FastAPI    │  │     Scheduler        │  │
│  │     Bot      │  │   (Web)      │  │   (APScheduler)      │  │
│  │              │  │              │  │                      │  │
│  │  - Mensagens │  │  - Gráficos  │  │  - Lembretes 9h      │  │
│  │  - Arquivos  │  │  - Relatórios│  │  - Alertas venc.     │  │
│  │  - Comandos  │  │  - Links temp│  │  - Resumo domingo    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                      │
│                    ┌──────▼───────┐                             │
│                    │   Supabase   │                             │
│                    │  (PostgreSQL)│                             │
│                    └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Telegram │ │  Gemini  │ │ OneDrive │
        │   API    │ │   API    │ │   API    │
        └──────────┘ └──────────┘ └──────────┘
```

## Components and Interfaces

### 1. Bot Telegram (bot.py)

Responsável por receber e processar mensagens.

```python
class TelegramBot:
    async def handle_message(update: Update) -> None
    async def handle_file(update: Update) -> None
    async def send_to_topic(topic: str, message: str, file_id: str = None) -> None
    async def reply(update: Update, text: str) -> None
```

**Fluxo de mensagem no Chat:**
1. Recebe mensagem
2. Detecta intenção (fechamento, lembrete, busca, relatório, conversa)
3. Executa ação correspondente
4. Responde no mesmo tópico

**Fluxo de documento no Chat:**
1. Recebe arquivo
2. Analisa com Gemini Vision
3. Classifica categoria
4. Reposta no tópico correto
5. Confirma no Chat

### 2. Servidor Web (web.py)

FastAPI servindo relatórios interativos.

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/relatorio/{token}")
async def get_relatorio(token: str) -> HTMLResponse

@app.get("/health")
async def health_check() -> dict
```

**Geração de relatório:**
1. Bot gera token único (UUID)
2. Salva dados do relatório no banco com TTL 24h
3. Retorna URL: `https://app.railway.app/relatorio/{token}`
4. Usuário acessa, vê gráficos Plotly interativos
5. Após 24h, token expira

### 3. Scheduler (scheduler.py)

APScheduler para tarefas agendadas.

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Jobs
@scheduler.scheduled_job('cron', hour=9)
async def check_lembretes()

@scheduler.scheduled_job('cron', hour=8)
async def check_vencimentos()

@scheduler.scheduled_job('cron', day_of_week='sun', hour=20)
async def resumo_semanal()
```

### 4. Integração Gemini (ai.py)

```python
async def get_response(user_id: int, message: str) -> str
async def analyze_image(image_data: bytes) -> dict
async def classify_document(text: str) -> str
async def extract_intent(message: str) -> dict
```

**Intenções detectadas:**
- `fechamento` - valor numérico
- `lembrete` - data + descrição
- `busca` - termo de busca
- `relatorio` - período
- `conversa` - resposta livre

### 5. Integração OneDrive (onedrive.py)

```python
class OneDriveClient:
    async def is_connected() -> bool
    async def search_files(query: str) -> List[dict]
    async def download_file(file_id: str) -> bytes
    async def get_recent_files() -> List[dict]
```

**Autenticação:**
- OAuth2 com Microsoft Graph API
- Token refresh automático
- Fallback gracioso quando offline

## Data Models

### Supabase Schema

```sql
-- Fechamentos de caixa
CREATE TABLE fechamentos (
    id SERIAL PRIMARY KEY,
    valor DECIMAL(10,2) NOT NULL,
    data DATE NOT NULL DEFAULT CURRENT_DATE,
    observacao TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lembretes
CREATE TABLE lembretes (
    id SERIAL PRIMARY KEY,
    descricao TEXT NOT NULL,
    data DATE NOT NULL,
    hora TIME DEFAULT '09:00',
    recorrente VARCHAR(20), -- 'diario', 'semanal', 'mensal', NULL
    ativo BOOLEAN DEFAULT TRUE,
    disparado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documentos
CREATE TABLE documentos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    descricao TEXT,
    file_id VARCHAR(200), -- Telegram file_id
    message_id INTEGER,   -- ID da mensagem no tópico
    topic_id INTEGER,     -- ID do tópico onde foi salvo
    categoria VARCHAR(50),
    dados_extraidos JSONB, -- valor, vencimento, etc
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vencimentos
CREATE TABLE vencimentos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2),
    data_vencimento DATE NOT NULL,
    recorrente VARCHAR(20),
    pago BOOLEAN DEFAULT FALSE,
    pago_em TIMESTAMP,
    documento_id INTEGER REFERENCES documentos(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Funcionários
CREATE TABLE funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    funcao VARCHAR(100),
    admissao DATE,
    status VARCHAR(20) DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Relatórios temporários (para links)
CREATE TABLE relatorios_temp (
    token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo VARCHAR(50),
    dados JSONB,
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_lembretes_data ON lembretes(data) WHERE ativo = TRUE;
CREATE INDEX idx_vencimentos_data ON vencimentos(data_vencimento) WHERE pago = FALSE;
CREATE INDEX idx_documentos_categoria ON documentos(categoria);
CREATE INDEX idx_relatorios_expires ON relatorios_temp(expires_at);
```

### Mapeamento Categoria → Tópico

```python
CATEGORIA_TOPICO = {
    'financeiro': 2,    # Boletos, comprovantes, extratos
    'empresa': 3,       # NF, DAS, DARF, guias
    'juridico': 5,      # Processos, intimações
    'pessoal': 4,       # Documentos pessoais
    'funcionarios': 6,  # Contratos, advertências, ASO
    'manutencao': 7,    # Orçamentos, notas de serviço
    'outros': 8,        # Não classificados
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.*

Antes de definir as propriedades, vou analisar cada critério de aceitação:


### Property 1: Documento no Chat é sempre classificado e movido

*For any* documento enviado no Tópico_Chat, o bot deve classificá-lo em uma categoria válida (financeiro, empresa, juridico, pessoal, funcionarios, manutencao, outros) e repostá-lo no tópico correspondente.

**Validates: Requirements 1.2, 2.1, 2.2**

### Property 2: Categoria mapeia corretamente para tópico

*For any* categoria válida, deve existir um mapeamento único para um ID de tópico do Telegram.

**Validates: Requirements 2.2**

### Property 3: Documento em tópico de arquivo não é movido

*For any* documento enviado diretamente em um Tópico_Arquivo (não Chat), o bot não deve mover para outro tópico.

**Validates: Requirements 2.5**

### Property 4: Pedido de lembrete cria lembrete no banco

*For any* mensagem que contém pedido de lembrete válido, um registro de lembrete deve ser criado no banco com data e descrição extraídas.

**Validates: Requirements 1.4, 3.1**

### Property 5: Lembrete sem hora usa 09:00 como padrão

*For any* lembrete criado sem hora especificada, a hora deve ser 09:00.

**Validates: Requirements 3.2**

### Property 6: Listagem de lembretes retorna apenas ativos

*For any* consulta de lembretes, apenas lembretes com ativo=TRUE devem ser retornados.

**Validates: Requirements 3.4**

### Property 7: Cancelamento de lembrete marca como inativo

*For any* operação de cancelamento de lembrete, o lembrete deve ter ativo=FALSE após a operação.

**Validates: Requirements 3.5**

### Property 8: Lembrete recorrente gera próximo após disparo

*For any* lembrete com recorrente != NULL que é disparado, um novo lembrete deve ser criado com data futura calculada.

**Validates: Requirements 3.6**

### Property 9: Fechamento salva com data atual

*For any* fechamento registrado, a data deve ser a data atual (ou data especificada).

**Validates: Requirements 4.1**

### Property 10: Variação percentual é calculada corretamente

*For any* dois fechamentos consecutivos, a variação percentual deve ser ((atual - anterior) / anterior) * 100.

**Validates: Requirements 4.2**

### Property 11: Soma semanal inclui últimos 7 dias

*For any* consulta de soma semanal, deve incluir todos os fechamentos dos últimos 7 dias.

**Validates: Requirements 4.3**

### Property 12: Relatório gera token com TTL de 24h

*For any* relatório gerado, o token deve ter expires_at = created_at + 24 horas.

**Validates: Requirements 5.1, 5.2**

### Property 13: Busca de documento retorna matches

*For any* termo de busca, os documentos retornados devem conter o termo na descrição ou tipo.

**Validates: Requirements 6.1**

### Property 14: OneDrive desconectado retorna mensagem apropriada

*For any* tentativa de acesso ao OneDrive quando desconectado, a resposta deve indicar que o notebook está offline.

**Validates: Requirements 7.2**

### Property 15: Alertas de vencimento baseados em dias restantes

*For any* vencimento não pago, alertas devem ser gerados quando dias_restantes está em [7, 3, 1].

**Validates: Requirements 8.1, 8.2, 8.3**

### Property 16: Vencimento pago não gera alertas

*For any* vencimento marcado como pago, não deve aparecer na lista de alertas pendentes.

**Validates: Requirements 8.4**

### Property 17: Vencimento recorrente gera próximo

*For any* vencimento com recorrente != NULL que é marcado como pago, um novo vencimento deve ser criado com data futura.

**Validates: Requirements 8.5**

### Property 18: Boleto tem valor e vencimento extraídos

*For any* documento classificado como boleto, os campos valor e data_vencimento devem ser extraídos e salvos.

**Validates: Requirements 2.3**

## Error Handling

### Erros de Rede
- Telegram API timeout → Retry com backoff exponencial (1s, 2s, 4s, max 30s)
- Gemini API quota → Fallback para respostas pré-definidas
- Supabase offline → Cache local temporário, sync quando reconectar

### Erros de Classificação
- Gemini não consegue classificar → Categoria "outros"
- Imagem corrompida → Informar usuário, não mover documento

### Erros de OneDrive
- Token expirado → Refresh automático
- Arquivo não encontrado → Informar usuário
- Notebook offline → Mensagem amigável explicando

### Erros de Scheduler
- Job falha → Log + retry na próxima execução
- Múltiplos lembretes mesmo horário → Processar em batch

## Testing Strategy

### Unit Tests
- Parsing de datas em português ("amanhã", "segunda", "dia 15")
- Cálculo de variação percentual
- Mapeamento categoria → tópico
- Extração de valores de texto

### Property-Based Tests (pytest + hypothesis)
- Classificação sempre retorna categoria válida
- Lembretes recorrentes sempre geram próximo
- Vencimentos pagos nunca aparecem em alertas
- Busca retorna apenas documentos que contêm termo

### Integration Tests
- Fluxo completo: documento → classificação → repost
- Fluxo lembrete: criar → disparar → notificar
- Fluxo relatório: gerar → acessar → expirar

### Configuração de Testes
- Mínimo 100 iterações por property test
- Usar banco de teste separado (Supabase test project)
- Mock para APIs externas (Telegram, Gemini, OneDrive)
