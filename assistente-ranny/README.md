# 🤖 Assistente Ranny V3

> Secretária virtual completa para GRN Pizzas via Telegram

![Version](https://img.shields.io/badge/version-3.2.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Tests](https://img.shields.io/badge/tests-113%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-gray)

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Como Funciona](#-como-funciona)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Deploy no Railway](#-deploy-no-railway)
- [Desenvolvimento Local](#-desenvolvimento-local)
- [Testes](#-testes)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [API Endpoints](#-api-endpoints)
- [Banco de Dados](#-banco-de-dados)
- [Tecnologias](#-tecnologias)

---

## ✅ Funcionalidades

| Função | Como usar | Descrição |
|--------|-----------|-----------|
| **Fechamento de caixa** | "fechei 2500" | Registra valor, compara com dia anterior, mostra soma da semana |
| **Classificação automática** | Enviar foto/PDF no Chat | Analisa com IA e move para tópico correto com descrição rica |
| **Extração de boletos** | Enviar boleto | Extrai valor, vencimento, beneficiário e **código de barras clicável** |
| **Extração local de PDFs** | Automático | PDFs com texto são processados localmente (economiza API) |
| **Lembretes simples** | "me lembra amanhã de pagar FGTS" | Cria lembrete com data e hora |
| **Lembretes relativos** | "me lembra daqui 5 minutos" | Suporta minutos/horas relativas |
| **Lembretes recorrentes** | "todo dia 7 lembra do FGTS" | Reagenda automaticamente após disparar |
| **Listar lembretes** | "quais meus lembretes?" | Lista todos os lembretes ativos |
| **Cancelar lembrete** | "cancela lembrete do FGTS" | Desativa o lembrete |
| **Alertas de vencimento** | Automático | Alerta 7, 3 e 1 dia antes do vencimento |
| **Marcar como pago** | "paguei a luz" | Marca vencimento como pago, cria próximo se recorrente |
| **Buscar documentos** | "cadê o contrato?" | Busca por descrição, tipo ou categoria |
| **Localizar documento** | "manda o 1" | Mostra em qual tópico o documento está |
| **Relatórios interativos** | "mostra gráfico da semana" | Gera página web com gráficos Plotly |
| **Resumo semanal** | Automático (domingo 20h) | Envia relatório semanal no Chat |
| **OneDrive** | "busca X no onedrive" | Busca arquivos na nuvem (não precisa PC ligado) |
| **Criar PDF** | "cria um pdf com: [texto]" | Gera PDF com o texto informado |
| **Criar Word** | "cria um word com: [texto]" | Gera documento DOCX |
| **Criar Excel** | "cria uma planilha com: [dados]" | Gera planilha XLSX |
| **Ler Word** | Enviar .docx + "lê esse documento" | Extrai e mostra conteúdo |
| **Ler Excel** | Enviar .xlsx + "lê essa planilha" | Extrai e mostra dados |
| **Editar Word** | Enviar .docx + "adiciona: [texto]" | Adiciona/substitui texto |
| **Editar Excel** | Enviar .xlsx + "adiciona linha: [dados]" | Adiciona/edita linhas |
| **Busca inteligente** | "procura contrato no notebook" | Busca e lê conteúdo de arquivos |
| **Conversa livre** | Qualquer mensagem | Responde com IA (Gemini) |

---

## 🏗 Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Telegram   │  │   FastAPI    │  │     Scheduler        │  │
│  │     Bot      │  │   (Web)      │  │   (APScheduler)      │  │
│  │              │  │              │  │                      │  │
│  │  - Mensagens │  │  - Gráficos  │  │  - Lembretes (1min)  │  │
│  │  - Arquivos  │  │  - Relatórios│  │  - Alertas (8h)      │  │
│  │  - Comandos  │  │  - Health    │  │  - Resumo (dom 20h)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                      │
│                    ┌──────▼───────┐                             │
│                    │    SQLite    │                             │
│                    │    (Local)   │                             │
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

---

## 🔧 Como Funciona

### 📁 Classificação de Documentos

Quando um documento é enviado no **Tópico Chat**, o bot:
1. Analisa o conteúdo (local ou com Gemini Vision)
2. Classifica em uma categoria
3. Reposta no tópico correto **com descrição rica**
4. Confirma: "Guardei em Financeiro! 📁"

**Descrição Rica para Boletos:**
```
📄 Boleto: NATURGY GÁS NATURAL
💰 R$ 78.5
📅 Venc: 2026-01-28

📋 Código (clique p/ copiar):
`23793381286000000000300000000400192340000007850`
```

O código de barras fica em formato clicável - basta tocar para copiar!

**Mapeamento de Categorias:**

| Categoria | Tópico | Exemplos |
|-----------|--------|----------|
| `financeiro` | Financeiro | Boletos, comprovantes, extratos |
| `empresa` | Empresa | NF, DAS, DARF, guias fiscais |
| `juridico` | Jurídico | Processos, intimações, contratos |
| `pessoal` | Pessoal | Documentos pessoais, RG, CPF |
| `funcionarios` | Funcionários | Contratos, advertências, ASO |
| `manutencao` | Manutenção | Orçamentos, notas de serviço |
| `outros` | Outros | Não classificados |

### 📄 Processamento Inteligente de PDFs

O sistema usa uma estratégia inteligente para economizar chamadas à API do Gemini:

```
PDF recebido → Tem texto? → SIM → Extração local (regex)
                         → NÃO → Converte para imagem → Gemini Vision
```

**Extração Local (sem usar IA):**
- Valor do boleto
- Data de vencimento
- Beneficiário/Cedente
- Tipo de conta (luz, água, gás, internet, etc.)
- **Código de barras / Linha digitável** (47-48 dígitos)

**Tipos de código de barras suportados:**
- Boletos bancários (47 dígitos)
- Contas de concessionárias (48 dígitos)
- Formatos com pontos, espaços ou sem formatação

### 📝 Sistema de Lembretes

**Parsing de datas em português:**
- `amanhã` → dia seguinte
- `segunda`, `terça`, etc. → próximo dia da semana
- `dia 15` → dia 15 do mês atual ou próximo
- `próxima semana` → 7 dias
- `daqui 3 dias` → 3 dias a partir de hoje
- `daqui 5 minutos` → 5 minutos a partir de agora
- `daqui 2 horas` → 2 horas a partir de agora

**Parsing de horas:**
- `às 14h` → 14:00
- `às 14h30` → 14:30
- `de manhã` → 09:00
- `à tarde` → 14:00
- `à noite` → 20:00
- Sem hora especificada → **09:00** (padrão)

**Recorrência:**
- `todo dia` → diário
- `toda semana` / `toda segunda` → semanal
- `todo mês` / `todo dia 7` → mensal

### ⏰ Alertas de Vencimentos

O sistema envia alertas automáticos:
- **7 dias antes**: "📅 Vencimento em 7 dias: Luz - R$ 350,00"
- **3 dias antes**: "⚠️ Vencimento em 3 dias: Luz - R$ 350,00"
- **1 dia antes**: "🚨 URGENTE! Vence amanhã: Luz - R$ 350,00"

Ao marcar como pago (`"paguei a luz"`):
- Cancela alertas futuros
- Se recorrente, cria próximo vencimento automaticamente

### 📊 Relatórios Interativos

Gera página web com gráficos **Plotly**:
- **Gráfico de linha**: Faturamento diário com média
- **Gráfico de barras**: Comparativo semanal
- **Gráfico de pizza**: Gastos por categoria

Períodos suportados:
- `"mostra gráfico de hoje"` → 1 dia
- `"mostra gráfico da semana"` → 7 dias
- `"mostra gráfico da quinzena"` → 15 dias
- `"mostra gráfico do mês"` → 30 dias
- `"mostra gráfico do trimestre"` → 90 dias

**Token expira em 24 horas** por segurança.

### 🔍 Busca de Documentos

Padrões suportados:
- `"cadê o contrato?"` / `"cadê a nota?"`
- `"onde está o boleto?"` / `"onde tá a fatura?"`
- `"acha o documento"` / `"procura o comprovante"`
- `"tem algum documento de..."` / `"você tem o contrato?"`

Após a busca, pode localizar:
- `"manda o 1"` → mostra em qual tópico está o primeiro documento encontrado

**⚠️ Nota:** O bot mostra onde o documento está (qual tópico), mas não reenvia automaticamente. Você precisa ir no tópico indicado para pegar o arquivo.

### ☁️ Integração OneDrive

Conecta ao OneDrive para buscar arquivos na nuvem. **Não depende do notebook estar ligado** - os arquivos ficam na nuvem da Microsoft.

**Comandos:**
- `"conecta onedrive"` → inicia conexão OAuth
- `"busca X no onedrive"` / `"procura X no notebook"` → busca arquivos
- `"manda o 1"` → envia arquivo encontrado
- `"status onedrive"` → verifica conexão
- `"desconecta onedrive"` → remove conexão

**Busca Inteligente:**
A busca no OneDrive agora lê o conteúdo dos arquivos encontrados:
- **PDF**: Extrai texto do documento
- **DOCX**: Lê parágrafos do Word
- **XLSX**: Lê dados das planilhas Excel

**Status de conexão:**
- 🟢 Conectado: busca arquivos normalmente
- ❌ Desconectado: precisa reconectar via OAuth

### 📝 Criação e Edição de Documentos

O bot pode criar e editar documentos diretamente no Telegram:

**Criar documentos:**
```
👤 "cria um pdf com: Lista de compras - Queijo, Presunto, Tomate"
🤖 📄 Envia arquivo lista_de_compras.pdf

👤 "cria um word com: Relatório mensal de vendas..."
🤖 📄 Envia arquivo relatorio_mensal.docx

👤 "cria uma planilha com: Nome, Valor, Data | João, 100, 01/01"
🤖 📄 Envia arquivo planilha.xlsx
```

**Ler documentos (envie o arquivo junto com a mensagem):**
```
👤 [anexa arquivo.docx] "lê esse documento"
🤖 "📄 Conteúdo do documento:
    Parágrafo 1: ...
    Parágrafo 2: ..."

👤 [anexa planilha.xlsx] "lê essa planilha"
🤖 "📊 Conteúdo da planilha:
    Planilha: Sheet1
    | Nome | Valor | Data |
    | João | 100   | 01/01 |"
```

**Editar documentos (envie o arquivo junto com a mensagem):**
```
👤 [anexa arquivo.docx] "adiciona: Novo parágrafo no final"
🤖 📄 Envia arquivo editado

👤 [anexa planilha.xlsx] "adiciona linha: Maria, 200, 02/01"
🤖 📄 Envia planilha com nova linha

👤 [anexa planilha.xlsx] "substitui João por Pedro"
🤖 📄 Envia planilha com substituição feita
```

**Formatos suportados:**

| Formato | Criar | Ler | Editar |
|---------|-------|-----|--------|
| PDF     | ✅    | ✅  | ❌     |
| DOCX    | ✅    | ✅  | ✅     |
| XLSX    | ✅    | ✅  | ✅     |

---

## 💬 Exemplos de Uso

### Fechamento de Caixa
```
👤 "fechei 2500"
🤖 "Anotado! 📊
    Hoje: R$ 2.500,00
    Ontem: R$ 2.200,00 (+13.6%)
    Semana: R$ 15.800,00
    
    Melhor que ontem! 🎉"
```

### Criar Lembrete
```
👤 "me lembra segunda às 14h de ligar pro contador"
🤖 "Anotado! 📝
    
    Vou te lembrar dia 20/01 às 14:00:
    'ligar pro contador'"
```

### Lembrete Recorrente
```
👤 "todo dia 7 lembra do FGTS"
🤖 "Anotado! 📝
    
    Vou te lembrar dia 07/02 às 09:00:
    'FGTS'
    
    🔄 Lembrete recorrente: todo mês"
```

### Criar Documento
```
👤 "cria um pdf com: Orçamento de reforma - Item 1: Pintura R$ 500"
🤖 📄 Envia arquivo orcamento_de_reforma.pdf
```

### Editar Planilha
```
👤 [anexa controle.xlsx] "adiciona linha: Produto X, 50, Estoque"
🤖 📄 Envia controle.xlsx atualizado com a nova linha
```

### Buscar Documento
```
👤 "cadê o contrato do aluguel?"
🤖 "Achei 2 documento(s) sobre 'contrato aluguel':

    1. 📄 Contrato de locação comercial
       documento | Juridico | 2025-01-10
       🔗 Ver mensagem
    
    2. 📄 Aditivo contrato aluguel
       pdf | Juridico | 2025-01-05
       🔗 Ver mensagem
    
    💡 Quer que eu te mande algum? Diz o número (ex: 'manda o 1')"

👤 "manda o 1"
🤖 "📁 Contrato de locação comercial
    📂 Categoria: Juridico
    📅 Salvo em: 2025-01-10
    
    💡 Você pode encontrar este arquivo no tópico Juridico do grupo!"
```

### Marcar Pagamento
```
👤 "paguei a luz"
🤖 "Anotado! ✅
    
    Marquei como pago:
    📄 Conta de luz - Janeiro
    💰 R$ 350,00
    
    🔄 Próximo vencimento criado: 20/02/2025"
```

---

## 🚀 Deploy no Railway

> 📖 **Guia completo**: [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)

### Variáveis de Ambiente Obrigatórias

```env
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
GEMINI_API_KEY=sua_chave_gemini
GROUP_ID=-1003536252896
```

### Tópicos do Grupo

```env
TOPIC_CHAT=47
TOPIC_FINANCEIRO=2
TOPIC_EMPRESA=3
TOPIC_JURIDICO=5
TOPIC_PESSOAL=4
TOPIC_FUNCIONARIOS=6
TOPIC_MANUTENCAO=7
TOPIC_OUTROS=8
```

### OneDrive (Opcional)

```env
MICROSOFT_CLIENT_ID=seu_client_id_azure
MICROSOFT_CLIENT_SECRET=seu_client_secret_azure
```

---

## 🔧 Desenvolvimento Local

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar ambiente
```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### 3. Rodar o bot
```bash
python bot.py
```

O bot inicia:
- 🤖 Bot Telegram
- 🌐 Servidor web na porta 8000
- 📅 Scheduler com jobs automáticos

---

## 🧪 Testes

O projeto possui **113 testes de propriedades** usando `pytest` e `hypothesis`.

### Rodar todos os testes
```bash
python -m pytest -v
```

### Rodar testes específicos
```bash
# Classificação de documentos
python -m pytest test_classification_properties.py -v

# Lembretes
python -m pytest test_lembretes_properties.py -v

# Busca de documentos
python -m pytest test_busca_properties.py -v

# Relatórios
python -m pytest test_relatorios_properties.py -v

# Alertas de vencimentos
python -m pytest test_alertas_properties.py -v

# Vencimentos recorrentes
python -m pytest test_vencimentos_properties.py -v

# OneDrive
python -m pytest test_onedrive_properties.py -v

# Playwright (página de relatórios)
python -m pytest test_relatorios_playwright.py -v
```

### Propriedades Testadas

| Arquivo | Propriedades | Descrição |
|---------|--------------|-----------|
| `test_classification_properties.py` | 12 | Classificação retorna categoria válida |
| `test_lembretes_properties.py` | 35 | Parsing de datas, recorrência, disparo |
| `test_busca_properties.py` | 17 | Busca retorna matches corretos |
| `test_relatorios_properties.py` | 9 | Token TTL 24h, dados preservados |
| `test_alertas_properties.py` | 14 | Alertas baseados em dias restantes |
| `test_vencimentos_properties.py` | 14 | Recorrente gera próximo, extração boleto |
| `test_onedrive_properties.py` | 11 | Desconectado retorna mensagem apropriada |
| `test_relatorios_playwright.py` | 5 | Página de relatórios no browser |

---

## 📁 Estrutura de Arquivos

```
assistente-ranny/
├── bot.py              # Bot principal + servidor web + handlers
├── ai.py               # Integração Gemini (classificação, conversa, análise de arquivos)
├── database_sqlite.py  # Banco SQLite (CRUD completo)
├── database_sqlite_compat.py  # Interface simplificada
├── database_adapter.py # Adaptador (usa SQLite)
├── config.py           # Configurações centralizadas
├── scheduler.py        # APScheduler (timezone Brasil)
├── jobs.py             # Jobs automáticos (lembretes, alertas, resumo)
├── web.py              # FastAPI (relatórios, health, OAuth)
├── onedrive.py         # Integração Microsoft Graph API
├── date_parser.py      # Parser de datas em português (inclui tempo relativo)
├── pdf_reader.py       # Extração local de PDFs (economiza API Gemini)
├── pdf_tools.py        # Criação e edição de PDF, DOCX, XLSX
├── Procfile            # Comando de start (Railway)
├── railway.toml        # Configuração Railway (health check, replicas)
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de variáveis de ambiente
├── DEPLOY_RAILWAY.md   # Guia completo de deploy
└── test_*.py           # Arquivos de teste
```

---

## 🔗 API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Health check (Railway) |
| `/relatorio/{token}` | GET | Relatório interativo (HTML + Plotly) |
| `/oauth/callback` | GET | Callback OAuth do OneDrive |

### Health Check Response
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.2.0",
  "timestamp": "2025-01-16T12:00:00",
  "components": {
    "web": "healthy",
    "database": {"status": "healthy", "error": null},
    "scheduler": {"status": "healthy", "jobs_count": 3}
  }
}
```

---

## 🗄 Banco de Dados

### Schema (SQLite)

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
    recorrente VARCHAR(20),  -- 'diario', 'semanal', 'mensal'
    ativo BOOLEAN DEFAULT TRUE,
    disparado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documentos
CREATE TABLE documentos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    descricao TEXT,
    file_id VARCHAR(200),
    message_id INTEGER,
    topic_id INTEGER,
    categoria VARCHAR(50),
    dados_extraidos JSONB,
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

-- Relatórios temporários
CREATE TABLE relatorios_temp (
    token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo VARCHAR(50),
    dados JSONB,
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tokens OneDrive
CREATE TABLE onedrive_tokens (
    id SERIAL PRIMARY KEY,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🛠 Tecnologias

| Tecnologia | Uso |
|------------|-----|
| **Python 3.10+** | Linguagem principal |
| **python-telegram-bot 21.0** | Bot Telegram (com suporte a tópicos) |
| **FastAPI** | Servidor web (relatórios, health) |
| **Uvicorn** | ASGI server |
| **SQLite** | Banco de dados local |
| **Google Gemini** | IA para classificação e conversa |
| **pdfplumber** | Extração de texto de PDFs |
| **PyMuPDF (fitz)** | Conversão PDF → imagem |
| **ReportLab** | Criação de PDFs |
| **python-docx** | Criação e edição de DOCX |
| **openpyxl** | Criação e edição de XLSX |
| **APScheduler** | Jobs agendados (timezone America/Sao_Paulo) |
| **Plotly** | Gráficos interativos |
| **Microsoft Graph API** | Integração OneDrive |
| **pytest + hypothesis** | Testes de propriedades |
| **Railway** | Hospedagem 24/7 |

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  <b>🍕 GRN Pizzas - Assistente Ranny V3</b><br>
  Desenvolvido com ❤️ para a Ranny
</p>
